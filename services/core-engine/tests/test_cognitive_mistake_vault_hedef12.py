"""
HEDEF 12: Kişisel Hata Otopsisi Kasası, Kendi Hatasını Düzeltme Seansı ve Boss Battle Test Paketi.
CognitiveMistakeVault, SelfCorrectionSessionManager ve BossBattleEngine Kapsamlı Testleri.
"""
import pytest
import time
import math
from app.retention.fsrs import Rating, DSRState
from app.vault.mistake_vault import (
    CognitiveMistakeVault,
    MistakeStatus,
    SelfCorrectionStage,
    SelfCorrectionSessionManager,
    BossBattleEngine,
    BossBattleState,
)


@pytest.fixture
def vault():
    return CognitiveMistakeVault()


@pytest.fixture
def session_manager(vault):
    return SelfCorrectionSessionManager(vault)


@pytest.fixture
def boss_engine(vault):
    return BossBattleEngine(vault)


# ==============================================================================
# 1. COGNITIVE MISTAKE VAULT OPERATIONS
# ==============================================================================

def test_vault_record_mistake_initialization(vault):
    """Yeni bir hatanın kasaya doğru FSRS-4.5 başlangıç durumuyla kaydedildiğini doğrular."""
    record = vault.record_mistake(
        user_id="user_123",
        node_id="N165",
        bug_id="BUG-EUC-04",
        problem_statement="Dik üçgende h = 6, p = 4 ise k = ?",
        offending_step="h^2 = b * c",
        correct_principle="h^2 = p * k",
        remediation_directive="Yüksekliğin karesi ayrılan parçaların çarpımına eşittir.",
    )
    assert record.mistake_id is not None
    assert record.user_id == "user_123"
    assert record.bug_id == "BUG-EUC-04"
    assert record.status == MistakeStatus.OPEN
    assert record.self_correction_stage == SelfCorrectionStage.STAGE_1_IDENTIFY
    assert record.dsr_state.repetitions == 1
    assert record.dsr_state.lapses == 1
    assert record.consecutive_clean_solves == 0


def test_vault_get_and_list_mistakes(vault):
    """Kayıtlı hataların ID ile çekilebildiğini ve kullanıcı bazında listelenebildiğini doğrular."""
    r1 = vault.record_mistake("user_1", "N01", "BUG-FOUND-01", "Prob 1", "-(-4)=-4", "-(-x)=+x", "")
    r2 = vault.record_mistake("user_1", "N02", "BUG-FOUND-02", "Prob 2", "3+4*2=14", "İşlem önceliği", "")
    r3 = vault.record_mistake("user_2", "N03", "BUG-QUAD-01", "Prob 3", "x(x+2)=3", "Sıfır çarpım", "")

    assert vault.get_mistake(r1.mistake_id) == r1
    user1_mistakes = vault.list_mistakes("user_1")
    assert len(user1_mistakes) == 2
    assert r1 in user1_mistakes and r2 in user1_mistakes

    user2_mistakes = vault.list_mistakes("user_2")
    assert len(user2_mistakes) == 1
    assert user2_mistakes[0] == r3


def test_vault_status_filtering(vault):
    """Hataların duruma göre filtrelenebildiğini doğrular."""
    r1 = vault.record_mistake("u1", "N10", "BUG-1", "p1", "s1", "c1", "")
    r2 = vault.record_mistake("u1", "N10", "BUG-2", "p2", "s2", "c2", "")
    r2.status = MistakeStatus.CURED
    vault.update_record(r2)

    open_mistakes = vault.list_mistakes("u1", status=MistakeStatus.OPEN)
    assert len(open_mistakes) == 1
    assert open_mistakes[0].mistake_id == r1.mistake_id

    cured_mistakes = vault.list_mistakes("u1", status=MistakeStatus.CURED)
    assert len(cured_mistakes) == 1
    assert cured_mistakes[0].mistake_id == r2.mistake_id


