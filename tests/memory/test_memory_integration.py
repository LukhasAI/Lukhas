import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock

from labs.memory.fold import FoldManager, MemoryFold
from labs.memory.memory_optimization import MemoryTier
from labs.memory.symbol_aware_tiered_memory import SymbolAwareTieredMemory
from memory.memory_orchestrator import MemoryOrchestrator
from prometheus_client import REGISTRY


class TestShortTermMemory(unittest.TestCase):

    def setUp(self):
        """Set up a new MemoryOrchestrator with mocked dependencies for each test."""
        # Unregister all collectors to prevent prometheus metric conflicts between tests
        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            REGISTRY.unregister(collector)

        self.mock_indexer = MagicMock()
        self.mock_guardian = MagicMock()
        # The guardian methods are async, so we need an AsyncMock
        self.mock_guardian.validate_action_async = AsyncMock()
        self.mock_guardian.monitor_behavior_async = AsyncMock()

        self.orchestrator = MemoryOrchestrator(
            indexer=self.mock_indexer,
            guardian=self.mock_guardian
        )
        self.session_id = "test_session_abc123"

    def test_store_item_in_session_fold(self):
        """Tests storing a single item in a simulated session fold."""
        text = "This is a short-term memory."
        meta = {"session_id": self.session_id, "type": "test_data"}
        expected_id = "event_1"
        self.mock_indexer.upsert.return_value = expected_id

        # Since add_event is async, we need to run it in an event loop
        event_id = asyncio.run(self.orchestrator.add_event(text, meta))

        self.assertEqual(event_id, expected_id)
        self.mock_indexer.upsert.assert_called_once_with(text, meta)
        self.mock_guardian.validate_action_async.assert_awaited_once_with("memory_add", {"text": text, "meta": meta})
        self.mock_guardian.monitor_behavior_async.assert_awaited_once()

    def test_retrieve_item_from_session_fold(self):
        """Tests retrieving an item from a simulated session fold."""
        query_text = "short-term memory"
        expected_results = [{"id": "event_1", "text": "This is a short-term memory.", "score": 0.9}]
        self.mock_indexer.search_text.return_value = expected_results

        filters = {"session_id": self.session_id}
        results = self.orchestrator.query(query_text, k=1, filters=filters)

        self.assertEqual(results, expected_results)
        self.mock_indexer.search_text.assert_called_once_with(query_text, k=1, filters=filters)

    def test_working_memory_capacity(self):
        """Tests storing and retrieving multiple items to simulate capacity."""
        items_to_store = 100
        stored_ids = [f"event_{i}" for i in range(items_to_store)]
        self.mock_indexer.upsert.side_effect = stored_ids

        for i in range(items_to_store):
            text = f"Memory event number {i}"
            meta = {"session_id": self.session_id, "index": i}
            asyncio.run(self.orchestrator.add_event(text, meta))

        self.assertEqual(self.mock_indexer.upsert.call_count, items_to_store)

        # Now, test retrieval
        query_text = "memory event"
        expected_results = [{"id": f"event_{i}", "text": f"Memory event number {i}", "score": 0.9} for i in range(items_to_store)]
        self.mock_indexer.search_text.return_value = expected_results

        filters = {"session_id": self.session_id}
        results = self.orchestrator.query(query_text, k=items_to_store, filters=filters)

        self.assertEqual(len(results), items_to_store)

    def test_time_to_live_filtering(self):
        """Simulates TTL by adding an expiry timestamp and filtering on it."""

        # Item that has not expired
        fresh_item_text = "This is a fresh item."
        fresh_meta = {"session_id": self.session_id, "expiry": int(time.time()) + 3600}

        # Item that has expired
        stale_item_text = "This is a stale item."
        stale_meta = {"session_id": self.session_id, "expiry": int(time.time()) - 3600}

        asyncio.run(self.orchestrator.add_event(fresh_item_text, fresh_meta))
        asyncio.run(self.orchestrator.add_event(stale_item_text, stale_meta))

        # We want to query for items that have not expired.
        # The filter would be handled by the indexer, e.g., "expiry > now"
        # We simulate this by just setting a filter the orchestrator should pass along.
        query_text = "item"
        current_time = int(time.time())
        # This filter structure depends on the backend, but we're just testing the pass-through
        filters = {"session_id": self.session_id, "expiry": {"$gt": current_time}}

        expected_results = [{"id": "fresh_event", "text": fresh_item_text, "score": 0.9}]
        self.mock_indexer.search_text.return_value = expected_results

        results = self.orchestrator.query(query_text, filters=filters)

        self.assertEqual(results, expected_results)
        self.mock_indexer.search_text.assert_called_once_with(query_text, k=8, filters=filters)

