"""Vectorized colony operations using PyTorch tensors."""

from __future__ import annotations

import time

import torch

from lukhas.core.colonies.base_colony import BaseColony
from lukhas.core.symbolism.tags import TagPermission, TagScope
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
    """
    Vectorized operations for colony management using PyTorch tensors.
    
    Provides high-performance batched operations for managing multiple
    colonies and their symbolic tag propagation.
    """
    
    def __init__(self, device: str = "auto"):
        """
        Initialize TensorColonyOps
        
        Args:
            device: Device to use ("cpu", "cuda", or "auto")
        """
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        self.resolver = SimpleTagResolver()
        self.colonies: list[BaseColony] = []
    
    def add_colony(self, colony: BaseColony) -> None:
        """Add a colony to the tensor operations manager"""
        self.colonies.append(colony)
    
    def batch_propagate_tags(
        self,
        tag_data: dict[str, tuple[str, TagScope, TagPermission, float]]
    ) -> None:
        """Propagate tags to all managed colonies using tensor operations"""
        batch_propagate(self.colonies, tag_data)
    
    def compute_colony_similarity(self) -> torch.Tensor:
        """Compute similarity matrix between colonies"""
        if not self.colonies:
            return torch.tensor([], device=self.device)
        
        # Extract colony feature vectors (placeholder implementation)
        vectors = []
        for colony in self.colonies:
            # Create feature vector from colony's symbolic carryover
            features = []
            for tag_data in colony.symbolic_carryover.values():
                if isinstance(tag_data, tuple) and len(tag_data) > 0:
                    if isinstance(tag_data[0], list):
                        features.extend(tag_data[0][:10])  # Take first 10 elements
                    else:
                        features.append(float(hash(str(tag_data)) % 1000) / 1000)
            
            # Pad or truncate to fixed size
            target_size = 64
            if len(features) < target_size:
                features.extend([0.0] * (target_size - len(features)))
            else:
                features = features[:target_size]
            
            vectors.append(features)
        
        if not vectors:
            return torch.tensor([], device=self.device)
        
        colony_vectors = torch.tensor(vectors, dtype=torch.float32, device=self.device)
        return colony_reasoning_tensor(colony_vectors)
    
    def get_performance_metrics(self, steps: int = 10) -> dict[str, float]:
        """Get performance metrics for tensor operations"""
        if not self.colonies:
            return {"avg_time": 0.0, "throughput": 0.0}
        
        # Create dummy vectors for performance testing
        dummy_vectors = torch.randn(len(self.colonies), 64, device=self.device)
        timings = simulate_throughput(dummy_vectors, steps)
        
        return {
            "avg_time": sum(timings) / len(timings),
            "min_time": min(timings),
            "max_time": max(timings),
            "throughput": len(self.colonies) / (sum(timings) / len(timings)),
            "device": str(self.device)
        }