def test_vault_due_mistakes_scheduling(vault):
    """FSRS zamanı gelen hataların get_due_mistakes ile tespit edildiğini doğrular."""
    now = 100000.0
    r1 = vault.record_mistake("u1", "N1", "BUG-1", "p1", "s1", "c1", "", timestamp=now)
    # r1 due_date = now (hemen due)
    due_now = vault.get_due_mistakes("u1", current_timestamp=now)
    assert len(due_now) == 1

    # Geleceğe ertelenen hata
    r1.due_date = now + 50000.0
    vault.update_record(r1)
    due_future = vault.get_due_mistakes("u1", current_timestamp=now)
    assert len(due_future) == 0

    # Süresi dolduğunda tekrar due
    due_later = vault.get_due_mistakes("u1", current_timestamp=now + 60000.0)
    assert len(due_later) == 1


def test_vault_analytics_calculation(vault):
    """Kasa analitiğinin oranları ve en sık yapılan yanılgıları doğru hesapladığını doğrular."""
    # Boş kasa
    empty_stats = vault.get_vault_analytics("empty_user")
    assert empty_stats["total_mistakes"] == 0
    assert empty_stats["cure_rate"] == 0.0

    # 3 hata ekle: 2x BUG-A, 1x BUG-B
    r1 = vault.record_mistake("u_stat", "N1", "BUG-A", "p1", "s1", "c1", "")
    r2 = vault.record_mistake("u_stat", "N2", "BUG-A", "p2", "s2", "c2", "")
    r3 = vault.record_mistake("u_stat", "N3", "BUG-B", "p3", "s3", "c3", "")

    r1.status = MistakeStatus.CURED
    vault.update_record(r1)

    stats = vault.get_vault_analytics("u_stat")
    assert stats["total_mistakes"] == 3
    assert stats["cured_count"] == 1
    assert stats["open_count"] == 2
    assert math.isclose(stats["cure_rate"], 1.0 / 3.0, abs_tol=1e-3)
    assert stats["top_bugs"]["BUG-A"] == 2
    assert stats["top_bugs"]["BUG-B"] == 1


# ==============================================================================
# 2. SELF-CORRECTION SESSION PROTOCOL (3 STAGES)
# ==============================================================================

def test_session_start(session_manager, vault):
    """Kendi hatasını düzeltme seansının 1. aşamadan başlatıldığını doğrular."""
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "")
    res = session_manager.start_session(record.mistake_id)
    assert res["stage"] == 1
    assert res["problem"] == "Problem"
    assert res["offending_step"] == "h^2=b*c"


def test_session_stage_1_diagnosis(session_manager, vault):
    """1. Aşamada hatalı adımı teşhis etme akışını doğrular."""
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "")

    # Başarısız teşhis
    fail_res = session_manager.submit_step_diagnosis(record.mistake_id, is_identified=False)
    assert not fail_res["success"]
    assert fail_res["stage"] == 1

    # Başarılı teşhis -> 2. Aşamaya geçiş
    succ_res = session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)
    assert succ_res["success"]
    assert succ_res["stage"] == 2

    updated = vault.get_mistake(record.mistake_id)
    assert updated.self_correction_stage == SelfCorrectionStage.STAGE_2_EXPLAIN


def test_session_stage_2_explanation(session_manager, vault):
    """2. Aşamada doğru matematiksel ilkeyi ifade etme akışını doğrular."""
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "Directive")
    session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)

    # Yanlış ilke açıklaması
    fail_res = session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=False)
    assert not fail_res["success"]
    assert "Directive" in fail_res["feedback"]

    # Doğru ilke açıklaması -> 3. Aşamaya geçiş
    succ_res = session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=True)
    assert succ_res["success"]
    assert succ_res["stage"] == 3

    updated = vault.get_mistake(record.mistake_id)
    assert updated.self_correction_stage == SelfCorrectionStage.STAGE_3_RESOLVE


