import base64
import importlib.util
import json
import sys
import types
import zlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

dummy_memory = types.ModuleType("lukhas.memory.glyph_memory_integration")


class DummyBridge:
    def process_dream_state(self, dream_data, activate_glyphs=True):
        return {
            "processed_memories": 1,
            "activated_glyphs": dream_data.get("glyphs", []),
            "new_associations": 0,
            "folded_memories": [],
        }


class DummySystem:
    def __init__(self):
        self.glyph_index = type(
            "GlyphIndex",
            (),
            {"glyph_to_folds": {"💡": {"fold1", "fold2"}}},
        )()
        self.dream_bridge = DummyBridge()


def get_system():
    return DummySystem()


dummy_memory.get_glyph_memory_system = get_system
sys.modules["lukhas.memory.glyph_memory_integration"] = dummy_memory

glyph_mod = types.ModuleType("lukhas.features.symbolic.glyphs")
glyph_mod.GLYPH_MAP = {"💡": "Insight"}
sys.modules["lukhas.features.symbolic.glyphs"] = glyph_mod

SPEC = importlib.util.spec_from_file_location(
    "glyph_exchange", Path("lukhas/api/glyph_exchange.py")
)
gx = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gx)  # type: ignore
router = gx.router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_export_endpoint():
    resp = client.get("/glyph/export")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data[0]["glyph"] == "💡"


def test_import_endpoint():
    payload = {"glyphs": [{"glyph": "🧠", "meaning": "Mind"}], "user_id": "tester"}
    resp = client.post("/glyph/import", json=payload)
    assert resp.status_code == 200
    assert "🧠" in resp.json()["data"]["imported"]


def test_compressed_tags_endpoint():
    dream_data = {"emotion": "joy", "content": "test", "glyphs": ["💡"]}
    packed = zlib.compress(json.dumps(dream_data).encode())
    payload = {
        "compressed_data": base64.b64encode(packed).decode(),
        "activate_glyphs": True,
    }
    resp = client.post("/glyph/dream-tags", json=payload)
    assert resp.status_code == 200
    assert resp.json()["data"]["activated_glyphs"] == ["💡"]
