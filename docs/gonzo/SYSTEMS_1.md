
---

# 1) ABAS: EU consent & minors gate for ads (OPA policy + CI)

**Title**
ABAS: Implement EU consent & minors gate for ads (Rego + CI)

**Labels**
`area:abas` `type:policy` `security` `compliance` `priority:high`

**Body**
**Goal:** Add an OPA/Rego policy that enforces EU-safe advertising rules: block personalized ads to minors, block use of sensitive signals (special categories), and require TCF v2.2 consent (P3, P4, P1) for personalization in EU. Add CI to run `opa test` on PRs.

**Files to add**

* `enforcement/abas/policy.rego`
* `enforcement/abas/policy_test.rego`
* `.github/workflows/policy-opa.yml`

**Policy summary**

* Default deny.
* Contextual allowed in EU if not using sensitive signals and not minors.
* Personalized allowed only when: not minor, not sensitive, and consent shows P3 & P4 & P1 (EU). For non-EU, allow unless minors/sensitive.
* Provide a `reason` result for denial messages.

**Acceptance criteria (Done when)**

* `opa test enforcement/abas -v` passes in CI for the provided tests.
* Policy denies personalized ad calls in EU when TC string is missing, when is_minor=true, or when `using_sensitive_signals=true`.
* Policy permits contextual ad calls in EU when `using_sensitive_signals=false` and `is_minor=false`.
* The policy returns human-readable `reason` strings for denials (e.g., `blocked: minors cannot receive targeted ads`).

**Suggested estimate**
3–4 hours (policy + tests + CI).

**Notes / Risk**

* This policy intentionally errs on the side of safety for EU; do not change P3/P4 checks without legal review.

---

# 2) NIAS: Middleware → OPA PDP (NIASPolicyMiddleware)

**Title**
NIAS: Add NIASPolicyMiddleware that queries ABAS/OPA for ad requests

**Labels**
`area:nias` `type:middleware` `security` `integration`

**Body**
**Goal:** Implement a FastAPI/Starlette middleware `NIASPolicyMiddleware` to guard all NIAS/ads routes. The middleware should: extract minimal consent/region/age/sensitive flags from request headers/cookies, build an `input` payload for OPA, call the ABAS PDP (`/v1/data/abas/ads/allow`), and enforce allow/deny. Fail-closed for personalized requests when configured.

**Files to add**

* `nias/middleware.py` (NIASPolicyMiddleware)
* Wire into app factory: add `app.add_middleware(NIASPolicyMiddleware)` in `get_app()` or `setup_middlewares`.

**Behavior**

* Only applies to routes starting with `/nias/` or `/ads/`.
* Reads headers: `X-Region`, `X-Targeting-Mode` (default `contextual`), `X-Age-Verified` (`minor`), `cookie` for TC string, and `X-Using-Sensitive`.
* Posts to `OPA_URL` (`env: OPA_URL`) and respects `NIAS_FAILCLOSE_PERSONALIZED` (`true` → 503/403 if PDP unreachable for personalized).

**Acceptance criteria**

* For `/nias/serve` POST with `X-Region: EU` + `X-Targeting-Mode: personalized` and no consent, middleware must block (403 or 503 per env).
* For `/nias/serve` POST with `X-Region: EU` + `X-Targeting-Mode: contextual` and no sensitive flags → request allowed.
* Middleware must not block non-NIAS routes.
* Round-trip latency measured: p50 overhead < 5–10ms (approx) when OPA local; middleware must be asynchronous and non-blocking for allowed requests.

**Tests**

* `tests/nias/test_policy.py` (covers personalized denied without consent, contextual allowed).

**Suggested estimate**
3–5 hours (middleware + wiring + tests).

---

# 3) Consent parsing (TCF v2.2) — ConsentContext

**Title**
NIAS: Implement server-side TCF v2.2 consent parsing (ConsentContext)

**Labels**
`area:nias` `type:feature` `compliance` `priority:high`

**Body**
**Goal:** Server-side decoder that reads TCF v2.2 TC strings from cookies or headers and returns a `ConsentContext` (region, tcf_present, P1/P3/P4 booleans, is_minor, using_sensitive_signals). Use `iab-tcf` if available; fall back to safe defaults (all false).

**Files to add**

* `nias/core/consent.py`
* Unit tests for both the `iab-tcf` present and not-present cases (`tests/nias/test_consent.py`).

**Acceptance criteria**

* `consent_from_request(headers)` correctly extracts:

  * `region` from header or default `NIAS_DEFAULT_REGION`.
  * `tcf_present` true if TC string exists.
  * `p1`, `p3`, `p4` booleans when `iab-tcf` is installed and decoding works.
  * `is_minor` when `X-Age-Verified: minor`.
* If `iab-tcf` missing or decode fails, function returns `p1/p3/p4` as `False` (safe default) and does not crash.

