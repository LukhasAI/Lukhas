import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestration.timeouts import TimeoutManager

class TestOrchestratorPartialFailures(unittest.TestCase):

    def test_partial_failure_in_pipeline(self):
        """
        Test that if a non-critical stage fails, the orchestrator continues
        processing and returns the partial results from the successful stages.
        """
        timeout_manager = TimeoutManager()

        # Mock a successful stage
        async def successful_stage(_):
            return "success_result"

        # Mock a failing stage
        async def failing_stage(_):
            raise ValueError("Simulated stage failure")

        orchestrator = Orchestrator(config=MagicMock())

        # Mock the pipeline executor
        async def mock_execute_pipeline(pipeline_id, nodes, initial_input):
            results = await timeout_manager.run_pipeline({
                "first_stage": successful_stage(initial_input),
                "second_stage": failing_stage(initial_input),
            })
            return results

        orchestrator.pipeline_executor = MagicMock()
        orchestrator.pipeline_executor.execute_pipeline = AsyncMock(
            side_effect=mock_execute_pipeline
        )

        # Run the orchestrator
        pipeline_results = asyncio.run(orchestrator.execute(
            pipeline_id="test_partial_failure",
            nodes=[
                ("first_stage", successful_stage),
                ("second_stage", failing_stage)
            ],
            initial_input="input"
        ))

        # Assert that the first stage succeeded
        first_stage_result = pipeline_results["first_stage"]
        self.assertTrue(first_stage_result.success)
        self.assertEqual(first_stage_result.result, "success_result")

        # Assert that the second stage failed
        second_stage_result = pipeline_results["second_stage"]
        self.assertFalse(second_stage_result.success)
        self.assertIsNone(second_stage_result.result)

if __name__ == '__main__':
    unittest.main()
