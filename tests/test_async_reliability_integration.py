"""
Integration tests for LUKHAS async reliability improvements.

Tests the complete async task lifecycle for consciousness architecture,
validating proper cleanup, monitoring, and production-grade reliability.
"""

import asyncio
import pytest
import time
import logging
from unittest.mock import patch, AsyncMock

# Test imports with fallbacks
try:
    from lukhas.async_manager import (
        ConsciousnessTaskManager,
        TaskPriority,
        shutdown_all_managers
    )
    from lukhas.async_utils import (
        consciousness_context,
        run_consciousness_task,
        run_guardian_task,
        run_background_task
    )
except ImportError:
    # Skip these tests if async manager not available
    pytest.skip("Async manager not available", allow_module_level=True)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestConsciousnessAsyncReliability:
    """Test consciousness system async reliability."""
    
    @pytest.mark.asyncio
    async def test_awareness_monitoring_async_flow(self):
        """Test awareness monitoring system async task management."""
        
        # Simulate awareness monitoring tasks
        monitoring_events = []
        
        async def awareness_monitoring_loop():
            """Simulate awareness monitoring loop."""
            for i in range(3):
                await asyncio.sleep(0.01)
                monitoring_events.append(f"awareness_check_{i}")
            return "monitoring_complete"
        
        async def pattern_detection_loop():
            """Simulate pattern detection."""
            for i in range(2):
                await asyncio.sleep(0.015)
                monitoring_events.append(f"pattern_detected_{i}")
            return "pattern_detection_complete"
        
        # Use consciousness context for proper task management
        async with consciousness_context("awareness_monitoring") as ctx:
            # Create managed consciousness tasks
            awareness_task = ctx.create_task(
                awareness_monitoring_loop(),
                name="awareness_monitoring_loop",
                priority=TaskPriority.CRITICAL,
                description="Monitor consciousness awareness levels"
            )
            
            pattern_task = ctx.create_task(
                pattern_detection_loop(),
                name="pattern_detection_loop", 
                priority=TaskPriority.HIGH,
                description="Detect awareness patterns"
            )
            
            # Wait for completion
            await asyncio.gather(awareness_task, pattern_task)
        
        # Verify all events occurred
        assert len(monitoring_events) == 5
        assert any("awareness_check" in event for event in monitoring_events)
        assert any("pattern_detected" in event for event in monitoring_events)
    
    @pytest.mark.asyncio
    async def test_memory_fold_processing_reliability(self):
        """Test memory fold processing with cascade prevention."""
        
        cascade_events = []
        
        async def memory_fold_worker():
            """Simulate memory fold processing."""
            await asyncio.sleep(0.02)
            cascade_events.append("fold_processed")
            
            # Simulate cascade prevention check
            if len(cascade_events) > 1:
                cascade_events.append("cascade_prevented")
            
            return {"fold_id": "test_fold", "status": "processed"}
        
        async def distributed_memory_sync():
            """Simulate distributed memory synchronization."""
            await asyncio.sleep(0.01)
            cascade_events.append("memory_synced")
            return {"sync_status": "complete"}
        
        # Create consciousness tasks for memory processing
        fold_task = await run_consciousness_task(
            memory_fold_worker(),
            name="memory_fold_processing",
            priority=TaskPriority.CRITICAL,
            description="Process memory fold with cascade prevention",
            consciousness_context="memory_processing"
        )
        
        sync_task = await run_consciousness_task(
            distributed_memory_sync(),
            name="distributed_memory_sync",
            priority=TaskPriority.HIGH,
            description="Synchronize distributed memory",
            consciousness_context="memory_processing"
        )
        
        # Wait for completion
        fold_result = await fold_task
        sync_result = await sync_task
        
        assert fold_result["status"] == "processed"
        assert sync_result["sync_status"] == "complete"
        assert "fold_processed" in cascade_events
        assert "memory_synced" in cascade_events


