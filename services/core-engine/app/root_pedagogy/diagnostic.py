from typing import Dict, List
from app.root_pedagogy.models import (
    ZeroBaselineDiagnosticQuestion,
    ZeroBaselineEvaluationRequest,
    ZeroBaselineEvaluationResponse,
)


class ZeroBaselineDiagnostic:
    """
    Sıfır Tabanlı Bilişsel Sezgi Testi (Zero-Baseline Diagnostic).
    Uygulamaya ilk giren öğrencinin 3 soruda temel aritmetik ve cebirsel sezgisini ölçer;
    gerekirse doğrudan Seviye -3 kök patikadan başlatır.
    """

    def __init__(self):
        self.questions: Dict[str, ZeroBaselineDiagnosticQuestion] = {
            "Q_ROOT_01": ZeroBaselineDiagnosticQuestion(
                question_id="Q_ROOT_01",
                node_id="N_ROOT_02",
                question_text="-6 - 5 işleminin sonucu kaçtır?",
                options=["-1", "1", "-11", "11"],
                correct_index=2,
                concept_tested="Borç / Alacak ve Negatif Sayılarda Toplama",
            ),
            "Q_ROOT_02": ZeroBaselineDiagnosticQuestion(
                question_id="Q_ROOT_02",
                node_id="N_ROOT_08",
                question_text="3 + 4 · 2 işleminin sonucu kaçtır?",
                options=["14", "11", "24", "9"],
                correct_index=1,
                concept_tested="Çarpmanın İşlem Önceliği (PEMDAS)",
            ),
            "Q_ROOT_03": ZeroBaselineDiagnosticQuestion(
                question_id="Q_ROOT_03",
                node_id="N_ROOT_15",
                question_text="2x + 3 = 11 denkleminde terazi dengesini sağlayan x kaçtır?",
                options=["7", "4", "8", "2"],
                correct_index=1,
                concept_tested="Bilinmeyen Kutu ve Terazi Dengesi",
            ),
        }

    def evaluate(self, request: ZeroBaselineEvaluationRequest) -> ZeroBaselineEvaluationResponse:
        correct_count = 0
        diagnoses = []
        failed_nodes = []

        for q_id, q in self.questions.items():
            chosen = request.answers.get(q_id)
            if chosen == q.correct_index:
                correct_count += 1
            else:
                failed_nodes.append(q.node_id)
                diagnoses.append(f"{q.concept_tested} konusunda kök önkoşul eksikliği tespit edildi.")

        score_ratio = correct_count / len(self.questions)
        needs_root = score_ratio < 1.0

        if score_ratio == 0.0 or "N_ROOT_02" in failed_nodes:
            rec_node = "N_ROOT_01"  # En temel sayı doğrusu
        elif "N_ROOT_08" in failed_nodes:
            rec_node = "N_ROOT_08"  # PEMDAS önceliği
        elif "N_ROOT_15" in failed_nodes:
            rec_node = "N_ROOT_13"  # Bilinmeyen kutusu
        else:
            rec_node = "N01"

        return ZeroBaselineEvaluationResponse(
            student_id=request.student_id,
            needs_root_pathway=needs_root,
            recommended_starting_node=rec_node,
            score_ratio=score_ratio,
            diagnoses=diagnoses if diagnoses else ["Tüm temel aritmetik ve cebir sezgileri tam."],
        )
