Below is a **copy‑pasteable, T4/0.01%‑grade TODO** for Claude Code / Copilot / Codex to implement—**tests‑first, fail‑closed, feature‑flagged, telemetry‑rich**. I grouped items by domain; each has: **Goal → Files → Flag(s) → Steps → Snippets → Tests → Observability → Acceptance / Rollback**. Keep PRs small: **1 feature = 1 PR**.

---

## 0) Global guardrails (apply to all PRs)

**Goal:** Keep every change safe, measurable, and reversible.

* **Flags:** keep new paths dark by default
  `LUKHAS_EXPERIMENTAL=1`, `LUKHAS_LANE=candidate`, `ENABLE_LLM_GUARDRAIL=1`
* **DoD:** unit+integration tests green; CI guard scripts green; add docstrings+usage; no ABI break without notes; metrics emitted; p95 budgets respected.

---

## A) Lane Isolation → Registry/Plugin completion

### A1. Finish cross‑lane decoupling via registry (no importlib shims)

**Files**

* `lukhas/core/registry.py` (new)
* `lukhas/core/interfaces.py` (new – Protocols/ABCs)
* Replace any `importlib.import_module("candidate.*")` calls across `lukhas/*` façades.

**Flags**

* `LUKHAS_PLUGIN_DISCOVERY=("auto"|"off")`, default `off` in prod.

**Steps**

1. Define minimal **Protocol**s for pluggable subsystems in `interfaces.py` (Memory, Identity, Guardian, Orchestrator Node).
2. Implement a **Registry** with explicit register/resolve + optional auto‑discovery of `candidate.*` plugins.
3. Replace remaining dynamic imports with `registry.resolve("memory")`, etc.
4. Gate auto‑discovery behind flag; default to explicit registration in tests.

**Snippet – interfaces & registry**

```python
# lukhas/core/interfaces.py
from typing import Protocol, runtime_checkable, Any, Mapping

@runtime_checkable
class Memory(Protocol):
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...

@runtime_checkable
class CognitiveNode(Protocol):
    name: str
    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]: ...

# lukhas/core/registry.py
import os, importlib, pkgutil
from typing import Dict, Any, TypeVar

T = TypeVar("T")
_REG: Dict[str, Any] = {}

def register(kind: str, impl: Any) -> None:
    _REG[kind] = impl

def resolve(kind: str) -> Any:
    if kind not in _REG:
        raise LookupError(f"no implementation registered for {kind}")
    return _REG[kind]

def autoload(prefix="candidate", module_suffix="plugins"):
    if os.getenv("LUKHAS_PLUGIN_DISCOVERY") != "auto": return
    for mod in pkgutil.walk_packages():
        if not mod.name.startswith(f"{prefix}."): continue
        if not mod.name.endswith(f".{module_suffix}"): continue
        importlib.import_module(mod.name)
```

**Snippet – plugin registration from candidate**

```python
# candidate/memory/plugins.py
from lukhas.core.registry import register
from .impl_redis import RedisMemory

register("memory", RedisMemory.from_env())
```

**Tests**

* `tests/registry/test_registry.py`: resolve returns same instance; missing kind raises; auto‑discovery registers plugins when flag on.
* `tests/lane/test_no_import_shims.py`: AST scan asserts no `importlib.import_module("candidate.")` outside `registry.autoload`.

**Observability**

* Counter: `registry_register_total{kind=...}`
* Gauge: `registry_kinds_loaded`
* Log: “registry.register(kind=..., impl=ClassName)”

**Acceptance**

* All shims removed; only `registry.resolve` in façades.
* **Rollback:** set `LUKHAS_PLUGIN_DISCOVERY=off` and re‑enable explicit register calls (kept in code behind flag).

---

## B) Orchestrator logic – sophistication & resilience

### B1. Async pipeline + per‑stage timeouts & backoff

**Files**

* `candidate/core/orchestration/orchestrator.py`
* `candidate/core/orchestration/config.yaml` (new)

**Flags**

* `MATRIZ_ASYNC=1` (default on in candidate lane)
* `MATRIZ_STAGE_TIMEOUT_MS=200`

**Steps**

1. Convert `process_query` to `async def`.
2. Wrap each node call with `asyncio.wait_for` using per‑stage timeout config.
3. Implement exponential backoff retry for transient node errors.

