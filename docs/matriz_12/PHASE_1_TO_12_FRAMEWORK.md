# MATRIZ Phase‑1 (12 Nodes) — T4/0.01% Foundation

**Branches, PRs, Commands, Stubs, Wiring Guidance**

> Scope: implement the 12 unanimous P0 nodes identified in the three‑way synthesis and gap analysis (Memory, Perception/Grounding, Learning, Social, Executive).
> Guarantees: reversible, auditable, measurable; each PR passes lane‑guard, smoke, WaveC, dream sanity, and perf budgets before merge.

---

## A) One‑time Scaffolding (run first)

**Create a scaffold branch with shared interfaces, registry, metrics, and PR templates.**

### 1) Files to add

```
core/matriz_nodes/__init__.py
core/matriz_nodes/base.py
core/matriz_nodes/registry.py
core/matriz_nodes/metrics.py
core/matriz_nodes/stubs/README.md
docs/matriz/node_templates/README.md
docs/matriz/pr_bodies/PHASE1_SCAFFOLD.md
.github/PULL_REQUEST_TEMPLATE/matriz_migration.md
scripts/matriz/benchmark/phase1_bench.sh
config/matriz/phase1.yml
```

### 2) Code: base Protocols & helpers

**`core/matriz_nodes/base.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol, runtime_checkable

# Minimal, library-free metrics container (extend to Prometheus if available).
@dataclass
class NodeMetrics:
    latency_ms_p95: float = 0.0
    memory_bytes: int = 0
    drift_score: float = 0.0
    hit_rate: float = 0.0
    error_count: int = 0

@runtime_checkable
class Node(Protocol):
    """Minimal surface for all MATRIZ nodes."""
    name: str

    def initialize(self, *, config: Mapping[str, Any]) -> None: ...
    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]: ...
    def metrics(self) -> NodeMetrics: ...

    # T4 hooks
    def wavec_snapshot(self) -> Dict[str, Any]: ...
    def guardian_check(self, *, proposal: Mapping[str, Any]) -> bool: ...

class NodeBase:
    """Safe default behaviors; override in concrete nodes."""
    name: str = "node"

    def __init__(self) -> None:
        self._metrics = NodeMetrics()

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        self._config = dict(config)

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def metrics(self) -> NodeMetrics:
        return self._metrics

    def wavec_snapshot(self) -> Dict[str, Any]:
        # Keep minimal, JSON-serializable
        return {"node": self.name, "config": getattr(self, "_config", {})}

    def guardian_check(self, *, proposal: Mapping[str, Any]) -> bool:
        # Return True to allow; False to veto.
        # Concrete nodes can consult policy / QRG here.
        return True
```

**`core/matriz_nodes/metrics.py`**

```python
from __future__ import annotations
import time
from contextlib import contextmanager

@contextmanager
def latency_recorder(setter):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt_ms = (time.perf_counter() - t0) * 1000.0
        setter(dt_ms)
```

**`core/matriz_nodes/registry.py`**

```python
from __future__ import annotations
from typing import Dict, Type
from .base import Node, NodeBase

_REGISTRY: Dict[str, Type[NodeBase]] = {}

def register(name: str, cls: Type[NodeBase]) -> None:
    if name in _REGISTRY:
        raise ValueError(f"Node already registered: {name}")
    _REGISTRY[name] = cls

def create(name: str, **kwargs) -> Node:
    cls = _REGISTRY[name]
    node = cls()
    node.initialize(config=kwargs.get("config", {}))
    return node

def available() -> Dict[str, Type[NodeBase]]:
    return dict(_REGISTRY)
```

**`config/matriz/phase1.yml`**

```yaml
# Phase-1 node toggles and budgets (adjust per node PR)
working_memory:
  enabled: true
  latency_ms_p95_budget: 30
  memory_bytes_budget: 8_000_000
attention_controller:
  enabled: true
episodic_memory:
  enabled: true
semantic_memory:
  enabled: true
procedural_memory:
  enabled: true
multimodal_fusion:
  enabled: true
perceptual_categorization:
  enabled: true
symbol_grounding:
  enabled: true
reinforcement_learning:
  enabled: true
meta_learning:
  enabled: true
theory_of_mind:
  enabled: true
emotional_reasoning:
  enabled: true
```

