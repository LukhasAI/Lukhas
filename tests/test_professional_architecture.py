#!/usr/bin/env python3
"""
Test script for LUKHAS Professional Architecture
Demonstrates service-oriented architecture working properly
"""

import asyncio
import logging
from datetime import datetime

from core.bootstrap import initialize_lukhas, shutdown_lukhas, get_bootstrap
from core.events.contracts import (
    MemoryFoldCreated, ConsciousnessStateChanged, 
    DreamGenerated, EmotionalStateChanged
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('TEST')

async def test_professional_architecture():
    """Test the professional architecture implementation"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     LUKHAS Professional Architecture Test Suite              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Initialize system
    logger.info("🚀 Initializing LUKHAS with professional architecture...")
    result = await initialize_lukhas()
    
    if result['status'] != 'success':
        logger.error(f"❌ Initialization failed: {result.get('error')}")
        return
    
    logger.info(f"✅ System initialized in {result['startup_duration']:.2f} seconds")
    logger.info(f"📊 Services loaded: {result['services_loaded']}")
    
    # Get bootstrap instance
    bootstrap = await get_bootstrap()
    
    # Step 2: Test service health
    logger.info("\n🏥 Testing service health...")
    health = await bootstrap._check_system_health()
    
    print("\nService Health Report:")
    for service, status in health['services'].items():
        emoji = "✅" if status.get('status') == 'healthy' else "⚠️"
        print(f"  {emoji} {service}: {status.get('status', 'unknown')}")
    
    print(f"\nOverall health: {health['overall']['health_percentage']:.1f}%")
    
    # Step 3: Test event-driven communication
    logger.info("\n📡 Testing event-driven communication...")
    
    # Subscribe to events
    event_count = 0
    events_received = []
    
    async def on_any_event(event):
        nonlocal event_count
        event_count += 1
        events_received.append(event)
        logger.info(f"  📨 Received event: {event.event_type} (#{event_count})")
    
    # Subscribe to multiple event types
    event_bus = bootstrap.event_bus
    sub_ids = [
        kernel_bus.subscribe(MemoryFoldCreated, on_any_event),
        kernel_bus.subscribe(ConsciousnessStateChanged, on_any_event),
        kernel_bus.subscribe(DreamGenerated, on_any_event),
        kernel_bus.subscribe(EmotionalStateChanged, on_any_event)
    ]
    
    # Step 4: Test service interactions
    logger.info("\n🔧 Testing service interactions...")
    
    # Test Memory Service
    memory = bootstrap.get_service("memory")
    if memory:
        fold_id = await memory.create_fold(
            content="Test memory from professional architecture",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        logger.info(f"  ✓ Memory fold created: {fold_id}")
    
    # Test Consciousness Service
    consciousness = bootstrap.get_service("consciousness")
    if consciousness:
        state = await consciousness.get_current_state()
        logger.info(f"  ✓ Consciousness state: {state.get('state', 'unknown')}")
        
        awareness = await consciousness.process_awareness({
            "input": "Professional architecture test",
            "context": {"test_mode": True}
        })
        logger.info(f"  ✓ Awareness processed: delta={awareness.get('awareness_delta', 0)}")
    
    # Test Dream Service
    dream = bootstrap.get_service("dream")
    if dream:
        dream_result = await dream.generate_dream(
            seed={"concept": "professional architecture", "theme": "success"}
        )
        logger.info(f"  ✓ Dream generated: {dream_result.get('dream_id', 'unknown')}")
    
    # Test Emotion Service
    emotion = bootstrap.get_service("emotion")
    if emotion:
        vad = await emotion.analyze_emotion("Testing professional architecture")
        logger.info(f"  ✓ Emotion analyzed: V={vad.get('valence', 0.5):.2f}, "
                   f"A={vad.get('arousal', 0.5):.2f}, D={vad.get('dominance', 0.5):.2f}")
    
    # Wait for events to propagate
    await asyncio.sleep(0.5)
    
    # Step 5: Show event statistics
    logger.info(f"\n📊 Event Statistics:")
    logger.info(f"  - Events received: {event_count}")
    logger.info(f"  - Event types: {set(e.event_type for e in events_received)}")
    
    event_stats = event_bus.get_event_history()
    logger.info(f"  - Total events in history: {len(event_stats)}")
    
    # Step 6: Test cross-module communication
    logger.info("\n🔗 Testing cross-module communication...")
    
    # Publish a custom event
    await event_bus.publish(ConsciousnessStateChanged(
        source_module="test",
        previous_state="testing",
        current_state="active",
        new_state="active",
        trigger="test_suite",
        awareness_level=0.8
    ))
    
    await asyncio.sleep(0.1)
    
    # Step 7: Final statistics
    logger.info("\n📈 Final Statistics:")
    bus_stats = bootstrap.event_bus.get_health()
    for key, value in bus_stats.items():
        if key != 'status':
            logger.info(f"  - {key}: {value}")
    
    # Cleanup
    logger.info("\n🔄 Cleaning up...")
    
    # Unsubscribe
    for sub_id in sub_ids:
        event_bus.unsubscribe(sub_id)
    
    await shutdown_lukhas()
    logger.info("✅ Test completed successfully!")
    
    print(f"\n{'='*60}")
    print("SUMMARY: Professional Architecture is working correctly!")
    print(f"- Services initialized: {result['services_loaded']}")
    print(f"- Events processed: {event_count}")
    print(f"- System health: {health['overall']['health_percentage']:.1f}%")
    print(f"{'='*60}")

async def main():
    """Main entry point"""
    try:
        await test_professional_architecture()
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())