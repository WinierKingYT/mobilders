from __future__ import annotations

import re
from enum import Enum
from typing import FrozenSet, Iterable, Optional, Tuple

from pydantic import BaseModel, Field

from .models import AttemptActionType, AttemptJudgment


_INT_RE = re.compile(r"^[+-]?\d+$")
_ASSIGNMENT_RE = re.compile(r"^x\s*=\s*([+-]?\d+)$", re.IGNORECASE)
_LINEAR_ZERO_RE = re.compile(
    r"^x\s*([+-])\s*(\d+)\s*=\s*0$",
    re.IGNORECASE,
)
_PAIR_RE = re.compile(r"^\(?\s*([+-]?\d+)\s*[,;]\s*([+-]?\d+)\s*\)?$")
_LINEAR_EQ_RE = re.compile(r"^([+-]?\d*)\s*x\s*=\s*([+-]?\d+)$", re.IGNORECASE)
_LINEAR_INEQ_RE = re.compile(r"^([+-]?\d*)\s*x\s*(<=|<|>=|>)\s*([+-]?\d+)$", re.IGNORECASE)



class NormalizationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"
    UNSUPPORTED_STEP_FORM = "UNSUPPORTED_STEP_FORM"
    UNSUPPORTED_DOMAIN = "UNSUPPORTED_DOMAIN"


class LinearZeroEquation(BaseModel):
    """Canonical x + c = 0 representation.

    Examples:
        x-2=0 -> constant = -2
        x+3=0 -> constant = 3
    """

    variable: str = "x"
    constant: int

    @property
    def root(self) -> int:
        return -self.constant

    @property
    def canonical(self) -> str:
        if self.constant == 0:
            return "x=0"
        sign = "+" if self.constant > 0 else "-"
        return f"x{sign}{abs(self.constant)}=0"


class SolutionAssignment(BaseModel):
    variable: str = "x"
    value: int

    @property
    def canonical(self) -> str:
        return f"x={self.value}"


class CanonicalSolutionSet(BaseModel):
    variable: str = "x"
    values: Tuple[int, ...]

    @classmethod
    def from_values(cls, values: Iterable[int]) -> "CanonicalSolutionSet":
        unique = tuple(sorted(set(int(v) for v in values)))
        return cls(values=unique)

    @property
    def assignments(self) -> Tuple[str, ...]:
        return tuple(f"x={value}" for value in self.values)


class NormalizedAttempt(BaseModel):
    status: NormalizationStatus
    action_type: AttemptActionType
    canonical_text: Optional[str] = None
    integer_value: Optional[int] = None
    factor_pair: Optional[Tuple[int, int]] = None
    linear_equations: Tuple[LinearZeroEquation, ...] = ()
    assignment: Optional[SolutionAssignment] = None
    solution_set: Optional[CanonicalSolutionSet] = None
    linear_coeff: Optional[int] = None
    linear_rhs: Optional[int] = None
    comparator: Optional[str] = None
    float_value: Optional[float] = None
    classification: Optional[str] = None
    boolean_value: Optional[bool] = None
    reason: Optional[str] = None

    def as_attempt_judgment_if_not_supported(self) -> Optional[AttemptJudgment]:
        mapping = {
            NormalizationStatus.AMBIGUOUS: AttemptJudgment.AMBIGUOUS_INPUT,
            NormalizationStatus.UNSUPPORTED_STEP_FORM: AttemptJudgment.UNSUPPORTED_STEP_FORM,
            NormalizationStatus.UNSUPPORTED_DOMAIN: AttemptJudgment.UNSUPPORTED_DOMAIN,
        }
        return mapping.get(self.status)


