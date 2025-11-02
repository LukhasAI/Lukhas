"""Import-smoke for core.governance.guardian.system_health_monitor."""


def test_system_health_monitor_imports():
    mod = __import__("core.governance.guardian.system_health_monitor", fromlist=["*"])
    assert mod is not None
