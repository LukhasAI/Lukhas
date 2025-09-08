---
title: Phase 2 To 3 Promotion Plan
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "testing", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "identity"]
  audience: ["dev"]
---

# Phase 2→3 Promotion Plan: Three Minimal Slices

## 🎯 Objective

Promote three minimal, working slices into `lukhas/` (accepted lane), each with:
- Interfaces + builtin safe provider (no network/PII; works in DRY_RUN)
- Registry pattern (runtime plug-ins; no static imports from candidate/)
- Feature flag to enable real provider wiring later
- MATRIZ instrumentation on public APIs
- Unit + integration smoke tests
- MODULE_MANIFEST.json with SLAs & emit points

### Three Slices:
1. **Governance → Consent Ledger** (`record_consent`)
2. **Identity → Passkey Verify** (`verify_passkey`)
3. **Orchestration → Context Handoff** (`handoff_context`)

---

## 0️⃣ Branching & Safety

```bash
git checkout -b feature/promote-three-slices
export LUKHAS_DRY_RUN_MODE=true
export LUKHAS_OFFLINE=true
```

---

## 1️⃣ Shared Observability (Confirm Exists)

Ensure these exist from Phase 1:
- `lukhas/observability/matriz_emit.py`
- `lukhas/observability/matriz_decorators.py`

If missing, recreate from Phase-1 instructions.

---

## 2️⃣ Slice #1 — Governance / Consent Ledger

### 2.1 Create Structure
```bash
mkdir -p lukhas/governance/consent_ledger/{providers,tests}
touch lukhas/governance/consent_ledger/__init__.py
```

### 2.2 Files to Create

#### `lukhas/governance/consent_ledger/api.py`
```python
from typing import Dict, Any, Optional
import os, time, uuid
from lukhas.observability.matriz_decorators import instrument
from .registry import get_provider

FEATURE = os.getenv("FEATURE_GOVERNANCE_LEDGER", "false").lower() == "true"

@instrument("CONSENT", label="governance:record", salience=0.6, urgency=0.2)
def record_consent(user_id: str, scope: str, metadata: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    """
    Minimal, safe consent recording API.
    - Works in DRY_RUN/OFFLINE with builtin provider (no network)
    - When FEATURE_GOVERNANCE_LEDGER=true, registry may supply real provider
    """
    provider = get_provider(enabled=FEATURE)
    entry = {
        "trace_id": str(uuid.uuid4()),
        "ts": int(time.time()*1000),
        "user_id": user_id,
        "scope": scope,
        "metadata": metadata or {},
    }
    return provider.record(entry)
```

#### `lukhas/governance/consent_ledger/registry.py`
```python
from typing import Optional
from .providers.null_provider import NullConsentProvider
# Registry is intentionally internal. candidate/* may register via runtime hooks later.
_provider = None

def register(provider) -> None:
    global _provider
    _provider = provider

def get_provider(enabled: bool):
    # If not enabled, force Null provider (no side-effects)
    if not enabled or _provider is None:
        return NullConsentProvider()
    return _provider
```

#### `lukhas/governance/consent_ledger/providers/null_provider.py`
```python
from typing import Dict, Any

class NullConsentProvider:
    """Safe, local, ephemeral provider; no network, no PII leaks."""
    def record(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        # Echo entry with ack; real provider plugs in via registry later.
        return {"ok": True, "provider": "null", "entry": entry}
```

#### `lukhas/governance/consent_ledger/MODULE_MANIFEST.json`
```json
{
  "module": "lukhas.governance.consent_ledger",
  "owner": "@consent-compliance-specialist",
  "capabilities": ["record_consent"],
  "feature_flag": "FEATURE_GOVERNANCE_LEDGER",
  "dependencies": [],
  "slas": { "p95_ms": 50 },
  "matriz_emit_points": ["CONSENT:governance:record"],
  "acceptance_checklist": [
    "No static imports from candidate/",
    "MATRIZ decorated public APIs",
    "DRY_RUN/OFFLINE supported",
    "Unit & smoke tests present",
    "PII logging avoided"
  ]
}
```

#### `lukhas/governance/consent_ledger/tests/test_consent_api.py`
```python
import os
os.environ.setdefault("FEATURE_GOVERNANCE_LEDGER","false")

from lukhas.governance.consent_ledger.api import record_consent

def test_record_consent_null_provider_dryrun():
    out = record_consent("usr_123","gmail.read",{"just":"testing"})
    assert out["ok"] is True
    assert out["provider"] == "null"
    assert out["entry"]["user_id"] == "usr_123"
```

