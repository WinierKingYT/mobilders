import pytest
from app.socratic.socratic_method_scaffold import (
    SocraticMethodScaffold,
    SocraticStage,
    SOCRATIC_TEMPLATES,
)
from app.socratic.guardrail import ZeroLeakageGuardrail


@pytest.fixture
def scaffold():
    return SocraticMethodScaffold()


# =====================================================================
# 1. 10 Core Socratic Templates Selection Tests
# =====================================================================

def test_select_template_inequality(scaffold):
    t = scaffold.select_template("-2x < 10")
    assert t.template_id == "INEQUALITY_NEGATIVE_DIV"
    assert "yön" in t.expected_keywords or "ters" in t.expected_keywords


def test_select_template_distributive(scaffold):
    t = scaffold.select_template("2x - (x - 4) = 12")
    assert t.template_id == "DISTRIBUTIVE_NEGATIVE_SIGN"
    assert "artı" in t.expected_keywords or "+4" in t.expected_keywords


def test_select_template_fraction(scaffold):
    t = scaffold.select_template("x/2 + x/3 = 5")
    assert t.template_id == "FRACTION_COMMON_DENOMINATOR"
    assert "payda" in t.expected_keywords


def test_select_template_factoring(scaffold):
    t = scaffold.select_template("x^2 - 16 = 0")
    assert t.template_id == "FACTORING_DIFFERENCE_OF_SQUARES"


def test_select_template_constant_transfer(scaffold):
    t = scaffold.select_template("2x + 6 = 14")
    assert t.template_id == "EQUATION_CONSTANT_TRANSFER"
    assert "eksi" in t.expected_keywords or "ters" in t.expected_keywords


def test_select_template_absolute_value(scaffold):
    t = scaffold.select_template("|x - 2| = 5")
    assert t.template_id == "ABSOLUTE_VALUE_SPLIT"


def test_select_template_exponent_negative(scaffold):
    t = scaffold.select_template("x^-3 = 8")
    assert t.template_id == "EXPONENT_NEGATIVE_POWER"
    assert "1/x^2" in t.expected_keywords or "payda" in t.expected_keywords


def test_select_template_logarithm(scaffold):
    t = scaffold.select_template("log_2(x - 1) = 3")
    assert t.template_id == "LOGARITHM_BASE_DOMAIN"
    assert "pozitif" in t.expected_keywords


def test_select_template_trigonometry(scaffold):
    t = scaffold.select_template("sin^2(x) + cos^2(x) = 1")
    assert t.template_id == "TRIGONOMETRIC_PYTHAGOREAN"
    assert "1" in t.expected_keywords


def test_select_template_calculus(scaffold):
    t = scaffold.select_template("türev: f(x) = x^2 * sin(x)")
    assert t.template_id == "CALCULUS_PRODUCT_RULE"


# =====================================================================
# 2. 3-Stage FSM Progression Tests
# =====================================================================

def test_fsm_stage_empathy_start(scaffold):
    state, output = scaffold.start_session(
        session_id="sess_01",
        target_equation="-2x < 10",
        solution_roots=[-5.0],
    )
    assert state.stage == SocraticStage.EMPATHY
    assert output.stage == SocraticStage.EMPATHY
    assert output.requires_student_input is False
    assert "Harika ilerliyorsun" in output.message


def test_fsm_stage_empathy_to_grounding(scaffold):
    state, _ = scaffold.start_session("sess_02", "-2x < 10")
    state, output = scaffold.advance(state)
    assert state.stage == SocraticStage.GROUNDING
    assert output.stage == SocraticStage.GROUNDING
    assert output.requires_student_input is False
    assert "sayı doğrusu" in output.message


def test_fsm_stage_grounding_to_self_discovery(scaffold):
    state, _ = scaffold.start_session("sess_03", "-2x < 10")
    state, _ = scaffold.advance(state)  # to grounding
    state, output = scaffold.advance(state)  # to self-discovery
    assert state.stage == SocraticStage.SELF_DISCOVERY
    assert output.stage == SocraticStage.SELF_DISCOVERY
    assert output.requires_student_input is True
    assert "eşitsizlik yönü" in output.message


def test_fsm_self_discovery_success_to_resolved(scaffold):
    state, _ = scaffold.start_session("sess_04", "-2x < 10")
    state, _ = scaffold.advance(state)
    state, _ = scaffold.advance(state)

    # Student types answer containing expected keyword 'yön değiştirir'
    state, output = scaffold.advance(state, student_input="İşaret yön değiştirmelidir")
    assert state.stage == SocraticStage.RESOLVED
    assert output.is_resolved is True
    assert output.confidence_bonus == 0.10
    assert "kendi başına keşfettin" in output.message


def test_fsm_self_discovery_incorrect_guidance_retry(scaffold):
    state, _ = scaffold.start_session("sess_05", "-2x < 10")
    state, _ = scaffold.advance(state)
    state, _ = scaffold.advance(state)

    # Student makes an incorrect / unrelated guess
    state, output = scaffold.advance(state, student_input="Hiçbir şey değişmez")
    assert state.stage == SocraticStage.SELF_DISCOVERY
    assert output.is_resolved is False
    assert output.requires_student_input is True
    assert "İpucu" in output.message
    assert state.attempts == 1


