"""Collapse simulator CLI for LUKHΛS.

This module provides a symbolic CLI to model collapse + TraceRepair
cycles across memory, ethical, and identity scenarios.

# ΛTAG: collapse
# ΛTAG: trace_repair_hook
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import random
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Dict, List

# NOTE: TraceRepairEngine is optional; defer import to runtime.
try:  # pragma: no cover - import side effects tested via simulation
    from trace.TraceRepairEngine import TraceRepairEngine
except Exception:  # pragma: no cover - optional dependency fallback
    TraceRepairEngine = None  # type: ignore


logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH = pathlib.Path("codex_artifacts/collapse_simulator.json")
DEFAULT_ITERATIONS = 3
DEFAULT_NOISE = 0.05


@dataclass
class SimulationContext:
    """Container for simulation state.

    Tracks drift metrics and TraceRepair invocations for symbolic reporting.
    """

    scenario: str
    iterations: int
    noise: float
    seed: int
    repair_attempts: int = 0
    repair_successes: int = 0
    drift_scores: List[float] = field(default_factory=list)
    affect_deltas: List[float] = field(default_factory=list)
    collapse_hashes: List[str] = field(default_factory=list)

    def record_step(self, drift_score: float, affect_delta: float, collapse_hash: str) -> None:
        self.drift_scores.append(drift_score)
        self.affect_deltas.append(affect_delta)
        self.collapse_hashes.append(collapse_hash)

    @property
    def mean_drift(self) -> float:
        return sum(self.drift_scores) / len(self.drift_scores) if self.drift_scores else 0.0

    @property
    def mean_affect_delta(self) -> float:
        return sum(self.affect_deltas) / len(self.affect_deltas) if self.affect_deltas else 0.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate collapse scenarios and optionally invoke the TraceRepairEngine "
            "to evaluate repair readiness."
        )
    )
    parser.add_argument(
        "scenario",
        choices=("memory", "ethical", "identity"),
        help="Collapse scenario to simulate."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help="Number of collapse iterations to simulate (default: %(default)s)."
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=DEFAULT_NOISE,
        help="Deterministic noise factor applied to drift calculations (default: %(default)s)."
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write JSON summary (default: codex_artifacts/collapse_simulator.json)."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed to override deterministic seed synthesis."
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point for CLI use."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        result = simulate_collapse(
            scenario=args.scenario,
            iterations=args.iterations,
            noise=args.noise,
            output_path=args.output,
            seed_override=args.seed,
        )
    except ValueError as err:
        logger.error("Simulation failed: %s", err)
        parser.error(str(err))
        return 2

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0


def simulate_collapse(
    *,
    scenario: str,
    iterations: int,
    noise: float,
    output_path: pathlib.Path,
    seed_override: int | None = None,
) -> Dict[str, Any]:
    """Simulate a collapse scenario and persist summary JSON."""

    if iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    if noise < 0:
        raise ValueError("noise must be non-negative")

    seed = seed_override if seed_override is not None else synthesize_seed(scenario, iterations, noise)
    rng = random.Random(seed)
    context = SimulationContext(scenario=scenario, iterations=iterations, noise=noise, seed=seed)

    repair_engine = initialize_trace_repair_engine()
    top_symbols = derive_top_symbols(scenario)

    for index in range(iterations):
        drift_score = compute_drift_score(rng, scenario, noise, index)
        affect_delta = compute_affect_delta(rng, scenario, noise, index)
        collapse_hash = compute_collapse_hash(scenario, drift_score, affect_delta, index)
        context.record_step(drift_score, affect_delta, collapse_hash)

        if repair_engine is not None:
            logger.debug(
                "Attempting TraceRepairEngine invocation for scenario=%s iteration=%s", scenario, index
            )
            context.repair_attempts += 1
            if invoke_trace_repair(repair_engine, scenario, drift_score, top_symbols):
                context.repair_successes += 1
        else:
            logger.info(
                "TraceRepairEngine unavailable; skipping repair attempt for scenario=%s iteration=%s",
                scenario,
                index,
            )

    summary = compile_summary(context, top_symbols)
    persist_summary(output_path, summary)
    return summary


def synthesize_seed(scenario: str, iterations: int, noise: float) -> int:
    """Generate a deterministic seed for repeatability."""

    base = hash((scenario, iterations, round(noise, 6))) & 0xFFFFFFFF
    return base or 7  # ensure non-zero seed for stability


def compute_drift_score(rng: random.Random, scenario: str, noise: float, index: int) -> float:
    """Compute symbolic drift score for a simulation step."""

    scenario_bias = {
        "memory": 0.18,
        "ethical": 0.22,
        "identity": 0.20,
    }[scenario]
    drift_variation = (rng.random() - 0.5) * noise
    drift = max(0.0, min(1.0, scenario_bias + drift_variation + index * 0.01))
    return round(drift, 4)


def compute_affect_delta(rng: random.Random, scenario: str, noise: float, index: int) -> float:
    """Compute affect delta metric for symbolic tracing."""

    affect_bias = {
        "memory": 0.05,
        "ethical": 0.08,
        "identity": 0.07,
    }[scenario]
    affect_variation = (rng.random() - 0.5) * noise * 0.5
    affect = affect_bias + affect_variation - index * 0.005
    return round(affect, 4)


def compute_collapse_hash(scenario: str, drift_score: float, affect_delta: float, index: int) -> str:
    """Compute symbolic collapse hash for the iteration."""

    digest_input = f"{scenario}:{drift_score}:{affect_delta}:{index}".encode()
    return str(abs(hash(digest_input)) % 10 ** 10).zfill(10)


def derive_top_symbols(scenario: str) -> List[str]:
    """Return representative top symbols for reporting."""

    symbol_map = {
        "memory": ["MNEME_CORE", "MEMORY_FOLD", "TRACE_THREAD"],
        "ethical": ["ETHOS_VECTOR", "CONSENT_GUARD", "TRUST_LATTICE"],
        "identity": ["SELF_SIM", "COHERENCE_NODE", "ALIGNMENT_TENSOR"],
    }
    return symbol_map.get(scenario, ["UNKNOWN_SYMBOL"])


def initialize_trace_repair_engine() -> TraceRepairEngine | None:
    """Initialize TraceRepairEngine if available."""

    if TraceRepairEngine is None:
        return None

    try:
        return TraceRepairEngine()
    except Exception as exc:  # pragma: no cover - best-effort guardrail
        logger.warning("TraceRepairEngine initialization failed: %s", exc)
        return None


def invoke_trace_repair(
    repair_engine: TraceRepairEngine,
    scenario: str,
    drift_score: float,
    top_symbols: List[str],
) -> bool:
    """Invoke TraceRepairEngine with synthetic context."""

    repair_context = {
        "scenario": scenario,
        "timestamp": time.time(),
        "driftScore": drift_score,
        "top_symbols": top_symbols,
    }
    try:
        result = repair_engine.reconsolidate(
            kind=scenario,
            score=drift_score,
            context=repair_context,
            top_symbols=top_symbols,
        )
    except Exception as exc:
        logger.debug("TraceRepairEngine reconsolidate raised exception: %s", exc)
        return False

    success = getattr(result, "success", False)
    return bool(success)


def compile_summary(context: SimulationContext, top_symbols: List[str]) -> Dict[str, Any]:
    """Prepare JSON summary payload for persistence."""

    summary = {
        "scenario": context.scenario,
        "iterations": context.iterations,
        "repairsInvoked": context.repair_attempts,
        "repairsSucceeded": context.repair_successes,
        "driftScore": round(context.mean_drift, 4),
        "affect_delta": round(context.mean_affect_delta, 4),
        "top_symbols": top_symbols,
        "collapseHash": context.collapse_hashes[-1] if context.collapse_hashes else "0" * 10,
        "seed": context.seed,
    }
    return summary


def persist_summary(output_path: pathlib.Path, summary: Dict[str, Any]) -> None:
    """Persist JSON summary to disk, ensuring directories exist."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2)
        fp.write("\n")


# ΛTAG: collapse_cli
# ΛTAG: fallback_protocol
# TODO: Integrate with real collapse telemetry stream once available.
if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
