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
from memory.consolidation.consolidation_orchestrator import (
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

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Protocol

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
    def seed_demo(cls, n: int = 32, seed: int | None = None) -> "InMemoryStore":
        rng = random.Random(seed)
        traces = [
            MemoryTrace(
                trace_id=f"t{i}",
                salience=rng.random(),
                domain=rng.choice(["episodic", "semantic", "procedural"]),
                payload={"tokens": rng.randint(8, 128)},
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
        # Policy: ≤1000 folds/run guardrail for cascade prevention
        # Prevents memory overflow and maintains system stability
        self.max_folds_per_run = 1000
        self._metrics = {
            "batches": 0,
            "folds_created": 0,
            "traces_consolidated": 0,
            "quarantined_folds": 0,
            "last_run_s": None,
        }

    # -------- Public API -------- #

    async def orchestrate_consolidation(self, num_cycles: int = 1) -> None:
        start = time.perf_counter()
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
            self._metrics["last_run_s"] = round(time.perf_counter() - start, 4)
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

            # Quarantine failing folds and enforce fold cap
            from memory.structural_conscience import StructuralConscience
            validator = StructuralConscience()
            validated = []
            for f in folds:
                r = validator.validate_memory_structure(f)
                if r.ok:
                    validated.append(f)
                else:
                    self._metrics["quarantined_folds"] += 1
                    self.consciousness.publish_event("fold_quarantined", {
                        "issues": r.issues, "domain": f.domain
                    })

            # Cap per run
            remaining = max(0, self.max_folds_per_run - self._metrics["folds_created"])
            validated = validated[:remaining]
            if not validated:
                return

            self.store.write_long_term(validated)
            self.store.mark_consolidated([t.trace_id for t in batch])
            self._metrics["batches"] += 1
            self._metrics["folds_created"] += len(validated)
            self._metrics["traces_consolidated"] += len(batch)
            self.consciousness.publish_event("stage_consolidated", {
                "stage": stage.value,
                "batch": len(batch),
                "folds": len(validated)
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