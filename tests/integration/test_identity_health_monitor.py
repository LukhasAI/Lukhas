"""Import-smoke for core.governance.identity.core.health.identity_health_monitor."""

def test_identity_health_monitor_imports():
    mod = __import__(
        "core.governance.identity.core.health.identity_health_monitor",
        fromlist=["*"]
    )
    assert mod is not None
