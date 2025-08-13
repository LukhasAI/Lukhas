"""
LUKHAS PWM - Legacy Compatibility Module
Redirects to new 'lukhas' namespace

This module exists for backwards compatibility.
All new code should use 'import lukhas' instead.
"""

import sys
import warnings

import lukhas

# Issue deprecation warning
warnings.warn(
    "The 'lukhas_pwm' namespace is deprecated. Please use 'import lukhas' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Make all lukhas attributes available through lukhas_pwm
sys.modules[__name__] = lukhas
