"""LUKHAS PWM - Pulse Width Modulation System
🎭 LUKHAS Trinity Framework (🎭🌈🎓) integration point

Note:
- The package namespace is transitioning from `lukhas_pwm` to `lukhas`.
- Existing imports continue to work. Prefer `import lukhas...` going forward.
"""

from __future__ import annotations

import os
import warnings

if os.environ.get("LUKHAS_SILENCE_IMPORT_NOTICE", "0") not in {"1", "true", "TRUE"}:
	warnings.warn(
		"Namespace notice: `lukhas_pwm` is kept for compatibility; please migrate imports to `lukhas`.",
		DeprecationWarning,
		stacklevel=2,
	)
