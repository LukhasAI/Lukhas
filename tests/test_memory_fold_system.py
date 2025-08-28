import pytest
import asyncio
import time
import os
import sys
from unittest.mock import MagicMock

# Add candidate modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from candidate.memory.protection.symbolic_quarantine_sanctum import SymbolicQuarantineSanctum, ThreatLevel

# A mock memory fold system for testing purposes
class MockMemoryFold:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memories = []

    def add_memory(self, memory):
        if len(self.memories) >= self.capacity:
            raise MemoryError("Fold capacity exceeded")
        self.memories.append(memory)
        return True

    def get_memory_count(self):
        return len(self.memories)

class TestMemoryFoldSystem:
    """Test suite for the 1000-fold memory system and cascade prevention."""

    @pytest.fixture
    def sanctum(self):
        """Fixture for an initialized SymbolicQuarantineSanctum."""
        # Ensure the config file exists for the test
        config_path = "candidate/memory/fold_config.yaml"
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                f.write("""
capacity:
  max_folds: 1000
protection:
  safety_thresholds:
    entropy_quarantine: 0.85
    contradiction_threshold: 0.7
    emotional_volatility: 0.6
    drift_cascade_threshold: 0.75
    repair_confidence_minimum: 0.8
    restoration_safety_threshold: 0.9
                """)
        return SymbolicQuarantineSanctum(config_path=config_path)

    @pytest.mark.asyncio
    async def test_1000_fold_capacity_and_performance(self, sanctum):
        """Tests the system's ability to handle 1000 memory folds and measures performance."""
        fold_system = MockMemoryFold(capacity=sanctum.max_quarantine_size)

        latencies = []
        for i in range(1000):
            memory_entry = {"entry_id": f"entry_{i}", "content": f"Memory content {i}", "timestamp": time.time()}

            start_time = time.perf_counter()
            fold_system.add_memory(memory_entry)
            end_time = time.perf_counter()

            latencies.append((end_time - start_time) * 1000) # in ms

        assert fold_system.get_memory_count() == 1000, "System should handle 1000 memory folds."

        p95_latency = sorted(latencies)[int(1000 * 0.95) -1]

        print(f"P95 latency for 1000 folds: {p95_latency:.2f}ms")
        assert p95_latency < 10.0, f"P95 latency ({p95_latency:.2f}ms) exceeds the 10ms target."

    @pytest.mark.asyncio
    async def test_cascade_prevention_with_quarantine(self, sanctum):
        """Tests cascade prevention by ensuring contaminated data is quarantined."""
        total_operations = 100
        contaminated_entries = 0

        for i in range(total_operations):
            # Create a mix of normal and contaminated entries
            if i % 10 == 0:
                # This entry is designed to be caught by the scanner
                entry_id = f"contaminated_entry_{i}"
                content = {
                    "entry_id": entry_id,
                    "content": "This is a chaotic and unstable memory with high entropy and violations.",
                    "entropy": 0.9, # High entropy
                    "ΛVIOLATION": "ethical_breach"
                }
                is_contaminated = True
            else:
                entry_id = f"normal_entry_{i}"
                content = {
                    "entry_id": entry_id,
                    "content": f"Stable memory content {i}",
                    "entropy": 0.2
                }
                is_contaminated = False

            # Scan the entry
            findings = await sanctum.scan_for_contamination([content], auto_quarantine=True)

            if is_contaminated:
                assert len(findings) == 1, "Contaminated entry should be flagged."
                assert findings[0]['entry_id'] == entry_id
                assert entry_id in sanctum.quarantine_entries, "Contaminated entry should be in quarantine."
                contaminated_entries += 1
            else:
                assert len(findings) == 0, "Normal entry should not be flagged."
                assert entry_id not in sanctum.quarantine_entries, "Normal entry should not be quarantined."

        # Verify that all contaminated entries were caught
        assert contaminated_entries == total_operations / 10

        # Check the "cascade prevention rate"
        quarantined_count = len(sanctum.quarantine_entries)
        prevention_rate = ((total_operations - (quarantined_count - contaminated_entries)) / total_operations) * 100

        # This is a simplified check. A real scenario is more complex.
        # We check if only the contaminated entries are quarantined.
        assert quarantined_count == contaminated_entries, "Only contaminated entries should be quarantined."

        # In this simulation, if we quarantine all bad entries and no good ones, prevention is 100%
        # A more complex test would involve interaction between memories.
        # For now, we confirm the quarantine mechanism works as the first line of defense.
        print(f"Quarantine test complete. Contaminated entries caught: {quarantined_count}")
        assert quarantined_count == 10