**Suggested estimate**
1–2 hours.

**Notes**

* Don’t log TC strings. If storing proof-of-consent, store salted hashes and TTL-only references.

---

# 4) NIAS: Contextual fallback endpoint (`POST /nias/serve`)

**Title**
NIAS: Create contextual ad serve endpoint (EU-safe default)

**Labels**
`area:nias` `type:endpoint` `privacy` `priority:high`

**Body**
**Goal:** Implement a minimal ad serving endpoint that **never** reads raw device identifiers or profile PII for EU traffic. By default: contextual-only creative selection using `page_context` (topic, category) and `slot_ids`. Personalized selection gated by NIASPolicyMiddleware/ABAS.

**Files to add**

* `nias/endpoints.py` (APIRouter `POST /nias/serve` and `GET /nias/ping`)
* Wire router into app factory (e.g., `app.include_router(nias_router)`).

**Behavior**

* If `X-Targeting-Mode: contextual` → select and return `creative` based only on provided `page_context`.
* If `X-Targeting-Mode: personalized` → endpoint only executed when middleware allowed; otherwise middleware blocks.
* Return structured JSON: `{ mode, creative, explanations }`. Explanations must indicate EU-safe behavior when contextual.

**Acceptance criteria**

* POST `/nias/serve` with `X-Region: EU` and no consent returns HTTP 200 with `mode: contextual`.
* No request handler touches cookies, device IDs, or TC strings (middleware handles gating).
* Unit tests assert contextual behavior and no PII in logs/response.

**Suggested estimate**
1–2 hours.

---

# 5) NIAS_AUDIT: Privacy-safe event stream (JSONL)

**Title**
NIAS_AUDIT: Add privacy-safe NIAS audit writer (JSONL)

**Labels**
`area:audits` `type:logging` `privacy` `priority:medium`

**Body**
**Goal:** Implement a lightweight audit writer that records aggregated NIAS events (no TC strings or IDs) to `audits/nias_events.jsonl` with salted pseudonymization only if unavoidable. Provide rotated salt env var and guidelines.

**Files to add**

* `audits/nias_audit.py` (class `NIASAuditEvent`, `write_event(evt)`).
* Hook `write_event` in `nias/endpoints.py` after selection to log `{ ts, route, mode, region, policy, status_code, slot_count }`.

**Acceptance criteria**

* Events are appended to `audits/nias_events.jsonl` with minimal metadata.
* No raw TC string, cookie, or device id is written.
* If pseudonymization used, it is HMAC with `NIAS_AUDIT_SALT` and only first 16 hex chars; salt must be rotated via env var.
* Tests assert that audit file contains one JSON line after calling `/nias/serve` and the line has only allowed fields.

**Suggested estimate**
1–2 hours.

**Notes**

* Consider migrating JSONL → Postgres later (NIAS_AUDIT table) for analytics; ensure GDPR DPIA before storing hashed identifiers.

---

# 6) Security headers middleware (OWASP minimum)

**Title**
Security: Add OWASP minimum HTTP security headers middleware

**Labels**
`area:security` `type:middleware` `priority:medium`

**Body**
**Goal:** Add a Starlette middleware that injects minimal OWASP-recommended headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and a conservative `Content-Security-Policy`. Add a test asserting presence on a public route.

**Files to add**

* `lukhas/middleware/security_headers.py`
* Wire: `app.add_middleware(SecurityHeaders)` in `get_app()` (apply earliest).
* `tests/dast/test_security_headers.py`

**Acceptance criteria**

* Requests to `/v1/models` or `/nias/ping` include `X-Content-Type-Options` and `Content-Security-Policy`.
* Tests pass in CI.

**Suggested estimate**
30–60 minutes.

**Notes**

* CSP is intentionally conservative; update after Swagger/UI asset plan.

---

# 7) DAST: ZAP Baseline (PR), ZAP Full+API (nightly), Schemathesis

**Title**
DAST: Add ZAP Baseline PR, ZAP Full & API nightly, and Schemathesis jobs

**Labels**
`area:dast` `ci` `security` `priority:high`

**Body**
**Goal:** Add three GitHub Actions workflows:

1. **ZAP Baseline**: run on PRs against local uvicorn app; upload HTML report; fail on High vulnerabilities.
2. **ZAP Full & API**: nightly spider + active scan + OpenAPI API scan against `/openapi.json`.
3. **Schemathesis**: nightly property-based fuzzing from `/openapi.json` with JUnit+HTML reports.

**Files to add**

* `.github/workflows/dast-zap-baseline.yml`
* `.github/workflows/dast-zap-full-api.yml`
* `.github/workflows/dast-schemathesis.yml`
* `dast/.zap/rules.tsv` (optional suppressions)

**Acceptance criteria**

