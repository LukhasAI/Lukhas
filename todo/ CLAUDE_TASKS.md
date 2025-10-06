---
status: wip
type: documentation
---


# CLAUDE_TASKS.md — T4 Delta Plan (Authoritative)

> **You are Claude Code operating inside the Lukhas repo.**
> This file is at the **repo root** and is the **canonical task driver**. If runtime context is missing or stale, re-open and follow this file verbatim.

---

## Operating Mode (Read Me First)
- **Follow-Source**: Treat this file and `docs/gonzo/T4-DELTA-PLAN.md` as source of truth. Do not improvise scope.
- **Small, Reviewable PRs**: One atomic concern per PR; include tests and docs.
- **Safety First**: Default lane is `experimental`; **no external side-effects** in experimental. Use dry-run paths.
- **Determinism**: Use `PYTHONHASHSEED=0`, `TZ=UTC`, `LUKHAS_RNG_SEED=42`. Avoid non-deterministic sleeps/timers in unit tests.
- **Feature Flags (default off)**: `DISPATCH_ENABLED=false`, `LEARNING_ENABLED=false`, `EXT_ACTIONS_ENABLED=false`.
- **Prompts in-tree**: Every automated change must reference a section from this file or `T4-DELTA-PLAN.md`.
- **Phase header dedup guard**: The only valid Phase 5 section is **"Phase 5 — Governance & Memory Synchronization (Planned 🚧)"**. If any other "Phase 5" header appears, treat it as deprecated and delete it in the same PR.

---

## Primary Objectives (T4 delta plan — **critical path, not wish list**)
The full prose lives in `docs/gonzo/T4-DELTA-PLAN.md`. Below is the actionable extraction for Claude Code.

### Phase 0 — Trunk health & reality checks (2–3 days)
- Make tests **collectible (0 errors)**.
- Add deterministic **30 FPS ticker** + observability skeleton (no features yet).
- Freeze **MATRIZ Node Contract v1** and **SymbolicMeshRouter** in **log-only** mode.

### Phase 1 — Contracts, lanes, and safety (1 week)
- Enforce **lane guards** (experimental/candidate/prod) via decorator + CI gates.
- Migrate **11 MATRIZ adapters** behind Node Contract (thin wrappers with golden fixtures).
- Wire **EQNOX/GLYPH identities** into message headers; carry trace crumbs.

### Phase 2 — Consciousness stream & drift (1 week)
- Implement **33ms consciousness tick** with ring buffers, decimation, backpressure.
- Ship **DriftScore v2** (windowed, per-lane) + **fold-cascade guard** on memory.

### Phase 3 — Learning loop & observability (1 week)
- Stand up **Experience Replay** (event-sourced), **BreakthroughDetector** (novelty×value), **explainability traces**.
- **Prometheus + OTEL** exporters, red/green dashboards, and a **capability regression suite**.

> Then scale. **Not before.**

---

## Immediate Execution Checklist (copy/paste run of show)
### Phase 0
- [ ] Create `scripts/audit_tests.py` and wire `make audit`.
- [ ] Add `core/lanes.py`, `conftest.py` markers; fail CI if **any** collection error.
- [ ] Introduce `matriz/node_contract.py`, `matriz/router.py` (**log‑only**).
- [ ] Add `core/clock.py`, `core/ring.py`; add `tests/test_clock.py`.

### Phase 1
- [ ] Wire `SymbolicMeshRouter.register/publish` into callsites (**no dispatch** yet).
- [ ] Implement `lane_guard`; mark external-action code paths as `candidate|prod` only.
- [ ] Migrate **11 adapters** under `matriz/adapters/*` using Node Contract; **3 golden tests each**.
- [ ] Integrate EQNOX/GLYPH IDs into `MatrizMessage` headers; add trace crumbs everywhere.

### Phase 2
- [ ] Implement central tick with decimation & metrics; export `lukhas_tick_duration_seconds`.
- [ ] Add `core/drift.py` (per-lane thresholds) and `memory/folds.py` guard + tests.

### Phase 3 (COMPLETED)
- [x] Implement `core/breakthrough.py`; log flags; add capability-regression tests.
- [x] Implement `storage/events.py` (event-sourced) + minimal Replay API.
- [x] Add Prometheus exporters + `dashboards/lukhas_ops.json` (tick p95, drift EMA, folds breaker, breakthroughs/min).

