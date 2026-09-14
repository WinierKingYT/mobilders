"""
Multimodal Math Vision & Handwriting Segmentation Pipeline.
Handles base64 decoding, image preprocessing, LaTeX normalization,
line segmentation, and Knowledge DAG node ontology linkage.
"""

from __future__ import annotations
import re
import base64
from typing import List, Tuple, Optional
from app.graph.knowledge_dag import KnowledgeDAG


class MathVisionPipeline:
    """
    Simulates / wraps mathematical OCR and handwritten line segmentation.
    Transforms raw pixel input or LaTeX strings into clean symbolic sequences.
    """

    def __init__(self, dag: Optional[KnowledgeDAG] = None):
        self.dag = dag or KnowledgeDAG()

    def process_image_or_text(
        self,
        image_base64: Optional[str] = None,
        raw_text_override: Optional[str] = None,
    ) -> List[str]:
        """
        Parses image or raw text into segmented mathematical lines:
        Line 0: Initial problem statement.
        Line 1..k: Student's intermediate written steps.
        """
        if raw_text_override:
            return self._segment_text_into_lines(raw_text_override)

        if image_base64:
            # Strip data URL prefix if present (e.g. data:image/png;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            try:
                decoded_bytes = base64.b64decode(image_base64)
                # In real production, decoded_bytes is passed to TrOCR / Nougat / Vision-LLM
                # For deterministic testing & offline mode, extract any embedded ASCII/LaTeX
                # or fallback to standard segmented structure.
                text_content = decoded_bytes.decode("utf-8", errors="ignore")
                if text_content and "\n" in text_content:
                    return self._segment_text_into_lines(text_content)
            except Exception:
                pass

        # Fallback default demo line sequence
        return ["x^2 + 6*x + 5 = 0", "(x + 3)^2 - 4 = 0", "(x + 3)^2 = 4"]

    def normalize_latex(self, text: str) -> str:
        """
        Converts LaTeX mathematical notation into clean Python / SymPy syntax.
        """
        s = text.strip()
        # Remove common LaTeX formatting commands
        s = re.sub(r"\\left\(", "(", s)
        s = re.sub(r"\\right\)", ")", s)
        s = re.sub(r"\\left\[", "[", s)
        s = re.sub(r"\\right\]", "]", s)
        s = re.sub(r"\\cdot", "*", s)
        s = re.sub(r"\\times", "*", s)
        s = re.sub(r"\\pm", "+/-", s)

        # Convert \frac{a}{b} -> (a)/(b)
        while r"\frac" in s:
            s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", s)

        # Convert \sqrt{x} -> sqrt(x)
        s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)

        # Convert integrals and derivatives
        s = re.sub(r"\\int", "integrate", s)
        s = re.sub(r"\\lim", "limit", s)
        s = re.sub(r"\\sin", "sin", s)
        s = re.sub(r"\\cos", "cos", s)
        s = re.sub(r"\\tan", "tan", s)
        s = re.sub(r"\\cot", "cot", s)
        s = re.sub(r"\\ln", "ln", s)
        s = re.sub(r"\\log", "log", s)

        # Power notation ^ -> **
        s = s.replace("^", "**")

        # Clean spaces around equals
        s = re.sub(r"\s*=\s*", " = ", s)
        return s.strip()

    def _segment_text_into_lines(self, raw: str) -> List[str]:
        """Segments multiline string into cleaned mathematical statements."""
        lines = []
        for line in raw.strip().splitlines():
            cleaned = line.strip()
            # Remove line enumeration like "1)", "1.", "Adım 1:"
            cleaned = re.sub(r"^(?:Adım\s*\d+:|\d+[\.)]\s*)", "", cleaned).strip()
            if cleaned and not cleaned.startswith("#") and not cleaned.startswith("//"):
                lines.append(cleaned)
        return lines

    def link_problem_to_dag_node(self, problem_str: str) -> Tuple[str, str]:
        """
        Maps the problem statement to the appropriate Knowledge DAG node.
        Returns: (node_id, node_title).
        """
        norm = problem_str.lower()

        # 1. Calculus Derivatives (N89 - N110)
        if any(w in norm for w in ("diff", "derivative", "türev", "d/dx", "f'(x)", "teğet")):
            if "teğet" in norm:
                return "N101", self.dag.get_node("N101").title
            if "zincir" in norm:
                return "N94", self.dag.get_node("N94").title
            return "N89", self.dag.get_node("N89").title

        # 2. Calculus Integrals (N111 - N135)
        if any(w in norm for w in ("integrate", "integral", r"\int", "alan hesabı", "riemann")) or (re.search(r"(?<!d/)dx\b", norm) and "d/dx" not in norm):
            if "alan" in norm or "eğri" in norm:
                return "N132", self.dag.get_node("N132").title
            if "u-dönüşümü" in norm or "u=" in norm or "ikame" in norm:
                return "N117", self.dag.get_node("N117").title
            if "riemann" in norm:
                return "N123", self.dag.get_node("N123").title
            return "N111", self.dag.get_node("N111").title

        # 3. Calculus Limits (N81 - N88)
        if any(w in norm for w in ("limit", "lim", "0/0", "süreklilik", "ivt")):
            if "0/0" in norm:
                return "N83", self.dag.get_node("N83").title
            return "N81", self.dag.get_node("N81").title

        # 4. Trigonometry (N51 - N65)
        if any(w in norm for w in ("sin", "cos", "tan", "cot", "birim çember", "radyan")):
            return "N52", self.dag.get_node("N52").title

        # 5. Logarithms & Exponentials (N66 - N80)
        if any(w in norm for w in ("log", "ln", "e**", "e^", "üstel")):
            return "N67", self.dag.get_node("N67").title

        # 6. Polynomials (N39 - N50)
        if any(w in norm for w in ("p(x)", "q(x)", "polinom", "kalan", "derece")):
            return "N47", self.dag.get_node("N47").title

        # 7. Parabolas (N27 - N38)
        if any(w in norm for w in ("parabol", "tepe noktası", "simetri ekseni")):
            return "N27", self.dag.get_node("N27").title

        # 8. Core Quadratics (N01 - N26)
        if "**2" in norm or "^2" in norm:
            return "N19", self.dag.get_node("N19").title

        return "N01", self.dag.get_node("N01").title
