import math
import numpy as np
import pytest
from app.adaptive.cat_engine import CATEngine
from app.psychometrics.sprt import WaldSPRT, MasteryDecision


def test_gate2_monte_carlo_wald_sprt_alpha_beta():
    """
    DoD KAPI 2: PSİKOMETRİK KESTİRİM VE CAT TEŞHİS KAPISI - BÖLÜM 1
    Wald SPRT Monte Carlo Doğrulaması:
    - 10,000 Usta Olmayan (p <= p0 = 0.60) öğrenci simülasyonu -> Tip-1 Hata (alpha) <= 0.05
    - 10,000 Gerçek Usta (p >= p1 = 0.88) öğrenci simülasyonu -> Tip-2 Hata (beta) <= 0.10
    """
    np.random.seed(42)
    sprt = WaldSPRT(p0=0.60, p1=0.88, alpha=0.05, beta=0.10, max_trials=12)
    N_TRIALS = 10000

    # 1. Non-master simulation (H0 true: p <= 0.60)
    # Sample true probabilities uniformly between 0.30 and 0.60
    p_non_masters = np.random.uniform(0.30, 0.60, size=N_TRIALS)
    type1_false_mastery_count = 0

    for p in p_non_masters:
        responses = []
        for step in range(sprt.max_trials):
            y = bool(np.random.binomial(1, p))
            responses.append(y)
            res = sprt.evaluate(responses)
            if res.is_terminal:
                if res.decision in (MasteryDecision.MASTERY_CONFIRMED, MasteryDecision.CONDITIONAL_MASTERY):
                    type1_false_mastery_count += 1
                break

    empirical_alpha = type1_false_mastery_count / N_TRIALS

    # 2. Master simulation (H1 true: p >= 0.88)
    # Sample true probabilities uniformly between 0.88 and 0.98
    p_masters = np.random.uniform(0.88, 0.98, size=N_TRIALS)
    type2_false_remediation_count = 0

    for p in p_masters:
        responses = []
        for step in range(sprt.max_trials):
            y = bool(np.random.binomial(1, p))
            responses.append(y)
            res = sprt.evaluate(responses)
            if res.is_terminal:
                if res.decision == MasteryDecision.NEEDS_REMEDIATION:
                    type2_false_remediation_count += 1
                break

    empirical_beta = type2_false_remediation_count / N_TRIALS

    print(f"\n--- DoD KAPI 2 WALD SPRT MONTE CARLO RAPORU ---")
    print(f"Simülasyon Büyüklüğü: {N_TRIALS} öğrenci x 2 grup")
    print(f"Empirical Tip-1 Hata (alpha): {empirical_alpha:.4f} (Kabul Sınırı: <= 0.05)")
    print(f"Empirical Tip-2 Hata (beta):  {empirical_beta:.4f} (Kabul Sınırı: <= 0.10)")

    assert empirical_alpha <= 0.05, f"Wald SPRT alpha exceeded: {empirical_alpha:.4f} > 0.05"
    assert empirical_beta <= 0.10, f"Wald SPRT beta exceeded: {empirical_beta:.4f} > 0.10"


def test_gate2_monte_carlo_2pl_cat_convergence():
    """
    DoD KAPI 2: PSİKOMETRİK KESTİRİM VE CAT TEŞHİS KAPISI - BÖLÜM 2
    2PL-IRT CAT Motorunun Adaptif Yakınsaması:
    - 2,000 sentetik öğrenci Monte Carlo simülasyonu (theta_true ~ N(0, 1) [-2.5, 2.5]).
    - Adaptif CAT durdurma kuralı (target_se=0.35, max_items=8).
    - Ortalama soru sayısının <= 5 olması (ortalama ~3.9 soru).
    - Öğrencilerin %100'ünde final SE(theta_hat) <= 0.35 hassasiyetinin doğrulanması.
    - theta_true ile theta_hat korelasyonunun >= 0.85 olması.
    """
    np.random.seed(42)
    cat = CATEngine()
    N_STUDENTS = 2000

    true_thetas = np.clip(np.random.normal(0.0, 1.0, size=N_STUDENTS), -2.5, 2.5)
    estimated_thetas = []
    final_ses = []
    items_taken = []

    for theta_true in true_thetas:
        administered = []
        administered_ids = set()
        current_theta = 0.0
        se = 1.0

        # Run adaptive test until target SE <= 0.35 is achieved or max items reached
        while not cat.is_test_complete(administered, se, max_items=8, target_se=0.35):
            item = cat.select_next_item(current_theta, administered_ids)
            if item is None:
                break
            administered_ids.add(item.item_id)

            # Generate response via 2PL-IRT true probability
            p_true = cat.probability_correct(theta_true, item.discrimination_a, item.difficulty_b)
            y = bool(np.random.binomial(1, p_true))
            administered.append((item.item_id, y))

            current_theta, se = cat.estimate_theta(administered, initial_theta=current_theta)

        estimated_thetas.append(current_theta)
        final_ses.append(se)
        items_taken.append(len(administered))

    mean_items = float(np.mean(items_taken))
    mean_se = float(np.mean(final_ses))
    p95_se = float(np.percentile(final_ses, 95))
    max_se = float(np.max(final_ses))
    corr = float(np.corrcoef(true_thetas, estimated_thetas)[0, 1])
    pct_meeting_threshold = float(np.mean(np.array(final_ses) <= 0.35) * 100.0)

    print(f"\n--- DoD KAPI 2 CAT MONTE CARLO RAPORU ---")
    print(f"Simüle Edilen Öğrenci Sayısı: {N_STUDENTS}")
    print(f"Ortalama Soru Sayısı:              {mean_items:.2f} soru (Hedef: <= 5.0)")
    print(f"Maksimum Soru Sayısı:              {np.max(items_taken)} soru (Tavan: 8)")
    print(f"Ortalama Final SE(theta):          {mean_se:.4f} (Hedef: <= 0.35)")
    print(f"P95 Final SE(theta):               {p95_se:.4f} (Hedef: <= 0.35)")
    print(f"Maksimum Final SE(theta):          {max_se:.4f} (Hedef: <= 0.35)")
    print(f"SE <= 0.35 Karşılama Oranı:        %{pct_meeting_threshold:.2f} (Hedef: %100)")
    print(f"True vs Hat Theta Korelasyonu:     r = {corr:.4f} (Hedef: >= 0.85)")

    assert mean_items <= 5.0, f"Mean items {mean_items:.2f} exceeds 5.0"
    assert mean_se <= 0.35, f"Mean SE {mean_se:.4f} exceeds 0.35"
    assert p95_se <= 0.35, f"P95 SE {p95_se:.4f} exceeds 0.35"
    assert max_se <= 0.35, f"Max SE {max_se:.4f} exceeds 0.35"
    assert pct_meeting_threshold >= 98.0, f"Only {pct_meeting_threshold}% reached SE <= 0.35"
    assert corr >= 0.85, f"Ability correlation r={corr:.4f} below 0.85"
