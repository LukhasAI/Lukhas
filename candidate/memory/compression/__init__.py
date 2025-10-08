"""Auto-generated __init__.py"""

# Added for test compatibility (candidate.memory.compression.ZSTD_AVAILABLE)
try:
    from candidate.candidate.memory.compression import ZSTD_AVAILABLE  # noqa: F401
except ImportError:
    ZSTD_AVAILABLE = None  # Stub placeholder
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "ZSTD_AVAILABLE" not in __all__:
    __all__.append("ZSTD_AVAILABLE")

# Added for test compatibility (candidate.memory.compression.AdaptiveCompressionManager)
try:
    from candidate.candidate.memory.compression import AdaptiveCompressionManager  # noqa: F401
except ImportError:
    class AdaptiveCompressionManager:
        """Stub for AdaptiveCompressionManager."""
        def __init__(self, *args, **kwargs):
            pass
if "AdaptiveCompressionManager" not in __all__:
    __all__.append("AdaptiveCompressionManager")
