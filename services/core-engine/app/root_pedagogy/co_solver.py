from typing import Dict, List, Optional, Any
import sympy as sp
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.root_pedagogy.models import (
    SubgoalStep,
    CoSolveRequest,
    CoSolveResponse,
)


class ActiveCoSolverEngine:
    """
    Aktif Birlikte Çözme Motoru (Active Co-Solver Engine).
    Faded Worked Examples & Subgoal Labeling ilkelerine göre çalışır.
    Öğrenciye asla pasif video veya çözüm metni sunmaz;
    soruyu mikro alt hedeflere böler ve her adımı öğrencinin kendisine yazdırır.
    """

    def __init__(self, cas_engine: Optional[SymbolicEquivalenceEngine] = None):
        self.cas = cas_engine or SymbolicEquivalenceEngine()
        self.preset_subgoals: Dict[str, List[SubgoalStep]] = self._init_subgoals()

    def _init_subgoals(self) -> Dict[str, List[SubgoalStep]]:
        """Standart soru tipleri için 3 aşamalı mikro alt hedefler."""
        return {
            "DEMO_LINEAR": [
                SubgoalStep(
                    subgoal_id="SG_LIN_01",
                    order=1,
                    title="Girdiyi Tespit Et",
                    prompt="2x + 6 = 14 denkleminde x'i yalnız bırakmak için ilk olarak hangi sabit sayıyı karşıya geçirmeliyiz?",
                    expected_answer_str="6",
                    socratic_hint="x'li terimin yanındaki +6 sayısını karşıya taşımalıyız.",
                    explanation="+6 sayısı karşıya -6 olarak geçer.",
                ),
                SubgoalStep(
                    subgoal_id="SG_LIN_02",
                    order=2,
                    title="Kuralı Uygula",
                    prompt="6 sayısını karşı taraftan (14) çıkardığında sağ tarafta hangi sayı kalır?",
                    expected_answer_str="8",
                    socratic_hint="14 - 6 işlemini yap.",
                    explanation="14 - 6 = 8 olur; denklem 2x = 8 haline gelir.",
                ),
                SubgoalStep(
                    subgoal_id="SG_LIN_03",
                    order=3,
                    title="Sadeleştir",
                    prompt="2x = 8 denkleminde x'in katsayısı olan 2'ye böldüğünde x kaç bulunur?",
                    expected_answer_str="4",
                    socratic_hint="8 / 2 işlemini yap.",
                    explanation="x = 4 olarak bulunur.",
                ),
            ],
            "DEMO_DISTRIB": [
                SubgoalStep(
                    subgoal_id="SG_DIST_01",
                    order=1,
                    title="Girdiyi Tespit Et",
                    prompt="3(x + 4) ifadesinde parantez dışındaki çarpan nedir?",
                    expected_answer_str="3",
                    socratic_hint="Parantezin hemen önündeki katsayıya bak.",
                    explanation="Dıştaki çarpan 3'tür.",
                ),
                SubgoalStep(
                    subgoal_id="SG_DIST_02",
                    order=2,
                    title="Kuralı Uygula",
                    prompt="3 çarpanını parantez içindeki x ile çarptığında elde edilen terim nedir?",
                    expected_answer_str="3x",
                    socratic_hint="3 ile x'i çarp.",
                    explanation="3 · x = 3x olur.",
                ),
                SubgoalStep(
                    subgoal_id="SG_DIST_03",
                    order=3,
                    title="Sadeleştir",
                    prompt="3 çarpanını parantez içindeki +4 ile çarptığında elde edilen sabit sayı nedir?",
                    expected_answer_str="12",
                    socratic_hint="3 · 4 çarpımını yap.",
                    explanation="Sonuç 3x + 12 olarak tamamlanır.",
                ),
            ],
        }

    def process_subgoal_step(self, request: CoSolveRequest) -> CoSolveResponse:
        # İlgili subgoal'ü bul
        active_sg: Optional[SubgoalStep] = None
        current_list: List[SubgoalStep] = []
        for sg_list in self.preset_subgoals.values():
            for sg in sg_list:
                if sg.subgoal_id == request.subgoal_id:
                    active_sg = sg
                    current_list = sg_list
                    break
            if active_sg:
                break

        if not active_sg:
            return CoSolveResponse(
                session_id=request.session_id,
                subgoal_id=request.subgoal_id,
                is_valid=False,
                subgoal_completed=False,
                feedback="Alt hedef (subgoal) bulunamadı.",
            )

        clean_input = request.student_answer.strip().lower().replace(" ", "")
        expected = active_sg.expected_answer_str.strip().lower().replace(" ", "")

        is_valid = (clean_input == expected) or (f"x={expected}" in clean_input) or (f"={expected}" in clean_input)

        # Akıllı Tereddüt Sensörü: 8 saniyeden uzun hareketsizlik varsa odaklama fısıltısı
        whisper = None
        if request.elapsed_seconds >= 8.0:
            whisper = f"Fısıltı: {active_sg.socratic_hint}"

        # "Nereden Geldi Bu?" Kaynak açıcı verisi
        source_data = {
            "subgoal_id": active_sg.subgoal_id,
            "origin_expression": active_sg.explanation,
            "highlight_tokens": [active_sg.expected_answer_str],
        }

        if is_valid:
            # Bir sonraki alt hedefi bul
            next_idx = active_sg.order
            next_sg = current_list[next_idx] if next_idx < len(current_list) else None
            all_done = (next_sg is None)

            return CoSolveResponse(
                session_id=request.session_id,
                subgoal_id=active_sg.subgoal_id,
                is_valid=True,
                subgoal_completed=True,
                feedback=f"Harika! {active_sg.explanation}",
                next_subgoal=next_sg,
                all_completed=all_done,
                hesitation_whisper=whisper,
                source_unpacker_data=source_data,
            )
        else:
            return CoSolveResponse(
                session_id=request.session_id,
                subgoal_id=active_sg.subgoal_id,
                is_valid=False,
                subgoal_completed=False,
                feedback=f"Tekrar düşün: {active_sg.socratic_hint}",
                next_subgoal=active_sg,
                all_completed=False,
                hesitation_whisper=whisper,
                source_unpacker_data=source_data,
            )
