"""
Multimodal Math Vision & Socratic OCR Package.
Provides line segmentation, LaTeX extraction, DAG node linkage,
and Anti-Photomath zero-leakage Socratic error diagnosis.
"""

from app.ocr.models import ScannedStep, MathScanRequest, MathScanResponse
from app.ocr.vision_pipeline import MathVisionPipeline
from app.ocr.socratic_diagnoser import SocraticNotebookDiagnoser

__all__ = [
    "ScannedStep",
    "MathScanRequest",
    "MathScanResponse",
    "MathVisionPipeline",
    "SocraticNotebookDiagnoser",
]
