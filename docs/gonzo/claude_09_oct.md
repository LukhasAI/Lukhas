
**Context**
We’re down to ~39 pytest *collection* errors. I inspected the repo to target the fastest, highest-leverage fixes. Below are atomic patches and commands to get us from “can’t collect” → “can run tests,” plus a short follow-through plan.

---

## 1) Immediate collection blockers (apply first)

### 1.1 Missing symbols: `lukhas.observability.service_metrics.MetricType`

Tests and runtime modules import `MetricType` from `lukhas.observability.service_metrics`, but the module is currently a stub with no exports. Implement a minimal enum so imports resolve.

**Patch**

```diff
*** a/lukhas/observability/service_metrics.py
--- b/lukhas/observability/service_metrics.py
@@
-"""Constellation Framework observability service metrics (stub)."""
-__all__: list[str] = []
+"""LUKHAS observability service metrics."""
+from enum import Enum
+
+class MetricType(Enum):
+    PERFORMANCE = "performance"
+    LATENCY = "latency"
+    THROUGHPUT = "throughput"
+    ERROR_RATE = "error_rate"
+    SAFETY = "safety"
+    TRINITY = "trinity"
+
+__all__ = ["MetricType"]
```

Why: multiple modules reference a `MetricType` concept; we also have parallel enums in orchestration monitoring (e.g., enterprise monitor & intelligence monitor) that should not block collection. Implementing a light version here satisfies imports cleanly. (See monitoring modules defining their own enums, which is fine at runtime, but the *import site* tests look for this canonical path.)   

---

### 1.2 Local urllib3 stub colliding with real urllib3

We vendor a `third_party_stubs/urllib3` shim used during collection. Tests and transitive deps expect `urllib3.__version__` and exceptions like `HTTPError`/`DependencyWarning`. Extend the stub to satisfy those imports.

**Patches**

```diff
*** a/third_party_stubs/urllib3/__init__.py
--- b/third_party_stubs/urllib3/__init__.py
@@
-"""Stub urllib3 package for testing environment."""
-from . import exceptions
+"""Stub urllib3 package for testing environment."""
+from . import exceptions
+__version__ = "0.0-stub"
@@
-def disable_warnings(category: type[Warning] | None = None) -> None:
+def disable_warnings(category: type[Warning] | None = None) -> None:
     """Stub disable_warnings to satisfy test harness."""
 
-__all__ = ["exceptions", "disable_warnings"]
+__all__ = ["exceptions", "disable_warnings", "__version__"]
```

```diff
*** a/third_party_stubs/urllib3/exceptions.py
--- b/third_party_stubs/urllib3/exceptions.py
@@
-"""Stub exceptions module for urllib3."""
+"""Stub exceptions module for urllib3."""
 
 class NotOpenSSLWarning(Warning):
     """Placeholder warning to satisfy test configuration."""
 
 class InsecureRequestWarning(Warning):
     """Placeholder warning for insecure request handling."""
 
+class DependencyWarning(Warning):
+    """Compatibility warning class expected by some libs."""
+
+class HTTPError(Exception):
+    """Base HTTP error used by callers importing from urllib3.exceptions."""
+
-__all__ = ["NotOpenSSLWarning", "InsecureRequestWarning"]
+__all__ = ["NotOpenSSLWarning", "InsecureRequestWarning", "DependencyWarning", "HTTPError"]
```

Evidence that the stub exists (and is minimal) is here. We add the attributes tests/deps demand.  

---

### 1.3 Markers: declare what tests actually use

Root `pytest.ini` defines a bunch of markers, but `load`, `soak`, and `mcp_operational` are used and not declared at the root (there is a second `tests/unit/pytest.ini` with `property_based`, etc.). Add the missing ones in the root to avoid collection aborts.

**Patch**

