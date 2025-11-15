"""
Comprehensive tests for async orchestrator timeout management.

Tests per-stage timeouts, cascading validation, graceful degradation,
and pipeline halt behavior for production stability.
"""

import pytest
import asyncio
from lukhas.orchestration.timeouts import (
    TimeoutManager,
    TimeoutConfig,
    TimeoutResult
)


class TestTimeoutManager:
    """Comprehensive timeout management tests"""

    @pytest.fixture
    def timeout_manager(self):
        config = TimeoutConfig(
            memory_retrieval_s=1.0,
            matriz_processing_s=2.0,
            llm_generation_s=3.0,
            guardian_check_s=0.5,
            total_pipeline_s=10.0
        )
        return TimeoutManager(config=config)

    @pytest.mark.asyncio
    async def test_successful_execution_within_timeout(self, timeout_manager):
        """Fast execution completes successfully"""
        async def fast_coro():
            await asyncio.sleep(0.1)
            return "success"

        result = await timeout_manager.run_with_timeout(
            coro=fast_coro(),
            stage="test_stage",
            timeout_s=1.0
        )

        assert result.success == True
        assert result.result == "success"
        assert result.timed_out == False
        assert result.duration_s < 0.2

    @pytest.mark.asyncio
    async def test_timeout_triggers_correctly(self, timeout_manager):
        """Slow execution triggers timeout"""
        async def slow_coro():
            await asyncio.sleep(5.0)  # Exceeds timeout
            return "should not return"

        result = await timeout_manager.run_with_timeout(
            coro=slow_coro(),
            stage="slow_stage",
            timeout_s=0.5  # Short timeout
        )

        assert result.success == False
        assert result.timed_out == True
        assert result.result is None
        assert result.duration_s >= 0.5

    @pytest.mark.asyncio
    async def test_fallback_result_on_timeout(self, timeout_manager):
        """Fallback result returned on timeout"""
        async def slow_coro():
            await asyncio.sleep(2.0)
            return "slow"

        result = await timeout_manager.run_with_timeout(
            coro=slow_coro(),
            stage="fallback_test",
            timeout_s=0.3,
            fallback_result={"fallback": "partial data"}
        )

        assert result.timed_out == True
        assert result.partial_result == {"fallback": "partial data"}

    @pytest.mark.asyncio
    async def test_pipeline_execution(self, timeout_manager):
        """Full pipeline runs with per-stage timeouts"""
        async def memory_retrieval():
            await asyncio.sleep(0.2)
            return {"memory": "data"}

        async def matriz_processing():
            await asyncio.sleep(0.3)
            return {"matriz": "result"}

        stages = {
            "memory_retrieval": memory_retrieval(),
            "matriz_processing": matriz_processing()
        }

        results = await timeout_manager.run_pipeline(stages)

        assert len(results) == 2
        assert results["memory_retrieval"].success == True
        assert results["matriz_processing"].success == True

    @pytest.mark.asyncio
    async def test_pipeline_halts_on_critical_timeout(self, timeout_manager):
        """Pipeline halts if critical stage times out"""
        async def memory_slow():
            await asyncio.sleep(5.0)
            return "slow"

        async def matriz_after():
            return "should not execute"

        stages = {
            "memory_retrieval": memory_slow(),
            "matriz_processing": matriz_after()
        }

        stage_timeouts = {
            "memory_retrieval": 0.5,  # Will timeout
            "matriz_processing": 2.0
        }

        results = await timeout_manager.run_pipeline(stages, stage_timeouts)

        # Memory timed out
        assert results["memory_retrieval"].timed_out == True

        # MATRIZ should not have executed (critical halt)
        assert "matriz_processing" not in results

    def test_cascading_timeout_validation(self):
        """Config validation catches invalid cascading timeouts"""
        # Invalid: total < sum of stages
        with pytest.raises(ValueError, match="must exceed sum"):
            bad_config = TimeoutConfig(
                memory_retrieval_s=5.0,
                matriz_processing_s=5.0,
                llm_generation_s=5.0,
                guardian_check_s=5.0,
                total_pipeline_s=10.0  # Too short!
            )
            bad_config.validate()

    @pytest.mark.asyncio
    async def test_exception_handling(self, timeout_manager):
        """Exceptions handled gracefully (not timeouts)"""
        async def failing_coro():
            raise ValueError("Intentional failure")

        result = await timeout_manager.run_with_timeout(
            coro=failing_coro(),
            stage="error_test",
            timeout_s=1.0
        )

        assert result.success == False
        assert result.timed_out == False  # Not a timeout, an exception

    def test_valid_timeout_config(self):
        """Valid config passes validation"""
        valid_config = TimeoutConfig(
            memory_retrieval_s=1.0,
            matriz_processing_s=5.0,
            llm_generation_s=10.0,
            guardian_check_s=0.5,
            total_pipeline_s=20.0  # Exceeds sum (16.5s)
        )
        # Should not raise
        valid_config.validate()

    @pytest.mark.asyncio
    async def test_custom_stage_timeouts(self, timeout_manager):
        """Custom timeouts override defaults"""
        async def custom_stage():
            await asyncio.sleep(0.8)
            return "custom"

        stages = {
            "custom_stage": custom_stage()
        }

        custom_timeouts = {
            "custom_stage": 1.0  # Custom timeout
        }

        results = await timeout_manager.run_pipeline(stages, custom_timeouts)

        assert results["custom_stage"].success == True
        assert results["custom_stage"].duration_s < 1.0

    @pytest.mark.asyncio
    async def test_default_timeout_fallback(self, timeout_manager):
        """Unknown stages use default 5s timeout"""
        async def unknown_stage():
            await asyncio.sleep(0.2)
            return "unknown"

        stages = {
            "unknown_stage": unknown_stage()
        }

        results = await timeout_manager.run_pipeline(stages)

        # Should complete with default timeout
        assert results["unknown_stage"].success == True

    @pytest.mark.asyncio
    async def test_guardian_critical_stage_halt(self, timeout_manager):
        """Guardian timeout halts pipeline (critical stage)"""
        async def guardian_slow():
            await asyncio.sleep(5.0)
            return "slow"

        async def llm_after():
            return "should not execute"

        stages = {
            "guardian_check": guardian_slow(),
            "llm_generation": llm_after()
        }

        stage_timeouts = {
            "guardian_check": 0.3,  # Will timeout
            "llm_generation": 10.0
        }

        results = await timeout_manager.run_pipeline(stages, stage_timeouts)

        # Guardian timed out
        assert results["guardian_check"].timed_out == True

        # LLM should not have executed (critical halt)
        assert "llm_generation" not in results

    @pytest.mark.asyncio
    async def test_non_critical_timeout_continues(self, timeout_manager):
        """Non-critical stage timeout doesn't halt pipeline"""
        async def llm_slow():
            await asyncio.sleep(5.0)
            return "slow"

        async def guardian_after():
            await asyncio.sleep(0.1)
            return "guardian"

        stages = {
            "llm_generation": llm_slow(),
            "guardian_check": guardian_after()
        }

        stage_timeouts = {
            "llm_generation": 0.3,  # Will timeout (non-critical)
            "guardian_check": 1.0
        }

        results = await timeout_manager.run_pipeline(stages, stage_timeouts)

        # LLM timed out
        assert results["llm_generation"].timed_out == True

        # Guardian should still execute (non-critical timeout)
        assert results["guardian_check"].success == True

    @pytest.mark.asyncio
    async def test_timeout_duration_accurate(self, timeout_manager):
        """Timeout duration recorded accurately"""
        async def timed_coro():
            await asyncio.sleep(0.5)
            return "result"

        result = await timeout_manager.run_with_timeout(
            coro=timed_coro(),
            stage="duration_test",
            timeout_s=1.0
        )

        # Duration should be close to 0.5s
        assert 0.4 <= result.duration_s <= 0.6

    @pytest.mark.asyncio
    async def test_multiple_stages_timeout_metrics(self, timeout_manager):
        """Multiple stages record individual metrics"""
        async def stage1():
            await asyncio.sleep(0.1)
            return "stage1"

        async def stage2():
            await asyncio.sleep(0.2)
            return "stage2"

        async def stage3():
            await asyncio.sleep(0.15)
            return "stage3"

        stages = {
            "stage1": stage1(),
            "stage2": stage2(),
            "stage3": stage3()
        }

        results = await timeout_manager.run_pipeline(stages)

        # All should succeed
        assert all(r.success for r in results.values())

        # Each should have recorded duration
        assert results["stage1"].duration_s < 0.2
        assert results["stage2"].duration_s < 0.3
        assert results["stage3"].duration_s < 0.25
