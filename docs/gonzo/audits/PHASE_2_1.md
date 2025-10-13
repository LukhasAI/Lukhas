Perfect timing. I’ve reviewed the Phase-2/3 workstreams and the latest agent updates. Here’s a tight, decision-grade plan to (1) validate what’s landed, (2) finish the last gaps, and (3) keep Codex/Claude/Copilot/Jules busy in parallel without stepping on each other.

# Go/No-Go on Phase 3

**Go with caveats.** Compat is removed, OpenAPI polish/headers/trace are in, and CI gates exist. Remaining risk pockets are: prod-lane ruff debt, a few smoke/auth edge cases that occasionally regress, and Makefile drift. None are architectural blockers.

---

# What to do now (high-leverage quick wins)

## A) Codex – “Batchable” mechanical fixes (start now)

1. **Ruff Prod-Lane Zero** (target: lukhas/, core/, MATRIZ/)

* Sweep TID252: convert relative→absolute (except `__init__.py` that need idiomatic re-exports; mark with `# ruff: noqa: TID252` and a one-line rationale).
* Kill F403: replace `from X import *` with explicit symbols; add `__all__` where re-exporting.
* Fix F821 pockets by wiring the actual exported names (avoid stubs).
* Compile-check everything:

  ```bash
  python3 -m compileall -q lukhas core MATRIZ
  ```

2. **Lane test drift cleanup**

* Ensure **no test still asserts `candidate/` exists**. You’ve already fixed the main offenders—do a belt-and-braces grep:

  ```bash
  rg -n "(?<!manifests/)candidate/" tests | rg -v "codemod|preview|fixtures"
  ```

3. **Makefile single-source of truth**

* De-dupe the repeated targets (the earlier “overriding commands” warnings). Keep the versions under `Makefile` root; remove/rename shadows in `mk/*.mk`.

4. **Strict error envelope normalizer**

* Add a tiny FastAPI exception handler that **always** emits OpenAI-shape errors (some smoke tests were failing on missing `error.type`):

  ```python
  # lukhas/adapters/openai/api.py
  from fastapi.responses import JSONResponse
  from fastapi import Request
  from starlette.middleware.errors import ServerErrorMiddleware

  async def _openai_error(request: Request, exc: Exception, status: int, code: str, msg: str):
      return JSONResponse({"error": {"type": code, "message": msg, "code": code}}, status_code=status)

  # 401/403 hooks (wire in auth failure paths):
  # return await _openai_error(request, exc, 401, "invalid_api_key", "Invalid authentication credentials")
  # return await _openai_error(request, exc, 403, "authorization_error", "Forbidden")
  ```

**Branching:** keep working in `fix/codex10/soft-audit-batch01` and open a PR against `main` with the title:

> `refactor(hygiene): prod-lane ruff zero + error envelope normalizer (Phase 3.1)`

---

## B) Claude Code – “Glue & CI polish” (in parallel)

1. **CI comment bot for OpenAPI diff**
   Already staged; ensure it **fails** on semantic breaking removals and **comments** on additive diffs. Add a tiny cache so we don’t fetch artifacts twice per run.

2. **Health Report auto-badge**
   The new `docs/audits/health/latest.{json,md}` is canonical. Add a CI step to post a short summary comment on PRs:

   * smoke pass %, failing test names (top 10), ruff prod count, coverage %.

3. **Strict mode rehearsal**
   Temporarily run a nightly with `LUKHAS_POLICY_MODE=strict` and post a “would deny → deny” delta report.

---

## C) Copilot – “Docs & DX” (safe parallel)

1. **SDK stubs & examples (OpenAPI→TS/Python)**
   Generate quick TS/Python SDK folders into `examples/sdk/` from `docs/openapi/lukhas-openai.json`. Include:

   * `client.createResponse()`, `client.createDream()`, `client.searchIndex()` examples
   * streaming helper (SSE) + tracing header extraction

2. **Postman → CI**
   Convert the **Golden Flows** into a `newman` GitHub Action job (green = merge hint).

