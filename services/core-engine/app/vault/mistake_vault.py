"""
Kişisel Hata Otopsisi Kasası, Kendi Hatasını Düzeltme Seansı ve Boss Battle Motoru (HEDEF 12).
FSRS-4.5 aralıklı tekrar modeliyle entegre bilişsel hata hafızası ve telafi seansları.
"""
from __future__ import annotations
import time
import uuid
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.retention.fsrs import FSRSEngine, Rating, DSRState


class MistakeStatus(str, Enum):
    OPEN = "open"                     # Yeni yapılan / telafi edilmemiş hata
    IN_REMEDIATION = "in_remediation" # Kendi hatasını düzeltme sürecinde
    CURED = "cured"                   # FSRS pekiştirilmiş, üst üste temiz çözülmüş


class SelfCorrectionStage(int, Enum):
    STAGE_1_IDENTIFY = 1  # 1. Aşama: Hatalı terimi ve bozuk kuralı teşhis et
    STAGE_2_EXPLAIN = 2   # 2. Aşama: Doğru matematiksel ilkeyi kendi cümlelerinle ifade et
    STAGE_3_RESOLVE = 3   # 3. Aşama: Eşyapılı (isomorphic) taze soruyu temiz çöz
    COMPLETED = 4         # Telafi başarıyla tamamlandı


class MistakeRecord(BaseModel):
    """Bilişsel Hata Otopsisi Kasasındaki kalıcı kayıt kartı."""
    mistake_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    node_id: str
    bug_id: str
    problem_statement: str
    offending_step: str
    correct_principle: str
    remediation_directive: str
    created_at: float = Field(default_factory=time.time)
    last_reviewed_at: Optional[float] = None
    due_date: float = Field(default_factory=time.time)
    status: MistakeStatus = MistakeStatus.OPEN
    dsr_state: DSRState
    self_correction_stage: SelfCorrectionStage = SelfCorrectionStage.STAGE_1_IDENTIFY
    consecutive_clean_solves: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)


class BossBattleState(BaseModel):
    """FSRS Boss Battle Oyun Durumu."""
    battle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    boss_name: str
    boss_max_hp: int
    boss_current_hp: int
    mistakes_queue: List[str]
    current_index: int = 0
    is_defeated: bool = False
    combo_streak: int = 0


