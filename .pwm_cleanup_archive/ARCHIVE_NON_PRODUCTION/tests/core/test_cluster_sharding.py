from core.cluster_sharding import ShardManager


def test_actor_assignment_and_move():
    manager = ShardManager(num_shards=3)
    shard = manager.assign_actor("actor1", {"value": 1})
    assert manager.get_actor_state("actor1") == {"value": 1}

    new_shard = (shard + 1) % 3
    manager.move_actor("actor1", new_shard)
    assert manager.get_actor_state("actor1") == {"value": 1}
    assert manager.get_shard_id("actor1") in manager.shards