* PR triggers ZAP Baseline and uploads artifacts.
* Nightly runs produce ZAP HTML artifacts and Schemathesis JUnit + HTML.
* ZAP baselines configured to fail on High severity findings.
* Schemathesis produces `schemathesis.junit.xml` artifact.

**Suggested estimate**
2–4 hours (CI tuning).

**Notes**

* Ensure CI has `pip install -e .` and boots the app via `uvicorn <factory> --factory`.
* If private Swagger, set auth headers to avoid false positives.

---

# 8) Docs: NIAS_PLAN.md + EU_COMPLIANCE.md

**Title**
Docs: Add `docs/nias/NIAS_PLAN.md` and `docs/nias/EU_COMPLIANCE.md`

**Labels**
`area:docs` `compliance` `priority:medium`

**Body**
**Goal:** Add two short docs describing NIAS architecture, legal posture, data handling rules, and MVP metrics. Include a mermaid diagram and a short checklist for developers (no raw TC strings in logs, pseudonymization guidance, env flags).

**Files to add**

* `docs/nias/NIAS_PLAN.md`
* `docs/nias/EU_COMPLIANCE.md`

**Acceptance criteria**

* Docs contain the NIAS modes (contextual vs personalized), architecture diagram, legal anchors (DSA, ePrivacy, TCF v2.2), and dev checklist.
* Docs referenced by the ABAS / NIAS issues.

**Suggested estimate**
1–2 hours.

---

# 9) Meta: PR checklist + environment flags

**Title**
NIAS/ABAS/DAST PR checklist & environment flags

**Labels**
`area:process` `devops` `priority:low`

**Body**
**Goal:** Add a short PR checklist and environment variable guide in repo root (e.g., `docs/NIAS_PR_CHECKLIST.md`) listing required env flags and CI knobs:

**ENV**

```
NIAS_DEFAULT_REGION=EU
NIAS_FAILCLOSE_PERSONALIZED=true
OPA_URL=http://127.0.0.1:8181/v1/data/abas/ads/allow
OPA_REASON_URL=http://127.0.0.1:8181/v1/data/abas/ads/reason
NIAS_AUDIT_SALT=rotate-me
```

**Acceptance criteria**

* Checklist merged and referenced in relevant issues.

**Suggested estimate**
30–60 minutes.

---

## Paste-ready checklist for Claude Code Web

When creating tasks in Claude Code Web, paste the **Title** as the issue title and the **Body** as the issue body. Use the Labels provided. For `assignee` leave blank or assign yourself.

---

## Final notes (legal & privacy)

* **Do not** log TC strings, raw cookies, or device fingerprints. If you must store proof-of-consent, store only HMAC-salted hashes with TTL.
* **Minors & special categories**: ABAS denies targeted ads; the policy is intentionally conservative. Any change requires legal review.
* **Testing**: Keep OPA and ZAP locally available for full CI runs. `opa test` must be used on PRs to validate policy changes.

---
Nice — below are the **complete, ready-to-paste files** (code, tests, CI workflows, docs) we discussed. I included small usage / shell tips at the end of each Python file so you can run and iterate quickly. After you paste these, the main remaining step is to **wire the middlewares** into your FastAPI factory (`lukhas.adapters.openai.api:get_app`) — I included that patch snippet at the end.

**Short summary (2 sentences).**
These files implement ABAS (OPA/Rego), NIAS (consent parser, middleware, endpoints, privacy-safe audit), security headers, DAST CI (ZAP + Schemathesis), tests, and docs. All code defaults to EU-safe behavior (contextual by default; personalization needs explicit TCF v2.2 consent; minors & sensitive signals denied).

**Grounded vs speculative**

* **Grounded:** OPA/rego approach, DAST jobs (ZAP, Schemathesis), TCF v2.2 consent checks, security headers, JSONL audit pattern.
* **Speculative (conservative):** exact header names (`X-Region`, `X-Targeting-Mode`, `X-Age-Verified`, etc.), route `/nias/serve`, and path names (easy to rename).

---

## Files (paste each file to the path shown)

---

### `enforcement/abas/policy.rego`

```rego
package abas.ads

# Default deny
default allow = false

# Human friendly reason when deny triggers
reason = msg {
  not allow
  msg := cond_msg
}

# Block flags
block_minors {
  input.is_minor == true
}

block_sensitive {
  input.using_sensitive_signals == true
}

# Determine legal basis: EU requires explicit TCF v2.2 consent for personalization
legal_basis_eu {
  input.region == "EU"
  input.consent.tcf_present == true
  input.consent.p3 == true
  input.consent.p4 == true
  input.consent.storage_p1 == true
}

# Non-EU: allow personalized unless minors or sensitive
legal_basis_non_eu {
  input.region != "EU"
  not block_minors
  not block_sensitive
}

# Contextual allowed in general if not minors/sensitive
allow {
  input.targeting_mode == "contextual"
  not block_minors
  not block_sensitive
}

# Personalized allowed only with legal basis
allow {
  input.targeting_mode == "personalized"
  not block_minors
  not block_sensitive
  (legal_basis_eu or legal_basis_non_eu)
}

# Denial message routing
cond_msg = "blocked: minors cannot receive targeted ads" {
  block_minors
}

cond_msg = "blocked: sensitive data cannot be used for ads" {
  block_sensitive
}

cond_msg = "blocked: consent missing for personalization (TCF v2.2 P3/P4/P1)" {
  input.region == "EU"
  not legal_basis_eu
}

cond_msg = "blocked: default-deny" {
  true
}
```

