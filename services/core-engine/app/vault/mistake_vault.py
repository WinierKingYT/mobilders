"""
Kişisel Hata Otopsisi Kasası, Kendi Hatasını Düzeltme Seansı ve Boss Battle Motoru (HEDEF 12).
FSRS-4.5 aralıklı tekrar modeliyle entegre bilişsel hata hafızası ve telafi seansları.
"""
from __future__ import annotations
import math
import time
import uuid
import sqlite3
import json
import os
import threading
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
    Öğrencinin kavramsal yanılgılarını (misconceptions) kalıcı olarak SQLite/Postgres tabanında saklar,
    FSRS-4.5 ile zamanlar ve unutma eğrisine göre telafi planlar.
    Eşzamanlı isteklerde tam thread-safety garantisi sunar.
    """

    def __init__(
        self,
        fsrs_engine: Optional[FSRSEngine] = None,
        db_path: str = ":memory:",
    ):
        self.fsrs = fsrs_engine or FSRSEngine()
        self.db_path = db_path
        self._lock = threading.Lock()
        with self._lock:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._init_db()
            self._records: Dict[str, MistakeRecord] = {}
            self._load_all_from_db()

    def _init_db(self) -> None:
        """SQLite şemasını ve indekslerini başlatır."""
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistake_records (
                mistake_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                bug_id TEXT NOT NULL,
                problem_statement TEXT NOT NULL,
                offending_step TEXT NOT NULL,
                correct_principle TEXT NOT NULL,
                remediation_directive TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_reviewed_at REAL,
                due_date REAL NOT NULL,
                status TEXT NOT NULL,
                dsr_stability REAL NOT NULL,
                dsr_difficulty REAL NOT NULL,
                dsr_retrievability REAL NOT NULL,
                dsr_repetitions INTEGER NOT NULL,
                dsr_lapses INTEGER NOT NULL,
                self_correction_stage INTEGER NOT NULL,
                consecutive_clean_solves INTEGER NOT NULL,
                history_json TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mistakes_user_due ON mistake_records(user_id, status, due_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mistakes_bug ON mistake_records(bug_id);")
        self._conn.commit()

    def _save_record_to_db(self, record: MistakeRecord) -> None:
        """Kayıt kartını SQLite veritabanına yazar."""
        with self._lock:
            cursor = self._conn.cursor()
            status_str = record.status.value if hasattr(record.status, "value") else str(record.status)
            stage_val = (
                record.self_correction_stage.value
                if hasattr(record.self_correction_stage, "value")
                else int(record.self_correction_stage)
            )
            cursor.execute("""
                INSERT OR REPLACE INTO mistake_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.mistake_id,
                record.user_id,
                record.node_id,
                record.bug_id,
                record.problem_statement,
                record.offending_step,
                record.correct_principle,
                record.remediation_directive,
                record.created_at,
                record.last_reviewed_at,
                record.due_date,
                status_str,
                record.dsr_state.stability,
                record.dsr_state.difficulty,
                record.dsr_state.retrievability,
                record.dsr_state.repetitions,
                record.dsr_state.lapses,
                stage_val,
                record.consecutive_clean_solves,
                json.dumps(record.history),
            ))
            self._conn.commit()

    def _row_to_record(self, row: tuple) -> MistakeRecord:
        """Veritabanı satırını MistakeRecord nesnesine dönüştürür."""
        (
            mistake_id, user_id, node_id, bug_id, problem_statement,
            offending_step, correct_principle, remediation_directive,
            created_at, last_reviewed_at, due_date, status_val,
            dsr_stability, dsr_difficulty, dsr_retrievability,
            dsr_repetitions, dsr_lapses,
            self_corr_stage_val, consec_clean, history_json
        ) = row

        try:
            stab = float(dsr_stability)
            if not math.isfinite(stab) or stab <= 0:
                stab = 0.5
        except Exception:
            stab = 0.5

        try:
            diff = float(dsr_difficulty)
            if not math.isfinite(diff):
                diff = 5.0
        except Exception:
            diff = 5.0

        try:
            ret = float(dsr_retrievability)
            if not math.isfinite(ret):
                ret = 1.0
        except Exception:
            ret = 1.0

        try:
            reps = int(dsr_repetitions)
        except Exception:
            reps = 0

        try:
            laps = int(dsr_lapses)
        except Exception:
            laps = 0

        dsr = DSRState(
            stability=stab,
            difficulty=diff,
            retrievability=ret,
            repetitions=reps,
            lapses=laps,
        )

        try:
            status_enum = MistakeStatus(status_val)
        except Exception:
            status_enum = MistakeStatus.OPEN

        try:
            stage_enum = SelfCorrectionStage(int(self_corr_stage_val))
        except Exception:
            stage_enum = SelfCorrectionStage.STAGE_1_IDENTIFY

        try:
            parsed_history = json.loads(history_json) if history_json else []
            if not isinstance(parsed_history, list):
                parsed_history = []
        except Exception:
            parsed_history = []

        try:
            c_at = float(created_at)
            if not math.isfinite(c_at):
                c_at = time.time()
        except Exception:
            c_at = time.time()

        lr_at = None
        if last_reviewed_at is not None:
            try:
                lr_val = float(last_reviewed_at)
                if math.isfinite(lr_val):
                    lr_at = lr_val
            except Exception:
                lr_at = None

        try:
            d_date = float(due_date)
            if not math.isfinite(d_date):
                d_date = time.time()
        except Exception:
            d_date = time.time()

        try:
            c_clean = int(consec_clean)
        except Exception:
            c_clean = 0

        return MistakeRecord(
            mistake_id=str(mistake_id),
            user_id=str(user_id),
            node_id=str(node_id),
            bug_id=str(bug_id),
            problem_statement=str(problem_statement),
            offending_step=str(offending_step),
            correct_principle=str(correct_principle),
            remediation_directive=str(remediation_directive),
            created_at=c_at,
            last_reviewed_at=lr_at,
            due_date=d_date,
            status=status_enum,
            dsr_state=dsr,
            self_correction_stage=stage_enum,
            consecutive_clean_solves=c_clean,
            history=parsed_history,
        )

    def _load_all_from_db(self) -> None:
        """Veritabanındaki tüm kayıtları önbelleğe yükler (bozuk kayıtları izole eder)."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM mistake_records")
        for row in cursor.fetchall():
            try:
                rec = self._row_to_record(row)
                self._records[rec.mistake_id] = rec
            except Exception:
                # Isolate corrupt records so the remaining valid vault items load without breaking
                continue

    def export_to_json(self, filepath: str) -> None:
        """Atomically writes all records to a JSON file using a .tmp file."""
        records_data = []
        with self._lock:
            for r in self._records.values():
                status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
                stage_val = (
                    r.self_correction_stage.value
                    if hasattr(r.self_correction_stage, "value")
                    else int(r.self_correction_stage)
                )
                records_data.append({
                    "mistake_id": r.mistake_id,
                    "user_id": r.user_id,
                    "node_id": r.node_id,
                    "bug_id": r.bug_id,
                    "problem_statement": r.problem_statement,
                    "offending_step": r.offending_step,
                    "correct_principle": r.correct_principle,
                    "remediation_directive": r.remediation_directive,
                    "created_at": r.created_at,
                    "last_reviewed_at": r.last_reviewed_at,
                    "due_date": r.due_date,
                    "status": status_str,
                    "stability": r.dsr_state.stability,
                    "difficulty": r.dsr_state.difficulty,
                    "retrievability": r.dsr_state.retrievability,
                    "repetitions": r.dsr_state.repetitions,
                    "lapses": r.dsr_state.lapses,
                    "self_correction_stage": stage_val,
                    "consecutive_clean_solves": r.consecutive_clean_solves,
                    "history": r.history,
                })

        tmp_path = filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(records_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, filepath)

    def import_from_json(self, filepath: str) -> int:
        """Imports records from JSON, isolating and skipping corrupt records."""
        if not os.path.exists(filepath):
            return 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return 0
        if not isinstance(data, list):
            return 0
        imported_count = 0
        for item in data:
            try:
                if not isinstance(item, dict):
                    continue
                try:
                    status_enum = MistakeStatus(item.get("status", "open"))
                except Exception:
                    status_enum = MistakeStatus.OPEN

                try:
                    stage_enum = SelfCorrectionStage(int(item.get("self_correction_stage", 1)))
                except Exception:
                    stage_enum = SelfCorrectionStage.STAGE_1_IDENTIFY

                dsr = DSRState(
                    stability=float(item.get("stability", 0.5)),
                    difficulty=float(item.get("difficulty", 5.0)),
                    retrievability=float(item.get("retrievability", 1.0)),
                    repetitions=int(item.get("repetitions", 0)),
                    lapses=int(item.get("lapses", 0)),
                )
                rec = MistakeRecord(
                    mistake_id=str(item.get("mistake_id", uuid.uuid4())),
                    user_id=str(item.get("user_id", "default_user")),
                    node_id=str(item.get("node_id", "N01")),
                    bug_id=str(item.get("bug_id", "BUG-UNKNOWN")),
                    problem_statement=str(item.get("problem_statement", "")),
                    offending_step=str(item.get("offending_step", "")),
                    correct_principle=str(item.get("correct_principle", "")),
                    remediation_directive=str(item.get("remediation_directive", "")),
                    created_at=float(item.get("created_at", time.time())),
                    last_reviewed_at=float(item["last_reviewed_at"]) if item.get("last_reviewed_at") is not None else None,
                    due_date=float(item.get("due_date", time.time())),
                    status=status_enum,
                    dsr_state=dsr,
                    self_correction_stage=stage_enum,
                    consecutive_clean_solves=int(item.get("consecutive_clean_solves", 0)),
                    history=item.get("history", []) if isinstance(item.get("history"), list) else [],
                )
                self._records[rec.mistake_id] = rec
                self._save_record_to_db(rec)
                imported_count += 1
            except Exception:
                # Isolate corrupt record
                continue
        return imported_count

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
        """Kavramsal bir hata yapıldığında kasaya yeni bir otopsi dosyası açar ve SQLite'a yazar."""
        curr_time = float(timestamp) if (timestamp is not None and math.isfinite(timestamp)) else time.time()
        init_dsr = self.fsrs.init_dsr(Rating.AGAIN)
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
        with self._lock:
            self._records[record.mistake_id] = record
        self._save_record_to_db(record)
        return record

    def get_mistake(self, mistake_id: str) -> Optional[MistakeRecord]:
        with self._lock:
            return self._records.get(mistake_id)

    def list_mistakes(
        self,
        user_id: str,
        status: Optional[MistakeStatus] = None,
    ) -> List[MistakeRecord]:
        """Kullanıcının kayıtlı hatalarını filtreli listeler."""
        with self._lock:
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
        with self._lock:
            due = [
                r for r in self._records.values()
                if r.user_id == user_id
                and r.status != MistakeStatus.CURED
                and r.due_date <= curr_time
            ]
            return sorted(due, key=lambda x: x.due_date)

    def update_record(self, record: MistakeRecord) -> None:
        """Kayıt kartını günceller ve SQLite'a yazar."""
        with self._lock:
            self._records[record.mistake_id] = record
        self._save_record_to_db(record)

    def delete_mistake(self, mistake_id: str) -> bool:
        """Hata kaydını hem bellekten hem SQLite veritabanından siler."""
        with self._lock:
            if mistake_id in self._records:
                del self._records[mistake_id]
                cursor = self._conn.cursor()
                cursor.execute("DELETE FROM mistake_records WHERE mistake_id = ?", (mistake_id,))
                self._conn.commit()
                return True
            return False

    def query_sql(self, query: str, params: tuple = ()) -> List[tuple]:
        """Doğrudan SQLite SQL sorgusu çalıştırır."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def close(self) -> None:
        """Veritabanı bağlantısını kapatır."""
        with self._lock:
            if self._conn:
                self._conn.close()

    def get_vault_analytics(self, user_id: str) -> Dict[str, Any]:
        """Kasa analitiği: Açık, telafide, kür edilmiş oranları ve en sık yapılan yanılgılar."""
        with self._lock:
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

    def get_misconception_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Öğrencinin kavramsal yanılgı profilini hiyerarşik ağaç yapısında,
        zaaf derecesi ve FSRS kalıcılık durumu ile birlikte döner.
        """
        # Standart pedagojik kategoriler ve metadata haritası
        KNOWN_CATEGORIES = [
            {"id": "KUADRATIK_DENKLEMLER", "title": "Kuadratik Denklemler"},
            {"id": "ISARET_VE_DAGILMA", "title": "İşaret ve Parantez Dağılımı"},
            {"id": "PARABOL_VE_POLINOM", "title": "Parabol ve Polinomlar"},
            {"id": "TRIGONOMETRI_VE_LOGARITMA", "title": "Trigonometri ve Logaritma"},
            {"id": "ANALIZ_TUREV_INTEGRAL", "title": "Analiz (Türev & İntegral)"},
            {"id": "GENEL_CEBIR", "title": "Genel Cebirsel İlkeler"},
        ]

        BUG_METADATA: Dict[str, Dict[str, str]] = {
            "BUG-QUAD-01": {
                "title": "Sıfır-Çarpım Kuralı İhlali",
                "category_id": "KUADRATIK_DENKLEMLER",
                "cognitive_cause": "Eşitliğin sağ tarafı sıfırdan farklı iken çarpanları doğrudan sayıya eşitleme.",
            },
            "BUG-QUAD-02": {
                "title": "Negatif İkiz Kök İhmali",
                "category_id": "KUADRATIK_DENKLEMLER",
                "cognitive_cause": "x² = c eşitliğinde sadece pozitif karekökü alıp negatif ikiz kökü unutma.",
            },
            "BUG-QUAD-03": {
                "title": "Binom Karesi Açılım Hatası",
                "category_id": "ISARET_VE_DAGILMA",
                "cognitive_cause": "(x+a)² açılımında orta terimi (2ax) atlayıp x²+a² yazma.",
            },
            "BUG-QUAD-04": {
                "title": "Tam Kare Denge Hatası",
                "category_id": "KUADRATIK_DENKLEMLER",
                "cognitive_cause": "Eşitliğin bir tarafına eklenen terimi diğer tarafa eklemeyip dengeyi bozma.",
            },
            "BUG-QUAD-05": {
                "title": "Formül Payda Hatası",
                "category_id": "KUADRATIK_DENKLEMLER",
                "cognitive_cause": "Kuadratik formülde paydadaki 2a katsayısı yerine 2 yazma.",
            },
            "SIGN_FLIP": {
                "title": "Eksi İşareti Dağıtım Yanılgısı",
                "category_id": "ISARET_VE_DAGILMA",
                "cognitive_cause": "Parantez önündeki eksi işaretini içteki tüm terimlere dağıtmama.",
            },
            "EXPONENT_DISTRIBUTION": {
                "title": "Üslerin Toplam Üzerine Hatalı Dağıtımı",
                "category_id": "GENEL_CEBIR",
                "cognitive_cause": "Çarpma kuralını toplama işlemine hatalı genelleştirme.",
            },
        }

        def _resolve_category(bug_id: str) -> tuple[str, str]:
            if bug_id in BUG_METADATA:
                cat_id = BUG_METADATA[bug_id]["category_id"]
                cat_title = next((c["title"] for c in KNOWN_CATEGORIES if c["id"] == cat_id), "Genel Cebir")
                return cat_id, cat_title
            b = bug_id.upper()
            if b.startswith("BUG-QUAD-"):
                return "KUADRATIK_DENKLEMLER", "Kuadratik Denklemler"
            if b.startswith("SIGN") or b.startswith("BUG-FOUND-") or "SIGN" in b:
                return "ISARET_VE_DAGILMA", "İşaret ve Parantez Dağılımı"
            if b.startswith("BUG-PARAB-") or b.startswith("BUG-POLY-"):
                return "PARABOL_VE_POLINOM", "Parabol ve Polinomlar"
            if b.startswith("BUG-TRIG-") or b.startswith("BUG-LOG-"):
                return "TRIGONOMETRI_VE_LOGARITMA", "Trigonometri ve Logaritma"
            if b.startswith("BUG-CALC-") or b.startswith("BUG-INT-"):
                return "ANALIZ_TUREV_INTEGRAL", "Analiz (Türev & İntegral)"
            return "GENEL_CEBIR", "Genel Cebirsel İlkeler"

        with self._lock:
            user_records = [r for r in self._records.values() if r.user_id == user_id]
            total_mistakes = len(user_records)
            cured_count = sum(1 for r in user_records if r.status == MistakeStatus.CURED)
            cure_rate = round(cured_count / max(1, total_mistakes), 3) if total_mistakes > 0 else 0.0

            # Grup: bug_id -> List[MistakeRecord]
            grouped_by_bug: Dict[str, List[MistakeRecord]] = {}
            for r in user_records:
                grouped_by_bug.setdefault(r.bug_id, []).append(r)

            # Her bug için düğüm verisi hazırla
            nodes_by_category: Dict[str, List[Dict[str, Any]]] = {}
            all_bug_summaries: List[Dict[str, Any]] = []

            for bug_id, records in grouped_by_bug.items():
                cat_id, cat_title = _resolve_category(bug_id)
                freq = len(records)
                open_cnt = sum(1 for r in records if r.status == MistakeStatus.OPEN)
                remed_cnt = sum(1 for r in records if r.status == MistakeStatus.IN_REMEDIATION)
                cur_cnt = sum(1 for r in records if r.status == MistakeStatus.CURED)

                if cur_cnt == freq and cur_cnt > 0:
                    status_str = "cured"
                elif open_cnt >= 2:
                    status_str = "critical"
                elif open_cnt == 1:
                    status_str = "warning"
                elif remed_cnt > 0:
                    status_str = "in_remediation"
                else:
                    status_str = "clean"

                latest_rec = max(records, key=lambda x: x.created_at)
                meta = BUG_METADATA.get(bug_id, {})
                title = meta.get("title", f"Yanılgı: {bug_id}")
                cause = meta.get("cognitive_cause", latest_rec.correct_principle or "Kavramsal kural ihlali.")
                avg_stab = round(sum(r.dsr_state.stability for r in records) / freq, 2)

                node_dict = {
                    "bug_id": bug_id,
                    "title": title,
                    "category_id": cat_id,
                    "category_title": cat_title,
                    "cognitive_cause": cause,
                    "remediation_directive": latest_rec.remediation_directive,
                    "correct_principle": latest_rec.correct_principle,
                    "frequency": freq,
                    "open_count": open_cnt,
                    "in_remediation_count": remed_cnt,
                    "cured_count": cur_cnt,
                    "status": status_str,
                    "last_offending_step": latest_rec.offending_step,
                    "last_problem": latest_rec.problem_statement,
                    "avg_stability_days": avg_stab,
                }
                nodes_by_category.setdefault(cat_id, []).append(node_dict)
                all_bug_summaries.append(node_dict)

            # Top 3 tekrarlayan tuzak (önce açık sayısı, sonra toplam frekans)
            top_traps = sorted(
                all_bug_summaries,
                key=lambda x: (x["open_count"], x["frequency"]),
                reverse=True,
            )[:3]

            # Kategorileri oluştur
            categories_list: List[Dict[str, Any]] = []
            for cat in KNOWN_CATEGORIES:
                cat_id = cat["id"]
                c_nodes = nodes_by_category.get(cat_id, [])
                cat_total = sum(n["frequency"] for n in c_nodes)
                cat_active = sum(n["open_count"] + n["in_remediation_count"] for n in c_nodes)
                cat_cured = sum(n["cured_count"] for n in c_nodes)

                categories_list.append({
                    "category_id": cat_id,
                    "category_title": cat["title"],
                    "total_mistakes": cat_total,
                    "active_mistakes": cat_active,
                    "cured_mistakes": cat_cured,
                    "nodes": sorted(c_nodes, key=lambda x: (x["status"] == "critical", x["open_count"]), reverse=True),
                })

            return {
                "user_id": user_id,
                "total_recorded_mistakes": total_mistakes,
                "total_cured": cured_count,
                "overall_cure_rate": cure_rate,
                "top_recurring_traps": top_traps,
                "categories": categories_list,
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

        now = float(current_time) if (current_time is not None and math.isfinite(current_time)) else time.time()
        raw_elapsed = (now - (record.last_reviewed_at or record.created_at)) / 86400.0
        elapsed_days = max(0.0, raw_elapsed) if math.isfinite(raw_elapsed) else 0.0

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
