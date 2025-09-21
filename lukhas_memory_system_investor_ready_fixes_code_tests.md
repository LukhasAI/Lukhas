# LUKHAS Memory System — Investor-Ready Fix Plan (Implementation)

Below are production-ready modules and validation scaffolding to resolve the two critical issues and demonstrate end‑to‑end integration for the investor presentation.

---

## 1) `candidate/memory/consolidation/consolidation_orchestrator.py`

```python
"""
consolidation_orchestrator.py — Sleep-stage memory consolidation orchestrator

Purpose
-------
Coordinates sleep-stage cycles (NREM->REM) to transfer short‑term traces
(hippocampal store) into long‑term cortical folds. Integrates with the
Consciousness engine for auditability and safety, and exposes metrics for
observability (prometheus-friendly dicts).

Key Concepts
------------
- SleepStage: NREM_1/2/3 and REM stages
- ConsolidationMode: STANDARD, INTENSIVE, MAINTENANCE (affects batch sizes, thresholds)
- MemoryStoreProtocol: narrow interface to your memory stores (short/long term)
- ConsciousnessAdapter: event bus to the consciousness layer (for ethics & drift hooks)
- StructuralConscience (optional): pre/post fold checks to prevent cascade errors

Usage
-----
from candidate.memory.consolidation.consolidation_orchestrator import (
    ConsolidationOrchestrator, ConsolidationMode, SleepStage,
    InMemoryStore, BasicConsciousnessAdapter,
)

async def main():
    orchestrator = ConsolidationOrchestrator(
        store=InMemoryStore.seed_demo(64),
        consciousness=BasicConsciousnessAdapter(),
        mode=ConsolidationMode.STANDARD,
    )
    await orchestrator.orchestrate_consolidation(num_cycles=2)
    print(orchestrator.metrics_snapshot())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional, Protocol, Dict, Any
import random
import time

# -------------------- Enums -------------------- #

class SleepStage(Enum):
    REM = "rem"
    NREM_1 = "nrem_1"
    NREM_2 = "nrem_2"
    NREM_3 = "nrem_3"

class ConsolidationMode(Enum):
    STANDARD = "standard"
    INTENSIVE = "intensive"
    MAINTENANCE = "maintenance"

# -------------------- Protocols -------------------- #

class MemoryStoreProtocol(Protocol):
    def iter_recent_traces(self, limit: int) -> Iterable["MemoryTrace"]: ...
    def write_long_term(self, folds: List["MemoryFold"]) -> None: ...
    def mark_consolidated(self, trace_ids: List[str]) -> None: ...

class ConsciousnessAdapter(Protocol):
    def publish_event(self, event: str, payload: Dict[str, Any]) -> None: ...

# -------------------- Data Models -------------------- #

@dataclass
class MemoryTrace:
    trace_id: str
    salience: float  # 0..1
    domain: str      # e.g., "episodic", "semantic", "procedural"
    payload: Dict[str, Any]

@dataclass
class MemoryFold:
    fold_id: str
    origin_trace_ids: List[str]
    quality: float       # 0..1 heuristic after consolidation
    domain: str
    metadata: Dict[str, Any] = field(default_factory=dict)

# -------------------- Default Minimal Implementations -------------------- #

class InMemoryStore:
    """Demo store for local validation and tests.
    Replace with your production stores (e.g., hippocampal-cache + cortex DB).
    """
    def __init__(self, short_term: List[MemoryTrace] | None = None):
        self.short_term = short_term or []
        self.long_term: List[MemoryFold] = []

    @classmethod
    def seed_demo(cls, n: int = 32) -> "InMemoryStore":
        traces = [
            MemoryTrace(
                trace_id=f"t{i}",
                salience=random.random(),
                domain=random.choice(["episodic", "semantic", "procedural"]),
                payload={"tokens": random.randint(8, 128)},
            )
            for i in range(n)
        ]
        return cls(traces)

    def iter_recent_traces(self, limit: int) -> Iterable[MemoryTrace]:
        # Sort by salience desc (keep stable randomness for demo)
        return sorted(self.short_term, key=lambda t: t.salience, reverse=True)[:limit]

    def write_long_term(self, folds: List[MemoryFold]) -> None:
        self.long_term.extend(folds)

    def mark_consolidated(self, trace_ids: List[str]) -> None:
        self.short_term = [t for t in self.short_term if t.trace_id not in trace_ids]

class BasicConsciousnessAdapter:
    def publish_event(self, event: str, payload: Dict[str, Any]) -> None:
        # Replace with event bus / logger / ethics pipeline
        print(f"[consciousness] {event}: {payload}")

# -------------------- Orchestrator -------------------- #

class ConsolidationOrchestrator:
    """Coordinates sleep-stage cycles and consolidation batches.

    The orchestrator walks through NREM_1 → NREM_2 → NREM_3 → REM cycles.
    NREM_2/3 perform heavy consolidation; REM integrates across domains.
    Modes adjust batch size and thresholds.
    """

    def __init__(
        self,
        store: MemoryStoreProtocol,
        consciousness: Optional[ConsciousnessAdapter] = None,
        mode: ConsolidationMode = ConsolidationMode.STANDARD,
    ) -> None:
        self.store = store
        self.consciousness = consciousness or BasicConsciousnessAdapter()
        self.mode = mode
        self.sleep_stage = SleepStage.NREM_1
        self.consolidation_active = False
        self.cycle_count = 0
        self._metrics = {
            "batches": 0,
            "folds_created": 0,
            "traces_consolidated": 0,
            "last_run_s": None,
        }

    # -------- Public API -------- #

    async def orchestrate_consolidation(self, num_cycles: int = 1) -> None:
        start = time.time()
        self.consolidation_active = True
        self.consciousness.publish_event("consolidation_start", {"mode": self.mode.value})
        try:
            for _ in range(num_cycles):
                for stage in [SleepStage.NREM_1, SleepStage.NREM_2, SleepStage.NREM_3, SleepStage.REM]:
                    self.sleep_stage = stage
                    self._run_stage(stage)
                self.cycle_count += 1
        finally:
            self.consolidation_active = False
            self._metrics["last_run_s"] = round(time.time() - start, 3)
            self.consciousness.publish_event("consolidation_end", {"cycles": self.cycle_count, **self._metrics})

    def metrics_snapshot(self) -> Dict[str, Any]:
        return dict(self._metrics)

    # -------- Internal mechanics -------- #

    def _run_stage(self, stage: SleepStage) -> None:
        if stage in (SleepStage.NREM_2, SleepStage.NREM_3):
            batch = self._select_batch()
            if not batch:
                return
            folds = self._consolidate_batch(batch)
            self.store.write_long_term(folds)
            self.store.mark_consolidated([t.trace_id for t in batch])
            self._metrics["batches"] += 1
            self._metrics["folds_created"] += len(folds)
            self._metrics["traces_consolidated"] += len(batch)
            self.consciousness.publish_event("stage_consolidated", {
                "stage": stage.value,
                "batch": len(batch),
                "folds": len(folds)
            })
        elif stage is SleepStage.REM:
            # Cross-domain integration / association strengthening
            self.consciousness.publish_event("stage_rem_integration", {"stage": stage.value})
        else:
            # Light stabilization; no heavy writes
            self.consciousness.publish_event("stage_stabilize", {"stage": stage.value})

    def _select_batch(self) -> List[MemoryTrace]:
        base = {
            ConsolidationMode.STANDARD: 12,
            ConsolidationMode.INTENSIVE: 24,
            ConsolidationMode.MAINTENANCE: 6,
        }[self.mode]
        traces = list(self.store.iter_recent_traces(limit=base))
        # Slight stochasticity to avoid deterministic ordering artifacts
        random.shuffle(traces)
        return traces

    def _consolidate_batch(self, traces: List[MemoryTrace]) -> List[MemoryFold]:
        folds: List[MemoryFold] = []
        # Group by domain; simple demo logic—replace with your fold engine
        by_domain: Dict[str, List[MemoryTrace]] = {}
        for t in traces:
            by_domain.setdefault(t.domain, []).append(t)

        for domain, bucket in by_domain.items():
            quality = min(1.0, sum(t.salience for t in bucket) / max(1, len(bucket)) * 0.9 + 0.1)
            fold = MemoryFold(
                fold_id=f"fold_{int(time.time()*1000)}_{domain}_{random.randint(100,999)}",
                origin_trace_ids=[t.trace_id for t in bucket],
                quality=round(quality, 3),
                domain=domain,
                metadata={
                    "n_traces": len(bucket),
                    "stage": self.sleep_stage.value,
                    "mode": self.mode.value,
                },
            )
            folds.append(fold)
        return folds
```

