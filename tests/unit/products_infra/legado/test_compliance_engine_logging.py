import json
import sys
from pathlib import Path

from products.infrastructure.legado.legacy_systems.compliance.engine import (
    AdvancedComplianceEthicsEngine,
)

path_obj = Path(__file__).resolve()
tests_unit_path = str(path_obj.parents[2])
if tests_unit_path in sys.path:
    sys.path.remove(tests_unit_path)

sys.path.insert(0, str(path_obj.parents[4]))



def test_compliance_engine_logging_and_timezone(tmp_path):
    violation_log = tmp_path / "violations.jsonl"
    drift_log = tmp_path / "drift.jsonl"

    engine = AdvancedComplianceEthicsEngine(
        config={
            "access_cultural_guard_config": {"violation_log_path": str(violation_log)},
            "ethics_drift_config": {"ethics_drift_log_path": str(drift_log), "ethical_threshold_for_drift": 0.75},
        }
    )

    engine.access_cultural_guard_module.log_violation(
        signal="test-signal",
        tier=2,
        context={"tier": 1},
        explanation="unit-test",
    )

    violation_entries = violation_log.read_text(encoding="utf-8").strip().splitlines()
    assert violation_entries
    entry = json.loads(violation_entries[-1])
    assert entry["timestamp"].endswith("Z")

    report = engine.perform_ethics_drift_detection(
        decision_log=[{"alignment_score": 0.9}, {"alignment_score": 0.4}],
        custom_threshold=0.8,
    )
    assert report["timestamp"].endswith("Z")
    assert (drift_log.exists())
    assert "AdvancedComplianceEthicsEngine" in engine.core_ethics_module.logger.name
