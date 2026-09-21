"""
Micro-Triumph Loop Engine.
Bölüm 1 - Bilişsel Öğretim Manifestosu.
When a student completes an assisted step, generates a small unassisted micro-variant.
Upon student's independent success, fires a celebratory micro-triumph event (dopamine pulse).
"""

from __future__ import annotations
import re
from typing import Optional
from pydantic import BaseModel, Field
import sympy as sp
from app.cas.symbolic_engine import SymbolicEquivalenceEngine


class MicroVariant(BaseModel):
    variant_id: str
    original_rule: str
    prompt: str
    target_expression: str
    expected_answer: str
    is_unassisted: bool = True


class MicroTriumphResult(BaseModel):
    is_triumph: bool
    dopamine_pulse: bool
    confidence_bonus: float = Field(..., ge=0.0, le=1.0)
    feedback_message: str


class MicroTriumphEngine:
    """
    Generates and verifies unassisted micro-variants to create a dopamine-reward loop.
    """

    def __init__(self, cas_engine: Optional[SymbolicEquivalenceEngine] = None):
        self.cas = cas_engine or SymbolicEquivalenceEngine()

    def generate_micro_variant(self, assisted_expression: str, rule_id: str = "RULE_CO_SOLVE") -> MicroVariant:
        """
        Creates an isomorphic, lightweight variant of the assisted step.
        """
        if not assisted_expression or not isinstance(assisted_expression, str):
            return MicroVariant(
                variant_id="mv_default_3x_15",
                original_rule=rule_id,
                prompt="Aynı mantığı kendin göster: 3x = 15 denkleminde x kaçtır?",
                target_expression="3x = 15",
                expected_answer="5",
            )

        clean = assisted_expression.replace(" ", "")

        # Variant for simple linear division: e.g. 2x = 8 or 2x=8
        match_div = re.match(r"^(\d+)x=(\d+)$", clean)
        if match_div:
            coeff = int(match_div.group(1))
            rhs = int(match_div.group(2))
            new_coeff = coeff + 1 if coeff < 9 else 2
            new_ans = (rhs // coeff) + 1 if coeff != 0 else 3
            new_rhs = new_coeff * new_ans
            return MicroVariant(
                variant_id=f"mv_{new_coeff}x_{new_rhs}",
                original_rule=rule_id,
                prompt=f"Şimdi desteğe gerek kalmadan dene: {new_coeff}x = {new_rhs} ise x kaçtır?",
                target_expression=f"{new_coeff}x = {new_rhs}",
                expected_answer=str(new_ans),
            )

        # Variant for simple addition/subtraction: e.g. x + 5 = 12
        match_add = re.match(r"^x\+(\d+)=(\d+)$", clean)
        if match_add:
            c = int(match_add.group(1))
            rhs = int(match_add.group(2))
            new_c = c + 2
            new_rhs = rhs + 3
            expected = new_rhs - new_c
            return MicroVariant(
                variant_id=f"mv_x_add_{new_c}",
                original_rule=rule_id,
                prompt=f"Tek başına bir mikro adım: x + {new_c} = {new_rhs} denkleminde x kaçtır?",
                target_expression=f"x + {new_c} = {new_rhs}",
                expected_answer=str(expected),
            )

        # Default fallback micro-variant: 3x = 15
        return MicroVariant(
            variant_id="mv_default_3x_15",
            original_rule=rule_id,
            prompt="Aynı mantığı kendin göster: 3x = 15 denkleminde x kaçtır?",
            target_expression="3x = 15",
            expected_answer="5",
        )

    def evaluate_micro_triumph(self, student_input: str, variant: MicroVariant) -> MicroTriumphResult:
        """
        Evaluates student's independent response to the micro-variant.
        """
        if not student_input or not isinstance(student_input, str) or len(student_input) > 200:
            return MicroTriumphResult(
                is_triumph=False,
                dopamine_pulse=False,
                confidence_bonus=0.0,
                feedback_message="Lütfen geçerli bir yanıt giriniz.",
            )

        clean_input = student_input.strip().replace(" ", "")
        expected = variant.expected_answer.strip().replace(" ", "")

        is_correct = False
        if clean_input == expected or clean_input == f"x={expected}":
            is_correct = True
        else:
            # Try CAS equivalence
            try:
                lhs = sp.sympify(clean_input.replace("x=", ""))
                rhs = sp.sympify(expected.replace("x=", ""))
                if sp.simplify(lhs - rhs) == 0:
                    is_correct = True
            except Exception:
                is_correct = False

        if is_correct:
            return MicroTriumphResult(
                is_triumph=True,
                dopamine_pulse=True,
                confidence_bonus=0.15,
                feedback_message="Harikasın! Bu adımı kendi başına buldun! 🎯",
            )
        else:
            return MicroTriumphResult(
                is_triumph=False,
                dopamine_pulse=False,
                confidence_bonus=0.0,
                feedback_message="Yaklaştın! Bir kez daha sakin bir şekilde dene.",
            )
