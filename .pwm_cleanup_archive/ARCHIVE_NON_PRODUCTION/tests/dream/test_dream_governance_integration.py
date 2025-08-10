import sys
import types
import unittest
from unittest.mock import MagicMock

if (
    "lukhas.consciousness.core_consciousness.dream_engine.dream_reflection_loop"
    not in sys.modules
):
    sys.modules[
        "lukhas.consciousness.core_consciousness.dream_engine.dream_reflection_loop"
    ] = types.ModuleType("dream_reflection_loop")
    sys.modules[
        "lukhas.consciousness.core_consciousness.dream_engine.dream_reflection_loop"
    ].DreamReflectionLoop = None

if "lukhas.creativity.dream_systems.dream_seed" not in sys.modules:
    stub_seed = types.ModuleType("dream_seed")
    stub_seed.seed_dream = lambda *a, **kw: {"symbol": "Δ"}
    sys.modules["lukhas.creativity.dream_systems.dream_seed"] = stub_seed

import importlib.util
from pathlib import Path

module_path = (
    Path(__file__).resolve().parents[2]
    / "lukhas/creativity/dream_systems/dream_convergence_tester.py"
)
spec = importlib.util.spec_from_file_location("dream_convergence_tester", module_path)
dream_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dream_module)
DreamConvergenceTester = dream_module.DreamConvergenceTester

from core.colonies.governance_colony import GovernanceColony


class TestDreamGovernanceIntegration(unittest.TestCase):
    def test_recursion_output_review(self):
        tester = DreamConvergenceTester("seed", max_recursion=1)
        colony = GovernanceColony("gov")
        colony.review_scenario = MagicMock(return_value={"allowed": True})
        result = tester.run_convergence_test(governance_colony=colony)
        colony.review_scenario.assert_called_once()
        self.assertIn("ethics_review", result)
        self.assertTrue(result["ethics_review"]["allowed"])


if __name__ == "__main__":
    unittest.main()
