---
status: wip
type: documentation
owner: unknown
module: gonzo
redirect: false
moved_to: null
---

⸻

M.1 — Memory Storage/Retrieval

lukhas/memory/backends/pgvector_store.py

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

# TODO: replace with real DB client (psycopg or sqlalchemy)
class _PgClient: ...

@dataclass(frozen=True)
class VectorDoc:
    id: str
    text: str
    embedding: List[float]
    meta: Dict[str, Any]

class PgVectorStore:
    """Minimal pgvector-backed store (scaffold).
    API is intentionally simple for mocking & tests.
    """
    def __init__(self, conn: _PgClient, table="mem_store", dim: int = 1536):
        self.conn = conn
        self.table = table
        self.dim = dim

    def add(self, doc: VectorDoc) -> str:
        """Insert one doc. TODO: upsert on id, return id."""
        # TODO: SQL: INSERT ... ON CONFLICT (id) DO UPDATE
        raise NotImplementedError("implement add()")

    def bulk_add(self, docs: Iterable[VectorDoc]) -> List[str]:
        """Bulk insert. TODO: chunked COPY for perf."""
        raise NotImplementedError("implement bulk_add()")

    def search(self, embedding: List[float], k: int = 10,
               filters: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float]]:
        """Return [(id, score)] by cosine distance. TODO: apply filters."""
        raise NotImplementedError("implement search()")

    def delete(self, *, id: Optional[str] = None, where: Optional[Dict[str, Any]] = None) -> int:
        """Delete by id or filter. Return rows affected."""
        raise NotImplementedError("implement delete()")

    def stats(self) -> Dict[str, Any]:
        """Return {count, table, dim}."""
        return {"table": self.table, "dim": self.dim, "count": None}  # TODO: SELECT COUNT(*)

lukhas/memory/indexer.py

from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Optional
from .backends.pgvector_store import PgVectorStore, VectorDoc

# TODO: plug in actual embedding providers
class Embeddings:
    def embed(self, text: str) -> List[float]:
        # TODO: call provider, cache results
        return [0.0] * 1536  # placeholder

def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

class Indexer:
    def __init__(self, store: PgVectorStore, emb: Optional[Embeddings] = None):
        self.store = store
        self.emb = emb or Embeddings()

    def upsert(self, text: str, meta: Dict[str, Any]) -> str:
        fp = _fingerprint(text)
        vec = self.emb.embed(text)
        # TODO: detect duplicates by fp in meta
        return self.store.add(VectorDoc(id=fp, text=text, embedding=vec, meta=meta))

    def search_text(self, query: str, k: int = 10, filters: Optional[Dict[str, Any]] = None):
        vec = self.emb.embed(query)
        return self.store.search(vec, k=k, filters=filters)

lukhas/memory/lifecycle.py

from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass
class RetentionPolicy:
    days: int = 30

class Lifecycle:
    def __init__(self, retention: RetentionPolicy):
        self.retention = retention

    def enforce_retention(self) -> int:
        """Delete/Archive docs older than policy. Return count.
        TODO: implement archive -> ./archive/ + tombstones + audit log
        """
        raise NotImplementedError

lukhas/memory/memory_orchestrator.py

from __future__ import annotations
from typing import Any, Dict, List
from .indexer import Indexer

class MemoryOrchestrator:
    """Public facade API kept stable for callers."""
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def add_event(self, text: str, meta: Dict[str, Any]) -> str:
        # TODO: add Prometheus histograms timers externally
        return self.indexer.upsert(text, meta)

    def query(self, text: str, k: int = 8, filters: Dict[str, Any] | None = None):
        return self.indexer.search_text(text, k=k, filters=filters)

Tests

tests/memory/test_storage_e2e.py

import time
import pytest
from lukhas.memory.memory_orchestrator import MemoryOrchestrator
from lukhas.memory.indexer import Indexer
from lukhas.memory.backends.pgvector_store import PgVectorStore

class DummyConn: ...  # TODO: mock/fixture

@pytest.fixture
def orch():
    store = PgVectorStore(DummyConn(), dim=8)  # small dim for tests
    return MemoryOrchestrator(Indexer(store))

def test_upsert_and_query_roundtrip(orch):
    doc_id = orch.add_event("hello world", {"lane": "candidate"})
    assert isinstance(doc_id, str)
    res = orch.query("hello", k=3)
    assert isinstance(res, list)

