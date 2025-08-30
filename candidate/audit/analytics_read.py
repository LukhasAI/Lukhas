import json
import os
import time
from pathlib import Path

_BASE = Path(os.getenv("LUKHAS_ANALYTICS_DIR", ".lukhas_analytics"))
_USAGE = _BASE / "tool_usage.jsonl"
_INC = _BASE / "incidents.jsonl"


def _read_jsonl(path: Path, limit: int = 1000) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out[-limit:] if limit else out


def recent_incidents(limit: int = 200) -> list[dict]:
    return list(reversed(_read_jsonl(_INC, limit=limit)))


def recent_tool_usage(limit: int = 200) -> list[dict]:
    return list(reversed(_read_jsonl(_USAGE, limit=limit)))


def summarize_tools(window_s: int = 24 * 3600) -> dict[str, dict]:
    now = time.time()
    rows = [
        r for r in _read_jsonl(_USAGE, limit=5000) if (now - (r.get("ts", now) / 1000)) <= window_s
    ]
    by: dict[str, dict] = {}
    for r in rows:
        name = r.get("tool") or r.get("name") or "unknown"
        bucket = by.setdefault(
            name, {"count": 0, "ok": 0, "error": 0, "p95_ms": None, "durations": []}
        )
        bucket["count"] += 1
        if r.get("status") == "ok":
            bucket["ok"] += 1
        else:
            bucket["error"] += 1
        d = r.get("duration_ms")
        if isinstance(d, (int, float)):
            bucket["durations"].append(d)
    for name, b in by.items():
        if b["durations"]:
            ds = sorted(b["durations"])
            p95_idx = max(0, int(0.95 * len(ds)) - 1)
            b["p95_ms"] = ds[p95_idx]
        del b["durations"]
    return by


def summarize_safety_modes(window_s: int = 24 * 3600) -> dict[str, int]:
    # infer from usage logs and/or incidents; fall back to counts in params snapshot
    now = time.time()
    counts = {"strict": 0, "balanced": 0, "creative": 0}
    for r in _read_jsonl(_USAGE, limit=5000):
        if (now - (r.get("ts", now) / 1000)) > window_s:
            continue
        mode = (r.get("params_snapshot") or {}).get("mode") or r.get("safety_mode") or "balanced"
        mode = str(mode).lower()
        if mode in counts:
            counts[mode] += 1
    return counts
