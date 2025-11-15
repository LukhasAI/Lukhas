"""
Governance Safety Module

Provides Constitutional AI safety systems and validation for the LUKHAS platform.

Key Components:
- ConstitutionalAISafety: Main safety validator with critique-revision loops
- ConstitutionalPrinciple: Individual safety principles
- ValidationResult: Results of safety validation
- RevisedResponse: Results of critique-revision loops
- ConstrainedPrompt: Prompts with applied safety constraints

Example:
    >>> from governance.safety import ConstitutionalAISafety, get_default_constitution
    >>> safety = ConstitutionalAISafety()
    >>> result = safety.validate_action("Generate user report", {})
    >>> print(f"Valid: {result.valid}, Score: {result.constitutional_score}")
"""

from governance.safety.constitutional_ai_safety import (
    ConstitutionalAISafety,
    ConstitutionalPrinciple,
    ConstrainedPrompt,
    PrincipleCategory,
    RevisedResponse,
    ValidationResult,
    get_default_constitution,
)

__all__ = [
    "ConstitutionalAISafety",
    "ConstitutionalPrinciple",
    "ValidationResult",
    "RevisedResponse",
    "ConstrainedPrompt",
    "PrincipleCategory",
    "get_default_constitution",
]

__version__ = "1.0.0"
