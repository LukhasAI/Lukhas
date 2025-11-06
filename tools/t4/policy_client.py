# tools/t4/policy_client.py
from __future__ import annotations

import os
import time

import requests

T4_API = os.environ.get("T4_INTENT_API", "http://127.0.0.1:8001")
T4_KEY = os.environ.get("T4_API_KEY")


def _hdrs():
    h = {"Content-Type": "application/json"}
    if T4_KEY:
        h["X-T4-API-KEY"] = T4_KEY
    return h


def register_intent(payload: dict):
    r = requests.post(f"{T4_API}/intents", headers=_hdrs(), json=payload, timeout=10)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"register_intent failed: {r.status_code} {r.text}")
    return r.json()


def intents_by_file(file: str):
    r = requests.get(f"{T4_API}/intents/by_file?file={file}", headers=_hdrs(), timeout=5)
    if r.status_code != 200:
        return []
    return r.json()


def pre_pr_check(files: list, critical_codes: list = None, auto_create_reserved: bool = True):
    missing = []
    for f in files:
        intents = intents_by_file(f)
        ok = False
        for it in intents:
            if not critical_codes or it.get("code") in critical_codes:  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_t4_policy_client_py_L40"}
                if it.get("status") in ("planned", "committed", "implemented"):
                    ok = True
                    break
        if not ok:
            missing.append(f)
            if auto_create_reserved:
                payload = {
                    "id": f"t4-auto-{int(time.time())}-{abs(hash(f)) % 99999}",
                    "code": (critical_codes[0] if critical_codes else "F821"),
                    "type": "lint",
                    "file": f,
                    "line": 1,
                    "reason": "Auto-registered pre-PR placeholder",
                    "status": "reserved",
                }
                try:
                    register_intent(payload)
                except Exception as e:
                    print(f"Auto-create reserved failed: {e}")
    return missing
