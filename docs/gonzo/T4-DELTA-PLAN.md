


The T4 delta plan (critical path, not wish list)

Phase 0 — Trunk health & reality checks (2–3 days of focused work)
	•	Make tests collectible (0 collection errors).
	•	Add deterministic orchestration tick + observability skeleton (no features yet).
	•	Freeze a MATRIZ Node Contract v1 and a SymbolicMeshRouter in log‑only mode.

Phase 1 — Contracts, lanes, and safety (1 week)
	•	Enforce lane guards (experimental/candidate/prod) with a decorator + CI gates.
	•	Migrate the 11 MATRIZ adapters behind the Node Contract (thin wrappers).
	•	Wire EQNOX/GLYPH identities into message headers for auditability.

Phase 2 — Consciousness stream & drift (1 week)
	•	Implement the 33ms consciousness tick with ring buffers, decimation, and backpressure.
	•	Ship DriftScore v2 (windowed, per‑lane) and fold‑cascade guard on memory.

Phase 3 — Learning loop & observability (1 week)
	•	Stand up Experience Replay (event‑sourced), BreakthroughDetector (novelty×value), and explainability traces.
	•	Prometheus + OTEL exporters, red/green dashboards, and a capability regression suite.

Then scale. Not before.

⸻

HAND‑TO‑CLAUDE: Full implementation plan

Everything below is ready to paste into your coding agent(s). It includes contracts, code scaffolds, tests, metrics, CI, and prompts.

⸻

0) Repo audit & invariants

0.1 Script: test collection must be zero

# scripts/audit_tests.py
"""
Collect pytest tests and exit non-zero if any collection errors are found.
Usage:
  python scripts/audit_tests.py
  pytest --maxfail=1 --disable-warnings -q
"""
import subprocess, sys, re
out = subprocess.run(["pytest","--collect-only","-q"], capture_output=True, text=True)
err = out.stderr + out.stdout
m = re.search(r"collected (\d+) items.*?(\d+) errors", err.replace('\n',' ')) or re.search(r"(\d+) errors during collection", err)
if "errors during collection" in err or "ERROR" in err:
    print(err)
    sys.exit(1)
print("OK: no collection errors")

0.2 Invariant checks
	•	No network calls in tests without @pytest.mark.net.
	•	No writes outside /tmp or ./.test_artifacts.
	•	Stable seeds via PYTHONHASHSEED=0, random.seed(1337), torch.use_deterministic_algorithms(True) if applicable.

Makefile

test:
	pytest -q

audit:
	python scripts/audit_tests.py

ci: audit test


⸻

1) Core contracts

1.1 MATRIZ Node Contract v1 (typed, minimal)

# matriz/node_contract.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

@dataclass(frozen=True)
class GLYPH:
    id: UUID
    kind: str              # e.g., "intent", "memory", "attention"
    version: str           # semantic version of the glyph schema
    tags: Dict[str, Any]   # arbitrary symbolic tags, ethical flags, provenance

@dataclass(frozen=True)
class MatrizMessage:
    msg_id: UUID
    ts: datetime
    lane: str              # "experimental" | "candidate" | "prod"
    glyph: GLYPH
    payload: Dict[str, Any]
    topic: str             # e.g., "contradiction", "resource", "trend"

@dataclass
class MatrizResult:
    ok: bool
    reasons: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    trace: Dict[str, Any] = field(default_factory=dict)  # explainability crumbs

class MatrizNode:
    name: str = "abstract-node"
    version: str = "0.1.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        raise NotImplementedError("Implement in adapter")

1.2 SymbolicMeshRouter (log‑only first)

# matriz/router.py
import queue, threading, time
from typing import Callable, Dict
from .node_contract import MatrizMessage, MatrizResult, MatrizNode

class SymbolicMeshRouter:
    def __init__(self, log_fn: Callable[[str, dict], None]):
        self.nodes: Dict[str, MatrizNode] = {}
        self.q = queue.Queue(maxsize=8192)
        self.log = log_fn
        self.running = False

    def register(self, topic: str, node: MatrizNode):
        self.nodes[topic] = node
        self.log("router.register", {"topic": topic, "node": node.name})

    def publish(self, msg: MatrizMessage):
        # log-only mode: do not dispatch, just record
        self.log("router.publish", {"topic": msg.topic, "lane": msg.lane, "msg_id": str(msg.msg_id)})

    def start(self):
        self.running = True
        self.log("router.start", {})

Later, flip a DISPATCH_ENABLED feature flag to actually call node.handle(msg) per topic. Start in log‑only to observe traffic safely.

