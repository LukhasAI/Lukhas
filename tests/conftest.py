# conftest.py — drop-in self-healing hooks (no per-test edits needed)
from __future__ import annotations
import os, json, time, hashlib, pathlib, random
from datetime import datetime
import pytest

# Import existing fixtures from labs.tests.conftest
from labs.tests.conftest import *

# Optional libs if present (don't hard error)
try:
    import numpy as np
except Exception:
    np = None
try:
    import torch
except Exception:
    torch = None

REPORTS = pathlib.Path("reports"); REPORTS.mkdir(parents=True, exist_ok=True)
EVENTS = REPORTS / "events.ndjson"

def _signature_hash(error_class: str, nodeid: str, message: str) -> str:
    m = hashlib.sha256()
    m.update((error_class or "Error").encode())
    m.update(b"|")
    m.update(nodeid.encode())
    m.update(b"|")
    m.update((message or "").encode())
    return m.hexdigest()[:16]

def pytest_configure(config):
    # Collect events for Memory Healix
    config._self_heal_events = []
    # Make runs reproducible by default (override via env)
    seed = int(os.environ.get("PYTEST_SEED", "1337"))
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = "0"
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        try:
            torch.manual_seed(seed)
        except Exception:
            pass

@pytest.fixture(autouse=True)
def _freeze_time(monkeypatch):
    """Optional deterministic time. Disable with FREEZE_TIME=0."""
    if os.environ.get("FREEZE_TIME", "1") != "1":
        yield; return
    fixed = 1735689600  # 2025-01-01T00:00:00Z
    start = time.time()
    start_monotonic = time.monotonic()

    def fake_time():
        # preserve monotonic deltas while keeping wall clock stable-ish
        return fixed + (time.monotonic() - start_monotonic)

    monkeypatch.setattr(time, "time", fake_time)
    yield

@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """Block real network during tests unless ALLOW_NET=1."""
    if os.environ.get("ALLOW_NET", "0") == "1":
        yield; return
    import socket
    real_socket = socket.socket

    class GuardedSocket(socket.socket):
        def connect(self, *args, **kwargs):  # noqa: D401
            raise RuntimeError("Network calls are blocked in tests (set ALLOW_NET=1 to override)")

    monkeypatch.setattr(socket, "socket", GuardedSocket)
    yield
    monkeypatch.setattr(socket, "socket", real_socket)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Capture failures for Memory Healix
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return
    if rep.failed:
        nodeid = item.nodeid
        error_class = getattr(rep.longrepr, "reprcrash", None)
        err_type = (error_class and error_class.message.split(":")[0]) or "Failure"
        message = str(rep.longrepr)[:512]
        evt = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "suite": "unit",
            "test_id": nodeid,
            "file": str(getattr(item, "fspath", "")),
            "error_class": err_type,
            "message": message,
            "stack": str(rep.longrepr)[:4000],
            "repro_cmd": f"pytest -q {nodeid}",
            "seed": int(os.environ.get("PYTEST_SEED", "1337")),
            "env": {
                "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", ""),
                "FREEZE_TIME": os.environ.get("FREEZE_TIME", ""),
                "ALLOW_NET": os.environ.get("ALLOW_NET", ""),
            },
            "signature": _signature_hash(err_type, nodeid, message),
        }
        item.config._self_heal_events.append(evt)

def pytest_sessionfinish(session, exitstatus):
    # Write NDJSON events your self-healing loop consumes
    if getattr(session.config, "_self_heal_events", None):
        with open(EVENTS, "a", encoding="utf-8") as w:
            for e in session.config._self_heal_events:
                w.write(json.dumps(e, ensure_ascii=False) + "\n")
