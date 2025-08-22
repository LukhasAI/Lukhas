import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Header, HTTPException, Query

router = APIRouter(prefix="/ops/perf", tags=["Perf"])

_BASE = Path(os.getenv("LUKHAS_PERF_DIR", ".lukhas_perf"))
_BASE.mkdir(parents=True, exist_ok=True)
_SERIES = _BASE / "k6_series.jsonl"  # 1 JSON per line


def _require_enabled(x_api_key: Optional[str]):
    """Check if perf ingestion is enabled and API key is valid."""
    # Check feature flag
    try:
        from lukhas.flags import get_flags

        if not Flags.get("OPS_PERF_INGEST", default=False):
            raise HTTPException(status_code=404, detail="Perf ingest disabled")
    except ImportError:
        # Fallback to env var if flags module not available
        if not os.getenv("FLAG_OPS_PERF_INGEST", "").lower() == "true":
            raise HTTPException(status_code=404, detail="Perf ingest disabled")

    # Check API key
    req = os.getenv("LUKHAS_API_KEY", "")
    if req and x_api_key != req:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/k6")
def ingest_k6_summary(
    payload: Dict[str, Any] = Body(...), x_api_key: Optional[str] = Header(default=None)
):
    """Ingests k6 summary.json (or a subset). Stores p95 per endpoint with timestamp."""
    _require_enabled(x_api_key)
    ts = int(time.time() * 1000)

    # Extract p95s by endpoint tag
    metrics = payload.get("metrics", {})
    p95 = {}
    for k, v in metrics.items():
        if not k.startswith("http_req_duration{endpoint:"):
            continue
        name = k.split("{endpoint:")[-1].rstrip("}")
        val = (v.get("values") or {}).get("p(95)")
        if isinstance(val, (int, float)):
            p95[name] = float(val)

    row = {"ts": ts, "p95": p95}
    with _SERIES.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")

    return {"ok": True, "saved": True, "points": len(p95)}


@router.get("/series")
def series(
    endpoint: str = Query(..., description="endpoint key e.g. health|tools|openapi"),
    hours: int = Query(24, ge=1, le=24 * 30),
):
    """Returns recent (ts, p95_ms) for the requested endpoint."""
    now = int(time.time() * 1000)
    window_ms = hours * 3600 * 1000
    out: List[Dict[str, Any]] = []

    if not _SERIES.exists():
        return {"points": out}

    for line in _SERIES.open("r", encoding="utf-8"):
        try:
            row = json.loads(line)
            ts = int(row.get("ts", 0))
            if now - ts > window_ms:
                continue
            v = (row.get("p95") or {}).get(endpoint)
            if isinstance(v, (int, float)):
                out.append({"ts": ts, "p95": float(v)})
        except Exception:
            continue

    out.sort(key=lambda r: r["ts"])
    return {"points": out}
