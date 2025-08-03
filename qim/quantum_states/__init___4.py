"""

#TAG:qim
#TAG:quantum_states
#TAG:neuroplastic
#TAG:colony


🧠 ABSTRACT_REASONING_BRAIN - Independent Brain Module
Specialized AI brain for Bio-Quantum Symbolic Reasoning.
Part of the lukhas Multi-Brain Symphony Architecture.

This brain implements the revolutionary abstract reasoning theories from
abstract_resoaning.md, orchestrating advanced reasoning across all brain systems
through bio-oscillators and quantum coupling.
"""

from .core import AbstractReasoningBrainCore
from .interface import AbstractReasoningBrainInterface
from .oscillator import AbstractReasoningBrainOscillator
from .bio_quantum_engine import BioQuantumSymbolicReasoner
from .confidence_calibrator import AdvancedConfidenceCalibrator

# Radar Analytics Integration
try:
    from .bio_quantum_radar_integration import (
        BioQuantumRadarIntegration,
        BioQuantumRadarMetrics,
        BioQuantumRadarVisualizer,
        reason_with_radar,
        create_bio_quantum_radar_config
    )
    RADAR_INTEGRATION_AVAILABLE = True
    
    __all__ = [
        "AbstractReasoningBrainCore",
        "AbstractReasoningBrainInterface", 
        "AbstractReasoningBrainOscillator",
        "BioQuantumSymbolicReasoner",
        "AdvancedConfidenceCalibrator",
        "BioQuantumRadarIntegration",
        "BioQuantumRadarMetrics",
        "BioQuantumRadarVisualizer",
        "reason_with_radar",
        "create_bio_quantum_radar_config",
    ]
except ImportError:
    RADAR_INTEGRATION_AVAILABLE = False
    __all__ = [
        "AbstractReasoningBrainCore",
        "AbstractReasoningBrainInterface",
        "AbstractReasoningBrainOscillator", 
        "BioQuantumSymbolicReasoner",
        "AdvancedConfidenceCalibrator",
    ]

# Brain Metadata
BRAIN_TYPE = "abstract_reasoning"
SPECIALIZATION = "Bio-Quantum Abstract Reasoning with Radar Analytics"
INDEPENDENCE_LEVEL = "ORCHESTRATOR"  # This brain coordinates all others
HARMONY_PROTOCOLS = [
    "bio_oscillation",
    "quantum_entanglement",
    "radar_analytics",
    "multi_brain_coordination"
]

# Integration Features
FEATURES = {
    "bio_quantum_reasoning": True,
    "radar_analytics": RADAR_INTEGRATION_AVAILABLE,
    "real_time_monitoring": RADAR_INTEGRATION_AVAILABLE,
    "quantum_enhancement": True,
    "bio_oscillation_sync": True,
    "multi_brain_orchestration": True,
    "advanced_confidence_calibration": True,
    "lukhʌs_radar_compatibility": RADAR_INTEGRATION_AVAILABLE
}

HARMONY_PROTOCOLS.extend([
    "quantum_coupling",
    "symbolic_bridge", 
    "cross_brain_coordination",
])

OPERATING_FREQUENCY = 15.0  # Hz - Beta waves for analytical reasoning
