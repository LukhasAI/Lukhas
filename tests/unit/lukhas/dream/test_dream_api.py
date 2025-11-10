import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock
import unittest
import asyncio

# --- Pre-emptive Mocking ---
MOCK_MODULES = {
    "streamlit": MagicMock(), "numpy": MagicMock(), "core.common": MagicMock(),
    "memory.systems.helix_mapper": MagicMock(), "orchestration.brain.cognitive.voice_engine": MagicMock(),
    "core.colonies.creativity_colony": MagicMock(), "qi.qi_dream_adapter": MagicMock(),
    "core.unified.bio_signals": MagicMock(), "consciousness.dream.engine.dream_engine": MagicMock(),
}
sys.modules.update(MOCK_MODULES)

mock_bio_orchestrator = MagicMock()
mock_unified_integration = MagicMock()

async def get_dreams_for_user(store_name):
    if store_name == "enhanced_memories":
        return [{"id": "existing_dream_id", "user_id": "user2", "seed": "retrieval_test", "state": "processed"}]
    return []
mock_unified_integration.get_data = AsyncMock(side_effect=get_dreams_for_user)
mock_unified_integration.store_data = AsyncMock()

patchers = [
    patch("labs.core.unified.orchestration.BioOrchestrator", return_value=mock_bio_orchestrator),
    patch("labs.core.unified.integration.UnifiedIntegration", return_value=mock_unified_integration)
]

os.environ["LUKHAS_DREAMS_ENABLED"] = "1"
os.environ["LUKHAS_PARALLEL_DREAMS"] = "1"

import lukhas.dream

class TestDreamApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for p in patchers: p.start()
        import importlib
        importlib.reload(lukhas.dream)

    @classmethod
    def tearDownClass(cls):
        for p in patchers: p.stop()

    def setUp(self):
        mock_bio_orchestrator.reset_mock()
        mock_unified_integration.reset_mock()
        mock_unified_integration.get_data.side_effect = get_dreams_for_user
        mock_unified_integration.store_data.side_effect = None

        import importlib
        importlib.reload(lukhas.dream)
        self.dream_api = lukhas.dream
        self.engine = self.dream_api.get_dream_engine()
        if self.engine: self.engine.process_dream = AsyncMock()

    def test_01_simulate_dream_success(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        result = self.dream_api.simulate_dream(seed="test_seed", user_id="user1")
        self.assertTrue(result["success"])
        self.assertIn("dream_id", result)
        self.engine.process_dream.assert_awaited_once()

    def test_02_get_dream_success(self):
        retrieved = self.dream_api.get_dream_by_id("existing_dream_id", user_id="user2")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["id"], "existing_dream_id")
        mock_unified_integration.get_data.assert_awaited_with("enhanced_memories")

    def test_03_get_dream_not_found(self):
        retrieved = self.dream_api.get_dream_by_id("non_existent_id", user_id="user1")
        self.assertIsNone(retrieved)

    def test_04_get_dream_cross_user_isolation(self):
        retrieved = self.dream_api.get_dream_by_id("existing_dream_id", user_id="userB")
        self.assertIsNone(retrieved)

    def test_05_parallel_dream_mesh_success(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        seeds = ["s1", "s2", "s3"]
        mesh_result = self.dream_api.parallel_dream_mesh(seeds=seeds, user_id="user_parallel")
        self.assertTrue(mesh_result["success"])
        self.assertEqual(len(mesh_result["dreams"]), len(seeds))
        self.assertEqual(self.engine.process_dream.await_count, len(seeds))

    def test_06_simulate_dream_with_context(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        context = {"emotion": "curiosity"}
        self.dream_api.simulate_dream(seed="context_seed", user_id="user_context", context=context)
        call_args, _ = self.engine.process_dream.call_args
        self.assertEqual(call_args[0]["context"], context)

    @patch("lukhas.dream.is_enabled", return_value=False)
    def test_07_dreams_disabled(self, mock_is_enabled):
        result = self.dream_api.simulate_dream(seed="disabled_test", user_id="user1")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Dream subsystem not enabled")

    @patch("lukhas.dream.is_parallel_enabled", return_value=False)
    def test_08_parallel_dreams_disabled(self, mock_is_parallel_enabled):
        result = self.dream_api.parallel_dream_mesh(seeds=["s1"], user_id="user1")
        self.assertFalse(result["success"])

    @patch("lukhas.dream._run_async")
    def test_09_simulate_dream_engine_exception(self, mock_run_async):
        mock_run_async.side_effect = Exception("Engine failure")
        result = self.dream_api.simulate_dream(seed="exc_seed", user_id="user_exc")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Engine failure")

    def test_10_input_validation_missing_userid(self):
        with self.assertRaises(TypeError): self.dream_api.simulate_dream(seed="s")
        with self.assertRaises(TypeError): self.dream_api.get_dream_by_id(dream_id="d")
        with self.assertRaises(TypeError): self.dream_api.parallel_dream_mesh(seeds=["s"])

    def test_11_retry_on_transient_error(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        self.engine.process_dream.side_effect = [Exception("Transient error"), "Success"]
        result = self.dream_api.simulate_dream(seed="retry_seed", user_id="user_retry")
        self.assertTrue(result["success"])
        self.assertEqual(self.engine.process_dream.await_count, 2)

    def test_12_retry_fails_after_max_attempts(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        self.engine.process_dream.side_effect = Exception("Persistent error")
        result = self.dream_api.simulate_dream(seed="fail_seed", user_id="user_fail")
        self.assertFalse(result["success"])
        self.assertEqual(self.engine.process_dream.await_count, self.dream_api.MAX_RETRIES)
        self.assertIn("Persistent error", result["error"])

    @patch("lukhas.dream.SIMULATION_TIMEOUT_SECONDS", 0.01)
    def test_13_timeout_simulation(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        async def slow_dream(*args, **kwargs):
            await asyncio.sleep(0.1)
        self.engine.process_dream.side_effect = slow_dream
        result = self.dream_api.simulate_dream(seed="timeout_seed", user_id="user_timeout")
        self.assertFalse(result["success"])
        self.assertIn("timed out", result["error"])

    def test_14_parallel_mesh_with_empty_seeds(self):
        mesh_result = self.dream_api.parallel_dream_mesh(seeds=[], user_id="user_empty")
        self.assertTrue(mesh_result["success"])
        self.assertEqual(len(mesh_result["dreams"]), 0)

    def test_15_simulate_dream_empty_seed(self):
        result = self.dream_api.simulate_dream(seed="", user_id="user_empty_seed")
        self.assertTrue(result["success"])
        self.assertEqual(result["seed"], "")

    def test_16_get_dream_by_id_no_match(self):
        mock_unified_integration.get_data.side_effect = AsyncMock(return_value=[{"id": "other_id"}])
        retrieved = self.dream_api.get_dream_by_id("existing_dream_id", user_id="user2")
        self.assertIsNone(retrieved)

    def test_17_parallel_mesh_with_one_failure(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        self.engine.process_dream.side_effect = ["Success", Exception("Failed dream"), "Success"]
        seeds = ["s1", "s2", "s3"]
        mesh_result = self.dream_api.parallel_dream_mesh(seeds=seeds, user_id="user_partial_fail")
        self.assertTrue(mesh_result["success"])
        self.assertEqual(mesh_result["metadata"]["successful_count"], 2)
        self.assertEqual(mesh_result["metadata"]["failed_count"], 1)

    def test_18_simulate_dream_no_context(self):
        result = self.dream_api.simulate_dream(seed="no_context", user_id="user_no_context")
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["context"], {})

    def test_19_get_dream_by_id_empty_store(self):
        mock_unified_integration.get_data.side_effect = AsyncMock(return_value=[])
        retrieved = self.dream_api.get_dream_by_id("some_id", user_id="user_empty_store")
        self.assertIsNone(retrieved)

    def test_20_parallel_mesh_all_failures(self):
        self.assertIsNotNone(self.engine, "Dream engine failed to initialize")
        self.engine.process_dream.side_effect = Exception("Total failure")
        seeds = ["s1", "s2"]
        mesh_result = self.dream_api.parallel_dream_mesh(seeds=seeds, user_id="user_total_fail")
        self.assertTrue(mesh_result["success"])
        self.assertEqual(mesh_result["metadata"]["successful_count"], 0)
        self.assertEqual(mesh_result["metadata"]["failed_count"], 2)

if __name__ == "__main__":
    unittest.main()