1.3 Lane guards (runtime + CI)

# core/lanes.py
import os
from functools import wraps

LANE = os.getenv("LUKHAS_LANE", "experimental")

def lane_guard(allowed=("experimental","candidate","prod")):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if LANE not in allowed:
                raise RuntimeError(f"Lane {LANE} not allowed for {fn.__name__}")
            return fn(*args, **kwargs)
        return wrapper
    return deco

Pytest marker ensures prod‑only tests can’t run accidentally:

# conftest.py
import pytest, os
def pytest_collection_modifyitems(items):
    lane = os.getenv("LUKHAS_LANE", "experimental")
    skip_prod = pytest.mark.skip(reason="not prod lane")
    for item in items:
        if "prod_only" in item.keywords and lane != "prod":
            item.add_marker(skip_prod)


⸻

2) EQNOX/GLYPH integration (auditability)

Message headers carry GLYPH IDs + provenance; enforce every node to copy trace crumbs.

# core/trace.py
from time import time
def mk_crumb(stage: str, data: dict):
    return {"t": time(), "stage": stage, **data}

Usage in adapters:

result.trace["node_enter"] = mk_crumb("enter", {"node": self.name})


⸻

3) Consciousness stream: deterministic tick + backpressure

3.1 Ticker

# core/clock.py
import time
from typing import Callable

class Ticker:
    def __init__(self, fps: int = 30):
        self.period = 1.0 / fps

    def run(self, step: Callable[[], None], run_for_seconds: int = 0):
        start = time.time()
        while True:
            t0 = time.time()
            step()
            elapsed = time.time() - t0
            sleep = max(0.0, self.period - elapsed)
            time.sleep(sleep)
            if run_for_seconds and time.time() - start >= run_for_seconds:
                break

3.2 Ring buffers + decimation

# core/ring.py
from collections import deque

class Ring:
    def __init__(self, capacity: int):
        self.q = deque(maxlen=capacity)
    def push(self, x): self.q.append(x)
    def pop_all(self): 
        out, self.q = list(self.q), deque(maxlen=self.q.maxlen)
        return out
    def __len__(self): return len(self.q)

Backpressure policy (pseudo):
	•	If producer backlog > k frames, drop oldest (decimate).
	•	Emit p95 processing time as metric; if p95 > budget, reduce FPS dynamically (e.g., 30→20).

⸻

4) DriftScore v2 & fold‑cascade guard

4.1 DriftScore v2 (windowed)

Working theory: drift is the distance between intention and realized action over a sliding window, stabilized by exponential smoothing.

# core/drift.py
import numpy as np
from dataclasses import dataclass

@dataclass
class DriftState:
    ema: float = 0.0
    alpha: float = 0.2

def cosine(a, b):
    na, nb = np.linalg.norm(a)+1e-9, np.linalg.norm(b)+1e-9
    return float(np.dot(a,b)/(na*nb))

def drift_score(intents: np.ndarray, actions: np.ndarray, state: DriftState):
    # 1 - cosine similarity => 0 good, 1 bad
    d = 1.0 - cosine(intents, actions)
    state.ema = state.alpha*d + (1-state.alpha)*state.ema
    return state.ema

Thresholding: start with warn@0.20, block@0.35 per lane; learn from data.

4.2 Memory fold cascade guard

Rule: a write to memory can fan out at most N linked folds per tick, and a circuit breaker trips if recursive folds exceed a moving window budget.

# memory/folds.py
class FoldGuard:
    def __init__(self, max_fanout=8, max_depth=4, window_budget=256):
        self.window = 0
        self.window_budget = window_budget
        self.max_fanout = max_fanout
        self.max_depth = max_depth

    def start_tick(self): self.window = 0

    def allow(self, fanout:int, depth:int):
        if fanout > self.max_fanout: return False
        if depth   > self.max_depth: return False
        if self.window + fanout > self.window_budget: return False
        self.window += fanout
        return True

Acceptance test:
	•	Simulate a recursion graph; assert no path writes more than budget; assert circuit breaker flips.

⸻

5) BreakthroughDetector (novelty × value)

Working theory: a “breakthrough” is a significant increase in novelty score (distance to recent embedding centroid) times value score (task reward or evaluator rating), detected via BOCPD or CUSUM on the product.

# core/breakthrough.py
import numpy as np

