"""Import-smoke for core.utils.orchestration_energy_aware_execution_planner."""

def test_orchestration_energy_aware_execution_planner_imports():
    mod = __import__("core.utils.orchestration_energy_aware_execution_planner", fromlist=["*"])
    assert mod is not None