def test_session_stage_3_clean_resolution_success(session_manager, vault):
    """3. Aşamada eşyapılı sorunun temiz çözülmesiyle FSRS stabilitesinin arttığını doğrular."""
    now = 200000.0
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "", timestamp=now)
    session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)
    session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=True)

    # Temiz çözüm (Rating.GOOD) 1 gün sonra
    solve_res = session_manager.submit_clean_resolution(
        record.mistake_id,
        is_correct=True,
        current_time=now + 86400.0,
    )
    assert solve_res["success"]
    assert solve_res["status"] == "in_remediation"
    assert solve_res["stability_days"] > 0

    updated = vault.get_mistake(record.mistake_id)
    assert updated.status == MistakeStatus.IN_REMEDIATION
    assert updated.consecutive_clean_solves == 1
    assert updated.due_date > now + 86400.0


def test_session_stage_3_recurrent_failure_resets(session_manager, vault):
    """3. Aşamada hatanın tekrarlanması durumunda 1. aşamaya geri dönüldüğünü doğrular."""
    now = 200000.0
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "", timestamp=now)
    session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)
    session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=True)

    # Başarısız çözüm
    solve_res = session_manager.submit_clean_resolution(
        record.mistake_id,
        is_correct=False,
        current_time=now + 86400.0,
    )
    assert not solve_res["success"]
    assert solve_res["stage"] == 1
    assert solve_res["status"] == "open"

    updated = vault.get_mistake(record.mistake_id)
    assert updated.status == MistakeStatus.OPEN
    assert updated.self_correction_stage == SelfCorrectionStage.STAGE_1_IDENTIFY
    assert updated.consecutive_clean_solves == 0


def test_session_cure_after_multiple_clean_solves(session_manager, vault):
    """Üst üste 2 temiz çözüm ve yüksek stabilite ile hatanın CURED olduğunu doğrular."""
    now = 100000.0
    record = vault.record_mistake("u1", "N164", "BUG-EUC-04", "Problem", "h^2=b*c", "h^2=p*k", "", timestamp=now)

    # 1. Temiz Çözüm
    session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)
    session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=True)
    session_manager.submit_clean_resolution(record.mistake_id, is_correct=True, current_time=now + 86400.0)

    # 2. Temiz Çözüm (3 gün sonra)
    session_manager.submit_step_diagnosis(record.mistake_id, is_identified=True)
    session_manager.submit_principle_explanation(record.mistake_id, is_principle_correct=True)
    res2 = session_manager.submit_clean_resolution(record.mistake_id, is_correct=True, current_time=now + 4 * 86400.0)

    updated = vault.get_mistake(record.mistake_id)
    assert updated.consecutive_clean_solves == 2
    assert updated.status == MistakeStatus.CURED


# ==============================================================================
# 3. FSRS BOSS BATTLE ENGINE
# ==============================================================================

def test_boss_battle_spawn_eligibility(boss_engine, vault):
    """En az 3 due hata yokken Boss Battle oluşturulamadığını, 3 hata olunca tetiklendiğini doğrular."""
    now = 50000.0
    # 2 hata ekle -> Boss spawn olmaz
    vault.record_mistake("u_boss", "N1", "BUG-1", "p1", "s1", "c1", "", timestamp=now)
    vault.record_mistake("u_boss", "N2", "BUG-2", "p2", "s2", "c2", "", timestamp=now)
    assert not boss_engine.can_spawn_boss("u_boss", current_time=now)
    assert boss_engine.spawn_boss_battle("u_boss", current_time=now) is None

    # 3. hatayı ekle -> Boss doğar!
    vault.record_mistake("u_boss", "N3", "BUG-3", "p3", "s3", "c3", "", timestamp=now)
    assert boss_engine.can_spawn_boss("u_boss", current_time=now)

    battle = boss_engine.spawn_boss_battle("u_boss", current_time=now)
    assert battle is not None
    assert battle.boss_max_hp == 300
    assert battle.boss_current_hp == 300
    assert len(battle.mistakes_queue) == 3
    assert not battle.is_defeated