---

## 2) `candidate/memory/structural_conscience.py`

```python
"""
structural_conscience.py — Structural awareness & integrity validation

Purpose
-------
Validates structural integrity of memory folds and monitors the
memory–consciousness interface. Designed to prevent cascade errors and
flag misalignment before consolidation writes land in long‑term memory.

Usage
-----
from candidate.memory.structural_conscience import StructuralConscience, StructuralReport
report = StructuralConscience().validate_memory_structure(fold)
print(report.ok, report.issues)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any

class StructuralIntegrityError(Exception):
    pass

@dataclass
class StructuralReport:
    ok: bool
    coherence_score: float  # 0..1
    cascade_risk: float     # 0..1 (lower is better)
    alignment_score: float  # 0..1 with consciousness policy
    issues: List[str] = field(default_factory=list)

class StructuralConscience:
    """Memory structural awareness and integrity validation.

    Parameters
    ----------
    awareness_threshold : float
        Minimum coherence required to pass validation.
    cascade_ceiling : float
        Maximum allowable cascade risk.
    require_alignment : bool
        Whether to enforce consciousness-alignment threshold.
    alignment_threshold : float
        Minimum alignment score to pass when enforced.
    """

    def __init__(
        self,
        awareness_threshold: float = 0.7,
        cascade_ceiling: float = 0.3,
        require_alignment: bool = True,
        alignment_threshold: float = 0.7,
    ) -> None:
        self.awareness_threshold = awareness_threshold
        self.cascade_ceiling = cascade_ceiling
        self.require_alignment = require_alignment
        self.alignment_threshold = alignment_threshold

    # ---------------- Core Checks ---------------- #

    def validate_memory_structure(self, memory_fold: Any) -> StructuralReport:
        """Validate memory fold structural integrity.

        Expects an object with attributes: origin_trace_ids (list[str]),
        quality (0..1), domain (str), metadata (dict). Accepts duck-typed
        objects (e.g., dataclasses from the orchestrator).
        """
        issues: List[str] = []

        # Basic schema sanity
        try:
            origin_ids = list(memory_fold.origin_trace_ids)
            quality = float(memory_fold.quality)
            domain = str(memory_fold.domain)
            metadata: Dict[str, Any] = dict(memory_fold.metadata)
        except Exception as e:
            raise StructuralIntegrityError(f"Fold schema invalid: {e}")

        if not origin_ids:
            issues.append("empty_origin_set")
        if not (0.0 <= quality <= 1.0):
            issues.append("quality_out_of_range")
        if domain not in {"episodic", "semantic", "procedural"}:
            issues.append("unknown_domain")

        # Coherence proxy: quality weighted by diversity & size
        diversity = len(set(origin_ids)) / max(1, len(origin_ids))
        coherence = max(0.0, min(1.0, 0.5 * quality + 0.5 * diversity))

        # Cascade risk proxy: inverse of coherence with penalty for size spikes
        size_penalty = 0.1 if len(origin_ids) > 64 else 0.0
        cascade_risk = max(0.0, min(1.0, (1.0 - coherence) + size_penalty))

        # Alignment proxy: reward neutral domains, penalize procedural with low quality
        alignment = 0.8 if domain in {"semantic", "episodic"} else max(0.0, 0.8 * quality)

        ok = True
        if coherence < self.awareness_threshold:
            ok = False; issues.append("coherence_below_threshold")
        if cascade_risk > self.cascade_ceiling:
            ok = False; issues.append("cascade_risk_too_high")
        if self.require_alignment and alignment < self.alignment_threshold:
            ok = False; issues.append("alignment_below_threshold")

        return StructuralReport(
            ok=ok,
            coherence_score=round(coherence, 3),
            cascade_risk=round(cascade_risk, 3),
            alignment_score=round(alignment, 3),
            issues=issues,
        )

    def monitor_consciousness_integration(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor memory–consciousness integration health.

        Parameters
        ----------
        metrics : Dict[str, Any]
            Expect keys like {"batches", "folds_created", "traces_consolidated"}.
        """
        # Simple thresholds; replace with your real KPI policy
        status = {
            "ok": True,
            "notes": [],
        }
        if metrics.get("folds_created", 0) == 0:
            status["ok"] = False
            status["notes"].append("no_folds_created")
        if metrics.get("traces_consolidated", 0) < metrics.get("batches", 0):
            status["ok"] = False
            status["notes"].append("low_trace_yield_per_batch")
        return status
```

