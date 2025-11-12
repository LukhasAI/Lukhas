# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for resonance mesh processing
# estimate: 10min | priority: high | dependencies: none

# core/mesh/resonance.py
import numpy as np
import json
from typing import Any
import hashlib

def glyph_hash(glyph: dict[str, Any]) -> str:
    s = json_canonical(glyph)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def json_canonical(o: dict):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))

def glyph_embedding_from_hash(h: str, dim: int = 128) -> np.ndarray:
    # deterministic embedding from hex fingerprint
    seed = int(h[:16], 16) % (2**32)
    rng = np.random.RandomState(seed)
    v = rng.normal(size=(dim,))
    return v / (np.linalg.norm(v) + 1e-12)

def resonance_score(glyph_hashes: list[str]) -> float:
    # score = mean pairwise cosine similarity of glyph embeddings (0..1)
    if len(glyph_hashes) < 2:
        return 1.0
    embs = [glyph_embedding_from_hash(h) for h in glyph_hashes]
    sims = []
    for i in range(len(embs)):
        for j in range(i+1, len(embs)):
            a = embs[i]
            b = embs[j]
            sims.append(float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-12)))
    return float(np.mean(sims))

def resonance_snapshot(glyphs: list[dict]) -> dict:
    hashes = [glyph_hash(g) for g in glyphs]
    score = resonance_score(hashes)
    return {"glyph_hashes": hashes, "score": score}
