"""
Pydantic schemas and models for Multimodal Math Vision & Socratic Scanner.
Ref: Hedef 5 (Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası).
"""

from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field


class ScannedStep(BaseModel):
    """Segmented line or handwritten step extracted from notebook."""
    step_index: int = Field(..., description="1-based index of the step in solution")
    raw_text: str = Field(..., description="Raw algebraic string extracted from handwriting")
    latex: str = Field(..., description="LaTeX formatted step representation")
    is_valid: bool = Field(..., description="Whether this algebraic transformation is mathematically valid")
    diagnostic_bug_id: Optional[str] = Field(None, description="Diagnosed Buggy Rule ID if step is invalid")
    error_reason: Optional[str] = Field(None, description="Diagnostic explanation of the misconception")


class MathScanRequest(BaseModel):
    """Payload for submitting notebook/textbook image for Socratic diagnosis."""
    image_base64: Optional[str] = Field(None, description="Base64 encoded image string (JPEG/PNG)")
    raw_text_override: Optional[str] = Field(None, description="Direct text input representing scanned lines for test/API mode")
    student_id: Optional[str] = Field("STU-SCAN-01", description="Student ID for telemetry and cognitive logging")
    target_problem: Optional[str] = Field(None, description="Optional expected problem statement if known")


class MathScanResponse(BaseModel):
    """Anti-Photomath Socratic diagnostic response with Zero-Leakage guarantee."""
    problem_statement: str = Field(..., description="Identified root equation or problem statement")
    dag_node_id: str = Field(..., description="Matched Knowledge DAG node ID (e.g. N26, N94, N117)")
    dag_node_title: str = Field(..., description="Title of the matched curriculum node")
    segmented_steps: List[ScannedStep] = Field(..., description="All segmented solution steps with validity")
    has_error: bool = Field(..., description="True if any student step contains a misconception or invalid move")
    error_step_index: Optional[int] = Field(None, description="1-based index of the first erroneous step")
    detected_bug_id: Optional[str] = Field(None, description="Buggy Rule ID of the diagnosed misconception")
    socratic_hint: str = Field(..., description="Socratic inquiry guiding student to self-correct without leaking answer")
    is_zero_leakage_sanitized: bool = Field(..., description="Confirmed true: no direct roots or final values leaked")
    confidence: float = Field(0.95, description="OCR and segmentation confidence score")
