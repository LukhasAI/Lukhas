"""Stub: lukhas.observability.performance_regression"""
from __future__ import annotations

# Minimal stub for test collection
__all__ = []

# Added for test compatibility (lukhas.observability.performance_regression.DetectionMethod)
try:
    from candidate.observability.performance_regression import DetectionMethod  # noqa: F401
except ImportError:
    class DetectionMethod:
        """Stub for DetectionMethod."""
        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "DetectionMethod" not in __all__:
    __all__.append("DetectionMethod")

# Added for test compatibility (lukhas.observability.performance_regression.PerformanceRegressionDetector)
try:
    from candidate.observability.performance_regression import PerformanceRegressionDetector  # noqa: F401
except ImportError:
    class PerformanceRegressionDetector:
        """Stub for PerformanceRegressionDetector."""
        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "PerformanceRegressionDetector" not in __all__:
    __all__.append("PerformanceRegressionDetector")

# Added for test compatibility (lukhas.observability.performance_regression.PerformanceBaseline)
try:
    from candidate.observability.performance_regression import PerformanceBaseline  # noqa: F401
except ImportError:
    class PerformanceBaseline:
        """Stub for PerformanceBaseline."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "PerformanceBaseline" not in __all__:
    __all__.append("PerformanceBaseline")

# Added for test compatibility (lukhas.observability.performance_regression.PerformanceRegression)
try:
    from candidate.observability.performance_regression import PerformanceRegression  # noqa: F401
except ImportError:
    class PerformanceRegression:
        """Stub for PerformanceRegression."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def evaluate(self, *args, **kwargs):
            return {}

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "PerformanceRegression" not in __all__:
    __all__.append("PerformanceRegression")
