"""
HEDEF 14: Olasılık, Kombinatorik ve İstatistik Motoru Doğrulama Testleri.
Asgari 40 test ile kombinatorik, olasılık, Bayes, Monte Carlo, tanımlayıcı istatistik
ve bilişsel yanılgı tespitlerini (BUG-COMB-01..05) matematiksel kesinlikle doğrular.
"""

import math
import pytest
from app.probability.combinatorics_engine import (
    factorial,
    permutation,
    circular_permutation,
    repeated_permutation,
    combination,
    pascal_row,
    verify_pascal_identity,
    binomial_term,
    geometric_combinations_triangles,
    classical_probability,
    complement_probability,
    union_probability,
    conditional_probability,
    bayes_theorem,
    bayes_multi_hypothesis,
    discrete_expected_value,
    discrete_variance,
    discrete_std_dev,
    mean,
    median,
    mode,
    data_range,
    variance,
    std_deviation,
    quartiles_and_iqr,
    z_score,
    t_score,
    empirical_rule_intervals,
    MonteCarloProbabilitySimulator,
    solve_combinatorics_or_probability,
)
from app.misconceptions.detector import QuadraticMisconceptionDetector as MisconceptionDetector


# =====================================================================
# 1. KOMBİNATÖRİK VE SAYMA TESTLERİ
# =====================================================================

def test_factorial_basic_and_edge_cases():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    assert factorial(6) == 720
    with pytest.raises(ValueError):
        factorial(-1)


def test_linear_permutation():
    assert permutation(5, 2) == 20
    assert permutation(5, 5) == 120
    assert permutation(4, 0) == 1
    assert permutation(3, 5) == 0  # r > n
    with pytest.raises(ValueError):
        permutation(-2, 3)


def test_circular_permutation():
    assert circular_permutation(1) == 1   # (1-1)! = 0! = 1
    assert circular_permutation(4) == 6   # (4-1)! = 3! = 6
    assert circular_permutation(6) == 120 # (6-1)! = 5! = 120
    with pytest.raises(ValueError):
        circular_permutation(0)


def test_repeated_permutation():
    # KELEBEK: K:2, E:3, L:1, B:1 (toplam 7) -> 7! / (2! * 3! * 1! * 1!) = 5040 / 12 = 420
    assert repeated_permutation(7, [2, 3, 1, 1]) == 420
    # ANKARA: A:3, N:1, K:1, R:1 (toplam 6) -> 6! / (3! * 1! * 1! * 1!) = 720 / 6 = 120
    assert repeated_permutation(6, [3, 1, 1, 1]) == 120
    # Hata durumları
    with pytest.raises(ValueError):
        repeated_permutation(5, [2, 2])  # Toplam 4 != 5


def test_combination_properties():
    assert combination(5, 0) == 1
    assert combination(5, 5) == 1
    assert combination(5, 2) == 10
    assert combination(5, 3) == 10  # C(n, r) == C(n, n-r)
    assert combination(7, 3) == 35
    assert combination(4, 5) == 0   # r > n


def test_pascal_row_and_identity():
    # 4. satır: 1, 4, 6, 4, 1
    assert pascal_row(4) == [1, 4, 6, 4, 1]
    # Pascal özdeşliği: C(6, 2) + C(6, 3) == C(7, 3) -> 15 + 20 == 35
    assert verify_pascal_identity(6, 2) is True
    assert verify_pascal_identity(5, 3) is True


def test_binomial_term_expansion():
    # (2x + 3y)^4 açılımında r=2 (3. terim): C(4, 2) * (2x)^2 * (3y)^2 = 6 * 4 * 9 = 216 x^2 y^2
    term = binomial_term(n=4, r=2, a=2.0, b=3.0)
    assert term["combination_coeff"] == 6
    assert term["numeric_coefficient"] == 216.0
    assert term["x_power"] == 2
    assert term["y_power"] == 2


def test_geometric_combinations_triangles():
    # Düzlemde 6 nokta (hiçbiri doğrusal değil): C(6, 3) = 20 üçgen
    assert geometric_combinations_triangles(6) == 20
    # 6 noktadan 4'ü doğrusal: C(6, 3) - C(4, 3) = 20 - 4 = 16
    assert geometric_combinations_triangles(6, collinear_sets=[4]) == 16


