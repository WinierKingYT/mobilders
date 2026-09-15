import pytest
from app.root_pedagogy.micro_triumph_engine import MicroTriumphEngine, MicroVariant, MicroTriumphResult


def test_micro_variant_generation_division():
    engine = MicroTriumphEngine()
    variant = engine.generate_micro_variant("2x = 8", rule_id="RULE_DIV")
    assert variant.original_rule == "RULE_DIV"
    assert variant.is_unassisted is True
    assert "x" in variant.target_expression
    # Coeff should be 3, ans should be 5, rhs should be 15
    assert variant.expected_answer == "5"
    assert variant.target_expression == "3x = 15"


def test_micro_variant_generation_addition():
    engine = MicroTriumphEngine()
    variant = engine.generate_micro_variant("x + 5 = 12", rule_id="RULE_ADD")
    assert variant.is_unassisted is True
    # new_c = 7, new_rhs = 15, expected = 8
    assert variant.target_expression == "x + 7 = 15"
    assert variant.expected_answer == "8"


def test_micro_triumph_evaluation_correct():
    engine = MicroTriumphEngine()
    variant = engine.generate_micro_variant("2x = 8")
    result = engine.evaluate_micro_triumph("5", variant)
    assert result.is_triumph is True
    assert result.dopamine_pulse is True
    assert result.confidence_bonus == 0.15
    assert "Harikasın" in result.feedback_message


def test_micro_triumph_evaluation_cas_equivalence():
    engine = MicroTriumphEngine()
    variant = MicroVariant(
        variant_id="mv_test",
        original_rule="RULE_TEST",
        prompt="Test",
        target_expression="x = 4/2",
        expected_answer="2",
    )
    # Student enters 4/2 instead of 2
    result = engine.evaluate_micro_triumph("4/2", variant)
    assert result.is_triumph is True
    assert result.dopamine_pulse is True
    assert result.confidence_bonus == 0.15


def test_micro_triumph_evaluation_incorrect():
    engine = MicroTriumphEngine()
    variant = engine.generate_micro_variant("2x = 8")
    result = engine.evaluate_micro_triumph("99", variant)
    assert result.is_triumph is False
    assert result.dopamine_pulse is False
    assert result.confidence_bonus == 0.0
    assert "Yaklaştın" in result.feedback_message
