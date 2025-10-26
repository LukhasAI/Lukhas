"""Import-smoke for matriz.consciousness.dream.parallel_reality_simulator."""

def test_parallel_reality_simulator_imports():
    mod = __import__("matriz.consciousness.dream.parallel_reality_simulator", fromlist=["*"])
    assert mod is not None
