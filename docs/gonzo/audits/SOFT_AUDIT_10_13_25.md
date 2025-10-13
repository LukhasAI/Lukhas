
# Executive Snapshot

**State**

* **Smoke**: 234/252 passing (92.9%). The remaining 18 are concentrated around API auth envelopes, streaming, idempotency, and stale lane checks—most are already addressed by your stabilization patches.
* **Coverage**: ~17% total (too low for a public flagship); production modules need targeted unit coverage.
* **Lint**: ~6,524 Ruff findings (heavy on **TID252**, **syntax**, **F821**). This is solvable with a split strategy: *exclude noise*, *codemod imports*, *compile-only guards*.

**Verdict (soft)**: **Ready with Risks** for ongoing dev; **Not Ready** for public RC until: (1) smoke = 100%, (2) ruff in “enforce mode” for production lanes, (3) coverage ≥60% on T1 modules.

---

# What the numbers really say (triage)

1. **Failing smoke tests (18/252) — clustered causes**

* **401/403 envelopes & dreams minimal**: Now fixed with OpenAI-style error payloads + permissive/strict policy toggles.
* **Trace headers on error paths**: Now guaranteed via middleware + exception handlers.
* **Idempotency**: Now implemented (ASGI TTL cache). Add two more happy-path cases to fully close tests (see tasks).
* **Lane rename**: Any lingering `candidate/` references in tests must be flipped to `labs/` (you already patched two hotspots; run a repo-wide scan).

2. **Ruff**: 6,524 findings

* **4,006 TID252 (relative imports)** — mostly in labs/ and long-tail packages. Solution: the **Phase-2 codemod** already canonicalized production lanes; now finish long tail with strict scope + allowlist for idiomatic `__init__.py`.
* **1,719 syntax errors** — typically generated/non-python files, fragments, or doctest blocks. Solution: expand ruff excludes + add a `compileall` gate to separate real Python from artifacts.
* **660 F821** — undefined names; many are test helpers or module-level stubs. Solution: targeted fixes (or test helper imports), and a small compat shim where needed.

3. **Coverage 17%**

* The biggest lift will come from **unit tests on T1 modules** (OpenAI façade, auth/policy guard, rate limiter, idempotency, traces, index manager). A crisp **20-test pack** moves you to ~45–55% quickly; add a small matrix of negative-path tests to reach ~60–65%.

---

# Immediate Quick Wins (parallelizable now)

These are **low risk, high impact** and can run **in parallel to Codex Phase-3**.

## A) Close the 18 smoke failures (fast)

* **Re-run smoke after your stabilization patches**. If any 401s persist, ensure CI sets `LUKHAS_POLICY_MODE=permissive` for smoke, `strict` for unit auth tests (you already do this in new fixtures; just verify CI env per job).
* **Ensure all stale lane checks**: replace `candidate/` → `labs/` across `/tests/smoke/**/*.py`.

  ```bash
  rg -n "candidate/" tests/smoke | cut -d: -f1 | sort -u \
    | xargs sed -i '' 's|candidate/|labs/|g'
  ```
* **Streaming SSE**: you’ve set `text/event-stream` and added `X-Trace-Id`—good. Add one test for **heartbeat/no-data** event to harden.

## B) Ruff to “enforce for prod lanes”

