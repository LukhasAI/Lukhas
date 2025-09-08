"""
Guardian subsystem for governance module.

This module exposes the main GuardianSystem class for use by other
parts of the LUKHAS AI system.
"""
import streamlit as st

from .guardian import GuardianSystem

# Import GuardianValidator
try:
    from .guardian_validator import GuardianValidator
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"GuardianValidator import failed: {e}")
    
    # Provide fallback GuardianValidator
    class GuardianValidator:
        def __init__(self, *args, **kwargs):
            logger.warning("Using fallback GuardianValidator")
        
        async def validate_audio_operation(self, *args, **kwargs):
            from .guardian_validator import ValidationResult, ValidationReport
            return ValidationReport(
                result=ValidationResult.APPROVED,
                confidence_score=1.0,
                validation_time_ms=0.0,
                issues_found=[],
                recommendations=[],
                metadata={"fallback": True}
            )

__all__ = ["GuardianSystem", "GuardianValidator"]
