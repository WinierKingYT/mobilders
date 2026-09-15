"""
Socratic Method Scaffold Engine.
Bölüm 2 - Takılma Anında Sokratik Metot Anlatımı (Yöntemi Bulduran Akış).
Enforces 3-stage scaffolding:
Stage 1: Acceptance & Empathy (Durum Kabulü ve Empati)
Stage 2: Grounding Intuition (Somut Sezgi Örneği: Sayı Doğrusu / Terazi / Alan)
Stage 3: Student Self-Discovery Question (Kuralı Öğrenciye Bizzat Buldurma)
Zero-Leakage Invariant: Never gives away the solution root or final answer.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import re

from app.socratic.guardrail import ZeroLeakageGuardrail


class SocraticStage(str, Enum):
    EMPATHY = "EMPATHY"
    GROUNDING = "GROUNDING"
    SELF_DISCOVERY = "SELF_DISCOVERY"
    RESOLVED = "RESOLVED"


class SocraticScaffoldTemplate(BaseModel):
    template_id: str
    concept_name: str
    trigger_keywords: List[str]
    empathy_message: str
    grounding_example: str
    discovery_question: str
    expected_keywords: List[str]
    guidance_if_stuck: str


# 10 Core Socratic Scaffolding Templates for critical mathematical hurdles
SOCRATIC_TEMPLATES: Dict[str, SocraticScaffoldTemplate] = {
    "INEQUALITY_NEGATIVE_DIV": SocraticScaffoldTemplate(
        template_id="INEQUALITY_NEGATIVE_DIV",
        concept_name="Eşitsizlikte Negatif Sayıya Bölme / Çarpma",
        trigger_keywords=["<", ">", "<=", ">=", "eşitsizlik", "inequality", "-x", "-2x", "-3x"],
        empathy_message="Harika ilerliyorsun, sona çok yaklaştın! Sakin bir nefes al, buradaki kritik eşiği birlikte aşalım.",
        grounding_example="Basit bir sayı doğrusu düşünelim: 2 < 5 olduğunu biliyoruz. Peki her iki tarafı -1 ile çarparsak -2 ve -5 sayılarından hangisi daha sağda (büyük) kalır?",
        discovery_question="Sayı doğrusunda -2, -5'in sağındadır, yani -2 > -5 olur! Öyleyse bir eşitsizliği negatif bir sayıya böldüğümüzde eşitsizlik yönü hakkında ne söyleyebilirsin?",
        expected_keywords=["yön değiştir", "ters", "döner", "yönü değiş", "değişmeli", "değişir", "büyük olur", "flip", "reverse"],
        guidance_if_stuck="İpucu: Sayı doğrusunda negatif tarafa geçince küçük olan sayı sıfıra daha yakın olur. Eşitsizlik işareti ters mi dönmeli?",
    ),
    "DISTRIBUTIVE_NEGATIVE_SIGN": SocraticScaffoldTemplate(
        template_id="DISTRIBUTIVE_NEGATIVE_SIGN",
        concept_name="Parantez Önündeki Eksi İşaretini Dağıtma",
        trigger_keywords=["-(", "- (", "parantez", "dağıtma", "distributive"],
        empathy_message="Çok iyi odaklandın, parantezli cebirsel ifadelere gayet hakimsin! Şimdi küçük ama çok önemli bir işaret detayına bakalım.",
        grounding_example="Bir parantezin önündeki eksi işareti, aslında içerideki her bir terimi (-1) ile çarpmak demektir. Örneğin -(a + b) = (-1)*a + (-1)*b.",
        discovery_question="Öyleyse -(x - 4) ifadesinde eksi içeri dağıtıldığında hem x'in hem de -4'ün işaretleri nasıl bir değişime uğrar?",
        expected_keywords=["artı", "+4", "eksi", "işaret", "değiş", "-x+4", "-x + 4", "+ 4"],
        guidance_if_stuck="İpucu: Eksi ile eksinin çarpımı pozitiftir. -4 terimi parantezden çıkınca hangi işareti alır?",
    ),
    "FRACTION_COMMON_DENOMINATOR": SocraticScaffoldTemplate(
        template_id="FRACTION_COMMON_DENOMINATOR",
        concept_name="Kesirlerde Payda Eşitleme",
        trigger_keywords=["/", "kesir", "payda", "rasyonel", "fraction"],
        empathy_message="Harika geldin! Rasyonel ifadeler bazen kalabalık görünür ama temel mantığı çok sadedir.",
        grounding_example="Yarım elma ile çeyrek elmayı toplamak için önce ikisini de çeyrek dilimler cinsinden (aynı birimle) ifade ederiz: 1/2 + 1/4 = 2/4 + 1/4.",
        discovery_question="Paydaları farklı olan iki kesri tek bir kesir çizgisi altında toplamak veya çıkarmak için ilk olarak neyi eşitlemeliyiz?",
        expected_keywords=["payda", "ortak", "kat", "ekok", "okek", "eşitle", "genişlet"],
        guidance_if_stuck="İpucu: Kesirlerin altındaki sayıları ortak bir katta buluşturmamız gerekir. Bu kısma ne ad veriyorduk?",
    ),
    "FACTORING_DIFFERENCE_OF_SQUARES": SocraticScaffoldTemplate(
        template_id="FACTORING_DIFFERENCE_OF_SQUARES",
        concept_name="İki Kare Farkı Çarpanlara Ayırma",
        trigger_keywords=["x^2 -", "x² -", "kare farkı", "çarpan", "factor"],
        empathy_message="Tebrikler, cebirsel sadeleştirmenin en zarif kurallarından birine ulaştın!",
        grounding_example="Alanı a² olan bir kareden alanı b² olan küçük bir kareyi kestiğimizi hayal et. Kalan alan a² - b² = (a - b)(a + b) olarak ayrılır.",
        discovery_question="x² - 9 ifadesinde 9 = 3² olduğuna göre, bu iki kare farkını hangi iki parantezin çarpımı olarak yazabilirsin?",
        expected_keywords=["x-3", "x+3", "(x-3)(x+3)", "(x+3)(x-3)", "3"],
        guidance_if_stuck="İpucu: Biri eksi biri artı iki parantez: (x - ?)(x + ?). Soru işareti yerine hangi sayı gelmeli?",
    ),
    "EQUATION_CONSTANT_TRANSFER": SocraticScaffoldTemplate(
        template_id="EQUATION_CONSTANT_TRANSFER",
        concept_name="Terazi Modelinde Karşıya Terim Geçirme",
        trigger_keywords=["=", "denklem", "karşıya", "transfer", "yalnız"],
        empathy_message="Çok iyi gidiyorsun, bilinmeyeni yalnız bırakma yolunda sona bir adım kaldı!",
        grounding_example="Dengede duran iki kefeli bir terazi düşün: Sol kefede x + 6 kg, sağ kefede 14 kg var. Dengeyi bozmadan x'i yalnız bırakmak için her iki kefeden de 6 kg eksiltiriz.",
        discovery_question="Bir sayıyı eşitliğin diğer tarafına geçirdiğimizde terazinin dengesini korumak için sayının işareti neye dönüşür?",
        expected_keywords=["eksi", "ters", "zıt", "işaret", "değiş", "-", "çıkar"],
        guidance_if_stuck="İpucu: Teraziye eklenen fazlalığı yok etmek için zıt işlem yaparız. Artı ise diğer tarafa ne olarak geçer?",
    ),
    "ABSOLUTE_VALUE_SPLIT": SocraticScaffoldTemplate(
        template_id="ABSOLUTE_VALUE_SPLIT",
        concept_name="Mutlak Değer Açılımı ve Mesafe Sezgisi",
        trigger_keywords=["|", "mutlak", "absolute", "uzaklık"],
        empathy_message="Harika ilerleme! Mutlak değer sayının sıfıra olan uzaklığıdır ve uzaklık asla negatif olamaz.",
        grounding_example="Sayı doğrusunda sıfıra uzaklığı tam 5 birim olan sayılar hangileridir? Hem +5 hem de -5!",
        discovery_question="Öyleyse |x| = 5 denkleminde x'in alabileceği iki farklı değer sence nelerdir?",
        expected_keywords=["5", "-5", "±5", "+5", "eksi 5", "artı 5"],
        guidance_if_stuck="İpucu: Biri pozitif biri negatif iki sayı sıfıra aynı 5 birim mesafededir. Bu sayılar hangileridir?",
    ),
    "EXPONENT_NEGATIVE_POWER": SocraticScaffoldTemplate(
        template_id="EXPONENT_NEGATIVE_POWER",
        concept_name="Negatif Üs Kuralı ve Çarpmaya Göre Ters",
        trigger_keywords=["^-", "negatif üs", "kuvvet", "exponent"],
        empathy_message="Süper gidiyorsun! Üslü sayılarda kuvvetin negatif olması sayının negatif olduğu anlamına gelmez.",
        grounding_example="2³ = 8, 2² = 4, 2¹ = 2. Her adımda 2'ye bölüyoruz! Bu örüntüyü devam ettirirsek 2⁰ = 1 ve 2⁻¹ = 1/2 olur.",
        discovery_question="Öyleyse x⁻² ifadesini pay ve payda yer değiştirecek şekilde nasıl kesirli yazarsın?",
        expected_keywords=["1/x^2", "1 / x^2", "payda", "ters", "1/x²", "kesir"],
        guidance_if_stuck="İpucu: Negatif üs sayıyı tepe taklak eder; yani 1 bölü x'in karesi şeklinde yazılır.",
    ),
    "LOGARITHM_BASE_DOMAIN": SocraticScaffoldTemplate(
        template_id="LOGARITHM_BASE_DOMAIN",
        concept_name="Logaritma Tanım Kümesi ve Taban Koşulu",
        trigger_keywords=["log", "ln", "taban", "tanım kümesi"],
        empathy_message="Çok iyi odaklandın! Logaritma aslında 'hangi üs bu sayıyı verir?' sorusunun cevabıdır.",
        grounding_example="log_a(b) = c demek, a^c = b demektir. Pozitif bir sayının reel kuvvetleri daima pozitiftir. Ayrıca 1'in her kuvveti 1 olduğundan taban 1 olamaz.",
        discovery_question="Öyleyse log_a(x) ifadesinin geçerli olabilmesi için hem a tabanı hem de x içi nasıl sayılar olmalıdır?",
        expected_keywords=["pozitif", "sıfırdan büyük", "> 0", ">0", "1 olamaz", "pozitif reel"],
        guidance_if_stuck="İpucu: Negatif sayıların logaritması reel sayılarda tanımlı değildir; yani içerisi sıfırdan...",
    ),
    "TRIGONOMETRIC_PYTHAGOREAN": SocraticScaffoldTemplate(
        template_id="TRIGONOMETRIC_PYTHAGOREAN",
        concept_name="Birim Çemberde Pisagor Özdeşliği",
        trigger_keywords=["sin", "cos", "trigonometri", "özdeşlik", "birim çember"],
        empathy_message="Tebrikler, trigonometrinin en güçlü ve temel direğine ulaştın!",
        grounding_example="Birim çember üzerinde hipotenüsü 1 olan bir dik üçgende yatay kenar cos(x), dikey kenar sin(x)'tir. Pisagor teoremi: a² + b² = c².",
        discovery_question="Hipotenüsün uzunluğu 1 olduğuna göre, sin²(x) + cos²(x) toplamı her zaman kaça eşittir?",
        expected_keywords=["1", "bir", "one"],
        guidance_if_stuck="İpucu: 1'in karesi yine 1'dir. Hipotenüsün karesi olduğuna göre sonuç sabit bir tam sayıdır.",
    ),
    "CALCULUS_PRODUCT_RULE": SocraticScaffoldTemplate(
        template_id="CALCULUS_PRODUCT_RULE",
        concept_name="Çarpımın Türevi Kuralı",
        trigger_keywords=["türev", "derivative", "çarpım kuralı", "u*v", "f(x)*g(x)"],
        empathy_message="Zirve matematiğe çok yaklaştın! İki fonksiyonun çarpımının türevi basitçe türevlerin çarpımı değildir.",
        grounding_example="Kenarları u ve v olan bir dikdörtgenin alanı A = u*v'dir. İki kenar da aynı anda uzadığında alan değişimi u*dv + v*du şeklinde iki parçadan oluşur.",
        discovery_question="Öyleyse (u * v)' türevi için hangi kural geçerlidir: birincinin türevi çarpı ikinci artı... devamını sen tamamla?",
        expected_keywords=["ikincinin türevi", "u'v + uv'", "u.v'", "uv'", "birinci çarpı ikincinin"],
        guidance_if_stuck="İpucu: Sırayla türev alırız: Birincinin türevi × İkinci + Birinci × İkincinin türevi.",
    ),
}


class SocraticSessionState(BaseModel):
    session_id: str
    stage: SocraticStage = SocraticStage.EMPATHY
    template_id: str
    target_equation: str
    solution_roots: List[float] = Field(default_factory=list)
    confidence_gain: float = 0.0
    attempts: int = 0
    history: List[str] = Field(default_factory=list)


class SocraticStepOutput(BaseModel):
    stage: SocraticStage
    message: str
    is_resolved: bool = False
    confidence_bonus: float = 0.0
    requires_student_input: bool = False


class SocraticMethodScaffold:
    """
    Orchestrates the 3-stage Socratic scaffolding cycle with absolute zero root leakage.
    """

    def __init__(self, guardrail: Optional[ZeroLeakageGuardrail] = None):
        self.guardrail = guardrail or ZeroLeakageGuardrail()

    def select_template(
        self,
        target_equation: str,
        user_expression: str = "",
        bug_id: Optional[str] = None,
    ) -> SocraticScaffoldTemplate:
        """
        Selects the best fitting template from the 10 core mathematical hurdles.
        """
        combined = f"{target_equation} {user_expression} {bug_id or ''}".lower()

        # Specific matches
        if any(k in combined for k in ["<", ">", "<=", ">=", "inequality"]):
            return SOCRATIC_TEMPLATES["INEQUALITY_NEGATIVE_DIV"]
        if "-(" in combined or "- (" in combined:
            return SOCRATIC_TEMPLATES["DISTRIBUTIVE_NEGATIVE_SIGN"]
        if "/" in combined or "kesir" in combined:
            return SOCRATIC_TEMPLATES["FRACTION_COMMON_DENOMINATOR"]
        if "^2 -" in combined or "x² -" in combined or "kare farkı" in combined:
            return SOCRATIC_TEMPLATES["FACTORING_DIFFERENCE_OF_SQUARES"]
        if "|" in combined or "mutlak" in combined:
            return SOCRATIC_TEMPLATES["ABSOLUTE_VALUE_SPLIT"]
        if "^-" in combined or "negatif üs" in combined:
            return SOCRATIC_TEMPLATES["EXPONENT_NEGATIVE_POWER"]
        if "log" in combined or "ln" in combined:
            return SOCRATIC_TEMPLATES["LOGARITHM_BASE_DOMAIN"]
        if "türev" in combined or "derivative" in combined:
            return SOCRATIC_TEMPLATES["CALCULUS_PRODUCT_RULE"]
        if "sin" in combined or "cos" in combined:
            return SOCRATIC_TEMPLATES["TRIGONOMETRIC_PYTHAGOREAN"]

        # Default fallback
        return SOCRATIC_TEMPLATES["EQUATION_CONSTANT_TRANSFER"]

    def start_session(
        self,
        session_id: str,
        target_equation: str,
        user_expression: str = "",
        solution_roots: Optional[List[float]] = None,
        bug_id: Optional[str] = None,
    ) -> tuple[SocraticSessionState, SocraticStepOutput]:
        """
        Initializes Socratic scaffold at Stage 1 (EMPATHY).
        """
        template = self.select_template(target_equation, user_expression, bug_id)
        state = SocraticSessionState(
            session_id=session_id,
            stage=SocraticStage.EMPATHY,
            template_id=template.template_id,
            target_equation=target_equation,
            solution_roots=solution_roots or [],
        )

        sanitized_msg, _ = self.guardrail.enforce_zero_leakage(
            template.empathy_message, state.solution_roots
        )
        state.history.append(f"EMPATHY: {sanitized_msg}")

        output = SocraticStepOutput(
            stage=SocraticStage.EMPATHY,
            message=sanitized_msg,
            is_resolved=False,
            confidence_bonus=0.0,
            requires_student_input=False,
        )
        return state, output

    def advance(
        self,
        state: SocraticSessionState,
        student_input: str = "",
    ) -> tuple[SocraticSessionState, SocraticStepOutput]:
        """
        Advances the Socratic FSM based on current stage and student input.
        Guarantees zero leakage at every stage.
        """
        template = SOCRATIC_TEMPLATES.get(state.template_id, SOCRATIC_TEMPLATES["EQUATION_CONSTANT_TRANSFER"])

        if state.stage == SocraticStage.EMPATHY:
            # Stage 1 -> Stage 2 (GROUNDING)
            state.stage = SocraticStage.GROUNDING
            raw_msg = template.grounding_example
            sanitized_msg, _ = self.guardrail.enforce_zero_leakage(raw_msg, state.solution_roots)
            state.history.append(f"GROUNDING: {sanitized_msg}")
            return state, SocraticStepOutput(
                stage=SocraticStage.GROUNDING,
                message=sanitized_msg,
                is_resolved=False,
                confidence_bonus=0.0,
                requires_student_input=False,
            )

        elif state.stage == SocraticStage.GROUNDING:
            # Stage 2 -> Stage 3 (SELF_DISCOVERY)
            state.stage = SocraticStage.SELF_DISCOVERY
            raw_msg = template.discovery_question
            sanitized_msg, _ = self.guardrail.enforce_zero_leakage(raw_msg, state.solution_roots)
            state.history.append(f"SELF_DISCOVERY: {sanitized_msg}")
            return state, SocraticStepOutput(
                stage=SocraticStage.SELF_DISCOVERY,
                message=sanitized_msg,
                is_resolved=False,
                confidence_bonus=0.0,
                requires_student_input=True,
            )

        elif state.stage == SocraticStage.SELF_DISCOVERY:
            # Stage 3: Evaluate student self-discovery input
            state.attempts += 1
            clean_input = student_input.strip().lower()

            # Check for explicit negation indicating misconception
            negations = ["değişmez", "dönmez", "aynı kalır", "etkilenmez", "sabit kalır", "fark etmez", "not", "no change"]
            has_negation = any(neg in clean_input for neg in negations)

            # Check if student's answer contains any of expected keywords
            is_matched = (not has_negation) and any(kw.lower() in clean_input for kw in template.expected_keywords)

            if is_matched:
                state.stage = SocraticStage.RESOLVED
                state.confidence_gain = 0.10
                raw_msg = "Harikasın! Bu temel kuralı kendi başına keşfettin. Şimdi çözüm tahtasına dönüp bir sonraki adımı güvenle atabilirsin!"
                sanitized_msg, _ = self.guardrail.enforce_zero_leakage(raw_msg, state.solution_roots)
                state.history.append(f"RESOLVED: {sanitized_msg}")
                return state, SocraticStepOutput(
                    stage=SocraticStage.RESOLVED,
                    message=sanitized_msg,
                    is_resolved=True,
                    confidence_bonus=0.10,
                    requires_student_input=False,
                )
            else:
                # Student missed the discovery: provide gentle guidance without leaking solution
                raw_msg = template.guidance_if_stuck
                sanitized_msg, _ = self.guardrail.enforce_zero_leakage(raw_msg, state.solution_roots)
                state.history.append(f"GUIDANCE_RETRY: {sanitized_msg}")
                return state, SocraticStepOutput(
                    stage=SocraticStage.SELF_DISCOVERY,
                    message=sanitized_msg,
                    is_resolved=False,
                    confidence_bonus=0.0,
                    requires_student_input=True,
                )

        # Default fallback for already resolved state
        return state, SocraticStepOutput(
            stage=SocraticStage.RESOLVED,
            message="Kural başarıyla keşfedildi. Çözüme devam edebilirsiniz!",
            is_resolved=True,
            confidence_bonus=0.0,
            requires_student_input=False,
        )