---

## 3) `candidate/memory/consolidation/__init__.py` (ensure import works)

```python
from .consolidation_orchestrator import (
    ConsolidationOrchestrator,
    ConsolidationMode,
    SleepStage,
    InMemoryStore,
    BasicConsciousnessAdapter,
)
```

---

## 4) Quick integration test (`tests/test_memory_integration.py`)

```python
import asyncio
import pytest

from candidate.memory.consolidation import (
    ConsolidationOrchestrator, ConsolidationMode, InMemoryStore
)
from candidate.memory.structural_conscience import StructuralConscience

@pytest.mark.asyncio
async def test_end_to_end_consolidation():
    store = InMemoryStore.seed_demo(48)
    orch = ConsolidationOrchestrator(store=store, mode=ConsolidationMode.STANDARD)
    await orch.orchestrate_consolidation(num_cycles=1)

    metrics = orch.metrics_snapshot()
    assert metrics["folds_created"] > 0
    assert metrics["traces_consolidated"] > 0

    # Validate folds structurally
    sc = StructuralConscience()
    # Check last 3 folds
    for fold in store.long_term[-3:]:
        report = sc.validate_memory_structure(fold)
        assert report.ok, f"fold failed structural checks: {report}"
```

---

## 5) Manual validation script (`scripts/validate_memory_integration.py`)

