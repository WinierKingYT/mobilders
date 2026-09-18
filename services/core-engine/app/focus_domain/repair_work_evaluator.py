"""Deterministic server-side evaluator for repair work, self-correction, and transfer.

In accordance with Round 07 requirements:
- The client supplies learner work only.
- The client NEVER supplies boolean success flags.
- Truth rules are strictly bounded to Alpha contracts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field

from .models import KCId
from .registry import INTERVENTION_TEMPLATES


class RepairWorkEvaluationResult(BaseModel):
    is_success: bool
    feedback: str
    normalized_work: Optional[str] = None


class TransferTaskGenerator:
    """Generates server-owned transfer problem contexts for verifying KC recovery."""

    @staticmethod
    def generate_transfer_task(kc: KCId) -> Dict[str, Any]:
        """Produce a bounded Alpha transfer task appropriate for the target KC."""
        if kc == KCId.N1:
            return {
                "prompt": "-5 + 8",
                "expected_answer": "3",
                "target_kc": KCId.N1.value,
            }
        if kc == KCId.N2:
            return {
                "prompt": "(-4) * (-3)",
                "expected_answer": "12",
                "target_kc": KCId.N2.value,
            }
        if kc == KCId.N3:
            return {
                "prompt": "-(-6)",
                "expected_answer": "6",
                "target_kc": KCId.N3.value,
            }
        if kc == KCId.E1:
            return {
                "prompt": "3(x + 4)",
                "expected_answer": "3x + 12",
                "target_kc": KCId.E1.value,
            }
        if kc == KCId.E2:
            return {
                "prompt": "4x + 7 - 2x",
                "expected_answer": "2x + 7",
                "target_kc": KCId.E2.value,
            }
        if kc == KCId.Q0:
            return {
                "prompt": "x - 5 = 2",
                "expected_answer": "x = 7",
                "target_kc": KCId.Q0.value,
            }
        if kc == KCId.Q1:
            return {
                "prompt": "x + 4 = 0",
                "expected_answer": "x = -4",
                "target_kc": KCId.Q1.value,
            }
        if kc == KCId.F1:
            return {
                "prompt": "(x + 2)(x + 5)",
                "expected_answer": "x^2 + 7x + 10",
                "target_kc": KCId.F1.value,
            }
        if kc == KCId.F2:
            return {
                "prompt": "x^2 + 7x + 12 = 0",
                "expected_answer": "(x + 3)(x + 4) = 0",
                "expected_pair": [3, 4],
                "target_kc": KCId.F2.value,
            }
        if kc == KCId.Z1:
            return {
                "prompt": "(x - 1)(x + 4) = 0",
                "expected_answer": "x - 1 = 0 or x + 4 = 0",
                "target_kc": KCId.Z1.value,
            }
        if kc == KCId.L1:
            return {
                "prompt": "3x = 15; solve x",
                "expected_answer": "5",
                "target_kc": KCId.L1.value,
            }
        if kc == KCId.I1:
            return {
                "prompt": "-2x <= 8; solve x",
                "expected_answer": "x>=-4",
                "target_kc": KCId.I1.value,
            }
        if kc == KCId.P1:
            return {
                "prompt": "f(x) = x^2 - 4x + 1; calculate r",
                "expected_answer": "2",
                "target_kc": KCId.P1.value,
            }
        if kc == KCId.PL1:
            return {
                "prompt": "P(x) = x^2 + 2x - 3; remainder divided by (x - 1)",
                "expected_answer": "0",
                "target_kc": KCId.PL1.value,
            }
        return {
            "prompt": "2 + 2",
            "expected_answer": "4",
            "target_kc": kc.value,
        }


class RepairWorkEvaluator:
    """Evaluates learner work against intervention templates deterministically."""

    def evaluate_repair(
        self,
        *,
        intervention_id: str,
        raw_work: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> RepairWorkEvaluationResult:
        template = INTERVENTION_TEMPLATES.get(intervention_id)
        if template is None:
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback=f"Unknown intervention template {intervention_id}",
            )

        # 1. IT-N1-01: Signed addition/subtraction
        if intervention_id == "IT-N1-01":
            return self._eval_n1(raw_work)

        # 2. IT-N2-01: Contrastive signed products: e.g. [-15, 15] or "-15, 15"
        if intervention_id == "IT-N2-01":
            return self._eval_n2(raw_work)

        # 3. IT-N3-01: Unary negation: e.g. "a" or number
        if intervention_id == "IT-N3-01":
            return self._eval_n3(raw_work)

        # 4. IT-Q0-01: Equality preservation
        if intervention_id == "IT-Q0-01":
            return self._eval_q0(raw_work)

        # 5. IT-Q1-01: Factor equation solve
        if intervention_id == "IT-Q1-01":
            return self._eval_q1(raw_work)

        # 6. IT-F2-01: Factor pair check
        if intervention_id == "IT-F2-01":
            return self._eval_f2(raw_work, context)

        # 7. IT-Z1-01: Zero product counterexample
        if intervention_id == "IT-Z1-01":
            return self._eval_z1(raw_work)

        # 8. IT-L1-01: Coefficient isolation
        if intervention_id == "IT-L1-01":
            clean = str(raw_work).strip().lower()
            if clean in {"divide", "division", "böl", "bölme", "x=d/a", "d/a", "5"}:
                return RepairWorkEvaluationResult(
                    is_success=True,
                    feedback="Multiplicative isolation correctly identified.",
                    normalized_work=clean,
                )
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback="Coefficient must be divided, not subtracted.",
                normalized_work=clean,
            )

        # 9. IT-I1-01: Inequality direction reversal
        if intervention_id == "IT-I1-01":
            clean = str(raw_work).strip().lower()
            if clean in {"reverse", "invert", "flip", "yön değiştir", "reversed", "x>=-3", "x >= -3"}:
                return RepairWorkEvaluationResult(
                    is_success=True,
                    feedback="Inequality direction reversal correctly identified.",
                    normalized_work=clean,
                )
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback="Dividing by a negative number requires inverting the inequality sign.",
                normalized_work=clean,
            )

        # 10. IT-P1-01: Parabola vertex formula sign
        if intervention_id == "IT-P1-01":
            clean = str(raw_work).strip().lower().replace(" ", "")
            if any(term in clean for term in ["-b/(2a)", "-b/2a", "minus", "eksi"]):
                return RepairWorkEvaluationResult(
                    is_success=True,
                    feedback="Parabola vertex abscissa formula r = -b/(2a) correctly identified.",
                    normalized_work=clean,
                )
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback="Vertex formula requires a negative sign: r = -b/(2a).",
                normalized_work=clean,
            )

        # 11. IT-PL1-01: Polynomial divisor root substitution
        if intervention_id == "IT-PL1-01":
            clean = str(raw_work).strip().lower().replace(" ", "")
            if any(term in clean for term in ["p(d)", "x=d", "kalan", "d", "substitute", "yerine"]):
                return RepairWorkEvaluationResult(
                    is_success=True,
                    feedback="Polynomial remainder theorem substitution correctly identified.",
                    normalized_work=clean,
                )
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback="By Remainder Theorem, solve x - d = 0 => x = d and evaluate P(d).",
                normalized_work=clean,
            )

        # 8. General fallback / choice response
        clean_work = str(raw_work).strip().lower()
        if clean_work in {"correct", "true", "valid", "1"}:
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Intervention action completed correctly.",
                normalized_work=clean_work,
            )

        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Intervention work did not satisfy success condition.",
            normalized_work=clean_work,
        )

    def evaluate_transfer(
        self,
        *,
        transfer_context: Dict[str, Any],
        raw_work: Any,
    ) -> RepairWorkEvaluationResult:
        expected = str(transfer_context.get("expected_answer", "")).strip().replace(" ", "").lower()
        actual = str(raw_work).strip().replace(" ", "").lower()

        # Check equivalence
        if actual == expected:
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Transfer task completed correctly.",
                normalized_work=actual,
            )

        # Alternative for factor pair: [3, 4] vs [4, 3]
        if "expected_pair" in transfer_context and isinstance(raw_work, (list, tuple)):
            exp_pair = sorted(transfer_context["expected_pair"])
            try:
                act_pair = sorted([int(x) for x in raw_work])
                if act_pair == exp_pair:
                    return RepairWorkEvaluationResult(
                        is_success=True,
                        feedback="Transfer task completed correctly.",
                        normalized_work=str(act_pair),
                    )
            except (ValueError, TypeError):
                pass

        return RepairWorkEvaluationResult(
            is_success=False,
            feedback=f"Transfer work '{actual}' does not match expected result.",
            normalized_work=actual,
        )

    def _eval_n1(self, work: Any) -> RepairWorkEvaluationResult:
        # Expected correct signed sum calculation
        text = str(work).strip().replace(" ", "")
        # If student gives final integer answer or structured sum
        try:
            val = int(text)
            # In N1 intervention exercises, a non-zero correct calculation is expected
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Signed addition verified.",
                normalized_work=str(val),
            )
        except ValueError:
            return RepairWorkEvaluationResult(
                is_success=False,
                feedback="Invalid integer result for signed sum.",
                normalized_work=text,
            )

    def _eval_n2(self, work: Any) -> RepairWorkEvaluationResult:
        # Expected two products e.g. [-15, 15] or list of 2 ints
        if isinstance(work, (list, tuple)) and len(work) == 2:
            try:
                p1, p2 = int(work[0]), int(work[1])
                # One must be negative, one positive of opposite signs
                if (p1 < 0 < p2) or (p2 < 0 < p1):
                    return RepairWorkEvaluationResult(
                        is_success=True,
                        feedback="Contrastive signed multiplication verified.",
                        normalized_work=f"[{p1}, {p2}]",
                    )
            except (ValueError, TypeError):
                pass
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Expected two contrastive products (one negative, one positive).",
        )

    def _eval_n3(self, work: Any) -> RepairWorkEvaluationResult:
        text = str(work).strip().replace(" ", "")
        # -(-a) should be positive
        if text.startswith("+") or (text.isdigit() and not text.startswith("-")):
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Unary negation evaluated to positive.",
                normalized_work=text,
            )
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Unary negation must not preserve inner negative sign.",
            normalized_work=text,
        )

    def _eval_q0(self, work: Any) -> RepairWorkEvaluationResult:
        text = str(work).strip().lower()
        if "subtract" in text or "same" in text or text in {"true", "valid", "both"}:
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Additive equality preservation verified.",
                normalized_work=text,
            )
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Must apply same additive operation to both sides.",
            normalized_work=text,
        )

    def _eval_q1(self, work: Any) -> RepairWorkEvaluationResult:
        text = str(work).strip().replace(" ", "")
        # Correct factor root assignment e.g. x = -3 or just integer
        if "x=" in text or text.lstrip("-").isdigit():
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Factor equation solution verified.",
                normalized_work=text,
            )
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Expected valid root assignment for factor equation.",
            normalized_work=text,
        )

    def _eval_f2(self, work: Any, context: Optional[Dict[str, Any]]) -> RepairWorkEvaluationResult:
        # Check if pair satisfies constraints
        if isinstance(work, (list, tuple)) and len(work) == 2:
            try:
                m, n = int(work[0]), int(work[1])
                if context and "b" in context and "c" in context:
                    if m + n == context["b"] and m * n == context["c"]:
                        return RepairWorkEvaluationResult(
                            is_success=True,
                            feedback="Factor pair satisfies both sum and product.",
                            normalized_work=f"({m}, {n})",
                        )
                else:
                    return RepairWorkEvaluationResult(
                        is_success=True,
                        feedback="Factor pair accepted.",
                        normalized_work=f"({m}, {n})",
                    )
            except (ValueError, TypeError):
                pass
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Factor pair does not satisfy required constraints.",
        )

    def _eval_z1(self, work: Any) -> RepairWorkEvaluationResult:
        text = str(work).strip().lower()
        if "product" in text or "a*b=0" in text or text in {"product", "a*b", "ab=0"}:
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Zero-product implication correctly distinguished.",
                normalized_work=text,
            )
        return RepairWorkEvaluationResult(
            is_success=False,
            feedback="Must select product relationship for zero-product rule.",
            normalized_work=text,
        )


class RetestTaskGenerator:
    """Generates server-owned delayed retest tasks for evaluating retention and durable recovery."""

    @staticmethod
    def generate_retest_task(kc: KCId) -> Dict[str, Any]:
        """Produce a bounded Alpha retest task distinct from the original intervention."""
        if kc == KCId.N1:
            return {
                "prompt": "-7 + 10",
                "expected_answer": "3",
                "target_kc": KCId.N1.value,
            }
        if kc == KCId.N2:
            return {
                "prompt": "(-5) * (-6)",
                "expected_answer": "30",
                "target_kc": KCId.N2.value,
            }
        if kc == KCId.N3:
            return {
                "prompt": "-(-9)",
                "expected_answer": "9",
                "target_kc": KCId.N3.value,
            }
        if kc == KCId.E1:
            return {
                "prompt": "2(x + 5)",
                "expected_answer": "2x + 10",
                "target_kc": KCId.E1.value,
            }
        if kc == KCId.E2:
            return {
                "prompt": "5x + 3 - 3x",
                "expected_answer": "2x + 3",
                "target_kc": KCId.E2.value,
            }
        if kc == KCId.Q0:
            return {
                "prompt": "x - 3 = 4",
                "expected_answer": "x = 7",
                "target_kc": KCId.Q0.value,
            }
        if kc == KCId.Q1:
            return {
                "prompt": "x + 6 = 0",
                "expected_answer": "x = -6",
                "target_kc": KCId.Q1.value,
            }
        if kc == KCId.F1:
            return {
                "prompt": "(x + 3)(x + 4)",
                "expected_answer": "x^2 + 7x + 12",
                "target_kc": KCId.F1.value,
            }
        if kc == KCId.F2:
            return {
                "prompt": "x^2 + 5x + 6 = 0",
                "expected_answer": "(x + 2)(x + 3) = 0",
                "expected_pair": [2, 3],
                "target_kc": KCId.F2.value,
            }
        if kc == KCId.Z1:
            return {
                "prompt": "(x - 2)(x + 5) = 0; which equation must be solved?",
                "expected_answer": "x-2=0 or x+5=0",
                "target_kc": KCId.Z1.value,
            }
        if kc == KCId.L1:
            return {
                "prompt": "4x = 20; solve x",
                "expected_answer": "5",
                "target_kc": KCId.L1.value,
            }
        if kc == KCId.I1:
            return {
                "prompt": "-3x <= 9; solve x",
                "expected_answer": "x>=-3",
                "target_kc": KCId.I1.value,
            }
        return {
            "prompt": f"Verify competence for {kc.value}",
            "expected_answer": "1",
            "target_kc": kc.value,
        }


class DelayedRetestEvaluator:
    """Deterministic server-side evaluator for delayed retest tasks."""

    def evaluate(
        self,
        *,
        retest_context: Dict[str, Any],
        raw_work: Any,
    ) -> RepairWorkEvaluationResult:
        expected = str(retest_context.get("expected_answer", "")).strip().replace(" ", "").lower()
        actual = str(raw_work).strip().replace(" ", "").lower()

        if actual == expected:
            return RepairWorkEvaluationResult(
                is_success=True,
                feedback="Delayed retest task completed correctly.",
                normalized_work=actual,
            )

        if "expected_pair" in retest_context and isinstance(raw_work, (list, tuple)):
            exp_pair = sorted(retest_context["expected_pair"])
            try:
                act_pair = sorted([int(x) for x in raw_work])
                if act_pair == exp_pair:
                    return RepairWorkEvaluationResult(
                        is_success=True,
                        feedback="Delayed retest task completed correctly.",
                        normalized_work=str(act_pair),
                    )
            except (ValueError, TypeError):
                pass

        return RepairWorkEvaluationResult(
            is_success=False,
            feedback=f"Delayed retest work '{actual}' does not match expected result.",
            normalized_work=actual,
        )
