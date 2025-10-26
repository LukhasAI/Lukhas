"""Import-smoke for core.governance.identity.core.tagging.identity_tag_resolver."""

def test_identity_tag_resolver_imports():
    mod = __import__(
        "core.governance.identity.core.tagging.identity_tag_resolver",
        fromlist=["*"]
    )
    assert mod is not None
