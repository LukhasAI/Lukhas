"""Import-safety test for GPT Colony Orchestrator.

This test ensures that importing `core.orchestration.gpt_colony_orchestrator`
does not import any `labs` modules at module-import time. The repository
uses lazy runtime imports for heavy `labs` dependencies; this test will
catch regressions where those imports are performed at import-time.
"""
import importlib
import sys


def test_gpt_colony_import_safe():
    before = set(sys.modules.keys())

    # Import the orchestrator module (should not trigger labs imports)
    importlib.import_module("core.orchestration.gpt_colony_orchestrator")

    after = set(sys.modules.keys())
    new = after - before

    pulled_labs = sorted([name for name in new if name.startswith("labs")])

    assert not pulled_labs, f"Import-time pulled labs modules: {pulled_labs}"