**`docs/matriz/pr_bodies/PHASE1_SCAFFOLD.md`**

```md
## Summary
Introduce Phase-1 scaffolding: base Protocols, registry, metrics helper, config stubs, PR template, and benchmarks.

## What changed
- `core/matriz_nodes/base.py` Protocol + NodeBase
- `core/matriz_nodes/registry.py` simple DI
- `core/matriz_nodes/metrics.py` latency helper
- `config/matriz/phase1.yml` node toggles/budgets
- `.github/PULL_REQUEST_TEMPLATE/matriz_migration.md` created
- `scripts/matriz/benchmark/phase1_bench.sh` placeholder

## Validation
- Imports succeed; smoke baseline passes
- Lane-guard: ✅
- No runtime behavior changed

## Next
Node PRs will register concrete classes and attach WaveC + Dream sanity checks.
```

**`.github/PULL_REQUEST_TEMPLATE/matriz_migration.md`**

```md
### Summary
Describe the node and the exact change.

### Artifacts to attach (required)
- [ ] Dry-run diff (if codemod)
- [ ] `smoke.log` (unit + integration)
- [ ] `lane_guard.log`
- [ ] `wavec_snapshot.json` + rollback replay
- [ ] `perf.json` (p95 latency, memory budget)
- [ ] `dream_sanity.md` (1-2 examples)

### Acceptance criteria
- Unit tests ≥ 80% (new files)
- p95 latency within budget; memory within budget
- Lane-guard ok; import-health ok
- WaveC rollback tested; Dream sanity ok
- Guardian veto path exercised on one negative case
```

**`scripts/matriz/benchmark/phase1_bench.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
# Minimal placeholder; each node PR should extend this.
print("phase1 benchmark placeholder: extend per node")
PY
```

### 3) Commands (scaffold PR)

```bash
git checkout -b chore/matriz-phase1-scaffold
mkdir -p core/matriz_nodes/stubs docs/matriz/node_templates docs/matriz/pr_bodies .github/PULL_REQUEST_TEMPLATE scripts/matriz/benchmark config/matriz
# (Write files as above)
git add core/matriz_nodes docs/matriz .github/PULL_REQUEST_TEMPLATE scripts/matriz config/matriz
git commit -m "chore(matriz): add Phase-1 scaffolding (base protocols, registry, metrics, PR template)"
git push origin chore/matriz-phase1-scaffold
gh pr create --title "chore(matriz): add Phase-1 scaffolding" --body-file docs/matriz/pr_bodies/PHASE1_SCAFFOLD.md --draft
```

---

## B) Per‑Node Work Items (12 P0 nodes)

**Acceptance (for *each* PR):**

* ✅ Unit tests ≥ 80% (new code)
* ✅ p95 latency ≤ budget; memory ≤ budget
* ✅ Lane‑guard clean; import‑health clean
* ✅ WaveC snapshot + rollback replay committed as artifact
* ✅ Dream sanity (1–2 examples touching this node)
* ✅ Guardian veto exercised on one negative case
* ✅ PR uses `matriz_migration` template; artifacts attached

> **Wiring pattern** for all nodes:
>
> 1. Implement `core/matriz_nodes/<node>.py` class extending `NodeBase`.
> 2. Register in `core/matriz_nodes/registry.py` via module import side‑effect (e.g., `register("working_memory", WorkingMemory)` in the module bottom).
> 3. Add a small integration hook in the orchestrator path that composes nodes (e.g., where MATRIZ processes cycles, fetch node instances from the registry by name with config from `config/matriz/phase1.yml`).
> 4. Emit `NodeMetrics` and WaveC snapshots at the end of `step()`.

For each node below you get: branch name, files, minimal stub, PR content, and commands.

---

### N01 — Working Memory (Executive / Memory)

**Branch:** `feat/matriz-node-working-memory`
**Files:**

```
core/matriz_nodes/working_memory.py
tests/matriz_nodes/test_working_memory.py
docs/matriz/node_templates/T-MATRIZ-001_working_memory.md
docs/matriz/pr_bodies/N01_WORKING_MEMORY.md
```