# =====================================================================
# 2. OLASILIK KURAMI VE BAYES TESTLERİ
# =====================================================================

def test_classical_probability():
    assert classical_probability(1, 6) == pytest.approx(1 / 6)
    assert classical_probability(3, 6) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        classical_probability(7, 6)  # favorable > sample_space
    with pytest.raises(ValueError):
        classical_probability(1, 0)  # sample_space == 0


def test_complement_probability():
    assert complement_probability(0.2) == pytest.approx(0.8)
    assert complement_probability(1.0) == 0.0
    assert complement_probability(0.0) == 1.0


def test_union_probability_disjoint_and_joint():
    # Ayrık olaylar: P(A ∪ B) = P(A) + P(B)
    assert union_probability(0.3, 0.4, 0.0) == pytest.approx(0.7)
    # Ayrık olmayan: P(A ∪ B) = 0.5 + 0.4 - 0.2 = 0.7
    assert union_probability(0.5, 0.4, 0.2) == pytest.approx(0.7)
    with pytest.raises(ValueError):
        union_probability(0.3, 0.4, 0.5)  # intersection > min(p_a, p_b)


def test_conditional_probability():
    # P(A ∩ B) = 0.15, P(B) = 0.5 -> P(A|B) = 0.3
    assert conditional_probability(0.15, 0.5) == pytest.approx(0.3)
    with pytest.raises(ValueError):
        conditional_probability(0.6, 0.5)  # intersection > condition


def test_bayes_theorem_two_events():
    # P(B) = 0.01 (hastalık sıklığı), P(A|B) = 0.99 (test duyarlılığı), P(A) = 0.05
    # P(B|A) = (0.99 * 0.01) / 0.05 = 0.0099 / 0.05 = 0.198
    posterior = bayes_theorem(prior_b=0.01, likelihood_a_given_b=0.99, marginal_a=0.05)
    assert posterior == pytest.approx(0.198)


def test_bayes_multi_hypothesis_total_probability():
    # 3 Fabrika: F1(%30), F2(%50), F3(%20). Hatalı üretim oranları: %1, %2, %3
    priors = [0.30, 0.50, 0.20]
    likelihoods = [0.01, 0.02, 0.03]
    # Seçilen hatalı ürünün F2'den gelme olasılığı: P(F2 | Hatalı)
    res = bayes_multi_hypothesis(priors, likelihoods, target_index=1)
    # Toplam hatalı: 0.30*0.01 + 0.50*0.02 + 0.20*0.03 = 0.003 + 0.010 + 0.006 = 0.019
    assert res["marginal_evidence"] == pytest.approx(0.019)
    # F2 payı: 0.010 / 0.019 = 10 / 19 ≈ 0.5263
    assert res["posterior"] == pytest.approx(10 / 19)


def test_discrete_expected_value_and_variance():
    # Adil zar atımı: X in {1, 2, 3, 4, 5, 6}, P(X) = 1/6
    vals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    probs = [1 / 6] * 6
    ev = discrete_expected_value(vals, probs)
    assert ev == pytest.approx(3.5)
    var = discrete_variance(vals, probs)
    # Var = E[X^2] - 3.5^2 = (91/6) - 12.25 = 15.1667 - 12.25 = 2.9167 (35/12)
    assert var == pytest.approx(35 / 12)
    assert discrete_std_dev(vals, probs) == pytest.approx(math.sqrt(35 / 12))


# =====================================================================
# 3. TANIMLAYICI İSTATİSTİK TESTLERİ
# =====================================================================

def test_descriptive_mean_median_mode():
    data = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    assert mean(data) == pytest.approx(5.0)
    assert median(data) == pytest.approx(4.5)  # (4 + 5) / 2
    assert mode(data) == [4.0]
    assert data_range(data) == 7.0  # 9 - 2


def test_descriptive_variance_and_std_dev():
    data = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
    # Sample variance
    s_var = variance(data, is_sample=True)
    assert s_var > 0
    assert std_deviation(data, is_sample=True) == pytest.approx(math.sqrt(s_var))


