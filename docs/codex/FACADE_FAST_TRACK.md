# 🧰 Codex Execution Package — Façade Fast-Track (Waves A & B)

**Version**: 1.0
**Target**: Audit-ready OpenAI-compatible API with minimal changes
**Status**: Production-safe, surgical patches only
**Updated**: 2025-10-23

**Doctrine**: **Zero Guesswork.** Every action must be based on explicit reads, verified state, or a defined pattern. No assumptions.

### Context Integrity Check (run before any patches)

```bash
pwd; git status --porcelain || true
test "$(pwd)" = "/Users/agi_dev/LOCAL-REPOS/Lukhas" || { echo "wrong repo root"; exit 1; }
test -f docs/codex/README.md && test -f claude.me || { echo "missing context files"; exit 1; }
```

### Mission Trace (short-term objective memory)

Create/update `.codex_trace.json`:

```json
{
  "session_id": "<auto>",
  "task": "Façade Fast-Track",
  "phase": 0,
  "last_verified_state": "<timestamp>",
  "expected_artifacts": ["serve/openai_routes.py","serve/main.py","tests/smoke/*"]
}
```

### Acceptance Gates (7+1)

1. Endpoint schema compliance
2. JSON response validation
3. Smoke test pass rate ≥ 90%
4. Lane guard boundaries intact
5. Rate-limit headers present
6. Log coverage > 85%
7. No new 404s on /v1/*
+1. Diagnostic self-report matches commit summary

### Operational Awareness

Before executing **Wave A**, summarize your objective in **one sentence** and append it to `.codex_trace.json`.

---

## 🎯 Goal

**Today**: Get RC soak green and smoke pass rate to 90%+ by completing:
- `/v1/models` (OpenAI list shape)
- `/v1/embeddings` (deterministic hash-based vectors)
- `/v1/responses` (non-stream minimal stub)
- Rate limit & trace headers (OpenAI-compatible)
- `/health` alias for ops tooling
- **Optionally**: Wire quota resolver + SSE streaming if modules exist

**Constraints**:
- ✅ Only touch existing files or create minimal, well-scoped routers
- ✅ No deep new dependencies
- ✅ Dev-permissive auth (Bearer token required, validation stubbed)
- ✅ Reuse existing modules (quota_resolver, async_orchestrator) only if already present
- ✅ Surgical, reviewable diffs

---

## 📋 Tools & Commands Reference

### Codex Tools Available

**File Operations**:
- `Read(file_path)` - Read file contents
- `Write(file_path, content)` - Create new file
- `Edit(file_path, old_string, new_string)` - Surgical patch existing file
- `Glob(pattern)` - Find files by pattern
- `Grep(pattern)` - Search file contents

**Execution**:
- `Bash(command)` - Run shell commands
- `Task(prompt, subagent_type)` - Launch specialized agent

**Testing**:
- `pytest` - Via Bash tool for test execution
- `make` targets - Via Bash tool for workflows

**Git Operations**:
- `git status/add/commit/push` - Via Bash tool

---

## 0️⃣ Preflight — Detect Where to Wire

```bash
# TOOL: Bash
# From repo root
set -euo pipefail

# Find FastAPI entrypoint (serve)
MAIN=$(git ls-files | grep -E '^serve/(main|app)\.py' | head -1)
test -n "$MAIN" || { echo "❌ serve/main.py not found"; exit 1; }
echo "✅ Using entrypoint: $MAIN"

# Check for existing OpenAI router
ROUTER=$(git ls-files | grep -E '^serve/(openai_routes|openai|routes)/.*\.py$|^serve/openai_routes\.py' | head -1 || true)
if [ -n "$ROUTER" ]; then
  echo "✅ Existing OpenAI router: $ROUTER"
  echo "ACTION: Merge handlers into existing router (don't duplicate)"
else
  echo "ℹ️  No router found"
  echo "ACTION: Create serve/openai_routes.py"
fi

# Check for existing quota resolver (optional Wave B)
QUOTA=$(git ls-files | grep -E 'quota_resolver\.py' | head -1 || true)
if [ -n "$QUOTA" ]; then
  echo "✅ Found quota resolver: $QUOTA"
  echo "OPTIONAL: Wire into rate limit headers (Wave B-1)"
else
  echo "ℹ️  No quota resolver found, using stub RL headers"
fi

# Check for async orchestrator (optional Wave B)
ORCH=$(git ls-files | grep -E 'async_orchestrator\.py' | head -1 || true)
if [ -n "$ORCH" ]; then
  echo "✅ Found async orchestrator: $ORCH"
  echo "OPTIONAL: Enable SSE streaming for /v1/responses (Wave B-2)"
else
  echo "ℹ️  No async orchestrator found, keeping non-stream only"
fi

echo ""
echo "✅ Preflight complete - ready for Wave A patches"
```

**Expected Output**:
```
✅ Using entrypoint: serve/main.py
ℹ️  No router found
ACTION: Create serve/openai_routes.py
ℹ️  No quota resolver found, using stub RL headers
ℹ️  No async orchestrator found, keeping non-stream only

✅ Preflight complete - ready for Wave A patches
```

---

## 1️⃣ PATCH A — Create OpenAI Routes

**TOOL**: `Write` (if new file) or `Edit` (if router exists)

**Action**: Create `serve/openai_routes.py` with production-safe OpenAI endpoints

**File**: `serve/openai_routes.py`

```python
"""
OpenAI-compatible API routes for LUKHAS.

Provides minimal, production-safe implementations of:
- /v1/models: Model catalog
- /v1/embeddings: Deterministic hash-based embeddings
- /v1/responses: Non-stream response generation (stub)

All endpoints include:
- Rate limit headers (OpenAI-compatible)
- Request/trace ID threading
- Dev-permissive auth (Bearer token required)
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response, status

# Router mounted under /v1
router = APIRouter(prefix="/v1", tags=["openai"])

# ------------------------------------------------------------------------------
# Auth (dev-permissive): accept any Bearer token if present
# PRODUCTION: Replace with your existing auth verifier dependency
# ------------------------------------------------------------------------------
def require_api_key(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dev-permissive auth: accepts any Bearer token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "type": "invalid_api_key",
                    "message": "Missing or invalid API key",
                    "code": "invalid_api_key"
                }
            }
        )
    token = authorization.split(" ", 1)[1].strip()
    # In production, validate token here
    return {"token": token}


def _rl_headers() -> Dict[str, str]:
    """Generate rate limit headers (stub values)."""
    now = int(time.time())
    return {
        # Standard X-RateLimit-* headers
        "X-RateLimit-Limit": "60",
        "X-RateLimit-Remaining": "59",
        "X-RateLimit-Reset": str(now + 60),
        # OpenAI-style lowercase aliases
        "x-ratelimit-limit-requests": "60",
        "x-ratelimit-remaining-requests": "59",
        "x-ratelimit-reset-requests": str(now + 60),
    }


def _with_std_headers(resp: Response, trace_id: Optional[str]) -> None:
    """Apply standard headers to response (RL + trace ID)."""
    for k, v in _rl_headers().items():
        resp.headers[k] = v
    # Thread request ID / trace ID
    req_id = trace_id or uuid.uuid4().hex
    resp.headers["X-Request-Id"] = req_id
    resp.headers["X-Trace-Id"] = req_id


# ------------------------------------------------------------------------------
# /v1/models - Model catalog (OpenAI list envelope)
# ------------------------------------------------------------------------------
@router.get("/models")
def list_models(
    request: Request,
    response: Response,
    _claims=Depends(require_api_key),
) -> Dict[str, Any]:
    """List available models (OpenAI-compatible format)."""
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    _with_std_headers(response, trace_id)

    # Static catalog - extend from config if needed
    data = [
        {"id": "lukhas-mini", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
        {"id": "lukhas-embed-1", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
    ]
    return {"object": "list", "data": data}


# ------------------------------------------------------------------------------
# /v1/embeddings - Deterministic hash-based embeddings
# ------------------------------------------------------------------------------
def _hash_to_vec(text: str, dim: int = 128) -> List[float]:
    """
    Generate deterministic embedding from text using hash expansion.

    Uses SHA-256 hash as seed, expands to requested dimensions.
    Different inputs produce different vectors (deterministic).
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # Expand deterministically to dim floats in [0,1)
    nums: List[float] = []
    seed = bytearray(h)
    idx = 0
    while len(nums) < dim:
        chunk = hashlib.sha256(seed + bytes([idx & 0xFF])).digest()
        nums.extend([b / 255.0 for b in chunk])
        idx += 1
    return nums[:dim]


@router.post("/embeddings")
def create_embeddings(
    request: Request,
    response: Response,
    payload: Dict[str, Any] = Body(...),
    _claims=Depends(require_api_key),
) -> Dict[str, Any]:
    """
    Create deterministic embeddings (OpenAI-compatible format).

    Accepts:
    - model: str (optional, default: "lukhas-embed-1")
    - input: str | List[str] (required)

    Returns OpenAI-compatible embedding response with unique vectors.
    """
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    _with_std_headers(response, trace_id)

    model = payload.get("model", "lukhas-embed-1")
    inputs = payload.get("input", [])
    if isinstance(inputs, str):
        inputs = [inputs]

    # Generate unique deterministic embeddings
    vectors = [
        {
            "object": "embedding",
            "index": i,
            "embedding": _hash_to_vec(f"{model}:{txt}")
        }
        for i, txt in enumerate(inputs)
    ]

    return {
        "object": "list",
        "data": vectors,
        "model": model,
        "usage": {
            "prompt_tokens": sum(len(str(txt).split()) for txt in inputs),
            "total_tokens": sum(len(str(txt).split()) for txt in inputs)
        }
    }


# ------------------------------------------------------------------------------
# /v1/responses - Non-stream response generation (minimal stub)
# ------------------------------------------------------------------------------
@router.post("/responses")
def create_response(
    request: Request,
    response: Response,
    payload: Dict[str, Any] = Body(...),
    _claims=Depends(require_api_key),
) -> Dict[str, Any]:
    """
    Create response (OpenAI Responses API format, non-stream stub).

    Accepts:
    - model: str (optional)
    - input: str | dict | list (required)
    - stream: bool (optional, ignored for now)

    Returns minimal echo response with deterministic ID.
    """
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    _with_std_headers(response, trace_id)

    model = payload.get("model", "lukhas-mini")

    # Accept multiple input formats
    user_text = payload.get("input") or payload.get("messages") or payload.get("contents") or ""

    if isinstance(user_text, list):
        # Try to extract text from structured input
        try:
            user_text = next(
                (p.get("text") for m in user_text for p in (m.get("content") or []) if p.get("type") == "input_text"),
                ""
            )
        except Exception:
            user_text = ""

    if not isinstance(user_text, str):
        user_text = str(user_text)

    # Generate minimal echo response
    out_text = f"echo: {user_text}".strip() if user_text else "[empty input]"
    now = int(time.time())
    resp_id = f"resp_{uuid.uuid4().hex}"

    return {
        "id": resp_id,
        "object": "response",
        "created": now,
        "model": model,
        "output": [{"type": "output_text", "text": out_text}],
        "usage": {
            "input_tokens": len(user_text.split()) if user_text else 0,
            "output_tokens": len(out_text.split()),
            "total_tokens": len(user_text.split()) + len(out_text.split()) if user_text else len(out_text.split())
        }
    }
```

**Codex Commands**:

```python
# If file doesn't exist
Write(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py",
    content=<content above>
)

# If file exists, merge handlers using Edit tool
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py")
# Then add handlers that don't exist
```

---

## 2️⃣ PATCH B — Mount Router + Health Alias

**TOOL**: `Edit`

**Action**: Update `serve/main.py` to mount router and add `/health` alias

**File**: `serve/main.py`

```python
# TOOL: Read first to see current structure
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py")

# TOOL: Edit to add router import and mount
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="from fastapi import FastAPI",
    new_string="""from fastapi import FastAPI

# OpenAI-compatible routes
try:
    from serve.openai_routes import router as openai_router
except ImportError:
    openai_router = None"""
)

# TOOL: Edit to mount router after app creation
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="app = FastAPI(",
    new_string="""app = FastAPI("""
)

# Then add after app instantiation (find suitable location)
# Look for existing healthz endpoint and add health alias + router mount nearby
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="""@app.get("/healthz")
def healthz():
    return {"status": "ok"}""",
    new_string="""@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/health")
def health():
    \"\"\"Alias for /healthz (ops tooling compatibility).\"\"\"
    return healthz()


# Mount OpenAI-compatible router
if openai_router:
    app.include_router(openai_router)"""
)
```

**Codex Strategy**:

1. **Read** `serve/main.py` to understand current structure
2. Find FastAPI import section → **Edit** to add openai_routes import
3. Find healthz endpoint → **Edit** to add health alias below it
4. Add router mount after health alias → **Edit** or append

**Verification**:

```bash
# TOOL: Bash
python3 -c "from serve.main import app; print('✅ App imports successfully')"
python3 -c "from serve.main import app; print(f'✅ Routes: {[r.path for r in app.routes]}')"
```

---

## 3️⃣ Quick Verification — Endpoints Smoke Test

**TOOL**: `Bash`

```bash
# Start server in background
uvicorn serve.main:app --port 8000 &
SERVER_PID=$!
sleep 2

echo "🧪 Testing /v1/models..."
curl -s -H "Authorization: Bearer test-token" \
  localhost:8000/v1/models | jq '.object,.data[0].object'

echo "🧪 Testing /v1/embeddings..."
curl -s -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"model":"lukhas-embed-1","input":["hello","world"]}' \
  localhost:8000/v1/embeddings | jq '.object, .data|length'

echo "🧪 Testing /v1/responses..."
curl -s -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"model":"lukhas-mini","input":"hi there"}' \
  localhost:8000/v1/responses | jq '.object,.output[0].text'

echo "🧪 Testing /health alias..."
curl -s localhost:8000/health | jq '.status'

echo "🧪 Testing rate limit headers..."
curl -sI -H "Authorization: Bearer test-token" \
  localhost:8000/v1/models | grep -i "x-ratelimit"

# Cleanup
kill $SERVER_PID || true

echo ""
echo "✅ Wave A verification complete"
```

**Expected Output**:

```
🧪 Testing /v1/models...
"list"
"model"

🧪 Testing /v1/embeddings...
"list"
2

🧪 Testing /v1/responses...
"response"
"echo: hi there"

🧪 Testing /health alias...
"ok"

🧪 Testing rate limit headers...
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
x-ratelimit-limit-requests: 60

✅ Wave A verification complete
```

---

## 4️⃣ Run Smoke Tests

**TOOL**: `Bash`

```bash
# Run new smoke tests
pytest tests/smoke/test_models_openai_shape.py -v
pytest tests/smoke/test_responses_stub.py -v
pytest tests/smoke/test_openai_rl_headers.py -v
pytest tests/smoke/test_embeddings.py::test_embeddings_unique_different_inputs -v

# Full smoke suite
pytest tests/smoke/ -v --tb=short | tail -20

echo ""
echo "📊 Smoke test summary:"
pytest tests/smoke/ -q 2>&1 | tail -1
```

**Success Criteria**:
- ✅ All new smoke tests pass
- ✅ Smoke pass rate ≥ 90% (target: 200+ passed / 220+ total)
- ✅ No 404s on /v1/models, /v1/embeddings, /v1/responses
- ✅ Rate limit headers present on all responses

---

## 5️⃣ T4 Commit — Wave A Complete

**TOOL**: `Bash`

```bash
# Pre-Commit Gate
pytest tests/smoke/ -q || { echo "Smoke suite failing"; exit 1; }
make lane-guard || { echo "Lane guard failed"; exit 1; }
python3 -m py_compile serve/openai_routes.py serve/main.py || { echo "Syntax check failed"; exit 1; }

# Stage Wave A changes
git add serve/openai_routes.py serve/main.py

# Commit with T4 format
git commit -m "$(cat <<'EOF'
feat(api): add OpenAI-compatible /v1 endpoints (Wave A)

Problem:
- Missing OpenAI-compatible API endpoints (/v1/models, /v1/embeddings, /v1/responses)
- Embeddings returning all-zero vectors (non-deterministic stub)
- No rate limit or trace headers on responses
- RC soak scripts failing with 404s

Solution:
- Created serve/openai_routes.py with 3 endpoints:
  * /v1/models - Model catalog (OpenAI list envelope)
  * /v1/embeddings - Deterministic hash-based embeddings (SHA-256)
  * /v1/responses - Non-stream echo stub with OpenAI format
- Added rate limit headers (X-RateLimit-* + x-ratelimit-*-requests aliases)
- Thread X-Request-Id and X-Trace-Id through all responses
- Dev-permissive auth (Bearer token required, validation stubbed)
- Added /health alias for /healthz (ops tooling compatibility)

Impact:
- Smoke test pass rate: expected 61% → 90%+ (Wave A target)
- OpenAI API compatibility: 3 new endpoints operational
- Embeddings: Unique deterministic vectors (different inputs → different outputs)
- Rate limit headers: Present on all /v1/* responses
- RC soak: 404 errors eliminated for /v1 endpoints

Artifacts:
- serve/openai_routes.py (new, 250 LOC)
- serve/main.py (mount router + /health alias)

Next: Wave B (optional quota resolver + SSE streaming)

Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo "✅ Wave A committed"
```

---

## 6️⃣ Wave B Seeds (Optional) — Advanced Features

**Only proceed if modules already exist in repo**

### B-1: Wire Quota Resolver (Optional)

**Condition**: `core/reliability/quota_resolver.py` exists

**TOOL**: `Bash` to check, then `Edit`

```bash
# Check if quota resolver exists
if [ -f "core/reliability/quota_resolver.py" ]; then
  echo "✅ Quota resolver found - can wire into rate limits"
else
  echo "⏭️  Skipping Wave B-1 (quota resolver not found)"
  exit 0
fi
```

If exists:

```python
# TOOL: Edit serve/openai_routes.py
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py",
    old_string="""def _rl_headers() -> Dict[str, str]:
    \"\"\"Generate rate limit headers (stub values).\"\"\"
    now = int(time.time())
    return {""",
    new_string="""def _rl_headers(user_id: Optional[str] = None) -> Dict[str, str]:
    \"\"\"Generate rate limit headers (from quota resolver if available).\"\"\"
    now = int(time.time())

    # Try to use quota resolver if available
    try:
        from core.reliability.quota_resolver import get_rate_limit_info
        if user_id:
            limits = get_rate_limit_info(user_id)
            return {
                "X-RateLimit-Limit": str(limits.get("limit", 60)),
                "X-RateLimit-Remaining": str(limits.get("remaining", 59)),
                "X-RateLimit-Reset": str(limits.get("reset", now + 60)),
                "x-ratelimit-limit-requests": str(limits.get("limit", 60)),
                "x-ratelimit-remaining-requests": str(limits.get("remaining", 59)),
                "x-ratelimit-reset-requests": str(limits.get("reset", now + 60)),
            }
    except ImportError:
        pass

    # Fallback to stub values
    return {"""
)
```

**Commit**:

```bash
git add serve/openai_routes.py
git commit -m "feat(rate-limit): wire quota_resolver into OpenAI endpoints (Wave B-1)"
```

### B-2: SSE Streaming (Optional)

**Condition**: `matriz/core/async_orchestrator.py` exists

**TOOL**: `Bash` to check, then `Edit`

```bash
# Check if async orchestrator exists
if [ -f "matriz/core/async_orchestrator.py" ]; then
  echo "✅ Async orchestrator found - can enable SSE streaming"
else
  echo "⏭️  Skipping Wave B-2 (async orchestrator not found)"
  exit 0
fi
```

If exists:

```python
# TOOL: Edit serve/openai_routes.py
# Add streaming endpoint below create_response

Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py",
    old_string="from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response, status",
    new_string="from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response, status\nfrom fastapi.responses import StreamingResponse"
)

# Add streaming endpoint
# (Insert new endpoint after create_response - use Edit with appropriate anchor)
```

**Commit**:

```bash
git add serve/openai_routes.py
git commit -m "feat(responses): enable SSE streaming via async_orchestrator (Wave B-2)"
```

---

## 7️⃣ Acceptance Gates

**TOOL**: `Bash`

Run the acceptance verification runbook:

```bash
# Full acceptance gates
cat > /tmp/acceptance_gates.sh <<'RUNBOOK'
#!/bin/bash
set -euo pipefail

echo "🚀 Starting acceptance gates verification..."
echo

# Gate 1: /v1/models returns OpenAI list shape (200)
echo "✓ Gate 1: /v1/models endpoint"
pytest tests/smoke/test_models_openai_shape.py::test_models_list_shape -v --tb=no | grep -E "PASSED|FAILED" | head -1

# Gate 2: /v1/responses returns valid stub (200)
echo "✓ Gate 2: /v1/responses endpoint"
pytest tests/smoke/test_responses_stub.py::test_responses_stub_with_messages -v --tb=no | grep -E "PASSED|FAILED" | head -1

# Gate 3: /v1/embeddings returns non-zero deterministic vectors
echo "✓ Gate 3: /v1/embeddings unique vectors"
pytest tests/smoke/test_embeddings.py::test_embeddings_unique_different_inputs -v --tb=no 2>&1 | grep -E "PASSED|FAILED|test_embeddings" | head -1

# Gate 4: RL headers present on 200 & 401
echo "✓ Gate 4: Rate limit headers"
pytest tests/smoke/test_openai_rl_headers.py::test_rl_headers_on_success_models -v --tb=no | grep -E "PASSED|FAILED" | head -1

# Gate 5: Security headers present on /healthz
echo "✓ Gate 5: Security/trace headers"
pytest tests/smoke/test_openai_rl_headers.py::test_rl_headers_on_healthz -v --tb=no | grep -E "PASSED|FAILED" | head -1

# Gate 6: Smoke pass ≥90%
echo "✓ Gate 6: Smoke test pass rate"
pytest tests/smoke/ --tb=no -q 2>&1 | tail -1

# Gate 7: Health alias works
echo "✓ Gate 7: /health alias"
curl -sf localhost:8000/health > /dev/null && echo "PASSED" || echo "FAILED"

echo
echo "✅ Acceptance gates verification complete!"
RUNBOOK

chmod +x /tmp/acceptance_gates.sh
/tmp/acceptance_gates.sh
```

**Success Criteria**:
- ✅ All 7 gates PASSED
- ✅ Smoke pass rate ≥ 90%
- ✅ Curl commands return expected shapes
- ✅ Headers include X-Request-Id, X-RateLimit-*, x-ratelimit-*-requests

---

## 8️⃣ Notes for Codex

### Critical Guidelines

1. **No Deep Dependencies**: Keep changes inside `serve/` and reuse existing modules only if they exist
2. **Honor Error Envelope**: Return well-shaped OpenAI-compatible errors
3. **Don't Touch Guardian**: Use dev-permissive `require_api_key` for now
4. **Surgical Diffs**: Each patch should be minimal and reviewable
5. **Test Before Commit**: Run smoke tests after each patch
6. **Wave B is Optional**: Only wire quota/streaming if modules already exist

### Tool Usage Pattern

```python
# 1. Check what exists
Bash(command="ls -la serve/")
Glob(pattern="**/quota_resolver.py")

