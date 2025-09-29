"""
LUKHAS Observability System
===========================

Central imports for observability and monitoring functionality.
"""

# Import from lukhas.aka_qualia.observability for backward compatibility
try:
    from lukhas.aka_qualia.observability import (
        CONTENT_TYPE_LATEST,
        AkaqMetrics,
        get_observability,
        measure_scene_processing,
        record_glyph_mapped,
        record_scene_processed,
        update_consciousness_metrics,
    )
except ImportError:
    # Fallback implementations for missing functions
    CONTENT_TYPE_LATEST = "text/plain"

    class AkaqMetrics:
        """Fallback metrics class"""

        pass

    def get_observability():
        """Fallback observability function"""
        return None

    def measure_scene_processing(*args, **kwargs):
        """Fallback scene processing measurement"""
        pass

    def record_glyph_mapped(*args, **kwargs):
        """Fallback glyph mapping recording"""
        pass

    def record_scene_processed(*args, **kwargs):
        """Fallback scene processing recording"""
        pass

    def update_consciousness_metrics(*args, **kwargs):
        """Fallback consciousness metrics update"""
        pass


__all__ = [
    "AkaqMetrics",
    "get_observability",
    "measure_scene_processing",
    "record_glyph_mapped",
    "record_scene_processed",
    "update_consciousness_metrics",
]