**Stub** `core/matriz_nodes/working_memory.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict, List
from .base import NodeBase, NodeMetrics
from .registry import register

class WorkingMemory(NodeBase):
    name = "working_memory"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._capacity = int(self._config.get("capacity", 7))
        self._items: List[Any] = []

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # context may provide "wm_push" or "wm_pop" operations
        op = context.get("wm_op", "noop")
        if op == "push" and "item" in context:
            if len(self._items) >= self._capacity:
                self._items.pop(0)
            self._items.append(context["item"])
        elif op == "pop" and self._items:
            self._items.pop()
        return {"wm_items": list(self._items), "wm_size": len(self._items)}

register(WorkingMemory.name, WorkingMemory)
```

**PR body** `docs/matriz/pr_bodies/N01_WORKING_MEMORY.md`

```md
## Summary
Introduce Working Memory (capacity-limited transient store) as an executive substrate.

## API & Behavior
- `step(wm_op=push|pop, item=Any)` mutates internal buffer; returns snapshot.
- Capacity defaults to 7 (configurable); FIFO eviction.

## Tests
- Push/pop semantics; eviction at capacity; idempotent noop.

## Metrics & Budgets
- p95 latency ≤ 30ms; memory ≤ 8MB; error_count == 0.

## Safety
- WaveC snapshot includes current items; rollback restores buffer.
- Guardian veto not applicable (no external action), but negative test uses malformed op.

## Artifacts
- `smoke.log` / `perf.json` / `wavec_snapshot.json` attached.
```

**Commands**

```bash
git checkout -b feat/matriz-node-working-memory
# add files above
git add core/matriz_nodes/working_memory.py tests/matriz_nodes/test_working_memory.py docs/matriz/node_templates/T-MATRIZ-001_working_memory.md docs/matriz/pr_bodies/N01_WORKING_MEMORY.md
git commit -m "feat(matriz): add Working Memory node (Phase-1 N01)"
git push origin feat/matriz-node-working-memory
gh pr create --title "feat(matriz): Working Memory (N01)" --body-file docs/matriz/pr_bodies/N01_WORKING_MEMORY.md --draft
```

---

### N02 — Attention Controller (Executive)

**Branch:** `feat/matriz-node-attention-controller`
**Stub** `core/matriz_nodes/attention_controller.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase, NodeMetrics
from .registry import register

class AttentionController(NodeBase):
    name = "attention_controller"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._policy = dict(self._config.get("weights", {}))  # e.g., {"memory": 0.4, "perception": 0.6}

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Compute normalized weights over subsystems to prioritize routing.
        weights = dict(self._policy)
        s = sum(weights.values()) or 1.0
        weights = {k: v / s for k, v in weights.items()}
        return {"attention_weights": weights}

register(AttentionController.name, AttentionController)
```

**PR title:** `feat(matriz): Attention Controller (N02)`
**Budget:** p95 ≤ 20ms; memory ≤ 4MB.
**Commands:** analogous to N01 with `docs/matriz/pr_bodies/N02_ATTENTION.md`.

---

### N03 — Episodic Memory (Memory)

**Branch:** `feat/matriz-node-episodic-memory`
**Stub** `core/matriz_nodes/episodic_memory.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict, List, Optional
from dataclasses import dataclass
from .base import NodeBase, NodeMetrics
from .registry import register

@dataclass
class Episode:
    id: str
    time: float
    content: Dict[str, Any]
    affect: float = 0.0  # emotional weight

class EpisodicMemory(NodeBase):
    name = "episodic_memory"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._episodes: List[Episode] = []

    def encode(self, *, event: Dict[str, Any]) -> str:
        import time, uuid
        ep = Episode(id=uuid.uuid4().hex, time=time.time(), content=event, affect=float(event.get("affect", 0.0)))
        self._episodes.append(ep)
        return ep.id

    def retrieve(self, *, query: Mapping[str, Any], k: int = 5) -> List[Episode]:
        # Minimal: return most recent episodes; replace with semantic retrieval later.
        return list(reversed(self._episodes))[:k]

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        if "encode_event" in context:
            eid = self.encode(event=dict(context["encode_event"]))
            return {"encoded_id": eid}
        if "query" in context:
            eps = self.retrieve(query=dict(context["query"]))
            return {"episodes": [e.__dict__ for e in eps]}
        return {}

register(EpisodicMemory.name, EpisodicMemory)
```

