import pytest
from app.cas.source_unpacker_service import SourceUnpackerService, SourceOrigin


def test_unpack_division_origin():
    origin = SourceUnpackerService.unpack_token(
        current_step="x = 4",
        previous_step="2x = 8",
        token="4",
    )
    assert origin is not None
    assert origin.operation == "DIVISION"
    assert origin.operand_left == "8"
    assert origin.operand_right == "2"
    assert origin.origin_formula == "8 ÷ 2"
    assert "8 sayısı 2'ye bölünerek 4 elde edildi" in origin.explanation


def test_unpack_subtraction_origin():
    origin = SourceUnpackerService.unpack_token(
        current_step="2x = 8",
        previous_step="2x + 6 = 14",
        token="8",
    )
    assert origin is not None
    assert origin.operation == "SUBTRACTION"
    assert origin.operand_left == "14"
    assert origin.operand_right == "6"
    assert origin.origin_formula == "14 - 6"
    assert "6 karşıya eksi geçerek" in origin.explanation


def test_unpack_addition_origin():
    origin = SourceUnpackerService.unpack_token(
        current_step="x = 14",
        previous_step="x - 4 = 10",
        token="14",
    )
    assert origin is not None
    assert origin.operation == "ADDITION"
    assert origin.operand_left == "10"
    assert origin.operand_right == "4"
    assert origin.origin_formula == "10 + 4"
    assert "4 karşıya artı geçerek" in origin.explanation


def test_unpack_parenthesis_expansion():
    origin = SourceUnpackerService.unpack_token(
        current_step="3x + 12 = 18",
        previous_step="3(x + 4) = 18",
        token="12",
    )
    assert origin is not None
    assert origin.operation == "MULTIPLICATION"
    assert origin.operand_left == "3"
    assert origin.operand_right == "4"
    assert origin.origin_formula == "3 × 4"
    assert "Dıştaki 3 çarpanı parantez içindeki 4 ile çarpılarak 12 oldu" in origin.explanation


def test_unpack_generic_fallback_and_empty():
    # Empty token check
    assert SourceUnpackerService.unpack_token("", "2x = 8", "") is None

    # Generic fallback
    origin = SourceUnpackerService.unpack_token(
        current_step="y = 2",
        previous_step="y^2 = 4",
        token="y",
    )
    assert origin is not None
    assert origin.operation == "STEP_DERIVATION"
    assert origin.target_token == "y"