class CognitiveMistakeVault:
    """
    Kişisel Bilişsel Hata Otopsisi Kasası.
    Öğrencinin kavramsal yanılgılarını (misconceptions) kalıcı olarak saklar,
    FSRS-4.5 ile zamanlar ve unutma eğrisine göre telafi planlar.
    """

    def __init__(self, fsrs_engine: Optional[FSRSEngine] = None):
        self.fsrs = fsrs_engine or FSRSEngine()
        # In-memory storage: mistake_id -> MistakeRecord
        self._records: Dict[str, MistakeRecord] = {}

    def record_mistake(
        self,
        user_id: str,
        node_id: str,
        bug_id: str,
        problem_statement: str,
        offending_step: str,
        correct_principle: str,
        remediation_directive: str,
        timestamp: Optional[float] = None,
    ) -> MistakeRecord:
        """Kavramsal bir hata yapıldığında kasaya yeni bir otopsi dosyası açar."""
        curr_time = timestamp if timestamp is not None else time.time()
        # Yeni hata için FSRS başlangıç durumu: Rating.AGAIN
        init_dsr = self.fsrs.init_dsr(Rating.AGAIN)
        # Hemen telafi edilmesi için due_date = curr_time
        due_date = curr_time

        record = MistakeRecord(
            user_id=user_id,
            node_id=node_id,
            bug_id=bug_id,
            problem_statement=problem_statement,
            offending_step=offending_step,
            correct_principle=correct_principle,
            remediation_directive=remediation_directive,
            created_at=curr_time,
            last_reviewed_at=curr_time,
            due_date=due_date,
            status=MistakeStatus.OPEN,
            dsr_state=init_dsr,
            self_correction_stage=SelfCorrectionStage.STAGE_1_IDENTIFY,
            consecutive_clean_solves=0,
            history=[{
                "action": "RECORDED",
                "timestamp": curr_time,
                "offending_step": offending_step,
            }],
        )
        self._records[record.mistake_id] = record
        return record

    def get_mistake(self, mistake_id: str) -> Optional[MistakeRecord]:
        return self._records.get(mistake_id)

    def list_mistakes(
        self,
        user_id: str,
        status: Optional[MistakeStatus] = None,
    ) -> List[MistakeRecord]:
        """Kullanıcının kayıtlı hatalarını filtreli listeler."""
        user_records = [r for r in self._records.values() if r.user_id == user_id]
        if status is not None:
            user_records = [r for r in user_records if r.status == status]
        return sorted(user_records, key=lambda x: x.created_at, reverse=True)

    def get_due_mistakes(
        self,
        user_id: str,
        current_timestamp: Optional[float] = None,
    ) -> List[MistakeRecord]:
        """FSRS tekrar zamanı gelmiş (due_date <= current_time) ve henüz kür edilmemiş hataları getirir."""
        curr_time = current_timestamp if current_timestamp is not None else time.time()
        due = [
            r for r in self._records.values()
            if r.user_id == user_id
            and r.status != MistakeStatus.CURED
            and r.due_date <= curr_time
        ]
        return sorted(due, key=lambda x: x.due_date)

    def update_record(self, record: MistakeRecord) -> None:
        self._records[record.mistake_id] = record

    def get_vault_analytics(self, user_id: str) -> Dict[str, Any]:
        """Kasa analitiği: Açık, telafide, kür edilmiş oranları ve en sık yapılan yanılgılar."""
        user_records = [r for r in self._records.values() if r.user_id == user_id]
        total = len(user_records)
        if total == 0:
            return {
                "total_mistakes": 0,
                "open_count": 0,
                "in_remediation_count": 0,
                "cured_count": 0,
                "cure_rate": 0.0,
                "top_bugs": {},
            }

        open_c = sum(1 for r in user_records if r.status == MistakeStatus.OPEN)
        remed_c = sum(1 for r in user_records if r.status == MistakeStatus.IN_REMEDIATION)
        cured_c = sum(1 for r in user_records if r.status == MistakeStatus.CURED)

        bug_freq: Dict[str, int] = {}
        for r in user_records:
            bug_freq[r.bug_id] = bug_freq.get(r.bug_id, 0) + 1

        top_bugs = dict(sorted(bug_freq.items(), key=lambda item: item[1], reverse=True)[:5])

        return {
            "total_mistakes": total,
            "open_count": open_c,
            "in_remediation_count": remed_c,
            "cured_count": cured_c,
            "cure_rate": round(cured_c / total, 3),
            "top_bugs": top_bugs,
        }


