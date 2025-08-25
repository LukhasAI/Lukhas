import pytest
import asyncio
import time
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from candidate.memory.fold_system.memory_fold import HybridMemoryFold

@pytest.mark.asyncio
async def test_memory_fold_in_performance():
    """
    Tests the performance of folding in a large number of memories.
    """
    memory = HybridMemoryFold()
    num_items = 1000

    start_time = time.time()

    for i in range(num_items):
        await memory.fold_in(
            data={"content": f"This is memory item {i}"},
            tags=[f"item_{i}", "performance_test"]
        )

    end_time = time.time()

    duration = end_time - start_time

    # Assert that the operation completes within a reasonable time.
    # This is a very generous limit and should be adjusted based on
    # the actual performance of the system.
    assert duration < 5.0, f"Folding in {num_items} items took {duration:.2f} seconds, which is too slow."
