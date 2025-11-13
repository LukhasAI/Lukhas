"""Bridge for `aka_qualia.glyphs`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.aka_qualia.glyphs
  2) candidate.aka_qualia.glyphs
  3) aka_qualia.glyphs

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
__all__: list[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.aka_qualia.glyphs",
    "candidate.aka_qualia.glyphs",
    "aka_qualia.glyphs",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
# No pre-defined stubs

# Add expected symbols as stubs if not found
if "map_scene_to_glyphs" not in globals():

    def map_scene_to_glyphs(scene):
        return []


if "normalize_glyph_keys" not in globals():

    def normalize_glyph_keys(keys):
        return keys
