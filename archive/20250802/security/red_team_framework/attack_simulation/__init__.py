"""
Red Team Framework - Attack Simulation Module
=============================================

Attack simulation and threat modeling components for AI security testing.
"""

from .attack_scenario_generator import (
    AIThreatModelingEngine,
    AttackMotivation,
    AttackPhase,
    AttackScenario,
    AttackSimulationEngine,
    AttackStep,
    SimulationResult,
    ThreatActor,
)

__all__ = [
    "AIThreatModelingEngine",
    "AttackSimulationEngine",
    "AttackScenario",
    "AttackStep",
    "SimulationResult",
    "ThreatActor",
    "AttackMotivation",
    "AttackPhase",
]
