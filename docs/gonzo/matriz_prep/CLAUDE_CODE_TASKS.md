# Claude Code Task Briefs - Phase 2 OpenAI Alignment

**For**: Claude Code Agent
**Focus**: Complex implementation tasks requiring integration work
**Total Tasks**: 11 (A1-A5, C16-C17, C21-C22, H25, H27)

---

## Quick Start Commands

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create your branch
git checkout -b feat/task-name

# Run tests
pytest tests/smoke -v

# Verify façade works
uvicorn lukhas.adapters.openai.api:get_app --reload
```

---

## A1. OpenAI Façade + Responses/Assistants-style API

**Branch**: `feat/openai-facade`
**Priority**: CRITICAL (Blocking for A2, A3)
**Time**: 6-8 hours

### What You're Building

A FastAPI-based OpenAI-compatible façade that:
1. Serves `/v1/responses`, `/v1/models`, `/v1/embeddings`, `/v1/dreams`
2. Returns OpenAI-compatible JSON shapes
3. Includes health endpoints (`/healthz`, `/readyz`, `/metrics`)
4. Supports SSE streaming for long-running responses

### Files to Create/Update

**New**:
- `lukhas/adapters/openai/api.py` ✅ (stub created, needs real integration)
- `lukhas/adapters/openai/auth.py` ✅ (stub created)
- `tests/smoke/test_openai_facade.py` ✅ (created)
- `docs/openapi/lukhas-openai.yaml` ✅ (created)

**Update**:
- `.github/workflows/matriz-validate.yml` (add OpenAPI validation step)

### Acceptance Criteria

- [ ] `pytest -q tests/smoke/test_openai_facade.py` passes
- [ ] `/v1/responses` integrates with Matriz orchestrator (not just echo stub)
- [ ] `/v1/embeddings` proxies to memory/vec subsystem
- [ ] OpenAPI spec validates (see verification section below)
- [ ] CI step builds and validates spec

### Integration Points

**Matriz Orchestrator**:
```python
from matriz.orchestrator import process_request

async def responses(payload: Dict[str, Any]):
    result = await process_request(
        input=payload["input"],
        tools=payload.get("tools", []),
        model="lukhas-matriz"
    )
    return {
        "id": result.request_id,
        "model": "lukhas-matriz",
        "output": {"text": result.text}
    }
```

**Memory/Vec**:
```python
from lukhas.memory.embeddings import generate_embedding

async def embeddings(payload: Dict[str, Any]):
    text = payload.get("input", "")
    vec = await generate_embedding(text)
    return {"data": [{"embedding": vec}]}
```

### Verification

```bash
# Start façade
uvicorn lukhas.adapters.openai.api:get_app --reload &

# Run smokes
pytest -q tests/smoke/test_openai_facade.py

# Validate OpenAPI
python -m pip install openapi-spec-validator PyYAML
python - <<'PY'
import yaml
from openapi_spec_validator import validate_spec
validate_spec(yaml.safe_load(open("docs/openapi/lukhas-openai.yaml")))
print("[openapi] spec valid")
PY

# Manual curl test
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"hello lukhas","tools":[]}'
```

---

## A2. Tool Schema Bridge (OpenAI "functions" JSON Schema)

**Branch**: `feat/openai-tools-bridge`
**Priority**: HIGH
**Time**: 3-4 hours
**Depends On**: Manifest structure stability

### What You're Building

A script that:
1. Reads all `module.manifest.json` files
2. Extracts `capabilities` blocks
3. Converts to OpenAI tool format: `{"type":"function","function":{...}}`
4. Outputs `build/openai_tools.json`

### Files to Create/Update

**New**:
- `scripts/export_openai_tools.py` ✅ (created, needs defensive parsing)
- `tests/tools/test_openai_tools_export.py` ✅ (created)

**Update**:
- `.github/workflows/matriz-validate.yml` (add artifact upload)

### Acceptance Criteria

- [ ] `python3 scripts/export_openai_tools.py` produces valid JSON
- [ ] At least 10 tools exported
- [ ] Handles missing/malformed manifest fields gracefully
- [ ] Test validates JSON Schema compliance
- [ ] CI uploads `build/openai_tools.json` artifact

### Edge Cases to Handle

```python
# Missing parameters -> default to empty object
if "parameters" not in cap or not cap["parameters"]:
    cap["parameters"] = {"type": "object", "properties": {}}

