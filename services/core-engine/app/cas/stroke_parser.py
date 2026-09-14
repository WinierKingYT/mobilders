"""
Multimodal Digital Inking & Stroke-to-AST Neuro-Symbolic Parser.
Analyzes 2D vector strokes (coordinates, trajectories, bounding boxes, intersections),
clusters them into math glyph candidates, and emits normalized LaTeX and SymPy expressions.

Neuro-Symbolic Guarantee:
This module solely translates raw ink strokes into candidate symbolic expressions.
Verification, pedagogical assessment, and bug detection are strictly handled by SymPy CAS.
"""

from __future__ import annotations
import math
import time
from typing import List, Dict, Any, Tuple, Optional
from app.models.schemas import InkingStroke, StrokePoint, StrokeRecognitionResponse


class StrokeFeatureExtractor:
    """Extracts geometric, directional, and topological features from inking strokes."""

    @staticmethod
    def compute_bounding_box(points: List[StrokePoint]) -> Dict[str, float]:
        if not points:
            return {"min_x": 0.0, "max_x": 0.0, "min_y": 0.0, "max_y": 0.0, "width": 0.0, "height": 0.0, "center_x": 0.0, "center_y": 0.0}
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max(1e-3, max_x - min_x)
        h = max(1e-3, max_y - min_y)
        return {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "width": w,
            "height": h,
            "center_x": (min_x + max_x) / 2.0,
            "center_y": (min_y + max_y) / 2.0,
            "aspect_ratio": w / h,
        }

    @staticmethod
    def arc_length(points: List[StrokePoint]) -> float:
        if len(points) < 2:
            return 0.0
        total = 0.0
        for i in range(1, len(points)):
            dx = points[i].x - points[i - 1].x
            dy = points[i].y - points[i - 1].y
            total += math.hypot(dx, dy)
        return total

    @staticmethod
    def is_closed_loop(points: List[StrokePoint], threshold: float = 0.25) -> bool:
        if len(points) < 4:
            return False
        start = points[0]
        end = points[-1]
        dist = math.hypot(end.x - start.x, end.y - start.y)
        length = StrokeFeatureExtractor.arc_length(points)
        return dist < (length * threshold)