---

## 3️⃣ Slice #2 — Identity / Passkey Verify

### 3.1 Create Structure
```bash
mkdir -p lukhas/identity/passkey/{providers,tests}
touch lukhas/identity/passkey/__init__.py
```

### 3.2 Files to Create

#### `lukhas/identity/passkey/api.py`
```python
import os
from typing import Dict, Any
from lukhas.observability.matriz_decorators import instrument
from .registry import get_provider

FEATURE = os.getenv("FEATURE_IDENTITY_PASSKEY", "false").lower() == "true"

@instrument("DECISION", label="identity:passkey.verify", salience=0.5, urgency=0.8)
def verify_passkey(assertion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal, safe passkey verify.
    - Works with builtin provider (stub) in DRY_RUN
    - Real WebAuthn provider can be registered via registry when enabled
    """
    provider = get_provider(enabled=FEATURE)
    return provider.verify(assertion)
```

#### `lukhas/identity/passkey/registry.py`
```python
from .providers.null_webauthn import NullWebAuthnProvider
_provider = None

def register(provider) -> None:
    global _provider
    _provider = provider

def get_provider(enabled: bool):
    if not enabled or _provider is None:
        return NullWebAuthnProvider()
    return _provider
```

#### `lukhas/identity/passkey/providers/null_webauthn.py`
```python
from typing import Dict, Any

class NullWebAuthnProvider:
    """Local, deterministic verification; does NOT touch network or PII."""
    def verify(self, assertion: Dict[str, Any]) -> Dict[str, Any]:
        # Always accept in DRY_RUN; include minimal audit info
        return {"ok": True, "provider": "null", "challenge": assertion.get("challenge","dryrun")}
```

#### `lukhas/identity/passkey/MODULE_MANIFEST.json`
```json
{
  "module": "lukhas.identity.passkey",
  "owner": "@identity-auth-specialist",
  "capabilities": ["verify_passkey"],
  "feature_flag": "FEATURE_IDENTITY_PASSKEY",
  "dependencies": [],
  "slas": { "p95_ms": 30 },
  "matriz_emit_points": ["DECISION:identity:passkey.verify"],
  "acceptance_checklist": [
    "No static imports from candidate/",
    "MATRIZ decorated public APIs",
    "DRY_RUN/OFFLINE supported",
    "Unit & smoke tests present",
    "No PII logging"
  ]
}
```

#### `lukhas/identity/passkey/tests/test_passkey_api.py`
```python
import os
os.environ.setdefault("FEATURE_IDENTITY_PASSKEY","false")

from lukhas.identity.passkey.api import verify_passkey

def test_passkey_verify_null_provider_dryrun():
    out = verify_passkey({"challenge":"xyz"})
    assert out["ok"] is True
    assert out["provider"] == "null"
    assert out["challenge"] == "xyz"
```

---

## 4️⃣ Slice #3 — Orchestration / Context Handoff

### 4.1 Create Structure
```bash
mkdir -p lukhas/orchestration/context/tests
touch lukhas/orchestration/context/__init__.py
```

### 4.2 Files to Create

#### `lukhas/orchestration/context/api.py`
```python
import os, time
from typing import Dict, Any
from lukhas.observability.matriz_decorators import instrument

FEATURE = os.getenv("FEATURE_ORCHESTRATION_HANDOFF", "false").lower() == "true"

def _rate_limit_ok() -> bool:
    # Minimal placeholder; expand later
    return True

@instrument("CONTEXT", label="orchestration:handoff", salience=0.4, urgency=0.7)
def handoff_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal, safe context bus handoff.
    - In Phase 3, wire to bus providers via registry if FEATURE enabled
    """
    if not _rate_limit_ok():
        return {"ok": False, "reason": "rate_limited"}

    # DRY_RUN behavior: simply echo with timings
    t0 = time.monotonic()
    # (If FEATURE true, call provider registry here; keep out for first promotion)
    t1 = time.monotonic()
    return {
        "ok": True,
        "mode": "dryrun" if not FEATURE else "feature",
        "latency_ms": int((t1 - t0) * 1000),
        "context_size": len(str(ctx)) if ctx else 0
    }
```

