# tools/ci/intent_api.py
from __future__ import annotations
import os
import json
import sqlite3
import time
import secrets
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

APP = FastAPI(title="T4 Intent API", version="2.0")
REPO = Path(__file__).resolve().parents[2]
DB = REPO / "reports" / "todos" / "intent_registry.db"
DB.parent.mkdir(parents=True, exist_ok=True)

API_KEY_HEADER = APIKeyHeader(name="X-T4-API-KEY", auto_error=False)
ADMIN_TOKEN = os.environ.get("T4_ADMIN_TOKEN", "CHANGE_ME_ADMIN_TOKEN")
REDIS_URL = os.environ.get("T4_RATE_REDIS")

# --- DB helpers ---
def get_conn():
    conn = sqlite3.connect(str(DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS intents (
      id TEXT PRIMARY KEY,
      code TEXT,
      type TEXT,
      file TEXT,
      line INTEGER,
      import_text TEXT,
      reason_category TEXT,
      reason TEXT,
      suggestion TEXT,
      owner TEXT,
      ticket TEXT,
      eta TEXT,
      status TEXT,
      created_at TEXT,
      modified_at TEXT,
      resolved_at TEXT,
      raw JSON
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
      key TEXT PRIMARY KEY,
      agent_id TEXT,
      owner TEXT,
      scopes TEXT,
      created_at TEXT,
      expires_at TEXT,
      revoked INTEGER DEFAULT 0,
      daily_limit REAL DEFAULT 100.0,
      daily_used REAL DEFAULT 0.0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT,
      api_key TEXT,
      agent_id TEXT,
      path TEXT,
      method TEXT,
      status_code INTEGER,
      ip TEXT,
      body JSON
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS llm_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT,
      api_key TEXT,
      agent_id TEXT,
      model TEXT,
      prompt_tokens INTEGER,
      completion_tokens INTEGER,
      est_cost REAL
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_status ON intents(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_owner ON intents(owner)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_code ON intents(code)")
    conn.commit()
    conn.close()

init_db()

# --- Rate limiting: Redis if available, otherwise in-process fallback ---
USE_REDIS = False
try:
    if REDIS_URL:
        import aioredis
        USE_REDIS = True
        _redis = None
        async def get_redis():
            global _redis
            if _redis is None:
                _redis = await aioredis.from_url(REDIS_URL)
            return _redis
        async def incr_rate(key, window=60):
            r = await get_redis()
            v = await r.incr(key)
            if v == 1:
                await r.expire(key, window)
            return v
    else:
        raise Exception("REDIS not configured")
except Exception:
    from collections import defaultdict, deque
    RATE_STATE = defaultdict(deque)
    def incr_rate_sync(key, window=60):
        now = time.time()
        dq = RATE_STATE[key]
        while dq and dq[0] < now - window:
            dq.popleft()
        dq.append(now)
        return len(dq)

# --- Auth & audit helpers ---
def lookup_api_key(key: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.execute("SELECT * FROM api_keys WHERE key=? AND revoked=0", (key,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def audit_insert(api_key, agent_id, path, method, status_code, ip, body):
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO audit_log (timestamp,api_key,agent_id,path,method,status_code,ip,body) VALUES (?,?,?,?,?,?,?,?)",
            (datetime.utcnow().isoformat(), api_key, agent_id, path, method, status_code, ip, json.dumps(body) if body else None)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

async def require_api_key(request: Request, x_api_key: str = Depends(API_KEY_HEADER)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-T4-API-KEY")
    keyinfo = lookup_api_key(x_api_key)
    if not keyinfo:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key")
    if keyinfo.get("expires_at"):
        try:
            exp = datetime.fromisoformat(keyinfo["expires_at"])
            if exp < datetime.utcnow():
                raise HTTPException(status_code=403, detail="API key expired")
        except Exception:
            pass
    rl_key = f"t4_rl:{x_api_key}:{int(time.time()//60)}"
    try:
        if USE_REDIS:
            cnt = await incr_rate(rl_key, window=60)
        else:
            cnt = incr_rate_sync(rl_key, window=60)
    except Exception:
        cnt = 0
    max_per_min = 120
    if cnt and cnt > max_per_min:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    request.state.t4_api_key = x_api_key
    request.state.t4_agent_id = keyinfo.get("agent_id")
    request.state.t4_owner = keyinfo.get("owner")
    return keyinfo

@APP.middleware("http")
async def audit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    body = None
    try:
        if request.method in ("POST","PATCH","PUT"):
            try:
                body = await request.json()
            except Exception:
                body = None
    except Exception:
        body = None
    api_key = request.headers.get("X-T4-API-KEY")
    agent_id = None
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        try:
            agent_id = getattr(request.state, "t4_agent_id", None)
            audit_insert(api_key, agent_id, str(request.url), request.method, status_code, ip, body)
        except Exception:
            pass
    return response

# --- Pydantic models ---
class IntentIn(BaseModel):
    id: str = Field(..., example="T4-abc123")
    code: str
    type: Optional[str] = "lint"
    file: Optional[str]
    line: Optional[int]
    import_text: Optional[str]
    reason_category: Optional[str]
    reason: Optional[str]
    suggestion: Optional[str]
    owner: Optional[str]
    ticket: Optional[str]
    eta: Optional[str]
    status: Optional[str] = "reserved"
    created_at: Optional[str] = None
    raw: Optional[Dict] = None

class AdminCreateKey(BaseModel):
    agent_id: str
    owner: Optional[str] = None
    scopes: Optional[str] = None
    expires_in_days: Optional[int] = None
    daily_limit: Optional[float] = 100.0

# --- DB helpers ---
def insert_intent(data: dict):
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    data.setdefault("created_at", now)
    data.setdefault("modified_at", now)
    conn.execute("""
      INSERT OR REPLACE INTO intents (id,code,type,file,line,import_text,reason_category,reason,suggestion,owner,ticket,eta,status,created_at,modified_at,raw)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("id"), data.get("code"), data.get("type"), data.get("file"), data.get("line"),
        data.get("import_text"), data.get("reason_category"), data.get("reason"), data.get("suggestion"),
        data.get("owner"), data.get("ticket"), data.get("eta"), data.get("status"),
        data.get("created_at"), data.get("modified_at"), json.dumps(data.get("raw") or {})
    ))
    conn.commit()
    conn.close()

# --- Endpoints ---
@APP.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@APP.post("/intents")
async def create_intent(intent: IntentIn, keyinfo: dict = Depends(require_api_key)):
    data = intent.dict()
    if not data.get("created_at"):
        data["created_at"] = datetime.utcnow().isoformat()
    data["modified_at"] = data["created_at"]
    insert_intent(data)
    return {"status":"ok", "intent": data}

@APP.get("/intents/stale")
async def get_stale(days: int = 30, keyinfo: dict = Depends(require_api_key)):
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    conn = get_conn()
    rows = conn.execute("SELECT * FROM intents WHERE status IN ('reserved','planned','committed') AND modified_at < ? ORDER BY modified_at ASC", (cutoff,)).fetchall()
    out = [dict(r) for r in rows]
    conn.close()
    return out

@APP.get("/intents/by_owner/{owner}")
async def intents_by_owner(owner: str, keyinfo: dict = Depends(require_api_key)):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM intents WHERE owner=? ORDER BY modified_at DESC", (owner,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@APP.get("/intents/by_file")
async def intents_by_file(file: str, keyinfo: dict = Depends(require_api_key)):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM intents WHERE file=? ORDER BY line ASC", (file,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@APP.get("/intents/{intent_id}")
async def get_intent(intent_id: str, keyinfo: dict = Depends(require_api_key)):
    conn = get_conn()
    row = conn.execute("SELECT * FROM intents WHERE id=?", (intent_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Intent not found")
    return dict(row)

@APP.patch("/intents/{intent_id}")
async def patch_intent(intent_id: str, patch: dict, keyinfo: dict = Depends(require_api_key)):
    conn = get_conn()
    fields = []
    vals = []
    for k,v in patch.items():
        if k in ("owner","ticket","status","reason","eta","modified_at"):
            fields.append(f"{k}=?")
            vals.append(v)
    vals.append(intent_id)
    if fields:
        q = f"UPDATE intents SET {','.join(fields)}, modified_at=? WHERE id=?"
        vals.insert(-1, datetime.utcnow().isoformat())
        conn.execute(q, tuple(vals))
        conn.commit()
    conn.close()
    return {"status":"ok"}

@APP.delete("/intents/{intent_id}")
async def delete_intent(intent_id: str, admin_token: Optional[str] = None):
    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin token required")
    conn = get_conn()
    conn.execute("DELETE FROM intents WHERE id=?", (intent_id,))
    conn.commit()
    conn.close()
    return {"status":"deleted"}

@APP.get("/metrics/summary")
async def metrics_summary(keyinfo: dict = Depends(require_api_key)):
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM intents").fetchone()[0]
    by_status_rows = conn.execute("SELECT status, COUNT(*) as cnt FROM intents GROUP BY status").fetchall()
    by_status = {r["status"]: r["cnt"] for r in by_status_rows}
    by_code_rows = conn.execute("SELECT code, COUNT(*) as cnt FROM intents GROUP BY code ORDER BY cnt DESC LIMIT 20").fetchall()
    by_code = {r["code"]: r["cnt"] for r in by_code_rows}
    qc_rows = conn.execute("SELECT status, code, owner, ticket FROM intents").fetchall()
    total_relevant = 0
    good = 0
    for r in qc_rows:
        if r["status"] in ("planned","committed"):
            total_relevant += 1
            if r["owner"] and r["ticket"]:
                good += 1
    quality_score = (good/total_relevant*100.0) if total_relevant else 100.0
    avg_resolved = conn.execute("SELECT AVG(julianday(resolved_at)-julianday(created_at)) FROM intents WHERE resolved_at IS NOT NULL").fetchone()[0]
    conn.close()
    return {
        "total": total,
        "by_status": by_status,
        "by_code": by_code,
        "quality_score": quality_score,
        "avg_time_to_resolve_days": float(avg_resolved) if avg_resolved else None
    }

# --- Admin: API key management ---
def require_admin_token(token: Optional[str]):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")

@APP.post("/admin/api_keys")
def admin_create_key(payload: AdminCreateKey, admin_token: Optional[str] = None):
    require_admin_token(admin_token)
    key = secrets.token_urlsafe(32)
    agent_id = payload.agent_id
    owner = payload.owner
    scopes = payload.scopes
    created = datetime.utcnow().isoformat()
    expires_at = None
    if payload.expires_in_days:
        expires_at = (datetime.utcnow() + timedelta(days=payload.expires_in_days)).isoformat()
    conn = get_conn()
    conn.execute("INSERT INTO api_keys (key,agent_id,owner,scopes,created_at,expires_at,daily_limit,daily_used) VALUES (?,?,?,?,?,?,?,?)",
                 (key, agent_id, owner, scopes, created, expires_at, payload.daily_limit or 100.0, 0.0))
    conn.commit()
    conn.close()
    return {"key": key, "agent_id": agent_id, "owner": owner, "expires_at": expires_at}

@APP.delete("/admin/api_keys/{key}")
def admin_revoke_key(key: str, admin_token: Optional[str] = None):
    require_admin_token(admin_token)
    conn = get_conn()
    conn.execute("UPDATE api_keys SET revoked=1 WHERE key=?", (key,))
    conn.commit(); conn.close()
    return {"revoked": True}

@APP.get("/admin/api_keys")
def admin_list_keys(admin_token: Optional[str] = None):
    require_admin_token(admin_token)
    conn = get_conn()
    rows = conn.execute("SELECT key,agent_id,owner,scopes,created_at,expires_at,revoked,daily_limit,daily_used FROM api_keys").fetchall()
    conn.close()
    return [dict(r) for r in rows]
