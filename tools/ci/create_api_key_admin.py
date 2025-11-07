# tools/ci/create_api_key_admin.py
import argparse
import secrets
import sqlite3
from datetime import datetime, timedelta

DB = "reports/todos/intent_registry.db"


def get_conn():
    c = sqlite3.connect(DB)
    return c


def create_key(agent_id, owner=None, expires_days=None, daily_limit=100.0):
    key = secrets.token_urlsafe(32)
    created = datetime.utcnow().isoformat()
    expires_at = (
        (datetime.utcnow() + timedelta(days=expires_days)).isoformat() if expires_days else None
    )
    conn = get_conn()
    conn.execute(
        "INSERT INTO api_keys (key,agent_id,owner,scopes,created_at,expires_at,daily_limit,daily_used) VALUES (?,?,?,?,?,?,?,?)",
        (key, agent_id, owner, "", created, expires_at, daily_limit, 0.0),
    )
    conn.commit()
    conn.close()
    return key


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--agent_id", required=True)
    p.add_argument("--owner", default=None)
    p.add_argument("--expires_days", type=int, default=365)
    p.add_argument("--daily_limit", type=float, default=100.0)
    args = p.parse_args()
    k = create_key(args.agent_id, args.owner, args.expires_days, args.daily_limit)
    print(k)