---

## Guardrails & CI Contracts (enforced)
- **Lane isolation**: `LUKHAS_LANE=experimental` in dev/CI; promotion requires candidate gate.
- **Strict emit (CI)**: `LUKHAS_STRICT_EMIT=1` → conflicting kwargs in signal emitters **raise**.
- **Hermetic runs**: Use pinned lockfiles when present: `requirements-${py}.lock` → `requirements-3.11.lock` → `requirements.txt`.
- **Zero-flake policy**: If any test reruns (`pytest-rerunfailures`) → **fail CI**.
- **Performance budgets**: enforce via `tests/perf_budgets.json` and JUnit parsing.
- **Toolchain lock-step**: use `requirements-{3.9,3.10,3.11}.lock`; weekly unlocked check runs separately.
- **Success log gates** (grep-able): require presence of "slowest 10 durations" for each suite and summary line "✅ All Python versions passed".
- **Observability validation**: verify Grafana dashboard JSON loads and alert PROMQL compiles during CI.
- **Stability sentinels**: fail if any of:
  - `lukhas_router_no_rule_total` rate > 0 over 5m (capability suite).
  - `lukhas_drift_ema{lane="prod"} > 0.35` in alert validation.
  - E2E network coherence < 0.70.
  - Presence of "Zero unrouted signals" and "coherence ≥0.8" in smoke logs.

---

## File Map (you may create/modify only these in each step)
- `scripts/audit_tests.py` — collection must be zero.
- `matriz/node_contract.py`, `matriz/router.py` — **frozen v1** (router starts log‑only).
- `core/lanes.py`, `core/clock.py`, `core/ring.py`, `core/drift.py`, `core/trace.py`.
- `memory/folds.py`, `core/breakthrough.py`, `storage/events.py`.
- `tests/**` — unit/contract/capability/E2E per taxonomy.
- `dashboards/lukhas_ops.json` — Grafana panels (tick p95, drift EMA, folds breaker, breakthroughs/min).

> For detailed scaffolds and code snippets, see `docs/gonzo/T4-DELTA-PLAN.md` (sections 0–22). Mirror names/fields **exactly**.

---

## DoD Gates (copy into PR description)
- **Phase 0**: `make audit` passes; pytest green; router log‑only; ticker proven.
- **Phase 1**: 11 adapters behind Node Contract; lanes enforced; EQNOX/GLYPH in headers; **95% contract coverage** (contracts/router/clock/guardian).
- **Phase 2**: 30 FPS tick under budget; drift EMA live with alerts; fold guard verified under synthetic storms.
- **Phase 3**: Replay working; breakthrough flags logged; dashboards online; capability regression suite in CI.

---

## Commands (copy/paste)
```bash
# Local baseline
export LUKHAS_LANE=experimental PYTHONHASHSEED=0 TZ=UTC LUKHAS_RNG_SEED=42
make audit && pytest -q

# Candidate lane rehearsal (no prod-only tests)
LUKHAS_LANE=candidate pytest -m "not prod_only" -q

# Smoke the ticker for 30s and print p95
python -m core.demo.tick_smoke --seconds 30
```

---

## Commit/PR Conventions
- **feat(t4): <scope> — <short imperative>** for plan-driven features
- **fix(t4): <scope> — <short imperative>** for corrections against this plan
- Always link the exact checklist item and plan section (e.g., *Phase 1 → Adapter Migration*).

---

## Reminder
If a task cannot be completed **because** upstream code is missing or deviates from this plan, open a PR that:
1) adds the smallest shim or stub to satisfy the contract, 2) adds tests, 3) files a follow-up TODO with owner.

**Do not proceed** to later phases until the current phase’s DoD gates are green.

----



⸻

Phase 2 — Consciousness Stream & Drift (T4-DELTA tips)

0) Non-negotiables
	•	Determinism: TZ=UTC, PYTHONHASHSEED=0, stable seeds in tests.
	•	No network. Pure, fast unit tests; E2E only in smoke.
	•	Metrics optional: import Prometheus if present; otherwise use no-op shims.
	•	Per-lane thresholds: experimental more lenient than candidate > prod.

⸻

1) core/drift.py — DriftScore v2 (windowed cosine + EMA)

