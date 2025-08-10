import asyncio

from symbolic.swarm_tag_simulation import simulate_swarm


def test_simulate_swarm_small_event_loop():
    metrics = asyncio.run(
        simulate_swarm(num_agents=50, rounds=2, high_trust_filter=True)
    )
    assert metrics["agents"] == 50
    assert metrics["collisions"] >= 0
    assert metrics["consensus_tags"] >= 0
