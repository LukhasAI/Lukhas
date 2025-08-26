"""Kernel Bus Integration Tests

Tests for the LUKHAS event coordination system.
Verifies dry_run mode, feature flag activation, and event dispatch.
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from candidate.orchestration import (
    KernelBus,
    EventPriority,
    get_kernel_bus,
    emit,
    subscribe,
    build_context
)


class TestKernelBusIntegration:
    """Test kernel bus event coordination"""
    
    def test_kernel_bus_initialization(self):
        """Test kernel bus can be initialized"""
        bus = KernelBus(max_history=50)
        assert bus is not None
        assert bus._metrics["events_emitted"] == 0
        assert bus._metrics["events_dispatched"] == 0
    
    def test_emit_dry_run_mode(self):
        """Test event emission in dry_run mode"""
        bus = KernelBus()
        result = bus.emit(
            "test.event",
            {"data": "test"},
            source="test_module",
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["dispatched"] == 0
        assert "event_id" in result
        assert bus._metrics["events_emitted"] == 1
        assert bus._metrics["events_dispatched"] == 0
    
    def test_emit_with_priority(self):
        """Test event emission with different priorities"""
        bus = KernelBus()
        
        # Test each priority level
        for priority in EventPriority:
            result = bus.emit(
                f"test.{priority.value}",
                {"priority": priority.value},
                priority=priority,
                mode="dry_run"
            )
            assert result["ok"] is True
    
    def test_subscribe_dry_run_mode(self):
        """Test subscription in dry_run mode"""
        bus = KernelBus()
        handler = MagicMock()
        
        result = bus.subscribe(
            "test.event",
            handler,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["subscribers"] == 0
        assert "test.event" not in bus._subscribers
    
    def test_emit_and_subscribe_active_mode(self):
        """Test event dispatch mechanics when active"""
        # Create a bus with _active flag manually set
        bus = KernelBus()
        bus._active = True  # Manually activate for testing
        handler = MagicMock()
        
        # Subscribe in live mode
        sub_result = bus.subscribe(
            "test.event",
            handler,
            mode="live"
        )
        assert sub_result["ok"] is True
        assert sub_result["mode"] == "live"
        assert sub_result["subscribers"] == 1
        
        # Emit in live mode
        emit_result = bus.emit(
            "test.event",
            {"data": "test"},
            source="test",
            mode="live"
        )
        assert emit_result["ok"] is True
        assert emit_result["mode"] == "live"
        assert emit_result["dispatched"] == 1
        
        # Handler should have been called
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args["event"] == "test.event"
        assert call_args["payload"]["data"] == "test"
    
    def test_correlation_id(self):
        """Test events with correlation IDs"""
        bus = KernelBus()
        correlation_id = "corr-123"
        
        result = bus.emit(
            "test.correlated",
            {"step": 1},
            correlation_id=correlation_id,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        # Check event history contains correlation ID
        last_event = bus._event_history[-1]
        assert last_event["correlation_id"] == correlation_id
    
    def test_get_status(self):
        """Test status reporting"""
        bus = KernelBus()
        
        # Emit some events
        bus.emit("test.1", {}, mode="dry_run")
        bus.emit("test.2", {}, mode="dry_run")
        
        status = bus.get_status(mode="dry_run")
        
        assert status["ok"] is True
        assert status["active"] is False
        assert status["metrics"]["events_emitted"] == 2
        assert status["history_size"] == 2
        assert status["mode"] == "dry_run"
    
    def test_global_instance(self):
        """Test global kernel bus instance"""
        bus1 = get_kernel_bus()
        bus2 = get_kernel_bus()
        
        # Should be the same instance
        assert bus1 is bus2
    
    def test_global_emit_function(self):
        """Test global emit function"""
        result = emit(
            "global.test",
            {"from": "global"},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
    
    def test_global_subscribe_function(self):
        """Test global subscribe function"""
        handler = MagicMock()
        result = subscribe(
            "global.test",
            handler,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
    
    def test_event_history_limit(self):
        """Test that event history respects max size"""
        bus = KernelBus(max_history=5)
        
        # Emit more events than history size
        for i in range(10):
            bus.emit(f"test.{i}", {"index": i}, mode="dry_run")
        
        # History should only contain last 5
        assert len(bus._event_history) == 5
        assert bus._event_history[-1]["payload"]["index"] == 9
        assert bus._event_history[0]["payload"]["index"] == 5
    
    def test_build_context_function(self):
        """Test the existing build_context function still works"""
        ctx = build_context(
            {"session_id": "test123", "tenant": "test_tenant"},
            mode="dry_run"
        )
        
        assert ctx["session"]["id"] == "test123"
        assert ctx["tenant"] == "test_tenant"
        assert "policy_hints" in ctx
    
    def test_matriz_instrumentation(self):
        """Test that MATRIZ decorators are applied"""
        bus = KernelBus()
        
        # Check that methods have MATRIZ instrumentation
        assert hasattr(bus.emit, "__wrapped__")
        assert hasattr(bus.subscribe, "__wrapped__")
        assert hasattr(bus.get_status, "__wrapped__")
        assert hasattr(emit, "__wrapped__")
        assert hasattr(subscribe, "__wrapped__")
        assert hasattr(build_context, "__wrapped__")
    
    def test_error_handling_in_handler(self):
        """Test that errors in handlers don't crash the bus"""
        bus = KernelBus()
        bus._active = True  # Manually activate for testing
        
        # Handler that raises exception
        def bad_handler(event):
            raise ValueError("Handler error")
        
        bus.subscribe("test.error", bad_handler, mode="live")
        
        # Should not crash
        result = bus.emit(
            "test.error",
            {"will": "cause_error"},
            mode="live"
        )
        
        assert result["ok"] is True
        assert result["dispatched"] == 1
    
    def test_module_manifest_updated(self):
        """Verify MODULE_MANIFEST.json has new capabilities"""
        import json
        import pathlib
        
        manifest_path = pathlib.Path("lukhas/orchestration/MODULE_MANIFEST.json")
        assert manifest_path.exists()
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check new capabilities
        assert "orchestrator:events" in manifest["capabilities"]
        assert "orchestrator:monitor" in manifest["capabilities"]
        
        # Check new emit points
        assert "emit" in manifest["matriz_emit_points"]
        assert "subscribe" in manifest["matriz_emit_points"]
        assert "get_status" in manifest["matriz_emit_points"]