---

### `enforcement/abas/policy_test.rego`

```rego
package abas.ads

test_contextual_ok {
  data.abas.ads.allow with input as {
    "region": "EU",
    "targeting_mode": "contextual",
    "is_minor": false,
    "using_sensitive_signals": false
  }
}

test_personalized_denied_without_consent_EU {
  not data.abas.ads.allow with input as {
    "region": "EU",
    "targeting_mode": "personalized",
    "is_minor": false,
    "using_sensitive_signals": false,
    "consent": {"tcf_present": false}
  }
}

test_personalized_ok_with_consent_EU {
  data.abas.ads.allow with input as {
    "region": "EU",
    "targeting_mode": "personalized",
    "is_minor": false,
    "using_sensitive_signals": false,
    "consent": {"tcf_present": true, "p3": true, "p4": true, "storage_p1": true}
  }
}

test_minors_denied_personalized {
  not data.abas.ads.allow with input as {
    "region": "EU",
    "targeting_mode": "personalized",
    "is_minor": true,
    "using_sensitive_signals": false,
    "consent": {"tcf_present": true, "p3": true, "p4": true, "storage_p1": true}
  }
}
```

---

### `.github/workflows/policy-opa.yml`

```yaml
name: ABAS - OPA Policy Tests
on:
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  opa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install OPA
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
          chmod +x opa && sudo mv opa /usr/local/bin/opa
      - name: Run OPA tests
        run: |
          opa test enforcement/abas -v
```

---

### `nias/core/consent.py`

```python
"""
nias.core.consent

Server-side helper to extract TCF v2.2 consent bits and basic consent context.

Design notes:
- Safe defaults: if we cannot decode a TC string, we return False for P1/P3/P4.
- Do NOT log raw TC strings. If you need to store consent proof, store HMAC(salt, tc_string) + TTL.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
import http.cookies

@dataclass
class ConsentContext:
    region: str = "EU"                 # "EU" | "ROW"
    tcf_present: bool = False
    p1: bool = False                   # storage / device consent
    p3: bool = False                   # create personalized profile
    p4: bool = False                   # select personalized ads
    vendors_ok: Dict[str, bool] = None
    is_minor: bool = False
    using_sensitive_signals: bool = False

def _parse_cookie_header(cookie_header: Optional[str]) -> Dict[str, str]:
    if not cookie_header:
        return {}
    c = http.cookies.SimpleCookie()
    c.load(cookie_header)
    return {k: morsel.value for k, morsel in c.items()}

def _decode_tcf(tc_string: str):
    """
    Try to decode TCF v2.2 TC string using `iab-tcf` if available.
    Returns tuple (p1, p3, p4) boolean flags.
    If decoding fails or library not installed, return (False, False, False).
    """
    try:
        # The iab-tcf library APIs vary; attempt common import pattern.
        from iab_tcf import decode_v2  # type: ignore
        consent = decode_v2(tc_string)
        # Many libs expose purposes as consent.core.purposes_consent or consent.purposes
        p = {}
        if hasattr(consent, "core") and hasattr(consent.core, "purposes_consent"):
            p = getattr(consent.core, "purposes_consent") or {}
        elif hasattr(consent, "purposes_consent"):
            p = getattr(consent, "purposes_consent") or {}
        elif hasattr(consent, "purposes"):
            # fallback mapping
            p = getattr(consent, "purposes") or {}

        # p is expected to be mapping int->bool or str->bool; normalize
        p1 = bool(p.get(1) or p.get("1"))
        p3 = bool(p.get(3) or p.get("3"))
        p4 = bool(p.get(4) or p.get("4"))
        return (p1, p3, p4)
    except Exception:
        return (False, False, False)

def consent_from_request(headers: Dict[str, str]) -> ConsentContext:
    """
    Build ConsentContext from request headers (or cookies).
    Expected headers:
      - X-Region: EU|ROW (optional, defaults to NIAS_DEFAULT_REGION or EU)
      - X-Age-Verified: "minor" | something else (optional)
      - cookie: may include euconsent-v2 or euconsent-v2 token
      - X-IABTCF_TCString or X-TCF-String (optional)
      - X-Using-Sensitive: "true"/"false" (optional)
    """
    region = headers.get("X-Region", os.getenv("NIAS_DEFAULT_REGION", "EU")).upper()
    is_minor = headers.get("X-Age-Verified", "").lower() == "minor"
    tc = (
        headers.get("X-IABTCF_TCString")
        or headers.get("X-TCF-String")
        or _parse_cookie_header(headers.get("cookie", "")).get("euconsent-v2")
    )
    p1, p3, p4 = _decode_tcf(tc) if tc else (False, False, False)
    return ConsentContext(
        region=region,
        tcf_present=bool(tc),
        p1=p1,
        p3=p3,
        p4=p4,
        vendors_ok={},
        is_minor=is_minor,
        using_sensitive_signals=(headers.get("X-Using-Sensitive", "").lower() == "true")
    )

# ---------------------------
# Usage / quick test (local)
# ---------------------------
# pip install iab-tcf   # optional, safe to run without it
# python -c "from nias.core.consent import consent_from_request; print(consent_from_request({'X-Region':'EU','cookie':'euconsent-v2=FAKE'}))"
```

