import asyncio
import sys
from pathlib import Path
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, call, patch

MOCK_MODULE_NAMES = [
    "dream.dashboard",
    "dream.oneiric_engine.oneiric_core.utils.drift_tracker",
    "memory.systems.dream_memory_fold",
    "sklearn.cluster",
    "sklearn.feature_extraction.text",
    "bio.bio_utilities",
]


@patch(
    "core.consciousness.dream_reflection_loop.BRAIN_INTEGRATION_AVAILABLE", True
)
@patch("core.consciousness.dream_reflection_loop.drift_tracker_available", True)
@patch(
    "core.consciousness.dream_reflection_loop.dream_memory_fold_available", True
)
@patch(
    "core.consciousness.dream_reflection_loop.DREAM_CLUSTERING_AVAILABLE", True
)
@patch("core.consciousness.dream_reflection_loop.metrics_db_available", True)
class TestDreamReflectionLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mocked_modules = {name: MagicMock() for name in MOCK_MODULE_NAMES}
        cls._module_patcher = patch.dict(sys.modules, cls._mocked_modules)
        cls._module_patcher.start()

        project_root = Path(__file__).resolve().parents[3]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        try:
            from core.consciousness import dream_reflection_loop
        except Exception:
            cls._module_patcher.stop()
            raise

        cls._dream_reflection_module = dream_reflection_loop
        cls.DreamReflectionLoop = dream_reflection_loop.DreamReflectionLoop
        cls.DreamReflectionConfig = dream_reflection_loop.DreamReflectionConfig
        cls.DreamState = dream_reflection_loop.DreamState

    @classmethod
    def tearDownClass(cls):
        cls._module_patcher.stop()

    def setUp(self):
        self.config = self.DreamReflectionConfig(
            reflection_interval=0.1,
            idle_trigger_seconds=1,
            dream_cycle_minutes=0.1,
            consolidation_batch_size=5,
        )
        self.bio_orchestrator = MagicMock()
        self.bio_orchestrator.get_current_state = AsyncMock(
            return_value={"phase": "REM", "coherence": 0.9}
        )

        self.memory_manager = MagicMock()
        self.memory_manager.get_recent_memories = MagicMock(return_value=[])
        self.memory_manager.store_memory = MagicMock()
        self.memory_manager.store_memory_async = AsyncMock(
            return_value={"id": "mem_123"}
        )
        self.dream_loop = self.DreamReflectionLoop(
            config=self.config,
            bio_orchestrator=self.bio_orchestrator,
            memory_manager=self.memory_manager,
            enable_logging=False,
        )
        self.dream_loop.drift_tracker = MagicMock()
        self.dream_loop.metrics_db = MagicMock()
        self.dream_loop.dream_memory_fold = MagicMock()
        self.dream_loop.dream_memory_fold.dream_snapshot = AsyncMock()
        self.dream_loop.dream_memory_fold.sync_fold = AsyncMock(
            return_value={"success": True}
        )
        self.dream_loop.dream_memory_fold.get_fold_snapshots = AsyncMock(
            return_value=[{}]
        )
        self.dream_loop.dream_memory_fold.get_fold_statistics = AsyncMock(
            return_value={}
        )

    def test_initialization(self, *args):
        self.assertIsNotNone(self.dream_loop)
        self.assertEqual(self.dream_loop.config, self.config)
        self.assertEqual(self.dream_loop.bio_orchestrator, self.bio_orchestrator)
        self.assertEqual(self.dream_loop.memory_manager, self.memory_manager)
        self.assertFalse(self.dream_loop.is_running)
        self.assertFalse(self.dream_loop.dreaming)
        self.assertIsNotNone(self.dream_loop.drift_tracker)

    def test_start_and_stop(self, *args):
        self.dream_loop.start()
        self.assertTrue(self.dream_loop.is_running)
        self.assertIsNotNone(self.dream_loop.reflection_thread)
        self.dream_loop.stop()
        self.assertFalse(self.dream_loop.is_running)

    @patch("core.consciousness.dream_reflection_loop.time.time")
    def test_idle_detection_and_dream_cycle(self, mock_time, *args):
        fixed_current_time = 1672531200.0
        mock_time.return_value = fixed_current_time
        self.dream_loop.last_activity_time = (
            fixed_current_time - self.config.idle_trigger_seconds - 1
        )
        self.dream_loop.start()
        time.sleep(self.config.reflection_interval * 2)  # Wait for loop to run
        self.assertTrue(self.dream_loop.dreaming)
        self.dream_loop.stop()

    def test_get_status(self, *args):
        status = self.dream_loop.get_status()
        self.assertFalse(status["running"])
        self.assertFalse(status["dreaming"])
        self.assertFalse(status["brain_connected"])

    def test_connect_brain(self, *args):
        mock_brain_integration = MagicMock()
        self.dream_loop.connect_brain(mock_brain_integration)
        self.assertTrue(self.dream_loop.brain_connected)
        mock_brain_integration.register_observer.assert_any_call(
            "system_idle", self.dream_loop.handle_system_idle
        )
        mock_brain_integration.register_observer.assert_any_call(
            "system_active", self.dream_loop.handle_system_active
        )

    def test_register_with_core(self, *args):
        mock_core_interface = MagicMock()
        self.dream_loop.register_with_core(mock_core_interface)
        self.assertEqual(self.dream_loop.core_interface, mock_core_interface)
        mock_core_interface.register_handler.assert_any_call(
            "dream_request", self.dream_loop.process_message
        )
        mock_core_interface.register_handler.assert_any_call(
            "consolidation_request", self.dream_loop.consolidate_memories
        )

    def test_process_dream(self, *args):
        dream_content = {"type": "test", "emotions": {"joy": 0.8}}
        result = asyncio.run(self.dream_loop.process_dream(dream_content))
        self.assertTrue(result["processed"])
        self.assertIn("reflection", result)
        self.assertEqual(result["bio_phase"], "REM")
        self.assertEqual(result["qi_coherence"], 0.9)
        self.assertEqual(self.dream_loop.metrics["dreams_processed"], 1)
        self.dream_loop.dream_memory_fold.dream_snapshot.assert_called_once()

    def test_consolidate_memories_no_memories(self, *args):
        self.dream_loop.consolidate_memories()
        self.memory_manager.get_recent_memories.assert_called_once()
        self.memory_manager.store_memory.assert_not_called()

    def test_consolidate_memories_with_clustering(self, *args):
        memories = [
            {"content": f"test memory {i}", "importance": 0.5} for i in range(6)
        ]
        self.memory_manager.get_recent_memories.return_value = memories
        with patch(
            "core.consciousness.dream_reflection_loop.TfidfVectorizer"
        ) as mock_vectorizer, patch(
            "core.consciousness.dream_reflection_loop.DBSCAN"
        ) as mock_dbscan:
            mock_vectorizer.return_value.fit_transform.return_value = [
                [0.1, 0.2]
            ] * 6
            mock_dbscan.return_value.fit_predict.return_value = [0] * 6
            self.dream_loop.consolidate_memories()
            self.memory_manager.store_memory.assert_called_once()
            self.assertIn(
                "consolidated",
                self.memory_manager.store_memory.call_args[0][0]["type"],
            )

    def test_extract_insights(self, *args):
        self.dream_loop.current_dreams = [
            self.DreamState(
                dream_id="1",
                content={},
                timestamp="2023-01-01",
                metadata={"themes": ["A"]},
            ),
            self.DreamState(
                dream_id="2",
                content={},
                timestamp="2023-01-01",
                metadata={"themes": ["A", "B"]},
            ),
            self.DreamState(
                dream_id="3",
                content={},
                timestamp="2023-01-01",
                metadata={"themes": ["A", "C"]},
            ),
        ]
        self.dream_loop.config.pattern_min_frequency = 3
        self.dream_loop.extract_insights()
        self.memory_manager.store_memory.assert_called_once()
        self.assertEqual(
            self.memory_manager.store_memory.call_args[0][0]["content"]["theme"],
            "A",
        )

    def test_recognize_patterns(self, *args):
        self.dream_loop.current_dreams = [
            self.DreamState(
                dream_id="1",
                content={},
                timestamp="2023-01-01",
                qi_coherence=0.1,
                bio_rhythm_phase="X",
            ),
            self.DreamState(
                dream_id="2",
                content={},
                timestamp="2023-01-01",
                qi_coherence=0.2,
                bio_rhythm_phase="X",
            ),
            self.DreamState(
                dream_id="3",
                content={},
                timestamp="2023-01-01",
                qi_coherence=0.3,
                bio_rhythm_phase="X",
            ),
        ]
        self.dream_loop.recognize_patterns()
        self.assertEqual(
            self.dream_loop.metrics["patterns_recognized"], 2
        )  # increasing_coherence and stable_phase

    @patch("core.consciousness.dream_reflection_loop.asyncio.run")
    def test_synthesize_dream(self, mock_asyncio_run, *args):
        self.dream_loop.current_dreams = [
            self.DreamState(dream_id="1", content={}, timestamp="2023-01-01")
        ]
        result = self.dream_loop.synthesize_dream()
        self.assertIn("dream", result)
        self.assertEqual(result["dream"]["type"], "synthesized")
        mock_asyncio_run.assert_called_once()

    def test_handle_system_idle_and_active(self, *args):
        self.assertFalse(self.dream_loop.dreaming)
        self.dream_loop.handle_system_idle({})
        self.assertTrue(self.dream_loop.dreaming)
        self.assertIsNotNone(self.dream_loop.dream_thread)
        self.dream_loop.handle_system_active({})
        self.assertFalse(self.dream_loop.dreaming)

    def test_process_message_dream_request(self, *args):
        message = {
            "type": "dream_request",
            "payload": {"content": {"text": "a test dream"}},
        }
        with patch("core.consciousness.dream_reflection_loop.asyncio.run") as mock_run:
            result = self.dream_loop.process_message(message)
            self.assertEqual(result["status"], "success")
            mock_run.assert_called_once()

    def test_process_message_get_metrics(self, *args):
        message = {"type": "get_metrics"}
        result = self.dream_loop.process_message(message)
        self.assertEqual(result["status"], "success")
        self.assertIn("metrics", result)
        self.assertEqual(result["metrics"], self.dream_loop.get_metrics())

    def test_process_message_unknown_type(self, *args):
        message = {"type": "unknown"}
        result = self.dream_loop.process_message(message)
        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown message type", result["error"])

    def test_synthesize_dream_with_sadness_repair(self, *args):
        from bio import bio_utilities

        self.dream_loop.config.sadness_repair_threshold = 0.5
        self.dream_loop.current_dreams = [
            self.DreamState(
                dream_id="1",
                content={"emotions": {"sadness": 0.8}},
                timestamp="2023-01-01",
            )
        ]
        with patch("core.consciousness.dream_reflection_loop.asyncio.run"):
            result = self.dream_loop.synthesize_dream()
        self.assertTrue(result["dream"]["repair_injected"])
        bio_utilities.inject_narrative_repair.assert_called_once()

    def test_update_scores(self, *args):
        dream_content = {"emotions": {"joy": 0.5, "sadness": 0.1}}
        self.dream_loop.update_scores(dream_content)
        self.assertNotEqual(self.dream_loop.affect_delta, 0.0)

    def test_process_dream_bio_integration_fails(self, *args):
        self.bio_orchestrator.get_current_state = AsyncMock(
            side_effect=Exception("Bio-link failed")
        )
        dream_content = {"type": "test"}
        result = asyncio.run(self.dream_loop.process_dream(dream_content))
        self.assertTrue(result["processed"])
        self.assertEqual(result["bio_phase"], "unknown")  # should fallback

    def test_process_dream_drift_tracker_fails(self, *args):
        self.dream_loop.drift_tracker.track_drift.side_effect = Exception("Drift error")
        dream_content = {"type": "test"}
        result = asyncio.run(self.dream_loop.process_dream(dream_content))
        self.assertTrue(result["processed"])
        self.assertNotIn("drift_metrics", result["metadata"])

    def test_process_dream_memory_consolidation_fails(self, *args):
        self.dream_loop.memory_manager.store_memory_async.side_effect = Exception(
            "Memory error"
        )
        dream_content = {"type": "test"}
        result = asyncio.run(self.dream_loop.process_dream(dream_content))
        self.assertTrue(result["processed"])
        self.assertEqual(result["metadata"]["consolidation"]["status"], "error")

    @patch("core.consciousness.dream_reflection_loop.time.sleep")
    def test_run_dream_cycle_exception(self, mock_sleep, *args):
        self.dream_loop.dreaming = True
        self.dream_loop.consolidate_memories = MagicMock(
            side_effect=Exception("stop")
        )
        self.dream_loop._run_dream_cycle(0.1)
        self.assertFalse(self.dream_loop.dreaming)

    def test_dream_to_memory_feedback(self, *args):
        dream = {"id": "dream123"}
        feedback = {"importance_delta": 0.1}
        self.dream_loop.dream_to_memory_feedback(dream, feedback)
        self.memory_manager.update_memory_importance.assert_called_once_with(
            "dream123", 0.1
        )

    def test_dream_snapshot(self, *args):
        snapshot = self.dream_loop.dream_snapshot()
        self.assertIn("active_dreams", snapshot)
        self.assertIn("metrics", snapshot)
        self.assertIn("timestamp", snapshot)

    def test_sleep_with_check_stops_dreaming(self, *args):
        self.dream_loop.dreaming = False
        with patch("core.consciousness.dream_reflection_loop.time.sleep") as mock_sleep:
            self.dream_loop._sleep_with_check(5)
            mock_sleep.assert_not_called()

    def test_sync_memory_fold(self, *args):
        result = asyncio.run(self.dream_loop.sync_memory_fold("fold1"))
        self.assertTrue(result)
        self.dream_loop.dream_memory_fold.sync_fold.assert_called_once_with("fold1")

    def test_get_fold_snapshots(self, *args):
        result = asyncio.run(self.dream_loop.get_fold_snapshots("fold1"))
        self.assertIsInstance(result, list)
        self.dream_loop.dream_memory_fold.get_fold_snapshots.assert_called_once_with(
            "fold1"
        )

    def test_get_fold_statistics(self, *args):
        result = asyncio.run(self.dream_loop.get_fold_statistics("fold1"))
        self.assertIsInstance(result, dict)
        self.dream_loop.dream_memory_fold.get_fold_statistics.assert_called_once_with(
            "fold1"
        )

    @patch("core.consciousness.dream_reflection_loop.json.dump")
    def test_log_dream_exception(self, mock_json_dump, *args):
        mock_json_dump.side_effect = Exception("JSON error")
        self.dream_loop._log_dream({"test": "dream"})
        # No assertion needed, just checking that it doesn't raise


if __name__ == "__main__":
    unittest.main()
