import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestration.timeouts import TimeoutManager, TimeoutConfig

class TestOrchestratorResourceLimits(unittest.TestCase):

    def test_memory_exhaustion_in_pipeline_stage(self):
        """
        Test that the orchestrator can gracefully handle a MemoryError
        in one of the pipeline stages, representing resource exhaustion.
        """
        # No special timeout config needed for this test
        timeout_manager = TimeoutManager()

        # Mock a pipeline stage that simulates a MemoryError
        async def memory_hog_stage(_):
            raise MemoryError("Simulated memory exhaustion")

        # Create a mock orchestrator
        orchestrator = Orchestrator(config=MagicMock())

        # Mock the pipeline executor to use our memory hog stage
        async def mock_execute_pipeline(pipeline_id, nodes, initial_input):
            # The `run_with_timeout` method in TimeoutManager has a generic
            # `except Exception` block that should catch the MemoryError.
            results = await timeout_manager.run_pipeline(
                {"memory_hog": memory_hog_stage(initial_input)}
            )
            # Check the result to see how it was handled
            return results

        orchestrator.pipeline_executor = MagicMock()
        orchestrator.pipeline_executor.execute_pipeline = AsyncMock(
            side_effect=mock_execute_pipeline
        )

        # Run the orchestrator and assert that it handles the error
        pipeline_result = asyncio.run(orchestrator.execute(
            pipeline_id="test_memory_exhaustion",
            nodes=[("memory_hog", memory_hog_stage)],
            initial_input="input"
        ))

        # Assert that the stage failed but did not time out
        stage_result = pipeline_result["memory_hog"]
        self.assertFalse(stage_result.success)
        self.assertFalse(stage_result.timed_out)
        self.assertIsNone(stage_result.result)

if __name__ == '__main__':
    unittest.main()