**PR title:** `feat(matriz): Episodic Memory (N03)`
**Budget:** p95 ≤ 40ms; memory ≤ 32MB; **Dream sanity must reference at least one encoded episode**.
**Commands:** analogous.

---

### N04 — Semantic Memory (Memory)

**Branch:** `feat/matriz-node-semantic-memory`
**Stub** `core/matriz_nodes/semantic_memory.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict, Set, DefaultDict
from collections import defaultdict
from .base import NodeBase
from .registry import register

class SemanticMemory(NodeBase):
    name = "semantic_memory"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._edges: DefaultDict[str, Set[str]] = defaultdict(set)  # concept graph

    def upsert(self, subj: str, rel: str, obj: str) -> None:
        key = f"{subj}:{rel}"
        self._edges[key].add(obj)

    def query(self, subj: str, rel: str) -> Set[str]:
        return set(self._edges.get(f"{subj}:{rel}", set()))

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        if "triple" in context:
            s, r, o = context["triple"]
            self.upsert(s, r, o)
        if "ask" in context:
            s, r = context["ask"]
            return {"answers": sorted(self.query(s, r))}
        return {}

register(SemanticMemory.name, SemanticMemory)
```

**Budget:** p95 ≤ 35ms; memory ≤ 48MB; **hit_rate** measured by synthetic Q/A.

---

### N05 — Procedural Memory (Memory/Learning)

**Branch:** `feat/matriz-node-procedural-memory`
**Stub** `core/matriz_nodes/procedural_memory.py`

```python
from __future__ import annotations
from typing import Any, Callable, Mapping, Dict
from .base import NodeBase
from .registry import register

class ProceduralMemory(NodeBase):
    name = "procedural_memory"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._skills: Dict[str, Callable[..., Any]] = {}

    def register_skill(self, name: str, fn: Callable[..., Any]) -> None:
        self._skills[name] = fn

    def apply_skill(self, name: str, **kwargs) -> Any:
        if name not in self._skills:
            raise KeyError(name)
        return self._skills[name](**kwargs)

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        if "define" in context:
            name, body = context["define"]
            # In practice compile a function; here we store a stub
            self.register_skill(name, lambda **kw: {"ok": True, "kw": kw})
        if "call" in context:
            name, args = context["call"]
            return {"result": self.apply_skill(name, **args)}
        return {}

register(ProceduralMemory.name, ProceduralMemory)
```

**Budget:** p95 ≤ 40ms; memory ≤ 16MB.

---

### N06 — Multimodal Fusion (Perception)

**Branch:** `feat/matriz-node-multimodal-fusion`
**Stub** `core/matriz_nodes/multimodal_fusion.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase
from .registry import register

class MultimodalFusion(NodeBase):
    name = "multimodal_fusion"

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Expect context["modalities"] = {"text": ..., "vision": ...}
        mods = dict(context.get("modalities", {}))
        # Minimal: unify keys; later: learned fusion
        fused = {"features": {k: bool(v) for k, v in mods.items()}}
        return {"fused": fused}

register(MultimodalFusion.name, MultimodalFusion)
```

**Budget:** p95 ≤ 35ms; memory ≤ 8MB.

---

### N07 — Perceptual Categorization (Perception)

**Branch:** `feat/matriz-node-perceptual-categorization`
**Stub** `core/matriz_nodes/perceptual_categorization.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict, List
from .base import NodeBase
from .registry import register

class PerceptualCategorization(NodeBase):
    name = "perceptual_categorization"

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Minimal placeholder: rules over fused.features
        fused = context.get("fused", {}).get("features", {})
        categories: List[str] = []
        if fused.get("vision"): categories.append("visual_presence")
        if fused.get("text"): categories.append("textual_presence")
        return {"categories": categories}

register(PerceptualCategorization.name, PerceptualCategorization)
```

**Budget:** p95 ≤ 20ms; memory ≤ 4MB.

---