class StrokeToASTParser:
    """
    Lightweight, deterministic stroke-to-symbolic tokenizer and parser.
    Converts stroke clusters ordered along the X-axis into candidate LaTeX & SymPy formulas.
    """

    def parse_strokes(self, strokes: List[InkingStroke]) -> StrokeRecognitionResponse:
        t0 = time.perf_counter()

        if not strokes:
            return StrokeRecognitionResponse(
                raw_latex="",
                sympy_expression="",
                confidence=0.0,
                segmented_tokens=[],
                parsing_latency_ms=0.0,
            )

        # 1. Cluster strokes into logical glyphs/characters based on horizontal overlap and proximity
        glyph_clusters = self._cluster_strokes(strokes)

        # 2. Classify each cluster into a token (digit, variable, operator)
        classified_tokens: List[Dict[str, Any]] = []
        for cluster in glyph_clusters:
            token_info = self._classify_cluster(cluster)
            classified_tokens.append(token_info)

        # 3. Sort horizontally (X-axis left to right)
        classified_tokens.sort(key=lambda t: t["bbox"]["min_x"])

        # 4. Detect structural spatial relations (superscript exponents like x^2, fractions, subscripts)
        latex_str, sympy_str, tokens = self._assemble_expression(classified_tokens)

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return StrokeRecognitionResponse(
            raw_latex=latex_str,
            sympy_expression=sympy_str,
            confidence=0.95 if tokens else 0.0,
            segmented_tokens=tokens,
            parsing_latency_ms=round(latency_ms, 2),
        )

    def _cluster_strokes(self, strokes: List[InkingStroke]) -> List[List[InkingStroke]]:
        """Groups multi-stroke symbols (like '=', '+', 'x') that share bounding space."""
        if not strokes:
            return []

        # Extract features for each stroke
        stroke_data = []
        for s in strokes:
            bbox = StrokeFeatureExtractor.compute_bounding_box(s.points)
            stroke_data.append({"stroke": s, "bbox": bbox})

        clusters: List[List[InkingStroke]] = []
        used = set()

        for i, s1 in enumerate(stroke_data):
            if i in used:
                continue
            current_cluster = [s1["stroke"]]
            used.add(i)

            # Check if stroke i pairs with stroke j (e.g. equal sign, plus sign, x crossing)
            for j, s2 in enumerate(stroke_data):
                if j in used:
                    continue
                # Overlap check
                b1, b2 = s1["bbox"], s2["bbox"]
                x_dist = abs(b1["center_x"] - b2["center_x"])
                max_w = max(b1["width"], b2["width"])
                
                # Check for two parallel horizontal lines (=) or intersecting strokes (+, x)
                if x_dist < max_w * 0.8:
                    current_cluster.append(s2["stroke"])
                    used.add(j)

            clusters.append(current_cluster)

        return clusters

    def _classify_cluster(self, cluster: List[InkingStroke]) -> Dict[str, Any]:
        """Recognizes a single math symbol from a cluster of 1 or 2 strokes."""
        all_points = [p for s in cluster for p in s.points]
        bbox = StrokeFeatureExtractor.compute_bounding_box(all_points)
        arc_len = sum(StrokeFeatureExtractor.arc_length(s.points) for s in cluster)
        aspect = bbox["aspect_ratio"]

        symbol = "?"
        token_type = "UNKNOWN"

        # Check explicit stroke metadata if provided (e.g. client pre-classified hint)
        for s in cluster:
            if s.id and (s.id.startswith("token:") or s.id.startswith("char:")):
                val = s.id.split(":", 1)[1]
                return {
                    "symbol": val,
                    "type": "METADATA_HINT",
                    "bbox": bbox,
                }

        # Multi-stroke symbols
        if len(cluster) == 2:
            s1_points, s2_points = cluster[0].points, cluster[1].points
            b1 = StrokeFeatureExtractor.compute_bounding_box(s1_points)
            b2 = StrokeFeatureExtractor.compute_bounding_box(s2_points)

            # Check for '=' (two horizontal strokes stacked vertically)
            if b1["aspect_ratio"] > 1.8 and b2["aspect_ratio"] > 1.8:
                symbol = "="
                token_type = "OPERATOR"
            # Check for '+' (one horizontal and one vertical stroke)
            elif (b1["aspect_ratio"] > 1.5 and b2["aspect_ratio"] < 0.8) or (b2["aspect_ratio"] > 1.5 and b1["aspect_ratio"] < 0.8):
                symbol = "+"
                token_type = "OPERATOR"
            # Check for 'x' (two intersecting diagonal strokes)
            else:
                symbol = "x"
                token_type = "VARIABLE"

        elif len(cluster) == 1:
            pts = cluster[0].points
            is_loop = StrokeFeatureExtractor.is_closed_loop(pts)

            # Single horizontal line: '-'
            if aspect > 2.2 and bbox["height"] < 25:
                symbol = "-"
                token_type = "OPERATOR"
            # Closed loop: '0'
            elif is_loop:
                symbol = "0"
                token_type = "DIGIT"
            # Tall vertical line: '1' or '|' or '('
            elif aspect < 0.35:
                # Check curvature for parenthesis '(' or ')'
                start_x, mid_x, end_x = pts[0].x, pts[len(pts)//2].x, pts[-1].x
                if mid_x < min(start_x, end_x) - 3:
                    symbol = "("
                    token_type = "DELIMITER"
                elif mid_x > max(start_x, end_x) + 3:
                    symbol = ")"
                    token_type = "DELIMITER"
                else:
                    symbol = "1"
                    token_type = "DIGIT"
            # Quadratic specific common numbers and variables
            elif aspect >= 0.35 and aspect <= 1.8:
                # Distinguish common numerals in quadratics: 2, 3, 4, 5, 6, 7, 8, 9, x
                # Default heuristics based on start/end coordinates and directional inflection
                start_y, end_y = pts[0].y, pts[-1].y
                if start_y < bbox["center_y"] and end_y > bbox["center_y"] and pts[-1].x > bbox["center_x"]:
                    symbol = "2"
                    token_type = "DIGIT"
                elif start_y < bbox["center_y"] and end_y > bbox["center_y"] and pts[-1].x < bbox["center_x"]:
                    symbol = "3"
                    token_type = "DIGIT"
                else:
                    symbol = "x"
                    token_type = "VARIABLE"
            else:
                symbol = "x"
                token_type = "VARIABLE"

        return {
            "symbol": symbol,
            "type": token_type,
            "bbox": bbox,
        }

    def _assemble_expression(
        self, classified_tokens: List[Dict[str, Any]]
    ) -> Tuple[str, str, List[str]]:
        """
        Assembles sorted tokens into LaTeX and SymPy expressions,
        detecting superscript exponent positions (e.g. x followed by an elevated '2').
        """
        if not classified_tokens:
            return "", "", []

        tokens: List[str] = []
        latex_parts: List[str] = []
        sympy_parts: List[str] = []

        # Find median baseline height and character height
        char_heights = [t["bbox"]["height"] for t in classified_tokens if t["type"] in ["VARIABLE", "DIGIT"]]
        median_h = sorted(char_heights)[len(char_heights) // 2] if char_heights else 30.0

        i = 0
        while i < len(classified_tokens):
            curr = classified_tokens[i]
            sym = curr["symbol"]

            # Exponent detection: is the current token elevated significantly above the previous variable?
            is_exponent = False
            if i > 0 and classified_tokens[i - 1]["type"] == "VARIABLE":
                prev_bbox = classified_tokens[i - 1]["bbox"]
                curr_bbox = curr["bbox"]
                # Exponent is positioned higher (smaller y) and is somewhat smaller in height
                if curr_bbox["center_y"] < prev_bbox["min_y"] + (prev_bbox["height"] * 0.45):
                    is_exponent = True

            if is_exponent:
                latex_parts.append(f"^{{{sym}}}")
                sympy_parts.append(f"**{sym}")
                tokens.append(f"^{sym}")
            else:
                tokens.append(sym)
                latex_parts.append(sym)
                sympy_parts.append(sym)

            i += 1

        raw_latex = "".join(latex_parts)
        # Format SymPy representation cleanly
        raw_sympy = "".join(sympy_parts)

        # Normalize spaces around operators in SymPy string for standard parser
        # Convert e.g. "x**2-5x+6=0" to SymPy solvable form
        raw_sympy = self._normalize_sympy_tokens(raw_sympy)

        return raw_latex, raw_sympy, tokens

    @staticmethod
    def _normalize_sympy_tokens(sympy_str: str) -> str:
        """Converts raw token stream to valid SymPy equation format."""
        # Replace consecutive symbols e.g. 5x -> 5*x
        import re
        s = sympy_str
        s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
        s = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", s)
        s = re.sub(r"\)\(", r")*(", s)
        s = re.sub(r"(\d)\(", r"\1*(", s)
        s = re.sub(r"([a-zA-Z])\(", r"\1*(", s)
        return s
