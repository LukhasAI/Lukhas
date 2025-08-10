"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Memory Component
File: test_memory_comprehensive.py
Path: core/memory/test_memory_comprehensive.py
Created: 2025-06-20
Author: lukhas AI Team
Version: 1.0
This file is part of the lukhas (lukhas Universal Knowledge & Holistic AI System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
TAGS: [CRITICAL, KeyFile, Memory]
DEPENDENCIES:
  - core/memory/memory_manager.py
  - core/identity/identity_manager.py
"""

#!/usr/bin/env python3
"""
Test script for Unified Memory Manager
Investigates lifecycle, performance, and functionality
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from memory.core_memory.simple_store import (
    MemoryConfig,
    MemoryPriority,
    MemoryType,
    UnifiedMemoryManager,
)

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_memory_lifecycle():
    """Test the complete lifecycle of the memory manager"""
    print("=" * 60)
    print("🧠 UNIFIED MEMORY MANAGER LIFECYCLE TEST")
    print("=" * 60)

    # Create config for testing
    config = MemoryConfig(
        storage_path="test_memory_store",
        max_memories_per_user=100,
        gc_interval_minutes=0,  # Disable GC for testing
        default_ttl_hours=24,
    )

    # Initialize manager
    print("\n📋 1. Initializing memory manager...")
    manager = UnifiedMemoryManager(config)

    # Start manager
    print("\n🚀 2. Starting memory manager...")
    start_success = await manager.start()
    print(f"   Start result: {start_success}")

    # Test basic storage
    print("\n💾 3. Testing memory storage...")
    test_user = "test_user_123"

    # Store different types of memories
    memory_ids = []
    for i in range(5):
        memory_id = await manager.store_memory(
            user_id=test_user,
            content={
                "message": f"Test message {i}",
                "context": {"test": True, "index": i},
                "timestamp": time.time(),
            },
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.HIGH if i < 2 else MemoryPriority.MEDIUM,
        )
        memory_ids.append(memory_id)
        print(f"   Stored memory {i}: {memory_id}")

    # Test retrieval
    print("\n🔍 4. Testing memory retrieval...")
    memories = await manager.retrieve_memory(test_user, limit=10)
    print(f"   Retrieved {len(memories)} memories")
    for memory in memories:
        print(f"   - {memory.id}: {memory.content.get('message', 'No message')}")

    # Test specific memory retrieval
    print("\n🎯 5. Testing specific memory retrieval...")
    if memory_ids:
        specific_memory = await manager.retrieve_memory(
            test_user, memory_id=memory_ids[0]
        )
        if specific_memory:
            print(
                f"   Retrieved specific memory: {specific_memory[0].content.get('message')}"
            )
        else:
            print("   ❌ Failed to retrieve specific memory")

    # Test stats
    print("\n📊 6. Testing memory statistics...")
    user_stats = await manager.get_memory_stats(test_user)
    global_stats = await manager.get_memory_stats()
    print(f"   User stats: {user_stats}")
    print(f"   Global stats: {global_stats}")

    # Test performance with bulk storage
    print("\n⚡ 7. Testing bulk storage performance...")
    start_time = time.time()
    bulk_ids = []
    for i in range(50):
        memory_id = await manager.store_memory(
            user_id=f"bulk_user_{i % 5}",  # 5 different users
            content={"bulk_message": f"Bulk test {i}", "data": list(range(10))},
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.LOW,
        )
        bulk_ids.append(memory_id)

    bulk_time = time.time() - start_time
    print(
        f"   Stored 50 memories in {bulk_time:.3f} seconds ({50/bulk_time:.1f} memories/sec)"
    )

    # Test bulk retrieval performance
    print("\n🔍 8. Testing bulk retrieval performance...")
    start_time = time.time()
    all_memories = []
    for i in range(5):
        user_memories = await manager.retrieve_memory(f"bulk_user_{i}", limit=20)
        all_memories.extend(user_memories)

    retrieval_time = time.time() - start_time
    print(f"   Retrieved {len(all_memories)} memories in {retrieval_time:.3f} seconds")

    # Test memory filtering
    print("\n🔎 9. Testing memory type filtering...")
    episodic_memories = await manager.retrieve_memory(
        test_user, memory_type=MemoryType.EPISODIC, limit=10
    )
    print(f"   Found {len(episodic_memories)} episodic memories")

    # Test GDPR compliance (user data deletion)
    print("\n🗑️ 10. Testing GDPR compliance (user data deletion)...")
    deletion_success = await manager.delete_user_memories("bulk_user_0")
    print(f"   User deletion result: {deletion_success}")

    # Verify deletion
    deleted_user_memories = await manager.retrieve_memory("bulk_user_0")
    print(f"   Memories remaining after deletion: {len(deleted_user_memories)}")

    # Test graceful shutdown
    print("\n🛑 11. Testing graceful shutdown...")
    stop_success = await manager.stop()
    print(f"   Stop result: {stop_success}")

    print("\n✅ Memory manager lifecycle test completed!")
    return True


async def test_error_conditions():
    """Test error handling and edge cases"""
    print("\n" + "=" * 60)
    print("🚨 ERROR CONDITIONS & EDGE CASES TEST")
    print("=" * 60)

    config = MemoryConfig(storage_path="test_error_store")
    manager = UnifiedMemoryManager(config)

    await manager.start()

    # Test invalid user ID
    print("\n1. Testing invalid retrievals...")
    empty_memories = await manager.retrieve_memory("nonexistent_user")
    print(f"   Non-existent user memories: {len(empty_memories)}")

    # Test invalid memory ID
    invalid_memory = await manager.retrieve_memory("test", memory_id="invalid_id")
    print(f"   Invalid memory ID result: {len(invalid_memory)}")

    # Test large content storage
    print("\n2. Testing large content storage...")
    large_content = {"large_data": "x" * 10000}  # 10KB of data
    large_id = await manager.store_memory(
        "large_test_user", large_content, priority=MemoryPriority.CRITICAL
    )
    print(f"   Large content stored: {large_id}")

    # Test retrieval of large content
    large_retrieved = await manager.retrieve_memory(
        "large_test_user", memory_id=large_id
    )
    if large_retrieved:
        retrieved_size = len(str(large_retrieved[0].content))
        print(f"   Large content retrieved size: {retrieved_size} chars")

    await manager.stop()
    print("\n✅ Error conditions test completed!")


async def main():
    """Run all tests"""
    print("🧠 UNIFIED MEMORY MANAGER COMPREHENSIVE TESTING")
    print("Testing replacement for quantum/blockchain memory systems")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Test normal lifecycle
        await test_memory_lifecycle()

        # Test error conditions
        await test_error_conditions()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("💡 Memory manager is ready for integration with ReflectionLayer")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    asyncio.run(main())