Create a single module with:
	•	cosine similarity (safe for zero vectors),
	•	instantaneous drift 1 - cos,
	•	EMA smoothing with α,
	•	small fixed window (e.g., 64) for raw stats,
	•	per-lane thresholds & guard decision, plus optional Prometheus export.

# core/drift.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math
import os

# Optional metrics
try:
    from prometheus_client import Gauge
    DRIFT_EMA = Gauge("lukhas_drift_ema", "EMA drift", ["lane"])
    PROM = True
except Exception:
    PROM = False
    class _Noop:  # minimal no-op
        def labels(self, *_, **__): return self
        def set(self, *_): pass
    DRIFT_EMA = _Noop()

@dataclass(frozen=True)
class DriftConfig:
    warn_threshold: float
    block_threshold: float
    alpha: float = 0.2
    window: int = 64  # small, bounded

LANE_CFG: Dict[str, DriftConfig] = {
    "experimental": DriftConfig(0.30, 0.50),
    "candidate":    DriftConfig(0.20, 0.35),
    "prod":         DriftConfig(0.15, 0.25),
}

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(y*y for y in b))
    if na == 0.0 or nb == 0.0: return 0.0
    # Clamp to avoid FP wobble
    v = max(-1.0, min(1.0, dot/(na*nb)))
    return v

class DriftMonitor:
    __slots__ = ("lane","cfg","ema","_raw")
    def __init__(self, lane: Optional[str] = None):
        self.lane = (lane or os.getenv("LUKHAS_LANE", "experimental")).lower()
        self.cfg  = LANE_CFG.get(self.lane, LANE_CFG["experimental"])
        self.ema: float = 0.0
        self._raw: List[float] = []

    def update(self, intent: List[float], action: List[float]) -> Dict[str, object]:
        sim   = _cosine(intent, action)
        drift = 1.0 - sim

        # windowed raw drift
        self._raw.append(drift)
        if len(self._raw) > self.cfg.window:
            self._raw.pop(0)

        # EMA smoothing
        self.ema = self.cfg.alpha * drift + (1.0 - self.cfg.alpha) * self.ema

        # decision
        guardian = "allow"
        if self.ema >= self.cfg.block_threshold:
            guardian = "block"
        elif self.ema >= self.cfg.warn_threshold:
            guardian = "warn"

        if PROM:
            DRIFT_EMA.labels(lane=self.lane).set(self.ema)

        return {
            "lane": self.lane,
            "drift": drift,
            "ema": self.ema,
            "guardian": guardian,
            "n": len(self._raw),
        }

Unit tests (tests/test_drift.py)
	•	Zero vectors → similarity 0 → drift 1.
	•	Orthogonal vectors → drift ~1.
	•	Identical vectors → drift 0; EMA stays 0; guardian “allow”.
	•	Threshold behavior per lane: fabricate updates to cross warn/block.

⸻

2) memory/folds.py — FoldGuard with circuit breaker

Bounded fanout, depth, and per-tick operation budget with clear failure codes; optional metric for breaker trips.

# memory/folds.py
from __future__ import annotations
from dataclasses import dataclass

try:
    from prometheus_client import Counter
    MEM_BREAKS = Counter("lukhas_memory_circuit_breaks_total", "Memory circuit trips")
    PROM = True
except Exception:
    PROM = False
    class _No: 
        def inc(self,*_): pass
    MEM_BREAKS = _No()

@dataclass
class FoldGuard:
    max_fanout: int = 8
    max_depth: int = 4
    window_budget: int = 256

    def __post_init__(self):
        self._ops = 0
        self._fan = 0
        self._depth = 0
        self.tripped = False

    def start_tick(self):
        self._ops = 0; self._fan = 0; self._depth = 0; self.tripped = False

    def allow(self, fanout: int, depth: int, cost: int = 1) -> bool:
        if self.tripped: return False
        self._fan += fanout
        self._depth = max(self._depth, depth)
        self._ops += cost
        ok = (self._fan <= self.max_fanout and
              self._depth <= self.max_depth and
              self._ops <= self.window_budget)
        if not ok:
            self.tripped = True
            if PROM: MEM_BREAKS.inc()
        return ok

    @property
    def window(self) -> int: return self._fan
    @property
    def ops(self) -> int: return self._ops
    @property
    def depth(self) -> int: return self._depth

Unit tests (tests/test_folds.py)
	•	Permit up to max_fanout, then deny.
	•	Depth overflow triggers trip.
	•	Budget overflow triggers trip and increments metric (if available).
	•	start_tick() resets safely.

