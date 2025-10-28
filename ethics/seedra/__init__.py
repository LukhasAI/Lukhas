"""
Seedra Ethics Module - Ethical Seed Management & Reasoning
========================================================

SEEDRA (Structured Ethical Evaluation, Decision-making, and Reasoning Architecture)
implements ethical seed management, reasoning validation, and constitutional compliance
for the LUKHAS ethics framework. This module provides the foundational ethical
reasoning capabilities that seed all ethical decisions across the system.

Features:
- Ethical seed generation and validation
- Constitutional AI reasoning chains
- Ethical decision tree evaluation
- Compliance checking and validation
- Ethical impact assessment
- Bias detection and mitigation
"""

from ethics.seedra.seedra_core.ethical_seed_manager import EthicalSeedManager
from ethics.seedra.seedra_core.reasoning_validator import ReasoningValidator
from ethics.seedra.seedra_core.constitutional_evaluator import ConstitutionalEvaluator

# Global seedra instance for system-wide ethical reasoning
_global_seedra_manager = None


def get_seedra():
    """
    Get the global SEEDRA (Structured Ethical Evaluation, Decision-making, 
    and Reasoning Architecture) instance for ethical seed management.
    
    Returns:
        EthicalSeedManager: Configured ethical seed manager with reasoning capabilities
    """
    global _global_seedra_manager
    
    if _global_seedra_manager is None:
        _global_seedra_manager = EthicalSeedManager()
    
    return _global_seedra_manager


def initialize_seedra_system():
    """
    Initialize the SEEDRA system with default ethical configurations.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        seedra = get_seedra()
        return seedra.initialize()
    except Exception as e:
        # Log error but don't raise to prevent system startup failures
        import structlog
        logger = structlog.get_logger(__name__)
        logger.error("seedra_initialization_failed", error=str(e))
        return False


def validate_ethical_decision(decision_context, proposed_action):
    """
    Validate an ethical decision using SEEDRA reasoning.
    
    Args:
        decision_context (dict): Context information for the decision
        proposed_action (dict): The proposed action to validate
        
    Returns:
        dict: Validation result with ethical assessment
    """
    seedra = get_seedra()
    return seedra.validate_decision(decision_context, proposed_action)


def generate_ethical_guidance(scenario):
    """
    Generate ethical guidance for a given scenario.
    
    Args:
        scenario (dict): Scenario description requiring ethical guidance
        
    Returns:
        dict: Ethical guidance with recommendations and constraints
    """
    seedra = get_seedra()
    return seedra.generate_guidance(scenario)


__all__ = [
    "get_seedra",
    "initialize_seedra_system", 
    "validate_ethical_decision",
    "generate_ethical_guidance",
    "EthicalSeedManager",
    "ReasoningValidator",
    "ConstitutionalEvaluator",
]