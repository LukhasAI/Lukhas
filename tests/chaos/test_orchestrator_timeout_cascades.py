import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestration.timeouts import TimeoutManager, TimeoutConfig

class TestOrchestratorTimeoutCascades(unittest.TestCase):

    def test_timeout_cascade_prevention_config_validation(self):
        """
        Test that the TimeoutConfig validation prevents total pipeline timeouts
        from being less than or equal to the sum of stage timeouts.
        """
        with self.assertRaisesRegex(ValueError, "must exceed sum of stage timeouts"):
            TimeoutConfig(
                memory_retrieval_s=1.0,
                matriz_processing_s=5.0,
                llm_generation_s=10.0,
                guardian_check_s=0.5,
                total_pipeline_s=16.0  # 16s <= 16.5s, should fail
            ).validate()

        # This should be valid
        TimeoutConfig(
            memory_retrieval_s=1.0,
            matriz_processing_s=5.0,
            llm_generation_s=10.0,
            guardian_check_s=0.5,
            total_pipeline_s=20.0  # 20s > 16.5s, should pass
        ).validate()

    def test_critical_stage_timeout_halts_pipeline(self):
        """
        Test that if a critical stage times out, the pipeline halts and does not
        execute subsequent stages.
        """
        # Configure a short timeout for the critical stage
        timeout_config = TimeoutConfig(
            memory_retrieval_s=0.1,
            llm_generation_s=10.0, # Make this long so it wouldn't time out
        )
        timeout_manager = TimeoutManager(config=timeout_config)

        # Mock pipeline stages
        async def slow_critical_stage(_):
            await asyncio.sleep(0.2)
            return "should_not_return"

        # This mock will track if it has been called and awaited
        mock_next_stage = AsyncMock(return_value="next_stage_result")

        # Create a mock orchestrator
        orchestrator = Orchestrator(config=MagicMock())

        # Mock the pipeline executor to run the stages.
        # The `run_pipeline` method eagerly creates the coroutines when the dictionary
        # is passed, so `mock_next_stage` WILL be called. However, it should not be
        # awaited if the critical stage before it times out.
        async def mock_execute_pipeline(pipeline_id, nodes, initial_input):
            results = await timeout_manager.run_pipeline({
                "memory_retrieval": slow_critical_stage(initial_input),
                "llm_generation": mock_next_stage(initial_input),
            })
            return results

        orchestrator.pipeline_executor = MagicMock()
        orchestrator.pipeline_executor.execute_pipeline = AsyncMock(
            side_effect=mock_execute_pipeline
        )

        # Run the orchestrator
        pipeline_results = asyncio.run(orchestrator.execute(
            pipeline_id="test_critical_stage_timeout",
            nodes=[
                ("memory_retrieval", slow_critical_stage),
                ("llm_generation", mock_next_stage)
            ],
            initial_input="input"
        ))

        # Assert that the critical stage timed out
        self.assertTrue(pipeline_results["memory_retrieval"].timed_out)

        # Assert that the subsequent stage's coroutine was created but NOT awaited
        mock_next_stage.assert_called_once()
        mock_next_stage.assert_not_awaited()

        # Assert that there is no result for the subsequent stage because the loop broke
        self.assertNotIn("llm_generation", pipeline_results)

if __name__ == '__main__':
    unittest.main()