⸻

3) Consciousness tick routing through core/clock.py

You already have Ticker. Wire a thin coordinator that:
	•	subscribes to Ticker,
	•	pushes frames into a Ring,
	•	performs decimation when buffer > threshold,
	•	exports tick duration and ticks_dropped.

Patch core/ring.py to add pop_all() and __len__ if missing.

Coordinator skeleton (core/consciousness_ticker.py):

from core.clock import Ticker
from core.ring import Ring
from time import perf_counter

try:
    from prometheus_client import Histogram, Counter
    TICK = Histogram("lukhas_tick_duration_seconds","Tick time",["lane"])
    TICKS_DROPPED = Counter("lukhas_ticks_dropped_total","Dropped ticks",["lane"])
    SUB_EXC = Counter("lukhas_subscriber_exceptions_total","Subscriber exceptions",["lane"])
    PROM=True
except Exception:
    class _N: 
        def labels(self,*_,**__): return self
        def observe(self,*_): pass
        def inc(self,*_): pass
    TICK=_N(); TICKS_DROPPED=_N(); SUB_EXC=_N(); PROM=False

import os
LANE = os.getenv("LUKHAS_LANE","experimental")

class ConsciousnessTicker:
    def __init__(self, fps: int = 30, cap: int = 120):
        self.ticker = Ticker(fps=fps)
        self.buffer = Ring(capacity=cap)
        self.ticker.subscribe(self._on_tick)

    def _on_tick(self, tick_count: int):
        t0 = perf_counter()
        try:
            frame = {"id": tick_count}  # keep it deterministic for tests
            self.buffer.push(frame)
            if len(self.buffer) > int(self.buffer.capacity * 0.8):
                self._decimate()
        except Exception:
            SUB_EXC.labels(lane=LANE).inc()
            raise
        finally:
            dur = perf_counter() - t0
            TICK.labels(lane=LANE).observe(dur)

    def _decimate(self):
        frames = self.buffer.pop_all()
        keep = frames[-(self.buffer.capacity // 2):]
        for f in keep:
            self.buffer.push(f)
        # A “drop” is conceptual at the coordinator level too
        TICKS_DROPPED.labels(lane=LANE).inc()

Unit test (tests/test_consciousness_tick.py)
	•	Spin a Ticker for ~0.2s at 30 FPS and assert tick counts grow and len(buffer) <= capacity.
	•	Force overload (tiny capacity) and assert decimation reduces backlog.
	•	p95 budget: < 35 ms (assert via histogram presence or local timing).

⸻

4) Metrics registry (central import)

If you already introduced candidate/core/metrics.py earlier, keep using it. Otherwise keep local, optional instrumentation as above to avoid import cycles. The key exported names CI checks for:
	•	lukhas_tick_duration_seconds
	•	lukhas_drift_ema
	•	lukhas_memory_circuit_breaks_total
	•	lukhas_ticks_dropped_total (new)
	•	lukhas_subscriber_exceptions_total (new)

⸻

5) Tests to add (minimal, fast, deterministic)

tests/
  test_drift.py                    # unit: thresholds + ema + zero-vector safety
  test_folds.py                    # unit: fanout/depth/budget + circuit breaker
  test_consciousness_tick.py       # unit: buffer + decimation + duration budget

Performance budgets (asserts / xfail gates):
	•	test_consciousness_tick.py: p95 < 35 ms (we can approximate by sleeping total 0.2s and asserting tick_count ≥ 4 and no backlog > capacity).
	•	test_folds.py: < 50 ms runtime.
	•	test_drift.py: < 50 ms runtime.

⸻

6) Per-lane thresholds wiring
	•	DriftMonitor(lane=...) should default from LUKHAS_LANE.
	•	Add a tiny test matrix param over ["experimental","candidate","prod"] to verify guardian actions for the same synthetic sequence.

⸻

7) CI wiring (Phase 2 target)
	•	Audit: make audit returns 0.
	•	Tests: pytest tests/test_drift.py tests/test_folds.py tests/test_consciousness_tick.py -q.
	•	Env: LUKHAS_LANE=experimental, DISPATCH_ENABLED=false.
	•	Perf gate: assert presence of “slowest 10 durations” and total wall time < 60s for Phase 2 slice.

⸻

