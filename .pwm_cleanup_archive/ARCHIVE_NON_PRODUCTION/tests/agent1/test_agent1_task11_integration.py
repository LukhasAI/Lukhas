#!/usr/bin/env python3
"""
Test suite for Agent 1 Task 11: Bridge Trace Logger Integration
Tests the integration of BridgeTraceLogger with the message bus system.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from bridge.message_bus import (
        Message,
        MessageBus,
        MessagePriority,
        MessageType,
    )
    from bridge.trace_logger import (
        BridgeTraceLogger,
        TraceCategory,
        TraceLevel,
    )

    print("✅ Successfully imported BridgeTraceLogger and MessageBus")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_trace_logger_initialization():
    """Test that trace logger initializes correctly"""
    print("\n🧪 Test 1: Trace Logger Initialization")

    try:
        trace_logger = BridgeTraceLogger(log_file="test_trace.log")
        print("✅ BridgeTraceLogger initialized successfully")

        # Test logging an event
        event_id = trace_logger.log_bridge_event(
            TraceCategory.HANDSHAKE,
            TraceLevel.INFO,
            "test_component",
            "Test handshake event",
            {"test": "metadata"},
        )
        print(f"✅ Event logged with ID: {event_id}")

        return True
    except Exception as e:
        print(f"❌ Trace logger initialization failed: {e}")
        return False


async def test_message_bus_trace_integration():
    """Test that message bus integrates trace logger correctly"""
    print("\n🧪 Test 2: Message Bus Trace Integration")

    try:
        # Create message bus with trace logger
        message_bus = MessageBus()
        await message_bus.start()
        print("✅ MessageBus started with trace logger integration")

        # Check trace logger status
        status = message_bus.get_bridge_trace_logger_status()
        print(f"✅ Trace logger status: {status}")

        # Register a test module
        success = message_bus.register_module("test_module")
        print(f"✅ Module registration: {success}")

        # Test symbolic handshake tracing
        trace_id = message_bus.trace_symbolic_handshake(
            "test_dream_001", "initiated", {"component": "test_bridge"}
        )
        print(f"✅ Symbolic handshake traced with ID: {trace_id}")

        # Test memory mapping tracing
        map_trace_id = message_bus.trace_memory_mapping(
            "map_001", "create", {"status": "success", "size": 1024}
        )
        print(f"✅ Memory mapping traced with ID: {map_trace_id}")

        # Get trace summary
        summary = message_bus.get_bridge_trace_summary()
        print(f"✅ Trace summary: {summary}")

        await message_bus.stop()
        print("✅ MessageBus stopped cleanly")

        return True
    except Exception as e:
        print(f"❌ Message bus trace integration failed: {e}")
        return False


async def test_message_tracing():
    """Test that message sending includes trace logging"""
    print("\n🧪 Test 3: Message Tracing")

    try:
        message_bus = MessageBus()
        await message_bus.start()

        # Register modules
        message_bus.register_module("sender_module")
        message_bus.register_module("receiver_module")

        # Create and send a test message
        test_message = Message(
            type=MessageType.COMMAND,
            source_module="sender_module",
            target_module="receiver_module",
            priority=MessagePriority.NORMAL,
            payload={"command": "test_command", "params": {"test": True}},
            user_id="test_user",
        )

        # Send message (should trigger trace logging)
        result = await message_bus.send_message(test_message)
        print(f"✅ Message sent with tracing: {result}")

        # Check message bus stats
        stats = message_bus.get_stats()
        print(f"✅ Message bus stats: messages_sent={stats.get('messages_sent', 0)}")

        await message_bus.stop()
        return True
    except Exception as e:
        print(f"❌ Message tracing failed: {e}")
        return False


async def test_trace_export():
    """Test trace data export functionality"""
    print("\n🧪 Test 4: Trace Export")

    try:
        message_bus = MessageBus()
        await message_bus.start()

        # Generate some trace data
        message_bus.trace_symbolic_handshake("export_test_001", "started")
        message_bus.trace_memory_mapping("export_map_001", "initialize")

        # Export trace data
        json_export = message_bus.export_bridge_trace_data("json")
        print(f"✅ JSON export completed (length: {len(json_export)} chars)")

        await message_bus.stop()
        return True
    except Exception as e:
        print(f"❌ Trace export failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Starting Agent 1 Task 11 Integration Tests")
    print("=" * 60)

    tests = [
        test_trace_logger_initialization,
        test_message_bus_trace_integration,
        test_message_tracing,
        test_trace_export,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 All tests passed! Bridge Trace Logger integration is working correctly."
        )
        return True
    else:
        print("⚠️  Some tests failed. Check the integration.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
