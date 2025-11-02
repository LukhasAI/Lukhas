"""Import-smoke for core.governance.ethics.ethical_decision_maker."""


def test_edm_imports():
    mod = __import__("core.governance.ethics.ethical_decision_maker", fromlist=["*"])
    assert mod is not None