def test_boss_battle_turn_clean_hit_and_victory(boss_engine, vault):
    """Boss savaşında temiz çözümlerle kombo ve zafer elde edildiğini doğrular."""
    now = 50000.0
    for i in range(3):
        vault.record_mistake("u_boss", f"N{i}", f"BUG-{i}", f"p{i}", f"s{i}", f"c{i}", "", timestamp=now)

    battle = boss_engine.spawn_boss_battle("u_boss", current_time=now)
    battle_id = battle.battle_id

    # 1. Raund: Temiz Çözüm -> 100 Hasar (combo=1)
    turn1 = boss_engine.submit_boss_turn(battle_id, is_clean_solve=True, current_time=now)
    assert not turn1["boss_defeated"]
    assert turn1["damage_dealt"] == 100
    assert turn1["remaining_hp"] == 200
    assert turn1["combo_streak"] == 1

    # 2. Raund: Temiz Çözüm -> 125 Hasar (combo=2)
    turn2 = boss_engine.submit_boss_turn(battle_id, is_clean_solve=True, current_time=now)
    assert not turn2["boss_defeated"]
    assert turn2["damage_dealt"] == 125
    assert turn2["remaining_hp"] == 75
    assert turn2["combo_streak"] == 2

    # 3. Raund: Temiz Çözüm -> 150 Hasar (kalan 75 HP biter, zafer!)
    turn3 = boss_engine.submit_boss_turn(battle_id, is_clean_solve=True, current_time=now)
    assert turn3["boss_defeated"]
    assert turn3["remaining_hp"] == 0
    assert "ZAFER" in turn3["message"]

    b_state = boss_engine.get_battle(battle_id)
    assert b_state.is_defeated


def test_boss_battle_counter_attack_on_mistake(boss_engine, vault):
    """Boss savaşında hata yapıldığında karşı saldırı yapıldığını ve kombonun sıfırlandığını doğrular."""
    now = 50000.0
    for i in range(3):
        vault.record_mistake("u_boss", f"N{i}", f"BUG-{i}", f"p{i}", f"s{i}", f"c{i}", "", timestamp=now)

    battle = boss_engine.spawn_boss_battle("u_boss", current_time=now)
    battle_id = battle.battle_id

    # 1. Vuruş başarılı
    boss_engine.submit_boss_turn(battle_id, is_clean_solve=True, current_time=now)
    # 2. Vuruş hatalı -> Karşı saldırı
    turn2 = boss_engine.submit_boss_turn(battle_id, is_clean_solve=False, current_time=now)
    assert not turn2["boss_defeated"]
    assert turn2["damage_dealt"] == 0
    assert turn2["combo_streak"] == 0
    assert turn2.get("counter_attack") is True


# ==============================================================================
# 4. ERROR HANDLING & BOUNDARY CASES
# ==============================================================================

def test_session_manager_invalid_id(session_manager):
    with pytest.raises(KeyError, match="bulunamadı"):
        session_manager.start_session("non_existent_id")

    with pytest.raises(KeyError, match="bulunamadı"):
        session_manager.submit_step_diagnosis("non_existent_id", True)

    with pytest.raises(KeyError, match="bulunamadı"):
        session_manager.submit_principle_explanation("non_existent_id", True)

    with pytest.raises(KeyError, match="bulunamadı"):
        session_manager.submit_clean_resolution("non_existent_id", True)


def test_boss_battle_inactive_turn(boss_engine):
    with pytest.raises(ValueError, match="Aktif olmayan"):
        boss_engine.submit_boss_turn("fake_battle_id", True)


# ==============================================================================
# 5. ADVANCED FSRS RETENTION, ZERO-LEAKAGE & STABILITY TESTS
# ==============================================================================

def test_vault_record_history_ledger(vault):
    """Her otopsi dosyasının geçmiş hamleleri (history ledger) kronolojik kaydettiğini doğrular."""
    r = vault.record_mistake("u1", "N10", "BUG-QUAD-01", "Prob", "x(x+2)=3", "Rule", "Dir")
    assert len(r.history) >= 1
    assert r.history[0]["action"] == "RECORDED"
    assert r.history[0]["offending_step"] == "x(x+2)=3"


def test_fsrs_initial_difficulty_within_bounds(vault):
    """Yeni oluşturulan hata kayıtlarında FSRS zorluk değerinin [1.0, 10.0] aralığında olduğunu doğrular."""
    r = vault.record_mistake("u1", "N10", "BUG-QUAD-01", "Prob", "step", "rule", "dir")
    assert 1.0 <= r.dsr_state.difficulty <= 10.0
    assert r.dsr_state.stability > 0.0