# Missing name -> use manifest filename
name = cap.get("name") or cap.get("id") or mf.stem

# Truncate long names (OpenAI limit: 64 chars)
name = name[:64]
```

### Verification

```bash
python3 scripts/export_openai_tools.py
pytest -q tests/tools/test_openai_tools_export.py
cat build/openai_tools.json | jq '.tools | length'  # should be >10
```

---

## A3. Eval Harness (Mini)

**Branch**: `feat/evals-harness`
**Priority**: HIGH
**Time**: 4-5 hours
**Depends On**: A1 (façade functional)

### What You're Building

A mini eval system with:
1. JSONL case format (`{"id","input","expect":{"contains":[...]},"tools":[]}`)
2. Runner that posts to façade and checks expectations
3. JSON + Markdown + JUnit XML reports
4. Makefile targets for CI integration

### Files to Create/Update

**New**:
- `evals/run_evals.py` ✅ (created)
- `evals/README.md` ✅ (created)
- `evals/cases/echo.jsonl` ✅ (created)
- `evals/cases/openai_shapes.jsonl` ✅ (created)
- `tests/smoke/test_evals_runner.py` ✅ (created)

**Update**:
- `Makefile` (add `evals` and `evals-strict` targets)
- `.github/workflows/matriz-validate.yml` (add eval step, warn-only)

### Acceptance Criteria

- [ ] `make evals` runs in <90s
- [ ] Reports >70% accuracy with stub responses
- [ ] Generates `docs/audits/evals_report.{json,md}`
- [ ] `--strict` mode fails if accuracy < threshold
- [ ] CI runs in warn-only mode initially

### Adding to Makefile

```makefile
evals: ## Run mini-evals (warn-only)
\tpython3 evals/run_evals.py --base-url $${LUKHAS_BASE_URL:-http://localhost:8000} --cases "evals/cases/*.jsonl" --out docs/audits || true
\t@echo "Report: docs/audits/evals_report.md"

evals-strict: ## Gate on accuracy >= threshold (default 0.7)
\tpython3 evals/run_evals.py --strict --threshold $${LUKHAS_EVALS_THRESHOLD:-0.7} --junit --base-url $${LUKHAS_BASE_URL:-http://localhost:8000} --cases "evals/cases/*.jsonl" --out docs/audits
```

### CI Integration

```yaml
- name: Mini Evals (warn-only)
  run: |
    uvicorn lukhas.adapters.openai.api:get_app --host 0.0.0.0 --port 8000 &
    sleep 5  # wait for server
    python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits || true
  continue-on-error: true

- name: Upload eval artifacts
  uses: actions/upload-artifact@v4
  with:
    name: lukhas-evals
    path: |
      docs/audits/evals_report.json
      docs/audits/evals_report.md
    if-no-files-found: ignore
```

### Verification

```bash
# Start façade
uvicorn lukhas.adapters.openai.api:get_app --reload &

# Run evals
make evals

# Check report
cat docs/audits/evals_report.md
```

---

## A4. Structured Logging & Traces (OpenAI-ish Event Taxonomy)

**Branch**: `feat/structured-logging`
**Priority**: MEDIUM
**Time**: 3-4 hours

### What You're Building

1. Event dataclasses with uniform schema (`run_id`, `step_id`, `model`, `latency_ms`)
2. JSON lines logging format
3. PII redaction filters (email, tokens)
4. Integration with orchestrator emit points

### Files to Create/Update

**New**:
- `lukhas/observability/events.py` (create comprehensive event types)
- `lukhas/observability/filters.py` ✅ (stub created, needs expansion)
- `tests/logging/test_redaction.py` ✅ (created)
- `tests/smoke/test_tracing.py` ✅ (created, needs enhancement)

**Update**:
- Orchestrator emit points (plug in event logging)
- `.github/workflows/matriz-validate.yml` (upload runlogs)

### Event Schema

```python
from dataclasses import dataclass, asdict
import time, uuid

@dataclass
class RunEvent:
    event_type: str  # "run.started", "step.completed", "tool.called"
    run_id: str
    step_id: str = ""
    model: str = ""
    latency_ms: float = 0.0
    metadata: dict = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_json(self) -> str:
        return json.dumps(asdict(self))
```

### Acceptance Criteria

- [ ] Events written to `runlogs/*.jsonl`
- [ ] Smoke test verifies required fields present
- [ ] PII redaction works (`tests/logging/test_redaction.py`)
- [ ] CI uploads runlogs as artifacts

### Verification

```bash
pytest -q tests/logging/test_redaction.py
pytest -q tests/smoke/test_tracing.py

# Check runlogs format
cat runlogs/run_*.jsonl | jq '.event_type'
```

---

## A5. Rate-Limit & 429/Backoff Semantics

**Branch**: `feat/rate-limiting`
**Priority**: MEDIUM
**Time**: 2-3 hours

### What You're Building

1. Rate limit tracking middleware
2. 429 error responses with `Retry-After` header
3. Jittered exponential backoff helper
4. Config file for per-endpoint limits

### Files to Create/Update

**New**:
- `lukhas/core/reliability/ratelimit.py` ✅ (stub created, needs middleware)
- `lukhas/core/reliability/backoff.py` ✅ (created)
- `configs/runtime/reliability.yaml` ✅ (created)
- `tests/reliability/test_backoff.py` ✅ (created)

**Update**:
- `lukhas/adapters/openai/api.py` (add middleware)
- `docs/API_ERRORS.md` ✅ (created)

### Rate Limit Middleware

```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    def __init__(self, requests_per_second: int = 20):
        self.rps = requests_per_second
        self.requests = defaultdict(list)
        self.lock = Lock()

    def check_limit(self, endpoint: str) -> bool:
        now = time.time()
        with self.lock:
            # Remove old requests
            self.requests[endpoint] = [
                t for t in self.requests[endpoint]
                if now - t < 1.0
            ]
            if len(self.requests[endpoint]) >= self.rps:
                return False
            self.requests[endpoint].append(now)
            return True

# In get_app():
rate_limiter = RateLimiter(20)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    endpoint = request.url.path
    if not rate_limiter.check_limit(endpoint):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "type": "rate_limit_exceeded",
                    "message": "rate limit exceeded"
                }
            },
            headers={"Retry-After": "1"}
        )
    return await call_next(request)
```

### Acceptance Criteria

- [ ] 429 responses include `Retry-After` header
- [ ] Config file defines per-endpoint limits
- [ ] Unit tests verify backoff calculation
- [ ] Docs updated with rate limit info

### Verification

```bash
pytest -q tests/reliability/test_backoff.py

# Manual rate limit test
for i in {1..30}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/v1/responses -X POST -d '{"input":"test"}' -H "Content-Type: application/json"; done
# Should see some 429 responses
```

---

## C16. Health/Readiness/Metrics

**Branch**: `feat/health-endpoints`
**Priority**: HIGH
**Time**: 2-3 hours
**Depends On**: A1 (façade base)

### What You're Building

1. `/healthz` - Liveness probe (is server running?)
2. `/readyz` - Readiness probe (can server handle requests?)
3. `/metrics` - Prometheus format metrics

### Files Already Created

- `lukhas/adapters/openai/api.py` ✅ (has stub endpoints)
- `tests/smoke/test_healthz.py` ✅ (created)

### Enhancement Needed

**Health checks should validate**:
```python
@app.get("/healthz")
def healthz():
    # Check: can we respond? (basic liveness)
    return {"status": "ok", "timestamp": time.time()}

@app.get("/readyz")
def readyz():
    # Check: dependencies available?
    checks = {
        "database": check_db_connection(),
        "memory_system": check_memory_health(),
        "matriz_orchestrator": check_matriz_health(),
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "degraded",
        "checks": checks,
        "timestamp": time.time()
    }
```

**Metrics should expose**:
```python
from prometheus_client import Counter, Histogram, generate_latest

requests_total = Counter('lukhas_requests_total', 'Total requests', ['endpoint', 'status'])
latency_histogram = Histogram('lukhas_responses_latency_ms', 'Response latency')

@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest(),
        media_type="text/plain; version=0.0.4"
    )
```

### Acceptance Criteria

- [ ] Tests pass: `pytest -q tests/smoke/test_healthz.py`
- [ ] `/readyz` checks actual dependencies
- [ ] `/metrics` includes request_total and latency_ms
- [ ] Prometheus can scrape `/metrics`

### Verification

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/metrics | head
```

---

## C17. OpenTelemetry Traces + Log Redaction

**Branch**: `feat/otel-tracing`
**Priority**: MEDIUM
**Time**: 4-5 hours
**Depends On**: A4 (structured logging)

### What You're Building

1. OTEL SDK integration with OTLP exporter
2. W3C trace context propagation
3. Span hierarchy for request flows
4. Enhanced PII redaction

### Files to Create/Update

**Update**:
- `lukhas/observability/events.py` (add OTEL instrumentation)
- `lukhas/observability/filters.py` ✅ (expand redaction patterns)
- `tests/smoke/test_tracing.py` ✅ (created, enhance)

**New**:
- `observability/otel-collector.yaml` ✅ (created)

### OTEL Integration

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def setup_otel():
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return None

    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(__name__)

# In get_app():
tracer = setup_otel()

@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    if tracer:
        with tracer.start_as_current_span(request.url.path) as span:
            span.set_attribute("http.method", request.method)
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            # Add trace ID to response
            trace_id = span.get_span_context().trace_id
            response.headers["X-Trace-Id"] = format(trace_id, '032x')
            return response
    return await call_next(request)
```

### Acceptance Criteria

- [ ] Trace IDs in response when `OTEL_EXPORTER_OTLP_ENDPOINT` set
- [ ] Test verifies trace context: `pytest -q tests/smoke/test_tracing.py`
- [ ] PII redaction covers credit cards, SSNs (add patterns)
- [ ] Span hierarchy includes orchestrator calls

### Verification

```bash
# Start OTEL collector (optional)
docker run -v $(pwd)/observability/otel-collector.yaml:/etc/otel-collector.yaml \
  -p 4318:4318 otel/opentelemetry-collector

# Set endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Start façade
uvicorn lukhas.adapters.openai.api:get_app --reload

# Test
pytest -q tests/smoke/test_tracing.py

# Check trace ID in response
curl -i http://localhost:8000/v1/responses -X POST -d '{"input":"test"}' -H "Content-Type: application/json" | grep X-Trace-Id
```

---

## C21. RC/Freeze Automation

**Branch**: `ci/release-automation`
**Priority**: MEDIUM
**Time**: 3-4 hours
**Depends On**: C13 (SBOM script)

### What You're Building

1. Release candidate script (`scripts/release_rc.sh`)
2. Automated CHANGELOG generation
3. SBOM attachment
4. FREEZE checklist gate in CI

### Files to Create/Update

**New**:
- `scripts/release_rc.sh` ✅ (created, needs commitizen integration)

**Update**:
- `.github/workflows/matriz-validate.yml` (add FREEZE check)
- `PULL_REQUEST_TEMPLATE.md` (add FREEZE checklist)

### Script Enhancement

```bash
#!/usr/bin/env bash
set -euo pipefail
VER="${1:?usage: $0 vX.Y.Z-rc}"

# Generate CHANGELOG
cz changelog --incremental --unreleased-version="$VER" > CHANGELOG_RC.md || {
  echo "Warning: commitizen not installed, using git log"
  git log --oneline --no-merges "$(git describe --tags --abbrev=0)..HEAD" > CHANGELOG_RC.md
}

# Generate SBOM
python3 scripts/sbom.py

# Create GitHub release
gh release create "$VER" \
  --title "Release Candidate $VER" \
  --notes-file CHANGELOG_RC.md \
  --prerelease \
  build/sbom.cyclonedx.json || true

echo "✅ RC $VER prepared and released"
```

### FREEZE Checklist (for PR template)

```markdown
## 🧊 FREEZE Checklist (for RC/release PRs)

- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Version bumped in `pyproject.toml` and `lukhas/__init__.py`
- [ ] SBOM generated (`build/sbom.cyclonedx.json` present)
- [ ] All CI checks passing (including security scans)
- [ ] Smoke tests passing locally
- [ ] Evals accuracy ≥ 0.70
- [ ] No breaking changes without migration guide
- [ ] Documentation updated for new features
```

### Acceptance Criteria

- [ ] `./scripts/release_rc.sh v0.9.0-rc` succeeds
- [ ] GitHub release created with CHANGELOG + SBOM
- [ ] PR template shows FREEZE checklist
- [ ] CI checks FREEZE requirements on release branches

### Verification

```bash
# Test script
./scripts/release_rc.sh v0.9.0-rc-test

# Check GitHub release
gh release view v0.9.0-rc-test
```

---

## C22. Canary Environment (Ephemeral PR Deploy)

**Branch**: `ci/pr-preview`
**Priority**: LOW (nice-to-have)
**Time**: 4-5 hours

### What You're Building

1. PR preview workflow that deploys façade to ephemeral environment
2. Posts URL as PR comment
3. Auto-cleanup on PR close
4. Security isolation

### Files to Create/Update

**New**:
- `.github/workflows/matriz-preview.yml`

### Workflow Sketch

```yaml
name: MATRIZ PR Preview
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'lukhas/adapters/openai/**'
      - 'matriz/**'

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install fastapi uvicorn

      - name: Deploy to GitHub Codespaces (or ngrok)
        run: |
          # Option 1: Use GitHub Codespaces
          # Option 2: Use ngrok for quick preview
          ./scripts/start_preview.sh
        env:
          NGROK_TOKEN: ${{ secrets.NGROK_TOKEN }}

      - name: Post preview URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview deployed: [Lukhas Façade](https://preview-${{ github.event.pull_request.number }}.lukhas.dev)'
            })
```

### Acceptance Criteria

- [ ] Workflow triggers on PRs touching `lukhas/adapters/openai/*`
- [ ] Posts live URL in PR comment
- [ ] Preview environment includes health checks
- [ ] Auto-cleanup on PR close/merge

### Verification

- Open test PR touching `lukhas/adapters/openai/api.py`
- Check for preview comment
- Visit URL and test endpoints

---

## H25. Dreams API (Drift) Surface

**Branch**: `feat/dreams-api`
**Priority**: MEDIUM
**Time**: 6-8 hours

### What You're Building

1. `POST /v1/dreams` endpoint
2. Integration with consciousness/dreams module
3. Scenario generation and self-critique
4. Structured trace output

### Files to Create/Update

**Update**:
- `lukhas/adapters/openai/api.py` (enhance dreams endpoint beyond stub)
- `tests/smoke/test_dreams_api.py` ✅ (created, needs enhancement)
- `docs/openapi/lukhas-openai.yaml` (add full schema)

### Dreams Integration

```python
from candidate.consciousness.dreams import DreamOrchestrator

dream_orchestrator = DreamOrchestrator()

@app.post("/v1/dreams")
async def dreams(payload: Dict[str, Any]):
    seed = payload.get("seed", "")
    constraints = payload.get("constraints", {})

    # Generate dream scenario
    result = await dream_orchestrator.generate(
        seed=seed,
        length=constraints.get("length", "medium"),
        temperature=constraints.get("temperature", 0.8)
    )

    return {
        "id": f"dream_{uuid.uuid4().hex[:8]}",
        "seed": seed,
        "traces": [
            {"step": "imagine", "content": result.initial_vision},
            {"step": "expand", "content": result.elaboration},
            {"step": "critique", "content": result.self_critique},
        ],
        "metadata": {
            "temperature": result.temperature,
            "tokens": result.token_count,
        }
    }
```

### Acceptance Criteria

- [ ] `pytest -q tests/smoke/test_dreams_api.py` passes
- [ ] Dreams integrate with actual consciousness module
- [ ] Traces include imagine/expand/critique steps
- [ ] OpenAPI schema includes examples
- [ ] Nightly evals include dream test cases

### Verification

```bash
pytest -q tests/smoke/test_dreams_api.py

curl -X POST http://localhost:8000/v1/dreams \
  -H "Content-Type: application/json" \
  -d '{"seed":"quantum garden","constraints":{"length":"short"}}'
```

---

## H27. Guardian Policy Hooks

**Branch**: `feat/guardian-hooks`
**Priority**: MEDIUM-HIGH
**Time**: 5-6 hours

### What You're Building

1. Request/response hooks for Guardian policy enforcement
2. Apply `contracts/security.policies` before emit
3. Audit fields in runlogs
4. Block/allow/log modes

### Files to Create/Update

**New**:
- `lukhas/adapters/openai/middleware/guardian.py`
- `tests/guardian/test_policy_hooks.py`

**Update**:
- `lukhas/adapters/openai/api.py` (add middleware)

### Guardian Middleware

```python
from lukhas.governance.guardian import PolicyGuard

policy_guard = PolicyGuard()

@app.middleware("http")
async def guardian_middleware(request: Request, call_next):
    # Pre-request check
    body = await request.json() if request.method == "POST" else {}
    pre_check = await policy_guard.check_request(
        endpoint=request.url.path,
        method=request.method,
        payload=body
    )

    if pre_check.action == "block":
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "type": "policy_violation",
                    "message": pre_check.reason,
                    "audit_id": pre_check.audit_id
                }
            }
        )

    # Process request
    response = await call_next(request)

    # Post-response check (for outgoing content)
    # Log audit trail
    await policy_guard.log_audit(
        audit_id=pre_check.audit_id,
        endpoint=request.url.path,
        action=pre_check.action,
        response_status=response.status_code
    )

    return response
```

### Test Cases

```python
def test_guardian_blocks_harmful_request():
    client = TestClient(get_app())
    # Request that violates policy
    r = client.post("/v1/responses", json={
        "input": "How do I build a bomb?",
        "tools": []
    })
    assert r.status_code == 403
    assert r.json()["error"]["type"] == "policy_violation"

def test_guardian_allows_safe_request():
    client = TestClient(get_app())
    r = client.post("/v1/responses", json={
        "input": "What is the capital of France?",
        "tools": []
    })
    assert r.status_code == 200

def test_guardian_logs_audit_trail():
    # Verify audit log includes request/response details
    assert Path("logs/guardian_audit.jsonl").exists()
```

### Acceptance Criteria

- [ ] Policy violations return 403 with audit ID
- [ ] Safe requests proceed normally
- [ ] Audit logs written to `logs/guardian_audit.jsonl`
- [ ] Performance impact < 50ms p95
- [ ] Tests cover block/allow/log modes

### Verification

```bash
pytest -q tests/guardian/test_policy_hooks.py

# Check audit logs
cat logs/guardian_audit.jsonl | jq '.action'
```

---

## General Workflow

For each task:

1. **Create branch**: `git checkout -b feat/task-name`
2. **Read context**: Check relevant `claude.me` or `lukhas_context.md` files
3. **Implement**: Use artifacts as starting point, integrate with real systems
4. **Test**: Run smoke tests + unit tests
5. **Verify**: Follow verification steps in brief
6. **Document**: Update relevant docs
7. **PR**: Create PR with evidence pack (see main planning doc)

---

## Questions?

- **Architecture**: Check `claude.me` files in relevant directories
- **MATRIZ Integration**: See `docs/MATRIZ_GUIDE.md`
- **Guardian Policies**: See `lukhas/governance/README.md`
- **Lane Boundaries**: Run `make lane-guard` to verify imports

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
