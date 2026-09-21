import time
import uuid
from typing import Dict, List, Optional
from app.root_pedagogy.models import WeaknessEntry, WeaknessSeverity
from app.root_pedagogy.root_dag import RootPrerequisiteDAG


class CognitiveWeaknessLedger:
    """
    Bilişsel Zaaf Defteri (Cognitive Weakness Ledger).
    Öğrencinin adımlarındaki hataları sınıflandırır:
    - SLIP (Basit İşlem Hatası)
    - MISCONCEPTION (Lise Kavram Yanılgısı)
    - ROOT_DEFICIT (Seviye -3..-1 Kök Önkoşul Delikleri)
    Kök delikleri tespit edildiğinde BKT ustalık cezası uygular ve kum havuzunu tetikler.
    """

    def __init__(self, root_dag: Optional[RootPrerequisiteDAG] = None):
        self.root_dag = root_dag or RootPrerequisiteDAG()
        self.ledger: Dict[str, List[WeaknessEntry]] = {}  # student_id -> entries

    def log_error(
        self,
        student_id: str,
        node_id: str,
        user_step: str,
        detected_bug_id: Optional[str] = None,
        elapsed_seconds: float = 0.0,
    ) -> WeaknessEntry:
        """Hatanın seviyesini tespit edip zaaf defterine kaydeder."""
        severity = WeaknessSeverity.SLIP

        # 1. Kök Yanılgı mı? (BUG-FOUND-01..15)
        if detected_bug_id and detected_bug_id.startswith("BUG-FOUND-"):
            severity = WeaknessSeverity.ROOT_DEFICIT
        # 2. Lise Kavram Yanılgısı mı? (BUG-QUAD, BUG-TRIG, BUG-PROB, vb.)
        elif detected_bug_id and (
            detected_bug_id.startswith("BUG-QUAD-")
            or detected_bug_id.startswith("BUG-PARAB-")
            or detected_bug_id.startswith("BUG-POLY-")
            or detected_bug_id.startswith("BUG-TRIG-")
            or detected_bug_id.startswith("BUG-LOG-")
            or detected_bug_id.startswith("BUG-CALC-")
            or detected_bug_id.startswith("BUG-INT-")
            or detected_bug_id.startswith("BUG-PROB-")
        ):
            severity = WeaknessSeverity.MISCONCEPTION
        else:
            # İşlem hatası: kısa sürede rastgele hatalı girdi
            severity = WeaknessSeverity.SLIP

        entry = WeaknessEntry(
            id=str(uuid.uuid4())[:8],
            student_id=student_id,
            node_id=node_id,
            bug_id=detected_bug_id,
            severity=severity,
            context_step=user_step,
            timestamp=str(int(time.time())),
            p_l_penalty=0.25 if severity == WeaknessSeverity.ROOT_DEFICIT else (0.15 if severity == WeaknessSeverity.MISCONCEPTION else 0.05),
        )

        if student_id not in self.ledger:
            self.ledger[student_id] = []
        elif len(self.ledger[student_id]) >= 500:
            self.ledger[student_id].pop(0)
        self.ledger[student_id].append(entry)
        return entry

    def get_student_weaknesses(self, student_id: str) -> List[WeaknessEntry]:
        return self.ledger.get(student_id, [])

    def should_trigger_sandbox(self, student_id: str, bug_id: Optional[str]) -> bool:
        """Kök açıklarında veya tekrarlayan hatalarda kum havuzunu aç."""
        if not bug_id:
            return False
        if bug_id.startswith("BUG-FOUND-"):
            return True
        # Aynı bug_id öğrencinin geçmişinde 2'den fazla var mı?
        history = self.ledger.get(student_id, [])
        matches = [e for e in history if e.bug_id == bug_id]
        return len(matches) >= 2