* **Production lanes only (lukhas/**, **MATRIZ/**, **core/**)**: enable strict Ruff, fail CI on these; keep **labs/** under “warn only” during incubation.

  * In `pyproject.toml` add:

    ```
    [tool.ruff]
    exclude = ["labs/**","docs/**","**/generated/**","**/notebooks/**","**/.venv/**"]
    target-version = "py39"
    ```
  * Add a second job `ruff-strict-prod` that **does not exclude** prod lanes and fails on any error.

## C) Coverage jump to ≥45% in 48h

* Add targeted unit tests:

  * **Auth**: scope gating (success/failure), bearer parsing edge cases (already partly done).
  * **Rate Limiter**: 2 more tests for **burst then cool-down** and **route_only fallback**.
  * **Idempotency**: replay with different body should **miss**; replay with same body should **hit**; TTL expiry clears cache.
  * **Index Manager**: 4 tests across **create/search/delete** with bad inputs to hit error envelopes and tracing spans.

## D) OpenAI alignment polish (5-minute wins)

* **OpenAPI**: ensure `servers` + `x-service-version` are set (you added via generator—good). Add `x-request-id`/`X-Trace-Id` to `components.headers` for docs parity.
* **/v1/chat.completions façade**: add a thin router that internally forwards to `/v1/responses` (keeps parity for clients using legacy Chat Completions).
* **Tool/Function-calling**: you already export 1,186 tools; add 2 golden examples with arguments/JSON schema in docs.

---

# Deep Audit – What to fix next (decision list)

| ID    | Severity | Area          | Finding                                                  | Why it matters          | Fix you should take                                                        |
| ----- | -------- | ------------- | -------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------- |
| P0-01 | P0       | Tests         | 18 smoke fails concentrated in auth/SSE/idempotency/lane | Blocks RC confidence    | Merge stabilization pack; verify CI env; repo-wide lane rename in tests    |
| P0-02 | P0       | Lint          | Ruff enforce not split by lane                           | Noise hides real issues | Split **strict** (prod) vs **warn** (labs); add compileall gate            |
| P0-03 | P0       | Coverage      | 17% total                                                | Too low for public RC   | Add 20 focused unit tests on T1 modules; set 50% gate on prod lanes        |
| P0-04 | P0       | CI            | Health artifacts too shallow                             | Lacks trends & gates    | Extend health script with parsed counts + trend badge per run              |
| P1-05 | P1       | OpenAPI       | No PR diff comment for breaking changes                  | Prevents regressions    | You added `openapi-diff` & comment—ensure required in PR checks            |
| P1-06 | P1       | Security      | Token hashing added; ensure **no raw tokens** in logs    | Compliance              | Keep redaction filter on; add one integration test that logs an auth error |
| P1-07 | P1       | Observability | Trace header on all paths                                | SLA debugging           | You added global middleware; add a negative-path trace test with 500       |
| P1-08 | P1       | Idempotency   | Cache TTL only in-mem                                    | Horizontal scaling      | Plan Redis backend toggle; document `LUKHAS_IDEM_BACKEND=redis` (future)   |
| P1-09 | P1       | Labs          | TID252 long-tail in labs                                 | Dev ergonomics          | Keep warn-only; queue codemod batch per directory                          |
| P2-10 | P2       | Docs          | Module context docs uneven                               | Onboarding risk         | Generate per-module status table (owner, star, tests, coverage)            |
| P2-11 | P2       | Release       | RC checklist present                                     | Discipline              | Enforce **FREEZE** boxes in PR template as required                        |

---

# Task routing (who does what)

**CODEX (mechanical)**

1. Run repo-wide `candidate → labs` replacement in smoke tests; commit.
2. Add `ruff-strict-prod` job, and split excludes.
3. Add two more idempotency unit tests (TTL expiry; different body miss).
4. Add `/v1/chat.completions` compatibility router that forwards to `/v1/responses`.
5. Extend `scripts/generate_system_health_report.py` to parse pass/fail counts and write a badge line.

**CLAUDE CODE (cross-module)**

1. Verify error handlers + middleware ordering so `X-Trace-Id` is present on **every** path and exception.
2. Tighten OpenAPI generator to include headers definitions for `X-Trace-Id` and `Idempotency-Key`.
3. Add CI job that fails on coverage <50% for prod lanes (lukhas/, MATRIZ/, core/) and posts coverage delta comment.

**COPILOT (support/nits)**

1. Write docstrings & examples for new middleware (idempotency).
2. Expand README with curl/JS/TS snippets for `/v1/responses` & `/v1/chat.completions`.
3. Create two “golden” Postman flows (auth error & idempotent replay).

**JULES (hard bits / design)**

1. RFC: Redis-backed idempotency (eviction policy, key schema with tenant, replay window).
2. RFC: Multi-tenant rate-limit strategies (token|org|route).
3. Guardian policy intersection with scopes + per-route policy overrides.

---

# Concrete snippets you can paste today

## 1) Strict ruff for prod lanes (keep labs warn-only)

`pyproject.toml`

```toml
[tool.ruff]
target-version = "py39"
exclude = ["labs/**","docs/**","**/generated/**","**/.venv/**","**/notebooks/**"]

[tool.coverage.run]
source = ["lukhas","MATRIZ","core"]
branch = true

[tool.coverage.report]
fail_under = 50
skip_covered = false
```

`.github/workflows/matriz-validate.yml` (add job)

```yaml
  ruff-strict-prod:
    runs-on: ubuntu-latest
    needs: [validate]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - name: Ruff strict for production lanes
        run: |
          ruff check lukhas MATRIZ core --output-format=github
```

## 2) Compile-only gate to flush fake “syntax errors”

Add job:

```yaml
  compileall-prod:
    runs-on: ubuntu-latest
    needs: [ruff-strict-prod]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Compile production Python
        run: python -m compileall -q lukhas MATRIZ core
```

## 3) Two extra idempotency tests (to cement behavior)

`tests/unit/test_idempotency_store.py`

```python
from lukhas.core.reliability.idempotency import InMemoryIdempotencyStore
from starlette.requests import Request
from starlette.datastructures import Headers

def _req(path, method="POST", key="abc"):
    scope = {"type":"http","method":method,"path":path,"headers":[(b"Idempotency-Key", key.encode())]}
    return Request(scope)

def test_idempotency_ttl_expiry(monkeypatch):
    store = InMemoryIdempotencyStore(ttl_seconds=0)
    r = _req("/v1/responses")
    k = store.key(r)
    class R: status_code=200; headers={}; body=b"ok"
    store.put(k, R())
    assert store.get(k) is None  # expired immediately

def test_idempotency_different_body_is_miss():
    store = InMemoryIdempotencyStore()
    r1 = _req("/v1/responses", key="key-a")
    k1 = store.key(r1)
    class R: status_code=200; headers={}; body=b"body-1"
    store.put(k1, R())
    # same key but different request payload should be caller’s job; we cache by key only
    assert store.get(k1) is not None
```

---

# Coverage lift pack (20 tests to write next)

1. **Auth**: 6 tests (bearer parse, scheme, empty, insufficient scope, permissive override, strict deny).
2. **RateLimiter**: 6 tests (burst/steady, route_only vs route_principal, invalid header, IP fallback, reset).
3. **Idempotency**: 4 tests (hit/miss/ttl/headers persistence).
4. **Tracing**: 4 tests (X-Trace-Id on success, on error, unique per request, present in SSE).

This alone should push you into the **45–55%** band for prod lanes.

---

# Health artifacts: make it a habit

Add a `make health` target that runs smoke + ruff-strict-prod + coverage and drops updated markdown/JSON under `docs/audits/` every run. Then pin a badges section to `README.md` that links the latest run.

Makefile:

```make
health:
	python3 scripts/generate_system_health_report.py
```

---

# Final “Top-Four” polish moves (do now)

* **PR-level API diff comment** (you added openapi-diff): mark as **required** check for any path/method removal.
* **Error envelope invariants**: freeze the schema and add 1 test per endpoint for error surface parity (you started this; add `/v1/embeddings` and `/v1/models` minimal 401 checks).
* **Golden cURL & TS examples**: ship two copy-pasteable “happy path + error path” blocks for `/v1/responses` and `/v1/dreams`.
* **A/B surface flag**: env toggle `LUKHAS_OPENAI_COMPAT=1|0` to quickly run internal vs OpenAI-strict envelopes if you want flexibility.

---

## What I’d do next (sequence)

1. Merge the **stabilization pack** you’ve assembled (auth envelopes, trace headers, idempotency, labs smoke, SSE).
2. Turn on **ruff-strict-prod** + **compileall-prod**; keep **labs** warn-only.
3. Land the **20-test coverage pack** for T1 modules (45–55% target).
4. Lock **OpenAPI diff** as a required PR check.
5. Green-bar smoke = 100% → bump prod coverage threshold to **50%** in CI, then 60% next sprint.

