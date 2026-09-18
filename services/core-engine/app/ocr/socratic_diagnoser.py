"""
Anti-Photomath Socratic Notebook Diagnoser.
Analyzes student handwritten notebook steps sequentially, identifies the exact step
where algebraic failure occurred, classifies the Buggy Rule, and formulates a Socratic
prompt that prompts the student to self-correct without disclosing answers.
Ref: Hedef 5.
"""

from __future__ import annotations
import re
from typing import List, Optional, Tuple, TYPE_CHECKING
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.graph.knowledge_dag import KnowledgeDAG
from app.socratic.guardrail import ZeroLeakageGuardrail
from app.ocr.models import ScannedStep, MathScanResponse
from app.ocr.vision_pipeline import MathVisionPipeline

if TYPE_CHECKING:
    from app.vault.mistake_vault import CognitiveMistakeVault


class SocraticNotebookDiagnoser:
    """
    Socratic OCR Diagnoser:
    Does NOT solve the problem for the user.
    Inspects intermediate steps, isolates mistakes, maps to DAG, and delivers Socratic guidance.
    """

    def __init__(
        self,
        cas: Optional[SymbolicEquivalenceEngine] = None,
        detector: Optional[QuadraticMisconceptionDetector] = None,
        dag: Optional[KnowledgeDAG] = None,
        vision_pipeline: Optional[MathVisionPipeline] = None,
        vault: Optional[CognitiveMistakeVault] = None,
    ):
        self.cas = cas or SymbolicEquivalenceEngine()
        self.detector = detector or QuadraticMisconceptionDetector(self.cas)
        self.dag = dag or KnowledgeDAG()
        self.vision = vision_pipeline or MathVisionPipeline(self.dag)
        self.guardrail = ZeroLeakageGuardrail()
        self.vault = vault

    def diagnose_notebook_solution(
        self,
        segmented_lines: List[str],
        target_problem: Optional[str] = None,
        user_id: str = "default_student",
    ) -> MathScanResponse:
        """
        Takes segmented lines from student notebook:
        Line 0: The question / problem being solved.
        Line 1..k: The student's written steps.
        """
        if not segmented_lines:
            return MathScanResponse(
                problem_statement="Boş görüntü veya taranamadı",
                dag_node_id="N01",
                dag_node_title="Genel Matematik",
                segmented_steps=[],
                has_error=True,
                error_step_index=None,
                detected_bug_id=None,
                socratic_hint="Görüntüde herhangi bir matematiksel adım tespit edilemedi. Lütfen soruyu daha net ve aydınlık bir ortamda tekrar fotoğraflayınız.",
                is_zero_leakage_sanitized=True,
                confidence=0.0,
            )

        problem_raw = target_problem or segmented_lines[0]
        steps_raw = segmented_lines[1:] if len(segmented_lines) > 1 else [segmented_lines[0]]

        # 1. Map to Knowledge DAG Node
        node_id, node_title = self.vision.link_problem_to_dag_node(problem_raw)

        # 2. Step-by-Step Mathematical Verification
        scanned_steps: List[ScannedStep] = []
        has_error = False
        first_error_index: Optional[int] = None
        detected_bug: Optional[str] = None
        error_explanation: Optional[str] = None

        prev_step_str = problem_raw

        for idx, step_str in enumerate(steps_raw, start=1):
            norm_step = self.vision.normalize_latex(step_str)
            norm_prev = self.vision.normalize_latex(prev_step_str)

            # Check mathematical equivalence with previous step
            norm_prev_lower = norm_prev.lower()
            is_indefinite_integral = ("integrate" in norm_prev_lower or "int(" in norm_prev_lower) and not any(k in norm_prev_lower for k in [",0,", ",1,", ",2,", "(x,0", "(x,1", "_0^", "_a^"])

            is_equiv = False
            if is_indefinite_integral:
                # Belirsiz integralde +C şarttır
                has_c = "+c" in norm_step.lower() or "+ c" in norm_step.lower() or norm_step.strip().endswith("+C")
                if not has_c:
                    is_equiv = False
                else:
                    m = re.search(r"integrate\(([^,]+),\s*([a-zA-Z])\)", norm_prev)
                    if m:
                        integrand, var = m.group(1).strip(), m.group(2).strip()
                        is_equiv = self.cas.verify_integral(integrand, norm_step, var=var)
                    else:
                        try:
                            is_equiv, _, _ = self.cas.verify_equivalence(norm_step, norm_prev)
                        except Exception:
                            is_equiv = False
            else:
                try:
                    is_equiv, _, _ = self.cas.verify_equivalence(norm_step, norm_prev)
                except Exception:
                    is_equiv = False

            if is_equiv:
                scanned_steps.append(
                    ScannedStep(
                        step_index=idx,
                        raw_text=step_str,
                        latex=step_str,
                        is_valid=True,
                        diagnostic_bug_id=None,
                        error_reason=None,
                    )
                )
                prev_step_str = step_str
            else:
                # Step is mathematically invalid! Detect Buggy Rule
                diag = self.detector.detect(
                    user_step_str=norm_step,
                    previous_step_str=norm_prev,
                    target_equation_str=problem_raw,
                )

                bug_id = diag.bug_id if diag else "GENERAL_ALGEBRAIC_MISSTEP"
                reason = (
                    diag.description
                    if diag
                    else "Bu adım önceki denklemle cebirsel olarak eşdeğer değil."
                )

                scanned_steps.append(
                    ScannedStep(
                        step_index=idx,
                        raw_text=step_str,
                        latex=step_str,
                        is_valid=False,
                        diagnostic_bug_id=bug_id,
                        error_reason=reason,
                    )
                )

                if not has_error:
                    has_error = True
                    first_error_index = idx
                    detected_bug = bug_id
                    error_explanation = reason

                # Once first error is caught, remaining steps inherit invalidity context
                prev_step_str = step_str

        # 3. Formulate Socratic Guidance
        socratic_hint = self._formulate_socratic_hint(
            has_error=has_error,
            error_step=first_error_index,
            bug_id=detected_bug,
            explanation=error_explanation,
            problem_str=problem_raw,
        )

        # 4. Zero-Leakage Shield: sanitize prompt to guarantee 0 answer leakage
        sanitized_hint, was_sanitized = self.guardrail.enforce_zero_leakage(
            proposed_text=socratic_hint,
            language="tr",
        )

        # 5. Auto-record to Cognitive Mistake Vault (Hedef 12 entegrasyonu)
        if has_error and detected_bug and self.vault:
            offending_content = (
                steps_raw[first_error_index - 1]
                if (first_error_index and 0 < first_error_index <= len(steps_raw))
                else problem_raw
            )
            self.vault.record_mistake(
                user_id=user_id,
                node_id=node_id,
                bug_id=detected_bug,
                problem_statement=problem_raw,
                offending_step=offending_content,
                correct_principle=error_explanation or "Matematiksel kural ihlali",
                remediation_directive=sanitized_hint,
            )

        return MathScanResponse(
            problem_statement=problem_raw,
            dag_node_id=node_id,
            dag_node_title=node_title,
            segmented_steps=scanned_steps,
            has_error=has_error,
            error_step_index=first_error_index,
            detected_bug_id=detected_bug,
            socratic_hint=sanitized_hint,
            is_zero_leakage_sanitized=True,
            confidence=0.96,
        )

    def _formulate_socratic_hint(
        self,
        has_error: bool,
        error_step: Optional[int],
        bug_id: Optional[str],
        explanation: Optional[str],
        problem_str: str,
    ) -> str:
        """Formulates targeted Socratic prompts with zero answer disclosure."""
        if not has_error:
            return (
                "Harika bir akıl yürütme! Defterindeki tüm adımlar matematiksel olarak tamamen doğru. "
                "Şimdi bu bulduğun ara adımlardan hareketle sonuca nasıl ulaşacağını açıklar mısın?"
            )

        step_num = error_step or 1

        # Specific pedagogical prompts per Buggy Rule family
        if bug_id == "BUG-QUAD-01":
            return (
                f"{step_num}. adımda sıfır-çarpım kuralını uygularken sağ tarafın sıfır olup olmadığına dikkat ettin mi? "
                "Çarpımı bu sayı eden başka değerler de olabilir mi?"
            )
        elif bug_id == "BUG-QUAD-02":
            return (
                f"{step_num}. adımda her iki tarafın karekökünü alırken karesi bu sayıyı veren negatif bir ikiz kök de olabilir mi?"
            )
        elif bug_id == "BUG-QUAD-03":
            return (
                f"{step_num}. adımda tam kare açılımı yaparken (a + b)^2 kuralındaki çarpımın iki katı (2ab) terimini tekrar kontrol etmek ister misin?"
            )
        elif bug_id == "BUG-QUAD-04":
            return (
                f"{step_num}. adımda her iki tarafı x ile sadeleştirirken köklerden birini (x=0) kaybetmiş olabilir misin?"
            )
        elif bug_id == "BUG-QUAD-05":
            return (
                f"{step_num}. adımda ikinci derece denklem formülünde (-b) teriminin işaretine dikkat ettin mi?"
            )
        elif bug_id == "BUG-QUAD-06" or bug_id == "BUG-FOUND-14":
            return (
                f"{step_num}. adımda eşitsizliğin her iki tarafını negatif bir sayıya bölerken eşitsizlik yönünün ne olması gerektiğini düşünelim mi?"
            )
        elif bug_id == "BUG-FOUND-15":
            return (
                f"{step_num}. adımda denklemin bir tarafına işlem yaparken terazi dengesini korumak için diğer tarafa da aynı işlemi uyguladın mı?"
            )
        elif bug_id == "BUG-PARAB-01" or bug_id == "BUG-QUAD-08":
            return (
                f"{step_num}. adımda parabolün tepe noktası apsisini bulurken r = -b / (2a) formülündeki eksi işaretini doğru uyguladın mı?"
            )
        elif bug_id == "BUG-PARAB-02":
            return (
                f"{step_num}. adımda simetri ekseni ile tepe noktasının ordinatını karıştırmış olabilir misin?"
            )
        elif bug_id == "BUG-POLY-01":
            return (
                f"{step_num}. adımda polinom kalan teoreminde (P(x)'in (x - a) ile bölümünden kalan için) böleni sıfıra eşitlerken x yerine ne koyman gerektiğini kontrol etmek ister misin?"
            )
        elif bug_id == "BUG-POLY-02":
            return (
                f"{step_num}. adımda katsayılar toplamı için x=1, sabit terim için x=0 yazma kuralını tekrar gözden geçirelim mi?"
            )
        elif bug_id == "BUG-TRIG-01":
            return (
                f"{step_num}. adımda sinüs fonksiyonunu parantez içine dağıtırken toplam-fark formülünü hatırlamaya ne dersin?"
            )
        elif bug_id == "BUG-LOG-01":
            return (
                f"{step_num}. adımda logaritmanın toplam ve çarpım kurallarını incelerken log(a+b) ifadesinin doğrudan dağılamayacağını anımsayalım mı?"
            )
        elif bug_id == "BUG-CALC-01":
            return (
                f"{step_num}. adımda bileşke fonksiyonun türevini alırken iç fonksiyonun türevini (zincir kuralı) çarpan olarak ekledin mi?"
            )
        elif bug_id == "BUG-CALC-02":
            return (
                f"{step_num}. adımda bölümün türevini alırken paydaki çıkarma işleminde işaret sırasına dikkat ettin mi?"
            )
        elif bug_id == "BUG-CALC-03":
            return (
                f"{step_num}. adımda 0/0 belirsizliğiyle karşılaştığında ifadeyi sadeleştirerek belirsizliği gidermeyi denedin mi?"
            )
        elif bug_id == "BUG-CALC-05":
            return (
                f"{step_num}. adımda çarpımın türevini alırken (uv)' = u'v + uv' kuralı yerine doğrudan terimleri çarpmış olabilir misin?"
            )
        elif bug_id == "BUG-CALC-06":
            return (
                f"{step_num}. adımda sabit bir sayının türevini alırken sabit fonksiyonun eğiminin ne olduğunu hatırlar mısın?"
            )
        elif bug_id == "BUG-CALC-10":
            return (
                f"{step_num}. adımda teğet doğrusunun eğimini hesaplarken türev fonksiyonunda apsis değerini yerine koymak yerine fonksiyon değerini mi aldın?"
            )
        elif bug_id == "BUG-INT-01":
            return (
                f"{step_num}. adımda belirsiz integrali tamamlarken integrasyon sabiti olan (+ C)'yi eklemeyi unuttun mu?"
            )
        elif bug_id == "BUG-INT-02":
            return (
                f"{step_num}. adımda u-dönüşümü yaparken dx diferansiyelini du cinsinden doğru ifade ettiğini teyit edebilir misin?"
            )
        elif bug_id == "BUG-INT-03":
            return (
                f"{step_num}. adımda belirli integralde sınırları yerine koyarken üst sınır ve alt sınır sırasını nasıl uyguladın?"
            )
        elif bug_id == "BUG-INT-04":
            return (
                f"{step_num}. adımda eğri altında kalan geometrik alanı hesaplarken negatif çıkan integral değerinin mutlak değerini almayı düşündün mü?"
            )
        elif bug_id == "BUG-INT-05":
            return (
                f"{step_num}. adımda kısmi integrasyon uygularken uv - int(v du) formülündeki işaret kuralına dikkat ettin mi?"
            )
        elif bug_id == "BUG-INT-06":
            return (
                f"{step_num}. adımda 1/x fonksiyonunun integralini alırken hangi fonksiyonun türevinin 1/x olduğunu hatırlar mısın?"
            )
        elif bug_id == "BUG-INT-07":
            return (
                f"{step_num}. adımda u-dönüşümü ile belirli integral çözerken integrasyon sınırlarını da u cinsine çevirdin mi?"
            )
        elif bug_id == "BUG-INT-08":
            return (
                f"{step_num}. adımda iki eğri arasında kalan alanı hesaplarken üstteki eğriden alttaki eğriyi çıkarma sırasını kontrol eder misin?"
            )

        return (
            f"{step_num}. adımdaki cebirsel dönüşümü tekrar inceleyelim. "
            "Bu adımdan bir önceki adıma geçerken uyguladığın işlemin eşitliği bozup bozmadığını nasıl test edebilirsin?"
        )
