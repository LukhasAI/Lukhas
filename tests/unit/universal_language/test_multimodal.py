import importlib.util
from pathlib import Path


def _load_module(module_name: str, rel_path: str):
    root = Path(__file__).resolve().parents[3]  # Go up to repo root
    file_path = root / rel_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


mm = _load_module("ul_multimodal", "products/experience/universal_language/core/multimodal.py")
ModalityProcessor = mm.ModalityProcessor
ModalityType = mm.ModalityType


def test_process_color_hex_parsing():
    mp = ModalityProcessor()
    mf = mp.process("#1a2b3c", ModalityType.COLOR)
    assert mf.metadata["rgb"] == (26, 43, 60)
    h, s, v = mf.metadata["hsv"]
    assert 0 <= h <= 360
    assert 0 <= s <= 1 and 0 <= v <= 1


def test_process_color_tuple_rgb():
    mp = ModalityProcessor()
    mf = mp.process((255, 0, 128), ModalityType.COLOR)
    assert mf.metadata["rgb"] == (255, 0, 128)
    assert "luminance" in mf.metadata
