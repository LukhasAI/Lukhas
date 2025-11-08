#!/usr/bin/env python3
"""
T4 Intent Registry API - Metrics and Query Endpoints

Provides REST API for querying Intent Registry SQLite database.

Endpoints:
  GET /metrics/summary - Aggregate metrics (total, by_status, by_code, quality_score)
  GET /intents/stale - List stale intents (planned/committed >30 days old)
  GET /intents/by_owner/{owner} - List intents for specific owner
  GET /intents/{intent_id} - Get single intent details
  POST /intents - Create new intent
  PATCH /intents/{intent_id} - Update intent status/owner/ticket
  DELETE /intents/{intent_id} - Delete intent (requires admin)

Usage:
  uvicorn tools.ci.intent_api:app --reload --port 8001
  curl http://localhost:8001/metrics/summary | jq
"""
from __future__ import annotations

import os
import sqlite3
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Deque, Dict

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "reports" / "todos" / "intent_registry.db"

app = FastAPI(
    title="T4 Intent Registry API",
    description="Query and manage T4 violation intents",
    version="2.0.0"
)

API_KEY_HEADER = APIKeyHeader(name="X-T4-API-KEY", auto_error=False)
DEFAULT_ADMIN_TOKEN = "CHANGE_ME_ADMIN_TOKEN"
ADMIN_TOKEN = os.environ.get("T4_ADMIN_TOKEN", DEFAULT_ADMIN_TOKEN)
RATE_LIMIT_PER_MIN = int(os.environ.get("T4_INTENT_RATE_LIMIT_PER_MIN", "120"))
ALLOWED_API_KEYS = {
    key.strip() for key in os.environ.get("T4_INTENT_ALLOWED_KEYS", "").split(",") if key.strip()
}
_rate_state: Dict[str, Deque[float]] = defaultdict(deque)
_rate_lock = Lock()


def _is_valid_api_key(x_api_key: str) -> bool:
    """Return whether the supplied API key is authorized."""
    if ALLOWED_API_KEYS:
        return x_api_key in ALLOWED_API_KEYS

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT 1 FROM api_keys WHERE key = ? AND revoked = 0",
            (x_api_key,),
        )
        return cursor.fetchone() is not None
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=503, detail="API key store not initialized") from exc
    finally:
        conn.close()


def _enforce_rate_limit(x_api_key: str) -> None:
    if RATE_LIMIT_PER_MIN <= 0:
        return

    now = time.time()
    with _rate_lock:
        dq = _rate_state[x_api_key]
        cutoff = now - 60

        while dq and dq[0] < cutoff:
            dq.popleft()

        dq.append(now)

        if len(dq) > RATE_LIMIT_PER_MIN:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")


def require_api_key(x_api_key: str = Depends(API_KEY_HEADER)) -> str:
    """Validate the caller's API key and apply per-minute rate limiting."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-T4-API-KEY header")

    if not _is_valid_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid or revoked API key")

    _enforce_rate_limit(x_api_key)
    return x_api_key


# Models
class Intent(BaseModel):
    id: str = Field(..., description="UUID for intent")
    code: str = Field(..., description="Lint code (F401, F821, etc.)")
    type: str = Field(..., description="Type: 'lint' or 'import'")
    file: str = Field(..., description="File path relative to repo root")
    line: int = Field(..., description="Line number")
    reason: str = Field(..., description="Human-readable justification")
    reason_category: str | None = Field(None, description="Category: MATRIZ, CONSTELLATION, etc.")
    status: str = Field(..., description="Status: documented, planned, committed")
    owner: str | None = Field(None, description="GitHub username")
    ticket: str | None = Field(None, description="GitHub issue/PR URL")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str | None = Field(None, description="ISO 8601 timestamp")


class IntentUpdate(BaseModel):
    status: str | None = None
    owner: str | None = None
    ticket: str | None = None
    reason: str | None = None


class MetricsSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_code: dict[str, int]
    quality_score: float
    avg_time_to_resolve: float | None


# Database helpers
def get_db_connection():
    """Get SQLite connection."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Intent Registry DB not initialized")

    return sqlite3.connect(DB_PATH)


def dict_from_row(row: tuple, columns: list[str]) -> dict:
    """Convert SQLite row to dict."""
    return dict(zip(columns, row))