@pytest.mark.integration  
class TestGuardianAsyncReliability:
    """Test Guardian system async reliability."""
    
    @pytest.mark.asyncio
    async def test_guardian_ethical_evaluation_flow(self):
        """Test Guardian ethical evaluation async flow."""
        
        evaluation_results = []
        
        async def ethical_drift_monitor():
            """Simulate ethical drift monitoring."""
            await asyncio.sleep(0.01)
            drift_score = 0.08  # Within threshold of 0.15
            evaluation_results.append({
                "type": "drift_monitor",
                "drift_score": drift_score,
                "status": "within_threshold"
            })
            return drift_score
        
        async def constitutional_enforcement():
            """Simulate constitutional AI enforcement."""
            await asyncio.sleep(0.015)
            evaluation_results.append({
                "type": "constitutional_check",
                "violations": 0,
                "status": "compliant"
            })
            return {"violations": 0, "enforcement_active": True}
        
        async def emergency_containment_check():
            """Simulate emergency containment assessment."""
            await asyncio.sleep(0.005)
            evaluation_results.append({
                "type": "emergency_check", 
                "containment_needed": False,
                "status": "normal"
            })
            return {"containment_active": False}
        
        # Create Guardian tasks
        drift_task = await run_guardian_task(
            ethical_drift_monitor(),
            name="ethical_drift_monitor",
            description="Monitor ethical drift (threshold: 0.15)",
            consciousness_context="guardian_ethics"
        )
        
        constitutional_task = await run_guardian_task(
            constitutional_enforcement(),
            name="constitutional_enforcement",
            description="Enforce constitutional AI constraints",
            consciousness_context="guardian_constitutional"
        )
        
        emergency_task = await run_guardian_task(
            emergency_containment_check(),
            name="emergency_containment_check",
            description="Check emergency containment status",
            consciousness_context="guardian_emergency"
        )
        
        # Wait for all Guardian evaluations
        drift_score = await drift_task
        constitutional_result = await constitutional_task
        emergency_result = await emergency_task
        
        # Validate results
        assert drift_score == 0.08
        assert constitutional_result["enforcement_active"] is True
        assert emergency_result["containment_active"] is False
        
        # Verify all evaluations completed
        assert len(evaluation_results) == 3
        types_evaluated = [result["type"] for result in evaluation_results]
        assert "drift_monitor" in types_evaluated
        assert "constitutional_check" in types_evaluated  
        assert "emergency_check" in types_evaluated


@pytest.mark.integration
class TestOrchestrationAsyncReliability:
    """Test orchestration system async reliability."""
    
    @pytest.mark.asyncio
    async def test_brain_integration_async_coordination(self):
        """Test brain integration async coordination."""
        
        integration_events = []
        
        async def glyph_communication():
            """Simulate GLYPH-based inter-module communication."""
            await asyncio.sleep(0.01)
            integration_events.append("glyph_message_sent")
            return {"message_id": "test_glyph", "status": "delivered"}
        
        async def context_bus_routing():
            """Simulate context bus message routing."""  
            await asyncio.sleep(0.008)
            integration_events.append("context_routed")
            return {"route_count": 3, "status": "routed"}
        
        async def multi_agent_coordination():
            """Simulate multi-agent coordination."""
            await asyncio.sleep(0.012)
            integration_events.append("agents_coordinated")
            return {"agents_synchronized": 5}
        
        # Use background tasks for orchestration
        glyph_task = await run_background_task(
            glyph_communication(),
            name="glyph_communication",
            description="Handle GLYPH inter-module communication"
        )
        
        context_task = await run_background_task(
            context_bus_routing(),
            name="context_bus_routing", 
            description="Route messages via context bus"
        )
        
        coordination_task = await run_background_task(
            multi_agent_coordination(),
            name="multi_agent_coordination",
            description="Coordinate multiple AI agents"
        )
        
        # Wait for orchestration completion
        glyph_result = await glyph_task
        context_result = await context_task  
        coordination_result = await coordination_task
        
        # Validate orchestration results
        assert glyph_result["status"] == "delivered"
        assert context_result["status"] == "routed"
        assert coordination_result["agents_synchronized"] == 5
        
        # Verify all integration events occurred
        assert "glyph_message_sent" in integration_events
        assert "context_routed" in integration_events
        assert "agents_coordinated" in integration_events


