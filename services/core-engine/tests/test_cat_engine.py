import pytest
from app.adaptive.cat_engine import CATEngine
from app.graph.knowledge_dag import KnowledgeDAG


@pytest.fixture
def cat():
    dag = KnowledgeDAG()
    return CATEngine(dag=dag)


def test_probability_correct_symmetry_and_extremes(cat):
    # theta = b olduğunda başarı olasılığı tam 0.5 olmalı
    p_mid = cat.probability_correct(theta=0.0, a=2.0, b=0.0)
    assert pytest.approx(p_mid, abs=1e-5) == 0.5

    # Çok yüksek yetenekte olasılık 1.0'a yaklaşmalı
    p_high = cat.probability_correct(theta=3.0, a=2.0, b=0.0)
    assert p_high > 0.99

    # Çok düşük yetenekte olasılık 0.0'a yaklaşmalı
    p_low = cat.probability_correct(theta=-3.0, a=2.0, b=0.0)
    assert p_low < 0.01


def test_fisher_information_peaks_at_difficulty(cat):
    # Fisher bilgisi b noktasında en yüksek tepeyi yapmalıdır
    info_peak = cat.fisher_information(theta=0.5, a=2.0, b=0.5)
    info_left = cat.fisher_information(theta=0.0, a=2.0, b=0.5)
    info_right = cat.fisher_information(theta=1.0, a=2.0, b=0.5)

    assert info_peak > info_left
    assert info_peak > info_right


def test_cat_simulation_high_ability_student(cat):
    administered = []
    administered_ids = set()
    current_theta = 0.0

    # İlk soru (Kök Madde CAT-ITEM-01, b=0.0)
    first_item = cat.select_next_item(current_theta, administered_ids)
    assert first_item is not None
    assert first_item.item_id == "CAT-ITEM-01"

    # Yüksek yetenekli öğrenci 4 soruyu üst üste doğru yanıtlasın
    for _ in range(4):
        item = cat.select_next_item(current_theta, administered_ids)
        assert item is not None
        administered_ids.add(item.item_id)
        administered.append((item.item_id, True))  # Doğru yanıt

        current_theta, se = cat.estimate_theta(administered, initial_theta=current_theta)

    # Yetenek kestirimi pozitif ve yüksek olmalı
    assert current_theta > 1.0
    # Standart hata başlangıçtakine göre (1.0) düşmüş olmalı
    assert se < 0.55


def test_cat_simulation_low_ability_student(cat):
    administered = []
    administered_ids = set()
    current_theta = 0.0

    # Düşük yetenekli öğrenci 4 soruyu üst üste yanlış yanıtlasın
    for _ in range(4):
        item = cat.select_next_item(current_theta, administered_ids)
        assert item is not None
        administered_ids.add(item.item_id)
        administered.append((item.item_id, False))  # Yanlış yanıt

        current_theta, se = cat.estimate_theta(administered, initial_theta=current_theta)

    # Yetenek kestirimi negatif olmalı
    assert current_theta < -1.0
    assert se < 0.55


def test_dag_seeding_based_on_theta(cat):
    # Yüksek yetenekli öğrenci (theta = +1.5)
    high_mastery = cat.seed_knowledge_dag(theta_hat=1.5)

    # Temel aritmetik ve çarpanlara ayırma düğümlerinde ustalık yüksek olmalı
    assert high_mastery["N01"] > 0.95
    assert high_mastery["N02"] > 0.95
    assert high_mastery["N12"] > 0.90

    # Düşük yetenekli öğrenci (theta = -1.5)
    low_mastery = cat.seed_knowledge_dag(theta_hat=-1.5)

    # Üst seviye tam kare ve diskriminant düğümlerinde ustalık düşük olmalı
    assert low_mastery["N15"] < 0.10
    assert low_mastery["N20"] < 0.05
