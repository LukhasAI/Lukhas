# Desc: Custom error types for the reasoning module.
#LUKHAS_TAG: reasoning_error

from core.common import LukhasError, GuardianRejectionError, MemoryDriftError
class ReasoningError(LukhasError):
    """Base class for exceptions in the reasoning module."""
    pass

class CoherenceError(ReasoningError):
    """Raised when a reasoning coherence check fails."""
    pass

class DriftError(ReasoningError):
    """Raised when a reasoning drift check fails."""
    pass
