import importlib

def test_enhanced_thought_engine_bridge_exports():
    m = importlib.import_module("lukhas.consciousness.enhanced_thought_engine")
    assert hasattr(m, "EnhancedThoughtEngine")
    assert hasattr(m, "EnhancedThoughtConfig")
    eng = m.EnhancedThoughtEngine()  # should construct with fallback config
    assert hasattr(eng, "think")
    assert callable(eng.think)
