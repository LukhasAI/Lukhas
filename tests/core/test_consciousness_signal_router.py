"""
Comprehensive Test Suite for Consciousness Signal Router
======================================================

Tests the advanced signal routing and network coordination system for consciousness data flow.
This module is critical for distributed consciousness architecture and requires thorough testing.

Test Coverage Areas:
- Signal routing strategies (broadcast, targeted, priority-based, coherence-based, adaptive)
- Signal filtering mechanisms (coherence threshold, awareness level, Trinity compliance)
- Cascade prevention and network health monitoring
- Router metrics and performance monitoring
- Network coordination and flow control
- Error handling and recovery scenarios
"""
import asyncio
import threading
import time
from collections import defaultdict, deque
from unittest.mock import MagicMock, Mock, patch

import pytest

from core.consciousness_signal_router import (
    CascadePrevention,
    ConsciousnessSignalRouter,
    NetworkHealthMonitor,
    RouteRegistry,
    RoutingStrategy,
    SignalBuffer,
    SignalFilter,
    SignalMetrics,
)
from core.matriz_consciousness_signals import (
    ConsciousnessSignal,
    ConsciousnessSignalType,
)


class TestConsciousnessSignalRouter:
    """Comprehensive test suite for the Consciousness Signal Router system."""

    @pytest.fixture
    def router(self):
        """Create a test router instance."""
        return ConsciousnessSignalRouter(
            max_buffer_size=1000,
            health_check_interval=1.0,
            cascade_prevention_enabled=True
        )

    @pytest.fixture
    def sample_signal(self):
        """Create a sample consciousness signal for testing."""
        return ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            data={"awareness_level": 0.8, "coherence_score": 0.9},
            source_module="test_module",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.9
        )

    @pytest.fixture
    def sample_signals(self):
        """Create multiple test signals."""
        signals = []
        for i in range(10):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                data={"index": i, "awareness_level": 0.1 * i},
                source_module=f"test_module_{i}",
                timestamp=time.time() + i,
                priority=i % 6,
                coherence_score=0.1 * i
            )
            signals.append(signal)
        return signals

    # Basic Router Functionality Tests
    def test_router_initialization(self, router):
        """Test router initializes with correct default settings."""
        assert router.max_buffer_size == 1000
        assert router.health_check_interval == 1.0
        assert router.cascade_prevention_enabled is True
        assert router.is_running is False
        assert isinstance(router.signal_buffer, SignalBuffer)
        assert isinstance(router.health_monitor, NetworkHealthMonitor)

    def test_router_start_stop(self, router):
        """Test router start and stop functionality."""
        # Test start
        router.start()
        assert router.is_running is True

        # Test stop
        router.stop()
        assert router.is_running is False

    def test_signal_registration(self, router, sample_signal):
        """Test signal registration and routing."""
        # Register a handler
        handler_called = False
        received_signal = None

        def test_handler(signal):
            nonlocal handler_called, received_signal
            handler_called = True
            received_signal = signal

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=test_handler,
            strategy=RoutingStrategy.TARGETED
        )

        # Send signal
        router.route_signal(sample_signal)

        # Verify handler was called
        assert handler_called is True
        assert received_signal == sample_signal

    # Routing Strategy Tests
    def test_broadcast_routing(self, router, sample_signal):
        """Test broadcast routing strategy."""
        handlers_called = []

        def create_handler(handler_id):
            def handler(signal):
                handlers_called.append(handler_id)
            return handler

        # Register multiple handlers
        for i in range(3):
            router.register_handler(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                handler=create_handler(f"handler_{i}"),
                strategy=RoutingStrategy.BROADCAST
            )

        # Send signal with broadcast strategy
        router.route_signal(sample_signal, strategy=RoutingStrategy.BROADCAST)

        # Verify all handlers were called
        assert len(handlers_called) == 3
        assert "handler_0" in handlers_called
        assert "handler_1" in handlers_called
        assert "handler_2" in handlers_called

    def test_targeted_routing(self, router, sample_signal):
        """Test targeted routing strategy."""
        target_handler_called = False
        other_handler_called = False

        def target_handler(signal):
            nonlocal target_handler_called
            target_handler_called = True

        def other_handler(signal):
            nonlocal other_handler_called
            other_handler_called = True

        # Register handlers
        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=target_handler,
            strategy=RoutingStrategy.TARGETED,
            target_modules=["test_module"]
        )

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=other_handler,
            strategy=RoutingStrategy.TARGETED,
            target_modules=["other_module"]
        )

        # Send signal
        router.route_signal(sample_signal, strategy=RoutingStrategy.TARGETED)

        # Verify only target handler was called
        assert target_handler_called is True
        assert other_handler_called is False

    def test_priority_based_routing(self, router, sample_signals):
        """Test priority-based routing strategy."""
        received_signals = []

        def priority_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=priority_handler,
            strategy=RoutingStrategy.PRIORITY_BASED,
            minimum_priority=3
        )

        # Send signals with various priorities
        for signal in sample_signals:
            router.route_signal(signal, strategy=RoutingStrategy.PRIORITY_BASED)

        # Verify only high priority signals were processed
        assert all(signal.priority >= 3 for signal in received_signals)

    def test_coherence_based_routing(self, router, sample_signals):
        """Test coherence-based routing strategy."""
        received_signals = []

        def coherence_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=coherence_handler,
            strategy=RoutingStrategy.COHERENCE_BASED,
            minimum_coherence=0.5
        )

        # Send signals with various coherence scores
        for signal in sample_signals:
            router.route_signal(signal, strategy=RoutingStrategy.COHERENCE_BASED)

        # Verify only high coherence signals were processed
        assert all(signal.coherence_score >= 0.5 for signal in received_signals)

    def test_adaptive_routing(self, router, sample_signal):
        """Test adaptive routing strategy."""
        # Mock network conditions
        with patch.object(router.health_monitor, 'get_network_load', return_value=0.8):
            with patch.object(router.health_monitor, 'get_coherence_score', return_value=0.6):
                handler_called = False

                def adaptive_handler(signal):
                    nonlocal handler_called
                    handler_called = True

                router.register_handler(
                    signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                    handler=adaptive_handler,
                    strategy=RoutingStrategy.ADAPTIVE
                )

                # Send signal
                router.route_signal(sample_signal, strategy=RoutingStrategy.ADAPTIVE)

                # Verify adaptive routing behavior
                assert handler_called is True

    # Signal Filtering Tests
    def test_coherence_threshold_filter(self, router, sample_signals):
        """Test coherence threshold filtering."""
        received_signals = []

        def filtered_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=filtered_handler,
            signal_filter=SignalFilter.COHERENCE_THRESHOLD,
            filter_threshold=0.5
        )

        # Send signals
        for signal in sample_signals:
            router.route_signal(signal)

        # Verify filtering
        assert all(signal.coherence_score >= 0.5 for signal in received_signals)

    def test_awareness_level_filter(self, router, sample_signals):
        """Test awareness level filtering."""
        received_signals = []

        def awareness_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=awareness_handler,
            signal_filter=SignalFilter.AWARENESS_LEVEL,
            filter_threshold=0.5
        )

        # Send signals
        for signal in sample_signals:
            router.route_signal(signal)

        # Verify awareness level filtering
        for signal in received_signals:
            if "awareness_level" in signal.data:
                assert signal.data["awareness_level"] >= 0.5

    def test_trinity_compliance_filter(self, router, sample_signal):
        """Test Trinity/Constellation Framework compliance filtering."""
        received_signals = []

        def trinity_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=trinity_handler,
            signal_filter=SignalFilter.TRINITY_COMPLIANCE
        )

        # Add Trinity compliance metadata
        sample_signal.data["trinity_compliant"] = True
        sample_signal.data["constellation_alignment"] = 0.9

        router.route_signal(sample_signal)

        # Verify Trinity compliance filtering
        assert len(received_signals) == 1
        assert received_signals[0].data.get("trinity_compliant") is True

    def test_frequency_band_filter(self, router, sample_signals):
        """Test frequency band filtering."""
        received_signals = []

        def frequency_handler(signal):
            received_signals.append(signal)

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=frequency_handler,
            signal_filter=SignalFilter.FREQUENCY_BAND,
            frequency_range=(0.1, 0.8)
        )

        # Add frequency data to signals
        for i, signal in enumerate(sample_signals):
            signal.data["frequency"] = 0.1 * i

        # Send signals
        for signal in sample_signals:
            router.route_signal(signal)

        # Verify frequency filtering
        for signal in received_signals:
            freq = signal.data.get("frequency", 0)
            assert 0.1 <= freq <= 0.8

    def test_signal_type_filter(self, router):
        """Test signal type filtering."""
        received_signals = []

        def type_handler(signal):
            received_signals.append(signal)

        # Register handler for specific signal type
        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=type_handler,
            signal_filter=SignalFilter.SIGNAL_TYPE
        )

        # Send different signal types
        awareness_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            data={}, source_module="test", timestamp=time.time(),
            priority=1, coherence_score=0.5
        )

        emotion_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.EMOTION_STATE,
            data={}, source_module="test", timestamp=time.time(),
            priority=1, coherence_score=0.5
        )

        router.route_signal(awareness_signal)
        router.route_signal(emotion_signal)

        # Verify only awareness signals were processed
        assert len(received_signals) == 1
        assert received_signals[0].signal_type == ConsciousnessSignalType.AWARENESS_UPDATE

    # Cascade Prevention Tests
    def test_cascade_prevention(self, router, sample_signal):
        """Test cascade prevention mechanism."""

        with patch.object(router.cascade_prevention, 'should_prevent_cascade', return_value=True):
            handler_called = False

            def test_handler(signal):
                nonlocal handler_called
                handler_called = True

            router.register_handler(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                handler=test_handler
            )

            # Attempt to route signal
            result = router.route_signal(sample_signal)

            # Verify cascade was prevented
            assert result is False  # Signal was blocked
            assert handler_called is False

    def test_cascade_detection(self, router, sample_signals):
        """Test cascade detection logic."""
        # Send rapid sequence of signals from same module
        for signal in sample_signals[:5]:  # First 5 signals
            signal.source_module = "rapid_module"
            router.route_signal(signal)

        # Check if cascade is detected
        cascade_detected = router.cascade_prevention.is_cascade_detected("rapid_module")
        assert cascade_detected is True

    # Network Health Monitoring Tests
    def test_network_health_monitoring(self, router):
        """Test network health monitoring functionality."""
        health_monitor = router.health_monitor

        # Test initial health state
        assert health_monitor.get_network_load() >= 0.0
        assert health_monitor.get_coherence_score() >= 0.0
        assert health_monitor.get_active_connections() >= 0

        # Test health metrics update
        health_monitor.update_network_metrics()

        # Verify metrics are tracked
        assert health_monitor.metrics_history is not None

    def test_network_overload_detection(self, router):
        """Test network overload detection."""
        # Simulate high load
        with patch.object(router.health_monitor, 'get_network_load', return_value=0.95):
            overload_detected = router.health_monitor.is_network_overloaded()
            assert overload_detected is True

    def test_coherence_degradation_detection(self, router):
        """Test coherence degradation detection."""
        # Simulate low coherence
        with patch.object(router.health_monitor, 'get_coherence_score', return_value=0.2):
            degradation_detected = router.health_monitor.is_coherence_degraded()
            assert degradation_detected is True

    # Signal Buffer Tests
    def test_signal_buffering(self, router, sample_signals):
        """Test signal buffering mechanism."""
        # Stop router to prevent immediate processing
        router.stop()

        # Add signals to buffer
        for signal in sample_signals:
            router.signal_buffer.add_signal(signal)

        # Verify buffering
        assert router.signal_buffer.size() == len(sample_signals)
        assert not router.signal_buffer.is_empty()

    def test_buffer_overflow_handling(self, router):
        """Test buffer overflow handling."""
        # Set small buffer size
        router.signal_buffer.max_size = 5

        # Add more signals than buffer capacity
        for i in range(10):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                data={"index": i}, source_module="test",
                timestamp=time.time(), priority=1, coherence_score=0.5
            )
            router.signal_buffer.add_signal(signal)

        # Verify buffer size is limited
        assert router.signal_buffer.size() <= 5

    def test_priority_buffer_ordering(self, router, sample_signals):
        """Test priority-based buffer ordering."""
        # Stop router
        router.stop()

        # Add signals with different priorities
        for signal in sample_signals:
            router.signal_buffer.add_signal(signal)

        # Process signals and verify priority ordering
        processed_priorities = []
        while not router.signal_buffer.is_empty():
            signal = router.signal_buffer.get_next_signal()
            processed_priorities.append(signal.priority)

        # Verify high priority signals were processed first
        assert processed_priorities == sorted(processed_priorities, reverse=True)

    # Metrics and Monitoring Tests
    def test_signal_metrics_tracking(self, router, sample_signal):
        """Test signal metrics tracking."""
        # Route signal
        router.route_signal(sample_signal)

        # Verify metrics are tracked
        metrics = router.get_metrics()
        assert metrics.total_signals_processed >= 1
        assert metrics.signals_by_type[ConsciousnessSignalType.AWARENESS_UPDATE] >= 1

    def test_performance_metrics(self, router, sample_signals):
        """Test performance metrics tracking."""
        time.time()

        # Process multiple signals
        for signal in sample_signals:
            router.route_signal(signal)

        metrics = router.get_metrics()

        # Verify performance metrics
        assert metrics.average_processing_time > 0
        assert metrics.throughput_per_second >= 0

    def test_error_metrics_tracking(self, router, sample_signal):
        """Test error metrics tracking."""
        def failing_handler(signal):
            raise Exception("Test error")

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=failing_handler
        )

        # Route signal that will cause error
        router.route_signal(sample_signal)

        # Verify error metrics
        metrics = router.get_metrics()
        assert metrics.total_errors >= 1

    # Concurrent Processing Tests
    @pytest.mark.asyncio
    async def test_concurrent_signal_processing(self, router, sample_signals):
        """Test concurrent signal processing."""
        processed_signals = []
        processing_lock = threading.Lock()

        def concurrent_handler(signal):
            with processing_lock:
                processed_signals.append(signal)
                time.sleep(0.01)  # Simulate processing time

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=concurrent_handler
        )

        # Start router
        router.start()

        # Send signals concurrently
        tasks = []
        for signal in sample_signals:
            task = asyncio.create_task(
                asyncio.to_thread(router.route_signal, signal)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Stop router
        router.stop()

        # Verify concurrent processing
        assert len(processed_signals) == len(sample_signals)

    def test_thread_safety(self, router, sample_signals):
        """Test thread safety of router operations."""
        processed_count = 0
        lock = threading.Lock()

        def thread_safe_handler(signal):
            nonlocal processed_count
            with lock:
                processed_count += 1

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=thread_safe_handler
        )

        # Start router
        router.start()

        # Create multiple threads
        threads = []
        for _i in range(5):
            thread = threading.Thread(
                target=lambda: [router.route_signal(s) for s in sample_signals]
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Stop router
        router.stop()

        # Verify thread safety
        expected_count = 5 * len(sample_signals)
        assert processed_count == expected_count

    # Configuration and Customization Tests
    def test_custom_routing_strategy(self, router):
        """Test custom routing strategy implementation."""
        custom_strategy_used = False

        def custom_strategy(signal, handlers):
            nonlocal custom_strategy_used
            custom_strategy_used = True
            return handlers[:1]  # Return only first handler

        router.register_custom_strategy("custom", custom_strategy)

        # Register multiple handlers
        handlers_called = []
        for i in range(3):
            def create_handler(handler_id):
                def handler(signal):
                    handlers_called.append(handler_id)
                return handler

            router.register_handler(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                handler=create_handler(f"handler_{i}")
            )

        sample_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            data={}, source_module="test", timestamp=time.time(),
            priority=1, coherence_score=0.5
        )

        # Use custom strategy
        router.route_signal(sample_signal, strategy="custom")

        # Verify custom strategy was used
        assert custom_strategy_used is True
        assert len(handlers_called) == 1

    def test_dynamic_handler_registration(self, router):
        """Test dynamic handler registration and deregistration."""
        handler_called = False

        def dynamic_handler(signal):
            nonlocal handler_called
            handler_called = True

        # Register handler
        handler_id = router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=dynamic_handler
        )

        sample_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            data={}, source_module="test", timestamp=time.time(),
            priority=1, coherence_score=0.5
        )

        # Test handler is called
        router.route_signal(sample_signal)
        assert handler_called is True

        # Deregister handler
        router.deregister_handler(handler_id)
        handler_called = False

        # Test handler is no longer called
        router.route_signal(sample_signal)
        assert handler_called is False

    def test_router_configuration_validation(self, router):
        """Test router configuration validation."""
        # Test invalid configuration
        with pytest.raises(ValueError):
            ConsciousnessSignalRouter(
                max_buffer_size=-1,  # Invalid negative size
                health_check_interval=0.0,  # Invalid zero interval
            )

    # Integration Tests
    def test_bio_symbolic_processor_integration(self, router, sample_signal):
        """Test integration with bio-symbolic processor."""
        bio_processor_called = False

        def bio_handler(signal):
            nonlocal bio_processor_called
            bio_processor_called = True

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=bio_handler,
            use_bio_symbolic_processing=True
        )

        router.route_signal(sample_signal)

        # Verify bio-symbolic integration
        assert bio_processor_called is True

    def test_full_system_integration(self, router, sample_signals):
        """Test full system integration scenario."""
        # Set up comprehensive routing scenario
        results = {
            "broadcast": [],
            "targeted": [],
            "priority": [],
            "coherence": []
        }

        # Register handlers for different strategies
        def create_strategy_handler(strategy_name):
            def handler(signal):
                results[strategy_name].append(signal)
            return handler

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=create_strategy_handler("broadcast"),
            strategy=RoutingStrategy.BROADCAST
        )

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=create_strategy_handler("targeted"),
            strategy=RoutingStrategy.TARGETED,
            target_modules=["test_module_0", "test_module_1"]
        )

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=create_strategy_handler("priority"),
            strategy=RoutingStrategy.PRIORITY_BASED,
            minimum_priority=3
        )

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=create_strategy_handler("coherence"),
            strategy=RoutingStrategy.COHERENCE_BASED,
            minimum_coherence=0.5
        )

        # Start router
        router.start()

        # Process all signals
        for signal in sample_signals:
            router.route_signal(signal, strategy=RoutingStrategy.BROADCAST)
            router.route_signal(signal, strategy=RoutingStrategy.TARGETED)
            router.route_signal(signal, strategy=RoutingStrategy.PRIORITY_BASED)
            router.route_signal(signal, strategy=RoutingStrategy.COHERENCE_BASED)

        # Stop router
        router.stop()

        # Verify comprehensive integration
        assert len(results["broadcast"]) == len(sample_signals)
        assert len(results["targeted"]) == 2  # Only first 2 modules match
        assert len(results["priority"]) == sum(1 for s in sample_signals if s.priority >= 3)
        assert len(results["coherence"]) == sum(1 for s in sample_signals if s.coherence_score >= 0.5)

    # Cleanup and Resource Management Tests
    def test_router_cleanup(self, router):
        """Test router resource cleanup."""
        # Start router with resources
        router.start()

        # Add some signals and handlers
        def test_handler(signal):
            pass

        router.register_handler(
            signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
            handler=test_handler
        )

        # Stop and cleanup
        router.stop()
        router.cleanup()

        # Verify cleanup
        assert router.is_running is False
        assert router.signal_buffer.is_empty()

    def test_memory_management(self, router, sample_signals):
        """Test memory management during extended operation."""
        # Start router
        router.start()

        # Process many signals
        for _ in range(100):
            for signal in sample_signals:
                router.route_signal(signal)

        # Verify memory is managed properly
        buffer_size = router.signal_buffer.size()
        assert buffer_size <= router.max_buffer_size

        # Stop router
        router.stop()
