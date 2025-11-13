# MATRIZ Phase‑1 scaffolding: N01–N03 nodes, tests, compose stub

## 1) Branch + PR boilerplate

> **Branch name:** `feat/matriz-phase1-scaffolding-tests-compose`
> **Scope:** Shared base/contracts, N01 Working Memory, N02 Attention Controller, N03 Episodic Memory; 3 unit test files; 1 integration test; compose stub; optional config.
> **Guarantees:** Typed, lane‑safe, small blast radius, easy rollback.

```bash
# Create branch
git checkout -b feat/matriz-phase1-scaffolding-tests-compose

# Create directories
mkdir -p MATRIZ/nodes/phase1 lukhas/orchestrator tests/matriz/phase1 tests/integration config/matriz

# (Paste the code blocks below into the listed files)

# Stage & commit
git add MATRIZ/nodes/phase1/*.py lukhas/orchestrator/matriz_phase1.py \
        tests/matriz/phase1/*.py tests/integration/test_matriz_phase1_compose.py \
        config/matriz/phase1.yml
git commit -m "feat(matriz): Phase‑1 scaffolding N01–N03 (typed base, tests, compose)"

# Push & open PR (draft)
git push -u origin feat/matriz-phase1-scaffolding-tests-compose
gh pr create --base main --head feat/matriz-phase1-scaffolding-tests-compose \
  --title "feat(matriz): Phase‑1 scaffolding N01–N03 (typed base, tests, compose)" \
  --body "Introduce typed base contracts, WaveC/event hooks, and skeleton nodes/tests for Working Memory, Attention Controller, and Episodic Memory. Add compose stub and integration smoke test. Safe, lane‑clean, and reversible." \
  --label "phase-1" --label "node" --label "migration/matriz" --draft
```

---

## 2) Strong foundation (shared contracts & hooks)

> Paths:
> `MATRIZ/nodes/phase1/base.py` • `MATRIZ/nodes/phase1/events.py` • `MATRIZ/nodes/phase1/__init__.py`

**MATRIZ/nodes/phase1/base.py**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Any, Dict, Mapping

@dataclass(frozen=True)
class NodeContext:
    """
    Immutable per-cycle context passed into every node.
    Budget fields are advisory limits; nodes should instrument themselves.
    """
    run_id: str
    cycle_idx: int
    seed: int
    latency_budget_ms: int = 20
    memory_budget_bytes: int = 1_000_000

@dataclass
class NodeMetrics:
    p95_ms: float = 0.0
    rss_bytes: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)

class Node(Protocol):
    """Minimal contract all Phase‑1 nodes implement."""
    name: str
    def configure(self, **kwargs: Any) -> None: ...
    def warmup(self, ctx: NodeContext) -> None: ...
    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]: ...
    def metrics(self) -> NodeMetrics: ...

class NodeRegistry:
    """Simple registry to resolve nodes by name; used by compose stub."""
    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}

    def register(self, node: Node) -> None:
        if node.name in self._nodes:
            raise ValueError(f"duplicate node: {node.name}")
        self._nodes[node.name] = node

    def get(self, name: str) -> Node:
        return self._nodes[name]

    def all(self) -> Mapping[str, Node]:
        return dict(self._nodes)
```

**MATRIZ/nodes/phase1/events.py**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class NodeEvent:
    node: str
    run_id: str
    cycle_idx: int
    payload: Dict[str, Any]

def emit_event(evt: NodeEvent) -> None:
    """
    Hook: integrate with core.events.typed_event_bus.
    For now, it’s a no-op so tests remain hermetic.
    """
    # TODO: wire to event bus when available
    pass

def wavec_checkpoint(run_id: str, cycle_idx: int, memory_state: Dict[str, Any]) -> None:
    """
    Hook: integrate with WaveC snapshot store (gzip+sha256+TTL).
    Tests will monkeypatch this function to assert it was called.
    """
    # TODO: persist snapshot in WaveC service when available
    pass
```