class TestLongTermMemory(unittest.TestCase):

    def setUp(self):
        """Set up a new FoldManager for each test."""
        self.fold_manager = FoldManager()

    def test_fold_creation_and_persistence(self):
        """Tests that a memory fold can be created and is persisted in the manager."""
        content = "This is a persistent memory."
        fold = self.fold_manager.create_fold(content)
        self.assertIn(fold.id, self.fold_manager.folds)
        self.assertEqual(self.fold_manager.folds[fold.id].content, content)

    def test_fold_retrieval(self):
        """Tests retrieving a fold and checks that access count increments."""
        content = "Memory to be retrieved."
        fold = self.fold_manager.create_fold(content)
        self.assertEqual(fold.accessed_count, 0)

        retrieved_fold = self.fold_manager.retrieve_fold(fold.id)
        self.assertIsNotNone(retrieved_fold)
        self.assertEqual(retrieved_fold.id, fold.id)
        self.assertEqual(retrieved_fold.accessed_count, 1)

        # Verify the original object in the manager was updated
        self.assertEqual(self.fold_manager.folds[fold.id].accessed_count, 1)

    def test_fold_cascade_prevention_pruning(self):
        """Tests that the oldest, least important folds are pruned when max capacity is reached."""
        # Set a smaller max for easier testing
        self.fold_manager.MAX_FOLDS = 10

        # Create 10 folds with low importance
        unimportant_folds = []
        for i in range(10):
            fold = self.fold_manager.create_fold(f"unimportant content {i}")
            fold.importance = 0.1
            unimportant_folds.append(fold)

        self.assertEqual(len(self.fold_manager.folds), 10)

        # Create one more fold, which should trigger pruning
        important_fold = self.fold_manager.create_fold("important content")
        important_fold.importance = 0.9

        # After pruning, we should have 90% of MAX_FOLDS + 1 new fold = 9 + 1 = 10
        # But the logic keeps 90% of the *old* folds, removing 1, then adds the new one.
        # So we should be back at 10 folds, with the oldest unimportant one removed.
        self.assertEqual(len(self.fold_manager.folds), 10)

        # The first unimportant fold should be pruned
        self.assertNotIn(unimportant_folds[0].id, self.fold_manager.folds)
        # The new important fold should be present
        self.assertIn(important_fold.id, self.fold_manager.folds)

    def test_retrieval_of_preserved_fold_after_pruning(self):
        """Tests that important memories are preserved and can be retrieved after pruning."""
        self.fold_manager.MAX_FOLDS = 10

        # Create an important fold and access it to make it more important
        important_fold = self.fold_manager.create_fold("critical memory")
        important_fold.importance = 0.9
        important_fold.accessed_count = 10

        # Fill the rest with unimportant folds
        for i in range(9):
            self.fold_manager.create_fold(f"filler content {i}")

        self.assertEqual(len(self.fold_manager.folds), 10)

        # This one will trigger pruning
        self.fold_manager.create_fold("final filler")

        self.assertEqual(len(self.fold_manager.folds), 10)

        # Verify the important fold is still retrievable
        retrieved_fold = self.fold_manager.retrieve_fold(important_fold.id)
        self.assertIsNotNone(retrieved_fold)
        self.assertEqual(retrieved_fold.content, "critical memory")

    def test_placeholder_consolidation(self):
        """Tests the placeholder consolidate method."""
        self.fold_manager.create_fold("some content")
        result = self.fold_manager.consolidate()
        self.assertTrue(result["consolidated"])
        self.assertEqual(result["fold_count"], 1)

