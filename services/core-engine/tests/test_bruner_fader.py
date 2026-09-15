import pytest
from app.root_pedagogy.bruner_fader import BrunerFadingOrchestrator, BrunerStage


def test_determine_stage_low_mastery_is_enactive():
    stage = BrunerFadingOrchestrator.determine_stage(bkt_mastery_p_l=0.25)
    assert stage == BrunerStage.ENACTIVE


def test_determine_stage_medium_mastery_is_iconic():
    stage = BrunerFadingOrchestrator.determine_stage(bkt_mastery_p_l=0.55)
    assert stage == BrunerStage.ICONIC


def test_determine_stage_high_mastery_is_symbolic():
    stage = BrunerFadingOrchestrator.determine_stage(bkt_mastery_p_l=0.85)
    assert stage == BrunerStage.SYMBOLIC


def test_determine_stage_friction_falls_back_to_enactive():
    # Even if mastery is high, 2 consecutive errors causes fallback to Enactive manipulatives
    stage = BrunerFadingOrchestrator.determine_stage(bkt_mastery_p_l=0.90, consecutive_errors=2)
    assert stage == BrunerStage.ENACTIVE


def test_get_representation_returns_concrete_materials():
    rep = BrunerFadingOrchestrator.get_representation("N15", BrunerStage.ENACTIVE)
    assert rep.stage == BrunerStage.ENACTIVE
    assert rep.material_type == "BALANCE_SCALE"
    assert rep.scaffold_level == 1.0


def test_progress_and_regress_stages():
    s1 = BrunerFadingOrchestrator.progress_stage(BrunerStage.ENACTIVE)
    assert s1 == BrunerStage.ICONIC

    s2 = BrunerFadingOrchestrator.progress_stage(BrunerStage.ICONIC)
    assert s2 == BrunerStage.SYMBOLIC

    back = BrunerFadingOrchestrator.regress_stage(BrunerStage.SYMBOLIC)
    assert back == BrunerStage.ICONIC
