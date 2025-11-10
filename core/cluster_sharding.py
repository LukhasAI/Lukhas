"""Bridge module for core.cluster_sharding → labs.core.cluster_sharding"""
from __future__ import annotations

from labs.core.cluster_sharding import ClusterShard, ShardManager, shard_cluster

__all__ = ["ClusterShard", "ShardManager", "shard_cluster"]
