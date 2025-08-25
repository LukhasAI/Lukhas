"""
LUKHAS Memory - Basic HybridMemoryFold Example
==============================================

This script demonstrates the basic usage of the HybridMemoryFold class
to store and retrieve memories using tags and semantic search.
"""

import sys
import os
import asyncio
import numpy as np

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

# Mock logger for the example
class Logger:
    def info(self, *args, **kwargs):
        print(f"INFO: {args} {kwargs}")

    def warning(self, *args, **kwargs):
        print(f"WARNING: {args} {kwargs}")

    def error(self, *args, **kwargs):
        print(f"ERROR: {args} {kwargs}")

    def debug(self, *args, **kwargs):
        print(f"DEBUG: {args} {kwargs}")

logger = Logger()

try:
    from candidate.memory.fold_system.memory_fold import HybridMemoryFold, MemoryItem
except ImportError as e:
    print(f"Error: Could not import HybridMemoryFold: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


async def main():
    """
    Demonstrates basic HybridMemoryFold functionality.
    """
    print("--- LUKHAS Memory: Basic HybridMemoryFold Example ---")

    # 1. Instantiate the HybridMemoryFold
    print("\n1. Instantiating HybridMemoryFold...")
    memory = HybridMemoryFold(embedding_dim=128)
    print("   - Memory system instantiated.")

    # 2. Fold in some memories
    print("\n2. Folding in some memories...")
    await memory.fold_in_with_embedding(
        data={"content": "The sky is blue."},
        tags=["nature", "color", "sky"],
        text_content="The sky is blue."
    )
    await memory.fold_in_with_embedding(
        data={"content": "The ocean is vast and blue."},
        tags=["nature", "water", "ocean"],
        text_content="The ocean is vast and blue."
    )
    await memory.fold_in_with_embedding(
        data={"content": "A red apple is a healthy snack."},
        tags=["food", "fruit", "color", "apple"],
        text_content="A red apple is a healthy snack."
    )
    print("   - Memories folded in.")

    # 3. Fold out memories by tag
    print("\n3. Folding out memories by tag 'color'...")
    color_memories = await memory.fold_out_by_tag("color")
    print(f"   - Found {len(color_memories)} memories with tag 'color':")
    for mem, score in color_memories:
        print(f"     - ID: {mem.item_id}, Content: {mem.data['content']}")

    # 4. Fold out memories by semantic search
    print("\n4. Folding out memories by semantic search for 'blue things'...")
    blue_things_memories = await memory.fold_out_semantic("blue things")
    print(f"   - Found {len(blue_things_memories)} memories related to 'blue things':")
    for mem, score in blue_things_memories:
        print(f"     - ID: {mem.item_id}, Score: {score:.2f}, Content: {mem.data['content']}")

    # 5. Get statistics
    print("\n5. Getting memory statistics...")
    stats = memory.get_enhanced_statistics()
    print(f"   - Total items: {stats['total_items']}")
    print(f"   - Total tags: {stats['total_tags']}")
    print(f"   - Total vectors: {stats['vector_stats']['total_vectors']}")


    print("\n--- Example Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
