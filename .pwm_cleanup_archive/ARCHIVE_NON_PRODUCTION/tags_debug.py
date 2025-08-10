"""
A simple tag visualizer for debugging tag propagation.
"""

import asyncio
import sys

sys.path.append(".")
from core.colonies.reasoning_colony import ReasoningColony


async def main():
    """
    A simple demo of the tag visualizer.
    """
    print("🚀 Starting Tag Visualizer Demo")
    print("=" * 60)

    colony = ReasoningColony("test_colony")
    await colony.start()

    task_data = {
        "type": "test_task",
        "tags": {
            "emotional_tone": ("curious", "local"),
            "directive_hash": ("a1b2c3d4", "global"),
        },
    }

    await colony.execute_task("test_task_id", task_data)

    print("\n--- Tag Propagation Log ---")
    for log_entry in colony.tag_propagation_log:
        print(
            f"[{log_entry['timestamp']}] "
            f"Tag: {log_entry['tag']}, "
            f"Value: {log_entry['value']}, "
            f"Source: {log_entry['source']}"
        )

    await colony.stop()

    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
