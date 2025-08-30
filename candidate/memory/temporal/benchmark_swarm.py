"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Benchmarking utility for Symbiotic Swarm actor/event bus system.
Measures message throughput and demonstrates energy-efficient computation.
"""

import asyncio
import time

from event_bus import *  # TODO: Specify imports
from minimal_actor import *  # TODO: Specify imports


def bench_behavior(actor, message):
    """Simple benchmark message handler."""
    # Simulate lightweight processing
    actor.state["count"] = actor.state.get("count", 0) + 1


def event_to_actor_bridge(actor):
    """Create a bridge function from event bus to actor."""

    def handle_event(event):
        actor.send(event.payload)

    return handle_event


async def run_benchmark(num_actors=1000, num_messages=10000):
    """Run async benchmark test."""
    bus = await get_global_event_bus()
    actors = []

    # Create actors and bridge them to event bus
    for i in range(num_actors):
        actor = Actor(bench_behavior)
        bridge = event_to_actor_bridge(actor)
        bus.subscribe("bench", bridge)
        actors.append(actor)

    start = time.time()

    # Publish messages
    for i in range(num_messages):
        await bus.publish("bench", {"msg_id": i, "data": f"msg-{i}"})

    # Wait for all messages to be processed
    await asyncio.sleep(2)

    total_processed = sum(a.state.get("count", 0) for a in actors)
    elapsed = time.time() - start

    print(f"Actors: {num_actors}, Messages: {num_messages}")
    print(f"Processed: {total_processed}, Time: {elapsed:.2f}s")
    print(f"Throughput: {total_processed / elapsed:.2f} messages/sec")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
    asyncio.run(run_benchmark())