# =====================================================================
# 3. Zero-Leakage & AST Interception Tests
# =====================================================================

def test_zero_leakage_in_empathy_stage():
    guardrail = ZeroLeakageGuardrail()
    # If text somehow contained the root value
    leaked_text = "Harika geldin, çünkü x = -5 olmalıdır."
    sanitized, was_intercepted = guardrail.enforce_zero_leakage(leaked_text, solution_roots=[-5.0])
    assert was_intercepted is True
    assert "-5" not in sanitized
    assert "hangi işlemi uygulamalıyız" in sanitized


def test_zero_leakage_in_ast_symbolic_equivalence():
    guardrail = ZeroLeakageGuardrail()
    # Expression evaluating to 4
    leaked_expr = "Şimdi x = 8/2 olduğunu görüyorsun."
    sanitized, was_intercepted = guardrail.enforce_zero_leakage(leaked_expr, solution_roots=[4.0])
    assert was_intercepted is True
    assert "8/2" not in sanitized


def test_zero_leakage_preserves_clean_socratic_text():
    guardrail = ZeroLeakageGuardrail()
    clean_text = "Önce parantezin önündeki eksi işaretini inceleyelim mi?"
    sanitized, was_intercepted = guardrail.enforce_zero_leakage(clean_text, solution_roots=[3.0])
    assert was_intercepted is False
    assert sanitized == clean_text


def test_all_10_templates_free_of_solution_leak():
    # Verify none of the static template texts leak answers
    for tid, template in SOCRATIC_TEMPLATES.items():
        assert "x = " not in template.empathy_message
        assert "kök =" not in template.grounding_example
        assert "cevap =" not in template.discovery_question
        assert "sonuç =" not in template.guidance_if_stuck


# =====================================================================
# 4. History and Confidence Bonus Tracking Tests
# =====================================================================

def test_session_state_history_tracking(scaffold):
    state, _ = scaffold.start_session("sess_hist", "2x + 6 = 14")
    assert len(state.history) == 1
    assert "EMPATHY:" in state.history[0]

    state, _ = scaffold.advance(state)
    assert len(state.history) == 2
    assert "GROUNDING:" in state.history[1]

    state, _ = scaffold.advance(state)
    assert len(state.history) == 3
    assert "SELF_DISCOVERY:" in state.history[2]

    state, _ = scaffold.advance(state, student_input="İşaret eksiye dönüşür")
    assert len(state.history) == 4
    assert "RESOLVED:" in state.history[3]
    assert state.confidence_gain == 0.10


# =====================================================================
# 5. Multi-Turn Socratic Pipeline Tests
# =====================================================================

def test_socratic_pipeline_multi_turn_flow():
    from app.socratic.pipeline import SocraticPipeline, SocraticRequest
    from app.models.schemas import DiagnosticPayload

    pipeline = SocraticPipeline()
    diag = DiagnosticPayload(
        bug_id="BUG-QUAD-03",
        severity="CRITICAL",
        category="STRUCTURAL_MISCONCEPTION",
        description="Tam kare açılımında çarpımın iki katı (2ab) terimi ihmal edildi.",
        remediation_directive="Geometrik karo modelini göster; iki adet ax dikdörtgenini hatırlat.",
        offending_term="(x + 3)^2 = x^2 + 9",
    )

    # Turn 1: Opening prompt on misconception
    req1 = SocraticRequest(
        user_input="(x + 3)^2 = x^2 + 9",
        target_equation="x^2 + 6*x + 9 = 0",
        solution_roots=[-3.0],
        diagnostic_bug=diag,
        conversation_history=[],
    )
    res1 = pipeline.process(req1)
    assert res1.socratic_ratio >= 2.0
    assert "-3" not in res1.final_output
    assert "alan" in res1.final_output.lower() or "dikdörtgen" in res1.final_output.lower()

    # Turn 2: Student asks "Neden?"
    history = [
        {"role": "assistant", "content": res1.final_output},
        {"role": "user", "content": "Neden iki adet ax terimi var?"},
    ]
    req2 = SocraticRequest(
        user_input="Neden iki adet ax terimi var?",
        target_equation="x^2 + 6*x + 9 = 0",
        solution_roots=[-3.0],
        diagnostic_bug=diag,
        conversation_history=history,
    )
    res2 = pipeline.process(req2)
    assert res2.socratic_ratio >= 1.0
    assert "alan" in res2.final_output.lower() or "topladığında" in res2.final_output.lower()

    # Turn 3: Student discovers middle term "6x"
    history.extend([
        {"role": "assistant", "content": res2.final_output},
        {"role": "user", "content": "Ortadaki iki 3x terimini toplayınca 6x olur"},
    ])
    req3 = SocraticRequest(
        user_input="Ortadaki iki 3x terimini toplayınca 6x olur",
        target_equation="x^2 + 6*x + 9 = 0",
        solution_roots=[-3.0],
        diagnostic_bug=diag,
        conversation_history=history,
    )
    res3 = pipeline.process(req3)
    assert "harika" in res3.final_output.lower() or "eksiksiz" in res3.final_output.lower()
    assert "-3" not in res3.final_output