@pytest.mark.e2e_perf
def test_search_p95_under_100ms(orch):
    # TODO: create N docs first
    lat = []
    for _ in range(200):
        t0 = time.perf_counter_ns()
        orch.query("hello", k=5)
        lat.append(time.perf_counter_ns() - t0)
    lat.sort()
    p95 = lat[int(0.95 * len(lat))] / 1_000_000
    assert p95 < 100.0


⸻

C.1 — Core Consciousness Components

lukhas/consciousness/types.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

StatePhase = Literal["IDLE","AWARE","REFLECT","DREAM"]

@dataclass
class ConsciousnessState:
    phase: StatePhase = "IDLE"
    ts_ms: int = 0
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReflectionReport:
    schema_version: str = "1.0"
    coherence_score: float = 0.0
    drift_ema: float = 0.0
    anomalies: List[str] = field(default_factory=list)

lukhas/consciousness/awareness_engine.py

from __future__ import annotations
from .types import ConsciousnessState

class AwarenessEngine:
    def update(self, state: ConsciousnessState, signals: dict) -> dict:
        """Return snapshot with drift EMA, load, anomalies (scaffold)."""
        # TODO: compute EMA, anomalies
        return {"drift_ema": 0.0, "anomalies": []}

lukhas/consciousness/reflection_engine.py

from __future__ import annotations
import time
from .types import ConsciousnessState, ReflectionReport

class ReflectionEngine:
    def reflect(self, state: ConsciousnessState) -> ReflectionReport:
        # TODO: real meta-cognition; for now return neutral report fast
        _ = state
        return ReflectionReport(coherence_score=1.0, drift_ema=0.0, anomalies=[])

lukhas/consciousness/dream_engine.py

from __future__ import annotations
from typing import Literal

Phase = Literal["IDLE","ENTERING","DREAMING","EXITING"]

class DreamEngine:
    def __init__(self) -> None:
        self.phase: Phase = "IDLE"

    def enter(self, reason: str, context: dict) -> None:
        assert self.phase in ("IDLE","EXITING")
        self.phase = "ENTERING"

    def step(self, max_time_ms: int = 50) -> None:
        assert self.phase in ("ENTERING","DREAMING")
        self.phase = "DREAMING"
        # TODO: consolidate memory, emit dream trace

    def exit(self) -> None:
        assert self.phase in ("DREAMING","ENTERING")
        self.phase = "EXITING"
        # TODO: flush artifacts, return to IDLE
        self.phase = "IDLE"

lukhas/consciousness/auto_consciousness.py

from __future__ import annotations
from .types import ConsciousnessState
from .awareness_engine import AwarenessEngine
from .reflection_engine import ReflectionEngine
from .dream_engine import DreamEngine

class AutoConsciousness:
    def __init__(self, guardian=None):
        self.awareness = AwarenessEngine()
        self.reflection = ReflectionEngine()
        self.dream = DreamEngine()
        self.guardian = guardian

    async def tick(self, state: ConsciousnessState, signals: dict) -> ConsciousnessState:
        snapshot = self.awareness.update(state, signals)
        report = self.reflection.reflect(state)
        # TODO: decide action; call guardian.validate_action_async
        return state

Tests

tests/consciousness/test_engines_contract.py

from lukhas.consciousness.types import ConsciousnessState
from lukhas.consciousness.awareness_engine import AwarenessEngine
from lukhas.consciousness.reflection_engine import ReflectionEngine
from lukhas.consciousness.dream_engine import DreamEngine

def test_awareness_contract():
    s = ConsciousnessState()
    out = AwarenessEngine().update(s, {"signal": 1})
    assert "drift_ema" in out

def test_reflection_contract():
    s = ConsciousnessState()
    r = ReflectionEngine().reflect(s)
    assert r.schema_version == "1.0"

def test_dream_fsm():
    d = DreamEngine()
    d.enter("test", {})
    d.step()
    assert d.phase == "DREAMING"
    d.exit()
    assert d.phase == "IDLE"


⸻

I.1 — ΛiD Token Generation & Validation

lukhas/identity/alias_format.py

from __future__ import annotations
import uuid, zlib

def make_alias(realm: str, zone: str, major: int = 1) -> str:
    core = f"lid#{realm}/{zone}/v{major}.{uuid.uuid4().hex}"
    crc = zlib.crc32(core.encode("utf-8")) & 0xffffffff
    return f"{core}-{crc:08x}"

def verify_crc(alias: str) -> bool:
    try:
        body, crc_hex = alias.rsplit("-", 1)
        return (zlib.crc32(body.encode("utf-8")) & 0xffffffff) == int(crc_hex, 16)
    except Exception:
        return False

