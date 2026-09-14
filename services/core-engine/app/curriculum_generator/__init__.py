"""
Autonomous Curriculum Generator & Formal Verification Package.
Synthesizes 30-node Knowledge DAGs, Buggy Rule catalogs, and formally verifies with SymPy.
"""
from app.curriculum_generator.formal_verifier import SymPyFormalVerifier
from app.curriculum_generator.buggy_synthesizer import TopicBuggySynthesizer
from app.curriculum_generator.dag_synthesizer import AutonomousCurriculumSynthesizer

__all__ = [
    "SymPyFormalVerifier",
    "TopicBuggySynthesizer",
    "AutonomousCurriculumSynthesizer",
]
