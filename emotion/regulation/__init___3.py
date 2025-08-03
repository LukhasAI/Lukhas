"""

#TAG:emotion
#TAG:regulation
#TAG:neuroplastic
#TAG:colony


Red Team Framework
==================

Comprehensive red team security testing framework for AI systems.

This framework provides:
- Adversarial testing suites for AI models
- Attack simulation and threat modeling
- Security control validation
- AI-specific penetration testing
- Comprehensive security reporting

Components:
-----------
- adversarial_testing: Adversarial attack testing and model robustness validation
- attack_simulation: Attack scenario generation and simulation execution
- penetration_testing: AI-specific penetration testing frameworks
- validation_frameworks: Security control validation and compliance testing

Usage:
------
from security.red_team_framework import (
    AdversarialTestingSuite,
    AttackSimulationEngine, 
    AIPenetrationTester,
    SecurityControlRegistry
)
"""

# Import main components from each module
from .adversarial_testing import (
    AdversarialTestingSuite,
    PromptInjectionSuite,
    DataPoisoningDetector,
    ModelInversionTester,
    AISystemTarget
)

from .attack_simulation import (
    AIThreatModelingEngine,
    AttackSimulationEngine,
    AttackScenario,
    ThreatActor,
    SimulationResult
)

from .penetration_testing import (
    AIPenetrationTester,
    PentestTarget,
    Vulnerability,
    AttackVector,
    Severity
)

from .validation_frameworks import (
    SecurityControlRegistry,
    ControlValidationEngine,
    SecurityControl,
    ControlCategory,
    ValidationResult
)

__version__ = "1.0.0"

__all__ = [
    # Adversarial Testing
    'AdversarialTestingSuite',
    'PromptInjectionSuite', 
    'DataPoisoningDetector',
    'ModelInversionTester',
    'AISystemTarget',
    
    # Attack Simulation
    'AIThreatModelingEngine',
    'AttackSimulationEngine',
    'AttackScenario',
    'ThreatActor',
    'SimulationResult',
    
    # Penetration Testing
    'AIPenetrationTester',
    'PentestTarget',
    'Vulnerability',
    'AttackVector', 
    'Severity',
    
    # Validation Frameworks
    'SecurityControlRegistry',
    'ControlValidationEngine',
    'SecurityControl',
    'ControlCategory',
    'ValidationResult'
]