class TestEpisodicMemory(unittest.TestCase):

    def setUp(self):
        """Set up a new FoldManager for each test."""
        self.fold_manager = FoldManager()

    def test_create_fold_with_causal_link(self):
        """Tests creating a fold that is causally linked to another."""
        event1 = self.fold_manager.create_fold("Event 1: The beginning.")
        event2 = self.fold_manager.create_fold("Event 2: The consequence.", causal_chain=[event1.id])

        self.assertIn(event1.id, event2.causal_chain)

    def test_retrieve_simple_causal_chain(self):
        """Tests retrieving a direct causal chain of one preceding event."""
        event1 = self.fold_manager.create_fold("Cause")
        event2 = self.fold_manager.create_fold("Effect", causal_chain=[event1.id])

        chain = self.fold_manager.get_causal_chain(event2.id)

        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0].id, event1.id)
        self.assertEqual(chain[0].content, "Cause")

    def test_retrieve_multi_step_event_timeline(self):
        """Tests retrieving a multi-step causal chain representing a timeline."""
        step1 = self.fold_manager.create_fold("Step 1: First, this happened.")
        step2 = self.fold_manager.create_fold("Step 2: Then, this was the result.", causal_chain=[step1.id])
        step3 = self.fold_manager.create_fold("Step 3: Finally, this concluded it.", causal_chain=[step2.id])

        # Retrieve the chain for Step 3. It should only contain Step 2.
        chain_step3 = self.fold_manager.get_causal_chain(step3.id)
        self.assertEqual(len(chain_step3), 1)
        self.assertEqual(chain_step3[0].id, step2.id)

        # To get the full story, we would need to traverse the chain
        full_timeline = []
        current_fold = step3
        while current_fold:
            full_timeline.insert(0, current_fold)
            chain = self.fold_manager.get_causal_chain(current_fold.id)
            current_fold = chain[0] if chain else None

        self.assertEqual(len(full_timeline), 3)
        self.assertEqual(full_timeline[0].id, step1.id)
        self.assertEqual(full_timeline[1].id, step2.id)
        self.assertEqual(full_timeline[2].id, step3.id)

    def test_retrieve_causal_chain_for_non_existent_fold(self):
        """Tests that retrieving a chain for a non-existent fold returns an empty list."""
        chain = self.fold_manager.get_causal_chain("non_existent_id")
        self.assertEqual(chain, [])

    def test_retrieve_causal_chain_with_missing_link(self):
        """Tests retrieving a chain where one of the linked folds has been pruned."""
        event1 = self.fold_manager.create_fold("This fold will be pruned.")
        event2 = self.fold_manager.create_fold("This fold links to the pruned one.", causal_chain=[event1.id])

        # Manually remove the first event to simulate it being pruned
        del self.fold_manager.folds[event1.id]

        chain = self.fold_manager.get_causal_chain(event2.id)

        # The chain should be empty as the linked fold does not exist in the manager
        self.assertEqual(len(chain), 0)

class TestSemanticMemory(unittest.TestCase):

    def setUp(self):
        """Set up a new SymbolAwareTieredMemory for each test."""
        self.semantic_memory = SymbolAwareTieredMemory()

    def test_store_and_retrieve_concept(self):
        """Tests storing a concept with symbols and retrieving it."""
        concept_id = "concept_apple"
        data = {"type": "fruit", "color": "red", "taste": "sweet"}
        symbols = ["fruit", "food", "apple"]

        self.semantic_memory.store(concept_id, data, symbols=symbols)

        retrieved_data = self.semantic_memory.retrieve(concept_id)
        self.assertEqual(retrieved_data, data)

        # Verify metadata was stored
        self.assertEqual(self.semantic_memory.metadata[concept_id]["symbols"], symbols)

    def test_store_in_different_tiers(self):
        """Tests storing concepts in different memory tiers."""
        hot_id = "concept_hot"
        warm_id = "concept_warm"
        cold_id = "concept_cold"

        self.semantic_memory.store(hot_id, "hot data", tier=MemoryTier.HOT)
        self.semantic_memory.store(warm_id, "warm data", tier=MemoryTier.WARM)
        self.semantic_memory.store(cold_id, "cold data", tier=MemoryTier.COLD)

        self.assertIn(hot_id, self.semantic_memory.cache.tiers[MemoryTier.HOT])
        self.assertIn(warm_id, self.semantic_memory.cache.tiers[MemoryTier.WARM])
        self.assertIn(cold_id, self.semantic_memory.cache.tiers[MemoryTier.COLD])

    def test_retrieve_dream_flagged_memories(self):
        """Tests the retrieval of memories flagged as 'dreams'."""
        self.semantic_memory.store("dream1", "This is a dream.", is_dream=True)
        self.semantic_memory.store("normal1", "This is not a dream.")
        self.semantic_memory.store("dream2", "This is another dream.", is_dream=True)

        dream_memories = self.semantic_memory.get_dream_flagged()

        self.assertEqual(len(dream_memories), 2)
        dream_ids = {d["id"] for d in dream_memories}
        self.assertIn("dream1", dream_ids)
        self.assertIn("dream2", dream_ids)
        self.assertNotIn("normal1", dream_ids)

    def test_retrieval_from_any_tier(self):
        """Tests that a concept can be retrieved regardless of its storage tier."""
        hot_id = "concept_hot"
        cold_id = "concept_cold"

        self.semantic_memory.store(hot_id, "hot data", tier=MemoryTier.HOT)
        self.semantic_memory.store(cold_id, "cold data", tier=MemoryTier.COLD)

        self.assertEqual(self.semantic_memory.retrieve(hot_id), "hot data")
        self.assertEqual(self.semantic_memory.retrieve(cold_id), "cold data")

if __name__ == '__main__':
    unittest.main()