def test_quartiles_iqr_and_outliers():
    # Normal veri + belirgin aykırı değer (100)
    data = [10, 12, 14, 15, 16, 18, 19, 21, 22, 24, 100]
    q_info = quartiles_and_iqr(data)
    assert q_info["q2_median"] == 18.0
    assert q_info["iqr"] > 0
    assert 100 in q_info["outliers"]


def test_z_score_and_t_score():
    # x = 85, mu = 70, sigma = 10 -> z = 1.5, T = 10*(1.5) + 50 = 65
    z = z_score(85.0, 70.0, 10.0)
    assert z == pytest.approx(1.5)
    assert t_score(z) == pytest.approx(65.0)


def test_empirical_rule_intervals():
    intervals = empirical_rule_intervals(mu=100.0, sigma=15.0)
    assert intervals["68_percent"] == (85.0, 115.0)
    assert intervals["95_percent"] == (70.0, 130.0)
    assert intervals["99_7_percent"] == (55.0, 145.0)


# =====================================================================
# 4. MONTE CARLO PROBABILITY SIMULATOR TESTLERİ
# =====================================================================

def test_monte_carlo_coin_flip_convergence():
    sim = MonteCarloProbabilitySimulator(seed=12345)
    # Hilesiz para atışı: P(Tura) = 0.5
    res = sim.simulate_event(
        trial_func=lambda rng: rng.random() < 0.5,
        num_trials=50_000,
        theoretical_prob=0.5,
    )
    assert res["observed_probability"] == pytest.approx(0.5, abs=0.01)
    assert res["converged"] is True
    assert res["ci_95"][0] <= 0.5 <= res["ci_95"][1]


def test_monte_carlo_urn_draw_without_replacement():
    sim = MonteCarloProbabilitySimulator(seed=999)
    # 4 Kırmızı, 6 Mavi top. 2 top çekiliyor, ikisinin de Kırmızı olma olasılığı:
    # C(4, 2) / C(10, 2) = 6 / 45 = 2 / 15 ≈ 0.1333
    res = sim.simulate_urn_draw(
        red_count=4,
        blue_count=6,
        draw_count=2,
        target_reds=2,
        with_replacement=False,
        num_trials=30_000,
    )
    assert res["theoretical_probability"] == pytest.approx(2 / 15)
    assert res["observed_probability"] == pytest.approx(2 / 15, abs=0.015)
    assert res["converged"] is True


def test_monte_carlo_urn_draw_with_replacement():
    sim = MonteCarloProbabilitySimulator(seed=777)
    # 5 Kırmızı, 5 Mavi top. 2 top çekiliyor (iadeli). İkisi de Kırmızı: (1/2)*(1/2) = 0.25
    res = sim.simulate_urn_draw(
        red_count=5,
        blue_count=5,
        draw_count=2,
        target_reds=2,
        with_replacement=True,
        num_trials=30_000,
    )
    assert res["theoretical_probability"] == pytest.approx(0.25)
    assert res["observed_probability"] == pytest.approx(0.25, abs=0.015)
    assert res["converged"] is True


# =====================================================================
# 5. SOKRATİK ADIM VE ZERO-LEAKAGE TESTLERİ
# =====================================================================

def test_solve_combinatorics_scaffolding_zero_leakage():
    res = solve_combinatorics_or_probability("combination_selection", {"n": 6, "r": 2})
    assert res["problem_type"] == "combination_selection"
    assert res["target_value"] == 15
    # Prompt metinlerinde doğrudan nihai cevabın sızmadığını doğrula
    for step in res["scaffolding_steps"]:
        assert "15" not in step.get("prompt", "")


def test_solve_conditional_scaffolding():
    res = solve_combinatorics_or_probability(
        "conditional_probability",
        {"p_intersection": 0.2, "p_condition": 0.5},
    )
    assert res["target_value"] == pytest.approx(0.4)
    assert len(res["scaffolding_steps"]) == 3


# =====================================================================
# 6. BİLİŞSEL YANILGI TESPİTLERİ (BUG-COMB-01..05) VE ZERO FALSE POSITIVES
# =====================================================================

@pytest.fixture
def detector():
    return MisconceptionDetector()


