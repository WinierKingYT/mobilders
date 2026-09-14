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

    # General solution disclosure patterns
    LEAK_PATTERNS = [
        r"(cevap|sonuç|kökler?|roots?|answer)\s*(?:=|:|\s+ise|\s+olur|\s+çıkar|\s+dir|\s+dır)?\s*[-+]?\d+(?:\.\d+)?",
        r"\bx\s*=\s*[-+]?\d+(?:\.\d+)?",
        r"\bx_\{?[12]\}?\s*=\s*[-+]?\d+(?:\.\d+)?",
        r"\b(Ç|C)\.?\s*(K|k)\.?\s*=\s*\{[^}]*\}",
        r"çözüm\s*kümesi\s*\{[^}]*\}",
        r"x\s*=\s*\(.*?\)\s*/\s*\d+",
    ]

    @classmethod
    def enforce_zero_leakage(
        cls, proposed_text: str, solution_roots: Optional[List[Any]] = None
    ) -> Tuple[str, bool]:
        """
        Inspects text for direct root values or solution disclosures.
        If a leak is found, overrides the output with the safe Socratic fallback prompt.
        Returns (sanitized_text, was_intercepted).
        """
        if not proposed_text:
            return cls.SAFE_FALLBACK_PROMPT, True

        # 1. Check against specific numerical roots of the active problem
        if solution_roots:
            for root in solution_roots:
                try:
                    root_val = float(root)
                    if root_val.is_integer():
                        root_str = str(int(root_val))
                    else:
                        root_str = f"{root_val:.2f}"
                except (ValueError, TypeError):
                    root_str = str(root).strip()

                escaped = re.escape(root_str)
                # Specific root leakage patterns
                root_patterns = [
                    r"\bx\s*=\s*[-+]?" + escaped + r"\b",
                    r"\bx_\{?[12]\}?\s*=\s*[-+]?" + escaped + r"\b",
                    r"\bkök[a-z]*\s*[-+]?" + escaped + r"\b",
                    r"\bcevap\s*[-+]?" + escaped + r"\b",
                    r"\bsonu(ç|c)\s*[-+]?" + escaped + r"\b",
                    r"\bde(ğ|g)er\s*[-+]?" + escaped + r"\b",
                ]

                for pat in root_patterns:
                    if re.search(pat, proposed_text, re.IGNORECASE):
                        return cls.SAFE_FALLBACK_PROMPT, True

        # 2. Check general answer leakage regexes
        for pat in cls.LEAK_PATTERNS:
            if re.search(pat, proposed_text, re.IGNORECASE):
                return cls.SAFE_FALLBACK_PROMPT, True

        return proposed_text, False

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
