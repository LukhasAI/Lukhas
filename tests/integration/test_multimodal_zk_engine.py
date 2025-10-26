"""Import-smoke for core.governance.identity.zkproof.multimodal_zk_engine."""

def test_multimodal_zk_engine_imports():
    mod = __import__("core.governance.identity.zkproof.multimodal_zk_engine", fromlist=["*"])
    assert mod is not None