**Snippet – async with timeout/backoff**

```python
# orchestrator.py
import asyncio, math
from typing import Mapping, Any, Callable

async def _with_retry(fn: Callable[[], Any], attempts=2, base_ms=80):
    for i in range(attempts):
        try: return await fn()
        except Exception: 
            if i == attempts-1: raise
            await asyncio.sleep((2**i)*base_ms/1000)

async def _run_node(node, ctx, stage, timeout_ms):
    async def call(): return await node.process(ctx)
    return await asyncio.wait_for(_with_retry(call), timeout=timeout_ms/1000)

async def process_query(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    # ... build intent, select nodes ...
    out = {}
    for stage, node in pipeline:
        out = await _run_node(node, {**ctx, **out}, stage, timeout_ms=ctx["conf"].get(stage+"_timeout", 200))
    return out
```

**Tests**

* `tests/orchestration/test_async_timeouts.py`: slow dummy node triggers timeout; retry path counted; result fallback recorded.

**Observability**

* Histogram: `matriz_stage_latency_seconds{stage=...}`
* Counter: `matriz_stage_timeouts_total{stage=...}`
* Span per stage (see OBS section).

**Acceptance**

* p95 per stage < configured budgets; timeouts recorded; no deadlocks.

---

### B2. **Consensus Arbitration** for competing proposals (ethics+confidence+recency)

**Files**

* `candidate/core/orchestration/consensus_arbitrator.py` (new)
* Wire in `agent_orchestrator.py`

**Steps**

1. Score candidates by weighted sum with **Guardian ethics risk as hard gate**.
2. Break ties by ΛiD role weight and recency decay.
3. Return winner + rationale for logs.

**Snippet – arbitration**

```python
# consensus_arbitrator.py
from dataclasses import dataclass
import math, time

@dataclass
class Proposal:
    id: str
    confidence: float
    ts: float
    ethics_risk: float  # 0 allow ... 1 block
    role_weight: float  # ΛiD role importance
    rationale: str

def score(p: Proposal, now=None):
    now = now or time.time()
    if p.ethics_risk >= 0.8: return -math.inf
    recency = math.exp(-(now - p.ts)/30.0)
    return (0.6*p.confidence) + (0.3*recency) + (0.1*p.role_weight) - (0.5*p.ethics_risk)

def choose(proposals):
    ranked = sorted(proposals, key=score, reverse=True)
    winner = ranked[0] if ranked else None
    return winner, {"ranking":[(p.id, score(p)) for p in ranked]}
```

**Tests**

* `tests/orchestration/test_arbitration.py`: high ethics\_risk proposal excluded; tie broken by role\_weight & recency.

**Observability**

* Log: arbitration rationale (top‑k with scores).
* Counter: `consensus_chosen_total{node=...}`.

**Acceptance**

* Deterministic stable choice across replays; rationale attached to trace.

---

### B3. **Meta‑Reasoning Controller** (loop/oscillation detection)

**Files**

* `candidate/core/orchestration/meta_controller.py` (new)
* Hook in orchestrator loop

**Steps**

1. Track last N stages; if cycle detected (e.g., A→B→A), apply rule: **escalate to human** or **inject alternative node** once.
2. Persist decision in trace.

**Snippet**

```python
from collections import deque

class MetaController:
    def __init__(self, k=4): self.window = deque(maxlen=k)
    def step(self, stage_name: str):
        s = list(self.window) + [stage_name]
        self.window.append(stage_name)
        # Detect simple 2-cycle
        return len(s)>=4 and s[-4]==s[-2] and s[-3]==s[-1]

# in orchestrator, per stage:
if meta.step(stage.name):
    guardian.warn("oscillation_detected")
    return {"action":"escalate","reason":"oscillation"}
```

**Tests**

* `tests/orchestration/test_meta_loops.py`: synthetic oscillation triggers escalation once.

---

### B4. **Dynamic node auto‑registration** (discovery)

**Files**

* `candidate/core/orchestration/loader.py` (new)

**Steps**

1. Scan `candidate/**/nodes/*.py` for `CognitiveNode` subclasses; instantiate via `from_env()` if present.
2. Honor `NODES_DISABLED` env var allow‑list/deny‑list.