```diff
*** a/pytest.ini
--- b/pytest.ini
@@
 markers =
     roadmap: Tests for the upcoming roadmap features (~12 months away)
     grad: Graduate-level complexity tests (EDA, the law of high numbers, advanced stats)
     expert: Spicy tests aimed for domain experts
     sanity: Smoke, must never fail under normal conditions
     basic: "First bring-up tests"
     mcp: Minimal Contingent Processes are operational in the system
+    mcp_operational: MCP end-to-end operational checks
+    load: Load/performance scenarios
+    soak: Long-running stability scenarios
     smoke: The most basic unit test to check the pipeline
```

Root markers file reference:  and evidence of separate unit-level markers: 

---

### 1.4 NameError: `logging` being used before import in some quantum/qi code

At least one quantum adapter had the logger instantiated before importing `logging` in earlier passes; the current, main adapter already imports logging at the top and sets `logger` correctly, which is what we want everywhere. Mirror that pattern in any stragglers.

Reference good pattern: top-of-file `import logging` + `logger = logging.getLogger(__name__)`. 

*(If you still see NameError on `logging` in collection, grep for files where `logging.getLogger` appears before `import logging` and reorder imports.)*

---

## 2) “RecursionError” in circuit breaker tests

Tests exercise `lukhas.core.reliability.circuit_breaker` together with async orchestration. The circuit breaker module itself is small and sane—decorator returns a wrapper that calls through; no obvious recursion in the implementation. The likely culprit is test wiring with orchestrator or a circular import in the test’s fixtures.

Action:

* Keep using the modern module paths under `lukhas.core.reliability` and `matriz.core.async_orchestrator` that already exist.
* If recursion persists, add a simple guard in the decorator to avoid re-wrapping functions already wrapped by the breaker:

```diff
*** a/lukhas/core/reliability/circuit_breaker.py
--- b/lukhas/core/reliability/circuit_breaker.py
@@
 def circuit_breaker(max_failures: int = 5, reset_timeout: float = 60.0):
-    def decorator(func):
+    def decorator(func):
+        if getattr(func, "__lukhas_cb_wrapped__", False):
+            return func
         breaker = CircuitBreaker(max_failures, reset_timeout)
         if asyncio.iscoroutinefunction(func):
             async def wrapper(*args, **kwargs):
                 return await breaker.call(func, *args, **kwargs)
             return wrapper
         else:
             def wrapper(*args, **kwargs):
                 return breaker.call(func, *args, **kwargs)  # type: ignore
-        return wrapper
+        wrapper.__lukhas_cb_wrapped__ = True
+        return wrapper
```

This prevents double wrapping (a common source of runaway recursion when fixtures stack decorators). If the error was from import cycles, this still leaves us safe.

---

## 3) “TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'”

This happens when `X | None` is evaluated at runtime (not just in type hints) or when running on 3.9 without `from __future__ import annotations`. We’re on modern Python, but some modules may be performing unions in values, not annotations.

Actions (codemod):

* Ensure all modules with runtime unions are converted to annotations only (e.g., `def f(x: int | None) -> str | None:` is fine; don’t compute `int | None` in values).
* Run a sweep and auto-upgrade:

  ```
  uvx pyupgrade --py311-plus $(git ls-files '*.py')
  ruff check --select UP --fix
  ```
* Quick detector:

  ```
  rg -n "=\s*[A-Za-z_][A-Za-z0-9_]*\s*\|\s*None\b" lukhas candidate matriz
  ```

---

## 4) Failed imports (oauth manager, guardian schema, provider compatibility)

Most of these are “missing bridge/export” class of errors. Two low-friction fixes:

### 4.1 Add governance/guardian serialization exports

Implement the minimal surface tests import:

