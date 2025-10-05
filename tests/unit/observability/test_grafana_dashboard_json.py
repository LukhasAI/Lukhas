"""
tests/unit/observability/test_grafana_dashboard_json.py

Tiny CI guard to ensure the four load-bearing PromQL expressions don't vanish.
Prevents dashboard drift during refactoring or metric name changes.
"""
import json
from pathlib import Path


def test_dashboard_queries_present():
    """Test that essential PromQL queries are present in Grafana dashboard."""
    p = Path("dashboards/lukhas_ops.json")
    data = json.loads(p.read_text())
    exprs = {t.get("expr") for panel in data["panels"] for t in panel.get("targets", [])}
    expected = {
        '1000 * histogram_quantile(0.95, sum by (le, lane) (rate(lukhas_tick_duration_seconds_bucket{lane=~"$lane"}[5m])))',
        'lukhas_drift_ema{lane=~"$lane"}',
        'rate(lukhas_memory_circuit_breaks_total[5m]) * 60',
        'rate(lukhas_breakthrough_flags_total[5m]) * 60',
    }
    missing = expected - exprs
    assert not missing, f"Missing queries: {missing}"


def test_dashboard_structure():
    """Test basic dashboard structure and metadata."""
    p = Path("dashboards/lukhas_ops.json")
    data = json.loads(p.read_text())

    # Core structure
    assert data["uid"] == "lukhas-ops"
    assert data["title"] == "LUKHAS Operations"
    assert data["timezone"] == "utc"

    # Should have exactly 4 panels
    assert len(data["panels"]) == 4

    # Panel titles match expected
    panel_titles = {panel["title"] for panel in data["panels"]}
    expected_titles = {
        "Consciousness Tick p95 (ms)",
        "Drift EMA by Lane",
        "Memory Circuit Breaks (rate / min)",
        "Breakthroughs / min"
    }
    assert panel_titles == expected_titles


def test_dashboard_thresholds():
    """Test that drift panel has proper warning/critical thresholds."""
    p = Path("dashboards/lukhas_ops.json")
    data = json.loads(p.read_text())

    # Find drift panel (ID 2)
    drift_panel = next(panel for panel in data["panels"] if panel["id"] == 2)

    # Check thresholds match our lane configurations
    steps = drift_panel["thresholds"]["steps"]
    threshold_values = {step["value"] for step in steps}

    # Should include 0.2 (warn) and 0.35 (critical) matching lane configs
    assert 0.2 in threshold_values  # Candidate warn threshold
    assert 0.35 in threshold_values  # Candidate block threshold


def test_dashboard_lane_template():
    """Test that lane template variable is properly configured."""
    p = Path("dashboards/lukhas_ops.json")
    data = json.loads(p.read_text())

    # Should have one template variable for lane
    templates = data["templating"]["list"]
    assert len(templates) == 1

    lane_template = templates[0]
    assert lane_template["name"] == "lane"
    assert lane_template["query"] == "label_values(lukhas_drift_ema, lane)"
    assert lane_template["includeAll"] is True
    assert lane_template["multi"] is True


def test_dashboard_json_validity():
    """Test that dashboard JSON is valid and well-formed."""
    p = Path("dashboards/lukhas_ops.json")

    # Should parse without errors
    data = json.loads(p.read_text())

    # Basic validation
    assert isinstance(data, dict)
    assert "panels" in data
    assert "templating" in data
    assert isinstance(data["panels"], list)