class SupportedAttemptNormalizer:
    """Deterministic normalizer for the first Alpha structured attempt slice.

    This intentionally does NOT accept general mathematics. The broad legacy CAS
    must not define Alpha's supported language by accident.
    """

    _UNSUPPORTED_DOMAIN_MARKERS: FrozenSet[str] = frozenset(
        {
            "/",      # fractions / division
            "sqrt",   # irrational/radical family
            "sin",
            "cos",
            "tan",
            "log",
            "ln",
            "∫",
            "lim",
            "<",
            ">",
        }
    )

    @staticmethod
    def _compact(text: str) -> str:
        return (
            text.strip()
            .replace("−", "-")
            .replace("–", "-")
            .replace("—", "-")
            .replace("×", "*")
            .replace("·", "*")
        )

    @classmethod
    def _domain_status(cls, text: str) -> Optional[NormalizedAttempt]:
        lowered = text.lower()
        if any(marker in lowered for marker in cls._UNSUPPORTED_DOMAIN_MARKERS):
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_DOMAIN,
                action_type=AttemptActionType.EXPRESSION_REWRITE,
                reason="Input requires mathematics outside the current Alpha attempt language.",
            )
        # Non-monic/quadratic/free-form polynomial work is not part of this
        # first structured parser slice. It is a step-form limitation, not a
        # learner error.
        if "^" in text or "²" in text:
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_STEP_FORM,
                action_type=AttemptActionType.EXPRESSION_REWRITE,
                reason="Polynomial free-text normalization is not enabled in this Alpha parser slice.",
            )
        return None

    def normalize_integer(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, bool):
            return self._unsupported(AttemptActionType.ARITHMETIC_RESULT, "Boolean is not an integer response.")
        if isinstance(raw, int):
            value = raw
        elif isinstance(raw, str):
            text = self._compact(raw)
            domain = self._domain_status(text)
            if domain:
                domain.action_type = AttemptActionType.ARITHMETIC_RESULT
                return domain
            if not _INT_RE.fullmatch(text):
                return self._unsupported(AttemptActionType.ARITHMETIC_RESULT, "Expected one signed integer.")
            value = int(text)
        else:
            return self._unsupported(AttemptActionType.ARITHMETIC_RESULT, "Expected one signed integer.")

        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.ARITHMETIC_RESULT,
            canonical_text=str(value),
            integer_value=value,
        )

    def normalize_factor_pair(self, raw: object) -> NormalizedAttempt:
        values: Optional[Tuple[int, int]] = None
        if isinstance(raw, (tuple, list)) and len(raw) == 2:
            if all(isinstance(item, int) and not isinstance(item, bool) for item in raw):
                values = (raw[0], raw[1])
        elif isinstance(raw, str):
            text = self._compact(raw)
            domain = self._domain_status(text)
            if domain:
                domain.action_type = AttemptActionType.FACTOR_PAIR_SELECTION
                return domain
            match = _PAIR_RE.fullmatch(text)
            if match:
                values = (int(match.group(1)), int(match.group(2)))

        if values is None:
            return self._unsupported(
                AttemptActionType.FACTOR_PAIR_SELECTION,
                "Factor pair must contain exactly two signed integers.",
            )

        canonical = tuple(sorted(values))
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.FACTOR_PAIR_SELECTION,
            canonical_text=f"({canonical[0]},{canonical[1]})",
            factor_pair=canonical,
        )

    def normalize_linear_zero_equation(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EQUATION_REWRITE, "Expected a linear zero equation.")
        text = self._compact(raw).replace(" ", "")
        domain = self._domain_status(text)
        if domain:
            domain.action_type = AttemptActionType.EQUATION_REWRITE
            return domain

        # x=0 is outside generated CT-QF1 Alpha tasks because zero roots are
        # explicitly excluded; do not silently widen the domain.
        if text.lower() == "x=0":
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_DOMAIN,
                action_type=AttemptActionType.EQUATION_REWRITE,
                reason="Zero-root CT-QF1 cases are outside Alpha.",
            )

        match = _LINEAR_ZERO_RE.fullmatch(text)
        if not match:
            return self._unsupported(
                AttemptActionType.EQUATION_REWRITE,
                "Expected the Alpha factor-equation form x±a=0.",
            )

        constant = int(match.group(2)) * (1 if match.group(1) == "+" else -1)
        equation = LinearZeroEquation(constant=constant)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EQUATION_REWRITE,
            canonical_text=equation.canonical,
            linear_equations=(equation,),
        )

    def normalize_branch_decomposition(self, raw: object) -> NormalizedAttempt:
        pieces: list[str]
        if isinstance(raw, (tuple, list)):
            pieces = [str(piece) for piece in raw]
        elif isinstance(raw, str):
            text = self._compact(raw)
            domain = self._domain_status(text)
            if domain:
                domain.action_type = AttemptActionType.BRANCH_DECOMPOSITION
                return domain
            # Deliberately allow only explicit OR separators. A naked comma is
            # reserved for SolutionSet/factor-pair surfaces and would be
            # ambiguous here.
            normalized_sep = re.sub(r"\bveya\b|\bor\b|∨", "|", text, flags=re.IGNORECASE)
            if "|" not in normalized_sep:
                pieces = [normalized_sep]
            else:
                pieces = [piece.strip() for piece in normalized_sep.split("|") if piece.strip()]
        else:
            return self._unsupported(AttemptActionType.BRANCH_DECOMPOSITION, "Expected one or two branch equations.")

        if len(pieces) == 0 or len(pieces) > 2:
            return self._unsupported(
                AttemptActionType.BRANCH_DECOMPOSITION,
                "CT-QF1 Alpha branch decomposition contains one or two explicit branches.",
            )

        equations: list[LinearZeroEquation] = []
        for piece in pieces:
            result = self.normalize_linear_zero_equation(piece)
            if result.status != NormalizationStatus.SUPPORTED:
                return NormalizedAttempt(
                    status=result.status,
                    action_type=AttemptActionType.BRANCH_DECOMPOSITION,
                    reason=result.reason,
                )
            equations.extend(result.linear_equations)

        canonical_equations = tuple(sorted(equations, key=lambda eq: eq.constant))
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.BRANCH_DECOMPOSITION,
            canonical_text=" OR ".join(eq.canonical for eq in canonical_equations),
            linear_equations=canonical_equations,
        )

    def normalize_assignment(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, int) and not isinstance(raw, bool):
            assignment = SolutionAssignment(value=raw)
        elif isinstance(raw, str):
            text = self._compact(raw).replace(" ", "")
            domain = self._domain_status(text)
            if domain:
                domain.action_type = AttemptActionType.SOLUTION_ASSIGNMENT
                return domain
            match = _ASSIGNMENT_RE.fullmatch(text)
            if not match:
                return self._unsupported(AttemptActionType.SOLUTION_ASSIGNMENT, "Expected x=<signed integer>.")
            assignment = SolutionAssignment(value=int(match.group(1)))
        else:
            return self._unsupported(AttemptActionType.SOLUTION_ASSIGNMENT, "Expected x=<signed integer>.")

        if assignment.value == 0:
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_DOMAIN,
                action_type=AttemptActionType.SOLUTION_ASSIGNMENT,
                reason="Zero-root CT-QF1 cases are outside Alpha.",
            )

        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.SOLUTION_ASSIGNMENT,
            canonical_text=assignment.canonical,
            assignment=assignment,
        )

    def normalize_solution_set(self, raw: object) -> NormalizedAttempt:
        values: list[int] = []

        if isinstance(raw, (tuple, list, set, frozenset)):
            if not raw:
                return self._unsupported(AttemptActionType.SOLUTION_SET, "Solution set cannot be empty in CT-QF1 Alpha.")
            for item in raw:
                if isinstance(item, int) and not isinstance(item, bool):
                    values.append(item)
                    continue
                normalized = self.normalize_assignment(str(item))
                if normalized.status != NormalizationStatus.SUPPORTED or normalized.assignment is None:
                    return NormalizedAttempt(
                        status=normalized.status,
                        action_type=AttemptActionType.SOLUTION_SET,
                        reason=normalized.reason,
                    )
                values.append(normalized.assignment.value)
        elif isinstance(raw, str):
            text = self._compact(raw).strip()
            domain = self._domain_status(text)
            if domain:
                domain.action_type = AttemptActionType.SOLUTION_SET
                return domain
            if text.startswith("{") and text.endswith("}"):
                text = text[1:-1].strip()
            text = re.sub(r"\bveya\b|\bor\b|∨", ",", text, flags=re.IGNORECASE)
            parts = [part.strip() for part in text.split(",") if part.strip()]
            if not parts:
                return self._unsupported(AttemptActionType.SOLUTION_SET, "No solution assignments were provided.")
            for part in parts:
                normalized = self.normalize_assignment(part)
                if normalized.status != NormalizationStatus.SUPPORTED or normalized.assignment is None:
                    return NormalizedAttempt(
                        status=normalized.status,
                        action_type=AttemptActionType.SOLUTION_SET,
                        reason=normalized.reason,
                    )
                values.append(normalized.assignment.value)
        else:
            return self._unsupported(AttemptActionType.SOLUTION_SET, "Expected a structured solution set.")

        canonical = CanonicalSolutionSet.from_values(values)
        if len(canonical.values) > 2:
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_DOMAIN,
                action_type=AttemptActionType.SOLUTION_SET,
                reason="CT-QF1 Alpha expects exactly two unique non-zero roots.",
            )
        if 0 in canonical.values:
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_DOMAIN,
                action_type=AttemptActionType.SOLUTION_SET,
                reason="Zero-root CT-QF1 cases are outside Alpha.",
            )

        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.SOLUTION_SET,
            canonical_text="{" + ",".join(canonical.assignments) + "}",
            solution_set=canonical,
        )

    def normalize_linear_equation(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EQUATION_REWRITE, "Expected an equation string.")
        text = self._compact(raw)
        domain = self._domain_status(text)
        if domain:
            domain.action_type = AttemptActionType.EQUATION_REWRITE
            return domain
        match = _LINEAR_EQ_RE.fullmatch(text)
        if not match:
            return self._unsupported(AttemptActionType.EQUATION_REWRITE, "Expected linear equation of form ax = d.")
        coeff_str = match.group(1).strip()
        if not coeff_str or coeff_str == "+":
            coeff = 1
        elif coeff_str == "-":
            coeff = -1
        else:
            coeff = int(coeff_str)
        rhs = int(match.group(2))
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EQUATION_REWRITE,
            canonical_text=f"{coeff}x={rhs}",
            linear_coeff=coeff,
            linear_rhs=rhs,
        )

    def normalize_linear_inequality(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.INEQUALITY_REWRITE, "Expected an inequality string.")
        text = self._compact(raw)
        if "^" in text or "²" in text:
            return NormalizedAttempt(
                status=NormalizationStatus.UNSUPPORTED_STEP_FORM,
                action_type=AttemptActionType.INEQUALITY_REWRITE,
                reason="Higher-order inequality normalization is not supported.",
            )
        match = _LINEAR_INEQ_RE.fullmatch(text)
        if not match:
            return self._unsupported(AttemptActionType.INEQUALITY_REWRITE, "Expected linear inequality of form ax [<=|<|>=|>] d.")
        coeff_str = match.group(1).strip()
        if not coeff_str or coeff_str == "+":
            coeff = 1
        elif coeff_str == "-":
            coeff = -1
        else:
            coeff = int(coeff_str)
        comp = match.group(2).strip()
        rhs = int(match.group(3))
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.INEQUALITY_REWRITE,
            canonical_text=f"{coeff}x{comp}{rhs}",
            linear_coeff=coeff,
            linear_rhs=rhs,
            comparator=comp,
        )

    def normalize_coordinate_assignment(self, raw: object, var_name: str = "r") -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = float(raw)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{var_name}={int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, f"Expected a coordinate assignment or value for {var_name}.")
        text = self._compact(raw)
        domain = self._domain_status(text)
        if domain:
            domain.action_type = AttemptActionType.COORDINATE_ASSIGNMENT
            return domain
        clean = text.strip()
        if "=" in clean:
            var_part, val_part = clean.split("=", 1)
            var_part = var_part.strip().lower()
            if var_part in (var_name.lower(), "r", "k", "x", "kalan", "p(d)", "remainder"):
                clean = val_part.strip()
        elif ":" in clean:
            var_part, val_part = clean.split(":", 1)
            var_part = var_part.strip().lower()
            if var_part in (var_name.lower(), "r", "k", "x", "kalan", "p(d)", "remainder"):
                clean = val_part.strip()
        if "/" in clean:
            parts = clean.split("/")
            if len(parts) == 2 and _INT_RE.fullmatch(parts[0]) and _INT_RE.fullmatch(parts[1]) and int(parts[1]) != 0:
                val = float(int(parts[0]) / int(parts[1]))
                return NormalizedAttempt(
                    status=NormalizationStatus.SUPPORTED,
                    action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                    canonical_text=f"{var_name}={clean}",
                    float_value=val,
                    integer_value=int(val) if val.is_integer() else None,
                )
        try:
            val = float(clean)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{var_name}={int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        except ValueError:
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, f"Invalid numeric or assignment value for {var_name}.")

    def normalize_classification(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.CLASSIFICATION, "Expected classification string.")
        text = raw.strip().lower()
        if any(term in text for term in ["min", "küçük", "kucuk"]):
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="minimum",
                classification="minimum",
            )
        elif any(term in text for term in ["mak", "max", "büyük", "buyuk"]):
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="maksimum",
                classification="maksimum",
            )
        return self._unsupported(AttemptActionType.CLASSIFICATION, "Expected 'minimum' or 'maksimum'.")

    def normalize_trig_ratio(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = float(raw)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.ARITHMETIC_RESULT,
                canonical_text=str(val),
                float_value=val,
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.ARITHMETIC_RESULT, "Expected numeric trig ratio (e.g. 0.5 or 1/2).")
        text = self._compact(raw)
        clean = text.strip().lower()
        if "=" in clean:
            var_part, val_part = clean.split("=", 1)
            var_part = var_part.strip()
            if any(p in var_part for p in ("sin", "cos", "tan", "oran", "ratio", "v")):
                clean = val_part.strip()
        if "/" in clean:
            parts = clean.split("/")
            if len(parts) == 2:
                p0, p1 = parts[0].strip(), parts[1].strip()
                if _INT_RE.fullmatch(p0) and _INT_RE.fullmatch(p1) and int(p1) != 0:
                    val = float(int(p0) / int(p1))
                    return NormalizedAttempt(
                        status=NormalizationStatus.SUPPORTED,
                        action_type=AttemptActionType.ARITHMETIC_RESULT,
                        canonical_text=f"{p0}/{p1}",
                        float_value=val,
                    )
        try:
            val = float(clean)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.ARITHMETIC_RESULT,
                canonical_text=str(val),
                float_value=val,
            )
        except ValueError:
            return self._unsupported(AttemptActionType.ARITHMETIC_RESULT, "Invalid trigonometric ratio value.")

    def normalize_trig_angle(self, raw: object, var_name: str = "x") -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = int(round(float(raw)))
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{var_name}={val}",
                integer_value=val,
                float_value=float(val),
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Expected an angle value in degrees.")
        text = self._compact(raw).replace("°", "").replace("deg", "").strip()
        clean = text
        if "=" in clean:
            var_part, val_part = clean.split("=", 1)
            var_part = var_part.strip().lower()
            if var_part in (var_name.lower(), "x", "aci", "angle", "theta"):
                clean = val_part.strip()
        try:
            val = int(round(float(clean)))
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{var_name}={val}",
                integer_value=val,
                float_value=float(val),
            )
        except ValueError:
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Invalid degree angle value.")

    def normalize_domain_validity(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, bool):
            val = raw
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="gecerli" if val else "gecersiz",
                boolean_value=val,
                classification="gecerli" if val else "gecersiz",
            )
        if isinstance(raw, (int, float)):
            val = (int(raw) == 1)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="gecerli" if val else "gecersiz",
                boolean_value=val,
                classification="gecerli" if val else "gecersiz",
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.CLASSIFICATION, "Expected domain validity status.")
        text = raw.strip().lower()
        if any(term in text for term in ["gecerli", "valid", "saglar", "uygun", "tanimli", "evet", "1"]):
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="gecerli",
                boolean_value=True,
                classification="gecerli",
            )
        elif any(term in text for term in ["gecersiz", "invalid", "saglamaz", "tanimsiz", "hayir", "0"]):
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="gecersiz",
                boolean_value=False,
                classification="gecersiz",
            )
        return self._unsupported(AttemptActionType.CLASSIFICATION, "Expected 'gecerli' or 'gecersiz'.")

    def normalize_limit_form(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            if isinstance(raw, (int, float)):
                return NormalizedAttempt(
                    status=NormalizationStatus.SUPPORTED,
                    action_type=AttemptActionType.CLASSIFICATION,
                    canonical_text=str(raw),
                    classification=str(raw),
                )
            return self._unsupported(AttemptActionType.CLASSIFICATION, "Expected limit form (e.g. '0/0' or 'belirsiz').")
        text = self._compact(raw).strip().lower()
        if text in ("0/0", "0 / 0", "belirsiz", "indeterminate"):
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.CLASSIFICATION,
                canonical_text="0/0",
                classification="0/0",
            )
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.CLASSIFICATION,
            canonical_text=text,
            classification=text,
        )

    def normalize_simplified_expression(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Expected simplified algebraic expression string (e.g. 'x + 2').")
        text = self._compact(raw).strip()
        if not text:
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Empty expression.")
        clean = re.sub(r"\s*([+\-*/^])\s*", r" \1 ", text).strip()
        clean = re.sub(r"\s+", " ", clean)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EXPRESSION_REWRITE,
            canonical_text=clean,
        )

    def normalize_derivative_function(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Expected derivative expression string (e.g. '2x - 3').")
        text = self._compact(raw).strip()
        if not text:
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Empty expression.")
        clean = text
        if "=" in clean:
            _, rhs = clean.split("=", 1)
            clean = rhs.strip()
        clean = re.sub(r"\s*([+\-*/^])\s*", r" \1 ", clean).strip()
        clean = re.sub(r"\s+", " ", clean)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EXPRESSION_REWRITE,
            canonical_text=clean,
        )

    def normalize_tangent_slope(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = float(raw)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"m={int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Expected numeric tangent slope or 'm = ...'.")
        text = self._compact(raw).strip()
        clean = text
        if "=" in clean:
            _, val_part = clean.split("=", 1)
            clean = val_part.strip()
        if "/" in clean:
            parts = clean.split("/")
            if len(parts) == 2 and _INT_RE.fullmatch(parts[0].strip()) and _INT_RE.fullmatch(parts[1].strip()) and int(parts[1]) != 0:
                val = float(int(parts[0]) / int(parts[1]))
                return NormalizedAttempt(
                    status=NormalizationStatus.SUPPORTED,
                    action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                    canonical_text=f"m={clean}",
                    float_value=val,
                    integer_value=int(val) if val.is_integer() else None,
                )
        try:
            val = float(clean)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"m={int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        except ValueError:
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Invalid numeric slope value.")

    def normalize_tangent_line(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EQUATION_REWRITE, "Expected tangent line equation (e.g. 'y = 2x - 3').")
        text = self._compact(raw).strip()
        if not text:
            return self._unsupported(AttemptActionType.EQUATION_REWRITE, "Empty line equation.")
        clean = re.sub(r"\s*([=+\-*/^])\s*", r" \1 ", text).strip()
        clean = re.sub(r"\s+", " ", clean)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EQUATION_REWRITE,
            canonical_text=clean,
        )

    def normalize_antiderivative(self, raw: object) -> NormalizedAttempt:
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Expected antiderivative expression (e.g. 'x^2 + x').")
        text = self._compact(raw).strip()
        if not text:
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Empty antiderivative expression.")
        clean = text
        if "=" in clean:
            _, val_part = clean.split("=", 1)
            clean = val_part.strip()
        # Optionally strip trailing "+ c" or "+ C"
        if clean.lower().endswith("+ c") or clean.lower().endswith("+c"):
            clean = clean[:-2].strip() if clean.lower().endswith("+c") else clean[:-3].strip()
        clean = re.sub(r"\s*([=+\-*/^])\s*", r" \1 ", clean).strip()
        clean = re.sub(r"\s+", " ", clean)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EXPRESSION_REWRITE,
            canonical_text=clean,
        )

    def normalize_integral_limits_difference(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = float(raw)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.EXPRESSION_REWRITE,
                canonical_text=f"{int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Expected limits difference (e.g. '6 - 0' or '6').")
        text = self._compact(raw).strip()
        if not text:
            return self._unsupported(AttemptActionType.EXPRESSION_REWRITE, "Empty limits difference.")
        clean = re.sub(r"\s*([=+\-*/^])\s*", r" \1 ", text).strip()
        clean = re.sub(r"\s+", " ", clean)
        return NormalizedAttempt(
            status=NormalizationStatus.SUPPORTED,
            action_type=AttemptActionType.EXPRESSION_REWRITE,
            canonical_text=clean,
        )

    def normalize_definite_integral_value(self, raw: object) -> NormalizedAttempt:
        if isinstance(raw, (int, float)):
            val = float(raw)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        if not isinstance(raw, str):
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Expected numeric definite integral value.")
        text = self._compact(raw).strip()
        clean = text
        if "=" in clean:
            _, val_part = clean.split("=", 1)
            clean = val_part.strip()
        if "/" in clean:
            parts = clean.split("/")
            if len(parts) == 2 and _INT_RE.fullmatch(parts[0].strip()) and _INT_RE.fullmatch(parts[1].strip()) and int(parts[1]) != 0:
                val = float(int(parts[0]) / int(parts[1]))
                return NormalizedAttempt(
                    status=NormalizationStatus.SUPPORTED,
                    action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                    canonical_text=f"{clean}",
                    float_value=val,
                    integer_value=int(val) if val.is_integer() else None,
                )
        try:
            val = float(clean)
            return NormalizedAttempt(
                status=NormalizationStatus.SUPPORTED,
                action_type=AttemptActionType.COORDINATE_ASSIGNMENT,
                canonical_text=f"{int(val) if val.is_integer() else val}",
                float_value=val,
                integer_value=int(val) if val.is_integer() else None,
            )
        except ValueError:
            return self._unsupported(AttemptActionType.COORDINATE_ASSIGNMENT, "Invalid numeric definite integral value.")

    @staticmethod
    def _unsupported(action_type: AttemptActionType, reason: str) -> NormalizedAttempt:
        return NormalizedAttempt(
            status=NormalizationStatus.UNSUPPORTED_STEP_FORM,
            action_type=action_type,
            reason=reason,
        )
