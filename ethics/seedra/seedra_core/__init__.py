"""
Seedra_Core Module - Core SEEDRA Components
===========================================

This module contains the core components of SEEDRA (Structured Ethical Evaluation,
Decision-making, and Reasoning Architecture):

- EthicalSeedManager: Manages ethical seeds and provides ethical reasoning
- ReasoningValidator: Validates ethical reasoning chains for soundness
- ConstitutionalEvaluator: Evaluates decisions against constitutional principles

These components work together to provide comprehensive ethical evaluation
and guidance for the LUKHAS system.
"""

from .ethical_seed_manager import (
    EthicalSeedManager,
    EthicalSeed,
    EthicalPrinciple,
    EthicalSeverity,
    EthicalDecisionContext,
    EthicalDecisionResult,
)

from .reasoning_validator import (
    ReasoningValidator,
    ReasoningChain,
    ReasoningStep,
    ReasoningType,
    ReasoningQuality,
    ReasoningValidationResult,
)

from .constitutional_evaluator import (
    ConstitutionalEvaluator,
    ConstitutionalEvaluation,
    ConstitutionalPrinciple,
    ConstitutionalRule,
    ComplianceFramework,
    ViolationSeverity,
)

__all__ = [
    # Ethical Seed Manager
    "EthicalSeedManager",
    "EthicalSeed", 
    "EthicalPrinciple",
    "EthicalSeverity",
    "EthicalDecisionContext",
    "EthicalDecisionResult",
    
    # Reasoning Validator
    "ReasoningValidator",
    "ReasoningChain",
    "ReasoningStep", 
    "ReasoningType",
    "ReasoningQuality",
    "ReasoningValidationResult",
    
    # Constitutional Evaluator
    "ConstitutionalEvaluator",
    "ConstitutionalEvaluation",
    "ConstitutionalPrinciple",
    "ConstitutionalRule",
    "ComplianceFramework",
    "ViolationSeverity",
]
