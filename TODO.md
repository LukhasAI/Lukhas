
# CLAUDE CODE HANDOFF — T4 / 0.01% TODO

## 1) Registry & Lane Isolation (Day 0)

**Goals:** eliminate dynamic cross-lane imports; make plugin wiring constructor-aware and observable.

* [ ] **Finish auto-wiring via registry**

  * Use `auto_discover()` at service boot when `LUKHAS_PLUGIN_DISCOVERY=auto`.
  * Replace any `importlib.import_module("candidate.*")` with `resolve("…")`.
  * **DoD:** `pytest -q tests/ast/test_no_importlib_outside_allowed.py` → green; `/_system/plugins` shows all required kinds loaded.

* [ ] **Constructor-aware instantiation (already drafted)**

  * Ensure `_instantiate_plugin(ep_name, klass)` tries factory classmethods, falls back to ctor signature, else registers class as factory.
  * **DoD:** `tests/unit/test_entry_points_smoke.py` (no mocks) passes; logs show which factory path used.

* [ ] **Status endpoint for ops**

  * Add `/system/plugins` returning `{"registered": list(_REG.keys())}`.
  * **DoD:** `curl /system/plugins | jq .registered | wc -l` > 0 in canary.

**Drop-in:** per-kind registration (inside discovery)

```python
# lukhas/core/registry.py
def _register_kind(group, name, obj):
    prefix = {
        "lukhas.cognitive_nodes": "node",
        "lukhas.constellation_components": "constellation",
        "lukhas.adapters": "adapter",
        "lukhas.monitoring": "monitor",
    }[group]
    register(f"{prefix}:{name}", obj)
```

---

## 2) MATRIZ Orchestrator Hardening

**Goals:** predictable latency; robust failure semantics; better node selection.

* [ ] **Per-stage timeouts + fail-soft**

  * Wrap stage invocations with `asyncio.wait_for`.
  * On timeout/Exception: record span event, continue if stage marked non-critical.
  * **DoD:** new tests under `tests/integration/test_orchestrator_timeouts.py` prove no pipeline crash; budget enforced.

**Drop-in:** timeout wrapper

```python
async def run_with_timeout(coro, stage, sec):
    try:
        return await asyncio.wait_for(coro, timeout=sec)
    except Exception as e:
        metrics.counter("matriz_stage_fail_total", {"stage": stage, "type": type(e).__name__}).inc()
        trace.get_current_span().add_event("stage_error", {"stage": stage, "error": str(e)})
        return {"_stage_error": True, "stage": stage, "error": str(e)}
```

* [ ] **Adaptive node selection**

  * Replace placeholder routing with a simple heuristic: prefer nodes with recent success + low p95; fallback to round-robin.
  * **DoD:** unit test injects two nodes (fast/slow); router picks fast ≥80% under load.

---

## 3) Memory System Refinement

**Goals:** fast, relevant recall; safe consolidation.

* [ ] **Top-K adaptive recall**

  * If `context_len > X` or `candidates > KMAX`, fetch top-K by relevance (embedding or scoring hook).
  * **DoD:** `tests/memory/test_topk_recall.py` proves ≤100ms median for 10k items (use fake store).

* [ ] **Scheduled folding**

  * Background task consolidates every N ops or when size > threshold.
  * **DoD:** `tests/memory/test_folding_trigger.py` shows fold invoked; size reduced; invariants hold.

---

## 4) Observability (OTel + Prometheus)

**Goals:** first-class tracing; Matriz metrics; budgets tracked.

* [ ] **Stage spans**

  * Create a parent trace per query; child spans: `memory`, `attention`, `thought`, `action`, `decision`, `awareness`.
  * **DoD:** `otelcol` receives spans; Grafana panel shows per-stage latency.

**Drop-in:** span helper

```python
from opentelemetry import trace
tracer = trace.get_tracer("lukhas.matriz")

async def run_stage(stage_name, fn, **kw):
    with tracer.start_as_current_span(f"stage.{stage_name}") as sp:
        sp.set_attribute("matriz.stage", stage_name)
        t0 = time.perf_counter()
        res = await fn(**kw)
        sp.set_attribute("matriz.duration_ms", (time.perf_counter()-t0)*1000)
        return res
```