8) Gotchas (pre-emptive)
	•	Don’t store unbounded lists: drift window is capped, ring has capacity.
	•	Guard division-by-zero in cosine.
	•	Avoid global Prometheus imports causing test failures; keep them optional.
	•	No async here—keep the Phase 2 tests synchronous and snappy.
	•	Keep types precise; don’t return numpy arrays from update()—plain Python types only.

⸻

9) Definition of Done (Phase 2)
	•	✅ core/drift.py with per-lane thresholds, EMA, window, and (optional) metric export.
	•	✅ memory/folds.py with fanout/depth/budget guard and circuit breaker metric.
	•	✅ core/consciousness_ticker.py routes ticks via core/clock.py, decimates on backpressure, exports tick/counters.
	•	✅ New unit tests green under time budgets.
	•	✅ make audit green.
	•	✅ Metrics names present (Prometheus installed in CI path).

⸻

---

## Phase 2 — Summary (Completed ✅)

**PR:** [#316](https://github.com/LukhasAI/Lukhas/pull/316)  
**Date:** 2025-09-17  

### Deliverables
- `core/drift.py`: DriftScore v2 (cosine, EMA, per-lane thresholds).
- `memory/folds.py`: FoldGuard (fanout/depth/budget breaker).
- `core/consciousness_ticker.py`: 30 FPS coordinator w/ ring decimation & metrics.
- Optional Prometheus metrics with no-op fallbacks:
  - `lukhas_drift_ema`
  - `lukhas_memory_circuit_breaks_total`
  - `lukhas_tick_duration_seconds`
  - `lukhas_ticks_dropped_total`
  - `lukhas_subscriber_exceptions_total`

### Tests & Performance
- 51 new tests green (<1s total).
- All under budget:
  - `test_drift.py`: <50ms
  - `test_folds.py`: <50ms
  - `test_consciousness_tick.py`: <35ms p95
- `make audit` passes (0 collection errors).

### Guardrails
- Deterministic env: `PYTHONHASHSEED=0`, `TZ=UTC`, `LUKHAS_RNG_SEED=42`.
- Per-lane thresholds:
  - experimental → warn 0.30 / block 0.50
  - candidate → warn 0.20 / block 0.35
  - prod → warn 0.15 / block 0.25
- Router still log-only; no dispatch.
- No network; pure CPU/memory tests.

### ✅ DoD Met
- Consciousness tick routed at 33ms, backlog decimates correctly.
- Drift EMA & guardian verified across all lanes.
- FoldGuard trips on fanout/depth/budget overflows.
- Prometheus names exported and stable.

---

## Phase 3 — Learning Loop & Observability (Completed ✅)

**PR:** [#317](https://github.com/LukhasAI/Lukhas/pull/317)  
**Branch:** `feat/t4-phase3-learning-observability`  
**Date:** 2025-09-17

### Deliverables
- `lukhas/core/breakthrough.py`: novelty × value detection (z-score, Welford online stats).
- `storage/events.py`: event-sourced replay + sliding-window queries, bounded capacity, glyph/kind indexes.
- `dashboards/lukhas_ops.json`: 4-panel ops dashboard (tick p95, drift EMA, fold breakers, breakthroughs/min) with lane templating.
- `lukhas/core/metrics_exporters.py`: Prometheus + OTEL exporters (safe defaults; noop fallbacks).
- Capability regression suite: `tests/capabilities/test_observability_contracts.py` (with module reload to avoid registry collisions).

### Tests & Performance
- All capability tests green; exporters validated in enabled/disabled modes.
- `make dash-validate` verifies dashboard schema and query presence.
- `curl /metrics` happy-path works when `LUKHAS_PROM_PORT` set.
- Suite time: < 1s; per-test < 500ms; deterministic ("slowest 10 durations" present).

### Guardrails
- Hermetic env (`PYTHONHASHSEED=0`, `TZ=UTC`); no external IO.
- Defensive metrics registration; graceful fallbacks for missing deps.
- Module reload pattern to reset singletons (`_PROM_SERVER`, `_otel_inited`) between tests.

### ✅ DoD Met
- Replay API correct ordering (recent: newest→oldest; replay: oldest→newest).
- Breakthrough flags logged and counter exported.
- Dashboard and alerts compile; capability regression suite green.

---

## Next: Phase 4 — Consciousness Stream Integration (Planned 🚧)

**Targets**
- Wire live stream: **Ticker → Router → EventStore** (no external dispatch).
- Per-stream metrics: breakthroughs/min, tick p95, drift EMA by lane.
- Experience Replay golden fixtures: deterministic replays under load.
- Backpressure guarantees: ring decimation & zero drops beyond allowed budget.
- Capability suite: stream-continuity tests (zero unrouted, coherence ≥0.8).

**DoD (Phase 4)**
- Live stream produces events into `EventStore` each tick.
- Zero unrouted signals in capability logs; cascade prevention active.
- Performance budgets green (suite < 60s; per-test < 500ms).
- Grafana panels reflect live metrics; alerts validate in CI.
- PR with DoD checklist + updates to this file's Phase 4 section.

## Phase 2 Summary (Baseline before Phase 4)

- **Drift v2:** windowed EMA, cosine drift; thresholds — prod(0.15/0.25), candidate(0.20/0.35), experimental(0.30/0.50)
- **FoldGuard:** fanout/depth/budget limits + circuit breaker; Prom counter `lukhas_memory_circuit_breaks_total`
- **Consciousness Ticker:** 33ms target; ring buffer decimation @80% fill; Prom histogram `lukhas_tick_duration_seconds`
- **Tests:** 51 tests; all <50ms; audit green; “slowest 10 durations” present
- **Guardrails:** deterministic env (PYTHONHASHSEED=0, TZ=UTC), no external IO, strict emit in CI

**Status:** Green across py3.9/3.10/3.11; coherence ≥0.8; zero unrouted.

---

## CI Success Gates — Log Signatures

Claude Code should verify these appear in CI logs:
- `============================= slowest 10 durations =============================` (for each suite)
- `✅ All Python versions passed: 3.9, 3.10, 3.11`
- `Zero unrouted signals` and `coherence ≥0.8`
- `Dashboard JSON validated` and `Alert rules validated`
- No occurrences of: `Router missing routing rules`, `zero routing rules configured`, `NotOpenSSLWarning` escalations, or `flake rerun needed`

## Phase 5 — Governance & Memory Synchronization (Planned 🚧)

**Starting point:** Phase 4 is green (continuity, backpressure, metrics). Begin governance on top of the stable stream & replay stack.

### Targets
- Introduce **policy‑gated learning** over Experience Replay (policies decide what can be replayed and at which lane).
- Add **cross‑lane promotion gates** using drift/coherence signals (promote only when thresholds stable for a window).
- Synchronize **memory folds** across lanes with governance guardrails (bounded fan‑in/out, budgeted ops).
- Extend capability suite with **governance regression tests** (policy denial/allow, promotion success, sync safety).

### Deliverables
- `lukhas/core/policy_guard.py` — Lane‑aware replay policy checker with deterministic allow/deny logs.
- `lukhas/memory/sync.py` — Memory fold synchronization module with bounded fan‑in/out and per‑tick budgets.
- Tests:
  - `tests/test_policy_guard.py` — replay policy enforcement matrix (lanes × kinds × thresholds).
  - `tests/test_memory_sync.py` — fold synchronization safety (fanout/depth/budget trips, idempotency).
  - `tests/capabilities/test_governance_suite.py` — end‑to‑end promotion/policy/coherence regression.

### Observability
- Prometheus counters (with no‑op fallbacks):
  - `lukhas_replay_policy_denials_total`
  - `lukhas_promotion_attempts_total`
  - `lukhas_promotion_success_total`
- Grafana: add panels for **policy denials/min** and **promotion success rate** to `dashboards/lukhas_ops.json`.

### File Map additions (Phase 5 only)
- `lukhas/core/policy_guard.py`
- `lukhas/memory/sync.py`
- `tests/test_policy_guard.py`
- `tests/test_memory_sync.py`
- `tests/capabilities/test_governance_suite.py`
- (Dashboard tweak) `dashboards/lukhas_ops.json` — append two panels as above.

### DoD (Phase 5)
- Replay governed by policy with deterministic allow/deny logs (lane‑scoped).
- Lane promotions succeed only when **drift/coherence** within thresholds for a configured window.
- Memory synchronization across folds proven safe in tests (fanout/depth/budget respected, no unbounded state).
- Governance regression suite green with “slowest 10 durations” present; all tests within budgets.
- All metrics exported with no‑op fallbacks; Grafana/alert JSON validates in CI.


-----