class SelfCorrectionSessionManager:
    """
    3 Aşamalı Kendi Hatasını Düzeltme Seansı Yöneticisi:
    1. Hatanı Teşhis Et
    2. İlkeyi İfade Et
    3. Temiz Çöz (İzomorfik Soru)
    """

    def __init__(self, vault: CognitiveMistakeVault):
        self.vault = vault

    def start_session(self, mistake_id: str) -> Dict[str, Any]:
        record = self.vault.get_mistake(mistake_id)
        if not record:
            raise KeyError(f"Hata kaydı bulunamadı: {mistake_id}")

        return {
            "mistake_id": record.mistake_id,
            "stage": record.self_correction_stage.value,
            "problem": record.problem_statement,
            "offending_step": record.offending_step,
            "prompt": "1. Aşama: Kendi yazdığın adımdaki mantıksal veya işlemsel kırılmayı tespit et.",
        }

    def submit_step_diagnosis(
        self,
        mistake_id: str,
        is_identified: bool,
    ) -> Dict[str, Any]:
        """Aşama 1: Öğrenci bozuk kuralı veya hatalı terimi doğru seçti mi?"""
        record = self.vault.get_mistake(mistake_id)
        if not record:
            raise KeyError(f"Hata kaydı bulunamadı: {mistake_id}")

        if is_identified:
            record.self_correction_stage = SelfCorrectionStage.STAGE_2_EXPLAIN
            record.history.append({
                "action": "DIAGNOSIS_SUCCESS",
                "timestamp": time.time(),
            })
            self.vault.update_record(record)
            return {
                "success": True,
                "stage": 2,
                "prompt": "Harika teşhis! Şimdi bu adımda uygulanması gereken doğru matematiksel kuralı seç veya ifade et.",
            }
        else:
            return {
                "success": False,
                "stage": 1,
                "feedback": "Seçilen ifade asıl kavramsal yanılgının kaynağı değil. Adımı tekrar incele.",
            }

    def submit_principle_explanation(
        self,
        mistake_id: str,
        is_principle_correct: bool,
    ) -> Dict[str, Any]:
        """Aşama 2: Öğrenci doğru matematiksel kuralı ifade etti mi?"""
        record = self.vault.get_mistake(mistake_id)
        if not record:
            raise KeyError(f"Hata kaydı bulunamadı: {mistake_id}")

        if is_principle_correct:
            record.self_correction_stage = SelfCorrectionStage.STAGE_3_RESOLVE
            record.history.append({
                "action": "EXPLANATION_SUCCESS",
                "timestamp": time.time(),
            })
            self.vault.update_record(record)
            return {
                "success": True,
                "stage": 3,
                "prompt": f"Kavramı mükemmel kavradın! Şimdi aynı kuralı kullanan şu taze soruyu çöz: [İzomorfik Soru]",
            }
        else:
            return {
                "success": False,
                "stage": 2,
                "feedback": "İfade edilen kural bu soru tipi için geçerli değil. Hatırla: " + record.remediation_directive,
            }

    def submit_clean_resolution(
        self,
        mistake_id: str,
        is_correct: bool,
        current_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Aşama 3: Öğrenci eşyapılı soruyu temiz çözdü mü?"""
        record = self.vault.get_mistake(mistake_id)
        if not record:
            raise KeyError(f"Hata kaydı bulunamadı: {mistake_id}")

        now = current_time if current_time is not None else time.time()
        elapsed_days = max(0.0, (now - (record.last_reviewed_at or record.created_at)) / 86400.0)

        if is_correct:
            # FSRS review with Rating.GOOD
            new_dsr = self.vault.fsrs.review(record.dsr_state, Rating.GOOD, elapsed_days)
            record.dsr_state = new_dsr
            record.last_reviewed_at = now
            record.consecutive_clean_solves += 1

            # Stability oranında ileriye at: interval = S (gün)
            interval_seconds = max(1.0, new_dsr.stability) * 86400.0
            record.due_date = now + interval_seconds

            # 2 kez üst üste temiz çözülmüşse ve stabilite >= 2.0 gün ise CURED
            if record.consecutive_clean_solves >= 2 and new_dsr.stability >= 2.0:
                record.status = MistakeStatus.CURED
            else:
                record.status = MistakeStatus.IN_REMEDIATION

            record.self_correction_stage = SelfCorrectionStage.COMPLETED
            record.history.append({
                "action": "CLEAN_SOLVE_SUCCESS",
                "timestamp": now,
                "new_stability": new_dsr.stability,
                "new_status": record.status.value,
            })
            self.vault.update_record(record)
            return {
                "success": True,
                "stage": 4,
                "status": record.status.value,
                "stability_days": new_dsr.stability,
                "next_due_date": record.due_date,
                "message": "Tebrikler! Bilişsel yanılgı başarıyla telafi edildi ve FSRS hafızasına işlendi.",
            }
        else:
            # Hata devam ediyor: Rating.AGAIN
            new_dsr = self.vault.fsrs.review(record.dsr_state, Rating.AGAIN, elapsed_days)
            record.dsr_state = new_dsr
            record.last_reviewed_at = now
            record.consecutive_clean_solves = 0
            record.due_date = now + 3600.0  # 1 saat sonra tekrar dene
            record.status = MistakeStatus.OPEN
            record.self_correction_stage = SelfCorrectionStage.STAGE_1_IDENTIFY
            record.history.append({
                "action": "CLEAN_SOLVE_FAILED",
                "timestamp": now,
                "new_stability": new_dsr.stability,
            })
            self.vault.update_record(record)
            return {
                "success": False,
                "stage": 1,
                "status": record.status.value,
                "message": "Çözümde aynı kavramsal tuzak tekrar tetiklendi. Telafi 1. aşamadan yeniden başlatılıyor.",
            }


class BossBattleEngine:
    """
    FSRS Boss Battle Motoru:
    Zamanı gelmiş (due) en az 3 hata biriktiğinde epik bir 'Kavram Canavarı' boss dövüşü tetikler.
    Her hatasız çözüm boss'a kritik hasar vurur; hata yapılması boss'u güçlendirir.
    """

    def __init__(self, vault: CognitiveMistakeVault):
        self.vault = vault
        self._active_battles: Dict[str, BossBattleState] = {}

    def can_spawn_boss(self, user_id: str, current_time: Optional[float] = None) -> bool:
        """En az 3 due hata varsa Boss Battle tetiklenebilir."""
        due_mistakes = self.vault.get_due_mistakes(user_id, current_time)
        return len(due_mistakes) >= 3

    def spawn_boss_battle(
        self,
        user_id: str,
        current_time: Optional[float] = None,
    ) -> Optional[BossBattleState]:
        due = self.vault.get_due_mistakes(user_id, current_time)
        if len(due) < 3:
            return None

        boss_names = [
            "Kavram Kargaşası Efendisi (Lord of Misconceptions)",
            "İşaret Katili (The Sign Slayer)",
            "Kök Yutucu Ejderha (Root Devourer)",
            "Öklid Gölgeleri Hükümdarı (Ruler of Euclidean Shadows)",
        ]
        # Boss HP = 100 * due_mistake_count
        hp = len(due) * 100
        name = boss_names[len(due) % len(boss_names)]
        mistake_ids = [m.mistake_id for m in due]

        state = BossBattleState(
            user_id=user_id,
            boss_name=name,
            boss_max_hp=hp,
            boss_current_hp=hp,
            mistakes_queue=mistake_ids,
            current_index=0,
            is_defeated=False,
            combo_streak=0,
        )
        self._active_battles[state.battle_id] = state
        return state

    def get_battle(self, battle_id: str) -> Optional[BossBattleState]:
        return self._active_battles.get(battle_id)

    def submit_boss_turn(
        self,
        battle_id: str,
        is_clean_solve: bool,
        current_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Boss savaşı raund hamlesi."""
        battle = self._active_battles.get(battle_id)
        if not battle or battle.is_defeated:
            raise ValueError("Aktif olmayan veya bitmiş Boss savaşı!")

        current_mistake_id = battle.mistakes_queue[battle.current_index]
        record = self.vault.get_mistake(current_mistake_id)

        if is_clean_solve:
            battle.combo_streak += 1
            damage = 100 + (battle.combo_streak - 1) * 25
            battle.boss_current_hp = max(0, battle.boss_current_hp - damage)

            # Hatayı kür et / güncelle
            if record:
                now = current_time if current_time is not None else time.time()
                record.status = MistakeStatus.CURED
                record.consecutive_clean_solves += 1
                record.last_reviewed_at = now
                record.dsr_state.stability = max(5.0, record.dsr_state.stability * 2.0)
                record.due_date = now + (record.dsr_state.stability * 86400.0)
                self.vault.update_record(record)

            battle.current_index += 1
            if battle.boss_current_hp == 0 or battle.current_index >= len(battle.mistakes_queue):
                battle.is_defeated = True
                return {
                    "boss_defeated": True,
                    "damage_dealt": damage,
                    "remaining_hp": 0,
                    "combo_streak": battle.combo_streak,
                    "message": f"ZAFER! {battle.boss_name} mağlup edildi! Tüm kavram yanılgıları bertaraf edildi!",
                }

            return {
                "boss_defeated": False,
                "damage_dealt": damage,
                "remaining_hp": battle.boss_current_hp,
                "combo_streak": battle.combo_streak,
                "next_mistake_index": battle.current_index,
                "message": f"Kritik Darbe! {damage} hasar verildi!",
            }
        else:
            # Hata yapıldı: Boss karşı saldırı yapar, combo sıfırlanır
            battle.combo_streak = 0
            if record:
                record.status = MistakeStatus.OPEN
                record.consecutive_clean_solves = 0
                self.vault.update_record(record)

            return {
                "boss_defeated": False,
                "damage_dealt": 0,
                "remaining_hp": battle.boss_current_hp,
                "combo_streak": 0,
                "counter_attack": True,
                "message": f"{battle.boss_name} karşı saldırı yaptı! Bilişsel tuzak tetiklendi.",
            }
