import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import streamlit as st
from fastapi import APIRouter

router = APIRouter(prefix="/ops/backup", tags=["ops", "backup"])


def _last_success_path() -> Path:
    p = Path(os.getenv("LUKHAS_BACKUP_STATE", ".lukhas_backup")) / "last_success.json"
    return p


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


@router.get("/health")
def backup_health() -> dict:
    last = _read_json(_last_success_path())
    now = datetime.now(timezone.utc).isoformat()
    status = {
        "now_utc": now,
        "last_success": last,
        "ok": bool(last),
    }
    # Optional freshness check: flag via env minutes
    try:
        max_age_min = int(os.getenv("BACKUP_MAX_AGE_MINUTES", "0"))
    except ValueError:
        max_age_min = 0
    if last and max_age_min > 0:
        try:
            ts = last.get("timestamp_utc") or last.get("timestamp")
            if ts:
                from datetime import datetime as dt

                t = dt.fromisoformat(ts.replace("Z", "+00:00"))
                age_min = (datetime.now(timezone.utc) - t).total_seconds() / 60.0
                status["fresh"] = age_min <= max_age_min
                status["age_minutes"] = round(age_min, 2)
                status["max_age_minutes"] = max_age_min
        except Exception:
            status["fresh"] = False
    return status
