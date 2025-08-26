"""
Tone Module
"""

# Import from the working consciousness_wordsmith.py file we fixed earlier
try:
    from .consciousness_wordsmith import ConsciousnessWordsmith
except ImportError:
    # Fallback to None if not available
    ConsciousnessWordsmith = None

__all__ = ["ConsciousnessWordsmith"]
