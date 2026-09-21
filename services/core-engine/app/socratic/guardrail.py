"""
Zero-Leakage Output Guardrail and Socratic Metric Verifier.
Protects student cognitive agency by deterministically intercepting any leaked roots or solutions.
Ref: 07-AI-TUTOR-BEHAVIOR-SPEC.md and 15-RISKS-FAILURE-MODES-AND-SAFETY.md.
"""

from __future__ import annotations
import re
from typing import List, Tuple, Any, Optional


class ZeroLeakageGuardrail:
    """
    Deterministic regex interceptor for LLM tutoring outputs.
    """

    SAFE_FALLBACK_PROMPT = (
        "Adımlarını çok iyi ilerletiyorsun! Şimdi bu aşamada eşitliği sağlamak için her iki tarafa hangi işlemi uygulamalıyız?"
    )
    SAFE_FALLBACK_PROMPT_EN = (
        "You are making great progress! What algebraic operation should we apply to both sides now to maintain balance?"
    )

    # General solution disclosure patterns
    LEAK_PATTERNS = [
        r"(cevap|sonuç|kökler?|roots?|answer|solution)\s*(?:=|:|\s+ise|\s+olur|\s+çıkar|\s+dir|\s+dır|\s+is|\s+are)?\s*[-+]?\d+(?:[./]\d+)?",
        r"\b[xyztXYZT]\s*=\s*[-+]?\d+(?:[./]\d+)?",
        r"\b[xyztXYZT]_\{?[12]\}?\s*=\s*[-+]?\d+(?:[./]\d+)?",
        r"\b[xyztXYZT]_\{?1\s*,\s*2\}?\s*=",
        r"\b[xyztXYZT]\s*=\s*[-+]?\d*\s*(?:\\pm|\+/-|\+-)\s*\\?sqrt",
        r"\b(Ç|C)\.?\s*(K|k)\.?\s*=\s*\{[^}]*\}",
        r"(çözüm\s*kümesi|solution\s*set)\s*\{[^}]*\}",
        r"[xyztXYZT]\s*=\s*\(.*?\)\s*/\s*\d+",
        r"\\frac\{[-+]?\d+\}\{[-+]?\d+\}",
    ]

    @classmethod
    def enforce_zero_leakage(
        cls,
        proposed_text: str,
        solution_roots: Optional[List[Any]] = None,
        language: str = "tr",
    ) -> Tuple[str, bool]:
        """
        Inspects text for direct root values or solution disclosures.
        If a leak is found, overrides the output with the safe Socratic fallback prompt.
        Returns (sanitized_text, was_intercepted).
        """
        fallback = cls.SAFE_FALLBACK_PROMPT_EN if language == "en" else cls.SAFE_FALLBACK_PROMPT
        if not proposed_text:
            return fallback, True

        # 1. Check against specific numerical roots of the active problem
        if solution_roots:
            for root in solution_roots:
                if root is None:
                    continue
                try:
                    root_val = float(root)
                    if root_val.is_integer():
                        root_str = str(int(root_val))
                    else:
                        root_str = f"{root_val:.2f}"
                except (ValueError, TypeError, OverflowError):
                    root_str = str(root).strip()

                if not root_str:
                    continue

                escaped = re.escape(root_str)
                # Specific root leakage patterns
                root_patterns = [
                    r"\b[xyztXYZT]\s*=\s*[-+]?" + escaped + r"\b",
                    r"\b[xyztXYZT]_\{?[12]\}?\s*=\s*[-+]?" + escaped + r"\b",
                    r"\bkök[a-z]*\s*(?:[=:]|\s+)?[-+]?" + escaped + r"\b",
                    r"\bcevap\s*(?:[=:]|\s+)?[-+]?" + escaped + r"\b",
                    r"\bsonu(ç|c)\s*(?:[=:]|\s+)?[-+]?" + escaped + r"\b",
                    r"\bde(ğ|g)er\s*(?:[=:]|\s+)?[-+]?" + escaped + r"\b",
                    r"\b(root|roots|solution|answer|zeros?)\s*(?:[=:]|\s+is|\s+are)?\s*[-+]?" + escaped + r"\b",
                ]

                for pat in root_patterns:
                    if re.search(pat, proposed_text, re.IGNORECASE):
                        return fallback, True

        # 2. Check general answer leakage regexes
        for pat in cls.LEAK_PATTERNS:
            if re.search(pat, proposed_text, re.IGNORECASE):
                return fallback, True

        # 3. Check AST / Symbolic equivalence leaks
        if solution_roots:
            if cls._check_symbolic_ast_leak(proposed_text, solution_roots):
                return fallback, True

        return proposed_text, False

    @classmethod
    def _check_symbolic_ast_leak(cls, text: str, solution_roots: List[Any]) -> bool:
        """
        Extracts mathematical equality candidates and evaluates AST equivalence against solution roots.
        """
        import sympy as sp

        # Find patterns like variable = expression or expression = number
        matches = re.findall(r"([a-zA-Z]\s*=\s*[^.!,;\n]+)", text)
        for match in matches:
            parts = match.split("=")
            if len(parts) == 2:
                rhs = parts[1].strip()
                try:
                    expr = sp.sympify(rhs)
                    val = float(expr.evalf())
                    for root in solution_roots:
                        if root is None:
                            continue
                        try:
                            if abs(val - float(root)) < 1e-5:
                                return True
                        except (ValueError, TypeError, OverflowError):
                            continue
                except Exception:
                    continue
        return False

    @classmethod
    def calculate_socratic_ratio(cls, text: str) -> float:
        """
        Calculates the Socratic Question-to-Explanation ratio:
        Count of interrogative sentences divided by count of purely declarative sentences.
        Target: ratio >= 2.0 (High Socratic fidelity).
        """
        if not text:
            return 0.0

        # Count questions
        question_marks = text.count("?")

        # Split sentences by ., !, or newline
        sentences = [s.strip() for s in re.split(r"[.!;\n]+", text) if s.strip()]
        declarative_count = sum(1 for s in sentences if not s.endswith("?"))

        if declarative_count == 0:
            return float(question_marks) if question_marks > 0 else 1.0

        return round(float(question_marks) / float(declarative_count), 2)