def test_bug_comb_01_permutation_instead_of_combination(detector):
    diag = detector.detect("komite = P(5, 3)", "5 kişiden 3 kişilik komite kaç farklı şekilde seçilir?", "")
    assert diag is not None
    assert diag.bug_id == "BUG-COMB-01"
    assert diag.category == "COMBINATORICS_PERMUTATION_INSTEAD_OF_COMBINATION"


def test_bug_comb_01_valid_step_no_false_positive(detector):
    # Doğru kombinasyon adımı permütasyonu 3!'e bölerek kullanabilir: C(5, 3) = P(5, 3) / 3!
    diag = detector.detect("C(5, 3) = P(5, 3) / 3!", "5 kişiden 3 kişilik komite", "")
    assert diag is None or diag.bug_id != "BUG-COMB-01"


def test_bug_comb_02_gamblers_fallacy(detector):
    diag = detector.detect("yazigeldi => P(Tura) > 0.5", "5 kez üst üste yazı geldi, sıradaki atış?", "")
    assert diag is not None
    assert diag.bug_id == "BUG-COMB-02"
    assert "hafızası" in diag.remediation_directive


def test_bug_comb_02_valid_step_no_false_positive(detector):
    # Kullanıcı "bağımsız olaylarda P(Tura) = 0.5" yazarsa hata tetiklenmemeli
    diag = detector.detect("Her atışta P(Tura) = 0.5", "5 kez üst üste yazı geldi", "")
    assert diag is None


def test_bug_comb_03_conditional_sample_space_not_reduced(detector):
    diag = detector.detect("kosullu_payda = 36", "Zarlardan birinin 4 geldiği bilindiğinde...", "")
    assert diag is not None
    assert diag.bug_id == "BUG-COMB-03"
    assert "daralmıştır" in diag.remediation_directive


def test_bug_comb_03_valid_step_no_false_positive(detector):
    # Daraltılmış örnek uzay s(B) = 11 yazarsa geçerli
    diag = detector.detect("s(B) = 11, yeni örnek uzay 11 elemanlı", "Zarlardan birinin 4 geldiği bilindiğinde", "")
    assert diag is None


def test_bug_comb_04_repeated_permutation_identical_omission(detector):
    diag = detector.detect("kelebek = 7!", "KELEBEK kelimesinin harfleriyle dizilimler", "")
    assert diag is not None
    assert diag.bug_id == "BUG-COMB-04"
    assert "özdeş eleman" in diag.description.lower()


def test_bug_comb_04_valid_step_no_false_positive(detector):
    # 7! / (2! * 3!) yazarsa hata tetiklenmemeli
    diag = detector.detect("kelebek = 7! / (2! * 3!)", "KELEBEK kelimesinin harfleri", "")
    assert diag is None


def test_bug_comb_05_union_without_intersection_subtraction(detector):
    diag = detector.detect("P(cift_veya_asal) = 3/6 + 3/6 = 1", "Zarda çift veya asal gelme olasılığı", "")
    assert diag is not None
    assert diag.bug_id == "BUG-COMB-05"
    assert "P(A ∩ B)" in diag.remediation_directive


def test_bug_comb_05_valid_step_no_false_positive(detector):
    # Kesişimi çıkaran öğrenci: P(A veya B) = 3/6 + 3/6 - 1/6
    diag = detector.detect("P(cift veya asal) = 3/6 + 3/6 - 1/6 = 5/6", "Zarda çift veya asal", "")
    assert diag is None


# =====================================================================
# 7. EK UÇ DEĞER VE MATEMATİKSEL SAĞLAMLIK TESTLERİ
# =====================================================================

def test_repeated_permutation_mississippi():
    # MISSISSIPPI: M:1, I:4, S:4, P:2 -> Toplam 11
    # 11! / (1! * 4! * 4! * 2!) = 39916800 / (1 * 24 * 24 * 2) = 39916800 / 1152 = 34650
    assert repeated_permutation(11, [1, 4, 4, 2]) == 34650


def test_data_range_and_median_even():
    data = [5.0, 1.0, 9.0, 3.0]
    assert data_range(data) == 8.0
    assert median(data) == 4.0  # (3 + 5) / 2


def test_descriptive_statistics_empty_raises():
    with pytest.raises(ValueError):
        mean([])
    with pytest.raises(ValueError):
        median([])
    with pytest.raises(ValueError):
        mode([])
    with pytest.raises(ValueError):
        data_range([])