**MATRIZ/nodes/phase1/**init**.py**

```python
from .base import Node, NodeContext, NodeRegistry, NodeMetrics
from .working_memory import WorkingMemory
from .attention_controller import AttentionController
from .episodic_memory import EpisodicMemory

__all__ = [
    "Node", "NodeContext", "NodeRegistry", "NodeMetrics",
    "WorkingMemory", "AttentionController", "EpisodicMemory",
]
```

---

## 3) Phase‑1 N01–N03 node skeletons (executable stubs)

> Paths:
> `MATRIZ/nodes/phase1/working_memory.py` • `MATRIZ/nodes/phase1/attention_controller.py` • `MATRIZ/nodes/phase1/episodic_memory.py`

**MATRIZ/nodes/phase1/working_memory.py**  *(N01)*

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from .base import Node, NodeContext, NodeMetrics
from .events import NodeEvent, emit_event

@dataclass
class WorkingMemory(Node):
    """
    Bounded, recency-biased store (7±2 by default).
    Exposes simple push semantics via `item=...` in process().
    """
    name: str = "working_memory"
    capacity: int = 7
    _items: List[Dict[str, Any]] = field(default_factory=list)
    _metrics: NodeMetrics = field(default_factory=NodeMetrics)

    def configure(self, **kwargs: Any) -> None:
        self.capacity = int(kwargs.get("capacity", self.capacity))

    def warmup(self, ctx: NodeContext) -> None:
        self._items.clear()

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        item = inputs.get("item")
        if item is not None:
            self._items.append(item)
            if len(self._items) > self.capacity:
                # Simple eviction: drop oldest
                self._items.pop(0)
                self._metrics.counters["wm_evictions"] = self._metrics.counters.get("wm_evictions", 0) + 1
        emit_event(NodeEvent(node=self.name, run_id=ctx.run_id, cycle_idx=ctx.cycle_idx,
                             payload={"size": len(self._items)}))
        return {"wm_items": list(self._items)}

    def metrics(self) -> NodeMetrics:
        return self._metrics
```

**MATRIZ/nodes/phase1/attention_controller.py**  *(N02)*

```python
from __future__ import annotations
import math
from typing import Any, Dict, List
from .base import Node, NodeContext, NodeMetrics

class AttentionController(Node):
    """
    Central resource allocator.
    Inputs: scores: List[float]
    Outputs: indices of top‑k attended items and entropy (diagnostic).
    """
    name: str = "attention_controller"

    def __init__(self, top_k: int = 3, temperature: float = 1.0) -> None:
        self.top_k = top_k
        self.temperature = temperature
        self._m = NodeMetrics(counters={"conflicts": 0}, gauges={"entropy": 0.0})

    def configure(self, **kwargs: Any) -> None:
        self.top_k = int(kwargs.get("top_k", self.top_k))
        self.temperature = float(kwargs.get("temperature", self.temperature))

    def warmup(self, ctx: NodeContext) -> None:
        # nothing to reset yet
        pass

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        scores: List[float] = inputs.get("scores", [])
        if not scores:
            return {"attn": [], "entropy": 0.0}
        probs = self._softmax(scores, self.temperature)
        entropy = -sum(p * math.log(max(p, 1e-9)) for p in probs)
        self._m.gauges["entropy"] = float(entropy)
        # Select top‑k indices
        top = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[: self.top_k]
        return {"attn": top, "entropy": float(entropy)}

    def metrics(self) -> NodeMetrics:
        return self._m

    @staticmethod
    def _softmax(x: List[float], t: float) -> List[float]:
        t = max(t, 1e-6)
        ex = [math.exp(v / t) for v in x]
        s = sum(ex) or 1.0
        return [v / s for v in ex]
```

**MATRIZ/nodes/phase1/episodic_memory.py**  *(N03)*

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .base import Node, NodeContext, NodeMetrics
from .events import NodeEvent, emit_event

@dataclass
class EpisodicMemory(Node):
    """
    Append‑only autobiographical episodes with time/context/affect.
    process(...):
      - append: bool = True -> appends {'time','context','affect','payload'}
      - query_last: int -> returns last N episodes (most recent last)
    """
    name: str = "episodic_memory"
    _episodes: List[Dict[str, Any]] = field(default_factory=list)
    _m: NodeMetrics = field(default_factory=NodeMetrics)

    def configure(self, **kwargs: Any) -> None:
        pass

    def warmup(self, ctx: NodeContext) -> None:
        # keep episodes across cycles by default; no clear unless requested
        pass

    def process(self, ctx: NodeContext, **inputs: Any) -> Dict[str, Any]:
        if inputs.get("append"):
            episode = {
                "time": inputs.get("time"),
                "context": inputs.get("context", {}),
                "affect": inputs.get("affect", {}),
                "payload": inputs.get("payload", {}),
                "cycle_idx": ctx.cycle_idx,
            }
            self._episodes.append(episode)
            emit_event(NodeEvent(node=self.name, run_id=ctx.run_id, cycle_idx=ctx.cycle_idx,
                                 payload={"op": "append"}))
            return {"count": len(self._episodes)}
        qn: Optional[int] = inputs.get("query_last")
        if qn is not None:
            result = self._episodes[-qn:] if qn > 0 else []
            return {"episodes": list(result)}
        return {"count": len(self._episodes)}

    def metrics(self) -> NodeMetrics:
        return self._m
```

---

## 4) Compose stub + integration smoke test

> Paths:
> `lukhas/orchestrator/matriz_phase1.py` • `tests/integration/test_matriz_phase1_compose.py` • `config/matriz/phase1.yml` (optional)

**lukhas/orchestrator/matriz_phase1.py**

```python
from __future__ import annotations
from typing import Dict, Any, Optional
import os, json

from MATRIZ.nodes.phase1 import (
    NodeRegistry, NodeContext,
    WorkingMemory, AttentionController, EpisodicMemory
)
from MATRIZ.nodes.phase1.events import wavec_checkpoint

DEFAULT_CONFIG = {
    "working_memory": {"capacity": 7},
    "attention_controller": {"top_k": 3, "temperature": 1.0},
    "episodic_memory": {},
    "wavec_every_n": 10,
}

def _load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    # Accept YAML or JSON; for now parse JSON if .json else fallback to defaults
    try:
        if path.endswith(".json"):
            with open(path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)

def compose_phase1(config_path: Optional[str] = None) -> NodeRegistry:
    cfg = _load_config(config_path)
    reg = NodeRegistry()
    # Register nodes (in dependency‑light order)
    wm = WorkingMemory(**cfg.get("working_memory", {}))
    attn = AttentionController(**cfg.get("attention_controller", {}))
    epi = EpisodicMemory(**cfg.get("episodic_memory", {}))
    reg.register(wm)
    reg.register(attn)
    reg.register(epi)
    return reg

def run_phase1_cycle(registry: NodeRegistry, run_id: str, cycle_idx: int, seed: int) -> Dict[str, Any]:
    ctx = NodeContext(run_id=run_id, cycle_idx=cycle_idx, seed=seed)
    wm = registry.get("working_memory")
    attn = registry.get("attention_controller")
    epi = registry.get("episodic_memory")

    # Warmup (idempotent)
    wm.warmup(ctx); attn.warmup(ctx); epi.warmup(ctx)

    # Minimal dataflow:
    wm_out = wm.process(ctx, item={"cycle": cycle_idx, "goal": "phase1-demo"})
    attn_out = attn.process(ctx, scores=[0.1, 0.7, 0.2, 0.3])
    epi.process(ctx, append=True, time=f"t{cycle_idx}", context={"demo": True},
                affect={"valence": 0.1}, payload={"wm_size": len(wm_out["wm_items"])})

    # WaveC checkpoint cadence
    every_n = 10
    if cycle_idx % every_n == 0:
        snapshot = {"wm_len": len(wm_out["wm_items"]), "attn": attn_out.get("attn", [])}
        wavec_checkpoint(run_id, cycle_idx, snapshot)

    return {"wm": wm_out, "attn": attn_out, "epi_count": registry.get("episodic_memory").process(ctx)["count"]}
```

**tests/integration/test_matriz_phase1_compose.py**

```python
from __future__ import annotations
import types
from lukhas.orchestrator.matriz_phase1 import compose_phase1, run_phase1_cycle
from MATRIZ.nodes.phase1.events import wavec_checkpoint

def test_compose_and_run_smoke(monkeypatch):
    reg = compose_phase1()
    # Monkeypatch WaveC to observe checkpoint calls (no real I/O)
    calls = {}
    def _fake_wavec(run_id, cycle_idx, memory_state):
        calls["last"] = (run_id, cycle_idx, memory_state)
    monkeypatch.setattr("lukhas.orchestrator.matriz_phase1.wavec_checkpoint", _fake_wavec, raising=True)

    last = None
    for c in range(1, 12):  # ensure at least one checkpoint (every 10)
        out = run_phase1_cycle(reg, run_id="r1", cycle_idx=c, seed=42)
        last = out
    assert "wm" in last and "attn" in last
    assert isinstance(last["wm"]["wm_items"], list)
    assert "last" in calls and calls["last"][1] == 10  # checkpoint on cycle 10
```

**config/matriz/phase1.yml** *(optional; present as a placeholder so downstream code can migrate to YAML later)*

```yaml
# Phase‑1 node defaults (overridable)
working_memory:
  capacity: 7
attention_controller:
  top_k: 3
  temperature: 1.0
episodic_memory: {}
wavec_every_n: 10
```

---

## 5) Unit test skeletons (N01–N03)

> Paths:
> `tests/matriz/phase1/test_working_memory.py` • `tests/matriz/phase1/test_attention_controller.py` • `tests/matriz/phase1/test_episodic_memory.py`

**tests/matriz/phase1/test_working_memory.py**

```python
from __future__ import annotations
import time
from MATRIZ.nodes.phase1.working_memory import WorkingMemory
from MATRIZ.nodes.phase1.base import NodeContext

def test_wm_capacity_and_eviction():
    wm = WorkingMemory(capacity=3)
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=123)
    wm.warmup(ctx)
    for i in range(5):
        wm.process(ctx, item={"i": i})
    out = wm.process(ctx)  # no-op call to read state
    assert len(out["wm_items"]) == 3
    # Oldest entries should have been evicted
    assert out["wm_items"][0]["i"] == 2
    assert out["wm_items"][-1]["i"] == 4

def test_wm_latency_budget_sanity():
    wm = WorkingMemory(capacity=64)
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=999, latency_budget_ms=5)
    wm.warmup(ctx)
    start = time.perf_counter()
    for i in range(100):
        wm.process(ctx, item={"i": i})
    ms = (time.perf_counter() - start) * 1000
    assert ms < 100.0  # loose bound; tune later with microbench
```

**tests/matriz/phase1/test_attention_controller.py**

```python
from __future__ import annotations
from MATRIZ.nodes.phase1.attention_controller import AttentionController
from MATRIZ.nodes.phase1.base import NodeContext

def test_attn_topk_deterministic():
    attn = AttentionController(top_k=2, temperature=1.0)
    ctx = NodeContext(run_id="r", cycle_idx=1, seed=0)
    attn.warmup(ctx)
    out = attn.process(ctx, scores=[0.1, 0.7, 0.2, 0.6])
    assert out["attn"] == [1, 3]
    assert out["entropy"] >= 0.0

def test_attn_empty_scores():
    attn = AttentionController(top_k=2)
    ctx = NodeContext(run_id="r", cycle_idx=2, seed=0)
    out = attn.process(ctx, scores=[])
    assert out["attn"] == []
    assert out["entropy"] == 0.0
```

**tests/matriz/phase1/test_episodic_memory.py**

```python
from __future__ import annotations
from MATRIZ.nodes.phase1.episodic_memory import EpisodicMemory
from MATRIZ.nodes.phase1.base import NodeContext
from MATRIZ.nodes.phase1 import events as events_mod

def test_epi_append_and_query(monkeypatch):
    epi = EpisodicMemory()
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=42)
    # Intercept event emission for safety “smell test”
    emissions = {}
    def fake_emit(evt):
        emissions["last"] = evt
    monkeypatch.setattr(events_mod, "emit_event", fake_emit, raising=True)

    for i in range(5):
        ctx2 = NodeContext(run_id="r", cycle_idx=i, seed=42)
        epi.process(ctx2, append=True, time=f"t{i}", context={"i": i}, affect={"valence": 0.0}, payload={"x": i})

    out = epi.process(ctx, query_last=2)
    eps = out["episodes"]
    assert len(eps) == 2 and eps[-1]["time"] == "t4"
    assert "last" in emissions and emissions["last"].payload["op"] == "append"
```

---

## 6) How these pieces fit (wiring guidance)

* **Orchestrator** calls `compose_phase1()` once at startup to build a `NodeRegistry`.
* Each cycle, it creates a **NodeContext** and calls `warmup()` (idempotent) then `process()` on a minimal dataflow path.
* **WaveC**: the compose stub triggers `wavec_checkpoint` every `N` cycles; tests monkeypatch the hook to avoid I/O.
* **Dream‑gate**: once nodes emit events, your dream pipeline can ingest `NodeEvent`s (scope for a follow‑up PR).
* **Guardian**: add a negative test per node in subsequent PRs where applicable (e.g., unsafe affect → veto).
* **Migrations**: the rest of Phase‑1 nodes (Semantic, Procedural, Fusion, Categorization, Grounding, RL, Meta‑Learning, ToM, Emotional) should follow the same contract and test shape. The compose stub can incrementally register them.

---

## 7) PR acceptance checklist (paste into PR body)

* [ ] Code conforms to `MATRIZ.nodes.phase1.Node` protocol; typed.
* [ ] Unit tests for the node pass locally (`pytest -q tests/matriz/phase1 -k <node>`).
* [ ] Integration smoke test passes (`pytest -q tests/integration -k phase1_compose`).
* [ ] Lane‑guard clean; no production→labs imports.
* [ ] WaveC hook exercised (monkeypatched in tests).
* [ ] p95 latency assertions present (loose for now; to be tightened with benchmarks).
* [ ] Docs stub added (API/metrics/rollback template to be expanded in subsequent PR).

---

### Optional: lightweight CI matrix (kept cheap)

If you want to run just these tests in PR CI, add (or update) a small job in your “Tier‑1” workflow to execute:

```yaml
- name: Phase-1 fast tests
  run: |
    python -m pytest -q tests/matriz/phase1 tests/integration/test_matriz_phase1_compose.py
```

This keeps PR minutes low while preserving a high-signal gate.

---

## 8) What to do next (fast path)

1. **Create the branch** and **paste these files** exactly as shown.
2. Run: `pytest -q tests/matriz/phase1 tests/integration/test_matriz_phase1_compose.py` (local)
3. Open the PR as **draft** and let CI run the fast tier.
4. In follow‑ups, replicate this pattern for N04–N12 (Semantic, Procedural, Fusion, Categorization, Grounding, RL, Meta‑Learning, ToM, Emotional). I can generate the next batch of stubs/tests on request.

If you want me to expand this to include **Semantic Memory** + **Symbol Grounding** next (N04 + N08), I’ll deliver two more node skeletons + unit tests plus the compose update in one more branch so you can parallelize reviews.
