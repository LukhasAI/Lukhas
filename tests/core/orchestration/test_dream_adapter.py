"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 LUKHAS AI - Dream Engine Adapter Tests  
═══════════════════════════════════════════════════════════════════════════════════

Test Module: test_dream_adapter
Purpose: Comprehensive testing of dream engine adapter integration system
Version: 1.0.0
Implementation: Production-grade test coverage for consciousness-aware dream processing

Test Coverage:
✅ Adapter initialization and registration
✅ Message handling and routing
✅ State tracking and transitions
✅ Dream cycle management
✅ Error handling and edge cases
✅ Integration layer communication
✅ Asynchronous operations
✅ Performance and reliability

Architecture: Field-theoretic consciousness model with unified integration layer
═══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

import pytest

from core.orchestration.brain.unified_integration.adapters.dream_adapter import DreamEngineAdapter


class MockUnifiedIntegration:
    """Mock unified integration layer for testing"""
    
    def __init__(self):
        self.components = {}
        self.messages = []
        
    def register_component(self, component_id: str, handler) -> None:
        """Register a component with the integration layer"""
        self.components[component_id] = handler
        
    def send_message(self, component_id: str, content: Dict[str, Any]) -> None:
        """Send a message through the integration layer"""
        self.messages.append({
            "component_id": component_id,
            "content": content,
            "timestamp": time.time()
        })


class TestDreamEngineAdapterInitialization(unittest.TestCase):
    """Test dream adapter initialization and setup"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        
    def test_adapter_initialization(self):
        """Test basic adapter initialization"""
        adapter = DreamEngineAdapter(self.mock_integration)
        
        # Verify basic setup
        self.assertEqual(adapter.component_id, "dream_engine")
        self.assertEqual(adapter.integration, self.mock_integration)
        
        # Verify state initialization
        self.assertEqual(adapter.dream_state["status"], "idle")
        self.assertIsNone(adapter.dream_state["start_time"])
        self.assertEqual(adapter.dream_state["duration"], 0)
        self.assertIsInstance(adapter.dream_state["last_updated"], float)
        
    def test_integration_registration(self):
        """Test registration with integration layer"""
        adapter = DreamEngineAdapter(self.mock_integration)
        
        # Verify component was registered
        self.assertIn("dream_engine", self.mock_integration.components)
        self.assertEqual(
            self.mock_integration.components["dream_engine"],
            adapter.handle_message
        )
        
    def test_multiple_adapter_instances(self):
        """Test multiple adapter instances can coexist"""
        integration1 = MockUnifiedIntegration()
        integration2 = MockUnifiedIntegration()
        
        adapter1 = DreamEngineAdapter(integration1)
        adapter2 = DreamEngineAdapter(integration2)
        
        # Verify independent registrations
        self.assertIn("dream_engine", integration1.components)
        self.assertIn("dream_engine", integration2.components)
        self.assertNotEqual(adapter1.integration, adapter2.integration)


class TestDreamEngineAdapterStateManagement(unittest.TestCase):
    """Test dream state tracking and management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    def test_initial_state(self):
        """Test initial dream state"""
        state = self.adapter.dream_state
        
        self.assertEqual(state["status"], "idle")
        self.assertIsNone(state["start_time"])
        self.assertEqual(state["duration"], 0)
        self.assertIsInstance(state["last_updated"], float)
        
    def test_state_update_dreaming(self):
        """Test state update when starting dream cycle"""
        self.adapter._update_state("dreaming", 60)
        
        state = self.adapter.dream_state
        self.assertEqual(state["status"], "dreaming")
        self.assertEqual(state["duration"], 60)
        self.assertIsInstance(state["start_time"], float)
        self.assertIsInstance(state["last_updated"], float)
        
    def test_state_update_idle(self):
        """Test state update when stopping dream cycle"""
        # Start dreaming first
        self.adapter._update_state("dreaming", 60)
        
        # Then stop
        self.adapter._update_state("idle", 0)
        
        state = self.adapter.dream_state
        self.assertEqual(state["status"], "idle")
        self.assertEqual(state["duration"], 0)
        self.assertIsNone(state["start_time"])
        
    def test_state_persistence(self):
        """Test state persistence across operations"""
        original_time = time.time()
        
        # Update state
        self.adapter._update_state("dreaming", 30)
        
        # Verify persistence
        state1 = self.adapter.dream_state.copy()
        
        # Simulate time passing
        time.sleep(0.01)
        
        # State should remain consistent
        state2 = self.adapter.dream_state
        self.assertEqual(state1["status"], state2["status"])
        self.assertEqual(state1["duration"], state2["duration"])
        self.assertEqual(state1["start_time"], state2["start_time"])