#### `lukhas/orchestration/context/MODULE_MANIFEST.json`
```json
{
  "module": "lukhas.orchestration.context",
  "owner": "@context-orchestrator-specialist",
  "capabilities": ["handoff_context"],
  "feature_flag": "FEATURE_ORCHESTRATION_HANDOFF",
  "dependencies": [],
  "slas": { "p95_ms": 250 },
  "matriz_emit_points": ["CONTEXT:orchestration:handoff"],
  "acceptance_checklist": [
    "No static imports from candidate/",
    "MATRIZ decorated public APIs",
    "DRY_RUN/OFFLINE supported",
    "Unit & smoke tests present",
    "Backpressure/rate-limit path covered"
  ]
}
```

#### `lukhas/orchestration/context/tests/test_context_api.py`
```python
import os
os.environ.setdefault("FEATURE_ORCHESTRATION_HANDOFF","false")

from lukhas.orchestration.context.api import handoff_context

def test_handoff_context_dryrun():
    out = handoff_context({"foo":"bar"})
    assert out["ok"] is True
    assert out["mode"] == "dryrun"
    assert out["latency_ms"] >= 0
```

---

## 5️⃣ Run Verification Locally (SHA-bound)

```bash
make verify
pytest -q lukhas/governance/consent_ledger/tests \
        lukhas/identity/passkey/tests \
        lukhas/orchestration/context/tests
```

**Expected:** All tests pass in DRY_RUN, gate clean.

---

## 6️⃣ Commit, Push, Open PRs

```bash
git add -A
git commit -m "feat(phase3): promote minimal slices (consent ledger, passkey verify, context handoff); manifests + MATRIZ + tests"
git push -u origin feature/promote-three-slices
```

Open three PRs (one per slice) using PR templates:
- `.github/pull_request_template/consent_ledger.md`
- `.github/pull_request_template/identity_passkey.md`
- `.github/pull_request_template/orchestration_context.md`

Each PR must include:
- SHA-bound artifacts path from Actions (e.g., `phase1-artifacts-<sha>`)
- Test counts & p95 latency numbers from artifact bundle
- Checkboxes ticked (manifest present, MATRIZ emit verified, no candidate imports, etc.)

---

## 7️⃣ How Real Providers Will Join (Later)

- Real implementations remain under `candidate/.../providers/*.`
- They register at runtime by calling the registry `register(...)` inside a guarded init when the feature flag is ON
- The accepted lane **NEVER** imports `candidate/...` statically

### Example (later, in `candidate/governance/providers/cloud_ledger.py`):
```python
from lukhas.governance.consent_ledger.registry import register

class CloudConsentProvider:
    def record(self, entry):
        # Real implementation here
        pass

def _wire():
    register(CloudConsentProvider())

if __name__ == "__main__":
    _wire()
```

Your deployment/bootstrap will invoke `_wire()` only in the correct tier, never during unit tests.

---

## 8️⃣ Rollback (if any PR regresses)

Click "Revert" on the PR, or:
```bash
git revert <merge_commit_sha> -m 1
```

The SHA-bound artifacts + `LUKHAS_SYSTEM_STATUS.md` tell you exactly what changed.

---

## 9️⃣ Success Criteria for Each PR

- ✅ **Acceptance gate:** PASS
- ✅ **No candidate|quarantine|archive imports** in lukhas/
- ✅ **MATRIZ events emitted** at specified API boundaries
- ✅ **Dry-run behavior deterministic;** tests green
- ✅ **MODULE_MANIFEST.json** present & accurate
- ✅ **CI artifact bundle** uploaded for the PR SHA

---

## 🔟 After These Three Promotions

1. **Enable canary runs** (flagged) in staging for each slice
2. **Add rate-limit/backpressure tests** to orchestration
3. **For Identity,** add a second provider stub (e.g., `fido2_mock`) and demonstrate provider swap via registry + flag in CI (still no external calls)

---

## 📋 TL;DR for Claude Code

1. **Create files above verbatim**
2. `make verify` → ensure pass
3. **Commit, push, open 3 PRs** (one per slice) with SHA artifact links
4. **Do not import from candidate/** anywhere under lukhas/
5. **Keep real providers in candidate/** and register at runtime only under feature flags

---

## 🔐 Critical Rules

- **NO static imports** from candidate/quarantine/archive in any lukhas/ file
- **All public APIs** must have MATRIZ instrumentation
- **All providers** must work safely in DRY_RUN mode
- **All feature flags** default to FALSE
- **All tests** must pass without network or external dependencies
- **Every slice** gets its own MODULE_MANIFEST.json with SLAs