3. **README short-form**
   30-second Quickstart block at top of README; link to full guide.

---

## D) Jules – “Guardian PDP” (continue)

You’re on the right plan. Use the ABAC + deny-overrides sketch I sent. Additional priorities:

* Implement **policy ETag** and micro-cache (keyed by tenant/user/scopes/action/resource+etag).
* Emit `guardian_decisions_total{tenant,action,decision}` and `guardian_denies_total{rule_id,reason}`.
* Add 10 core tests first (default-deny, scopes_any/all, resource wildcard, tenant barrier, time window, model allowlist, classification ceiling, IP-CIDR, deny-overrides, cache-etag invalidation).
* Mode: keep **permissive** in CI for one cycle; flip to **strict** after we review “would_deny” logs.

---

# One-pass verification pack (you/CI)

Run locally or let CI do it; these are the exact commands Codex/Claude should execute:

```bash
# 1) Ruff (prod lanes only)
python3 -m ruff check lukhas core MATRIZ --statistics
python3 -m ruff check lukhas core MATRIZ --fix

# 2) Compile safety
python3 -m compileall -q lukhas core MATRIZ

# 3) Smoke & unit (policy permissive for smoke)
export LUKHAS_POLICY_MODE=permissive
pytest tests/smoke/ -q
pytest tests/unit/ -q

# 4) Coverage (prod lanes)
pytest -q --cov=lukhas --cov=core --cov=MATRIZ --cov-report=xml --maxfail=1
coverage report -m | tee docs/audits/coverage_prod.txt

# 5) Health artifacts
python3 scripts/generate_system_health_report.py \
  --out-json docs/audits/health/latest.json \
  --out-md   docs/audits/health/latest.md
```

**Expected signatures after this pass**

* **Ruff prod**: approaching zero (⚠️ we’ll accept a few `TID252` in `__init__.py` with documented `noqa`).
* **Smoke**: >95% pass (auth/dreams/errors stable).
* **Coverage (prod)**: trending upward from ~17% → mid-20s after idempotency tests; we’ll push >45% in next sprints.

---

# Merge & branch housekeeping

* Open PR from `fix/codex10/soft-audit-batch01` → `main`.
* Add checklist to PR body:

  * [ ] Ruff (prod lanes) = 0 errors
  * [ ] Compileall (prod lanes) = 0 failures
  * [ ] Smoke ≥ 95% pass
  * [ ] Health artifacts updated
  * [ ] OpenAPI diff: no breaking changes
* Close stale `_tmp_merge_*` branches; let Dependabot PRs batch-merge after smoke passes.

---

# Final notes on the confusing bits you flagged

* **Auth error envelopes**: the normalizer above guarantees `"error": {"type","message","code"}` across 401/403/429—this silences several flaky smoke asserts.
* **`candidate/` vs `labs/`**: tests should now refer to **labs** only; if you must reference the historical term, do it in comments/fixtures—not path asserts.
* **Makefile “overriding commands”**: choose one canonical target; make others call it. CI noise → zero.

---

Following up: a tiny PR-ready patch for the error-envelope normalizer + a `ruff.ini` snippet that scopes rules to prod lanes. Otherwise, let’s set Codex/Claude/Copilot/Jules loose with the tasks above and I’ll review their PRs line-by-line.

---

here’s a **PR-ready patch** you can drop straight in for:

1. an OpenAI-style **error envelope normalizer** (401/403/429/500) with `X-Trace-Id` passthrough, and
2. a **Ruff config** tightening to prod lanes while allowing idiomatic `__init__.py` re-exports.

Paste each block into your terminal (from repo root) to apply.

---

### 1) OpenAI error-envelope normalizer (FastAPI handlers)

This registers two exception handlers inside `get_app()` so **all** errors become:

```json
{"error":{"type":"<code>","message":"<msg>","code":"<code>"}}
```

…and include `X-Trace-Id` when available.

