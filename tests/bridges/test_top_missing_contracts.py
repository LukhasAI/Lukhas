"""Contract tests for top missing imports - Patch 1+2."""
import importlib

import pytest


@pytest.mark.parametrize(
    "mod,sym",
    [
        # Patch 2: Symbol exports
        ("core.interfaces", "CognitiveNodeBase"),
        ("core.interfaces", "ICognitiveNode"),
        ("core.registry", "register"),
        ("core.registry", "_REG"),
        ("consciousness.matriz_thought_loop", "MATRIZProcessingContext"),
        ("consciousness.matriz_thought_loop", "MATRIZThoughtLoop"),
        ("consciousness.consciousness_stream", "ConsciousnessStream"),
        # Patch 1: Package bridges
        ("candidate.observability", "get_metrics"),
        ("candidate.observability", "get_tracer"),
        ("candidate.observability", "Counter"),
        ("candidate.observability", "Histogram"),
        ("candidate.cognitive_core", "__all__"),
    ],
)
def test_symbol_or_module_resolves(mod, sym):
    """Verify symbols resolve from their expected modules."""
    m = importlib.import_module(mod)
    assert hasattr(m, sym), f"{mod} missing expected symbol {sym}"


@pytest.mark.parametrize(
    "mod",
    [
        "lukhas.governance.schema_registry",
        "lukhas.bio.utils",
        "candidate.observability",
        "candidate.cognitive_core",
    ],
)
def test_module_imports(mod):
    """Verify high-impact modules can be imported."""
    m = importlib.import_module(mod)
    assert m is not None
    assert hasattr(m, "__all__")