def test_fsrs_retrievability_decay_over_time(vault):
    """Zaman geçtikçe FSRS retrievability değerinin azaldığını doğrular."""
    stability = 2.0
    r0 = vault.fsrs.retrievability(0.0, stability)
    r1 = vault.fsrs.retrievability(1.0, stability)
    r5 = vault.fsrs.retrievability(5.0, stability)
    assert r0 == 1.0
    assert r0 > r1 > r5 > 0.0


def test_fsrs_circadian_sleep_barrier(vault, session_manager):
    """Aynı gün içinde (14 saatten az sürede) yapılan tekrarlarda Circadian Sleep Barrier nedeniyle stabilitenin artmadığını doğrular."""
    now = 100000.0
    r = vault.record_mistake("u1", "N1", "BUG-1", "P", "S", "C", "D", timestamp=now)
    init_stability = r.dsr_state.stability

    # 4 saat sonra temiz çözüm (4 saat < 14 saat)
    session_manager.submit_step_diagnosis(r.mistake_id, True)
    session_manager.submit_principle_explanation(r.mistake_id, True)
    res = session_manager.submit_clean_resolution(r.mistake_id, True, current_time=now + 4 * 3600.0)

    updated = vault.get_mistake(r.mistake_id)
    # Circadian lock nedeniyle stabilite artmaz, aynı kalır
    assert updated.dsr_state.stability == init_stability


def test_fsrs_sleep_consolidated_stability_increase(vault, session_manager):
    """Uyku konsolidasyonu (14 saatten fazla) sonrasında yapılan temiz çözümde stabilitenin arttığını doğrular."""
    now = 100000.0
    r = vault.record_mistake("u1", "N1", "BUG-1", "P", "S", "C", "D", timestamp=now)
    init_stability = r.dsr_state.stability

    # 24 saat (1 gün) sonra temiz çözüm
    session_manager.submit_step_diagnosis(r.mistake_id, True)
    session_manager.submit_principle_explanation(r.mistake_id, True)
    session_manager.submit_clean_resolution(r.mistake_id, True, current_time=now + 24 * 3600.0)

    updated = vault.get_mistake(r.mistake_id)
    assert updated.dsr_state.stability > init_stability


def test_zero_leakage_self_correction_prompts(session_manager, vault):
    """Kendi hatasını düzeltme seansının soru kökünü ve yönlendirmesini sızdırmadan sunduğunu doğrular."""
    r = vault.record_mistake(
        "u1", "N1", "BUG-EUC-04",
        "h = 6, p = 4 ise k = 9",
        "h^2 = b * c",
        "h^2 = p * k",
        "Yüksekliğin karesi ayrılan parçaların çarpımına eşittir.",
    )
    res1 = session_manager.start_session(r.mistake_id)
    # Prompt ipucu içermeli ancak hedef cevap olan 9'u sızdırmamalıdır
    assert "9" not in res1["prompt"]
    assert "mantıksal veya işlemsel kırılmayı tespit et" in res1["prompt"]


def test_boss_battle_cannot_spawn_with_non_due_mistakes(boss_engine, vault):
    """Hatalar mevcut olsa bile henüz due_date'i gelmemişse Boss Battle oluşturulamadığını doğrular."""
    now = 100000.0
    for i in range(5):
        r = vault.record_mistake("u_future", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)
        # Geleceğe ertele
        r.due_date = now + 100000.0
        vault.update_record(r)

    assert not boss_engine.can_spawn_boss("u_future", current_time=now)
    assert boss_engine.spawn_boss_battle("u_future", current_time=now) is None


def test_boss_battle_multiple_due_scaling(boss_engine, vault):
    """5 due hata varken Boss HP'sinin 500 olarak ölçeklendiğini doğrular."""
    now = 100000.0
    for i in range(5):
        vault.record_mistake("u_epic", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)

    battle = boss_engine.spawn_boss_battle("u_epic", current_time=now)
    assert battle.boss_max_hp == 500
    assert battle.boss_current_hp == 500
    assert len(battle.mistakes_queue) == 5