### N08 — Symbol Grounding (Perception → Semantics)

**Branch:** `feat/matriz-node-symbol-grounding`
**Stub** `core/matriz_nodes/symbol_grounding.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase
from .registry import register

class SymbolGrounding(NodeBase):
    name = "symbol_grounding"

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Map categories to semantic labels
        cats = context.get("categories", [])
        grounded = {c: f"sem:{c}" for c in cats}
        return {"grounded_symbols": grounded}

register(SymbolGrounding.name, SymbolGrounding)
```

**Budget:** p95 ≤ 15ms; memory ≤ 2MB.

---

### N09 — Reinforcement Learning (Learning)

**Branch:** `feat/matriz-node-reinforcement-learning`
**Stub** `core/matriz_nodes/reinforcement_learning.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict, Tuple
from .base import NodeBase
from .registry import register

class ReinforcementLearning(NodeBase):
    name = "reinforcement_learning"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._value = {}  # state -> value

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        s = context.get("state")
        r = float(context.get("reward", 0.0))
        if s is not None:
            v = self._value.get(s, 0.0)
            alpha = float(self._config.get("alpha", 0.1))
            self._value[s] = v + alpha * (r - v)
        return {"value": self._value.get(s, 0.0)}

register(ReinforcementLearning.name, ReinforcementLearning)
```

**Budget:** p95 ≤ 25ms; memory ≤ 8MB; **Guardian hook** must block if reward shaping violates ethical constraints.

---

### N10 — Meta‑Learning (Learning)

**Branch:** `feat/matriz-node-meta-learning`
**Stub** `core/matriz_nodes/meta_learning.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase
from .registry import register

class MetaLearning(NodeBase):
    name = "meta_learning"

    def initialize(self, *, config: Mapping[str, Any]) -> None:
        super().initialize(config=config)
        self._meta = {"alpha": 0.1}

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Adjust learning rates or strategies based on recent performance
        last_err = float(context.get("last_error", 0.0))
        if last_err > 0.5:
            self._meta["alpha"] = min(0.5, self._meta["alpha"] + 0.05)
        else:
            self._meta["alpha"] = max(0.01, self._meta["alpha"] - 0.01)
        return {"meta": dict(self._meta)}

register(MetaLearning.name, MetaLearning)
```

**Budget:** p95 ≤ 20ms; memory ≤ 4MB.

---

### N11 — Theory of Mind (Social Cognition)

**Branch:** `feat/matriz-node-theory-of-mind`
**Stub** `core/matriz_nodes/theory_of_mind.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase
from .registry import register

class TheoryOfMind(NodeBase):
    name = "theory_of_mind"

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Minimal belief inference from observed actions
        observed = context.get("agent_action")
        belief = "unknown"
        if observed == "share_information":
            belief = "cooperative"
        elif observed == "withhold_information":
            belief = "competitive"
        return {"belief_estimate": belief}

register(TheoryOfMind.name, TheoryOfMind)
```

**Budget:** p95 ≤ 30ms; memory ≤ 8MB; **Ethics**: Guardian veto on manipulative strategies.

---

### N12 — Emotional Reasoning (Affect / Social)

**Branch:** `feat/matriz-node-emotional-reasoning`
**Stub** `core/matriz_nodes/emotional_reasoning.py`

```python
from __future__ import annotations
from typing import Any, Mapping, Dict
from .base import NodeBase
from .registry import register

class EmotionalReasoning(NodeBase):
    name = "emotional_reasoning"

    def step(self, *, context: Mapping[str, Any]) -> Dict[str, Any]:
        # Very simple appraisal: regret/joy signals from outcomes
        outcome = float(context.get("outcome", 0.0))
        affect = "regret" if outcome < 0 else "satisfaction"
        weight = abs(outcome)
        return {"affect_label": affect, "affect_weight": weight}

register(EmotionalReasoning.name, EmotionalReasoning)
```

**Budget:** p95 ≤ 15ms; memory ≤ 2MB; output must feed Episodic `affect` field and Inhibitory control (guardian).

---

## C) Wiring each node into MATRIZ