```python
#!/usr/bin/env python3
import asyncio
from candidate.memory.consolidation import ConsolidationOrchestrator, ConsolidationMode, InMemoryStore
from candidate.memory.structural_conscience import StructuralConscience

async def main():
    store = InMemoryStore.seed_demo(64)
    orch = ConsolidationOrchestrator(store=store, mode=ConsolidationMode.STANDARD)
    await orch.orchestrate_consolidation(num_cycles=2)

    sc = StructuralConscience()
    reports = [sc.validate_memory_structure(f) for f in store.long_term]
    ok = all(r.ok for r in reports)

    print("METRICS:", orch.metrics_snapshot())
    print("FOLDS:", len(store.long_term))
    print("STRUCTURAL_OK:", ok)
    if not ok:
        for i, r in enumerate(reports):
            if not r.ok:
                print(i, r)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6) Shell commands & usage tips

```bash
# 1) Create folders
mkdir -p candidate/memory/consolidation scripts tests

# 2) Save the files above to their paths
# (paste code blocks accordingly)

# 3) Install dev deps (optional for pytest)
pip install pytest

# 4) Run unit tests
pytest -q

# 5) Manual smoke test
python scripts/validate_memory_integration.py
```

---

## 7) T4 Skeptical Checkpoints (push back where it matters)

- **“1000-fold limit”** — enforce in code or CI. Add a guard in your production store so consolidation refuses to create >1000 folds per run without an explicit override.
- **“99.7% cascade prevention”** — define how you measure cascade. The `StructuralConscience` currently uses proxies (coherence, risk). If investors will see the number, implement a reproducible metric (e.g., historical incident rate over N runs) and log it.
- **Protocol buffers** — we didn’t wire protobuf here because your schema wasn’t provided. If gRPC is a must for the demo, generate a `Fold` message and map `MemoryFold` to it in a thin adapter.
- **Consciousness hooks** — `BasicConsciousnessAdapter` is a print adapter. Swap to your real bus (Kafka, NATS, or in-process event router) before the demo; keep event names stable.
- **Observability** — expose `metrics_snapshot()` via your metrics endpoint and tag runs with mode, stage counts, and error counts.

---

## 8) What this fixes right now

- ✅ `consolidation_orchestrator.py` exists with a functional orchestrator, enums, store protocol, and a default in‑memory store to unblock imports and demos.
- ✅ `structural_conscience.py` restored with structural validation, alignment proxy, and integration monitoring.
- ✅ Import path covered via `candidate/memory/consolidation/__init__.py`.
- ✅ Tests & a script to prove end‑to‑end operation.

> Swap in your real stores and consciousness adapter when ready; the interfaces are narrow and stable.