```diff
*** a/lukhas/governance/guardian_serializers.py
--- b/lukhas/governance/guardian_serializers.py
@@
-"""Guardian serialization (stub)."""
+"""Guardian serialization."""
+from dataclasses import dataclass
+from typing import Any, Protocol
+
+class GuardianSerializer(Protocol):
+    def serialize(self, obj: Any) -> dict: ...
+    def deserialize(self, data: dict) -> Any: ...
+
+@dataclass
+class GuardianEnvelopeSerializer:
+    version: str = "1"
+    def wrap(self, payload: dict) -> dict:
+        return {"v": self.version, "payload": payload}
+    def unwrap(self, envelope: dict) -> dict:
+        return envelope.get("payload", {})
+
+class GuardianSerializerRegistry:
+    _reg: dict[str, GuardianSerializer] = {}
+    @classmethod
+    def register(cls, name: str, ser: GuardianSerializer) -> None:
+        cls._reg[name] = ser
+    @classmethod
+    def get(cls, name: str) -> GuardianSerializer:
+        return cls._reg[name]
+
+def deserialize_guardian(envelope: dict) -> Any:
+    # Minimal default path (tests can inject registry entries)
+    return envelope.get("payload")
+
+__all__ = [
+    "GuardianSerializer",
+    "GuardianEnvelopeSerializer",
+    "GuardianSerializerRegistry",
+    "deserialize_guardian",
+]
```

### 4.2 Async utils: ensure `consciousness_context` exists

Good news: `lukhas/async_utils.py` already provides `consciousness_context` and friends, so imports should succeed where callers expect them. If any tests still import from `lukhas.async_utils.consciousness_context`, that symbol is present. 

---

## 5) Prometheus duplication during collection

We already have a pytest-level guard that resets the global registry during session start—keep it; that should neutralize “duplicate CollectorRegistry” failures during collection and reruns. (Look at `tests/conftest.py` for the registry reset and telemetry guard.) 

If any module defines metrics at import time, wrap the histogram/counter/gauge definitions in an “already_registered?” guard keyed by metric name to avoid re-registration on reimport in collection.

---

## 6) Optional: tiny paper cuts that cascade

* **Fix broken f-strings / typos in monitoring code**: e.g. a brace mismatch will kill collection. In `intelligence_monitor.py`, `_check_alert_conditions` builds an f-string with mismatched braces—repair it:

  ```diff
  -alert_id = f"{metric_name}_{alert_level.value}_{int(time.time())"
  +alert_id = f"{metric_name}_{alert_level.value}_{int(time.time())}"
  -message=f"{metric_name} threshold exceeded: {value} (threshold: {threshold_value)})",
  +message=f"{metric_name} threshold exceeded: {value} (threshold: {threshold_value})",
  ```

  File context here. 

* **Keep imports on canonical paths**: tests already import `AsyncCognitiveOrchestrator` from `matriz.core.async_orchestrator` and circuit functions from `lukhas.core.reliability.circuit_breaker`. Those modules exist and are self-contained; keep using them rather than candidate-layer paths to avoid bridge churn.

---

## 7) Commands to run (sanity + push)

```bash
# 1) Lint codemods for PEP 604/py311
uvx pyupgrade --py311-plus $(git ls-files '*.py')
ruff check --select UP --fix

# 2) Run collection-only first (fast feedback)
pytest -q --collect-only

# 3) If collection succeeds, run unit subset with markers ignored:
pytest -q -m "not soak and not load and not mcp_operational" tests/unit

# 4) Push the accumulated commits
git status
git push origin HEAD:main
```

---

## 8) Stretch goals after collection is green

* Replace any lingering “dynamic imports” pointing at `candidate.*` with stable `lukhas.*`/`matriz.*` APIs (we’ve created the minimal exports so that is now possible).
* Add more behavior to in-repo fakes so tests asserting state changes can pass (e.g., memory fold engine & fake backends).
* Tame the 3k+ non-blocking ruff issues after the suite is runnable.

---

**That’s it.** Apply the patches in §1 (metric enum, urllib3 stub, markers), then rerun *collection only*. If we still see the three RecursionErrors, drop in the breaker de-dup guard in §2 and re-collect. After that, run the small unit subset and proceed to the behavior fixes.
