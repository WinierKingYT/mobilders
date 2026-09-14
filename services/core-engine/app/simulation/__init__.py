"""
Synthetic Student Twin Simulation Package.
Vectorized Monte Carlo engine for 100,000 student agents over 30-day accelerated learning.
"""
from app.simulation.student_twin import CognitivePersonaType, StudentTwinProfile
from app.simulation.bottleneck_detector import BottleneckDetector
from app.simulation.cohort_factory import VectorizedCohortSimulationFactory

__all__ = [
    "CognitivePersonaType",
    "StudentTwinProfile",
    "BottleneckDetector",
    "VectorizedCohortSimulationFactory",
]
