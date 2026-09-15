"""
Bruner E-I-S (Enactive - Iconic - Symbolic) Concreteness Fading Orchestrator.
Bölüm 1 - Bilişsel Öğretim Manifestosu.
Controls the fading of concrete representations into pure symbolic algebra.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BrunerStage(str, Enum):
    ENACTIVE = "ENACTIVE"  # Dokunsal / Eylemsel: Sayı doğrusu, terazi kefesi, karo birleştirme
    ICONIC = "ICONIC"      # İkonik / Şematik: Kutu modelleri, yönlü oklar, alan taslakları
    SYMBOLIC = "SYMBOLIC"  # Sembolik: Saf cebirsel notasyon (2x + 3 = 11)


class BrunerRepresentation(BaseModel):
    stage: BrunerStage
    node_id: str
    material_type: str
    visual_cue: str
    scaffold_level: float = Field(..., ge=0.0, le=1.0)
    allowed_input_modes: List[str]
    description: str


class BrunerFadingOrchestrator:
    """
    Manages the transition of learners through Bruner's E-I-S stages.
    Enactive -> Iconic -> Symbolic.
    Automatically provides scaffolding fallback if student struggles.
    """

    DEFAULT_REPRESENTATIONS: Dict[str, Dict[BrunerStage, BrunerRepresentation]] = {
        "N15": {
            BrunerStage.ENACTIVE: BrunerRepresentation(
                stage=BrunerStage.ENACTIVE,
                node_id="N15",
                material_type="BALANCE_SCALE",
                visual_cue="Terazi kefesi: Sol kefedeki kutulardan ve ağırlıklardan sağ kefeye dengeleme yap.",
                scaffold_level=1.0,
                allowed_input_modes=["touchpad", "inkingCanvas"],
                description="Eylemsel Terazi Modeli ile denklem sezgisi.",
            ),
            BrunerStage.ICONIC: BrunerRepresentation(
                stage=BrunerStage.ICONIC,
                node_id="N15",
                material_type="BOX_DIAGRAM",
                visual_cue="Kutu şeması: [2x] + [6] = [14] bloklarını sadeleştir.",
                scaffold_level=0.5,
                allowed_input_modes=["touchpad", "virtualKeyboard", "inkingCanvas"],
                description="İkonik kutu ve blok diyagramı ile terim gruplama.",
            ),
            BrunerStage.SYMBOLIC: BrunerRepresentation(
                stage=BrunerStage.SYMBOLIC,
                node_id="N15",
                material_type="PURE_SYMBOLIC",
                visual_cue="2x + 6 = 14",
                scaffold_level=0.0,
                allowed_input_modes=["touchpad", "virtualKeyboard"],
                description="Saf cebirsel denklem çözümü.",
            ),
        },
        "N_ROOT_02": {
            BrunerStage.ENACTIVE: BrunerRepresentation(
                stage=BrunerStage.ENACTIVE,
                node_id="N_ROOT_02",
                material_type="NUMBER_LINE_WALKER",
                visual_cue="Sayı doğrusunda sola yürü: -6 noktasından 5 adım daha sola git.",
                scaffold_level=1.0,
                allowed_input_modes=["touchpad", "inkingCanvas"],
                description="Sayı doğrusunda borç ve yön yürüme modeli.",
            ),
            BrunerStage.ICONIC: BrunerRepresentation(
                stage=BrunerStage.ICONIC,
                node_id="N_ROOT_02",
                material_type="ARROW_VECTOR",
                visual_cue="<-(-6) ve <-(-5) okları toplam borcu gösterir.",
                scaffold_level=0.5,
                allowed_input_modes=["touchpad", "inkingCanvas"],
                description="Yönlü oklar ile borcun büyümesi.",
            ),
            BrunerStage.SYMBOLIC: BrunerRepresentation(
                stage=BrunerStage.SYMBOLIC,
                node_id="N_ROOT_02",
                material_type="PURE_SYMBOLIC",
                visual_cue="-6 - 5 = -11",
                scaffold_level=0.0,
                allowed_input_modes=["touchpad", "virtualKeyboard"],
                description="Saf negatif toplama notasyonu.",
            ),
        },
    }

    @classmethod
    def determine_stage(
        cls,
        bkt_mastery_p_l: float,
        consecutive_errors: int = 0,
        current_stage: Optional[BrunerStage] = None,
    ) -> BrunerStage:
        """
        Determines the optimal Bruner stage based on BKT mastery and friction indicators.
        """
        # Friction fallback: 2 or more consecutive errors triggers scaffold fallback to Enactive
        if consecutive_errors >= 2:
            return BrunerStage.ENACTIVE

        # Low mastery: concrete manipulatives
        if bkt_mastery_p_l < 0.40:
            return BrunerStage.ENACTIVE

        # Intermediate mastery: iconic diagrams
        if bkt_mastery_p_l < 0.75:
            return BrunerStage.ICONIC

        # High mastery (>= 0.75): full symbolic fluency
        return BrunerStage.SYMBOLIC

    @classmethod
    def get_representation(cls, node_id: str, stage: BrunerStage) -> BrunerRepresentation:
        if node_id in cls.DEFAULT_REPRESENTATIONS:
            stage_map = cls.DEFAULT_REPRESENTATIONS[node_id]
            if stage in stage_map:
                return stage_map[stage]

        # Generic fallback
        return BrunerRepresentation(
            stage=stage,
            node_id=node_id,
            material_type="GENERIC_" + stage.value,
            visual_cue=f"Düğüm {node_id} için {stage.value} görsel modeli.",
            scaffold_level=1.0 if stage == BrunerStage.ENACTIVE else (0.5 if stage == BrunerStage.ICONIC else 0.0),
            allowed_input_modes=["touchpad", "virtualKeyboard", "inkingCanvas"],
            description=f"Otomatik üretilmiş {stage.value} modeli.",
        )

    @classmethod
    def progress_stage(cls, current_stage: BrunerStage) -> BrunerStage:
        if current_stage == BrunerStage.ENACTIVE:
            return BrunerStage.ICONIC
        return BrunerStage.SYMBOLIC

    @classmethod
    def regress_stage(cls, current_stage: BrunerStage) -> BrunerStage:
        if current_stage == BrunerStage.SYMBOLIC:
            return BrunerStage.ICONIC
        return BrunerStage.ENACTIVE