class BreakthroughDetector:
    def __init__(self, novelty_w=0.5, value_w=0.5, z=3.0):
        self.mu, self.sq, self.n = 0.0, 0.0, 0
        self.z = z
        self.w = (novelty_w, value_w)

    def step(self, novelty, value):
        score = self.w[0]*novelty + self.w[1]*value
        self.n += 1
        self.mu += (score - self.mu)/self.n
        self.sq += (score - self.mu)*(score - (self.mu - (score - self.mu)/self.n))
        std = (self.sq/(self.n-1))**0.5 if self.n>1 else 0.0
        is_break = (std>0) and (score > self.mu + self.z*std)
        return {"score": score, "mean": self.mu, "std": std, "breakthrough": is_break}

Metric not vanity: count breakthrough flags per 1k ticks with post‑hoc human validation, not “innovations/week”.

⸻

6) Autonomous Goal Manager (hierarchy + planner loop)

Spec: Goals are trees with constraints, scored by expected value under risk; planner produces plans → actions → evaluation → replay.

# agi/goals.py
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Goal:
    id: str
    description: str
    parent: str | None
    constraints: Dict[str, float] = field(default_factory=dict)
    priority: float = 1.0
    status: str = "pending"  # pending|active|done|blocked

@dataclass
class PlanStep:
    action: str
    args: Dict[str, str]
    expected_value: float
    risk: float

class GoalManager:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}

    def add_goal(self, g: Goal):
        self.goals[g.id] = g

    def plan(self, goal_id: str) -> List[PlanStep]:
        # Placeholder: plug in symbolic planner later
        return [PlanStep("query", {"topic": "subtask"}, 0.6, 0.2)]


⸻

7) Observability & explainability

Prometheus metrics names (flat, stable):
	•	lukhas_tick_duration_seconds{lane=…} (summary)
	•	lukhas_consciousness_frames_total{lane=…}
	•	lukhas_backlog_frames{lane=…}
	•	lukhas_drift_ema{lane=…}
	•	lukhas_memory_circuit_breaks_total
	•	lukhas_breakthrough_flags_total
	•	lukhas_router_publish_total{topic=…}

Explainability trace structure: every decision returns trace: {crumbs: […], inputs: …, outputs: …, constraints: …} persisted to the event store.

⸻

8) Event‑sourced memory & experience replay

Event schema:

# storage/events.py
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4, UUID
from typing import Dict

@dataclass(frozen=True)
class Event:
    id: UUID
    ts: datetime
    kind: str        # "intention","action","memory_write","reward"
    lane: str
    glyph_id: UUID
    payload: Dict

Replay:
	•	Query events by glyph_id and time.
	•	Build state by folding events; feed to learning modules; persist derived artifacts with versioned schema.

⸻

9) Safety interlocks (Guardian system)

Policy engine skeleton:

# safety/guardian.py
from typing import Dict

class Guardian:
    def __init__(self, policies: Dict[str, float]):
        self.policies = policies  # e.g., max_risk, drift_block
    def allow(self, step) -> bool:
        if step.get("risk",0) > self.policies.get("max_risk", 0.5): return False
        if step.get("drift",0) > self.policies.get("max_drift", 0.35): return False
        return True

Default to dry‑run in non‑prod lanes. Every external action must have preview → approve → execute; prod requires human approval for P0 actions.

⸻

10) Test taxonomy and examples

Markers:
	•	@pytest.mark.contract — node contract compliance
	•	@pytest.mark.router — publish/dispatch semantics
	•	@pytest.mark.clock — tick timing within budget
	•	@pytest.mark.safety — guardian policy enforcement
	•	@pytest.mark.e2e — end‑to‑end lane rehearsal (dry‑run)

Example tests

# tests/test_contracts.py
import pytest
from matriz.node_contract import MatrizNode, MatrizMessage, GLYPH, MatrizResult
from datetime import datetime
from uuid import uuid4

class Dummy(MatrizNode):
    name="dummy"; version="0.0.1"
    def handle(self, msg): 
        return MatrizResult(ok=True, payload={"echo": True}, trace={"handled_by": self.name})

def mk_msg():
    return MatrizMessage(
        msg_id=uuid4(), ts=datetime.utcnow(), lane="experimental",
        glyph=GLYPH(id=uuid4(), kind="intent", version="1.0.0", tags={"src": "test"}),
        payload={"x":1}, topic="contradiction"
    )

@pytest.mark.contract
def test_node_contract_handle():
    d = Dummy()
    res = d.handle(mk_msg())
    assert res.ok and res.payload["echo"]
    assert "handled_by" in res.trace