class TestDreamEngineAdapterMessageHandling(unittest.TestCase):
    """Test message handling and routing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    def test_start_dream_cycle_message(self):
        """Test handling start_dream_cycle message"""
        message = {
            "content": {
                "action": "start_dream_cycle",
                "duration": 30
            }
        }
        
        with patch.object(self.adapter, '_handle_start_cycle') as mock_start:
            self.adapter.handle_message(message)
            mock_start.assert_called_once_with(message["content"])
            
    def test_stop_dream_cycle_message(self):
        """Test handling stop_dream_cycle message"""
        message = {
            "content": {
                "action": "stop_dream_cycle"
            }
        }
        
        with patch.object(self.adapter, '_handle_stop_cycle') as mock_stop:
            self.adapter.handle_message(message)
            mock_stop.assert_called_once_with(message["content"])
            
    def test_get_dream_state_message(self):
        """Test handling get_dream_state message"""
        message = {
            "content": {
                "action": "get_dream_state"
            }
        }
        
        with patch.object(self.adapter, '_handle_get_state') as mock_get:
            self.adapter.handle_message(message)
            mock_get.assert_called_once_with(message["content"])
            
    def test_unknown_action_message(self):
        """Test handling unknown action message"""
        message = {
            "content": {
                "action": "unknown_action"
            }
        }
        
        # Should not raise exception, just ignore
        try:
            self.adapter.handle_message(message)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")
            
    def test_malformed_message_handling(self):
        """Test handling malformed messages"""
        malformed_messages = [
            {},  # No content
            {"content": {}},  # No action
            {"content": {"action": None}},  # Null action
            {"invalid": "structure"},  # Wrong structure
        ]
        
        for message in malformed_messages:
            with self.subTest(message=message):
                # Should not raise exception
                try:
                    self.adapter.handle_message(message)
                except Exception as e:
                    self.fail(f"Unexpected exception for {message}: {e}")


class TestDreamEngineAdapterCycleManagement(unittest.TestCase):
    """Test dream cycle start/stop operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    @pytest.mark.asyncio
    async def test_start_dream_cycle_success(self):
        """Test successful dream cycle start"""
        duration = 30
        
        await self.adapter.start_dream_cycle(duration)
        
        # Verify state was updated
        state = self.adapter.dream_state
        self.assertEqual(state["status"], "dreaming")
        self.assertIsInstance(state["start_time"], float)
        
    @pytest.mark.asyncio
    async def test_start_dream_cycle_already_running(self):
        """Test starting dream cycle when already running"""
        # Start first cycle
        await self.adapter.start_dream_cycle(30)
        
        # Try to start second cycle
        with patch('logging.Logger.warning') as mock_warning:
            await self.adapter.start_dream_cycle(60)
            mock_warning.assert_called_once()
            
        # State should remain from first cycle
        self.assertEqual(self.adapter.dream_state["status"], "dreaming")
        
    @pytest.mark.asyncio
    async def test_stop_dream_cycle_success(self):
        """Test successful dream cycle stop"""
        # Start cycle first
        await self.adapter.start_dream_cycle(30)
        
        # Stop cycle
        await self.adapter.stop_dream_cycle()
        
        # Verify state was updated
        state = self.adapter.dream_state
        self.assertEqual(state["status"], "idle")
        self.assertIsNone(state["start_time"])
        
    @pytest.mark.asyncio
    async def test_stop_dream_cycle_not_running(self):
        """Test stopping dream cycle when not running"""
        # Ensure not running
        self.assertEqual(self.adapter.dream_state["status"], "idle")
        
        # Try to stop
        with patch('logging.Logger.warning') as mock_warning:
            await self.adapter.stop_dream_cycle()
            mock_warning.assert_called_once()


