import logging
import sys
from pathlib import Path

import pytest
from products.infrastructure.legado.legacy_systems.safety import compliance_dashboard

path_obj = Path(__file__).resolve()
tests_unit_path = str(path_obj.parents[2])
if tests_unit_path in sys.path:
    sys.path.remove(tests_unit_path)

sys.path.insert(0, str(path_obj.parents[4]))



def test_compliance_dashboard_streamlit_fallback_logs(caplog, tmp_path, monkeypatch):
    if compliance_dashboard.STREAMLIT_AVAILABLE:
        pytest.skip("Streamlit is installed; fallback not exercised")

    caplog.set_level(logging.INFO)
    caplog.clear()
    monkeypatch.setattr(compliance_dashboard, "LOG_PATH", str(tmp_path / "missing_log.jsonl"))
    monkeypatch.setattr(
        compliance_dashboard,
        "trace_path",
        tmp_path / "missing_trace.csv",
    )

    compliance_dashboard.st.markdown("Λ fallback test")
    records = [record for record in caplog.records if "Streamlit fallback markdown" in record.message]
    assert records, "Expected fallback logging to capture markdown invocation"

    selection = compliance_dashboard.st.multiselect("cols", ["a", "b"], default=["a"])
    assert selection == ["a"]
    assert compliance_dashboard.st.button("trigger") is False