# tests/test_clock.py
import time
from core.clock import Ticker
def test_ticker_budget():
    ticks = 0
    def step():
        nonlocal ticks; ticks += 1; time.sleep(0.005)
    Ticker(fps=30).run(step, run_for_seconds=1)
    assert 20 <= ticks <= 35


⸻

11) CI gates

.github/workflows/ci.yml

name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -U pip
      - run: pip install -r requirements.txt
      - run: make audit
      - run: pytest -m "not prod_only" -q --maxfail=1

Lane enforcement in CI: require LUKHAS_LANE=candidate for merge to main; prod only on tagged releases.

Perf budgets (A):
  • CI runs pytest with --junitxml=reports/junit-unit.xml
  • tools/verify_perf.py parses JUnit and enforces budgets from tests/perf/perf_budgets.json (unit_contracts_total=60s by default)

Lockfiles (B):
  • If requirements-${python}.lock exists (e.g., requirements-3.11.lock), CI installs from it for deterministic toolchains.
  • Fallback order: requirements-${python}.lock → requirements-3.11.lock → requirements.txt → editable project.
  • Generate lockfiles locally with pip-compile and commit them per Python minor.

⸻

12) KPIs that aren’t fairy dust
	•	Test health: 0 collection errors; p95 lukhas_tick_duration_seconds < 35ms in candidate; < 50ms in prod with real I/O stubbed.
	•	Coverage where it counts: 95%+ on core contracts, router, guardian, clock (not blanket repo).
	•	Drift: lukhas_drift_ema < 0.20 in candidate; alert at 0.25; block at 0.35.
	•	Reliability: 0 P0 production incidents per release; MTTR < 30m (measured).
	•	Learning: +N net passing tests in capability regression suite per week (N chosen by capacity, not ego).

⸻

13) Migration of the 11 existing MATRIZ adapters

Pattern (one adapter example):

# matriz/adapters/contradiction_adapter.py
from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from core.trace import mk_crumb

class ContradictionAdapter(MatrizNode):
    name="contradiction-adapter"; version="1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        trace = {"enter": mk_crumb("enter", {"topic": msg.topic})}
        # TODO: map payload -> standardized contradiction structure
        # e.g., {parameter_A, parameter_B, target_improve, side_effect_limit}
        result = {"resolved": False, "candidates": []}
        return MatrizResult(ok=True, payload=result, trace=trace)

Acceptance criterion for each adapter:
	•	Contract compliance: type, fields, trace crumbs.
	•	Golden files: deterministic I/O fixtures for 3 representative inputs.
	•	No network calls in adapter; pure function or stubbed ports.

⸻

14) Consciousness coherence metric (explicit)

Working theory: coherence is the time‑average cosine similarity between intent vector and action consequence vector over the last W ticks, adjusted by constraint satisfaction.

\text{coherence} = \frac{1}{W}\sum_{t=1}^{W} \left( \cos(I_t, A_t) \cdot c_t \right)
where c_t \in [0,1] penalizes constraint violations.

Implement alongside drift.py and export as lukhas_coherence.

⸻

15) Production hardening
	•	Feature flags: DISPATCH_ENABLED, LEARNING_ENABLED, EXT_ACTIONS_ENABLED.
	•	Kill switches: env var or config file toggles; CI blocks if missing.
	•	Rollback: blue/green lanes with canary at 1% traffic in candidate lane; logs compared to baseline before promotion.

⸻

16) Security & governance stubs (tie to LUKHΛS_ID)
	•	Every MatrizMessage includes glyph.tags['subject_sid'] (Symbolic Identity Hash).
	•	Consent & purpose logged per action event; deny by default for missing consent tags.
	•	Add EU AI compliance markers in traces: risk_class, data_origin, explanation_link.

⸻

17) Developer ergonomics
	•	Docstring + usage in every new file, e.g.:

"""
contradiction_adapter.py

Implements MATRIZ contradiction handling behind the Node Contract.

Usage:
  export LUKHAS_LANE=experimental
  python -m matriz.demo.contradiction   # runs demo with fixtures
  pytest -k contradiction -q
"""

	•	Runbook commands:

# Local
export LUKHAS_LANE=experimental
make audit && make test

# Candidate lane simulate
LUKHAS_LANE=candidate pytest -m "not prod_only" -q

# Smoke the ticker for 30s, print p95
python -m core.demo.tick_smoke --seconds 30


⸻

18) “Do this now” task list for Claude (copy/paste checklist)

Phase 0
	•	Create scripts/audit_tests.py and wire make audit.
	•	Add core/lanes.py, conftest.py markers, fail if collection errors > 0.
	•	Introduce matriz/node_contract.py, matriz/router.py (log‑only).
	•	Add core/clock.py, core/ring.py; unit tests test_clock.py.