lukhas/identity/token_generator.py

from __future__ import annotations
import hmac, hashlib, base64, json, time
from typing import Dict, Any
from .alias_format import make_alias

def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

class TokenGenerator:
    def __init__(self, secret_provider, kid: str = "kid-1", ttl_s: int = 3600):
        self.secret_provider = secret_provider
        self.kid = kid
        self.ttl_s = ttl_s

    def create(self, claims: Dict[str, Any]) -> Dict[str, Any]:
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT", "kid": self.kid}
        payload = {**claims, "iat": now, "exp": now + self.ttl_s}
        signing_input = ".".join([_b64url(json.dumps(header).encode()),
                                  _b64url(json.dumps(payload).encode())]).encode()
        secret = self.secret_provider(self.kid)
        sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
        jwt = f"{signing_input.decode()}.{_b64url(sig)}"
        alias = make_alias(claims.get("realm","public"), claims.get("zone","default"))
        return {"alias": alias, "jwt": jwt, "kid": self.kid, "exp": payload["exp"]}

lukhas/identity/token_validator.py

from __future__ import annotations
import hmac, hashlib, base64, json, time
from typing import Tuple

def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

class TokenValidator:
    def __init__(self, secret_provider):
        self.secret_provider = secret_provider

    def verify(self, jwt: str) -> Tuple[bool, dict | None, str | None]:
        try:
            header_b64, payload_b64, sig_b64 = jwt.split(".")
            header = json.loads(_b64url_decode(header_b64))
            payload = json.loads(_b64url_decode(payload_b64))
            kid = header.get("kid")
            secret = self.secret_provider(kid)
            signing_input = f"{header_b64}.{payload_b64}".encode()
            expected = hmac.new(secret, signing_input, hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _b64url_decode(sig_b64)):
                return False, None, "bad_signature"
            if payload.get("exp", 0) < int(time.time()):
                return False, None, "expired"
            return True, payload, None
        except Exception as e:
            return False, None, f"error:{type(e).__name__}"

Tests

tests/identity/test_token_roundtrip.py

import os
from lukhas.identity.token_generator import TokenGenerator
from lukhas.identity.token_validator import TokenValidator
from lukhas.identity.alias_format import make_alias, verify_crc

def secrets(kid: str) -> bytes:
    return os.environ.get(f"LID_SECRET_{kid}", "devsecret").encode()

def test_alias_crc_roundtrip():
    a = make_alias("realmA","zone1")
    assert verify_crc(a)

def test_jwt_roundtrip():
    gen = TokenGenerator(secrets, kid="kid-1", ttl_s=60)
    out = gen.create({"sub":"user123","realm":"realmA","zone":"zone1"})
    ok, payload, err = TokenValidator(secrets).verify(out["jwt"])
    assert ok and payload["sub"] == "user123" and err is None


⸻

I.2 — Tiered Authentication (T1–T5)

lukhas/identity/tiers.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Tier = Literal["T1","T2","T3","T4","T5"]

@dataclass
class AuthResult:
    tier: Tier
    ok: bool
    reason: str = ""

class Tiers:
    def authenticate_T1(self, ctx) -> AuthResult:
        return AuthResult("T1", ok=True)

    def authenticate_T2(self, ctx) -> AuthResult:
        # See: https://github.com/LukhasAI/Lukhas/issues/562
        return AuthResult("T2", ok=False, reason="not_implemented")

    def authenticate_T3(self, ctx) -> AuthResult:
        # TODO: TOTP check
        return AuthResult("T3", ok=False, reason="not_implemented")

    async def authenticate_T4(self, ctx) -> AuthResult:
        verification = await self._verify_webauthn(ctx)
        if not verification.success:
            return AuthResult("T4", ok=False, reason=verification.error_code or "invalid_webauthn_response")
        return AuthResult("T4", ok=True, reason="hardware_key_authenticated")

    def authenticate_T5(self, ctx) -> AuthResult:
        # TODO: biometric attestation (mock provider)
        return AuthResult("T5", ok=False, reason="not_implemented")

Minimal API wiring (optional scaffold)

lukhas/api/identity.py

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from ..identity.tiers import Tiers

router = APIRouter(prefix="/identity", tags=["identity"])
tiers = Tiers()

@router.post("/authenticate/{tier}")
def authenticate(tier: str, body: dict):
    fn = getattr(tiers, f"authenticate_{tier}", None)
    if not fn:
        raise HTTPException(400, "unknown tier")
    res = fn(body)
    if not res.ok:
        raise HTTPException(401, f"auth_failed:{res.reason}")
    return {"tier": res.tier, "ok": True}

