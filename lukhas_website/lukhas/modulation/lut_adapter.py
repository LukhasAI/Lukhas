from typing import Any

from feedback.store import get_lut


def apply_lut(params: dict[str, Any]) -> dict[str, Any]:
    """Apply bounded style nudges from lut_to modulated params.
    Safety invariants: does not relax safety_mode or exceed core bounds.
    """
    lut = get_lut()
    style = (lut or {}).get("style", {})
    out = dict(params)
    out["temperature"] = float(out.get("temperature", 0.6)) + float(style.get("temperature_delta", 0.0))
    out["top_p"] = float(out.get("top_p", 0.9)) + float(style.get("top_p_delta", 0.0))
    out["memory_write"] = float(out.get("memory_write", 0.4)) + float(style.get("memory_write_boost", 0.0))

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    out["temperature"] = clamp(out["temperature"], 0.0, 1.0)
    out["top_p"] = clamp(out["top_p"], 0.1, 1.0)
    out["memory_write"] = clamp(out["memory_write"], 0.1, 1.0)
    return out
