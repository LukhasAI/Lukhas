import asyncio
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.modules["metrics"] = MagicMock()
sys.modules["core.orchestration.consensus_arbitrator"] = MagicMock()
sys.modules["core.orchestration.meta_controller"] = MagicMock()
sys.modules["core.orchestration.otel"] = MagicMock()

from core.orchestration.async_orchestrator import (
    AsyncOrchestrator,
    CancellationToken,
    StageConfig,
)

# Mock ICognitiveNode
class MockCognitiveNode:
    def __init__(self, name, process_func=None):
        self.name = name
        self.process_func = process_func

    async def process(self, context):
        if self.process_func:
            return await self.process_func(context)
        return {"status": "success", "node": self.name}

@pytest.fixture
def orchestrator():
    with patch("core.orchestration.async_orchestrator.MetaController") as mock_meta_controller, \
         patch("core.orchestration.async_orchestrator.choose") as mock_choose:
        mock_meta_controller.return_value.step.return_value = False
        mock_choose.return_value = (MagicMock(), "rationale")
        yield AsyncOrchestrator()

class TestAsyncOrchestrator:
    async def test_configure_stages(self, orchestrator):
        stages_config = [
            {"name": "stage1", "timeout_ms": 100},
            {"name": "stage2", "max_retries": 3},
        ]
        orchestrator.configure_stages(stages_config)

        assert len(orchestrator.stages) == 2
        assert orchestrator.stages[0].name == "stage1"
        assert orchestrator.stages[0].timeout_ms == 100
        assert orchestrator.stages[1].name == "stage2"
        assert orchestrator.stages[1].max_retries == 3

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_single_stage_success(self, mock_resolve, orchestrator):
        mock_node = MockCognitiveNode("stage1")
        mock_resolve.return_value = mock_node

        stages_config = [{"name": "stage1"}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query({"input": "test"})

        assert result.success is True
        assert result.output["status"] == "success"
        assert result.output["node"] == "stage1"

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_multi_stage_success(self, mock_resolve, orchestrator):
        async def stage1_process(context):
            return {"status": "success", "node": "stage1", "output": "from stage1"}

        async def stage2_process(context):
            return {"status": "success", "node": "stage2", "input": context.get("output")}

        mock_node1 = MockCognitiveNode("stage1", process_func=stage1_process)
        mock_node2 = MockCognitiveNode("stage2", process_func=stage2_process)
        mock_resolve.side_effect = [mock_node1, mock_node2]

        stages_config = [{"name": "stage1"}, {"name": "stage2"}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query({"input": "test"})

        assert result.success is True
        assert result.output["status"] == "success"
        assert result.output["node"] == "stage2"
        assert result.output["input"] == "from stage1"

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_stage_failure_with_retry(self, mock_resolve, orchestrator):
        retryable_error = Exception("transient error")
        retryable_error.retryable = True
        process_func = MagicMock()
        process_func.side_effect = [retryable_error, {"status": "success"}]

        mock_node = MockCognitiveNode("stage1", process_func=AsyncMock(side_effect=process_func.side_effect))
        mock_resolve.return_value = mock_node

        stages_config = [{"name": "stage1", "max_retries": 2}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query({"input": "test"})

        assert result.success is True
        assert result.output["status"] == "success"
        assert mock_node.process_func.call_count == 2

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_stage_failure_with_fallback(self, mock_resolve, orchestrator):
        async def failing_process(context):
            raise Exception("permanent error")

        mock_failing_node = MockCognitiveNode("stage1", process_func=failing_process)
        mock_fallback_node = MockCognitiveNode("fallback_node")
        mock_resolve.side_effect = [mock_failing_node, mock_fallback_node]

        stages_config = [{
            "name": "stage1",
            "max_retries": 1,
            "fallback_nodes": ["fallback_node"]
        }]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query({"input": "test"})

        assert result.success is True
        assert result.output["status"] == "success"
        assert result.output["node"] == "fallback_node"

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_stage_timeout(self, mock_resolve, orchestrator):
        async def slow_process(context):
            await asyncio.sleep(0.2)
            return {"status": "success"}

        mock_slow_node = MockCognitiveNode("stage1", process_func=slow_process)
        mock_resolve.return_value = mock_slow_node

        stages_config = [{"name": "stage1", "timeout_ms": 100}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query({"input": "test"})

        assert result.success is True
        assert result.output["action"] == "timeout"

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_parallel_success(self, mock_resolve, orchestrator):
        orchestrator.parallel_enabled = True

        async def stage_process(context):
            return {"status": "success", "node": context["stage_name"]}

        mock_node1 = MockCognitiveNode("stage1", process_func=lambda ctx: stage_process({**ctx, "stage_name": "stage1"}))
        mock_node2 = MockCognitiveNode("stage2", process_func=lambda ctx: stage_process({**ctx, "stage_name": "stage2"}))
        mock_resolve.side_effect = [mock_node1, mock_node2]

        stages_config = [{"name": "stage1"}, {"name": "stage2"}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query_parallel({"input": "test"})

        assert result.success is True
        assert len(result.stage_results) == 2

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_query_parallel_with_failure(self, mock_resolve, orchestrator):
        orchestrator.parallel_enabled = True

        async def failing_process(context):
            raise Exception("permanent error")

        mock_node1 = MockCognitiveNode("stage1")
        mock_node2 = MockCognitiveNode("stage2", process_func=failing_process)
        mock_resolve.side_effect = [mock_node1, mock_node2]

        stages_config = [{"name": "stage1"}, {"name": "stage2"}]
        orchestrator.configure_stages(stages_config)

        result = await orchestrator.process_query_parallel({"input": "test"})

        assert result.success is True
        assert len(result.stage_results) == 2
        assert result.stage_results[1]["status"] == "error"

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_process_adaptive(self, mock_resolve, orchestrator):
        orchestrator.parallel_enabled = True

        mock_node1 = MockCognitiveNode("stage1")
        mock_node2 = MockCognitiveNode("stage2")
        mock_resolve.side_effect = [mock_node1, mock_node2, mock_node1, mock_node2]

        stages_config = [{"name": "stage1"}, {"name": "stage2"}]
        orchestrator.configure_stages(stages_config)

        # Test sequential mode for short query
        with patch.object(orchestrator, "process_query") as mock_process_query:
            await orchestrator.process_adaptive({"query": "short"})
            mock_process_query.assert_called_once()

        # Test parallel mode for long query
        with patch.object(orchestrator, "process_query_parallel") as mock_process_query_parallel:
            long_query = "a" * 101
            await orchestrator.process_adaptive({"query": long_query})
            mock_process_query_parallel.assert_called_once()

    @patch("core.orchestration.async_orchestrator.resolve")
    async def test_pipeline_cancellation(self, mock_resolve, orchestrator):
        async def long_running_process(context):
            await asyncio.sleep(1)
            return {"status": "success"}

        mock_node = MockCognitiveNode("stage1", process_func=long_running_process)
        mock_resolve.return_value = mock_node

        stages_config = [{"name": "stage1"}]
        orchestrator.configure_stages(stages_config)

        cancellation_token = CancellationToken()
        task = asyncio.create_task(orchestrator.process_query({}, cancellation=cancellation_token))

        await asyncio.sleep(0.1)
        cancellation_token.cancel("test cancellation")

        result = await task

        assert result.success is False
        assert result.escalation_reason == "cancelled"