def test_empirical_rule_invalid_sigma():
    with pytest.raises(ValueError):
        empirical_rule_intervals(mu=50, sigma=-5)


def test_monte_carlo_invalid_trials_raises():
    sim = MonteCarloProbabilitySimulator()
    with pytest.raises(ValueError):
        sim.simulate_event(lambda rng: True, num_trials=0)


def test_solve_linear_permutation_scaffolding():
    res = solve_combinatorics_or_probability("linear_permutation", {"n": 5, "r": 3})
    assert res["problem_type"] == "linear_permutation"
    assert res["target_value"] == 60
    assert len(res["scaffolding_steps"]) == 3


def test_bayes_invalid_parameters_raises():
    # Priors toplamı 1 değil
    with pytest.raises(ValueError):
        bayes_multi_hypothesis([0.4, 0.4], [0.1, 0.2], target_index=0)
    # Hedef indeks liste sınırları dışında
    with pytest.raises(IndexError):
        bayes_multi_hypothesis([0.5, 0.5], [0.1, 0.2], target_index=5)


# =====================================================================
# 8. FASTAPI REST API INTEGRATION TESTS
# =====================================================================

def test_fastapi_probability_solve_and_vault():
    """Olasılık / Kombinatorik çözücü ve Bilişsel Hata Kasası REST API entegrasyonunu doğrular."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Normal Çözüm
    payload = {
        "problem_type": "combination_selection",
        "params": {"n": 5, "r": 2},
    }
    resp = client.post("/api/v1/probability/solve", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["problem_type"] == "combination_selection"
    assert data["result_data"]["target_value"] == 10
    assert data["vault_recorded"] is False

    # 2. Hatalı Adım ve Kasaya Otomatik Kayıt (BUG-COMB-01)
    student_id = "student_prob_1"
    err_payload = {
        "problem_type": "combination_selection",
        "params": {"n": 5, "r": 3},
        "student_id": student_id,
        "problem_statement": "5 kişiden 3 kişilik komite kaç farklı şekilde seçilir?",
        "student_step": "komite = P(5, 3)",
    }
    err_resp = client.post("/api/v1/probability/solve", json=err_payload)
    assert err_resp.status_code == 200
    err_data = err_resp.json()
    assert err_data["detected_bug"] is not None
    assert err_data["detected_bug"]["bug_id"] == "BUG-COMB-01"
    assert err_data["vault_recorded"] is True

    # 3. Kasadan kontrol et
    v_resp = client.get(f"/api/v1/vault/list/{student_id}")
    assert v_resp.status_code == 200
    v_list = v_resp.json()
    assert len(v_list) >= 1
    assert any(m["bug_id"] == "BUG-COMB-01" for m in v_list)


def test_fastapi_monte_carlo_api():
    """Canlı Monte Carlo Olasılık Simülatörü REST API rotasını doğrular."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Para Atışı Simülasyonu (10.000 deneme)
    flip_payload = {
        "experiment_type": "coin_flip",
        "params": {"prob": 0.5, "seed": 42},
        "num_trials": 10_000,
    }
    f_resp = client.post("/api/v1/probability/monte-carlo", json=flip_payload)
    assert f_resp.status_code == 200
    f_data = f_resp.json()
    assert f_data["num_trials"] == 10_000
    assert f_data["theoretical_probability"] == 0.5
    assert abs(f_data["observed_probability"] - 0.5) < 0.02
    assert f_data["converged"] is True

    # 2. Torba Çekim Simülasyonu
    urn_payload = {
        "experiment_type": "urn_draw",
        "params": {
            "red_count": 4,
            "blue_count": 6,
            "draw_count": 2,
            "target_reds": 2,
            "with_replacement": False,
            "seed": 999,
        },
        "num_trials": 10_000,
    }
    u_resp = client.post("/api/v1/probability/monte-carlo", json=urn_payload)
    assert u_resp.status_code == 200
    u_data = u_resp.json()
    assert u_data["theoretical_probability"] == pytest.approx(2 / 15)
    assert abs(u_data["observed_probability"] - (2 / 15)) < 0.02