# 2. Read before editing
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py")

# 3. Make surgical changes
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="<exact match>",
    new_string="<replacement>"
)

# 4. Verify changes
Bash(command="python3 -c 'from serve.main import app; print(app.routes)'")

# 5. Test
Bash(command="pytest tests/smoke/test_models_openai_shape.py -v")

# 6. Commit
Bash(command="git add serve/ && git commit -m '...'")
```

### Error Recovery

If a patch fails:

```python
# Check current state
Bash(command="git status")
Bash(command="git diff serve/main.py")

# Reset if needed
Bash(command="git checkout -- serve/main.py")

# Try alternative approach (Read full file, then Edit with different anchor)
```

---

## 🧠 Reflection & Recovery

### Phase Reflection Protocol

After each step or phase (Preflight, Patch A, Patch B, Verify, Tests):
1. **Summarize outcome** in one sentence
2. **Compare to Mission Trace** `.expected_artifacts`
3. **If logic deviation > 10%** from expected state → revert and re-execute

### Controlled Recovery Mode

1. Log failure summary to `.codex_trace.json`
2. `git restore --staged . && git checkout -- .`
3. Re-read the last two modified files
4. Retry using explicit `Edit` anchors (exact strings)
5. Escalate to manual audit if the same failure repeats twice

---

## 9️⃣ Quick Reference Card

### Codex Execution Checklist

- [ ] **0. Preflight** → Detect entrypoint and existing files
- [ ] **1. PATCH A** → Create/update `serve/openai_routes.py`
- [ ] **2. PATCH B** → Mount router in `serve/main.py` + `/health` alias
- [ ] **3. Verify** → Curl smoke test (models, embeddings, responses, health)
- [ ] **4. Test** → Run pytest smoke tests
- [ ] **5. Commit** → T4 format (Wave A)
- [ ] **6. Wave B** → Optional quota + SSE (only if modules exist)
- [ ] **7. Gates** → Run full acceptance gates
- [ ] **8. Done** → Smoke pass rate ≥90%, RC soak green

### Key Endpoints

- `GET /v1/models` → OpenAI list envelope
- `POST /v1/embeddings` → Deterministic hash→vec
- `POST /v1/responses` → Non-stream echo stub
- `GET /health` → Alias for `/healthz`

### Headers Added

- `X-Request-Id` / `X-Trace-Id` → Request tracking
- `X-RateLimit-Limit/Remaining/Reset` → Standard RL headers
- `x-ratelimit-limit-requests/remaining-requests/reset-requests` → OpenAI aliases

---

## 🎯 Success Metrics

**Before Wave A**:
- Smoke pass rate: 61% (136/224)
- Missing endpoints: /v1/models, /v1/responses
- Embeddings: All-zero vectors
- RC soak: 404 errors on /v1/*

**After Wave A** (Target):
- Smoke pass rate: ≥90% (200+/220+)
- All endpoints operational
- Embeddings: Unique deterministic vectors
- RC soak: >95% success, no 404s
- Headers: RL + trace IDs on all responses

**After Wave B** (Optional):
- Quota resolver: Real RL limits per user
- SSE streaming: Enabled for `/v1/responses?stream=true`

---

**End of Codex Execution Package**

This package provides complete, surgical instructions for Codex to implement OpenAI-compatible endpoints with minimal risk and maximum test coverage. All changes are production-safe and reversible.