Tests

tests/identity/test_tiers_end_to_end.py

from lukhas.identity.tiers import Tiers

def test_t1_allows_basic_access():
    t = Tiers()
    res = t.authenticate_T1({"ip":"127.0.0.1"})
    assert res.ok and res.tier == "T1"

def test_t2_placeholder_blocks_without_impl():
    t = Tiers()
    res = t.authenticate_T2({"user":"a","pass":"b"})
    assert res.ok is False


⸻

CI Glue (add-on snippet)

.github/workflows/t4-validation.yml (fragments)

jobs:
  memory-storage-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e .[test]
      - run: pytest -q tests/memory -m "not slow"
  consciousness-core-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e .[test]
      - run: pytest -q tests/consciousness
  identity-token-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e .[test]
      - run: pytest -q tests/identity -m "not slow"


⸻

Acceptance Reminders (pin these to PRs)
	•	M.1: E2E p95 <100ms (search/upsert), GDPR delete audited, dedupe invariant holds.
	•	C.1: Reflection p95 <10ms, Dream FSM legal transitions, Guardian consulted on actions.
	•	I.1: JWT + ΛiD alias roundtrip, rotation/expiry enforced, constant-time compare.
	•	I.2: T1–T5 flows wired; T2 uses argon2id; T3 TOTP; T4 WebAuthn; T5 biometric mock; metrics exported.


---------------------------
Here are drop-in observability hooks (Prometheus + OpenTelemetry) tailored to the scaffolds you just adopted (Memory, Consciousness, Identity). Everything is production-friendly, minimal, and ready for CI validation.

⸻

0) Lightweight Observability SDK (drop-in)

lukhas/observability/metrics.py

# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import os, time, contextlib
from prometheus_client import Counter, Histogram, Gauge

_BUCKETS_FAST = (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1)          # 0.5–100ms
_BUCKETS_STD  = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)         # 5ms–2.5s

# Common labels across modules
COMMON_LABELS = dict(
    lane=os.getenv("LUKHAS_LANE", "candidate"),
    service=os.getenv("LUKHAS_SERVICE", "lukhas"),
)

# Memory
MEM_UPSERT_LATENCY = Histogram(
    "lukhas_memory_upsert_seconds", "Latency of memory upsert",
    buckets=_BUCKETS_STD, labelnames=("lane", "service")
)
MEM_SEARCH_LATENCY = Histogram(
    "lukhas_memory_search_seconds", "Latency of memory search",
    buckets=_BUCKETS_STD, labelnames=("lane", "service")
)
MEM_DOCS_TOTAL = Counter(
    "lukhas_memory_docs_total", "Total docs indexed", labelnames=("lane", "service")
)
MEM_DEDUP_DROPPED_TOTAL = Counter(
    "lukhas_memory_dedup_dropped_total", "Dropped duplicate docs", labelnames=("lane", "service")
)

# Consciousness
REFLECT_LATENCY = Histogram(
    "lukhas_reflection_latency_seconds", "Latency of reflection step",
    buckets=_BUCKETS_FAST, labelnames=("lane","service")
)
REFLECT_ANOMALIES_TOTAL = Counter(
    "lukhas_reflection_anomalies_total", "Anomalies detected during reflection",
    labelnames=("lane","service")
)
DREAM_STEP_LATENCY = Histogram(
    "lukhas_dream_step_seconds", "Latency of dream step",
    buckets=_BUCKETS_STD, labelnames=("lane","service")
)
DREAM_BACKPRESSURE = Gauge(
    "lukhas_dream_backpressure", "Backpressure ratio [0..1]", labelnames=("lane","service")
)

# Identity
AUTH_LATENCY = Histogram(
    "lukhas_auth_latency_seconds", "Auth/tier flow latency",
    buckets=_BUCKETS_STD, labelnames=("lane","service","tier")
)
AUTH_FAILURES = Counter(
    "lukhas_auth_failures_total", "Auth failures by tier", labelnames=("lane","service","tier","reason")
)

@contextlib.contextmanager
def time_hist(histogram, **labels):
    # Merge common labels with call-time labels
    lab = {**COMMON_LABELS, **labels}
    start = time.perf_counter()
    try:
        yield
    finally:
        histogram.labels(**lab).observe(time.perf_counter() - start)

def inc(counter, **labels):
    counter.labels(**{**COMMON_LABELS, **labels}).inc()

def set_gauge(gauge, value: float, **labels):
    gauge.labels(**{**COMMON_LABELS, **labels}).set(value)

