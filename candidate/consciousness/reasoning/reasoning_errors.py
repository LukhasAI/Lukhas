# Desc: Custom error types for the reasoning module.
# LUKHAS_TAG: reasoning_error


from candidate.core.common import LukhasError


class ReasoningError(LukhasError):
    """Base class for exceptions in the reasoning module."""


class CoherenceError(ReasoningError):
    """Raised when a reasoning coherence check fails."""


class DriftError(ReasoningError):
    """Raised when a reasoning drift check fails."""