**Snippet**

```python
# loader.py
import importlib, pkgutil, os, inspect
from lukhas.core.interfaces import CognitiveNode
from lukhas.core.registry import register

def discover_nodes(pkg="candidate"):
    disabled = set(os.getenv("NODES_DISABLED","").split(","))
    for m in pkgutil.walk_packages():
        if not m.name.startswith(f"{pkg}."): continue
        if ".nodes." not in m.name: continue
        mod = importlib.import_module(m.name)
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, CognitiveNode) and getattr(cls, "AUTOINIT", False):
                if cls.name in disabled: continue
                register(f"node:{cls.name}", cls.from_env())
```

**Tests**

* `tests/orchestration/test_node_discovery.py`: dummy node with `AUTOINIT=True` is registered; disable works.

---

## C) Constellation × MATRIZ alignment & terminology

### C1. Unify terms (Trinity→Constellation), deprecate “AGI” in code

**Files**

* `scripts/lint/text_conventions.py` (new – simple content linter)
* `.pre-commit-config.yaml` add hook
* Update docstrings & comments selectively

**Steps**

1. Add linter that **fails** on “Trinity” / “AGI” in code except in docs/branding allow‑list.
2. Replace module docstrings with “Constellation (Identity, Memory, Vision, Guardian)”.

**Snippet – mini linter**

```python
# scripts/lint/text_conventions.py
import sys, re, pathlib
BAD = [(re.compile(r"\bTrinity\b"), "Use 'Constellation'"), (re.compile(r"\bAGI\b"), "Prefer 'AI'")]
ALLOW = ("docs/branding",)
fail = False
for p in map(pathlib.Path, sys.argv[1:]):
    if any(str(p).startswith(a) for a in ALLOW): continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    for rgx,msg in BAD:
        if rgx.search(text):
            print(f"{p}: {msg}"); fail=True
sys.exit(1 if fail else 0)
```

**Tests**

* `tests/lint/test_text_conventions.py`: synthetic file triggers linter.

**Acceptance**

* CI gate runs linter over changed files; violations = PR block.

---

### C2. Mapping document + runtime rationale tags

**Files**

* `docs/consciousness/CONSTELLATION_X_MATRIZ.md` (new)
* Add rationale tags in orchestrator outputs

**Steps**

1. Document mapping (Identity→Awareness, Memory→Memory/Attention, Vision→Thought/Perception, Guardian→Decision).
2. Attach `"constellation_star":"Guardian"` on Decision nodes, etc.

**Snippet – tag**

```python
# when building node result
result["_constellation"] = {"star":"Guardian","why":"ethics_validation"}
```

**Tests**

* `tests/orchestration/test_constellation_tags.py`: node outputs include correct star tag.

---

## D) Ethics, consent, safety integration points

### D1. Pre‑Action Plan Verifier gate

**Files**

* `core/symbolic/constraints/plan_verifier.py` (new)
* Wire in orchestrator before Action stage

**Steps**

1. Define `verify(plan)->(ok, violations[])` with simple constraints (no external POST if PII present; time/purpose policy).
2. Abort/require human when violations exist; log to Guardian ledger.

**Snippet**

```python
from typing import Mapping, List, Tuple
def verify(plan: Mapping) -> Tuple[bool, List[str]]:
    v=[]
    if plan.get("contains_pii") and plan.get("verb")=="POST" and "external" in plan.get("target",""):
        v.append("PII+external_POST")
    return (len(v)==0, v)
```

**Tests**

* `tests/constraints/test_plan_verifier.py`: sample plans pass/fail as expected.

---

### D2. Safety Tags consult before external call

**Files**

* `core/bridge/llm_guardrail.py` (already added)
* Hook: orchestrator Action node reads `safety_tags` and adjusts band/action.

**Steps**

1. If `high_risk_tag_combination` true, set action → `require_human`; attach rationale.
2. Emit metric for band.

**Snippet**

```python
if tags.high_risk_combo(ctx):
    return {"action":"require_human","reason":"PII+external"}
```

**Tests**

* `tests/ethics/test_action_guard.py`: PII+external Action returns require\_human, not execute.

---

## E) Observability – tracing & metrics

