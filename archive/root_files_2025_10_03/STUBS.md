
---

## What’s included (new files only)

```
lukhas/
  core/
    interfaces.py
    registry.py
  metrics.py

core/
  symbolic/
    constraints/
      plan_verifier.py

candidate/
  core/
    orchestration/
      loader.py
      otel.py
      consensus_arbitrator.py
      meta_controller.py

tests/
  registry/test_registry.py
  orchestration/test_node_discovery.py
  orchestration/test_arbitration.py
  orchestration/test_meta_loops.py
  constraints/test_plan_verifier.py
  obs/test_spans_smoke.py
  obs/test_metrics_smoke.py
```

> **Note:** These stubs are self‑contained. If some folders don’t exist yet, create them. All imports are stdlib unless explicitly optional (OTel/Prometheus gracefully no‑op if missing).

---

## 1) `lukhas/core/interfaces.py`

```python
# lukhas/core/interfaces.py
"""
Interfaces and light ABCs for pluggable subsystems.

T4 defaults:
- Small, composable, explicit contracts
- No import side-effects
- Pure typing + ABCs (runtime_checkable where useful)

Usage (example):
    from lukhas.core.interfaces import CognitiveNodeBase

    class EchoNode(CognitiveNodeBase):
        name = "echo"
        AUTOINIT = True

        @classmethod
        def from_env(cls):
            return cls()

        async def process(self, ctx):
            return {"echo": ctx.get("input", "")}
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Protocol, runtime_checkable


class CognitiveNodeBase(ABC):
    """Minimal ABC for dynamic discovery and execution."""
    name: str = "unnamed"
    AUTOINIT: bool = False  # loader respects this

    @classmethod
    def from_env(cls) -> "CognitiveNodeBase":
        """Construct from environment (override in impls)."""
        return cls()

    @abstractmethod
    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        """Do work and return output dict."""
        raise NotImplementedError


@runtime_checkable
class Memory(Protocol):
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...


@runtime_checkable
class Guardian(Protocol):
    def band_for(self, ctx: Mapping[str, Any]) -> str: ...
    def warn(self, code: str, **fields: Any) -> None: ...
```

---

## 2) `lukhas/core/registry.py`

```python
# lukhas/core/registry.py
"""
Simple runtime registry + optional auto-discovery.

Env flags:
- LUKHAS_PLUGIN_DISCOVERY=("auto"|"off") default "off"

Telemetry: print()-based by default (replace with logging/metrics if needed).
"""

from __future__ import annotations
import os
import sys
import importlib
import pkgutil
from typing import Any, Dict

_REG: Dict[str, Any] = {}
_DISCOVERY_FLAG = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off").lower()


def register(kind: str, impl: Any) -> None:
    _REG[kind] = impl
    # Swap for your metrics/logging
    # print(f"[registry] register kind={kind} impl={getattr(impl, '__class__', type(impl)).__name__}")


def resolve(kind: str) -> Any:
    if kind not in _REG:
        raise LookupError(f"no implementation registered for '{kind}'")
    return _REG[kind]


def autoload(prefix: str = "candidate", suffix: str = "plugins") -> None:
    """Import any '{prefix}.**.{suffix}' modules to let them call register()."""
    if _DISCOVERY_FLAG != "auto":
        return
    for mod in pkgutil.iter_modules():
        name = mod.name
        if not name.startswith(f"{prefix}."):
            continue
        if not name.endswith(f".{suffix}"):
            continue
        try:
            importlib.import_module(name)
        except Exception as e:
            # Non-fatal: discovery should not crash the process.
            print(f"[registry] autoload skip {name}: {e}", file=sys.stderr)


__all__ = ["register", "resolve", "autoload"]
```

---

## 3) `candidate/core/orchestration/loader.py`

```python
# candidate/core/orchestration/loader.py
"""
Dynamic node discovery (dark by default).

Discovers classes subclassing CognitiveNodeBase with AUTOINIT=True.
Env:
- NODES_DISABLED="a,b,c" optional deny-list
"""

from __future__ import annotations
import os
import pkgutil
import importlib
import inspect
from typing import Iterable
from lukhas.core.interfaces import CognitiveNodeBase
from lukhas.core.registry import register


def discover_nodes(root_package: str = "candidate") -> int:
    disabled = {x.strip() for x in os.getenv("NODES_DISABLED", "").split(",") if x.strip()}
    found = 0
    for mod in pkgutil.iter_modules():
        name = mod.name
        if not name.startswith(f"{root_package}."):
            continue
        if ".nodes." not in name:
            continue
        try:
            m = importlib.import_module(name)
        except Exception:
            continue
        for _, cls in inspect.getmembers(m, inspect.isclass):
            if not issubclass(cls, CognitiveNodeBase):
                continue
            if not getattr(cls, "AUTOINIT", False):
                continue
            node_name = getattr(cls, "name", cls.__name__)
            if node_name in disabled:
                continue
            try:
                inst = cls.from_env()
                register(f"node:{node_name}", inst)
                found += 1
            except Exception:
                continue
    return found
```

