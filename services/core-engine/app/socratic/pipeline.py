"""
4-Layer Inner Monologue Socratic Pipeline.
Implements:
- Layer 1: Pedagogical Intent & Scaffolding Strategist.
- Layer 2: Mathematical CAS & Bug Context Synthesizer.
- Layer 3: Socratic Dialogue Generator (Question-to-Explanation ratio >= 2.0).
- Layer 4: Deterministic Zero-Leakage Output Guardrail.
"""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.schemas import DiagnosticPayload
from app.socratic.guardrail import ZeroLeakageGuardrail


class SocraticRequest(BaseModel):
    user_input: str
    target_equation: str
    previous_step: Optional[str] = None
    solution_roots: List[float] = Field(default_factory=list)
    diagnostic_bug: Optional[DiagnosticPayload] = None
    affective_state: Optional[str] = "FLOW"
    scaffolding_level: int = Field(1, ge=1, le=4)


class InnerMonologueLog(BaseModel):
    layer1_pedagogical_intent: str
    layer2_cas_context: Dict[str, Any]
    layer3_raw_dialogue: str
    layer4_intercepted: bool
    socratic_ratio: float
    final_output: str
    latency_ms: float


class SocraticPipeline:
    """
    Orchestrates the 4-layer Socratic AI Tutor monologue and output enforcement.
    """

    def __init__(self):
        self.guardrail = ZeroLeakageGuardrail()

    def process(self, request: SocraticRequest) -> InnerMonologueLog:
        t0 = time.perf_counter()

        # -------------------------------------------------------------
        # KATMAN 1: Pedagojik Stratejist (ZPD, Niyet ve İskele Seviyesi)
        # -------------------------------------------------------------
        if request.diagnostic_bug:
            layer1_intent = f"MISCONCEPTION_REMEDIATION:{request.diagnostic_bug.bug_id}"
        elif request.affective_state == "FRUSTRATION":
            layer1_intent = "AFFECTIVE_CIRCUIT_BREAKER_EMPATHY"
        elif "neden" in request.user_input.lower() or "nasıl" in request.user_input.lower():
            layer1_intent = "CONCEPTUAL_DEEPENING_PROBE"
        else:
            layer1_intent = "SOCRATIC_STEP_SCAFFOLDING"

        # -------------------------------------------------------------
        # KATMAN 2: Matematiksel CAS ve Hata Bağlamı
        # -------------------------------------------------------------
        cas_context = {
            "target_equation": request.target_equation,
            "solution_roots": request.solution_roots,
            "bug_id": request.diagnostic_bug.bug_id if request.diagnostic_bug else None,
            "offending_term": request.diagnostic_bug.offending_term if request.diagnostic_bug else None,
        }

        # -------------------------------------------------------------
        # KATMAN 3: Sokratik İletişimci (Soru / Açıklama Oranı >= 2.0)
        # -------------------------------------------------------------
        raw_dialogue = self._generate_socratic_response(request, layer1_intent)

        # -------------------------------------------------------------
        # KATMAN 4: Güvenlik Sübapı (Zero-Leakage Interceptor)
        # -------------------------------------------------------------
        final_output, was_intercepted = self.guardrail.enforce_zero_leakage(
            raw_dialogue, request.solution_roots
        )

        socratic_ratio = self.guardrail.calculate_socratic_ratio(final_output)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        return InnerMonologueLog(
            layer1_pedagogical_intent=layer1_intent,
            layer2_cas_context=cas_context,
            layer3_raw_dialogue=raw_dialogue,
            layer4_intercepted=was_intercepted,
            socratic_ratio=socratic_ratio,
            final_output=final_output,
            latency_ms=round(latency_ms, 2),
        )

    def _generate_socratic_response(self, request: SocraticRequest, intent: str) -> str:
        """
        Deterministik yüksek kaliteli Sokratik şablon sentezleyici.
        Daima yüksek Sokratik soru oranı (soru/açıklama >= 2.0) üretir.
        """
        # Jailbreak / doğrudan cevap talep girişimlerini saptama
        user_lower = request.user_input.lower()
        direct_demands = [
            "cevabı söyle", "cevabı ver", "x kaç", "x nedir", "çözümü ver", "çöz", "kök nedir",
            "hesapla", "dan mode", "ignore all previous", "jailbreak", "bana cevabı yaz",
            "ödevimi yap", "doğrudan cevap", "sınavdayım", "kökleri söyle",
        ]
        if any(d in user_lower for d in direct_demands):
            return (
                "Cevabı doğrudan vermek senin matematiksel keşif gücünü elinden alır, değil mi? "
                "Peki sence bu denklemde bilinmeyeni yalnız bırakmak için ilk adımı nasıl atabilirsin? "
                "Sol taraftaki terimleri incelediğinde dikkatini çeken ortak bir çarpan var mı?"
            )

        # Misconception remediation responses
        if request.diagnostic_bug:
            bug_id = request.diagnostic_bug.bug_id
            if bug_id == "BUG-QUAD-01":
                return (
                    "Eşitliğin sağ tarafı sıfırdan farklı bir sayı iken sıfır-çarpım kuralı geçerli olabilir mi? "
                    "Çarpımları bu sayıyı veren sonsuz sayıda sayı çifti olduğunu hatırlıyor musun? "
                    "Sence tüm terimleri önce sol tarafa toplayıp sağ tarafı sıfır yapsak nasıl olur?"
                )
            elif bug_id == "BUG-QUAD-02":
                return (
                    "Aklına gelen ilk pozitif kökü buldun, harika! "
                    "Peki karesi bu hedef sayıyı veren negatif bir ikiz kök de var olabilir mi? "
                    "Negatif bir sayının karesini aldığında işaretin ne olduğunu hatırlıyor musun?"
                )
            elif bug_id == "BUG-QUAD-03":
                return (
                    "İki terimin toplamının karesini alırken alan modelini gözünün önüne getirebilir misin? "
                    "Bir kenarı (x+a) olan karenin alanında sadece x² ve a² mi oluşur? "
                    "İki adet ax alanlı dikdörtgen terimini nereye yerleştirmeliyiz?"
                )
            elif bug_id == "BUG-QUAD-04":
                return (
                    "Her iki tarafı x ile böldüğünde x=0 ihtimalini gözden kaçırmış olabilir miyiz? "
                    "Sıfıra bölmenin matematikte tanımsız olduğunu biliyor musun? "
                    "Sadeleştirmek yerine tüm terimleri bir tarafa toplayıp ortak paranteze alsak hangi kökleri buluruz?"
                )
            elif bug_id == "BUG-QUAD-05":
                return (
                    "Formüldeki (-b) terimini yerine koyarken işaretlere dikkat ettin mi? "
                    "Eksi ile eksinin çarpımının artı olduğunu hatırlıyor musun? "
                    "Formüldeki b katsayısı negatif olduğuna göre en baştaki terimin işareti ne olmalıdır?"
                )

        # Affective Circuit Breaker
        if intent == "AFFECTIVE_CIRCUIT_BREAKER_EMPATHY":
            return (
                "Dur bir an, derin bir nefes alalım mı? "
                "Tarihte matematikçilerin de bu tür cebirsel düğümlerde yüzlerce yıl zorlandığını biliyor muydun? "
                "Şimdi bu adımı birlikte somut bir geometri modeliyle incelemeye ne dersin?"
            )

        # Standard step exploration
        return (
            "Yazdığın bu adımı önceki denklemle nasıl ilişkilendirdin? "
            "Eşitliğin iki tarafına da aynı işlemi uyguladığından emin misin? "
            "Bir sonraki hamlede hangi terimi sadeleştirmeyi hedefliyorsun?"
        )
