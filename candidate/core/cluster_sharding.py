import logging
from typing import Any, Optional

# ΛTAG: cluster_sharding
logger = logging.getLogger("ΛTRACE.cluster_sharding")


class ShardManager:
    """Lightweight shard manager for distributing actors across nodes."""

    def __init__(self, num_shards: int = 10):
        self.num_shards = num_shards
        self.shards: dict[int, dict[str, Any]] = {i: {} for i in range(num_shards)}
        logger.info(f"ΛTRACE: ShardManager initialized with {num_shards} shards")

    def get_shard_id(self, actor_id: str) -> int:
        """Compute shard ID for a given actor."""
        return hash(actor_id) % self.num_shards

    def assign_actor(self, actor_id: str, state: Optional[dict[str, Any]] = None) -> int:
        """Assign an actor to its shard."""
        shard_id = self.get_shard_id(actor_id)
        self.shards[shard_id][actor_id] = state or {}
        logger.debug(f"ΛTRACE: Actor assigned - actor_id={actor_id}, shard_id={shard_id}")
        return shard_id

    def move_actor(self, actor_id: str, new_shard_id: int) -> None:
        """Move an actor to a new shard (e.g., after node failure)."""
        for actors in self.shards.values():
            if actor_id in actors:
                state = actors.pop(actor_id)
                self.shards[new_shard_id][actor_id] = state
                logger.info(f"ΛTRACE: Actor moved - actor_id={actor_id}, shard_id={new_shard_id}")
                return

    def get_actor_state(self, actor_id: str) -> Optional[dict[str, Any]]:
        """Retrieve actor state regardless of current shard."""
        shard_id = self.get_shard_id(actor_id)
        state = self.shards[shard_id].get(actor_id)
        if state is not None:
            return state

        # Search other shards if actor was rebalanced
        for actors in self.shards.values():
            if actor_id in actors:
                return actors[actor_id]
        return None
