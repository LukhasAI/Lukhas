"""
Lazy-loading proxy for the evidence collection system.
This module defers the import of the actual evidence collection engine
until one of its members is accessed. This improves startup time and
allows for optional dependency graceful degradation.
"""
import importlib
from enum import Enum
from types import ModuleType

# List of all attributes that this module is expected to export.
__all__ = [
    "ComplianceRegime",
    "EvidenceCollectionEngine",
    "EvidenceType",
    "collect_evidence",
    "get_evidence_engine",
    "initialize_evidence_collection",
]

_loaded_module = None

def _load_module():
    """Loads the real implementation module or a stub if not found."""
    global _loaded_module
    if _loaded_module is not None:
        return _loaded_module

    try:
        # The real implementation is located here.
        _loaded_module = importlib.import_module("lukhas_website.lukhas.observability.evidence_collection")
    except ImportError:
        # If the real module is not found, create a stub module.
        _stub = ModuleType("evidence_collection_stub")

        class ComplianceRegime(Enum):
            STRICT = "strict"
            BALANCED = "balanced"
            PERMISSIVE = "permissive"

        class EvidenceCollectionEngine:
            def __init__(self, *args, **kwargs): pass
            async def collect_evidence(self, *args, **kwargs): return ""
            def verify_evidence(self, *args, **kwargs): return True
            async def shutdown(self): pass

        class EvidenceType(Enum):
            METRIC = "metric"
            LOG = "log"

        async def collect_evidence(*args, **kwargs): return ""
        def initialize_evidence_collection(*args, **kwargs): return EvidenceCollectionEngine()
        def get_evidence_engine(*args, **kwargs): return EvidenceCollectionEngine()

        _stub.ComplianceRegime = ComplianceRegime
        _stub.EvidenceCollectionEngine = EvidenceCollectionEngine
        _stub.EvidenceType = EvidenceType
        _stub.collect_evidence = collect_evidence
        _stub.initialize_evidence_collection = initialize_evidence_collection
        _stub.get_evidence_engine = get_evidence_engine

        _loaded_module = _stub

    return _loaded_module

def __getattr__(name: str):
    """
    Lazily loads an attribute from the backing module on first access.
    """
    module = _load_module()

    try:
        attr = getattr(module, name)
        # Cache the loaded attribute in the current module's globals
        globals()[name] = attr
        return attr
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
