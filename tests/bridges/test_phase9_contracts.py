"""Phase 9 bridge contract tests: ultra-targeted silencers."""

import importlib as I


def test_governance_guardian_system_start():
    "governance.guardian_system exports start() function."
    m = I.import_module("governance.guardian_system")
    assert hasattr(m, "start"), "governance.guardian_system missing start"


def test_matriz_thought_loop_symbols():
    """consciousness.matriz_thought_loop exports key symbols."""
    m = I.import_module("consciousness.matriz_thought_loop")
    assert hasattr(m, "MATRIZThoughtLoop"), "Missing MATRIZThoughtLoop"
    assert hasattr(m, "MATRIZProcessingContext"), "Missing MATRIZProcessingContext"


def test_enhanced_thought_engine():
    """consciousness.enhanced_thought_engine imports successfully."""
    m = I.import_module("consciousness.enhanced_thought_engine")
    assert m is not None


def test_advanced_metrics():
    """observability.advanced_metrics exports core metrics."""
    m = I.import_module("observability.advanced_metrics")
    assert hasattr(m, "router_cascade_preventions_total"), "Missing router_cascade_preventions_total"