---

### `nias/middleware.py`

```python
"""
NIASPolicyMiddleware

Guards /nias/ and /ads/ routes by querying ABAS/OPA PDP (enforcement/abas/policy.rego).
Failure modes:
 - If OPA is unreachable and targeting_mode == 'personalized' and NIAS_FAILCLOSE_PERSONALIZED=true -> 503/403
 - Otherwise degrade to contextual (if allowed below) or pass-through for contextual.
"""

import os
import json
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from .core.consent import consent_from_request

OPA_URL = os.getenv("OPA_URL", "http://127.0.0.1:8181/v1/data/abas/ads/allow")
OPA_REASON_URL = os.getenv("OPA_REASON_URL", "http://127.0.0.1:8181/v1/data/abas/ads/reason")
FAILCLOSE = os.getenv("NIAS_FAILCLOSE_PERSONALIZED", "true").lower() == "true"

class NIASPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = str(request.url.path)
        if not (path.startswith("/nias/") or path.startswith("/ads/")):
            # Non-NIAS paths bypass.
            return await call_next(request)

        targeting_mode = request.headers.get("X-Targeting-Mode", "contextual").lower()
        cctx = consent_from_request(dict(request.headers))

        payload = {
            "input": {
                "region": cctx.region,
                "targeting_mode": targeting_mode,
                "is_minor": cctx.is_minor,
                "using_sensitive_signals": cctx.using_sensitive_signals,
                "consent": {
                    "tcf_present": cctx.tcf_present,
                    "p3": cctx.p3,
                    "p4": cctx.p4,
                    "storage_p1": cctx.p1
                }
            }
        }

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.post(OPA_URL, json=payload)
                resp.raise_for_status()
                allow = resp.json().get("result", False)
                if not allow:
                    # attempt to fetch a reason (non-essential)
                    try:
                        r2 = await client.post(OPA_REASON_URL, json=payload, timeout=1.0)
                        reason = r2.json().get("result", "policy_denied")
                    except Exception:
                        reason = "policy_denied"
                    return JSONResponse({"error": {"message": reason, "type": "policy_denied"}}, status_code=403)
        except Exception:
            # OPA unreachable or error:
            if targeting_mode == "personalized" and FAILCLOSE:
                return JSONResponse({"error": {"message": "policy unavailable", "type": "policy_error"}}, status_code=503)
            # otherwise allow contextual degradation
            # continue to handler

            # NOTE: don't leak OPA failure details to client.
        return await call_next(request)

# ---------------------------
# Usage / wiring
# ---------------------------
# In your FastAPI factory (e.g., lukhas.adapters.openai.api:get_app), add:
#
#   from nias.middleware import NIASPolicyMiddleware
#   app.add_middleware(NIASPolicyMiddleware)
#
# Recommended env:
# NIAS_DEFAULT_REGION=EU
# NIAS_FAILCLOSE_PERSONALIZED=true
# OPA_URL=http://127.0.0.1:8181/v1/data/abas/ads/allow
# OPA_REASON_URL=http://127.0.0.1:8181/v1/data/abas/ads/reason
#
# Run OPA locally for integration:
# opa run --server -a :8181
```

---

### `nias/endpoints.py`

