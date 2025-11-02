"""Import-smoke for matriz.consciousness.dream.colony_dream_coordinator."""


def test_colony_dream_coordinator_imports():
    mod = __import__("matriz.consciousness.dream.colony_dream_coordinator", fromlist=["*"])
    assert mod is not None
