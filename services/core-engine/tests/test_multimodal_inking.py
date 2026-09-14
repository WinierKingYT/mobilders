"""
Test Suite: Multimodal Freehand Inking & Neuro-Symbolic AST Parser.
Verifies:
1. StrokeFeatureExtractor geometric and trajectory metrics.
2. StrokeToASTParser token clustering, horizontal ordering, and exponent elevation detection.
3. /api/v1/multimodal/stroke-to-ast endpoint.
4. /api/v1/multimodal/ink/verify endpoint:
   - Neuro-symbolic safety boundary enforcement: SymPy CAS deterministic validation.
   - Misconception diagnosis on recognized handwriting.
   - Latency guarantees.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cas.stroke_parser import StrokeFeatureExtractor, StrokeToASTParser
from app.models.schemas import InkingStroke, StrokePoint

client = TestClient(app)


def test_stroke_feature_extractor_bounding_box():
    pts = [
        StrokePoint(x=10.0, y=20.0),
        StrokePoint(x=30.0, y=50.0),
        StrokePoint(x=20.0, y=35.0),
    ]
    bbox = StrokeFeatureExtractor.compute_bounding_box(pts)
    assert bbox["min_x"] == 10.0
    assert bbox["max_x"] == 30.0
    assert bbox["min_y"] == 20.0
    assert bbox["max_y"] == 50.0
    assert bbox["width"] == 20.0
    assert bbox["height"] == 30.0
    assert bbox["center_x"] == 20.0
    assert bbox["center_y"] == 35.0


def test_stroke_feature_extractor_arc_length_and_loop():
    # Straight line
    line_pts = [StrokePoint(x=0.0, y=0.0), StrokePoint(x=3.0, y=4.0)]
    assert StrokeFeatureExtractor.arc_length(line_pts) == 5.0

    # Closed circle-like loop
    loop_pts = [
        StrokePoint(x=10.0, y=10.0),
        StrokePoint(x=20.0, y=10.0),
        StrokePoint(x=20.0, y=20.0),
        StrokePoint(x=10.0, y=20.0),
        StrokePoint(x=10.5, y=10.5),  # close to start
    ]
    assert StrokeFeatureExtractor.is_closed_loop(loop_pts, threshold=0.25) is True


def test_stroke_to_ast_parser_exponent_detection():
    parser = StrokeToASTParser()

    # Stroke 1: variable 'x' at x=10..30, y=50..90
    stroke_x = InkingStroke(
        id="char:x",
        points=[StrokePoint(x=10.0, y=50.0), StrokePoint(x=30.0, y=90.0)],
    )
    # Stroke 2: elevated exponent '2' at x=35..50, y=25..45 (above baseline)
    stroke_2 = InkingStroke(
        id="char:2",
        points=[StrokePoint(x=35.0, y=25.0), StrokePoint(x=50.0, y=45.0)],
    )

    response = parser.parse_strokes([stroke_x, stroke_2])
    assert "^2" in response.segmented_tokens or "2" in response.segmented_tokens
    assert response.confidence > 0.8
    assert "x" in response.sympy_expression
    assert response.parsing_latency_ms >= 0.0


def test_stroke_to_ast_api_endpoint():
    payload = {
        "strokes": [
            {
                "id": "char:x",
                "points": [{"x": 10.0, "y": 50.0}, {"x": 30.0, "y": 90.0}],
            },
            {
                "id": "char:2",
                "points": [{"x": 35.0, "y": 25.0}, {"x": 50.0, "y": 45.0}],
            },
            {
                "id": "char:-",
                "points": [{"x": 60.0, "y": 65.0}, {"x": 80.0, "y": 65.0}],
            },
            {
                "id": "char:9",
                "points": [{"x": 90.0, "y": 50.0}, {"x": 105.0, "y": 90.0}],
            },
            {
                "id": "char:=",
                "points": [
                    {"x": 115.0, "y": 60.0}, {"x": 135.0, "y": 60.0},
                    {"x": 115.0, "y": 70.0}, {"x": 135.0, "y": 70.0},
                ],
            },
            {
                "id": "char:0",
                "points": [{"x": 145.0, "y": 50.0}, {"x": 160.0, "y": 90.0}],
            },
        ],
        "session_id": "test-session-ink",
    }

    res = client.post("/api/v1/multimodal/stroke-to-ast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "raw_latex" in data
    assert "sympy_expression" in data
    assert data["confidence"] > 0.0


def test_multimodal_ink_verify_valid_step():
    # Valid algebraic step: (x-3)(x+3) = 0 for target x^2 - 9 = 0
    payload = {
        "strokes": [
            {"id": "char:(", "points": [{"x": 5.0, "y": 40.0}, {"x": 5.0, "y": 80.0}]},
            {"id": "char:x", "points": [{"x": 15.0, "y": 40.0}, {"x": 25.0, "y": 80.0}]},
            {"id": "char:-", "points": [{"x": 35.0, "y": 60.0}, {"x": 45.0, "y": 60.0}]},
            {"id": "char:3", "points": [{"x": 55.0, "y": 40.0}, {"x": 65.0, "y": 80.0}]},
            {"id": "char:)", "points": [{"x": 75.0, "y": 40.0}, {"x": 75.0, "y": 80.0}]},
            {"id": "char:(", "points": [{"x": 85.0, "y": 40.0}, {"x": 85.0, "y": 80.0}]},
            {"id": "char:x", "points": [{"x": 95.0, "y": 40.0}, {"x": 105.0, "y": 80.0}]},
            {"id": "char:+", "points": [{"x": 115.0, "y": 40.0}, {"x": 115.0, "y": 80.0}]},
            {"id": "char:3", "points": [{"x": 125.0, "y": 40.0}, {"x": 135.0, "y": 80.0}]},
            {"id": "char:)", "points": [{"x": 145.0, "y": 40.0}, {"x": 145.0, "y": 80.0}]},
            {"id": "char:=", "points": [{"x": 155.0, "y": 55.0}, {"x": 170.0, "y": 55.0}]},
            {"id": "char:0", "points": [{"x": 180.0, "y": 40.0}, {"x": 195.0, "y": 80.0}]},
        ],
        "session_id": "sess-ink-001",
        "node_id": "N06",
        "step_number": 1,
        "target_equation": "x**2 - 9 = 0",
        "elapsed_ms": 1450,
    }

    res = client.post("/api/v1/multimodal/ink/verify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["detected_bug"] is None
    assert data["psychometrics"] is not None
    assert data["total_latency_ms"] < 250.0


def test_multimodal_ink_verify_buggy_rule_detection():
    # Misconception step: BUG-QUAD-01 non-zero product property fallacy: x*(x+6) = 2 -> x = 2
    payload = {
        "strokes": [
            {"id": "char:x", "points": [{"x": 10.0, "y": 40.0}, {"x": 25.0, "y": 80.0}]},
            {"id": "char:=", "points": [{"x": 35.0, "y": 55.0}, {"x": 50.0, "y": 55.0}]},
            {"id": "char:2", "points": [{"x": 60.0, "y": 40.0}, {"x": 75.0, "y": 80.0}]},
        ],
        "session_id": "sess-ink-bug",
        "node_id": "N12",
        "step_number": 2,
        "target_equation": "x**2 + 6*x - 2 = 0",
        "previous_step": "x*(x + 6) = 2",
    }

    res = client.post("/api/v1/multimodal/ink/verify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is False
    assert data["detected_bug"] is not None
    assert data["detected_bug"]["bug_id"] == "BUG-QUAD-01"

