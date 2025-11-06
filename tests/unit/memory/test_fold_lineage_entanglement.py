"""Unit tests for fold lineage entanglement detection."""

import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_DIR = REPO_ROOT / "memory"

package_spec = importlib.util.spec_from_file_location(
    "memory", PACKAGE_DIR / "__init__.py", submodule_search_locations=[str(PACKAGE_DIR)]
)
memory_pkg = sys.modules.get("memory")
if memory_pkg is None:
    memory_pkg = importlib.util.module_from_spec(package_spec)
    sys.modules["memory"] = memory_pkg
    if package_spec.loader is not None:
        package_spec.loader.exec_module(memory_pkg)

flt_spec = importlib.util.spec_from_file_location(
    "memory.fold_lineage_tracker", PACKAGE_DIR / "fold_lineage_tracker.py"
)
flt_module = importlib.util.module_from_spec(flt_spec)
sys.modules["memory.fold_lineage_tracker"] = flt_module
if flt_spec.loader is not None:
    flt_spec.loader.exec_module(flt_module)


from memory.fold_lineage_tracker import (  # noqa: E402 - test constructs in-memory package before import
    CausationType,
    FoldLineageTracker,
)


# ΛTAG: fold_lineage
def _configure_tracker_paths(tracker: FoldLineageTracker, tmp_path: Path) -> None:
    if not hasattr(flt_module.logger, "bind"):
        def _bind_logger(self, **_kwargs):
            return self

        flt_module.logger.bind = _bind_logger.__get__(flt_module.logger, type(flt_module.logger))  # type: ignore[attr-defined]

    tracker.lineage_log_path = tmp_path / "lineage.jsonl"
    tracker.causal_map_path = tmp_path / "analysis.jsonl"
    tracker.lineage_graph_path = tmp_path / "graph.jsonl"


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
