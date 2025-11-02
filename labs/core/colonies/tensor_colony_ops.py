"""Vectorized colony operations using PyTorch tensors."""

from __future__ import annotations

import time

import torch

from core.colonies.base_colony import BaseColony
from core.symbolism.tags import TagPermission, TagScope
from tagging import SimpleTagResolver

# ΛTAG: vectorized_tag_ops
# Provides GPU-optional batched tag propagation and reasoning utilities.

# Resolver for symbolic tag vectors
_resolver = SimpleTagResolver()
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def tags_to_tensor(
    tag_data: dict[str, tuple[str, TagScope, TagPermission, float]],
) -> torch.Tensor:
    """Convert tag values to a tensor for batched processing."""
    vectors = [_resolver.resolve_tag(value).vector for value, _scope, _perm, _ in tag_data.values()]
    tensor = torch.tensor(vectors, dtype=torch.float32, device=_device)
    return tensor


def batch_propagate(
    colonies: list[BaseColony],
    tag_data: dict[str, tuple[str, TagScope, TagPermission, float]],
) -> None:
    """Propagate tags to multiple colonies via tensor broadcast."""
    tag_tensor = tags_to_tensor(tag_data)
    for colony in colonies:
        for (tag_key, (_, scope, perm, lifespan)), vector in zip(tag_data.items(), tag_tensor):
            creation_time = time.time()
            colony.symbolic_carryover[tag_key] = (
                vector.cpu().tolist(),
                scope,
                perm,
                creation_time,
                lifespan,
            )
            colony.tag_propagation_log.append(
                {
                    "tag": tag_key,
                    "value": vector.cpu().tolist(),
                    "scope": scope.value,
                    "permission": perm.value,
                    "source": "batched",
                    "timestamp": creation_time,
                    "lifespan": lifespan,
                }
            )


def colony_reasoning_tensor(colony_vectors: torch.Tensor) -> torch.Tensor:
    """Simple tensor-based reasoning placeholder."""
    # ΛTAG: colony_tensor_reasoning
    return torch.matmul(colony_vectors, colony_vectors.T)


def simulate_throughput(colony_vectors: torch.Tensor, steps: int = 10) -> list[float]:
    """Run a throughput simulation and return processing times."""
    timings: list[float] = []
    for _ in range(steps):
        start = time.time()
        _ = colony_reasoning_tensor(colony_vectors)
        timings.append(time.time() - start)
    return timings


def plot_throughput(timings: list[float]) -> None:
    """Visualize throughput timings."""
    import matplotlib.pyplot as plt

    plt.plot(timings, marker="o")
    plt.xlabel("Step")
    plt.ylabel("Time (s)")
    plt.title("Colony Reasoning Throughput")
    plt.tight_layout()
    plt.show()


class TensorColonyOps:
    """Tensor-based colony operations class"""

    def __init__(self):
        self.device = _device
        self.resolver = _resolver

    def tags_to_tensor(self, tag_data):
        """Convert tag data to tensor"""
        return tags_to_tensor(tag_data)

    def batch_propagate(self, colonies):
        """Batch propagate across colonies"""
        return batch_propagate(colonies)

    def colony_reasoning_tensor(self, colony_vectors):
        """Perform tensor-based reasoning"""
        return colony_reasoning_tensor(colony_vectors)

    def simulate_throughput(self, colony_vectors, steps=10):
        """Run throughput simulation"""
        return simulate_throughput(colony_vectors, steps)


__all__ = [
    "TensorColonyOps",
    "tags_to_tensor",
    "batch_propagate",
    "colony_reasoning_tensor",
    "simulate_throughput",
    "plot_throughput",
]