* [ ] **Metrics**

  * Counters: `matriz_stage_total{stage}`, `matriz_stage_fail_total{stage,type}`.
  * Histograms: `matriz_stage_duration_seconds{stage}`; `matriz_end_to_end_seconds`.
  * **DoD:** PromQL panels render; SLO alerts wired (p95 < target).

---

## 5) Security & Supply Chain

**Goals:** reproducible env; no secrets; vulnerability visibility.

* [ ] **Pin & lock**

  * Add `requirements.in` → `requirements.txt` via pip-tools, commit lock.
  * **DoD:** CI uses locked deps; `pip install -r requirements.txt` on clean venv works.

* [ ] **pip-audit in CI**

  * Fail on critical vulnerabilities.
  * **DoD:** GH Actions job `security-audit` green; known issues triaged.

* [ ] **Secret rotation & scanners**

  * Rotate any flagged keys; enable `gitleaks`/GH secret scanning on push.
  * **DoD:** “secrets present” dashboards = 0; rotation notes in runbook.

---

## 6) Naming & Docs Consistency

**Goals:** one vocabulary; zero cognitive friction.

* [ ] **Constellation vs Constellation**

  * Pick “Constellation”; search-replace code/docs; keep minimal shims with deprecation notice.
  * **DoD:** `grep -R "Constellation" -n | wc -l` → 0 (outside archive/notes).

* [ ] **Cognitive AI → AI / cognitive**

  * Rename `cognitive_*` where still active; add 1-release alias if needed.
  * **DoD:** import graph has no `cognitive_` outside compat; CI legacy-guard passes.

* [ ] **Context files sync**

  * Apply v2 template to top-level `claude.me` / `lukhas_context.md` (lanes, schema v2.0.0, 692 components).
  * **DoD:** `scripts/context_updater.py --check` → clean.

---

## 7) Test Strategy Upgrades

**Goals:** zero-regression; resilience proven; budgets locked.

* [ ] **E2E MATRIZ loop**

  * Golden-path test drives full pipeline; asserts trace shape + outputs.
  * **DoD:** `tests/e2e/test_matriz_pipeline.py` green; saved golden trace schema.

* [ ] **Chaos / fault injection**

  * Tests for timeouts, partial store failures, slow node; orchestrator degrades gracefully.
  * **DoD:** all chaos tests pass; no unhandled exceptions.

* [ ] **Performance budgets**

  * `pytest-benchmark` or lightweight timing asserts: per-stage p95 and end-to-end SLO.
  * **DoD:** `LUKHAS_PERF=1 pytest -q tests/perf` passes; thresholds versioned.

* [ ] **Coverage diff gate**

  * Fail PRs that decrease coverage or add untested paths in core/orchestrator/memory.
  * **DoD:** action enforces ≥ current baseline.

---

## 8) CI/CD Enhancements

**Goals:** keep the bar high; detect drift early.

* [ ] **Plugin discovery in CI**

  * Boot app with `LUKHAS_PLUGIN_DISCOVERY=auto` and assert minimal plugin set present.
  * **DoD:** `make ci-smoke-plugin` target passes.

* [ ] **Lane guard (already on) + report**

  * Emit a lane-violation summary artifact for PRs (even when zero).
  * **DoD:** artifact attached to PR; zero by default.

---

## 9) Lane Assignment Readiness (quick pass)

**Promote now:** Core, Memory, Identity, Governance/Guardian.
**Gate on tests/metrics:** Orchestrator routing & Thought/Action nodes.
**Keep in candidate:** Vivox, advanced/experimental stars, heavy adapters.

**Minimal promotion criteria (per module):**

* ✔ Interface stable + covered (≥90% module coverage)
* ✔ Observability (spans + metrics) present
* ✔ p95 ≤ budget under CI perf mode
* ✔ No cross-lane imports; registry-loaded
* ✔ Rollback flag present

---

### Helpful run commands (pasteable)

```bash
# Plugin smoke + no shims
LUKHAS_PLUGIN_DISCOVERY=auto pytest -q tests/unit/test_entry_points_smoke.py

# Orchestrator timeouts & chaos
pytest -q tests/integration/test_orchestrator_timeouts.py tests/integration/test_orchestrator_chaos.py

# Perf budgets
LUKHAS_PERF=1 pytest -q tests/perf

# Coverage diff (example)
pytest --cov=lukhas --cov-fail-under=$(cat .ci/coverage_baseline)

# Security
pip-compile -q requirements.in && pip-audit -r requirements.txt
```