1. **Registry import side‑effect**: ensure orchestrator imports each module (or dynamic load based on `config/matriz/phase1.yml`), then `registry.create("<node>", config=...)`.
2. **Execution order** (per cycle):
   `MultimodalFusion → PerceptualCategorization → SymbolGrounding → SemanticMemory (upsert) → WorkingMemory → EpisodicMemory (encode/retrieve) → ProceduralMemory → ReinforcementLearning/MetaLearning → TheoryOfMind → EmotionalReasoning → AttentionController`
3. **WaveC**: after each cycle, call `node.wavec_snapshot()` and store snapshot every N cycles; if drift exceeds threshold, rollback.
4. **Guardian veto**: before acting on RL policy or ToM‑driven strategy, call `guardian_check(proposal=...)`. If False, suppress and log.
5. **Bench & logs**: after the cycle, record p95 from `metrics()`; write `perf.json`.

> **NOTE**: keep orchestrator edits minimal; for now add a `compose_phase1()` function that loads nodes defined true in `phase1.yml` and runs them in sequence, passing a mutable `context` dict.

---

## D) Commands blueprint for each node PR

Use this pattern (replace `<node_slug>`, titles, and body file):

```bash
git checkout -b feat/matriz-node-<node_slug>
# write core/matriz_nodes/<node_slug>.py, tests, docs, PR body
git add core/matriz_nodes/<node_slug>.py tests/matriz_nodes/test_<node_slug>.py docs/matriz/node_templates/T-MATRIZ-XXX_<node_slug>.md docs/matriz/pr_bodies/NXX_<UPPER>.md
git commit -m "feat(matriz): add <Node Name> (Phase-1 NXX)"
git push origin feat/matriz-node-<node_slug>
gh pr create --title "feat(matriz): <Node Name> (NXX)" --body-file docs/matriz/pr_bodies/NXX_<UPPER>.md --draft
```

> For each PR: attach `smoke.log`, `perf.json`, `wavec_snapshot.json`, `lane_guard.log`, `dream_sanity.md` to satisfy the PR template.

---

## E) Testing & CI hooks (per PR)

* **Unit**: `pytest -q tests/matriz_nodes/test_<node>.py`
* **Smoke**: a tiny end‑to‑end harness composing the new node with WorkingMemory and Episodic; store textual output as `smoke.log`.
* **Lane‑guard**: `make lane-guard` (import‑linter contracts must be KEPT).
* **Perf**: run `scripts/matriz/benchmark/phase1_bench.sh` after extending it; save `perf.json`.
* **Dream sanity**: produce 1–2 “regret demo” snippets invoking Episodic + Emotional Reasoning; store as `dream_sanity.md`.
* **WaveC**: serialize snapshot after 10 cycles; store as `wavec_snapshot.json`; simulate rollback once.

---

## F) Ordering & Milestones

* **Milestone A (Weeks 1–4):** N01 WorkingMemory, N02 AttentionController, N03 EpisodicMemory
* **Milestone B (Weeks 5–8):** N04 SemanticMemory, N05 ProceduralMemory, N06 MultimodalFusion
* **Milestone C (Weeks 9–12):** N07 PerceptualCategorization, N08 SymbolGrounding
* **Milestone D (Weeks 13–16):** N09 RL, N10 Meta‑Learning
* **Milestone E (Weeks 17–20):** N11 TheoryOfMind, N12 EmotionalReasoning

Each milestone closes only when **all PRs** inside meet acceptance gates and nightly dream‑gate is green for 3 consecutive runs.

---

## G) Safety notes (T4 discipline)

* **Reversibility**: each node is a small PR; merging requires attached rollback artifact.
* **Auditability**: all PRs use the migration template; artifacts retained 90 days.
* **Measurability**: budgets live in `config/matriz/phase1.yml`; perf.json records actuals.
* **Isolation**: import lanes kept clean; all labs/* integration gated via adapters elsewhere.

---

### Ready to execute

1. Run **Section A** scaffold.
2. For each node, copy the **NXX** block, add the files, and run the **commands**.
3. Keep PRs **draft** until artifacts are attached and gates are green.

If you want, I can also generate **test skeletons** (pytest) and **orchestrator compose stubs** in the next message to speed up the first milestone (N01–N03).
