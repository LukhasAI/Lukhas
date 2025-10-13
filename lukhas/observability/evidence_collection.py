"""Stub: lukhas.observability.evidence_collection"""
from __future__ import annotations

from enum import Enum

# Minimal stub for test collection
__all__ = []

# Add ComplianceRegime for test compatibility
try:
    from labs.observability.evidence_collection import ComplianceRegime
    __all__.append("ComplianceRegime")
except ImportError:
    # Stub enum
    class ComplianceRegime(Enum):
        """Stub compliance regime enum."""
        STRICT = "strict"
        BALANCED = "balanced"
        PERMISSIVE = "permissive"
    __all__.append("ComplianceRegime")

# Add EvidenceCollectionEngine for test compatibility
try:
    from labs.observability.evidence_collection import EvidenceCollectionEngine
    __all__.append("EvidenceCollectionEngine")
except ImportError:
    # Stub class
    class EvidenceCollectionEngine:
        """Stub evidence collection engine."""
        def __init__(self, *args, **kwargs):
            pass
        def collect(self, *args, **kwargs):
            return []
    __all__.append("EvidenceCollectionEngine")

# Add EvidenceType for test compatibility
try:
    from labs.observability.evidence_collection import EvidenceType
    __all__.append("EvidenceType")
except ImportError:
    # Stub enum
    class EvidenceType(Enum):
        """Stub evidence type enum."""
        METRIC = "metric"
        LOG = "log"
        TRACE = "trace"
        EVENT = "event"
    __all__.append("EvidenceType")

# Add collect_evidence for test compatibility
try:
    from labs.observability.evidence_collection import collect_evidence
    __all__.append("collect_evidence")
except ImportError:
    def collect_evidence(*args, **kwargs):
        """Stub evidence collection function."""
        return []
    __all__.append("collect_evidence")

# Added for test compatibility (lukhas.observability.evidence_collection.initialize_evidence_collection)
try:
    from labs.observability.evidence_collection import initialize_evidence_collection
except ImportError:
    def initialize_evidence_collection(*args, **kwargs):
        """Stub for initialize_evidence_collection."""
        return None
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "initialize_evidence_collection" not in __all__:
    __all__.append("initialize_evidence_collection")