lukhas/observability/tracing.py

# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter  # replace/exporters as needed

_tracer = None

def init_tracer(service: str = "lukhas"):
    global _tracer
    if _tracer:  # idempotent
        return _tracer
    rp = Resource.create({
        "service.name": service,
        "service.version": os.getenv("LUKHAS_VERSION","dev"),
        "lukhas.lane": os.getenv("LUKHAS_LANE","candidate"),
    })
    tp = TracerProvider(resource=rp)
    # TODO: swap ConsoleSpanExporter with OTLP exporter (grpc/http) in prod
    tp.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tp)
    _tracer = trace.get_tracer(service)
    return _tracer

def tracer():
    return _tracer or init_tracer()

def start_span(name: str, **attrs):
    span = tracer().start_span(name)
    for k, v in attrs.items():
        if v is not None:
            span.set_attribute(k, v)
    return span

✅ Minimal, idempotent, no global side effects beyond setting the provider. Replace ConsoleSpanExporter with OTLP exporter at deploy time.

⸻

1) Wire hooks into Memory scaffolds

lukhas/memory/memory_orchestrator.py (add timings & counters)

from .indexer import Indexer
from lukhas.observability.metrics import time_hist, MEM_UPSERT_LATENCY, MEM_SEARCH_LATENCY, MEM_DOCS_TOTAL
from lukhas.observability.tracing import start_span

class MemoryOrchestrator:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def add_event(self, text: str, meta: dict) -> str:
        with start_span("memory.add_event", lane=meta.get("lane"), fold=meta.get("fold")) as span:  # type: ignore[attr-defined]
            span.set_attribute("mem.meta.size", len(text))
            with time_hist(MEM_UPSERT_LATENCY):
                doc_id = self.indexer.upsert(text, meta)
            MEM_DOCS_TOTAL.labels(lane=meta.get("lane","candidate"), service="lukhas").inc()
            return doc_id

    def query(self, text: str, k: int = 8, filters: dict | None = None):
        with start_span("memory.query", k=k):
            with time_hist(MEM_SEARCH_LATENCY):
                return self.indexer.search_text(text, k=k, filters=filters)

(If you also implement dedupe inside Indexer.upsert, call MEM_DEDUP_DROPPED_TOTAL there.)

⸻

2) Wire hooks into Consciousness scaffolds

lukhas/consciousness/reflection_engine.py

from lukhas.observability.metrics import time_hist, REFLECT_LATENCY, REFLECT_ANOMALIES_TOTAL
from lukhas.observability.tracing import start_span
# ...
class ReflectionEngine:
    def reflect(self, state: ConsciousnessState) -> ReflectionReport:
        with start_span("consciousness.reflect", phase=state.phase):
            with time_hist(REFLECT_LATENCY):
                # TODO: real meta-cognition
                report = ReflectionReport(coherence_score=1.0, drift_ema=0.0, anomalies=[])
                if report.anomalies:
                    REFLECT_ANOMALIES_TOTAL.labels().inc()
                return report

lukhas/consciousness/dream_engine.py

from lukhas.observability.metrics import time_hist, DREAM_STEP_LATENCY, set_gauge, DREAM_BACKPRESSURE
from lukhas.observability.tracing import start_span
# ...
    def step(self, max_time_ms: int = 50) -> None:
        with start_span("consciousness.dream.step", phase=self.phase, max_time_ms=max_time_ms):
            with time_hist(DREAM_STEP_LATENCY):
                self.phase = "DREAMING"
                # TODO: compute backpressure ratio 0..1
                set_gauge(DREAM_BACKPRESSURE, 0.0)


⸻

3) Wire hooks into Identity scaffolds

lukhas/identity/tiers.py

import time
import argon2
from argon2.exceptions import VerifyMismatchError
from lukhas.observability.metrics import AUTH_LATENCY, AUTH_FAILURES, time_hist

password_hasher = argon2.PasswordHasher()

