#!/usr/bin/env python3
"""
Intent Registry - ingest T4 annotations log into a SQLite DB for queries and reporting.
"""
import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "reports" / "todos" / "unused_imports.jsonl"
DB = REPO / "reports" / "todos" / "intent_registry.db"

def init_db(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS intents (
      id TEXT PRIMARY KEY,
      file TEXT,
      line INTEGER,
      import_text TEXT,
      reason_category TEXT,
      reason TEXT,
      owner TEXT,
      ticket TEXT,
      eta TEXT,
      status TEXT,
      created_at TEXT,
      raw JSON
    )
    """)
    conn.commit()

def normalize_log_obj(obj):
    # Given an older-format log or new structured entry, map to schema
    id_ = obj.get("id") or f"t4-{abs(hash(obj.get('file','') + str(obj.get('line',''))))}"
    return {
        "id": id_,
        "file": obj.get("file"),
        "line": int(obj.get("line") or 0),
        "import_text": obj.get("message"),
        "reason_category": obj.get("reason_category"),
        "reason": obj.get("reason"),
        "owner": obj.get("owner"),
        "ticket": obj.get("ticket"),
        "eta": obj.get("eta"),
        "status": obj.get("status", "reserved"),
        "created_at": obj.get("timestamp") or obj.get("created_at"),
        "raw": json.dumps(obj),
    }

def ingest():
    conn = sqlite3.connect(str(DB))
    init_db(conn)
    if not LOG.exists():
        print("No log found:", LOG)
        return
    inserted = 0
    with LOG.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            row = normalize_log_obj(obj)
            try:
                conn.execute("""
                INSERT OR REPLACE INTO intents (id,file,line,import_text,reason_category,reason,owner,ticket,eta,status,created_at,raw)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    row["id"], row["file"], row["line"], row["import_text"], row["reason_category"], row["reason"],
                    row["owner"], row["ticket"], row["eta"], row["status"], row["created_at"], row["raw"]
                ))
                inserted += 1
            except Exception as e:
                print("DB insert error:", e, row.get("id"))
    conn.commit()
    conn.close()
    print(f"Ingest finished. DB: {DB} (inserted {inserted})")

if __name__ == "__main__":
    ingest()