```python
"""
Minimal NIAS endpoints (contextual-first ad serving).
This handler intentionally avoids reading or persisting any user identifiers for EU traffic.
"""

from fastapi import APIRouter, Header, Request
from typing import Optional, List, Dict, Any
from audits.nias_audit import NIASAuditEvent, write_event

router = APIRouter(prefix="/nias", tags=["nias"])

@router.get("/ping")
def ping():
    return {"ok": True}

@router.post("/serve")
def serve_ad(
    request: Request,
    X_Targeting_Mode: Optional[str] = Header(default="contextual"),
    slot_ids: Optional[List[str]] = None,
    page_context: Optional[Dict[str, Any]] = None
):
    """
    Serve an ad with contextual-only default. The selector MUST NOT read cookies/device IDs;
    middleware enforces gating for personalization.
    """
    mode = (X_Targeting_Mode or "contextual").lower()
    topic = (page_context or {}).get("topic", "general")
    creative = f"contextual-{topic}"

    resp = {
        "mode": mode,
        "creative": creative,
        "explanations": ["contextual targeting only (EU-safe)"] if mode == "contextual" else ["personalized (policy-allowed)"],
    }

    # Audit minimal metadata
    try:
        evt = NIASAuditEvent(
            route=str(request.url.path),
            mode=mode,
            region=(request.headers.get("X-Region") or "EU"),
            policy="abas.ads",
            status_code=200,
            slot_count=len(slot_ids) if slot_ids else 0
        )
        write_event(evt)
    except Exception:
        # Audit must not break response
        pass

    return resp

# ---------------------------
# Usage / wiring
# ---------------------------
# In your get_app() factory:
#
#   from nias.endpoints import router as nias_router
#   app.include_router(nias_router)
#
# Example:
# curl -X POST http://127.0.0.1:8000/nias/serve -H "X-Region: EU" -H "Content-Type: application/json" \
#      -H "X-Targeting-Mode: contextual" -d '{"page_context": {"topic":"tech"}}'
```

---

### `audits/nias_audit.py`

```python
"""
Privacy-safe NIAS audit writer.

Writes JSONL lines to audits/nias_events.jsonl with minimal metadata.
Never write TC strings, cookies, or identifiers.
If pseudonymization is needed, HMAC with NIAS_AUDIT_SALT is used.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import hashlib, hmac, os, json

_SALT = os.getenv("NIAS_AUDIT_SALT", "rotate-me")

def _pseudonymize(s: str) -> str:
    return hmac.new(_SALT.encode(), s.encode(), hashlib.sha256).hexdigest()[:16]

class NIASAuditEvent(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    route: str
    mode: str
    region: str
    policy: str
    status_code: int
    slot_count: int = 0

def write_event(evt: NIASAuditEvent):
    path = os.getenv("NIAS_AUDIT_LOG", "audits/nias_events.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(evt.model_dump_json() + "\n")

# ---------------------------
# Usage
# ---------------------------
# Example (manual):
# python -c "from audits.nias_audit import NIASAuditEvent, write_event; evt=NIASAuditEvent(route='/nias/serve',mode='contextual',region='EU',policy='abas.ads',status_code=200); write_event(evt)"
```

---

### `lukhas/middleware/security_headers.py`

```python
"""
Minimal OWASP HTTP security headers middleware.
"""

from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        resp = await call_next(request)
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        resp.headers.setdefault("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
        return resp

# ---------------------------
# Usage / wiring
# ---------------------------
# In your get_app():
#   from lukhas.middleware.security_headers import SecurityHeaders
#   app.add_middleware(SecurityHeaders)
```

---

### `tests/nias/test_policy.py`

```python
import os
from fastapi.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_personalized_denied_in_eu_without_consent():
    os.environ["NIAS_FAILCLOSE_PERSONALIZED"] = "true"
    app = get_app()
    client = TestClient(app)
    r = client.post("/nias/serve", headers={"X-Region": "EU", "X-Targeting-Mode": "personalized"})
    assert r.status_code in (403, 503)

def test_contextual_ok():
    os.environ["NIAS_FAILCLOSE_PERSONALIZED"] = "true"
    app = get_app()
    client = TestClient(app)
    r = client.post("/nias/serve", headers={"X-Region": "EU"}, json={"page_context": {"topic": "tech"}})
    assert r.status_code == 200
    assert r.json().get("mode") == "contextual"
```

---

### `tests/nias/test_consent.py`

```python
from nias.core.consent import consent_from_request

def test_consent_no_tc():
    headers = {"X-Region": "EU"}
    c = consent_from_request(headers)
    assert c.region == "EU"
    assert c.tcf_present is False
    assert not c.p1 and not c.p3 and not c.p4

def test_consent_with_fake_decoder(monkeypatch):
    # Monkeypatch the decode_v2 function to simulate iab-tcf library
    class FakeConsentCore:
        purposes_consent = {1: True, 3: True, 4: False}
    class FakeConsent:
        core = FakeConsentCore()

    def fake_decode(tc):
        return FakeConsent()

    monkeypatch.setattr("nias.core.consent.decode_v2", fake_decode, raising=False)
    headers = {"X-IABTCF_TCString": "FAKE"}
    c = consent_from_request(headers)
    # _decode_tcf expects to find p1,p3,p4 from fake; our fake maps 1 True, 3 True, 4 False
    assert c.tcf_present is True
    assert c.p1 is True
    assert c.p3 is True
    assert c.p4 is False
```