class Tiers:
    def authenticate_T1(self, ctx) -> AuthResult:
        with time_hist(AUTH_LATENCY, tier="T1"):
            return AuthResult("T1", ok=True)

    def authenticate_T2(self, ctx) -> AuthResult:
        start_ok = False
        failure_reason = "invalid_credentials"
        with time_hist(AUTH_LATENCY, tier="T2"):
            candidate_password = getattr(ctx, "password", None)
            stored_hash = getattr(ctx, "password_hash", None)
            credentials = getattr(ctx, "credentials", None)
            if stored_hash is None and credentials is not None:
                stored_hash = credentials.get("password_hash")
            if candidate_password is None and credentials is not None:
                candidate_password = credentials.get("password")

            if not stored_hash:
                failure_reason = "missing_hash"
            elif candidate_password is None:
                failure_reason = "missing_credentials"
            else:
                try:
                    password_hasher.verify(stored_hash, candidate_password)
                except VerifyMismatchError:
                    failure_reason = "invalid_credentials"
                except Exception:
                    failure_reason = "argon2_error"
                else:
                    start_ok = True
        if not start_ok:
            AUTH_FAILURES.labels(tier="T2", reason=failure_reason).inc()
            return AuthResult("T2", ok=False, reason=failure_reason)
        return AuthResult("T2", ok=True, reason="password_authenticated")


⸻

4) Export metrics & traces
	•	If you already have an exporter, skip this. If not, add a tiny HTTP metrics server:

lukhas/observability/export_http.py

from __future__ import annotations
import os, threading
from wsgiref.simple_server import make_server
from prometheus_client import make_asgi_app, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
# Option A: ASGI app (FastAPI can mount make_asgi_app())
app = make_asgi_app()

# Option B: bare WSGI server for quick local testing
def serve_metrics(port: int = 9109):
    def _run():
        httpd = make_server("", port, app)
        httpd.serve_forever()
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

	•	Call serve_metrics() early in your bootstrap / tests to expose /metrics.

⸻

5) Prometheus rules (SLOs) + promtool tests

monitoring/rules/memory.yml

groups:
- name: memory-slos
  rules:
  - record: job:lukhas_memory_search_p95:rate5m
    expr: histogram_quantile(0.95, sum(rate(lukhas_memory_search_seconds_bucket[5m])) by (le))
  - alert: MemorySearchLatencyHigh
    expr: job:lukhas_memory_search_p95:rate5m > 0.1  # 100ms
    for: 10m
    labels: { severity: page }
    annotations:
      summary: "Memory search p95 > 100ms for 10m"

monitoring/rules/reflection.yml

groups:
- name: reflection-slos
  rules:
  - record: job:lukhas_reflection_p95:rate5m
    expr: histogram_quantile(0.95, sum(rate(lukhas_reflection_latency_seconds_bucket[5m])) by (le))
  - alert: ReflectionLatencyHigh
    expr: job:lukhas_reflection_p95:rate5m > 0.01  # 10ms
    for: 5m
    labels: { severity: page }
    annotations:
      summary: "Reflection p95 > 10ms"
  - alert: ReflectionAnomalyBurst
    expr: rate(lukhas_reflection_anomalies_total[5m]) > 0.1
    for: 5m
    labels: { severity: warn }
    annotations:
      summary: "Reflection anomalies elevated"

monitoring/rules/identity.yml

groups:
- name: identity-slos
  rules:
  - record: job:lukhas_auth_p95:rate5m
    expr: histogram_quantile(0.95, sum by (le,tier) (rate(lukhas_auth_latency_seconds_bucket[5m])))
  - alert: IdentityAuthFailures
    expr: sum(rate(lukhas_auth_failures_total[5m])) by (tier) > 0.2
    for: 10m
    labels: { severity: warn }
    annotations:
      summary: "Auth failures elevated"

Promtool tests (fast CI smoke)

monitoring/tests/reflection_rules_test.yml

rule_files:
  - ../rules/reflection.yml
evaluation_interval: 1m
tests:
- interval: 1m
  input_series:
    - series: 'lukhas_reflection_latency_seconds_bucket{le="0.005"}'
      values: 10x5
    - series: 'lukhas_reflection_latency_seconds_bucket{le="0.01"}'
      values: 20x5
    - series: 'lukhas_reflection_latency_seconds_bucket{le="+Inf"}'
      values: 30x5
  alert_rule_test:
    - eval_time: 5m
      alertname: ReflectionLatencyHigh
      exp_alerts: []   # below 10ms → no alert

Add similar *_rules_test.yml for memory & identity.

⸻

6) CI glue (fragments)

.github/workflows/t4-validation.yml (add jobs)

jobs:
  prom-rules-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: promtool
        run: |
          wget -qO promtool.tar.gz https://github.com/prometheus/prometheus/releases/download/v2.54.1/prometheus-2.54.1.linux-amd64.tar.gz
          tar -xzf promtool.tar.gz --strip-components=1 prometheus-2.54.1.linux-amd64/promtool
          chmod +x promtool
          ./promtool test rules monitoring/tests/reflection_rules_test.yml
          # add memory/identity tests here as you create them

  e2e-perf-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e .[test]
      - name: run perf suites
        run: |
          pytest -q tests/memory -m e2e_perf
          pytest -q tests/consciousness -m e2e_perf
          pytest -q tests/identity -m e2e_perf