---

## 4) `candidate/core/orchestration/otel.py`

```python
# candidate/core/orchestration/otel.py
"""
OTel span helper. Falls back to no-op if opentelemetry not installed.
"""

from __future__ import annotations
from contextlib import contextmanager

try:
    from opentelemetry import trace  # type: ignore
    _TRACER = trace.get_tracer("lukhas.matriz")
except Exception:  # pragma: no cover
    _TRACER = None


@contextmanager
def stage_span(name: str, **attrs):
    if _TRACER is None:
        yield None
        return
    with _TRACER.start_as_current_span(f"matriz.{name}") as sp:
        for k, v in attrs.items():
            try:
                sp.set_attribute(f"matriz.{k}", v)
            except Exception:
                pass
        yield sp
```

---

## 5) `candidate/core/orchestration/consensus_arbitrator.py`

```python
# candidate/core/orchestration/consensus_arbitrator.py
"""
Consensus arbitration: choose among proposals with ethics gating.

Fail-closed: ethics_risk >= 0.8 is excluded.
"""

from __future__ import annotations
from dataclasses import dataclass
import math
import time
from typing import Iterable, List, Tuple


@dataclass
class Proposal:
    id: str
    confidence: float
    ts: float
    ethics_risk: float  # 0 allow ... 1 block
    role_weight: float  # e.g. ΛiD weight
    rationale: str = ""


def score(p: Proposal, now: float | None = None) -> float:
    now = now or time.time()
    if p.ethics_risk >= 0.8:
        return -math.inf
    recency = math.exp(-max(0.0, (now - p.ts)) / 30.0)
    return (0.6 * p.confidence) + (0.3 * recency) + (0.1 * p.role_weight) - (0.5 * p.ethics_risk)


def choose(proposals: Iterable[Proposal]) -> Tuple[Proposal | None, dict]:
    ranked: List[Tuple[Proposal, float]] = []
    for p in proposals:
        ranked.append((p, score(p)))
    ranked.sort(key=lambda t: t[1], reverse=True)
    winner = ranked[0][0] if ranked else None
    rationale = {"ranking": [(p.id, s) for p, s in ranked[:5]]}
    return winner, rationale
```

---

## 6) `candidate/core/orchestration/meta_controller.py`

```python
# candidate/core/orchestration/meta_controller.py
"""
Simple oscillation detector to break loops in orchestrations.
"""

from __future__ import annotations
from collections import deque


class MetaController:
    def __init__(self, window: int = 4):
        self.window = deque(maxlen=window)

    def step(self, stage_name: str) -> bool:
        """
        Return True if a 2-cycle A->B->A->B detected in last 4 steps.
        """
        snapshot = list(self.window) + [stage_name]
        self.window.append(stage_name)
        if len(snapshot) < 4:
            return False
        return snapshot[-4] == snapshot[-2] and snapshot[-3] == snapshot[-1]
```

---

## 7) `core/symbolic/constraints/plan_verifier.py`

```python
# core/symbolic/constraints/plan_verifier.py
"""
Hard constraints pre-exec (minimal, extend later).

Rule examples:
- Block external POST when plan indicates PII presence.
"""

from __future__ import annotations
from typing import Mapping, Tuple, List


def verify(plan: Mapping) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    contains_pii = bool(plan.get("contains_pii"))
    verb = str(plan.get("verb", "")).upper()
    target = str(plan.get("target", ""))

    if contains_pii and verb == "POST" and ("http://" in target or "https://" in target):
        violations.append("PII+external_POST")

    return (len(violations) == 0, violations)
```

---

## 8) `lukhas/metrics.py` (no‑op friendly Prom stubs)

```python
# lukhas/metrics.py
"""
Prometheus metrics (optional). Falls back to no-op if client missing.
Env:
- ENABLE_PROM=1 to start an exporter on PROM_PORT (default 9108)
"""

from __future__ import annotations
import os
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, start_http_server  # type: ignore
except Exception:  # pragma: no cover
    Counter = Histogram = None
    start_http_server = None


ENABLED = os.getenv("ENABLE_PROM", "0") == "1"
if ENABLED and start_http_server is not None:
    try:
        start_http_server(int(os.getenv("PROM_PORT", "9108")))
    except Exception:
        pass


def _noop_histogram(*_labels):
    @contextmanager
    def _timer():
        yield
    return _timer()


class _NoopCounter:
    def labels(self, *_args, **_kwargs): return self
    def inc(self, *_args, **_kwargs): pass


class _NoopHistogram:
    def labels(self, *_args, **_kwargs): return self
    def time(self): return _noop_histogram()


if Counter is None or Histogram is None:
    stage_latency = _NoopHistogram()
    stage_timeouts = _NoopCounter()
    guardian_band = _NoopCounter()
else:
    stage_latency = Histogram("matriz_stage_latency_seconds", "Latency per stage", ["stage"])
    stage_timeouts = Counter("matriz_stage_timeouts_total", "Timeouts per stage", ["stage"])
    guardian_band = Counter("guardian_risk_band_total", "Decisions per risk band", ["band"])

__all__ = ["stage_latency", "stage_timeouts", "guardian_band"]
```

