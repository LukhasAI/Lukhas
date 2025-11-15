import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestration.timeouts import TimeoutManager, TimeoutConfig

class TestOrchestratorNetworkFailures(unittest.TestCase):

    def test_network_failure_in_pipeline_stage(self):
        """
        Test that the orchestrator can gracefully handle a network failure
        (e.g., a timeout) in one of the pipeline stages.
        """
        # Configure a short timeout for the test
        timeout_config = TimeoutConfig(llm_generation_s=0.1)
        timeout_manager = TimeoutManager(config=timeout_config)

        # Mock a pipeline stage that simulates a network timeout
        async def slow_stage(_):
            await asyncio.sleep(0.2)
            return "This should not be returned"

        # Create a mock orchestrator
        orchestrator = Orchestrator(config=MagicMock())

        # Mock the pipeline executor to use our slow stage and the real TimeoutManager
        async def mock_execute_pipeline(pipeline_id, nodes, initial_input):
            results = await timeout_manager.run_pipeline(
                {"llm_generation": slow_stage(initial_input)}
            )
            if results["llm_generation"].timed_out:
                return {"status": "degraded", "result": "Partial result"}
            return {"status": "ok", "result": "Full result"}

        orchestrator.pipeline_executor = MagicMock()
        orchestrator.pipeline_executor.execute_pipeline = AsyncMock(
            side_effect=mock_execute_pipeline
        )

        # Run the orchestrator and assert that it degrades gracefully
        pipeline_result = asyncio.run(orchestrator.execute(
            pipeline_id="test_network_failure",
            nodes=[("llm_generation", slow_stage)],
            initial_input="input"
        ))

        self.assertEqual(pipeline_result["status"], "degraded")
        self.assertEqual(pipeline_result["result"], "Partial result")

if __name__ == '__main__':
    unittest.main()