⸻

7) Tiny test hooks to assert metrics exist

tests/observability/test_metrics_exposed.py

import re, requests, threading, time
from lukhas.observability.export_http import serve_metrics

def test_metrics_endpoint_smoke():
    t = serve_metrics(port=9109)
    time.sleep(0.5)
    resp = requests.get("http://127.0.0.1:9109/metrics", timeout=3)
    assert resp.status_code == 200
    body = resp.text
    assert "lukhas_memory_search_seconds_bucket" in body
    assert "lukhas_reflection_latency_seconds_bucket" in body

If using offline CI, replace requests with stdlib urllib.request.

⸻

8) OTLP exporter (when you’re ready)

Replace ConsoleSpanExporter with OTLP:

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# ...
tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT","http://otel-collector:4318/v1/traces"))))

Set OTEL_EXPORTER_OTLP_ENDPOINT in your env/helm values.

⸻

Acceptance checklist (per module)
	•	Memory
	•	lukhas_memory_upsert_seconds / search_seconds histograms populate
	•	p95 PromQL recording rules compute as expected
	•	E2E p95 < 100ms gate enforced in CI
	•	Consciousness
	•	lukhas_reflection_latency_seconds histogram emits on each reflection
	•	anomaly counter increments on injected anomalies
	•	dream backpressure gauge visible
	•	Identity
	•	lukhas_auth_latency_seconds{tier=...} per-tier emitted
	•	failures counter increments on negative paths
	•	Tracing
	•	Spans memory.add_event, memory.query, consciousness.reflect, consciousness.dream.step, identity.authenticate_T*
	•	service.name, lukhas.lane, component attributes present



---------------------------

Here’s a ready-to-import Grafana dashboard JSON wired to the metric names we just added. Save as monitoring/grafana-dashboard-lukhas.json, then import in Grafana → Dashboards → Import.

⸻

File: monitoring/grafana-dashboard-lukhas.json

