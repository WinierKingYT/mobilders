"""
Kişisel Öğrenme Motoru (PLE) - Seviye 18: Sayma, Kombinatorik, Olasılık ve İstatistik Motoru
Matematiksel kesinlik, pedagojik Sokratik iskele (Zero-Leakage) ve Monte Carlo simülasyonu.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable


# =====================================================================
# 1. KOMBİNATÖRİK VE SAYMA İLKELERİ
# =====================================================================

def factorial(n: int) -> int:
    """Faktöriyel hesabı: n! = n * (n-1) * ... * 1, 0! = 1."""
    if n < 0:
        raise ValueError(f"Negatif sayıların faktöriyeli tanımlı değildir: {n}")
    if n > 10000:
        raise ValueError(f"Faktöriyel için n en fazla 10000 olabilir: {n}")
    return math.factorial(n)


def permutation(n: int, r: int) -> int:
    """
    Doğrusal permütasyon P(n, r) = n! / (n - r)!.
    Sıralı seçim durumlarında kullanılır.
    """
    if n < 0 or r < 0:
        raise ValueError(f"n ve r negatif olamaz: n={n}, r={r}")
    if n > 10000 or r > 10000:
        raise ValueError(f"n ve r en fazla 10000 olabilir: n={n}, r={r}")
    if r > n:
        return 0
    return math.perm(n, r)


def circular_permutation(n: int) -> int:
    """
    Dairesel (dönel) permütasyon: (n - 1)!.
    Dönel simetri nedeniyle 1 eleman sabitlenir.
    """
    if n <= 0:
        raise ValueError(f"Dairesel dizilim için eleman sayısı pozitif olmalıdır: {n}")
    if n > 10000:
        raise ValueError(f"Dairesel dizilim için n en fazla 10000 olabilir: {n}")
    return factorial(n - 1)


def repeated_permutation(n: int, counts: List[int]) -> int:
    """
    Tekrarlı permütasyon: n! / (n1! * n2! * ... * nk!).
    Özdeş elemanların dizilim sayısını hesaplar.
    """
    if n < 0:
        raise ValueError(f"n negatif olamaz: {n}")
    if n > 10000:
        raise ValueError(f"n en fazla 10000 olabilir: {n}")
    if sum(counts) != n:
        raise ValueError(f"Grup eleman sayıları toplamı ({sum(counts)}) n'e ({n}) eşit olmalıdır!")
    for c in counts:
        if c < 0:
            raise ValueError(f"Grup eleman adedi negatif olamaz: {c}")

    numerator = factorial(n)
    denominator = 1
    for c in counts:
        denominator *= factorial(c)
    return numerator // denominator


def combination(n: int, r: int) -> int:
    """
    Kombinasyon C(n, r) = n! / (r! * (n - r)!).
    Sırasız seçim (küme alt kümesi, komite vb.) durumlarında kullanılır.
    """
    if n < 0 or r < 0:
        raise ValueError(f"n ve r negatif olamaz: n={n}, r={r}")
    if n > 10000 or r > 10000:
        raise ValueError(f"n ve r en fazla 10000 olabilir: n={n}, r={r}")
    if r > n:
        return 0
    return math.comb(n, r)


def pascal_row(n: int) -> List[int]:
    """Pascal üçgeninin n. satırını [C(n, 0), C(n, 1), ..., C(n, n)] döndürür."""
    if n < 0:
        raise ValueError(f"Satır indeksi negatif olamaz: {n}")
    if n > 1000:
        raise ValueError(f"Pascal satırı için n en fazla 1000 olabilir: {n}")
    return [combination(n, r) for r in range(n + 1)]


def verify_pascal_identity(n: int, r: int) -> bool:
    """Pascal özdeşliği: C(n, r) + C(n, r + 1) == C(n + 1, r + 1)."""
    if n < 0 or r < 0 or r >= n:
        return False
    lhs = combination(n, r) + combination(n, r + 1)
    rhs = combination(n + 1, r + 1)
    return lhs == rhs


def binomial_term(n: int, r: int, a: float = 1.0, b: float = 1.0) -> Dict[str, Any]:
    """
    (a*x + b*y)^n açılımında baştan (r + 1). terimin katsayısı ve dereceleri:
    T_(r+1) = C(n, r) * a^(n-r) * b^r * x^(n-r) * y^r.
    """
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError("Katsayılar 'a' ve 'b' sonlu reel sayılar olmalıdır.")
    if n < 0 or r < 0 or r > n:
        raise ValueError(f"Geçersiz binom terim indeksleri: n={n}, r={r}")
    if n > 1000:
        raise ValueError(f"Binom açılımı için n en fazla 1000 olabilir: {n}")

    comb_coeff = combination(n, r)
    numeric_coeff = comb_coeff * (a ** (n - r)) * (b ** r)
    x_power = n - r
    y_power = r

    return {
        "term_index": r + 1,
        "n": n,
        "r": r,
        "combination_coeff": comb_coeff,
        "numeric_coefficient": numeric_coeff,
        "x_power": x_power,
        "y_power": y_power,
        "representation": f"{numeric_coeff} * x^{x_power} * y^{y_power}",
    }


def geometric_combinations_triangles(total_points: int, collinear_sets: Optional[List[int]] = None) -> int:
    """
    Doğrusal noktalar içeren bir düzlemde oluşturulabilecek üçgen sayısı:
    C(n, 3) - sum(C(k_i, 3))
    """
    if total_points < 3:
        return 0
    total = combination(total_points, 3)
    if collinear_sets:
        for k in collinear_sets:
            if k >= 3:
                total -= combination(k, 3)
    return max(0, total)


# =====================================================================
# 2. OLASILIK MOTORU (KLASİK, KOŞULLU, BAYES, BEKLENEN DEĞER)
# =====================================================================

def classical_probability(favorable: int, sample_space: int) -> float:
    """
    Eş olumlu örnek uzayda klasik olasılık: P(A) = s(A) / s(E).
    """
    if sample_space <= 0:
        raise ValueError(f"Örnek uzay eleman sayısı pozitif olmalıdır: {sample_space}")
    if favorable < 0 or favorable > sample_space:
        raise ValueError(f"İstenen durum sayısı ({favorable}) [0, {sample_space}] aralığında olmalıdır!")
    return favorable / sample_space


def complement_probability(p_a: float) -> float:
    """Tümleyen olasılık: P(A') = 1 - P(A)."""
    if not math.isfinite(p_a) or not (0.0 <= p_a <= 1.0):
        raise ValueError(f"Olasılık değeri [0, 1] aralığında olmalıdır: {p_a}")
    return 1.0 - p_a


def union_probability(p_a: float, p_b: float, p_intersection: float = 0.0) -> float:
    """
    Birleşim olasılığı (Veya Kuralı):
    P(A ∪ B) = P(A) + P(B) - P(A ∩ B).
    Ayrık olaylarda P(A ∩ B) = 0.
    """
    for name, p in [("P(A)", p_a), ("P(B)", p_b), ("P(A∩B)", p_intersection)]:
        if not math.isfinite(p) or not (0.0 <= p <= 1.0):
            raise ValueError(f"{name} değeri [0, 1] aralığında olmalıdır: {p}")
    if p_intersection > min(p_a, p_b):
        raise ValueError(f"Kesişim olasılığı ({p_intersection}) P(A) ({p_a}) ve P(B) ({p_b})'den büyük olamaz!")

    p_union = p_a + p_b - p_intersection
    return min(1.0, max(0.0, p_union))


def conditional_probability(p_intersection: float, p_condition: float) -> float:
    """
    Koşullu olasılık: P(A|B) = P(A ∩ B) / P(B).
    """
    if not math.isfinite(p_condition) or p_condition <= 0.0 or p_condition > 1.0:
        raise ValueError(f"Koşul olasılığı (0, 1] aralığında olmalıdır: {p_condition}")
    if not math.isfinite(p_intersection) or p_intersection < 0.0 or p_intersection > p_condition:
        raise ValueError(f"P(A ∩ B) ({p_intersection}) değeri [0, P(B)={p_condition}] aralığında olmalıdır!")
    return p_intersection / p_condition


def bayes_theorem(prior_b: float, likelihood_a_given_b: float, marginal_a: float) -> float:
    """
    Bayes Teoremi: P(B|A) = (P(A|B) * P(B)) / P(A).
    """
    if not (math.isfinite(prior_b) and math.isfinite(likelihood_a_given_b) and math.isfinite(marginal_a)):
        raise ValueError("Olasılık parametreleri sonlu reel sayılar olmalıdır.")
    if marginal_a <= 0.0:
        raise ValueError(f"Marjinal kanıt olasılığı P(A) pozitif olmalıdır: {marginal_a}")
    numerator = likelihood_a_given_b * prior_b
    posterior = numerator / marginal_a
    return min(1.0, max(0.0, posterior))


def bayes_multi_hypothesis(priors: List[float], likelihoods: List[float], target_index: int) -> Dict[str, Any]:
    """
    Çok hipotezli Bayes kuralı:
    P(B_i | A) = [P(A | B_i) * P(B_i)] / sum_j [P(A | B_j) * P(B_j)].
    """
    if len(priors) != len(likelihoods):
        raise ValueError("Priors ve likelihoods listeleri eşit uzunlukta olmalıdır.")
    if not (0 <= target_index < len(priors)):
        raise IndexError(f"Geçersiz hedef hipotez indeksi: {target_index}")
    if not (all(math.isfinite(p) for p in priors) and all(math.isfinite(l) for l in likelihoods)):
        raise ValueError("Önsel ve olabilirlik değerleri sonlu reel sayılar olmalıdır.")
    if abs(sum(priors) - 1.0) > 1e-4:
        raise ValueError(f"Önsel olasılıklar (priors) toplamı 1 olmalıdır: {sum(priors)}")

    # Toplam olasılık yasası: P(A) = sum(P(A|B_j) * P(B_j))
    marginal_evidence = sum(p * l for p, l in zip(priors, likelihoods))
    if marginal_evidence <= 0:
        raise ValueError("Toplam kanıt olasılığı sıfır olamaz.")

    target_numerator = priors[target_index] * likelihoods[target_index]
    posterior = target_numerator / marginal_evidence

    return {
        "marginal_evidence": marginal_evidence,
        "target_index": target_index,
        "target_prior": priors[target_index],
        "target_likelihood": likelihoods[target_index],
        "posterior": posterior,
    }


def discrete_expected_value(values: List[float], probabilities: List[float]) -> float:
    """
    Kesikli rastgele değişkenin beklenen değeri:
    E[X] = sum(x_i * P(X = x_i)).
    """
    if len(values) != len(probabilities):
        raise ValueError("Değerler ve olasılıklar eşit sayıda olmalıdır.")
    if not all(math.isfinite(x) for x in values) or not all(math.isfinite(p) for p in probabilities):
        raise ValueError("Tüm değerler ve olasılıklar sonlu reel sayılar olmalıdır.")
    if abs(sum(probabilities) - 1.0) > 1e-4:
        raise ValueError(f"Olasılıklar toplamı 1 olmalıdır: {sum(probabilities)}")

    return sum(x * p for x, p in zip(values, probabilities))


def discrete_variance(values: List[float], probabilities: List[float]) -> float:
    """
    Kesikli rastgele değişkenin varyansı:
    Var(X) = E[X^2] - (E[X])^2.
    """
    ev = discrete_expected_value(values, probabilities)
    ev_squared = sum((x ** 2) * p for x, p in zip(values, probabilities))
    return max(0.0, ev_squared - (ev ** 2))


def discrete_std_dev(values: List[float], probabilities: List[float]) -> float:
    """Kesikli rastgele değişkenin standart sapması: sigma = sqrt(Var(X))."""
    return math.sqrt(discrete_variance(values, probabilities))


# =====================================================================
# 3. TANIMLAYICI İSTATİSTİK (MERKEZİ EĞİLİM VE YAYILIM)
# =====================================================================

def mean(data: List[float]) -> float:
    """Aritmetik ortalama: sum(x) / n."""
    if not data:
        raise ValueError("Veri kümesi boş olamaz.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    """Medyan (ortanca değer)."""
    if not data:
        raise ValueError("Veri kümesi boş olamaz.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")
    s = sorted(data)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2.0


def mode(data: List[float]) -> List[float]:
    """Mod (tepe değer) - en çok tekrar eden değer(ler)."""
    if not data:
        raise ValueError("Veri kümesi boş olamaz.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")
    counts: Dict[float, int] = {}
    for x in data:
        counts[x] = counts.get(x, 0) + 1
    max_count = max(counts.values())
    return sorted([k for k, v in counts.items() if v == max_count])


def data_range(data: List[float]) -> float:
    """Açıklık (range): max(x) - min(x)."""
    if not data:
        raise ValueError("Veri kümesi boş olamaz.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")
    return max(data) - min(data)


def variance(data: List[float], is_sample: bool = True) -> float:
    """
    Varyans hesabı.
    Örneklem varyansı için payda (n - 1), popülasyon varyansı için n.
    """
    n = len(data)
    if is_sample and n < 2:
        raise ValueError("Örneklem varyansı için en az 2 veri noktası gereklidir.")
    if not is_sample and n < 1:
        raise ValueError("Popülasyon varyansı için en az 1 veri noktası gereklidir.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")

    m = mean(data)
    sq_diff_sum = sum((x - m) ** 2 for x in data)
    divisor = (n - 1) if is_sample else n
    return sq_diff_sum / divisor


def std_deviation(data: List[float], is_sample: bool = True) -> float:
    """Standart sapma: sqrt(varyans)."""
    return math.sqrt(variance(data, is_sample=is_sample))


def quartiles_and_iqr(data: List[float]) -> Dict[str, Any]:
    """
    Çeyrekler (Q1, Q2/medyan, Q3), Çeyrekler Açıklığı (IQR) ve aykırı değer sınırları.
    """
    if len(data) < 4:
        raise ValueError("Çeyrekler hesabı için en az 4 veri noktası gereklidir.")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Veri kümesindeki tüm elemanlar sonlu reel sayılar olmalıdır.")
    s = sorted(data)
    n = len(s)
    q2 = median(s)

    mid = n // 2
    if n % 2 == 0:
        lower_half = s[:mid]
        upper_half = s[mid:]
    else:
        lower_half = s[:mid]
        upper_half = s[mid + 1:]

    q1 = median(lower_half)
    q3 = median(upper_half)
    iqr = q3 - q1

    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    outliers = [x for x in s if x < lower_fence or x > upper_fence]

    return {
        "q1": q1,
        "q2_median": q2,
        "q3": q3,
        "iqr": iqr,
        "lower_fence": lower_fence,
        "upper_fence": upper_fence,
        "outliers": outliers,
    }


def z_score(x: float, mu: float, sigma: float) -> float:
    """Z-Puanı standartlaştırması: z = (x - mu) / sigma."""
    if not (math.isfinite(x) and math.isfinite(mu) and math.isfinite(sigma)):
        raise ValueError("Tüm parametreler sonlu reel sayılar olmalıdır.")
    if sigma <= 0:
        raise ValueError(f"Standart sapma pozitif olmalıdır: {sigma}")
    return (x - mu) / sigma


def t_score(z: float) -> float:
    """T-Puanı dönüşümü: T = 10 * z + 50."""
    if not math.isfinite(z):
        raise ValueError("z değeri sonlu bir reel sayı olmalıdır.")
    return 10.0 * z + 50.0


def empirical_rule_intervals(mu: float, sigma: float) -> Dict[str, Tuple[float, float]]:
    """
    Normal Dağılımda 68-95-99.7 Ampirik Kuralı aralıkları:
    - %68.27: [mu - sigma, mu + sigma]
    - %95.45: [mu - 2*sigma, mu + 2*sigma]
    - %99.73: [mu - 3*sigma, mu + 3*sigma]
    """
    if not (math.isfinite(mu) and math.isfinite(sigma)):
        raise ValueError("mu ve sigma sonlu reel sayılar olmalıdır.")
    if sigma <= 0:
        raise ValueError("Standart sapma pozitif olmalıdır.")
    return {
        "68_percent": (mu - sigma, mu + sigma),
        "95_percent": (mu - 2 * sigma, mu + 2 * sigma),
        "99_7_percent": (mu - 3 * sigma, mu + 3 * sigma),
    }


# =====================================================================
# 4. MONTE CARLO PROBABILITY SIMULATOR
# =====================================================================

class MonteCarloProbabilitySimulator:
    """
    100.000 denemeli Monte Carlo olasılık simülatörü.
    Büyük sayılar yasasını (Law of Large Numbers) deneysel olarak doğrular.
    """

    def __init__(self, seed: Optional[int] = 42):
        self.rng = random.Random(seed)

    def simulate_event(
        self,
        trial_func: Callable[[random.Random], bool],
        num_trials: int = 100_000,
        theoretical_prob: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Her denemede True/False üreten bir deneyi num_trials kez çalıştırır.
        """
        if num_trials <= 0:
            raise ValueError("Deneme sayısı pozitif olmalıdır.")

        success_count = 0
        for _ in range(num_trials):
            if trial_func(self.rng):
                success_count += 1

        observed_prob = success_count / num_trials
        # Standart hata: SE = sqrt(p * (1-p) / N)
        std_error = math.sqrt((observed_prob * (1.0 - observed_prob)) / num_trials)
        # %95 Güven Aralığı: observed ± 1.96 * SE
        ci_95 = (max(0.0, observed_prob - 1.96 * std_error), min(1.0, observed_prob + 1.96 * std_error))

        converged = True
        delta = None
        if theoretical_prob is not None:
            delta = abs(observed_prob - theoretical_prob)
            # 100.000 denemede azami beklenen sapma genellikle 3 * SE (< 0.01) düzeyindedir
            converged = delta <= max(0.015, 3.5 * std_error)

        return {
            "num_trials": num_trials,
            "success_count": success_count,
            "observed_probability": observed_prob,
            "theoretical_probability": theoretical_prob,
            "delta": delta,
            "standard_error": std_error,
            "ci_95": ci_95,
            "converged": converged,
        }

    def simulate_urn_draw(
        self,
        red_count: int,
        blue_count: int,
        draw_count: int,
        target_reds: int,
        with_replacement: bool = False,
        num_trials: int = 100_000,
    ) -> Dict[str, Any]:
        """
        Torba çekim deneyi simülasyonu (İadeli veya İadesiz).
        Örnek: Kırmızı ve Mavi toplar arasından rastgele çekim.
        """
        urn = ["R"] * red_count + ["B"] * blue_count
        total_balls = red_count + blue_count

        def trial(rng: random.Random) -> bool:
            if with_replacement:
                drawn = [rng.choice(urn) for _ in range(draw_count)]
            else:
                drawn = rng.sample(urn, draw_count)
            return drawn.count("R") == target_reds

        # Teorik olasılık hesabı
        theoretical_prob = None
        if not with_replacement:
            # Hipergeometrik: C(red, target) * C(blue, draw - target) / C(total, draw)
            target_blues = draw_count - target_reds
            if 0 <= target_reds <= red_count and 0 <= target_blues <= blue_count:
                fav = combination(red_count, target_reds) * combination(blue_count, target_blues)
                tot = combination(total_balls, draw_count)
                theoretical_prob = fav / tot
        else:
            # Binom: C(draw, target) * p^target * (1-p)^(draw-target)
            p_red = red_count / total_balls
            fav_comb = combination(draw_count, target_reds)
            theoretical_prob = fav_comb * (p_red ** target_reds) * ((1.0 - p_red) ** (draw_count - target_reds))

        return self.simulate_event(trial, num_trials=num_trials, theoretical_prob=theoretical_prob)


# =====================================================================
# 5. SOKRATİK ADIM ÇÖZÜCÜ (ZERO-LEAKAGE SKELETON)
# =====================================================================

def solve_combinatorics_or_probability(problem_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sokratik pedagojik adımlarla sayma, olasılık veya istatistik problemini iskeletlendirir.
    ZERO-LEAKAGE: Öğrenciye sunulan yönlendirme ipuçlarında nihai sayısal sonuç doğrudan verilmez.
    """
    steps: List[Dict[str, Any]] = []

    if problem_type == "combination_selection":
        n = params["n"]
        r = params["r"]
        result = combination(n, r)
        steps.append({
            "step_index": 1,
            "title": "Seçim Türünü ve Sıra Önemini Belirleme",
            "prompt": f"{n} eleman arasından {r} tanesi seçilirken elemanların diziliş sırası önemli midir?",
            "expected_concept": "Sırasız seçim (Kombinasyon)",
        })
        steps.append({
            "step_index": 2,
            "title": "Kombinasyon Formülünü Kurma",
            "prompt": "C(n, r) = n! / (r! * (n - r)!) formülünde n ve r değerlerini yerine yerleştir.",
            "formula": f"C({n}, {r}) = {n}! / ({r}! * ({n}-{r})!)",
        })
        steps.append({
            "step_index": 3,
            "title": "Faktöriyel Sadeleştirmesi ve Hesaplama",
            "prompt": "Paydaki faktöriyeli paydadaki büyük faktöriyele kadar açarak sadeleştir.",
            "calculated_value": result,
        })

    elif problem_type == "linear_permutation":
        n = params["n"]
        r = params["r"]
        result = permutation(n, r)
        steps.append({
            "step_index": 1,
            "title": "Sıralama (Permütasyon) Şartını Belirleme",
            "prompt": f"{n} farklı nesneden {r} tanesi bir sıraya dizilecektir. Sıra değişince yeni durum oluşur mu?",
            "expected_concept": "Sıralı seçim (Permütasyon P(n, r))",
        })
        steps.append({
            "step_index": 2,
            "title": "Çarpma Kuralı veya Formülü Yazma",
            "formula": f"P({n}, {r}) = {n}! / ({n} - {r})!",
        })
        steps.append({
            "step_index": 3,
            "title": "Hesaplama Adımı",
            "prompt": "İlk r pozisyon için seçenek sayılarını art arda çarp.",
            "calculated_value": result,
        })

    elif problem_type == "conditional_probability":
        p_intersection = params["p_intersection"]
        p_condition = params["p_condition"]
        result = conditional_probability(p_intersection, p_condition)
        steps.append({
            "step_index": 1,
            "title": "Örnek Uzayı Daraltma",
            "prompt": "Koşul gerçekleştiğinde evrensel küme hangi alt kümeye indirgenir?",
            "expected_concept": "Yeni örnek uzay B olayıdır.",
        })
        steps.append({
            "step_index": 2,
            "title": "Koşullu Olasılık Bağıntısı",
            "formula": "P(A|B) = P(A ∩ B) / P(B)",
        })
        steps.append({
            "step_index": 3,
            "title": "Oranı Hesaplama",
            "prompt": "Kesişim olasılığını koşulun olasılığına böl.",
            "calculated_value": result,
        })

    else:
        raise ValueError(f"Bilinmeyen problem tipi: {problem_type}")

    return {
        "problem_type": problem_type,
        "scaffolding_steps": steps,
        "step_count": len(steps),
        "target_value": steps[-1].get("calculated_value"),
    }
