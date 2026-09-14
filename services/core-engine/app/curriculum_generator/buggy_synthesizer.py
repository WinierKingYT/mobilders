"""
Topic-Specific Misconception and Buggy Rule Synthesizer.
Generates comprehensive catalogs of student misconceptions (VanLehn Buggy Rules)
with pedagogical descriptions, detection patterns, and Socratic remediation directives.
"""

from __future__ import annotations
from typing import Dict, List, Any


class TopicBuggySynthesizer:
    """Synthesizes topic-specific Buggy Rules for advanced mathematical domains."""

    @staticmethod
    def get_buggy_rules_for_topic(topic: str) -> List[Dict[str, Any]]:
        t = topic.upper()
        if "LOG" in t:
            return TopicBuggySynthesizer._logarithm_buggy_rules()
        elif "TRIG" in t:
            return TopicBuggySynthesizer._trigonometry_buggy_rules()
        elif "LIM" in t:
            return TopicBuggySynthesizer._limits_buggy_rules()
        else:
            return TopicBuggySynthesizer._generic_advanced_buggy_rules(topic)

    @staticmethod
    def _logarithm_buggy_rules() -> List[Dict[str, Any]]:
        return [
            {
                "bug_id": "BUG-LOG-01",
                "name": "Logarithm Sum-Product Fallacy",
                "category": "PROPERTY_MISAPPLICATION",
                "flawed_rule": "log(a + b) = log(a) + log(b)",
                "correct_rule": "log(a * b) = log(a) + log(b)",
                "description": "Öğrenci logaritmanın toplam üzerine dağılma özelliği olduğunu zannederek log(a+b)=log(a)+log(b) yazar.",
                "remediation_directive": "Öğrenciye somut sayı değerleri vererek (örn: a=10, b=100) eşitliğin sağlanmadığını hissettir ve logaritmanın üs olduğunu hatırlat.",
            },
            {
                "bug_id": "BUG-LOG-02",
                "name": "Logarithm Quotient-Difference Inversion",
                "category": "PROPERTY_MISAPPLICATION",
                "flawed_rule": "log(a) / log(b) = log(a - b)",
                "correct_rule": "log(a / b) = log(a) - log(b)",
                "description": "İki logaritmanın oranını, argümanların farkının logaritması ile karıştırma.",
                "remediation_directive": "Taban değiştirme kuralı log_b(a) = log(a)/log(b) ile bölmenin logaritması log(a/b) arasındaki farkı görselleştir.",
            },
            {
                "bug_id": "BUG-LOG-03",
                "name": "Power Rule Misplacement",
                "category": "EXPONENT_ORDER_CONFUSION",
                "flawed_rule": "log(a^k) = (log(a))^k",
                "correct_rule": "log(a^k) = k * log(a)",
                "description": "Argümanın üssü olan k çarpanını logaritmanın kuvveti olarak dışarı alma.",
                "remediation_directive": "log(a^3) = log(a*a*a) açılımını yazdırarak 3*log(a) eşitliğini öğrencinin kendisinin türetmesini sağla.",
            },
            {
                "bug_id": "BUG-LOG-04",
                "name": "Negative Argument Domain Violation",
                "category": "DOMAIN_RESTRICTION_OMISSION",
                "flawed_rule": "log(-x) = -log(x)",
                "correct_rule": "log(x) tanımlı olması için x > 0 ve taban > 0, taban != 1 olmalıdır.",
                "description": "Negatif sayının logaritmasının reel sayılarda tanımsız olduğunu göz ardı etme.",
                "remediation_directive": "Hangi sayının reel kuvvetinin negatif bir sayı verebileceğini sorgulatarak reel tanım kümesi sınırını fark ettir.",
            },
        ]

    @staticmethod
    def _trigonometry_buggy_rules() -> List[Dict[str, Any]]:
        return [
            {
                "bug_id": "BUG-TRIG-01",
                "name": "Trigonometric Linearity Fallacy",
                "category": "LINEARITY_ASSUMPTION",
                "flawed_rule": "sin(a + b) = sin(a) + sin(b)",
                "correct_rule": "sin(a + b) = sin(a)cos(b) + cos(a)sin(b)",
                "description": "Trigonometrik fonksiyonların toplama üzerine dağıldığını varsayarak sin(a+b)=sin(a)+sin(b) yazma yanılgısı.",
                "remediation_directive": "a=30° ve b=60° değerlerini yerine koydurarak sin(90°)=1 iken sin(30°)+sin(60°) toplamının 1'e eşit olmadığını göster.",
            },
            {
                "bug_id": "BUG-TRIG-02",
                "name": "Pythagorean Sign Confusion",
                "category": "SIGN_AND_IDENTITY_ERROR",
                "flawed_rule": "sin^2(x) - cos^2(x) = 1",
                "correct_rule": "sin^2(x) + cos^2(x) = 1",
                "description": "Pisagor trigonometrik özdeşliğindeki artı işaretini eksi olarak kullanma veya cos(2x) açılımı ile karıştırma.",
                "remediation_directive": "Birim çember üzerindeki (cos x, sin x) koordinatlarını ve x² + y² = 1 Pisagor denklemini çizdir.",
            },
            {
                "bug_id": "BUG-TRIG-03",
                "name": "Radian to Degree Ratio Reversal",
                "category": "UNIT_CONVERSION_ERROR",
                "flawed_rule": "derece / 180 = radyan / pi yerine ters oran",
                "correct_rule": "D / 180 = R / pi",
                "description": "Açı birimlerini dönüştürürken pi ve 180 çarpanlarını ters yerleştirme.",
                "remediation_directive": "Tam bir çemberin 360 derece ve 2*pi radyan olduğu temel tanımını hatırlat.",
            },
            {
                "bug_id": "BUG-TRIG-04",
                "name": "Tangent Quotient Inversion",
                "category": "RATIO_INVERSION",
                "flawed_rule": "tan(x) = cos(x) / sin(x)",
                "correct_rule": "tan(x) = sin(x) / cos(x)",
                "description": "Tanjant ve kotanjant oranlarının pay ve paydasını ters yazma.",
                "remediation_directive": "Karşı kenar / komşu kenar tanımından sinüs ve kosinüs oranını adım adım kurdur.",
            },
        ]

    @staticmethod
    def _limits_buggy_rules() -> List[Dict[str, Any]]:
        return [
            {
                "bug_id": "BUG-LIM-01",
                "name": "Indeterminate 0/0 Zero Claim Fallacy",
                "category": "INDETERMINACY_MISCONCEPTION",
                "flawed_rule": "0 / 0 = 0 veya tanımsız deyip limiti hesaplamayı bırakma",
                "correct_rule": "0/0 belirsizlik durumunda çarpanlara ayırma, sadeleştirme veya L'Hopital uygulanır",
                "description": "Öğrenci 0/0 sonucuna ulaştığında limitin 0 olduğunu veya mevcut olmadığını iddia eder.",
                "remediation_directive": "Limitin fonksiyonun x noktasındaki değeri değil, o noktaya yaklaşırken aldığı eğilim olduğunu vurgula; (x-a) çarpanını sadeleştirmesini iste.",
            },
            {
                "bug_id": "BUG-LIM-02",
                "name": "Premature Denominator Cancellation",
                "category": "ALGEBRAIC_SLIP",
                "flawed_rule": "lim (f(x)/g(x)) = (lim f) / 0 = sonsuz doğrudan yazma",
                "correct_rule": "Payda sıfır iken payın işaretine ve tek/çift katlı sıfırına bakılmalıdır",
                "description": "Pay sıfırdan farklı bir sayı iken paydanın sıfır olması durumunda sağdan ve soldan limitin işaret farkını atlayarak doğrudan sonsuz yazma.",
                "remediation_directive": "Sağdan (x -> a+) ve soldan (x -> a-) yaklaşım değer tablosu oluşturarak işaret kontrolü yaptır.",
            },
            {
                "bug_id": "BUG-LIM-03",
                "name": "One-Sided Limit Existence Assumption",
                "category": "EXISTENCE_CRITERIA_OMISSION",
                "flawed_rule": "Soldan limit var ise iki taraflı limit de doğrudan vardır",
                "correct_rule": "lim f(x) vardır <=> lim_{x->a-} f(x) = lim_{x->a+} f(x)",
                "description": "Sağdan ve soldan limitlerin eşitliğini doğrulamadan genel limitin var olduğunu varsayma.",
                "remediation_directive": "Parçalı fonksiyonda sağ ve sol limit değerlerini yan yana yazarak eşit olup olmadıklarını teyit ettir.",
            },
        ]

    @staticmethod
    def _generic_advanced_buggy_rules(topic: str) -> List[Dict[str, Any]]:
        return [
            {
                "bug_id": f"BUG-{topic[:4].upper()}-01",
                "name": f"{topic} Distributive Fallacy",
                "category": "LINEARITY_FALLACY",
                "flawed_rule": f"f(x + y) = f(x) + f(y) for non-linear {topic}",
                "correct_rule": "Fonksiyonel bağıntılar ve tanım kuralları uygulanmalıdır.",
                "description": f"{topic} konusunda doğrusal olmayan fonksiyonun toplama üzerine dağıldığı yanılgısı.",
                "remediation_directive": "Temel tanım ve özellikleri adım adım yazdırarak teyit et.",
            }
        ]
