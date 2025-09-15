#TAG:temporal
#TAG:neuroplastic
#TAG:colony

"""Benchmark utilities for the Symbiotic Swarm actor/event bus system.

Measures message throughput and demonstrates energy-efficient computation.
"""

import asyncio
import time
from typing import Any, Callable

from ...core.event_bus import Event, get_global_event_bus
from ...core.minimal_actor import Actor


def bench_behavior(actor: Actor, message: dict[str, Any]) -> None:
    """Increment an actor's message counter.

    Args:
        actor: Actor instance handling the message.
        message: Incoming message payload.
    """
    actor.state["count"] = actor.state.get("count", 0) + 1


def event_to_actor_bridge(actor: Actor) -> Callable[[Event], None]:
    """Create an event-to-actor bridge handler.

    Args:
        actor: Actor that should receive event payloads.

    Returns:
        Callable[[Event], None]: Function forwarding event payloads to the actor.
    """

    def handle_event(event: Event) -> None:
        actor.send(event.payload)

    return handle_event


async def run_benchmark(num_actors: int = 1000, num_messages: int = 10000) -> None:
    """Run an asynchronous throughput benchmark.

    Args:
        num_actors: Number of actors to spawn.
        num_messages: Number of messages to publish.
    """
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
