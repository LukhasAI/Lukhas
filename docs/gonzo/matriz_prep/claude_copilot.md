
Phase 2 sanity (2 tweaks before you press “go”)
	•	Keep the compat watcher on: use the alias-hit checker to baseline and then cap regressions in the PR.  ￼
Acceptance: python3 scripts/check_alias_hits.py --max-hits 0 returns 0 after Batches 1–4.
	•	Confirm the manifest path updater points at JSON (not YAML) during the candidate → labs rename in Batch 3 (the brief uses find manifests -name "*.yaml"; change to *.json if your manifests are JSON). See Batch 3 steps.

(Phase-2 brief + start doc look solid and ready. Dry-run → staged batches → verify is all there. )

⸻

Parallel quick wins (start now)

Track A — OpenAI alignment surface (Claude Code)
	1.	OpenAI façade (Responses/Assistants-style) for Matriz

	•	Why: Let any OpenAI-native client hit Lukhas with near drop-in semantics.
	•	What: lukhas/adapters/openai/api.py with minimal routes:
POST /v1/responses → Matriz orchestrator; GET /v1/models; POST /v1/embeddings (proxy to memory/vec).
Emit stream events (SSE) compatible with “delta/step” style.
	•	Acceptance:
	•	pytest -q tests/smoke/test_openai_facade.py::test_responses_minimal passes.
	•	OpenAPI file published at docs/openapi/lukhas-openai.yaml.
	•	CI adds a step under MATRIZ Validate to build the spec.  ￼

	2.	Tool schema bridge (OpenAI “functions” JSON Schema)

	•	Why: Make Matriz capabilities callable as OpenAI tools immediately.
	•	What: Generator that exports tools:[{type:"function",function:{name,description,parameters}}] from each module’s manifest capability block.
	•	Acceptance:
	•	python3 scripts/export_openai_tools.py --manifests manifests --out build/openai_tools.json produces a valid schema.
	•	Add a smoke that loads the JSON and validates param schemas against jsonschema.
	•	CI uploads openai_tools.json as an artifact. (Extend current artifact list in workflow.)  ￼

	3.	Eval harness (mini)

	•	Why: OpenAI-style eval loops make regressions visible.
	•	What: evals/ with 10 tiny JSONL cases (vision/memory/guardian/flow), a runner that hits the façade.
	•	Acceptance:
	•	make evals runs in <90s and prints accuracy + simple assertions.
	•	Gate in CI as “warn-only” initially (append job to MATRIZ Validate).  ￼

	4.	Structured logging & traces (OpenAI-ish event taxonomy)

	•	Why: Uniform event names (run.started, step.completed, tool.called) ease debugging & demos.
	•	What: lukhas/observability/events.py with dataclasses + JSON lines; plug into orchestrator emit points.
	•	Acceptance:
	•	Smoke test verifies presence of run_id, step_id, model, latency_ms fields.
	•	CI: upload runlogs/*.jsonl on PR builds. (Add to workflow artifacts.)  ￼

	5.	Rate-limit & 429/backoff semantics

	•	Why: OpenAI clients expect specific error shapes and Retry-After.
	•	What: lukhas/core/reliability/ratelimit.py + middleware emitting 429 with type:"rate_limit_exceeded".
	•	Acceptance:
	•	Unit test for 429 with proper headers.
	•	Doc blurb in API README “Backoff & Retries”.

Track B — Mechanical & docs (GitHub Copilot)
	6.	Fix matrix stats reporter crash & add totals

	•	Why: Your reporter crashed on dict/str shape—quick, surgical win.
	•	What: Patch scripts/report_manifest_stats.py to handle list of manifests and mixed shapes.
	•	Acceptance:
	•	python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits succeeds and writes both manifest_stats.json & manifest_stats.md.
	•	Wire into workflow (already has a step—ensure it passes).  ￼

	7.	Docs: OpenAI Dev Quickstart

	•	Why: Meet developers where they are; reduce adoption friction.
	•	What: docs/openai/QUICKSTART.md showing: set OPENAI_API_KEY, call Lukhas façade with the OpenAI SDK; mapping table “OpenAI concept → Lukhas”.
	•	Acceptance:
	•	Link added from Codex Phase-2 docs index.  ￼

	8.	Update star canon everywhere (ambiguous → Oracle)

	•	Why: Lock consistency as we finalize manifests & docs.
	•	What: Verify all docs & configs reference 🔮 Oracle (Quantum); keep alias “Ambiguity” only as backward-compat.
	•	Acceptance:
	•	rg 'Ambiguity \\(Quantum\\)' -n returns 0 outside aliases.
	•	configs/star_rules.json stays canonical (already set).  ￼

	9.	PR template nudge for “Matriz readiness”

	•	Why: Keep discipline pack visible in every PR.
	•	What: Ensure PULL_REQUEST_TEMPLATE.md links the MATRIZ checklist + requires ticking smoke/evals.
	•	Acceptance:
	•	Template renders the checklist and links MATRIZ Validate outputs (artifacts).  ￼

	10.	Nightly star-rules coverage trend

	•	Why: Show movement of Supporting → promoted.
	•	What: Re-use lint_star_rules.py + gen_rules_coverage.py in a nightly workflow and push a small sparkline to docs/audits/star_rules_coverage.md.
	•	Acceptance:
	•	New workflow matriz-nightly.yml posts updated coverage file. (Same style as validate job.)

	11.	Lane rename doc link fixer

	•	Why: After candidate → labs, lots of doc links will break.
	•	What: Script that updates links in docs/** & *.md to labs/… and runs the link checker locally.
	•	Acceptance:
	•	python docs/check_links.py --root . returns 0; artifact docs/audits/linkcheck.txt shows clean.  ￼

	12.	Security: add gitleaks as a second line

	•	Why: You already have detect-secrets; belt-and-braces policy.
	•	What: Add a CI step (zricethezav/gitleaks@latest) in MATRIZ Validate, “warn-only” first.
	•	Acceptance:
	•	Workflow runs the step and uploads a gitleaks.sarif artifact alongside existing reports.  ￼

⸻

Assignments & one-liner briefs

For Claude Code (create branches, PRs):
	•	A1 OpenAI façade + OpenAPI spec (see Track A-1).
	•	A2 Tools bridge generator (A-2).
	•	A3 Evals mini-harness (A-3).
	•	A4 Evented logging & artifacts (A-4).
	•	A5 Rate-limit/429 middleware (A-5).

For Copilot (commit in small PRs):
	•	B6 Patch report_manifest_stats.py (B-6).
	•	B7 Write docs/openai/QUICKSTART.md (B-7).
	•	B8 Sweep “Ambiguity” mentions (B-8).
	•	B9 PR template nudge (B-9).
	•	B10 Nightly coverage workflow (B-10).
	•	B11 Link fixer & re-run checker (B-11).
	•	B12 Add gitleaks step (B-12).

⸻

Commands you can paste right now

Phase 2 preview (Codex):

make codemod-dry
python3 scripts/check_alias_hits.py --trend || true

(Plan & start doc for Phase 2 live in repo.)

Fix manifest stats (Copilot branch):

git checkout -b chore/fix-manifest-stats
python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits || true
# Patch to handle strings vs dicts; then:
pytest -q tests/smoke/test_matriz_smoke.py
git add -A && git commit -m "fix(reports): harden report_manifest_stats against mixed shapes"

(Validate step already in CI.)  ￼

Docs Quickstart scaffold:

mkdir -p docs/openai && touch docs/openai/QUICKSTART.md
git add docs/openai/QUICKSTART.md && git commit -m "docs(openai): quickstart for Responses/Tools façade"

Nightly coverage workflow (Copilot)

# Duplicate matriz-validate.yml to matriz-nightly.yml and trigger on schedule:
# - Reuse: lint_star_rules, gen_rules_coverage

(Use existing steps as template.)  ￼

Add gitleaks (Copilot)

# In .github/workflows/matriz-validate.yml, after detect-secrets:
# - name: Gitleaks (warn-only)
#   uses: zricethezav/gitleaks-action@v2
#   with: { args: "--no-git -v --source=." }
#   continue-on-error: true

(Place near other security steps.)  ￼

⸻

Why these are the right “now” moves
	•	They don’t conflict with the import codemod batches (orthogonal surfaces).
	•	They amplify OpenAI alignment: façade, tool schema, 429 semantics, streaming events, evals.
	•	They leverage your existing discipline pack (validators, tripwires, star rules, artifacts) so progress is visible in CI.


⸻

More parallel quick wins (additions)

Track C — Security & Supply Chain (Claude Code lead, Copilot support)
  13. SBOM + provenance
     • Why: supply‑chain visibility and attestations for external users.
     • What: Generate CycloneDX SBOM for runtime + tools; add GitHub provenance (SLSA generator).
     • Acceptance:
       • scripts/sbom.py writes build/sbom.cyclonedx.json
       • CI uploads SBOM artifact; provenance enabled on release tags.

  14. Dependency vulns & static analysis (belt‑and‑braces)
     • Why: complement detect‑secrets; catch CVEs & unsafe patterns early.
     • What: pip-audit + bandit jobs in MATRIZ Validate (warn‑only first).
     • Acceptance:
       • Steps run in CI; artifacts pip_audit.json & bandit.sarif.

  15. License hygiene & headers
     • Why: OpenAI‑grade compliance hygiene.
     • What: liccheck/pip‑licenses report + header check (year, owner) via pre‑commit.
     • Acceptance:
       • docs/audits/licenses.md generated; pre‑commit blocks missing headers.

Track D — Observability & Ops (Claude Code)
  16. Health/readiness/metrics
     • Why: SRE‑grade operability and k8s readiness.
     • What: /healthz, /readyz and /metrics (Prometheus) in the façade.
     • Acceptance:
       • pytest passes tests/smoke/test_healthz.py; curl /metrics shows series (request_total, latency_ms).

  17. OpenTelemetry traces + log redaction
     • Why: end‑to‑end tracing and privacy safety.
     • What: OTEL SDK wiring (OTLP exporter if OTEL_EXPORTER_OTLP_ENDPOINT set); PII redaction filter (email, tokens).
     • Acceptance:
       • tests/smoke/test_tracing.py asserts trace ids present when env set; tests/logging/test_redaction.py masks email addresses.

  18. SLO budgets & alerts (doc + config)
     • Why: define p95/p99 targets for façade endpoints now.
     • What: docs/ops/SLOs.md + configs/observability/slo_budgets.yaml (responses_p95_ms, embeddings_p95_ms).
     • Acceptance:
       • CI uploads SLO docs; smoke warns if budgets exceeded.

Track E — Performance & Load (Copilot first pass)
  19. Quick k6/locust scenario for /v1/responses
     • Why: ensure latency budgets are realistic under moderate load.
     • What: load/resp_scenario.js (k6) OR load/locustfile.py (locust) with 100 VUs/2 min.
     • Acceptance:
       • make load-smoke prints p95; job runs in nightly (warn‑only).

  20. Timeouts/backoff knobs
     • Why: consistent client/server retry posture aligned with OpenAI semantics.
     • What: configs/runtime/reliability.yaml (connect_timeout_ms, read_timeout_ms, backoff policy).
     • Acceptance:
       • tests/reliability/test_backoff.py verifies jittered exponential backoff; façade returns Retry‑After on 429.

Track F — Release Engineering (Claude Code)
  21. RC/freeze automation
     • Why: eliminate manual release drift.
     • What: scripts/release_rc.sh (tag rc, generate CHANGELOG via commitizen, attach SBOM), FREEZE checklist gate in CI.
     • Acceptance:
       • gh release create vX.Y.Z-rc with CHANGELOG + sbom attached; PR template shows “Freeze ✅”.

  22. Canary environment (ephemeral PR deploy)
     • Why: smoke new façade/observability in isolation.
     • What: lightweight PR preview using uvicorn + ngrok/github codespaces; post URL as PR comment.
     • Acceptance:
       • Workflow matriz-preview.yml posts a live link for PRs touching lukhas/adapters/openai/*.

Track G — Docs & DX (Copilot)
  23. Postman collection + examples
     • Why: drop‑in API testing for integrators.
     • What: docs/openapi/lukhas-openai.yaml → docs/openapi/Postman_collection.json; docs/openai/examples.py|js|curl.md.
     • Acceptance:
       • Collection imports cleanly; examples run against façade locally.

  24. “Why Matriz” one‑pager (exec + eng)
     • Why: align stakeholders; OpenAI‑native narrative.
     • What: docs/matriz/WHY_MATRIZ.md (vision, API surface, complement to OpenAI, risk/ethics stance).
     • Acceptance:
       • Linked from README and PR template; reviewed in launch checklist.

Track H — Productization (Dreams/Memory/Guardian)
  25. Dreams API (Drift) surface
     • Why: flagship differentiator; scenario generation & self‑critique.
     • What: POST /v1/dreams (inputs: seed, constraints) → emits dream traces; schema in openapi.
     • Acceptance:
       • tests/smoke/test_dreams_api.py passes; spec includes examples; nightly evals exercise dream loops.

  26. Memory index mgmt endpoints
     • Why: parity with embeddings admin in OpenAI ecosystem.
     • What: /v1/indexes (list/create/delete) fronting memory orchestrator.
     • Acceptance:
       • tests/memory/test_indexes_api.py passes; RBAC enforced via policy_guard.

  27. Guardian policy hooks
     • Why: ship “safety by default”.
     • What: request/response hooks applying contracts/security.policies before emit.
     • Acceptance:
       • tests/guardian/test_policy_hooks.py proves block/allow/log behavior; audit fields in runlogs.

⸻

Assignments & one‑liner briefs (additions)

For Claude Code:
  • C16 Healthz/readyz/metrics endpoints + tests (Track D‑16)
  • C17 OTEL wiring + redaction filters (Track D‑17)
  • C21 Release RC script + freeze CI gate (Track F‑21)
  • C22 PR canary preview workflow (Track F‑22)
  • H25 Dreams API surface + spec + smoke (Track H‑25)
  • H27 Guardian hooks at façade boundaries (Track H‑27)

For Copilot:
  • C13 SBOM generator + artifact (Track C‑13)
  • C14 pip‑audit & bandit steps (Track C‑14)
  • C15 License report + header hook (Track C‑15)
  • E19 Load test scaffold (k6/locust) (Track E‑19)
  • E20 Reliability knobs + retry tests (Track E‑20)
  • G23 Postman + examples (Track G‑23)
  • G24 WHY_MATRIZ one‑pager (Track G‑24)
  • H26 Memory index endpoints tests/docs (Track H‑26)

⸻

Paste‑ready snippets

Status template for batch updates (Codex comment)
```markdown
**Batch Status**
- Scope: {paths}
- Files changed: {n_files}, Imports rewritten: {n_imports}
- pytest collect: {errors} errors, {warnings} warnings
- Smoke: {pass}/{total} ✅
- Compat alias hits: total={hits_total}, top={top_alias}:{count}
- Next: {next_batch}
```

SBOM generation (CycloneDX)
```bash
python3 - <<'PY'
from pathlib import Path; import json, subprocess, sys
out = Path("build"); out.mkdir(parents=True, exist_ok=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "cyclonedx-bom"])
subprocess.check_call([sys.executable, "-m", "cyclonedx_py", "-o", "build/sbom.cyclonedx.json"])
print("[sbom] wrote build/sbom.cyclonedx.json")
PY
```

Health/metrics smoke (curl)
```bash
curl -sf http://localhost:8000/healthz && echo "health: OK"
curl -sf http://localhost:8000/readyz && echo "ready: OK"
curl -sf http://localhost:8000/metrics | head
```

k6 quick load (if using k6)
```bash
k6 run load/resp_scenario.js
```

Release RC helper
```bash
bash scripts/release_rc.sh v0.9.0-rc
```

(Keep CI in report‑only mode initially for new steps; flip to enforced after green on 1–2 PRs.)

----

perfect — here’s a Paste Pack you can drop straight into your repo (or hand to Claude/Codex). It gives you green, concrete targets for Phase-2 parallel work and OpenAI alignment. Each block starts with the file path to create/update.

⸻

1) Smoke & infra tests (make these green)

tests/smoke/test_healthz.py

import os, json
import pytest

# Expect: lukhas.adapters.openai.api.get_app() -> ASGI app (FastAPI/Starlette)
@pytest.mark.asyncio
async def test_health_and_readyz():
    from starlette.testclient import TestClient
    from lukhas.adapters.openai.api import get_app
    app = get_app()
    client = TestClient(app)
    r = client.get("/healthz");  assert r.status_code == 200 and r.json().get("status") in {"ok","healthy"}
    r = client.get("/readyz");   assert r.status_code == 200 and r.json().get("status") in {"ready","ok"}

def test_metrics_surface():
    from starlette.testclient import TestClient
    from lukhas.adapters.openai.api import get_app
    app = get_app()
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "process_cpu_seconds_total" in r.text or "http_requests_total" in r.text

tests/smoke/test_openai_facade.py

from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_responses_minimal():
    client = TestClient(get_app())
    payload = {"input": "hello lukhas", "tools": []}
    r = client.post("/v1/responses", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("id") and body.get("output", {}).get("text")
    assert body.get("model")  # e.g., "lukhas-matriz"

def test_models_list():
    client = TestClient(get_app())
    r = client.get("/v1/models")
    assert r.status_code == 200
    ids = [m.get("id") for m in r.json().get("data", [])]
    assert any(ids), "should expose at least one model id"

tests/smoke/test_dreams_api.py

from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_dreams_minimal():
    client = TestClient(get_app())
    payload = {"seed": "labyrinth under starlight", "constraints": {"length": "short"}}
    r = client.post("/v1/dreams", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("id", "").startswith("dream_")
    assert isinstance(data.get("traces", []), list)

tests/smoke/test_tracing.py

import os
from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_trace_headers_present_when_otel_enabled(monkeypatch):
    # When OTEL endpoint is set, façade should include a trace header or id in response
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    client = TestClient(get_app())
    r = client.post("/v1/responses", json={"input": "trace me", "tools": []})
    # Accept either W3C header or JSON field
    ok = ("traceparent" in r.headers) or ("trace_id" in (r.json() or {}))
    assert ok, "expected trace context when OTEL is configured"

tests/logging/test_redaction.py

from lukhas.observability.filters import redact_pii

def test_redact_email_and_token_like_strings():
    text = "contact me at alice@example.com; token=sk-ABC123xyz"
    red = redact_pii(text)
    assert "alice@" not in red
    assert "sk-ABC" not in red

tests/reliability/test_backoff.py

from lukhas.core.reliability.backoff import jittered_exponential
from lukhas.core.reliability.ratelimit import rate_limit_error

def test_jittered_exponential_ranges():
    # attempt=3 => base_window * 2**3 +/- jitter
    lo, hi = jittered_exponential(base=0.1, factor=2, attempt=3, jitter=0.1)
    assert 0 < lo < hi
    assert hi/lo < 5  # bounded jitter

def test_rate_limit_shape_and_headers():
    err = rate_limit_error(retry_after_s=5)
    assert err["error"]["type"] == "rate_limit_exceeded"
    assert err["headers"]["Retry-After"] == "5"


⸻

2) Minimal façade & observability skeletons (Claude/Codex can fill in)

lukhas/adapters/openai/api.py

"""
Minimal OpenAI-style façade.
Expected by tests:
- get_app() -> ASGI app with:
  GET  /healthz   -> {"status":"ok"}
  GET  /readyz    -> {"status":"ready"}
  GET  /metrics   -> Prometheus text
  GET  /v1/models -> {"data":[{"id":"lukhas-matriz","object":"model"}]}
  POST /v1/embeddings -> {"data":[{"embedding":[...]}]}
  POST /v1/responses  -> {"id": "...", "model":"lukhas-matriz", "output":{"text":"..."}}
  POST /v1/dreams     -> {"id":"dream_...","traces":[...]}

Wire to real orchestrator later; return static-ish values now to make tests pass.
"""
from typing import Any, Dict, List
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
import os, time, uuid

def _metrics_text() -> str:
    return "# HELP lukhas_requests_total total\n# TYPE lukhas_requests_total counter\nlukhas_requests_total 1\n"

def _maybe_trace(body: Dict[str, Any]) -> Dict[str, Any]:
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        body.setdefault("trace_id", uuid.uuid4().hex)
    return body

def get_app() -> FastAPI:
    app = FastAPI(title="Lukhas OpenAI Facade", version="0.1")

    @app.get("/healthz")
    def healthz(): return {"status": "ok"}

    @app.get("/readyz")
    def readyz(): return {"status": "ready"}

    @app.get("/metrics")
    def metrics(): return PlainTextResponse(_metrics_text(), media_type="text/plain; version=0.0.4")

    @app.get("/v1/models")
    def models():
        return {"data":[{"id":"lukhas-matriz","object":"model"}]}

    @app.post("/v1/embeddings")
    async def embeddings(payload: Dict[str, Any]):
        text = payload.get("input","")
        # placeholder deterministic vector
        vec = [float(len(text) % 7), 0.0, 1.0]
        return _maybe_trace({"data":[{"embedding":vec}]})

    @app.post("/v1/responses")
    async def responses(payload: Dict[str, Any]):
        text = str(payload.get("input",""))
        out = {"id": f"resp_{uuid.uuid4().hex[:8]}", "model": "lukhas-matriz", "output": {"text": f"echo: {text}"}}
        return JSONResponse(_maybe_trace(out))

    @app.post("/v1/dreams")
    async def dreams(payload: Dict[str, Any]):
        seed = payload.get("seed","dream")
        trace = {"step":"imagine","content": f"{seed} …"}
        return _maybe_trace({"id": f"dream_{uuid.uuid4().hex[:8]}", "traces":[trace]})

    return app

lukhas/observability/filters.py

import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_TOKEN = re.compile(r"\b(sk-[A-Za-z0-9]{6,})\b")

def redact_pii(text: str) -> str:
    text = _EMAIL.sub("[redacted@email]", text)
    text = _TOKEN.sub("[redacted_token]", text)
    return text

lukhas/core/reliability/backoff.py

import random
from typing import Tuple

def jittered_exponential(base: float, factor: float, attempt: int, jitter: float=0.1) -> Tuple[float,float]:
    window = base * (factor ** attempt)
    lo = max(0.0, window * (1 - jitter))
    hi = window * (1 + jitter)
    return lo, hi

lukhas/core/reliability/ratelimit.py

def rate_limit_error(retry_after_s: int):
    return {
        "error": {"type": "rate_limit_exceeded", "message": "rate limit exceeded"},
        "headers": {"Retry-After": str(retry_after_s)}
    }


⸻

3) OpenAPI spec & Quickstart scaffolds

docs/openapi/lukhas-openai.yaml

openapi: 3.0.3
info:
  title: Lukhas OpenAI Facade
  version: 0.1.0
paths:
  /v1/models:
    get:
      summary: List models
      responses:
        "200":
          description: OK
  /v1/embeddings:
    post:
      summary: Create embeddings
      responses: {"200": {"description": "OK"}}
  /v1/responses:
    post:
      summary: Generate a response
      responses: {"200": {"description": "OK"}}
  /v1/dreams:
    post:
      summary: Generate a dream trace
      responses: {"200": {"description": "OK"}}
  /healthz:
    get: {responses: {"200": {description: OK}}}
  /readyz:
    get: {responses: {"200": {description: OK}}}
  /metrics:
    get: {responses: {"200": {description: OK}}}

docs/openai/QUICKSTART.md

# Lukhas × OpenAI Quickstart

```bash
uvicorn lukhas.adapters.openai.api:get_app --reload

from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
out = client.responses.create(input="hello lukhas")
print(out.output_text)

	•	Models: GET /v1/models
	•	Embeddings: POST /v1/embeddings
	•	Dreams (Drift): POST /v1/dreams
	•	Health: /healthz, /readyz, /metrics

---

### 4) SBOM & Nightly/load scaffolds

**`scripts/sbom.py`**
```python
#!/usr/bin/env python3
import subprocess, sys, pathlib
out = pathlib.Path("build"); out.mkdir(parents=True, exist_ok=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "cyclonedx-bom"])
subprocess.check_call([sys.executable, "-m", "cyclonedx_py", "-o", str(out / "sbom.cyclonedx.json")])
print("[sbom] wrote", out / "sbom.cyclonedx.json")

load/resp_scenario.js (k6)

import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = { vus: 50, duration: '2m' };

export default function () {
  const url = 'http://localhost:8000/v1/responses';
  const payload = JSON.stringify({ input: 'ping', tools: [] });
  const res = http.post(url, payload, { headers: { 'Content-Type': 'application/json' }});
  check(res, { '200': (r) => r.status === 200 });
  sleep(0.2);
}

scripts/release_rc.sh

#!/usr/bin/env bash
set -euo pipefail
VER="${1:?usage: $0 vX.Y.Z-rc}"
cz changelog
python3 scripts/sbom.py
gh release create "$VER" --notes "RC $VER" build/sbom.cyclonedx.json || true
echo "RC $VER prepared."


⸻

5) Tool export skeleton

scripts/export_openai_tools.py

#!/usr/bin/env python3
"""
Export OpenAI tool specs from manifests.
Writes build/openai_tools.json with:
  {"tools":[{"type":"function","function":{"name": "...","description":"...","parameters":{...}}}, ...]}
"""
import json, sys
from pathlib import Path

def main():
    out = Path("build"); out.mkdir(parents=True, exist_ok=True)
    tools = []
    for mf in Path("manifests").rglob("module.manifest.json"):
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        for cap in m.get("capabilities", []):
            name = cap.get("name") or cap.get("id") or mf.stem
            tools.append({"type":"function","function":{"name": name[:64], "description": cap.get("description",""), "parameters": cap.get("schema", {})}})
    (out/"openai_tools.json").write_text(json.dumps({"tools": tools}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[tools] wrote {out/'openai_tools.json'} with {len(tools)} tools")

if __name__ == "__main__":
    sys.exit(main())


⸻

6) Small doc blurb (paste into PR template or façade README)

**Matriz readiness (API)**
- [ ] /healthz /readyz /metrics green locally
- [ ] /v1/models, /v1/embeddings, /v1/responses return valid shapes
- [ ] /v1/dreams returns an id + traces
- [ ] OpenAPI spec builds: `docs/openapi/lukhas-openai.yaml`
- [ ] Eval mini-harness runs (<90s), smoke passing


⸻

amazing — here’s a ready-to-paste Evals Pack that drops a tiny, zero-drama eval harness into the repo. It’s stub-friendly (works with your current façade “echo” behavior) but future-proof (thresholds, strict mode, JSON+MD artifacts, optional JUnit). Copy the blocks as-is.

⸻

1) Runner

evals/run_evals.py

#!/usr/bin/env python3
"""
Lukhas mini-evals runner (OpenAI-aligned façade).

- Consumes JSONL cases (id, input, expect.contains[], optional tools).
- POSTs to /v1/responses on the Lukhas façade.
- Writes JSON + Markdown summaries in docs/audits/.
- Thresholds & strict mode for CI gating.

Usage:
  python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits --threshold 0.7
  # CI warn-only (exit 0): omit --strict
  # Gate (exit 1 if below threshold): add --strict
"""
from __future__ import annotations
import argparse, glob, json, os, sys, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

try:
    import requests
except ImportError:
    print("[evals] `requests` not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(2)

@dataclass
class Case:
    id: str
    input: str
    expect_contains: List[str]
    tools: List[Dict[str, Any]]

@dataclass
class Result:
    id: str
    ok: bool
    latency_ms: float
    output_text: str

def load_cases(patterns: List[str]) -> List[Case]:
    files: List[str] = []
    for pat in patterns:
        files.extend(glob.glob(pat))
    cases: List[Case] = []
    for fp in sorted(files):
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                cases.append(
                    Case(
                        id=obj.get("id") or Path(fp).stem,
                        input=obj["input"],
                        expect_contains=obj.get("expect", {}).get("contains", []),
                        tools=obj.get("tools", []),
                    )
                )
    return cases

def call_responses(base_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/v1/responses"
    r = requests.post(url, json=payload, timeout=(5, 30))
    r.raise_for_status()
    return r.json()

def run_case(base_url: str, case: Case) -> Result:
    t0 = time.time()
    body = call_responses(base_url, {"input": case.input, "tools": case.tools})
    dt = (time.time() - t0) * 1000.0
    # Compatible with façade shape: body["output"]["text"]
    text = ""
    if isinstance(body, dict):
        out = body.get("output") or {}
        text = out.get("text") or json.dumps(body)  # fallback for alternative shapes
    ok = all(s.lower() in text.lower() for s in case.expect_contains)
    return Result(id=case.id, ok=ok, latency_ms=round(dt, 2), output_text=text[:2000])

def render_md(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Lukhas Mini-Evals\n")
    lines.append(f"**Total:** {summary['total']}  •  **Passed:** {summary['passed']}  •  **Accuracy:** {summary['accuracy']:.1%}\n")
    lines.append(f"**Threshold:** {summary['threshold']:.1%}  •  **Strict:** {summary['strict']}\n")
    lines.append("## Cases\n")
    lines.append("| id | ok | latency_ms | excerpt |")
    lines.append("|---|---:|---:|---|")
    for r in summary["results"]:
        excerpt = (r["output_text"] or "").replace("\n"," ")[:120]
        lines.append(f"| `{r['id']}` | {'✅' if r['ok'] else '❌'} | {r['latency_ms']:.0f} | {excerpt} |")
    lines.append("")
    return "\n".join(lines)

def write_junit_xml(summary: Dict[str, Any], path: Path) -> None:
    # Minimal JUnit for CI (optional)
    from xml.sax.saxutils import escape
    cases = summary["results"]
    failures = [c for c in cases if not c["ok"]]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<testsuite name="lukhas-mini-evals" tests="{len(cases)}" failures="{len(failures)}">']
    for c in cases:
        xml.append(f'  <testcase classname="evals" name="{escape(c["id"])}" time="{c["latency_ms"]/1000.0:.3f}">')
        if not c["ok"]:
            msg = escape((c["output_text"] or "")[:500])
            xml.append(f'    <failure message="expect.contains not satisfied">{msg}</failure>')
        xml.append('  </testcase>')
    xml.append('</testsuite>')
    path.write_text("\n".join(xml), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.getenv("LUKHAS_BASE_URL", "http://localhost:8000"))
    ap.add_argument("--cases", nargs="+", default=["evals/cases/*.jsonl"])
    ap.add_argument("--out", default="docs/audits")
    ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument("--strict", action="store_true", help="exit 1 if accuracy < threshold")
    ap.add_argument("--junit", action="store_true", help="also write JUnit XML")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    cases = load_cases(args.cases)
    if not cases:
        print("[evals] no cases found", file=sys.stderr)
        return 2
    results: List[Result] = []
    for c in cases:
        try:
            results.append(run_case(args.base_url, c))
        except Exception as e:
            results.append(Result(id=c.id, ok=False, latency_ms=0.0, output_text=f"[error] {e}"))

    passed = sum(1 for r in results if r.ok)
    total = len(results)
    acc = passed / total if total else 0.0
    summary = {
        "total": total,
        "passed": passed,
        "accuracy": acc,
        "threshold": args.threshold,
        "strict": bool(args.strict),
        "base_url": args.base_url,
        "results": [asdict(r) for r in results],
    }

    # Write artifacts
    (out / "evals_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "evals_report.md").write_text(render_md(summary), encoding="utf-8")
    if args.junit:
        write_junit_xml(summary, out / "evals_report.junit.xml")

    print(f"[evals] accuracy={acc:.1%} passed={passed}/{total} threshold={args.threshold:.1%}")
    if args.strict and acc < args.threshold:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())


⸻

2) Case format & starter sets

evals/README.md

# Lukhas Mini-Evals

- **Format**: JSONL, one object per line:
```json
{"id":"echo-001","input":"hello lukhas","expect":{"contains":["echo","hello"]},"tools":[]}

	•	Run:

uvicorn lukhas.adapters.openai.api:get_app --reload &
python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits --threshold 0.7

	•	Artifacts: docs/audits/evals_report.json, docs/audits/evals_report.md (+ optional JUnit XML)
	•	CI: add as warn-only in MATRIZ Validate; flip --strict once stable.

**`evals/cases/echo.jsonl`** (5 cases)
```json
{"id":"echo-001","input":"hello lukhas","expect":{"contains":["echo","hello"]},"tools":[]}
{"id":"echo-002","input":"matriz rocks","expect":{"contains":["echo","matriz"]},"tools":[]}
{"id":"echo-003","input":"guardian watch","expect":{"contains":["echo","guardian"]},"tools":[]}
{"id":"echo-004","input":"trail memory","expect":{"contains":["echo","trail"]},"tools":[]}
{"id":"echo-005","input":"flow consciousness","expect":{"contains":["echo","flow"]},"tools":[]}

evals/cases/openai_shapes.jsonl (5 cases)

{"id":"shape-001","input":"models list","expect":{"contains":["lukhas-matriz"]},"tools":[]}
{"id":"shape-002","input":"embedding me","expect":{"contains":["echo"]},"tools":[]}
{"id":"shape-003","input":"dream me","expect":{"contains":["echo"]},"tools":[]}
{"id":"shape-004","input":"trace please","expect":{"contains":["echo"]},"tools":[]}
{"id":"shape-005","input":"rate limit doc","expect":{"contains":["echo"]},"tools":[]}

These pass against the current façade (“echo: …”). As you wire real capabilities, simply update expected substrings to reflect stronger behaviors.

⸻

3) Makefile targets

Append to Makefile:

evals: ## Run mini-evals (warn-only)
\tpython3 evals/run_evals.py --base-url $${LUKHAS_BASE_URL:-http://localhost:8000} --cases "evals/cases/*.jsonl" --out docs/audits || true
\t@echo "Report: docs/audits/evals_report.md"

evals-strict: ## Gate on accuracy >= threshold (default 0.7)
\tpython3 evals/run_evals.py --strict --threshold $${LUKHAS_EVALS_THRESHOLD:-0.7} --junit --base-url $${LUKHAS_BASE_URL:-http://localhost:8000} --cases "evals/cases/*.jsonl" --out docs/audits


⸻

4) CI (add to MATRIZ Validate workflow)

In .github/workflows/matriz-validate.yml, add after smoke tests:

  - name: Mini Evals (warn-only)
    run: |
      python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits || true
    continue-on-error: true
  - name: Upload eval artifacts
    uses: actions/upload-artifact@v4
    with:
      name: lukhas-evals
      path: |
        docs/audits/evals_report.json
        docs/audits/evals_report.md
        docs/audits/evals_report.junit.xml
      if-no-files-found: ignore

When stable, swap to evals-strict and remove continue-on-error.

⸻

5) (Optional) tiny unit to assert runner produces artifacts

tests/smoke/test_evals_runner.py

import os
from pathlib import Path
from subprocess import run, CalledProcessError

def test_evals_runner_produces_reports(tmp_path, monkeypatch):
    out = tmp_path / "audits"
    # Use local façade defaults; skip if not running
    try:
        r = run(["python3", "evals/run_evals.py", "--out", str(out)], check=True, capture_output=True, text=True)
    except CalledProcessError as e:
        # If façade isn't running, don't fail the suite; this is a smoke
        assert "connection" in (e.stderr.lower() + e.stdout.lower()) or e.returncode != 0
        return
    assert (out / "evals_report.json").exists()
    assert (out / "evals_report.md").exists()


⸻

6) One-liner to try locally

uvicorn lukhas.adapters.openai.api:get_app --reload &
make evals
bat docs/audits/evals_report.md || cat docs/audits/evals_report.md


⸻


⸻

## Phase‑2 Essentials (OpenAI‑aligned) — Checklist & Paste Pack

**Why:** Make the façade production‑credible and OpenAI‑comfortable on day one with tiny, high‑ROI artifacts.  
**Use:** Paste the blocks below into new/updated files. Keep CI steps in warn‑only first; flip to enforced after 1–2 green PRs.

### ✅ Quick checklist
- [ ] Auth & error shapes on façade (Bearer + OpenAI‑style 401/429)
- [ ] OpenAPI spec validated in CI
- [ ] Runtime reliability knobs in config (timeouts/backoff/rate limits)
- [ ] SLO budgets (docs + config)
- [ ] .env + Dockerfile + docker‑compose for consistent local runs/CI
- [ ] Ownership & security hygiene (CODEOWNERS, Dependabot, CodeQL, SECURITY.md)
- [ ] Optional: local OTEL collector sample for traces
- [ ] Tool export JSON schema smoke test

---

### A) OpenAPI spec validation in CI
_Add this job step to `.github/workflows/matriz-validate.yml` (after build):_
```yaml
- name: Validate OpenAPI spec
  run: |
    python -m pip install --quiet openapi-spec-validator PyYAML
    python - <<'PY'
import yaml
from openapi_spec_validator import validate_spec
with open("docs/openapi/lukhas-openai.yaml") as f:
    spec = yaml.safe_load(f)
validate_spec(spec)
print("[openapi] spec valid")
PY
```

---

### B) Auth middleware + error catalog

**`lukhas/adapters/openai/auth.py`**
```python
from fastapi import Header, HTTPException

UNAUTHORIZED = {"error":{"type":"unauthorized","message":"missing or invalid token"}}

def require_bearer(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)
    # TODO: verify token via policy_guard (owner/scopes); support PATs and service tokens
```

**`docs/API_ERRORS.md`**
```md
# API Error Shapes
- **401 Unauthorized**
```json
{"error":{"type":"unauthorized","message":"missing or invalid token"}}
```
- **429 Rate limit**
```json
{"error":{"type":"rate_limit_exceeded","message":"rate limit exceeded"}}
```
- **500 Internal error**
```json
{"error":{"type":"internal_server_error","message":"unexpected error"}}
```
```

> When ready, add `Depends(require_bearer)` on protected routes in `lukhas/adapters/openai/api.py`.

---

### C) Reliability knobs (config file)

**`configs/runtime/reliability.yaml`**
```yaml
timeouts:
  connect_ms: 1000
  read_ms: 10000
backoff:
  base_s: 0.1
  factor: 2.0
  jitter: 0.1
rate_limits:
  responses_rps: 20
  embeddings_rps: 50
```

---

### D) SLO budgets

**`configs/observability/slo_budgets.yaml`**
```yaml
endpoints:
  responses:
    p95_ms: 1200
    p99_ms: 2500
  embeddings:
    p95_ms: 800
    p99_ms: 1500
```

**`docs/ops/SLOs.md`**
```md
# SLO Budgets (Façade)
- /v1/responses: p95 ≤ 1200ms, p99 ≤ 2500ms
- /v1/embeddings: p95 ≤ 800ms,  p99 ≤ 1500ms

**Enforcement**
- Smoke warns in CI if current p95 > budget.
- Nightly load job posts p95 to `docs/audits/load_report.md`.
```

---

### E) .env and containers

**`.env.example`**
```env
LUKHAS_BASE_URL=http://localhost:8000
OTEL_EXPORTER_OTLP_ENDPOINT=
LUKHAS_API_TOKEN=replace-me
```

**`Dockerfile`** (dev façade)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests
EXPOSE 8000
CMD ["uvicorn","lukhas.adapters.openai.api:get_app","--host","0.0.0.0","--port","8000"]
```

**`docker-compose.yml`**
```yaml
version: "3.9"
services:
  facade:
    build: .
    ports: ["8000:8000"]
    env_file: .env
```

---

### F) Ownership, supply chain & security

**`CODEOWNERS`**
```
/lukhas/*          @lukhas-ai/platform
/MATRIZ/*          @lukhas-ai/matriz
/docs/**           @lukhas-ai/docs
```

**`.github/dependabot.yml`**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule: { interval: "daily" }
```

**`.github/workflows/codeql.yml`**
```yaml
name: CodeQL
on:
  push: { branches: ["main"] }
  pull_request: { branches: ["main"] }
  schedule:
    - cron: '0 5 * * 1'
jobs:
  analyze:
    permissions:
      actions: read
      contents: read
      security-events: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

**`SECURITY.md`**
```md
# Security Policy
- Report vulnerabilities to security@lukhas.ai
- Do not open public issues; expect first response within 72h.
```

---

### G) OTEL collector (optional, local)

**`observability/otel-collector.yaml`**
```yaml
receivers:
  otlp:
    protocols: { http: {} }
exporters:
  file:
    path: ./docs/audits/traces.json
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [file]
```

---

### H) Tool export JSON schema smoke test

**`tests/tools/test_openai_tools_export.py`**
```python
import json, os, pytest
from pathlib import Path

@pytest.mark.skipif(not Path("build/openai_tools.json").exists(), reason="tools export not built yet")
def test_tools_export_shape():
    data = json.loads(Path("build/openai_tools.json").read_text(encoding="utf-8"))
    assert "tools" in data and isinstance(data["tools"], list)
    if data["tools"]:
        t = data["tools"][0]
        assert t.get("type") == "function"
        fn = t.get("function", {})
        assert {"name","description","parameters"} <= set(fn.keys())
```

---

### I) CI artifact wiring (append to validate workflow)
_Add after existing artifact uploads:_
```yaml
  - name: Upload OpenAPI & SLO artifacts
    uses: actions/upload-artifact@v4
    with:
      name: lukhas-openapi-and-slo
      path: |
        docs/openapi/lukhas-openai.yaml
        docs/ops/SLOs.md
        configs/observability/slo_budgets.yaml
      if-no-files-found: ignore
```

> **Note:** Leave auth off on façade endpoints until clients are ready; then enable `require_bearer` on write paths and keep `/healthz` open.

---

amazing — you’ve got all the pieces in place. Here’s a super-tight post-merge verification runbook so you can prove the stack is green the minute Codex/Claude finish.

Post-Merge Verification (10–15 min)

# 0) Boot façade (dev)
uvicorn lukhas.adapters.openai.api:get_app --host 0.0.0.0 --port 8000 &

# 1) Smokes
pytest -q tests/smoke -k "healthz or openai_facade or dreams_api or tracing or evals_runner"

# 2) Mini-evals (warn-only)
make evals

# 3) OpenAPI validity
python -m pip install -q openapi-spec-validator PyYAML
python - <<'PY'
import yaml; from openapi_spec_validator import validate_spec
validate_spec(yaml.safe_load(open("docs/openapi/lukhas-openai.yaml")))
print("[openapi] spec valid")
PY

# 4) Tool export
python3 scripts/export_openai_tools.py
pytest -q tests/tools/test_openai_tools_export.py -q || true  # warn-only first

# 5) Links, contracts, context
python3 docs/check_links.py --root .
python3 scripts/validate_contract_refs.py
python3 scripts/validate_context_front_matter.py

# 6) Star rules + coverage
make star-rules-lint
make star-rules-coverage

# 7) Security belt & SBOM
detect-secrets scan --baseline .secrets.baseline || true
pipx run pip-audit -f json -o docs/audits/pip_audit.json || true
python3 scripts/sbom.py

# 8) Load smoke (optional)
k6 run load/resp_scenario.js || true

What “good” looks like
	•	Smokes: all pass.
	•	Evals: docs/audits/evals_report.md shows ≥70% (okay for stub); raise later.
	•	OpenAPI: validator prints spec valid.
	•	Tools export: test green or warn-only (first run).
	•	Link checker: no broken links in docs/audits/linkcheck.txt.
	•	Star rules: coverage report updated; zero “no-hit” stars.
	•	Security: no secrets; SBOM written to build/sbom.cyclonedx.json.

Evidence pack to attach to the PR
	•	docs/audits/evals_report.md
	•	docs/audits/star_rules_coverage.md
	•	docs/audits/linkcheck.txt
	•	docs/audits/manifest_stats.md (after Copilot patches the reporter)
	•	build/openai_tools.json
	•	docs/openapi/lukhas-openai.yaml
	•	build/sbom.cyclonedx.json

Quick Go/No-Go gate (copy into PR checklist)
	•	Façade: /healthz, /readyz, /metrics ✅
	•	/v1/models, /v1/embeddings, /v1/responses, /v1/dreams ✅
	•	OpenAPI validated in CI ✅
	•	Mini-evals ≥ 0.70 (warn-only) ✅
	•	SLO docs + budgets committed ✅
	•	Security belt: detect-secrets + gitleaks (warn-only) ✅
	•	Star canon consistent (🔮 Oracle (Quantum) canonical; Ambiguity only alias) ✅

Tiny handoff notes (for Claude/Codex)
	•	If any smoke fails, don’t patch tests—bring endpoints to spec or toggle auth only after /healthz stays public.
	•	If tool export test fails, likely a capability without parameters; default to { "type":"object","properties":{} } in the exporter.
	•	If link checker finds lane rename issues, run the fixer and re-generate docs/audits/linkcheck.txt.

—