---

### `tests/dast/test_security_headers.py`

```python
from fastapi.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_security_headers_present():
    app = get_app()
    client = TestClient(app)
    r = client.get("/v1/models")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert "default-src" in r.headers.get("Content-Security-Policy", "")
```

> **Note:** tests assume `get_app()` exists at `lukhas.adapters.openai.api:get_app`. If your factory is named differently, update the imports accordingly.

---

### `.github/workflows/dast-zap-baseline.yml`

```yaml
name: DAST - ZAP Baseline (PR)
on:
  pull_request:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  security-events: write

jobs:
  zap-baseline:
    runs-on: ubuntu-latest
    timeout-minutes: 40
    services:
      postgres:
        image: postgres:15
        ports: ['5432:5432']
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=5s --health-timeout=5s --health-retries=10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install app
        run: |
          pip install -e .
      - name: Boot API (background)
        run: |
          nohup python -m uvicorn lukhas.adapters.openai.api:get_app --factory --host 0.0.0.0 --port 8000 &
          for i in {1..60}; do curl -fsS http://127.0.0.1:8000/ || { sleep 2; continue; }; exit 0; done
          echo "API failed to start" && exit 1
      - name: ZAP Baseline
        uses: zaproxy/action-baseline@v0.11.0
        with:
          target: 'http://127.0.0.1:8000'
          rules_file_name: 'dast/.zap/rules.tsv'
          allow_issue_writing: false
          cmd_options: '-a -m 5'
      - name: Upload ZAP report
        uses: actions/upload-artifact@v4
        with:
          name: zap-baseline-report
          path: |
            report_html.html
            owasp_zap_log.txt
```

---

### `.github/workflows/dast-zap-full-api.yml`

```yaml
name: DAST - ZAP Full & API (nightly)
on:
  schedule: [{ cron: '0 2 * * *' }]
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install app
        run: |
          pip install -e .
      - name: Boot API
        run: |
          nohup python -m uvicorn lukhas.adapters.openai.api:get_app --factory --host 0.0.0.0 --port 8000 &
          for i in {1..60}; do curl -fsS http://127.0.0.1:8000/openapi.json && break || sleep 2; done
      - name: ZAP Full Scan (site)
        uses: zaproxy/action-full-scan@v0.8.0
        with:
          target: 'http://127.0.0.1:8000'
          cmd_options: '-m 15'
      - name: ZAP API Scan (OpenAPI)
        uses: zaproxy/action-api-scan@v0.7.0
        with:
          target: 'http://127.0.0.1:8000/openapi.json'
          rules_file_name: 'dast/.zap/rules.tsv'
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: zap-full-api-artifacts
          path: |
            report_html.html
            zap_scan.log
            owasp_zap_log.txt
```

---

### `.github/workflows/dast-schemathesis.yml`

```yaml
name: DAST - Schemathesis
on:
  schedule: [{ cron: '0 3 * * *' }]
  workflow_dispatch:

jobs:
  schemathesis:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install app + schemathesis
        run: |
          pip install -e .
          pip install "schemathesis[all]"
      - name: Boot API
        run: |
          nohup python -m uvicorn lukhas.adapters.openai.api:get_app --factory --host 0.0.0.0 --port 8000 &
          for i in {1..60}; do curl -fsS http://127.0.0.1:8000/openapi.json && break || sleep 2; done
      - name: Run Schemathesis
        run: |
          schemathesis run http://127.0.0.1:8000/openapi.json \
            --checks all --hypothesis-deadline=1000 --workers=4 \
            --target-ascii --generic-charset --stateful=links \
            --junit-xml=schemathesis.junit.xml \
            --report=schemathesis-report.html
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: schemathesis-artifacts
          path: |
            schemathesis.junit.xml
            schemathesis-report.html
```

---

### `dast/.zap/rules.tsv`

```
# Optional ZAP suppressions. Add lines like:
# RULE_ID  ACTION   COMMENT
10054  IGNORE   Ignoring overly broad CSP until ABAS policies ship
```

---

### `docs/nias/NIAS_PLAN.md`

````md
# NIAS (Non-Intrusive Ad System) — Plan

**Purpose:** Deliver ads that respect EU law by default. Personalization is opt-in via TCF v2.2; minors get contextual only.

## Modes
- **Contextual** (default, EU-safe): page/topic/time signals only. No IDs.  
- **Personalized** (guarded): requires TCF v2.2 consent for Purposes **3 & 4** and **P1**; never for minors; never using special categories.