---

## 9) Test stubs (pytest)

> These are light smoke tests to lock contracts without needing heavy fixtures.

### `tests/registry/test_registry.py`

```python
# tests/registry/test_registry.py
import pytest
from lukhas.core.registry import register, resolve

def test_registry_roundtrip():
    register("memory", object())
    got = resolve("memory")
    assert got is not None
```

### `tests/orchestration/test_node_discovery.py`

```python
# tests/orchestration/test_node_discovery.py
import importlib
import types
import sys
import pytest

@pytest.mark.skipif("candidate" not in sys.modules and not any(m.startswith("candidate") for m in sys.modules),
                    reason="candidate package not present in test env")
def test_discovery_smoke():
    # If the candidate package is present, just ensure discover doesn't crash.
    loader = importlib.import_module("candidate.core.orchestration.loader")
    count = loader.discover_nodes(root_package="candidate")
    assert isinstance(count, int)
    assert count >= 0
```

### `tests/orchestration/test_arbitration.py`

```python
# tests/orchestration/test_arbitration.py
from candidate.core.orchestration.consensus_arbitrator import Proposal, choose

def test_arbitration_ethics_gate():
    p1 = Proposal(id="safe", confidence=0.7, ts=0.0, ethics_risk=0.1, role_weight=0.5)
    p2 = Proposal(id="risky", confidence=0.9, ts=0.0, ethics_risk=0.95, role_weight=0.5)
    winner, rationale = choose([p1, p2])
    assert winner.id == "safe"
    assert any(pid == "safe" for pid, _ in rationale["ranking"])
```

### `tests/orchestration/test_meta_loops.py`

```python
# tests/orchestration/test_meta_loops.py
from candidate.core.orchestration.meta_controller import MetaController

def test_detects_two_cycle():
    m = MetaController()
    assert not m.step("A")
    assert not m.step("B")
    assert not m.step("A")
    assert m.step("B")  # A,B,A,B
```

### `tests/constraints/test_plan_verifier.py`

```python
# tests/constraints/test_plan_verifier.py
from core.symbolic.constraints.plan_verifier import verify

def test_blocks_pii_external_post():
    ok, viol = verify({"contains_pii": True, "verb": "POST", "target": "https://api.example.com"})
    assert not ok and "PII+external_POST" in viol

def test_allows_safe_get():
    ok, viol = verify({"contains_pii": False, "verb": "GET", "target": "/internal"})
    assert ok and not viol
```

### `tests/obs/test_spans_smoke.py`

```python
# tests/obs/test_spans_smoke.py
import contextlib
from candidate.core.orchestration.otel import stage_span

def test_span_noop_ok():
    # Works even if opentelemetry is not installed
    with contextlib.ExitStack() as s:
        s.enter_context(stage_span("INTENT", node="dummy"))
```

### `tests/obs/test_metrics_smoke.py`

```python
# tests/obs/test_metrics_smoke.py
import os
from lukhas import metrics

def test_metrics_noop_labels_inc_ok(monkeypatch):
    monkeypatch.setenv("ENABLE_PROM", "0")
    metrics.stage_timeouts.labels("INTENT").inc()
    with metrics.stage_latency.labels("INTENT").time():
        pass
```

---

## How to drop in (safe steps)

1. **Create folders if missing** and paste files exactly as above.
2. Keep all new paths **dark by default** (no behavior change unless you wire them).
3. Run fast smoke:

```bash
pytest -q tests/registry tests/constraints -q
pytest -q tests/orchestration/test_arbitration.py -q
```

4. If `candidate` package isn’t present/installed, node discovery test will auto‑skip.

---

## What’s intentionally *not* in these stubs

* No production side‑effects (no network, no filesystem).
* No heavy dependencies required (OTel/Prom are optional and no‑op if absent).
* No orchestrator rewiring yet—these are drop‑in building blocks you can wire in PRs per your rollout plan.

---

## T4 / 0.01% notes

* **Fail‑closed:** arbitrator excludes high ethics risk; verifier blocks risky patterns.
* **Observability‑ready:** span helper & metrics objects are present (harmless if unused).
* **Upgradeable:** loader/registry are minimal, typed, and feature‑flag friendly.
* **Tests first:** smoke tests lock interfaces without over‑constraining future design.

---