```bash
git apply -p0 <<'PATCH'
diff --git a/lukhas/adapters/openai/api.py b/lukhas/adapters/openai/api.py
--- a/lukhas/adapters/openai/api.py
+++ b/lukhas/adapters/openai/api.py
@@ -1,10 +1,20 @@
-from fastapi import FastAPI
+from fastapi import FastAPI, Request
+from fastapi import HTTPException  # noqa: F401  (used by callers; kept for API parity)
+from starlette.responses import JSONResponse
+from starlette.exceptions import HTTPException as StarletteHTTPException
@@
-def get_app() -> FastAPI:
-    app = FastAPI(
+def get_app() -> FastAPI:
+    app = FastAPI(
         title="LUKHAS OpenAI-Compatible API",
         version="0.9.0",
     )
+
+    # ---------- OpenAI-style error envelope normalizer ----------
+    OPENAI_ERROR_CODE_BY_STATUS = {
+        401: "invalid_api_key",
+        403: "authorization_error",
+        429: "rate_limit_exceeded",
+    }
+
+    def _trace_headers(request: Request) -> dict:
+        tid = getattr(getattr(request, "state", object()), "trace_id", None)
+        return {"X-Trace-Id": tid} if tid else {}
+
+    def _payload(code: str, message: str) -> dict:
+        return {"error": {"type": code, "message": message, "code": code}}
+
+    async def _http_exc_handler(request: Request, exc: StarletteHTTPException):
+        code = OPENAI_ERROR_CODE_BY_STATUS.get(exc.status_code, "http_error")
+        # Prefer explicit detail; fall back to canonical messages.
+        if exc.status_code == 401 and not (exc.detail or "").strip():
+            message = "Invalid authentication credentials"
+        elif exc.status_code == 403 and not (exc.detail or "").strip():
+            message = "Forbidden"
+        elif exc.status_code == 429 and not (exc.detail or "").strip():
+            message = "Rate limit exceeded"
+        else:
+            message = (exc.detail or "HTTP error")
+        return JSONResponse(
+            _payload(code, str(message)),
+            status_code=exc.status_code,
+            headers=_trace_headers(request),
+        )
+
+    async def _generic_exc_handler(request: Request, exc: Exception):
+        # Optionally log with your structured logger here.
+        return JSONResponse(
+            _payload("internal_error", "Internal server error"),
+            status_code=500,
+            headers=_trace_headers(request),
+        )
+
+    app.add_exception_handler(StarletteHTTPException, _http_exc_handler)
+    app.add_exception_handler(Exception, _generic_exc_handler)
+    # ---------- /OpenAI-style error envelope normalizer ----------
@@
     return app
PATCH
```

> **Why this fixes failures:**
> Your failing smoke tests expected `"error.type"` to be present for 401/403/500. These handlers guarantee it, and also propagate `X-Trace-Id` so trace tests pass even on error paths.

---

### 2) Ruff: focus on prod lanes & allow idiomatic re-exports

This keeps Ruff strict on `lukhas/`, `core/`, `MATRIZ/`, ignores `labs/`, and allows `TID252`/`F401` in `__init__.py` only (documented).

> If your Ruff config already lives in `pyproject.toml` (likely), this **appends** safe sections. If you prefer a separate file, create `ruff.toml` instead with the same contents.

```bash
git apply -p0 <<'PATCH'
diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@
 [tool.ruff]
+target-version = "py39"
+line-length = 100
+# Limit lint scope to production lanes. Labs/dev content stays out of the gate.
+src = ["lukhas", "core", "MATRIZ"]
+extend-exclude = [
+  "labs",
+  "examples",
+  "docs",
+  "tests/fixtures",
+  "scripts/migrations",
+]
+select = ["E", "F", "W", "I", "ARG", "TID", "RUF"]
+# We allow TID252/F401 only in __init__.py where explicit, documented re-exports are idiomatic.
+
+[tool.ruff.lint.per-file-ignores]
+"**/__init__.py" = ["TID252", "F401"]
PATCH
```

---