## Architecture
```mermaid
flowchart LR
  Client -->|TC String / Headers| NIAS_MW[NIASPolicyMiddleware]
  NIAS_MW -->|input| OPA[ABAS/OPA]
  OPA -->|allow/deny| NIAS_MW
  NIAS_MW --> App
  App -->|/nias/serve| Selector
  Selector --> ContextualOnly
  App --> Audit[NIAS_AUDIT JSONL]
````

## Legal anchors

* **DSA**: bans targeted ads to minors and use of special categories.
* **ePrivacy**: consent required for storage/access (cookies, fingerprinting).
* **TCF v2.2**: consent mandatory for P3/P4; do not fall back to LI for personalization in EU.

## Data handling

* **No raw PII** in logs.
* **Do not** store TC strings. If needed, store HMAC(salt, tc_string) + TTL.
* **Audit** only aggregated metadata (timestamp, route, mode, region, slot_count).

## MVP metrics

* Policy denials per 1k ad calls
* % traffic contextual vs personalized (EU/ROW)
* DAST regressions = 0 before release

````

---

### `docs/nias/EU_COMPLIANCE.md`
```md
# EU Compliance Notes (non-legal guidance)

- **DSA**: no targeted ads to minors; special categories forbidden for targeting.  
- **GDPR/ePrivacy**: consent needed for tracking; avoid fingerprinting.  
- **TCF v2.2**: consent is mandatory for Purposes 3–6; server-side parsing using `iab-tcf` is recommended.

Implementation notes:
- ABAS Rego denies personalized when P3/P4/P1 missing, or when `is_minor` or `using_sensitive_signals`.
- NIAS defaults to contextual in EU when consent absent or ambiguous.
- Keep a DPIA log if you plan to store pseudonymous user references.
````

---

### `docs/NIAS_PR_CHECKLIST.md`

```md
# NIAS / ABAS / DAST PR Checklist

- [ ] All new code includes tests.
- [ ] `opa test enforcement/abas -v` passes.
- [ ] DAST PR job (ZAP baseline) passes or has approved exceptions.
- [ ] No TC strings, cookies, or raw identifiers are written to logs or audit files.
- [ ] NIAS audited events contain only allowed fields.
- [ ] Env variables listed and set in CI secrets if needed:
  - NIAS_DEFAULT_REGION=EU
  - NIAS_FAILCLOSE_PERSONALIZED=true
  - OPA_URL=http://127.0.0.1:8181/v1/data/abas/ads/allow
  - OPA_REASON_URL=http://127.0.0.1:8181/v1/data/abas/ads/reason
  - NIAS_AUDIT_SALT=rotate-me
```

---

## Wiring snippet — add to your FastAPI factory

Open `lukhas/adapters/openai/api.py` (or wherever `get_app()` is defined) and **add** the following lines in the app factory (order matters: security → ABAS/OPA middleware → NIAS middleware → routers):

```python
# near top of file (imports)
from lukhas.middleware.security_headers import SecurityHeaders
from enforcement.abas.middleware import ABASMiddleware  # if you create ABAS middleware (optional)
from nias.middleware import NIASPolicyMiddleware
from nias.endpoints import router as nias_router

def setup_middlewares(app):
    app.add_middleware(SecurityHeaders)
    # If you implemented ABAS middleware (policy enforcement for non-nias routes), add it here.
    # app.add_middleware(ABASMiddleware)
    app.add_middleware(NIASPolicyMiddleware)
    return app

def get_app():
    app = FastAPI()
    setup_middlewares(app)
    app.include_router(nias_router)
    # ... rest of your existing routers / setup
    return app
```

> If you prefer ABAS to run before NIAS, put ABAS middleware before NIAS.

---

## Quick local run & smoke test

1. Run OPA (optional for integration; required for ABAS positive allow):

```bash
# from repo root
opa run --server -a :8181
# optionally load policy bundle:
# opa run --server -a :8181 enforcement/abas
```

2. Boot the app (adjust path if your factory is different):

```bash
uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000
```

3. Smoke calls:

```bash
# contextual (EU, no consent) => 200
curl -X POST http://127.0.0.1:8000/nias/serve -H 'X-Region: EU' -d '{"page_context":{"topic":"tech"}}' -H "Content-Type: application/json"

# personalized (EU, no consent) => 403/503 (middleware blocks)
curl -X POST http://127.0.0.1:8000/nias/serve -H 'X-Region: EU' -H 'X-Targeting-Mode: personalized'
```

4. Run tests:

```bash
pip install -e .
pip install pytest httpx
pytest -q
```

---

## Final notes & safety guardrails

* **Do not** log TC strings or cookie values. If you need to persist consent proof, store **HMAC(salt, tc_string)** with TTL and rotation.
* NIAS defaults to **contextual** for EU traffic. Personalization always requires explicit P3/P4 and P1. Minors and sensitive signals are always denied.
* Rego tests (`opa test`) must run in CI; we added a GH Action for that.
* If you want, I can also produce a **small ABAS middleware** (Python) to call OPA for the broader app (not just NIAS) so ABAS can enforce other sensitive routes — I left that optional to avoid duplicating logic.

---
