"""Collapse simulator module alias.

This module re-exports the collapse simulator functionality 
from its actual location in lukhas_website.lukhas.tools.
"""

# Re-export all collapse_simulator functionality from the actual location
from lukhas_website.lukhas.tools.collapse_simulator import (
    DEFAULT_OUTPUT_PATH,
    SimulationContext,
    build_parser,
    compile_summary,
    compute_affect_delta,
    compute_collapse_hash,
    compute_drift_score,
    derive_top_symbols,
    initialize_trace_repair_engine,
    invoke_trace_repair,
    main,
    persist_summary,
    simulate_collapse,
    synthesize_seed,
)

__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "SimulationContext",
    "build_parser", 
    "compile_summary",
    "compute_affect_delta",
    "compute_collapse_hash",
    "compute_drift_score",
    "derive_top_symbols",
    "initialize_trace_repair_engine",
    "invoke_trace_repair",
    "main",
    "persist_summary",
    "simulate_collapse",
    "synthesize_seed",
]