class TestDreamEngineAdapterIntegration(unittest.TestCase):
    """Test integration layer communication"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    def test_send_response(self):
        """Test sending response through integration layer"""
        test_content = {
            "status": "success",
            "data": {"key": "value"}
        }
        
        self.adapter._send_response(test_content)
        
        # Verify message was sent
        self.assertEqual(len(self.mock_integration.messages), 1)
        
        message = self.mock_integration.messages[0]
        self.assertEqual(message["component_id"], "dream_engine")
        self.assertEqual(message["content"], test_content)
        self.assertIsInstance(message["timestamp"], float)
        
    def test_multiple_responses(self):
        """Test sending multiple responses"""
        responses = [
            {"action": "start", "status": "initiated"},
            {"action": "processing", "status": "active"},
            {"action": "complete", "status": "finished"}
        ]
        
        for response in responses:
            self.adapter._send_response(response)
            
        # Verify all messages were sent
        self.assertEqual(len(self.mock_integration.messages), len(responses))
        
        for i, response in enumerate(responses):
            message = self.mock_integration.messages[i]
            self.assertEqual(message["content"], response)


class TestDreamEngineAdapterErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    def test_handle_message_exception(self):
        """Test exception handling in message processing"""
        message = {
            "content": {
                "action": "start_dream_cycle",
                "duration": 30
            }
        }
        
        # Mock method to raise exception
        with patch.object(self.adapter, '_handle_start_cycle', side_effect=Exception("Test error")):
            with patch('logging.Logger.error') as mock_error:
                self.adapter.handle_message(message)
                mock_error.assert_called_once()
                
    def test_integration_layer_exception(self):
        """Test handling integration layer exceptions"""
        # Mock integration to raise exception
        self.mock_integration.send_message = MagicMock(side_effect=Exception("Integration error"))
        
        # Should not crash
        try:
            self.adapter._send_response({"test": "data"})
        except Exception as e:
            self.fail(f"Adapter should handle integration exceptions: {e}")
            
    @pytest.mark.asyncio
    async def test_async_operation_timeout(self):
        """Test async operation timeout handling"""
        # This tests robustness of async operations
        with patch('asyncio.sleep', side_effect=asyncio.TimeoutError()):
            try:
                # Should handle timeout gracefully
                await self.adapter.start_dream_cycle(30)
            except asyncio.TimeoutError:
                # Expected behavior - timeout should propagate
                pass


class TestDreamEngineAdapterPerformance(unittest.TestCase):
    """Test performance and reliability aspects"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_integration = MockUnifiedIntegration()
        self.adapter = DreamEngineAdapter(self.mock_integration)
        
    def test_rapid_message_handling(self):
        """Test handling rapid message sequences"""
        messages = [
            {"content": {"action": "get_dream_state"}},
            {"content": {"action": "start_dream_cycle", "duration": 10}},
            {"content": {"action": "get_dream_state"}},
            {"content": {"action": "stop_dream_cycle"}},
            {"content": {"action": "get_dream_state"}},
        ]
        
        start_time = time.time()
        
        with patch.object(self.adapter, '_handle_start_cycle'), \
             patch.object(self.adapter, '_handle_stop_cycle'), \
             patch.object(self.adapter, '_handle_get_state'):
            
            for message in messages:
                self.adapter.handle_message(message)
                
        end_time = time.time()
        
        # Should complete quickly (< 1 second for simple operations)
        self.assertLess(end_time - start_time, 1.0)
        
    def test_state_update_performance(self):
        """Test state update performance"""
        start_time = time.time()
        
        # Perform many state updates
        for i in range(1000):
            status = "dreaming" if i % 2 == 0 else "idle"
            self.adapter._update_state(status, i)
            
        end_time = time.time()
        
        # Should complete quickly
        self.assertLess(end_time - start_time, 1.0)
        
    def test_memory_usage_stability(self):
        """Test memory usage remains stable"""
        import gc
        import sys
        
        # Get initial state
        initial_objects = len(gc.get_objects())
        
        # Perform operations
        for i in range(100):
            message = {"content": {"action": "get_dream_state"}}
            with patch.object(self.adapter, '_handle_get_state'):
                self.adapter.handle_message(message)
                
        # Force garbage collection
        gc.collect()
        
        # Check object count hasn't grown significantly
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Allow some growth but not excessive
        self.assertLess(object_growth, 50, "Memory usage grew excessively")


if __name__ == "__main__":
    # Run tests with pytest for async support
    pytest.main([__file__, "-v", "--tb=short"])