### Quick verify (local)

```bash
# From repo root:
python3 -m ruff check lukhas core MATRIZ --statistics
python3 -m ruff check lukhas core MATRIZ --fix

export LUKHAS_POLICY_MODE=permissive
pytest tests/smoke/test_auth.py -q
pytest tests/smoke/test_error_handling.py -q
pytest tests/smoke/test_trace_header.py -q
```

You should see the auth/trace error-shape assertions flip to green.

---

### (Optional) tiny follow-ups Claude/Codex can tack on

* **Auth dependency returns**: make sure any explicit 401/403 raised in `auth.py` use `HTTPException(status_code=..., detail="…")`; the handler will wrap them properly.
* **429 paths**: ensure your rate limiter raises `HTTPException(status_code=429, detail="Rate limit exceeded")` so the handler emits `"rate_limit_exceeded"`.

Following with **three-test microfile** that asserts the envelope for 401/403/500 without relying on other app code.

These self-contained tests now. they exercise the **real app** (`get_app()`), but mount three throwaway routes just for testing, so we validate your OpenAI-style error envelope and `X-Trace-Id` passthrough **without depending on other app behavior**.

### 🧪 Add 3 minimal envelope tests (401/403/500)

```bash
git apply -p0 <<'PATCH'
diff --git a/tests/smoke/test_error_envelope_minimal.py b/tests/smoke/test_error_envelope_minimal.py
new file mode 100644
--- /dev/null
+++ b/tests/smoke/test_error_envelope_minimal.py
@@
+import re
+from fastapi import HTTPException
+from fastapi.testclient import TestClient
+
+# Use the real app so we exercise the exception handlers you registered in get_app().
+from lukhas.adapters.openai.api import get_app
+
+HEX32 = re.compile(r"^[0-9a-f]{32}$")
+
+
+def make_app():
+    """
+    Build a test instance of the real app and add three throw routes that
+    intentionally raise HTTP errors, so we can assert the OpenAI-style
+    error envelope and X-Trace-Id passthrough without relying on other endpoints.
+    """
+    app = get_app()
+
+    @app.get("/__test__/401")
+    def _t401():
+        # Explicit detail mirrors what your auth layer would normally produce.
+        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
+
+    @app.get("/__test__/403")
+    def _t403():
+        raise HTTPException(status_code=403, detail="Forbidden")
+
+    @app.get("/__test__/500")
+    def _t500():
+        # Any unhandled exception should be normalized to internal_error by the generic handler.
+        raise RuntimeError("boom")
+
+    return app
+
+
+def _assert_envelope(resp, expected_code: str):
+    data = resp.json()
+    assert "error" in data, f"missing error envelope: {data}"
+    err = data["error"]
+    for key in ("type", "message", "code"):
+        assert key in err, f"missing '{key}' in error: {err}"
+    assert err["code"] == expected_code, f"expected '{expected_code}', got '{err['code']}'"
+    # If your TraceHeaderMiddleware is active, we should see a W3C-style 32-hex trace id.
+    trace_id = resp.headers.get("X-Trace-Id")
+    if trace_id:
+        assert HEX32.match(trace_id), f"X-Trace-Id not hex32: {trace_id}"
+
+
+def test_envelope_401_minimal():
+    client = TestClient(make_app())
+    r = client.get("/__test__/401")
+    assert r.status_code == 401
+    _assert_envelope(r, "invalid_api_key")
+
+
+def test_envelope_403_minimal():
+    client = TestClient(make_app())
+    r = client.get("/__test__/403")
+    assert r.status_code == 403
+    _assert_envelope(r, "authorization_error")
+
+
+def test_envelope_500_minimal():
+    client = TestClient(make_app())
+    r = client.get("/__test__/500")
+    assert r.status_code == 500
+    _assert_envelope(r, "internal_error")
PATCH
```

### quick sanity run (locally)

```bash
# these don’t change your app; they only add tests.
pytest tests/smoke/test_error_envelope_minimal.py -q
```



