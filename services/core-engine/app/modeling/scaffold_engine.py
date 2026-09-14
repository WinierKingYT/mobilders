import time
import re
from typing import Optional, Dict, Any, List
import sympy as sp
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.models.schemas import DiagnosticPayload
from app.modeling.models import (
    ModelingProblemSpec,
    ProblemCategory,
    ModelingStage,
    SchematicType,
    SchematicDiagramSpec,
    ScaffoldStepRequest,
    ScaffoldStepResponse,
)


class SocraticModelingScaffoldEngine:
    """
    3 Aşamalı Sokratik Modelleme İskelesi Motoru (Scaffold Engine).
    Metin halindeki problemleri Değişken Tanımlama -> Denklem Kurma -> Adım Adım Çözüm
    aşamalarında denetler, Sokratik rehberlik sunar ve çözümü asla sızdırmaz.
    """

    def __init__(
        self,
        cas_engine: Optional[SymbolicEquivalenceEngine] = None,
        detector: Optional[QuadraticMisconceptionDetector] = None,
    ):
        self.cas = cas_engine or SymbolicEquivalenceEngine()
        self.detector = detector or QuadraticMisconceptionDetector(self.cas)
        self.problem_bank: Dict[str, ModelingProblemSpec] = self._init_problem_bank()

    def _init_problem_bank(self) -> Dict[str, ModelingProblemSpec]:
        """Standart modelleme problemlerini yükler."""
        bank = [
            ModelingProblemSpec(
                id="PROB_AGE_01",
                category=ProblemCategory.AGE,
                node_id="N04",
                title="Babanın ve Oğlunun Yaşları",
                story_text="Bir babanın bugünkü yaşı, oğlunun bugünkü yaşının 3 katıdır. 5 yıl sonra babanın ve oğlunun yaşları toplamı 50 olacaktır. Oğlunun bugünkü yaşı kaçtır?",
                target_unknown_description="Oğlunun bugünkü yaşı",
                canonical_variable="x",
                acceptable_variables=["x", "y", "a", "o"],
                canonical_equation_str="(x + 5) + (3*x + 5) = 50",
                alternative_equations=["4*x + 10 = 50", "3*x + x + 10 = 50"],
                canonical_solution_str="10",
                domain_constraints={"positive": True, "integer_only": True, "min_val": 1, "max_val": 120},
                socratic_hints={
                    "STAGE_1": "Babanın yaşı oğlunun yaşının 3 katı olduğuna göre, oğlunun yaşına x dersek babanın yaşı kaç x olur?",
                    "STAGE_2": "5 yıl sonra hem oğul hem de baba 5 yaş büyüyecektir. İkisinin 5 yıl sonraki yaşlarını toplayıp 50'ye eşitle.",
                    "STAGE_3": "Denklemde önce sabit terimleri karşı taraftan çıkar, sonra her iki tarafı bilinmeyenin katsayısına bölerek x'i yalnız bırak.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.PERCENTAGE_BAR,
                    title="Yaş Zaman Çizgisi",
                    data={"timeline_years": [0, 5], "actors": ["Oğul: x", "Baba: 3x"]},
                ),
            ),
            ModelingProblemSpec(
                id="PROB_MOTION_01",
                category=ProblemCategory.MOTION,
                node_id="N04",
                title="Karşıt Yönlü İki Aracın Karşılaşması",
                story_text="A ve B şehirleri arasındaki mesafe 400 kilometredir. Saatteki hızları 60 km ve 40 km olan iki otomobil aynı anda birbirlerine doğru yola çıkıyor. Kaç saat sonra karşılaşırlar?",
                target_unknown_description="Araçların karşılaşma süresi (saat)",
                canonical_variable="t",
                acceptable_variables=["t", "x", "s"],
                canonical_equation_str="(60 + 40) * t = 400",
                alternative_equations=["100 * t = 400", "60*t + 40*t = 400"],
                canonical_solution_str="4",
                domain_constraints={"positive": True, "integer_only": False, "min_val": 0.1, "max_val": 100},
                socratic_hints={
                    "STAGE_1": "Bizden istenen geçen zamandır. Süreyi t değişkeni olarak belirleyelim.",
                    "STAGE_2": "İki araç birbirine doğru geldiğinde saatte birbirlerine ne kadar yaklaşırlar? Bağıl hızları toplamı ile sürenin çarpımı toplam yolu vermelidir.",
                    "STAGE_3": "100 * t = 400 denkleminde t'yi yalnız bırakmak için iki tarafı 100'e böl.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.MOTION_TIMELINE,
                    title="Hareket ve Karşılaşma Şeması",
                    data={
                        "distance_km": 400,
                        "vehicle_1": {"name": "A Aracı", "speed": 60, "direction": "RIGHT"},
                        "vehicle_2": {"name": "B Aracı", "speed": 40, "direction": "LEFT"},
                        "meeting_point_ratio": 0.6,
                    },
                ),
            ),
            ModelingProblemSpec(
                id="PROB_MIXTURE_01",
                category=ProblemCategory.MIXTURE,
                node_id="N04",
                title="Tuzlu Su Karışımlarının Birleşimi",
                story_text="Tuz oranı %20 olan 40 litre tuzlu su ile tuz oranı %50 olan 60 litre tuzlu su karıştırılıyor. Yeni karışımın tuz oranı yüzde kaç olur?",
                target_unknown_description="Yeni karışımın tuz yüzdesi (%)",
                canonical_variable="x",
                acceptable_variables=["x", "y", "c", "p"],
                canonical_equation_str="40 * 20 + 60 * 50 = (40 + 60) * x",
                alternative_equations=["800 + 3000 = 100 * x", "100 * x = 3800"],
                canonical_solution_str="38",
                domain_constraints={"positive": True, "integer_only": False, "min_val": 0, "max_val": 100},
                socratic_hints={
                    "STAGE_1": "Bilinmeyenimiz yeni karışımın tuz yüzdesidir; buna x diyelim.",
                    "STAGE_2": "Birinci kaptaki saf tuz (40 * %20) ile ikinci kaptaki saf tuzun (60 * %50) toplamı, yeni toplam hacimdeki (100 L) tuz miktarına eşit olmalıdır.",
                    "STAGE_3": "800 + 3000 = 100x eşitliğini sadeleştirip x'i bul.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.MIXTURE_VESSEL,
                    title="Kap Karışım Şeması",
                    data={
                        "vessel_1": {"volume": 40, "percentage": 20, "solute": "Tuz"},
                        "vessel_2": {"volume": 60, "percentage": 50, "solute": "Tuz"},
                        "result_vessel": {"volume": 100, "expected_percentage": 38},
                    },
                ),
            ),
            ModelingProblemSpec(
                id="PROB_WORK_01",
                category=ProblemCategory.WORK,
                node_id="N04",
                title="Birlikte Çalışan İşçiler",
                story_text="Bir işi Ali tek başına 6 günde, Veli ise 12 günde bitirebilmektedir. İkisi birlikte çalışırlarsa aynı işi kaç günde bitirirler?",
                target_unknown_description="İşin birlikte bitirilme süresi (gün)",
                canonical_variable="t",
                acceptable_variables=["t", "x", "g"],
                canonical_equation_str="1/6 + 1/12 = 1/t",
                alternative_equations=["3/12 = 1/t", "1/4 = 1/t", "t/6 + t/12 = 1"],
                canonical_solution_str="4",
                domain_constraints={"positive": True, "integer_only": False, "min_val": 0.1, "max_val": 30},
                socratic_hints={
                    "STAGE_1": "Birlikte bitirme süresine t diyelim.",
                    "STAGE_2": "Ali 1 günde işin 1/6'sını, Veli ise 1/12'sini yapar. Bir günde birlikte yaptıkları iş 1/t'ye eşit olmalıdır.",
                    "STAGE_3": "1/6 + 1/12 toplamında payda eşitleyip ters çevir.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.WORK_PROGRESS,
                    title="İşçi Kapasite Dağılımı",
                    data={"worker_1": {"name": "Ali", "rate": "1/6"}, "worker_2": {"name": "Veli", "rate": "1/12"}},
                ),
            ),
            ModelingProblemSpec(
                id="PROB_PERCENT_01",
                category=ProblemCategory.PERCENTAGE,
                node_id="N04",
                title="Ardışık Zam ve İndirim",
                story_text="Bir mağaza bir cekete maliyet üzerinden %30 kâr koyarak satış fiyatı belirliyor. Sezon sonunda bu satış fiyatı üzerinden %20 indirim uyguluyor. Mağazanın net kâr oranı yüzde kaçtır?",
                target_unknown_description="Net kâr oranı (%)",
                canonical_variable="k",
                acceptable_variables=["k", "x", "y", "p"],
                canonical_equation_str="100 * 1.30 * 0.80 = 100 + k",
                alternative_equations=["104 = 100 + k", "1.30 * 0.80 = 1 + k/100"],
                canonical_solution_str="4",
                domain_constraints={"positive": True, "integer_only": False, "min_val": -100, "max_val": 500},
                socratic_hints={
                    "STAGE_1": "Net kâr oranına k diyelim. Başlangıç maliyetini hesap kolaylığı için 100 TL kabul edebilirsin.",
                    "STAGE_2": "%30 kârlı fiyat 100 * 1.30'dur. Bu fiyata %20 indirim uygulandığında 0.80 ile çarpılır. Eşitliğin sağ tarafı 100 + k olmalıdır.",
                    "STAGE_3": "1.30 * 0.80 = 1.04 değerinden kâr oranını tespit et.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.PERCENTAGE_BAR,
                    title="Fiyat Değişim Çubuğu",
                    data={"stages": ["Maliyet: 100", "+%30 Kâr: 130", "-%20 İndirim: 104"]},
                ),
            ),
            ModelingProblemSpec(
                id="PROB_OPTIMIZATION_01",
                category=ProblemCategory.OPTIMIZATION,
                node_id="N38",
                title="Bahçe Alanını Maksimum Yapma",
                story_text="Çevresi 60 metre olan dikdörtgen biçimindeki bir bahçenin alanının en büyük olması için bir kenar uzunluğu kaç metre olmalıdır?",
                target_unknown_description="Maksimum alan veren kenar uzunluğu (metre)",
                canonical_variable="x",
                acceptable_variables=["x", "a", "k"],
                canonical_equation_str="x * (30 - x) = 225",
                alternative_equations=["-x**2 + 30*x = 225", "-x^2 + 30*x = 225", "x = 15"],
                canonical_solution_str="15",
                domain_constraints={"positive": True, "integer_only": False, "min_val": 0.1, "max_val": 30},
                socratic_hints={
                    "STAGE_1": "Bir kenara x diyelim. Çevre 60 ise, iki komşu kenarın toplamı 30 olur.",
                    "STAGE_2": "Diğer kenar (30 - x) olur. Alan f(x) = x * (30 - x) fonksiyonudur. Tepe noktası apsisi r = -b / (2a) ile maksimum kenarı bul.",
                    "STAGE_3": "f(x) = -x² + 30x parabolünde tepe noktası apsisi r = -30 / (2 * -1) değerini hesapla.",
                },
                schematic=SchematicDiagramSpec(
                    diagram_type=SchematicType.PERCENTAGE_BAR,
                    title="Geometrik Alan Optimizasyonu",
                    data={"perimeter": 60, "half_perimeter": 30, "optimal_shape": "Kare: 15x15"},
                ),
            ),
        ]
        return {p.id: p for p in bank}

    def evaluate_step(self, request: ScaffoldStepRequest) -> ScaffoldStepResponse:
        """
        Öğrencinin modelleme adımını denetler ve Sokratik geri bildirim üretir.
        """
        t0 = time.perf_counter()
        problem = self.problem_bank.get(request.problem_id)
        if not problem:
            return ScaffoldStepResponse(
                problem_id=request.problem_id,
                stage=request.stage,
                is_valid=False,
                stage_completed=False,
                socratic_feedback=f"Hata: '{request.problem_id}' kimlikli problem bulunamadı.",
            )

        if request.stage == ModelingStage.STAGE_1_VARIABLE:
            resp = self._evaluate_stage_1(problem, request)
        elif request.stage == ModelingStage.STAGE_2_EQUATION:
            resp = self._evaluate_stage_2(problem, request)
        elif request.stage == ModelingStage.STAGE_3_SOLVE:
            resp = self._evaluate_stage_3(problem, request)
        else:
            resp = ScaffoldStepResponse(
                problem_id=request.problem_id,
                stage=request.stage,
                is_valid=False,
                stage_completed=False,
                socratic_feedback="Geçersiz modelleme aşaması.",
            )

        resp.analysis_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return resp

    def _evaluate_stage_1(self, problem: ModelingProblemSpec, request: ScaffoldStepRequest) -> ScaffoldStepResponse:
        """Aşama 1: Değişken Tanımlama."""
        raw_input = request.student_input.strip().lower()
        # Temel değişken sembollerini veya metin atamalarını analiz et (örn: 'x', 'x = oğul', 't')
        var_match = re.search(r"\b([a-zA-Z])\b", raw_input)
        chosen_var = var_match.group(1).lower() if var_match else raw_input

        if chosen_var in [v.lower() for v in problem.acceptable_variables]:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_1_VARIABLE,
                is_valid=True,
                stage_completed=True,
                socratic_feedback=f"Harika bir başlangıç! '{chosen_var}' değişkenini '{problem.target_unknown_description}' olarak belirledik. Şimdi metindeki ilişkileri birleştiren matematiksel denklemi kuralım.",
                next_stage=ModelingStage.STAGE_2_EQUATION,
                schematic_state_update={"active_variable": chosen_var},
            )
        else:
            hint = problem.socratic_hints.get("STAGE_1", "Problemin bilinmeyenine x veya t gibi bir değişken ata.")
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_1_VARIABLE,
                is_valid=False,
                stage_completed=False,
                socratic_feedback=f"Seçtiğin değişken veya ifade tam anlaşılamadı. {hint}",
            )

    def _evaluate_stage_2(self, problem: ModelingProblemSpec, request: ScaffoldStepRequest) -> ScaffoldStepResponse:
        """Aşama 2: Denklem Kurma ve Buggy Rule Denetimi."""
        raw_input = request.student_input.strip()

        # 1. Önce kavram yanılgısı (Buggy Rule) var mı kontrol et
        bug = self.detector.detect(
            user_step_str=raw_input,
            previous_step_str=problem.story_text,
            target_equation_str=problem.canonical_equation_str,
        )
        if bug:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_2_EQUATION,
                is_valid=False,
                stage_completed=False,
                detected_bug=bug,
                socratic_feedback=f"{bug.remediation_directive}",
            )

        # 2. Denklem geçerliliği ve denkliği (CAS)
        is_equiv = False
        # Doğrudan kanonik denkleme veya alternatiflere denk mi?
        if "=" in raw_input and "=" in problem.canonical_equation_str:
            is_equiv = self.cas.verify_equivalence(raw_input, problem.canonical_equation_str)
            if not is_equiv:
                for alt_eq in problem.alternative_equations:
                    if self.cas.verify_equivalence(raw_input, alt_eq):
                        is_equiv = True
                        break
        elif raw_input == problem.canonical_equation_str or raw_input in problem.alternative_equations:
            is_equiv = True

        if is_equiv:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_2_EQUATION,
                is_valid=True,
                stage_completed=True,
                socratic_feedback="Mükemmel modelleme! Kurduğun matematiksel eşitlik problem metnini eksiksiz yansıtıyor. Şimdi son aşamaya geçip denklemi adım adım çözelim.",
                next_stage=ModelingStage.STAGE_3_SOLVE,
                schematic_state_update={"equation_locked": True},
            )
        else:
            hint = problem.socratic_hints.get("STAGE_2", "Metindeki eşitliği tekrar gözden geçir.")
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_2_EQUATION,
                is_valid=False,
                stage_completed=False,
                socratic_feedback=f"Kurduğun eşitlik problemdeki verilerle tam uyuşmuyor. {hint}",
            )

    def _evaluate_stage_3(self, problem: ModelingProblemSpec, request: ScaffoldStepRequest) -> ScaffoldStepResponse:
        """Aşama 3: Çözüm ve Gerçek Dünya Kısıtı Denetimi (Zero Leakage)."""
        raw_input = request.student_input.strip()

        # Buggy Rule kontrolü (Örn: BUG-PROB-10 negatif kök)
        bug = self.detector.detect(
            user_step_str=raw_input,
            previous_step_str=problem.canonical_equation_str,
            target_equation_str=problem.canonical_solution_str,
        )
        if bug:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_3_SOLVE,
                is_valid=False,
                stage_completed=False,
                detected_bug=bug,
                socratic_feedback=bug.remediation_directive,
            )

        # Temizle ve x = 10 veya 10 formundaki yanıtı ayrıştır
        match = re.search(r"=\s*([-\d\.]+)", raw_input)
        num_str = match.group(1) if match else raw_input.replace("x", "").replace("t", "").replace("=", "").strip()

        is_correct = False
        domain_ok = True
        domain_msg = None

        try:
            val = float(num_str)
            target_val = float(problem.canonical_solution_str)

            # Gerçek dünya kısıtlarını kontrol et
            constraints = problem.domain_constraints
            if constraints.get("positive", True) and val <= 0:
                domain_ok = False
                domain_msg = "Bulduğun değer negatif veya sıfır. Gerçek hayatta bu büyüklük pozitif olmalıdır."
            elif constraints.get("integer_only", False) and not (val.is_integer() or abs(val - round(val)) < 1e-5):
                domain_ok = False
                domain_msg = "Bu problem için sonuç bir tam sayı olmalıdır."
            elif constraints.get("min_val") is not None and val < constraints["min_val"]:
                domain_ok = False
                domain_msg = f"Bulunan değer minimum sınırın ({constraints['min_val']}) altında."
            elif constraints.get("max_val") is not None and val > constraints["max_val"]:
                domain_ok = False
                domain_msg = f"Bulunan değer maksimum sınırın ({constraints['max_val']}) üstünde."

            if abs(val - target_val) < 1e-4:
                is_correct = True
        except Exception:
            is_correct = False

        if is_correct and domain_ok:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_3_SOLVE,
                is_valid=True,
                stage_completed=True,
                domain_valid=True,
                socratic_feedback="Tebrikler! Problemi 3 aşamalı olarak modelledin, denklemi doğru kurdun ve gerçek hayat şartlarına uygun doğru sonuca ulaştın.",
                schematic_state_update={"completed": True},
            )
        elif not domain_ok:
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_3_SOLVE,
                is_valid=False,
                stage_completed=False,
                domain_valid=False,
                socratic_feedback=f"Dikkat: {domain_msg} Lütfen adımlarını kontrol et.",
            )
        else:
            hint = problem.socratic_hints.get("STAGE_3", "İşlemleri sırasıyla tekrar yap.")
            # Zero-Leakage Shield: Asla hedef sayıyı feedback içine koyma!
            return ScaffoldStepResponse(
                problem_id=problem.id,
                stage=ModelingStage.STAGE_3_SOLVE,
                is_valid=False,
                stage_completed=False,
                domain_valid=domain_ok,
                socratic_feedback=f"Hesaplamada bir işlem hatası görünüyor. {hint}",
            )