{
  "uid": "lukhas-t4-core",
  "title": "LUKHΛS • Core (Memory • Consciousness • Identity) — T4/0.01%",
  "schemaVersion": 39,
  "version": 1,
  "tags": ["lukhas", "t4", "observability"],
  "timezone": "browser",
  "editable": true,
  "refresh": "10s",
  "time": { "from": "now-6h", "to": "now" },
  "templating": {
    "list": [
      {
        "type": "datasource",
        "name": "DS_PROM",
        "label": "Prometheus",
        "query": "prometheus",
        "refresh": 1
      },
      {
        "type": "query",
        "name": "lane",
        "label": "Lane",
        "datasource": "$DS_PROM",
        "refresh": 2,
        "hide": 0,
        "definition": "label_values(lukhas_memory_search_seconds_bucket, lane)",
        "query": "label_values(lukhas_memory_search_seconds_bucket, lane)",
        "current": { "text": "candidate", "value": "candidate" },
        "includeAll": false,
        "multi": false
      },
      {
        "type": "query",
        "name": "service",
        "label": "Service",
        "datasource": "$DS_PROM",
        "definition": "label_values(lukhas_memory_search_seconds_bucket, service)",
        "query": "label_values(lukhas_memory_search_seconds_bucket, service)",
        "current": { "text": "lukhas", "value": "lukhas" }
      }
    ]
  },
  "panels": [
    {
      "type": "row",
      "title": "Overview",
      "gridPos": { "h": 1, "w": 24, "x": 0, "y": 0 },
      "collapsed": false
    },
    {
      "type": "stat",
      "title": "SLO • Reflection p95 (<10ms)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 1 },
      "options": { "reduceOptions": { "calcs": ["lastNotNull"] } },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_reflection_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "s",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "red", "value": 0.01 }
            ]
          }
        },
        "overrides": []
      }
    },
    {
      "type": "stat",
      "title": "SLO • Memory search p95 (<100ms)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 6, "y": 1 },
      "options": { "reduceOptions": { "calcs": ["lastNotNull"] } },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_memory_search_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "s",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "red", "value": 0.1 }
            ]
          }
        }
      }
    },
    {
      "type": "stat",
      "title": "SLO • Identity auth p95 (<250ms)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 12, "y": 1 },
      "options": { "reduceOptions": { "calcs": ["lastNotNull"] } },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_auth_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "s",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "red", "value": 0.25 }
            ]
          }
        }
      }
    },
    {
      "type": "stat",
      "title": "Guardian anomalies (5m rate)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 18, "y": 1 },
      "options": { "reduceOptions": { "calcs": ["lastNotNull"] } },
      "targets": [
        {
          "expr": "rate(lukhas_reflection_anomalies_total{lane=\"$lane\",service=\"$service\"}[5m])",
          "legendFormat": "anomalies/s"
        }
      ],
      "fieldConfig": { "defaults": { "unit": "ops" } }
    },

    { "type": "row", "title": "Memory", "gridPos": { "h": 1, "w": 24, "x": 0, "y": 5 } },

    {
      "type": "timeseries",
      "title": "Memory • Search latency (p50/p95/p99)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 0, "y": 6 },
      "fieldConfig": { "defaults": { "unit": "s" } },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum by (le) (rate(lukhas_memory_search_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_memory_search_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, sum by (le) (rate(lukhas_memory_search_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p99"
        }
      ]
    },
    {
      "type": "timeseries",
      "title": "Memory • Upsert latency (p50/p95)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 12, "y": 6 },
      "fieldConfig": { "defaults": { "unit": "s" } },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum by (le) (rate(lukhas_memory_upsert_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_memory_upsert_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        }
      ]
    },
    {
      "type": "stat",
      "title": "Memory • Docs indexed (total)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 13 },
      "targets": [
        {
          "expr": "sum(increase(lukhas_memory_docs_total{lane=\"$lane\",service=\"$service\"}[1h]))",
          "legendFormat": "docs/h"
        }
      ],
      "fieldConfig": { "defaults": { "unit": "ops" } }
    },
    {
      "type": "stat",
      "title": "Memory • Dedupe drops (1h)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 4, "w": 6, "x": 6, "y": 13 },
      "targets": [
        {
          "expr": "sum(increase(lukhas_memory_dedup_dropped_total{lane=\"$lane\",service=\"$service\"}[1h]))",
          "legendFormat": "drops/h"
        }
      ],
      "fieldConfig": { "defaults": { "unit": "ops" } }
    },

    { "type": "row", "title": "Consciousness", "gridPos": { "h": 1, "w": 24, "x": 0, "y": 17 } },

    {
      "type": "timeseries",
      "title": "Reflection • latency (p50/p95/p99)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 0, "y": 18 },
      "fieldConfig": { "defaults": { "unit": "s" } },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum by (le) (rate(lukhas_reflection_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_reflection_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, sum by (le) (rate(lukhas_reflection_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "p99"
        }
      ]
    },
    {
      "type": "timeseries",
      "title": "Dream • step latency & backpressure",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 12, "y": 18 },
      "fieldConfig": { "defaults": { "unit": "s" } },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(lukhas_dream_step_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "step p95"
        },
        {
          "expr": "avg_over_time(lukhas_dream_backpressure{lane=\"$lane\",service=\"$service\"}[5m])",
          "legendFormat": "backpressure avg"
        }
      ]
    },

    { "type": "row", "title": "Identity", "gridPos": { "h": 1, "w": 24, "x": 0, "y": 25 } },

    {
      "type": "timeseries",
      "title": "Identity • auth latency (p95 by tier)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 0, "y": 26 },
      "fieldConfig": { "defaults": { "unit": "s" } },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le,tier) (rate(lukhas_auth_latency_seconds_bucket{lane=\"$lane\",service=\"$service\"}[5m])))",
          "legendFormat": "tier {{tier}}"
        }
      ]
    },
    {
      "type": "timeseries",
      "title": "Identity • auth failures (rate by tier)",
      "datasource": "$DS_PROM",
      "gridPos": { "h": 7, "w": 12, "x": 12, "y": 26 },
      "targets": [
        {
          "expr": "sum by (tier,reason) (rate(lukhas_auth_failures_total{lane=\"$lane\",service=\"$service\"}[5m]))",
          "legendFormat": "tier {{tier}} ({{reason}})"
        }
      ],
      "fieldConfig": { "defaults": { "unit": "ops" } }
    }
  ]
}


⸻

Import & wire-up
	1.	Save the JSON to monitoring/grafana-dashboard-lukhas.json.
	2.	In Grafana → Dashboards → Import → Upload JSON → choose Prometheus datasource.
	3.	Ensure Prometheus scrapes your /metrics endpoint (use the serve_metrics() helper you added).
	4.	Optional: point the row SLO panels at your recording rules (if you created them) by swapping expressions to your job:*:rate5m records.

⸻

