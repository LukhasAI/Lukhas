"""Unit tests for fold lineage entanglement detection."""

import os
import sys

from pathlib import Path

import pytest

import memory.fold_lineage_tracker as flt_module

if "memory" in sys.modules:
    del sys.modules["memory"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from memory.fold_lineage_tracker import CausationType, FoldLineageTracker


# ΛTAG: fold_lineage
def _configure_tracker_paths(tracker: FoldLineageTracker, tmp_path: Path) -> None:
    if not hasattr(flt_module.logger, "bind"):
        def _bind_logger(self, **_kwargs):
            return self

        flt_module.logger.bind = _bind_logger.__get__(flt_module.logger, type(flt_module.logger))  # type: ignore[attr-defined]

    tracker.lineage_log_path = str(tmp_path / "lineage.jsonl")
    tracker.causal_map_path = str(tmp_path / "analysis.jsonl")
    tracker.lineage_graph_path = str(tmp_path / "graph.jsonl")


def test_entanglement_detection_correlates_with_dreams(tmp_path):
    tracker = FoldLineageTracker()
    _configure_tracker_paths(tracker, tmp_path)

    tracker.track_fold_state(
        "root-fold",
        importance_score=0.7,
        drift_score=0.3,
        content_hash="hash-root",
        causative_events=["dream:alpha"],
    )
    tracker.track_fold_state(
        "child-fold",
        importance_score=0.6,
        drift_score=0.4,
        content_hash="hash-child",
        causative_events=["dream:alpha"],
    )
    tracker.track_causation(
        "root-fold",
        "child-fold",
        CausationType.QUANTUM_ENTANGLEMENT,
        strength=0.9,
        metadata={"dream_id": "alpha", "entanglement_level": 0.75},
    )

    analysis = tracker.analyze_fold_lineage("child-fold")
    entanglement = analysis["entanglement_analysis"]

    assert entanglement["status"] == "detected"
    assert entanglement["entangled_links"] == 1
    assert entanglement["dream_correlations"][0]["dream_id"] == "alpha"
    assert set(entanglement["dream_correlations"][0]["folds"]) == {"root-fold", "child-fold"}