def test_boss_battle_cured_mistakes_in_vault(boss_engine, vault):
    """Boss battle'da yenilen hataların kasada CURED olarak güncellendiğini doğrular."""
    now = 100000.0
    r_list = [
        vault.record_mistake("u_cure", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)
        for i in range(3)
    ]
    battle = boss_engine.spawn_boss_battle("u_cure", current_time=now)

    # 3 raund temiz çözüm
    for _ in range(3):
        boss_engine.submit_boss_turn(battle.battle_id, is_clean_solve=True, current_time=now)

    assert battle.is_defeated
    for r in r_list:
        fresh = vault.get_mistake(r.mistake_id)
        assert fresh.status == MistakeStatus.CURED
        assert fresh.consecutive_clean_solves >= 1


def test_vault_user_isolation(vault):
    """Farklı kullanıcıların hatalarının birbirine karışmadığını doğrular."""
    vault.record_mistake("alice", "N1", "BUG-1", "P", "S", "C", "D")
    vault.record_mistake("bob", "N2", "BUG-2", "P", "S", "C", "D")

    alice_m = vault.list_mistakes("alice")
    bob_m = vault.list_mistakes("bob")
    assert len(alice_m) == 1
    assert len(bob_m) == 1
    assert alice_m[0].bug_id == "BUG-1"
    assert bob_m[0].bug_id == "BUG-2"


def test_fsrs_rating_hard_modifier(vault):
    init_dsr = vault.fsrs.init_dsr(Rating.AGAIN)
    # HARD review
    dsr_hard = vault.fsrs.review(init_dsr, Rating.HARD, elapsed_days=2.0)
    # GOOD review
    dsr_good = vault.fsrs.review(init_dsr, Rating.GOOD, elapsed_days=2.0)
    # HARD artışı GOOD artışından daha düşüktür
    assert dsr_hard.stability <= dsr_good.stability


def test_fsrs_rating_easy_modifier(vault):
    init_dsr = vault.fsrs.init_dsr(Rating.AGAIN)
    # EASY review
    dsr_easy = vault.fsrs.review(init_dsr, Rating.EASY, elapsed_days=2.0)
    dsr_good = vault.fsrs.review(init_dsr, Rating.GOOD, elapsed_days=2.0)
    # EASY artışı GOOD artışından daha büyüktür
    assert dsr_easy.stability >= dsr_good.stability


def test_fsrs_rating_again_increments_lapse(vault):
    init_dsr = vault.fsrs.init_dsr(Rating.GOOD)
    assert init_dsr.lapses == 0
    lapsed_dsr = vault.fsrs.review(init_dsr, Rating.AGAIN, elapsed_days=2.0)
    assert lapsed_dsr.lapses == 1


def test_fsrs_fatigue_discount_over_15_minutes(vault):
    init_dsr = vault.fsrs.init_dsr(Rating.AGAIN)
    normal = vault.fsrs.review(init_dsr, Rating.GOOD, elapsed_days=2.0, session_duration_minutes=10.0)
    fatigued = vault.fsrs.review(init_dsr, Rating.GOOD, elapsed_days=2.0, session_duration_minutes=25.0)
    assert fatigued.stability < normal.stability


def test_boss_battle_damage_streak_progression(boss_engine, vault):
    now = 10000.0
    for i in range(4):
        vault.record_mistake("u_combo", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)
    battle = boss_engine.spawn_boss_battle("u_combo", current_time=now)

    turn1 = boss_engine.submit_boss_turn(battle.battle_id, True, current_time=now)
    assert turn1["damage_dealt"] == 100
    turn2 = boss_engine.submit_boss_turn(battle.battle_id, True, current_time=now)
    assert turn2["damage_dealt"] == 125
    turn3 = boss_engine.submit_boss_turn(battle.battle_id, True, current_time=now)
    assert turn3["damage_dealt"] == 150


def test_boss_battle_get_battle(boss_engine, vault):
    now = 10000.0
    for i in range(3):
        vault.record_mistake("u_get", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)
    battle = boss_engine.spawn_boss_battle("u_get", current_time=now)
    found = boss_engine.get_battle(battle.battle_id)
    assert found == battle


