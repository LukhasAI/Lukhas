# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Remove unused deprecated List, Dict imports in dream simulator
# estimate: 5min | priority: medium | dependencies: core-dream-system

# core/dream/simulator.py
"""
A deterministic, small dream simulator for validation/demos.
Replace the embedding stub with a real embedding model in prod.
"""
import numpy as np
from typing import Any
import hashlib
import json

def _deterministic_vector(text: str, dim: int = 128, seed: int = 0) -> np.ndarray:
    # seed derived from text to make repeatable pseudo-embeddings
    h = hashlib.sha256((text + str(seed)).encode("utf-8")).digest()
    rng_seed = int.from_bytes(h[:8], "big")
    rng = np.random.RandomState(rng_seed % (2**32))
    v = rng.normal(size=(dim,))
    # normalize to unit vector
    v = v / (np.linalg.norm(v) + 1e-12)
    return v.astype(np.float32)

def semantic_distance(a: np.ndarray, b: np.ndarray) -> float:
    # cosine distance: 1 - cosine_similarity
    cos = np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12)
    return 1.0 - float(np.clip(cos, -1.0, 1.0))

class DreamCycle:
    def __init__(self, prompt: str, seed: int = 0):
        self.prompt = prompt
        self.seed = seed
        self.response = None
        self.embedding = None

    def run(self) -> Dict[str, Any]:
        # Simplified: "dream" = seed-influenced paraphrase (placeholder)
        self.response = f"DREAM_RESPONSE({self.prompt[:60]})_seed={self.seed}"
        self.embedding = _deterministic_vector(self.response, seed=self.seed)
        return {"response": self.response, "embedding": self.embedding}

class DreamSimulator:
    def __init__(self, dim: int = 128):
        self.dim = dim

    def run_cycle(self, prompt: str, seed: int = 0):
        c = DreamCycle(prompt, seed)
        return c.run()

def measure_drift(responses_a: List[np.ndarray], responses_b: List[np.ndarray]) -> float:
    # compute mean pairwise distance between corresponding embeddings
    if not responses_a or not responses_b or len(responses_a) != len(responses_b):
        raise ValueError("Need two same-length lists of embeddings")
    ds = [semantic_distance(a, b) for a, b in zip(responses_a, responses_b)]
    return float(np.mean(ds))
