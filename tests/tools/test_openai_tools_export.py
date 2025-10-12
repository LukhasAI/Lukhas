import json, os, pytest
from pathlib import Path

@pytest.mark.skipif(not Path("build/openai_tools.json").exists(), reason="tools export not built yet")
def test_tools_export_shape():
    data = json.loads(Path("build/openai_tools.json").read_text(encoding="utf-8"))
    assert "lukhas.tools" in data and isinstance(data["lukhas.tools"], list)
    if data["lukhas.tools"]:
        t = data["lukhas.tools"][0]
        assert t.get("type") == "function"
        fn = t.get("function", {})
        assert {"name","description","parameters"} <= set(fn.keys())