def test_vault_update_existing_record(vault):
    r = vault.record_mistake("u1", "N1", "BUG-1", "P", "S", "C", "D")
    r.problem_statement = "Updated Problem"
    vault.update_record(r)
    retrieved = vault.get_mistake(r.mistake_id)
    assert retrieved.problem_statement == "Updated Problem"


def test_vault_get_non_existent_mistake(vault):
    assert vault.get_mistake("does_not_exist") is None


def test_vault_list_mistakes_sorting(vault):
    now = 1000.0
    r1 = vault.record_mistake("u_sort", "N1", "BUG-1", "P", "S", "C", "D", timestamp=now)
    r2 = vault.record_mistake("u_sort", "N2", "BUG-2", "P", "S", "C", "D", timestamp=now + 100.0)
    sorted_list = vault.list_mistakes("u_sort")
    # En yeni ilk gelir (reverse=True)
    assert sorted_list[0].mistake_id == r2.mistake_id
    assert sorted_list[1].mistake_id == r1.mistake_id


def test_vault_analytics_multiple_bugs(vault):
    for i in range(5):
        vault.record_mistake("u_multi", f"N{i}", "BUG-A", "P", "S", "C", "D")
    for i in range(3):
        vault.record_mistake("u_multi", f"N{i}", "BUG-B", "P", "S", "C", "D")
    for i in range(1):
        vault.record_mistake("u_multi", f"N{i}", "BUG-C", "P", "S", "C", "D")

    stats = vault.get_vault_analytics("u_multi")
    assert stats["total_mistakes"] == 9
    top = list(stats["top_bugs"].keys())
    assert top[0] == "BUG-A"
    assert top[1] == "BUG-B"
    assert top[2] == "BUG-C"


def test_session_manager_stage_progression_integrity(session_manager, vault):
    r = vault.record_mistake("u_prog", "N1", "BUG-1", "P", "S", "C", "D")
    assert r.self_correction_stage == SelfCorrectionStage.STAGE_1_IDENTIFY
    session_manager.submit_step_diagnosis(r.mistake_id, True)
    r = vault.get_mistake(r.mistake_id)
    assert r.self_correction_stage == SelfCorrectionStage.STAGE_2_EXPLAIN
    session_manager.submit_principle_explanation(r.mistake_id, True)
    r = vault.get_mistake(r.mistake_id)
    assert r.self_correction_stage == SelfCorrectionStage.STAGE_3_RESOLVE


def test_session_manager_repeated_clean_solve_remediation(session_manager, vault):
    now = 50000.0
    r = vault.record_mistake("u_rep", "N1", "BUG-1", "P", "S", "C", "D", timestamp=now)
    # İlk temiz çözüm -> in_remediation
    session_manager.submit_step_diagnosis(r.mistake_id, True)
    session_manager.submit_principle_explanation(r.mistake_id, True)
    session_manager.submit_clean_resolution(r.mistake_id, True, current_time=now + 86400.0)
    r = vault.get_mistake(r.mistake_id)
    assert r.status == MistakeStatus.IN_REMEDIATION
    assert r.consecutive_clean_solves == 1


def test_boss_battle_queue_advancement(boss_engine, vault):
    now = 10000.0
    for i in range(3):
        vault.record_mistake("u_q", f"N{i}", f"BUG-{i}", "P", "S", "C", "D", timestamp=now)
    battle = boss_engine.spawn_boss_battle("u_q", current_time=now)
    assert battle.current_index == 0
    boss_engine.submit_boss_turn(battle.battle_id, True, current_time=now)
    assert battle.current_index == 1
    boss_engine.submit_boss_turn(battle.battle_id, True, current_time=now)
    assert battle.current_index == 2


def test_boss_battle_state_schema():
    b = BossBattleState(
        user_id="u_schema",
        boss_name="Test Boss",
        boss_max_hp=200,
        boss_current_hp=150,
        mistakes_queue=["m1", "m2"],
    )
    assert b.boss_name == "Test Boss"
    assert b.boss_max_hp == 200
    assert not b.is_defeated