Phase 1
	•	Wire SymbolicMeshRouter.register/publish into existing calling sites (no dispatch).
	•	Implement lane_guard and mark external‑action code paths as candidate|prod only.
	•	Migrate 11 adapters: create stubs under matriz/adapters/* using Node Contract; 3 golden tests each.
	•	Integrate EQNOX/GLYPH IDs into MatrizMessage headers; add trace crumbs.

Phase 2
	•	Implement consciousness tick loop with decimation; export Prometheus metrics.
	•	Add core/drift.py DriftState and wire to tick; thresholds per lane.
	•	Add memory/folds.py guard and tests for fanout/depth/budget.

Phase 3
	•	Implement core/breakthrough.py; log flags; add cap‑reg tests.
	•	Add event‑sourced storage/events.py and a minimal Replay API.
	•	Add OTEL & Prometheus exporters; Grafana dashboard JSON with panels for tick p95, drift EMA, circuit breaks, breakthroughs.

Promotion rule before scaling:
	•	0 collection errors; contract coverage ≥ 95% lines.
	•	lukhas_tick_duration_seconds:p95 ≤ 35ms (candidate lane).
	•	Drift EMA ≤ 0.20 for 10k ticks; 0 safety interlock breaches.

⸻

19) Prompts you can hand to Claude per step

Prompt A — Create Node Contract & Router (log‑only)

Implement matriz/node_contract.py and matriz/router.py exactly as specified. Do not change field names. Write unit tests that:
	1.	register a node and assert router.register logs are emitted,
	2.	publish a message and assert the router.publish log contains topic, lane, msg_id,
	3.	ensure no actual dispatch occurs (no handle calls).
Use dependency injection for the logger.

Prompt B — Lane Guards

Add core/lanes.py with lane_guard decorator and conftest.py marker behavior. Convert any functions that perform external actions to require @lane_guard(("candidate","prod")). Add a test that setting LUKHAS_LANE=experimental raises RuntimeError for those functions.

Prompt C — Consciousness Tick

Implement core/clock.py and core/ring.py. Add a smoke test to verify the ticker stays within ±5 ticks of the theoretical count for 1s at 30 FPS. Instrument with a Prometheus summary metric lukhas_tick_duration_seconds.

Prompt D — Drift & Memory Guards

Create core/drift.py and memory/folds.py per the code. Add tests: (1) drift EMA increases when intents and actions diverge; (2) fold guard denies excessive fanout/depth and trips the window budget.

Prompt E — Adapter Migration

For each of the 11 MATRIZ adapters, create thin classes inheriting MatrizNode with deterministic I/O using fixtures. No network calls. Provide three golden tests per adapter that verify contract compliance and trace crumbs.

Prompt F — Breakthrough Detector & Replay

Implement core/breakthrough.py and storage/events.py. Add tests where a spike in novelty×value triggers a breakthrough with z=3.0. Provide a minimal API to fetch a sliding window of events for replay.

Prompt G — Observability

Add Prometheus counters/gauges for router publishes, drift EMA, circuit breaks, breakthrough flags. Provide a Grafana dashboard JSON with four panels (tick p95, drift EMA, folds breaker rate, breakthroughs/min).

⸻

20) What we’re not doing yet (on purpose)
	•	No horizontal scale across hundreds of modules until explainability traces are trustworthy.
	•	No “autonomous self‑modification” beyond test‑driven refactors behind the Node Contract.
	•	No external side‑effects in experimental lane. Dry‑run only.

⸻

21) Definition of Done (DoD) per phase
	•	Phase 0 DoD: make audit passes; pytest green; router log‑only; ticker proven.
	•	Phase 1 DoD: 11 adapters behind Node Contract; lanes enforced; EQNOX/GLYPH in headers; 95% contract coverage.
	•	Phase 2 DoD: 30 FPS tick under budget; drift EMA live with alerts; fold guard verified under synthetic storms.
	•	Phase 3 DoD: Replay working; breakthrough flags logged; dashboards online; capability regression suite added to CI.

⸻

22) Practical notes & code style
	•	Keep filenames minimal (fits your preference): node_contract.py, router.py, lanes.py, clock.py, ring.py, drift.py, folds.py, breakthrough.py.
	•	Every module: top docstring + Usage block + a tiny CLI.
	•	Ensure seeded determinism in tests; no sleeps >10ms inside unit tests.

⸻

