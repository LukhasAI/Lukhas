#!/usr/bin/env python3
"""
Test the Symbolic Kernel Bus functionality
"""

import asyncio
import time
from orchestration.symbolic_kernel_bus import (
    kernel_bus,
    SymbolicEffect,
    EventPriority,
    emit,
    subscribe
)

async def test_kernel_bus():
    """Test kernel bus operations"""
    
    print("🧪 Testing Symbolic Kernel Bus")
    print("="*60)
    
    # Start the kernel bus
    await kernel_bus.start()
    print("✅ Kernel bus started")
    
    # Test 1: Basic event emission
    print("\n📤 Test 1: Basic event emission")
    event_id = emit(
        "test.basic.event",
        {"message": "Hello from kernel bus"},
        source="test.suite"
    )
    print(f"  Emitted event: {event_id[:20]}...")
    
    # Test 2: Event with symbolic effects
    print("\n🎯 Test 2: Event with symbolic effects")
    event_id = emit(
        "memory.fold.init",
        {"fold_id": "test_fold_123", "content": {"data": "test"}},
        source="test.memory",
        effects=[SymbolicEffect.MEMORY_FOLD, SymbolicEffect.LOG_TRACE],
        priority=EventPriority.HIGH
    )
    print(f"  Emitted memory fold event with effects")
    
    # Test 3: Agent drift detection
    print("\n📊 Test 3: Agent drift detection")
    emit(
        "agent.drift.detected",
        {"agent_id": "agent_001", "drift_score": 0.65},
        source="test.monitor",
        effects=[SymbolicEffect.DRIFT_DETECT],
        priority=EventPriority.HIGH
    )
    print(f"  Triggered drift detection")
    
    # Test 4: Dream cycle with correlation
    print("\n💭 Test 4: Dream cycle with correlation")
    dream_id = "dream_" + str(int(time.time()))
    emit(
        "dream.cycle.started",
        {"dream_id": dream_id, "theme": "symbolic_test"},
        source="test.dreams",
        effects=[SymbolicEffect.DREAM_TRIGGER, SymbolicEffect.MEMORY_FOLD],
        correlation_id=dream_id
    )
    
    # Correlated event
    emit(
        "consciousness.state.changed",
        {"state": "dreaming", "dream_id": dream_id},
        source="test.consciousness",
        effects=[SymbolicEffect.AWARENESS_UPDATE],
        correlation_id=dream_id
    )
    print(f"  Started dream cycle: {dream_id}")
    
    # Test 5: Plugin loading
    print("\n🔌 Test 5: Plugin system update")
    emit(
        "plugin.loaded",
        {"name": "test_plugin", "version": "1.0.0"},
        source="test.plugins",
        effects=[SymbolicEffect.PLUGIN_LOAD, SymbolicEffect.PLUGIN_UPDATE]
    )
    print(f"  Plugin loaded event sent")
    
    # Test 6: Critical safety event
    print("\n🛡️ Test 6: Safety boundary check")
    emit(
        "safety.boundary.approached",
        {"boundary": "memory_limit", "distance": 0.05},
        source="test.safety",
        effects=[SymbolicEffect.SAFETY_GATE],
        priority=EventPriority.CRITICAL
    )
    print(f"  Safety boundary event (CRITICAL priority)")
    
    # Wait for events to process
    await asyncio.sleep(1)
    
    # Get metrics
    print("\n📊 Kernel Bus Metrics:")
    metrics = kernel_bus.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Get event history
    print("\n📜 Recent Event History:")
    history = kernel_bus.get_event_history(limit=5)
    for event in history:
        print(f"  - {event['event_type']} from {event['source']}")
    
    # Get correlation chain
    print(f"\n🔗 Correlation Chain for {dream_id}:")
    chain = kernel_bus.get_correlation_chain(dream_id)
    for event in chain:
        print(f"  - {event['event_type']} at {event['timestamp']}")
    
    # Stop the kernel bus
    await kernel_bus.stop()
    print("\n✅ Kernel bus stopped")
    
    print("\n" + "="*60)
    print("🎉 All tests completed successfully!")

def main():
    """Run the test"""
    asyncio.run(test_kernel_bus())

if __name__ == "__main__":
    main()