### E1. OpenTelemetry spans per MATRIZ stage

**Files**

* `candidate/core/orchestration/otel.py` (new helper)
* Instrument orchestrator

**Steps**

1. Create `span(stage_name)` context manager.
2. Wrap each stage execution; set attributes (star, node\_name, timeout\_ms, retries).

**Snippet**

```python
# otel.py
from contextlib import contextmanager
from opentelemetry import trace
tracer = trace.get_tracer("lukhas.matriz")

@contextmanager
def stage_span(name, **attrs):
    with tracer.start_as_current_span(f"matriz.{name}") as sp:
        for k,v in attrs.items(): sp.set_attribute(f"matriz.{k}", v)
        yield sp
```

**Usage**

```python
from .otel import stage_span
with stage_span(stage.name, node=node.name, timeout=timeout_ms):
    out = await _run_node(node, ctx, stage.name, timeout_ms)
```

**Tests**

* `tests/obs/test_spans_smoke.py`: run a query with in‑memory OTEL exporter; assert span names present.

---

### E2. Domain metrics (Prometheus)

**Files**

* `lukhas/metrics.py` (new – optional Prometheus client)
* Import and use in orchestrator & guardian

**Snippet**

```python
# metrics.py
import os
from prometheus_client import Counter, Histogram, start_http_server

ENABLED = os.getenv("ENABLE_PROM","0")=="1"
if ENABLED:
    start_http_server(int(os.getenv("PROM_PORT","9108")))

stage_latency = Histogram("matriz_stage_latency_seconds", "Latency per stage", ["stage"])
stage_timeout = Counter("matriz_stage_timeouts_total", "Timeouts per stage", ["stage"])
guardian_band = Counter("guardian_risk_band_total", "Risk band decisions", ["band"])
```

**Usage**

```python
from lukhas.metrics import stage_latency, stage_timeout
with stage_latency.labels(stage).time():
    try: ...
    except asyncio.TimeoutError:
        stage_timeout.labels(stage).inc()
        raise
```

**Tests**

* `tests/obs/test_metrics_smoke.py`: metrics endpoint exposes expected names when `ENABLE_PROM=1`.

---

## F) Testing – behavioral, property‑based, perf

### F1. MATRIZ behavioral E2E tests

**Files**

* `tests/matriz/test_behavioral_e2e.py`

**Cases**

* Q\&A path: Intent→Thought(facts)→Decision→Awareness; final answer contains fact; trace includes all stages.
* Vision hint path: “look at image” selects vision node; trace shows star=Vision.

**Snippet**

```python
def test_trace_contains_required_stages(client):
    r = client.post("/api/ask", json={"q":"What is 2+2?"})
    trace = r.json()["trace"]
    stages = [n["stage"] for n in trace]
    assert stages[:3] == ["INTENT","THOUGHT","DECISION"]
```

---

### F2. Property tests: memory cascade prevention

**Files**

* `tests/memory/test_cascade_property.py`

**Snippet (Hypothesis)**

```python
from hypothesis import given, strategies as st
@given(st.lists(st.tuples(st.text(min_size=1, max_size=10), st.integers()), min_size=1, max_size=50))
def test_no_cascade(seq):
    mem = MemoryUnderTest()
    for k,v in seq: mem.set(k,str(v))
    for k,_ in seq: _ = mem.get(k)
    assert mem.cascade_counter == 0
```

---

### F3. Perf budget microbenchmarks (env‑gated)

**Files**

* `tests/perf/test_matriz_perf.py`

**Snippet (pytest‑benchmark or timeit)**

```python
import os, time
import statistics as stats
def test_pipeline_p95_under_budget():
    if os.getenv("LUKHAS_PERF")!="1": return
    from candidate.core.orchestration import orchestrator
    lat=[]
    for _ in range(100):
        t0=time.perf_counter()
        _ = asyncio.run(orchestrator.process_query({"q":"short"}))
        lat.append(1000*(time.perf_counter()-t0))
    lat.sort()
    p95 = lat[int(0.95*len(lat))-1]
    assert p95 < 250.0
```

---

## G) Security & DevOps

### G1. Locked dependencies (pip‑tools)

**Files**

* `requirements.in` (curated)
* `requirements.txt` (generated, pinned)
* `Makefile` targets: `deps-compile`, `deps-sync`
* CI step to check drift