# Endpoints
@app.get("/metrics/summary", response_model=MetricsSummary)
def get_metrics_summary(api_key: str = Depends(require_api_key)):
    """
    Get aggregate metrics for all intents.

    Returns:
      - total: Total intents
      - by_status: Count grouped by status
      - by_code: Count grouped by lint code
      - quality_score: Weighted quality score
      - avg_time_to_resolve: Average days from created to resolved
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total
    cursor.execute("SELECT COUNT(*) FROM intents")
    total = cursor.fetchone()[0]

    # By status
    cursor.execute("SELECT status, COUNT(*) FROM intents GROUP BY status")
    by_status = {row[0]: row[1] for row in cursor.fetchall()}

    # By code
    cursor.execute("SELECT code, COUNT(*) FROM intents GROUP BY code")
    by_code = {row[0]: row[1] for row in cursor.fetchall()}

    # Quality score (weighted)
    cursor.execute("SELECT code, status, owner, ticket FROM intents")
    rows = cursor.fetchall()

    severity_weights = {
        "F821": 3,
        "F401": 3,
        "B904": 2,
        "B008": 2,
        "RUF006": 2,
        "SIM102": 1,
        "SIM105": 1,
        "E702": 1,
        "B018": 1,
    }

    weighted_total = 0
    weighted_good = 0

    for code, status, owner, ticket in rows:
        weight = severity_weights.get(code, 1)
        weighted_total += weight

        if status not in ("planned", "committed") or (owner and ticket):
            weighted_good += weight

    quality_score = 100.0 * weighted_good / weighted_total if weighted_total > 0 else 100.0

    # Avg time to resolve
    cursor.execute("""
        SELECT AVG(JULIANDAY(updated_at) - JULIANDAY(created_at))
        FROM intents
        WHERE status = 'resolved' AND updated_at IS NOT NULL
    """)
    avg_days = cursor.fetchone()[0]

    conn.close()

    return MetricsSummary(
        total=total,
        by_status=by_status,
        by_code=by_code,
        quality_score=round(quality_score, 2),
        avg_time_to_resolve=round(avg_days, 2) if avg_days else None
    )


@app.get("/intents/stale", response_model=list[Intent])
def get_stale_intents(days: int = 30, api_key: str = Depends(require_api_key)):
    """
    List intents with status=planned or committed that are older than `days`.

    Args:
      days: Age threshold (default: 30)

    Returns:
      List of stale intents
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM intents
        WHERE status IN ('planned', 'committed')
          AND created_at < ?
        ORDER BY created_at ASC
    """, (cutoff_str,))

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    return [Intent(**dict_from_row(row, columns)) for row in rows]


@app.get("/intents/by_owner/{owner}", response_model=list[Intent])
def get_intents_by_owner(owner: str, api_key: str = Depends(require_api_key)):
    """
    List all intents assigned to specific owner.

    Args:
      owner: GitHub username

    Returns:
      List of intents
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM intents WHERE owner = ? ORDER BY created_at DESC", (owner,))

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()

    return [Intent(**dict_from_row(row, columns)) for row in rows]


@app.get("/intents/{intent_id}", response_model=Intent)
def get_intent(intent_id: str, api_key: str = Depends(require_api_key)):
    """
    Get single intent by ID.

    Args:
      intent_id: UUID

    Returns:
      Intent details
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM intents WHERE id = ?", (intent_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Intent {intent_id} not found")

    columns = [desc[0] for desc in cursor.description]
    conn.close()

    return Intent(**dict_from_row(row, columns))


@app.post("/intents", response_model=Intent, status_code=201)
def create_intent(intent: Intent, api_key: str = Depends(require_api_key)):
    """
    Create new intent in registry.

    Args:
      intent: Intent object

    Returns:
      Created intent
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO intents (id, code, type, file, line, reason, reason_category, status, owner, ticket, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        intent.id, intent.code, intent.type, intent.file, intent.line,
        intent.reason, intent.reason_category, intent.status,
        intent.owner, intent.ticket, now, None
    ))

    conn.commit()
    conn.close()

    return intent


@app.patch("/intents/{intent_id}", response_model=Intent)
def update_intent(intent_id: str, update: IntentUpdate, api_key: str = Depends(require_api_key)):
    """
    Update intent fields (status, owner, ticket, reason).

    Args:
      intent_id: UUID
      update: Fields to update

    Returns:
      Updated intent
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check exists
    cursor.execute("SELECT * FROM intents WHERE id = ?", (intent_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Intent {intent_id} not found")

    # Build update query
    fields = []
    values = []

    if update.status is not None:
        fields.append("status = ?")
        values.append(update.status)

    if update.owner is not None:
        fields.append("owner = ?")
        values.append(update.owner)

    if update.ticket is not None:
        fields.append("ticket = ?")
        values.append(update.ticket)

    if update.reason is not None:
        fields.append("reason = ?")
        values.append(update.reason)

    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    fields.append("updated_at = ?")
    values.append(datetime.now(timezone.utc).isoformat())

    values.append(intent_id)

    cursor.execute(f"UPDATE intents SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()

    # Fetch updated
    cursor.execute("SELECT * FROM intents WHERE id = ?", (intent_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    return Intent(**dict_from_row(row, columns))


@app.delete("/intents/{intent_id}", status_code=204)
def delete_intent(
    intent_id: str,
    api_key: str = Depends(require_api_key),
    admin_token: str | None = Header(default=None, alias="X-T4-ADMIN-TOKEN"),
):
    """
    Delete intent from registry (admin only).

    Args:
      intent_id: UUID

    Returns:
      204 No Content
    """
    if ADMIN_TOKEN == DEFAULT_ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="Admin token not configured")

    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin token required")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM intents WHERE id = ?", (intent_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Intent {intent_id} not found")

    conn.commit()
    conn.close()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "database": "connected" if DB_PATH.exists() else "missing"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