@pytest.mark.integration
class TestAsyncSystemShutdown:
    """Test system-wide async shutdown reliability."""
    
    @pytest.mark.asyncio
    async def test_graceful_consciousness_system_shutdown(self):
        """Test graceful shutdown of entire consciousness system."""
        
        shutdown_events = []
        long_running_tasks = []
        
        async def consciousness_processing():
            """Simulate long-running consciousness processing."""
            try:
                for i in range(10):  # Would take 0.1s to complete naturally
                    await asyncio.sleep(0.01)
                    shutdown_events.append(f"consciousness_step_{i}")
                shutdown_events.append("consciousness_completed_naturally")
            except asyncio.CancelledError:
                shutdown_events.append("consciousness_cancelled_gracefully")
                raise
        
        async def memory_processing():
            """Simulate long-running memory processing."""
            try:
                for i in range(8):  # Would take 0.08s to complete naturally
                    await asyncio.sleep(0.01)
                    shutdown_events.append(f"memory_step_{i}")
                shutdown_events.append("memory_completed_naturally")
            except asyncio.CancelledError:
                shutdown_events.append("memory_cancelled_gracefully")
                raise
        
        async def guardian_monitoring():
            """Simulate Guardian monitoring."""
            try:
                for i in range(5):  # Would take 0.05s to complete naturally
                    await asyncio.sleep(0.01)
                    shutdown_events.append(f"guardian_step_{i}")
                shutdown_events.append("guardian_completed_naturally")
            except asyncio.CancelledError:
                shutdown_events.append("guardian_cancelled_gracefully")
                raise
        
        # Start consciousness system components
        consciousness_task = await run_consciousness_task(
            consciousness_processing(),
            name="consciousness_processing",
            priority=TaskPriority.CRITICAL,
            description="Long-running consciousness processing"
        )
        long_running_tasks.append(consciousness_task)
        
        memory_task = await run_consciousness_task(
            memory_processing(),
            name="memory_processing", 
            priority=TaskPriority.HIGH,
            description="Long-running memory processing"
        )
        long_running_tasks.append(memory_task)
        
        guardian_task = await run_guardian_task(
            guardian_monitoring(),
            name="guardian_monitoring",
            description="Long-running Guardian monitoring"
        )
        long_running_tasks.append(guardian_task)
        
        # Let tasks run briefly
        await asyncio.sleep(0.02)
        
        # Initiate graceful shutdown
        start_shutdown = time.time()
        await shutdown_all_managers(timeout=0.05)  # Short timeout for testing
        shutdown_duration = time.time() - start_shutdown
        
        # Verify shutdown completed quickly
        assert shutdown_duration < 0.2  # Should complete within 200ms
        
        # All tasks should be cancelled or completed
        for task in long_running_tasks:
            assert task.done()
        
        # Verify graceful cancellation occurred
        cancellation_events = [
            event for event in shutdown_events 
            if "cancelled_gracefully" in event
        ]
        assert len(cancellation_events) >= 1  # At least one task was cancelled gracefully
        
        logger.info(f"Shutdown events: {shutdown_events}")
        logger.info(f"Shutdown completed in {shutdown_duration:.3f}s")


@pytest.mark.performance
class TestAsyncPerformanceReliability:
    """Test async performance and reliability under load."""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_consciousness_tasks(self):
        """Test high concurrency with consciousness tasks."""
        
        completed_tasks = []
        
        async def consciousness_work_unit(work_id):
            """Simulate a unit of consciousness work."""
            await asyncio.sleep(0.001)  # Very brief work
            completed_tasks.append(work_id)
            return f"work_unit_{work_id}_complete"
        
        # Create many concurrent consciousness tasks
        tasks = []
        for i in range(50):  # 50 concurrent tasks
            task = await run_consciousness_task(
                consciousness_work_unit(i),
                name=f"consciousness_work_{i}",
                priority=TaskPriority.NORMAL,
                description=f"Consciousness work unit {i}"
            )
            tasks.append(task)
        
        start_time = time.time()
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        completion_time = time.time() - start_time
        
        # Verify all tasks completed
        assert len(results) == 50
        assert len(completed_tasks) == 50
        assert all(f"work_unit_{i}_complete" in results for i in range(50))
        
        # Performance should be reasonable (parallel execution)
        assert completion_time < 1.0  # Should complete within 1 second
        
        logger.info(f"50 concurrent consciousness tasks completed in {completion_time:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])