**Snippet – Makefile**

```make
deps-compile:
\tpip-compile --generate-hashes -o requirements.txt requirements.in
deps-sync:
\tpip-sync requirements.txt
```

**CI (step)**

```yaml
- name: Check deps drift
  run: |
    pip-compile --quiet -o /tmp/req.txt requirements.in
    diff -u requirements.txt /tmp/req.txt && echo "OK" || (echo "Drift"; exit 1)
```

---

### G2. Pre‑commit hooks

**Files**

* `.pre-commit-config.yaml` add: ruff, black, mypy, **text\_conventions**, secret scan

**Snippet**

```yaml
-   repo: local
    hooks:
    - id: text-conventions
      name: text conventions
      entry: python3 scripts/lint/text_conventions.py
      language: system
      files: \.(py|md|yaml)$
```

---

### G3. Harden Dockerfile (non‑root, slim)

**Files**

* `Dockerfile`

**Snippet**

```dockerfile
FROM python:3.11-slim
RUN adduser --disabled-password --gecos '' app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER app
ENV ENABLE_PROM=1 PROM_PORT=9108
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8080"]
```

---

## H) Docs & Context refresh (minimal, precise)

### H1. Mapping doc (Constellation × MATRIZ) + Runbook delta

**Files**

* `docs/consciousness/CONSTELLATION_X_MATRIZ.md` (new)
* `docs/runbooks/matriz_observability.md` (new – spans & metrics list)
* Update top‑level `claude.me` & `lukhas_context.md` with Schema v2.0.0 bullets (lane types, flags, budgets).

**Acceptance**

* Docs reference exact env flags, metric names, span names, file paths added above.

---

## I) Lane Readiness & Rollout

### I1. Lane waiver elimination & CI gate

**Files**

* `scripts/check_lane_violations.py` (new – forbids imports & importlib to candidate outside registry/loader)
* `.github/workflows/ci.yml` add step
* Remove `ops/lane_waivers.txt` or ensure empty

**Snippet – simple AST check**

```python
# detect importlib import_module("candidate.")
```

**Acceptance**

* CI fails if any violation appears outside allowed files list: `lukhas/core/registry.py`, `candidate/core/orchestration/loader.py`.

---

# PR sequencing (one per):

1. **A1 Registry completion** (+ tests, metrics)
2. **B1 Async+timeouts** (+ metrics)
3. **B2 Arbitration**
4. **B3 Meta‑reasoning controller**
5. **B4 Node discovery**
6. **D1 Plan verifier gate**
7. **E1 OTel spans**
8. **E2 Prom metrics**
9. **F1 Behavioral E2E**
10. **F2 Property memory**
11. **F3 Perf microbench**
12. **C1 Text conventions linter**
13. **C2 Constellation tags + doc**
14. **G1 Locked deps**
15. **G2 Pre‑commit**
16. **G3 Docker hardening**
17. **H1 Docs refresh**
18. **I1 Lane gate**

Each PR: update `CHANGELOG.md`, add **Makefile** targets where relevant (e.g., `make obs`, `make deps-compile`), and **dashboard panel** deltas for new metrics.

---

## Acceptance Gates (global)

* **Isolation:** 0 lane violations (static + AST checks); only registry/loader allowed to touch discovery.
* **Perf:** MATRIZ p95 ≤ **250 ms** (env‑gated perf test green).
* **Ethics:** Safety tags + plan verifier block PII+external POST; guardian bands metrics flowing.
* **Obs:** Spans present for all stages; metrics endpoint exposes `matriz_stage_latency_seconds`, `guardian_risk_band_total`.
* **Docs:** Mapping doc present; top‑level contexts updated to Schema v2.0.0.
* **Security:** requirements pinned; Docker non‑root; pre‑commit runs locally; CI drift check green.

---

## Rollback & Kill‑switches

* Set `MATRIZ_ASYNC=0` to revert to sync pipeline.
* Set `LUKHAS_PLUGIN_DISCOVERY=off` to disable auto discovery (explicit register path still present).
* Set `ENABLE_PROM=0` to disable metrics server quickly.
* Feature flags around each new gate default **off** in production lane until canary passes.

---

