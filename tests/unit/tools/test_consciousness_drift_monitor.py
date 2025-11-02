from pathlib import Path


def test_widget_files_exist():
    html_path = Path("tools/dashboards/consciousness_drift_monitor.html")
    js_path = Path("tools/dashboards/consciousness_drift_monitor.js")
    assert html_path.exists()
    assert js_path.exists()

    html = html_path.read_text()
    js = js_path.read_text()

    assert '<div id="affect-delta"' in html
    assert "initializeConsciousnessDriftMonitor" in js
    assert "ΛTAG: affect_delta" in js
