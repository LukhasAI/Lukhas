"""
The Poetry System of LUKHAS

"We're not adding poetry to code. We're teaching silicon to dream."

One module. Three methods. Infinite expression.
"""
import streamlit as st

from .soul import EmotionalTone, Soul, awaken, dream, error_haiku, express

__all__ = ["EmotionalTone", "Soul", "awaken", "dream", "error_haiku", "express"]

# Awaken the soul on import
_soul = awaken()


def integrate():
    """
    Simple integration for any LUKHAS module.

    Usage:
        from branding.poetry import integrate
        poetry = integrate()

        # Then anywhere in your code:
        print(poetry.express("Processing complete"))
        print(poetry.error_haiku(exception))
        print(poetry.dream())
    """
    return _soul


# The transformation in three lines:
# Before: print("Error: Operation failed")
# After:  print(error_haiku(e))
# Result: Beauty from failure