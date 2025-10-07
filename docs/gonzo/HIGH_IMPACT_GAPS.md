---
status: wip
type: documentation
owner: unknown
module: gonzo
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# 🚩 High-impact gaps (with precise fix prompts)

### 1) Memory lifecycle is only partially wired

**Why it matters:** MATRiZ depends on deterministic retention/GDPR & archival to avoid cascade risk and legal exposure.
**Signal:** Lifecycle code exists but archival/expiration paths show placeholders (e.g., empty/unchecked expiry queries) and lack an end-to-end audit in tests.

**Agent Prompt (drop-in):**

```
Goal: Finish memory lifecycle (retention, archival, GDPR delete) to production grade with evidence.

Tasks:
- Implement expiration scan that queries by creation_ts/ttl and moves docs to {S3 or ./archive} gzip with manifest.
- On GDPR delete(lid): write tombstone {lid, deleted_at, reason} and redact in hot/read paths.
- Emit Prom metrics: lukhas_memory_retained_total, ..._archived_total, ..._gdpr_deleted_total; hist ..._lifecycle_seconds.
- Add tests:
  - tests/memory/test_lifecycle.py: create→expire→archive→restore-none; GDPR delete leaves tombstone and removes result from search; artifacts JSON with counts.
  - tests/memory/test_storage_e2e.py: p95 upsert/search <100ms with lifecycle hooks enabled.

Acceptance:
- “promtool test rules” green for lifecycle alerts.
- artifacts/memory_validation_*.json contains counts and p95s.
```

### 2) Lane enums inconsistent with adapters

**Why it matters:** Routing & policy must agree on lane taxonomy to keep MATRiZ isolation airtight.
**Signal:** `guardian_schema.json` enumerates `["candidate","lukhas","MATRIZ","integration","production","canary","experimental"]`, but some backends/clients constrain lanes differently (e.g., storage/orchestrator helpers using older sets like `candidate/integration/production`).

**Agent Prompt (drop-in):**

```
Goal: Unify lane taxonomy everywhere.

Tasks:
- Grep codebase for lane enums and hard-coded strings; replace with a single source: lukhas/governance/schema_registry.py:get_lane_enum().
- Add contract test tests/governance/test_lane_consistency.py that imports {orchestrator, memory backends, identity, guardian clients} and asserts common enum set equals schema registry’s.
- Add import-linter rule: no module defines its own lane constants.

Acceptance:
- test_lane_consistency passes; import-linter lane check green.
```

### 3) OIDC provider: conformance & security posture not proven

**Why it matters:** Identity is the blast radius. MATRiZ must pass OIDC basic profile, PKCE, rotation, clock skew, and leak-proof logging.
**Signal:** Provider/JWT utilities present; conformance/example tests missing; no jwks/rotation burn tests or SSRF/nonce replay checks.

**Agent Prompt (drop-in):**

```
Goal: Achieve OIDC basic profile conformance and T4 security checks.

Tasks:
- Add tests/identity/oidc/test_conformance_basic.py: discovery, jwks, authz code + PKCE, token, userinfo; clock skew ±120s; nonce replay blocked.
- Add tests/identity/oidc/test_rotation_hardening.py: kid rotation, revoked key rejection, JWKS cache TTLs.
- Add tests/identity/oidc/test_abuse.py: alg=none reject, “kid” path traversal, JKU SSRF blocked, audience/issuer exact match.
- Metrics: lukhas_oidc_token_latency_seconds; counters for verification failures.
- Docs: docs/identity/oidc_conformance.md (matrix + how to reproduce with oidc-conformance suite).

Acceptance:
- All tests green; artifacts/oidc_validation_*.json produced with CI95% latency and failure rates.
```

### 4) Observability contracts: end-to-end stitching

**Why it matters:** T4 requires **provable** SLOs. Orchestrator/context/memory/perf metrics must share correlation\_id and lane attributes for joined queries.
**Signal:** Orchestrator/perf tests exist; ensure span attributes (`lane`, `correlation_id`, `provider`, `rule`) and memory metrics share labels; add promtool rule tests for T4 burn-rates.

**Agent Prompt (drop-in):**

```
Goal: Make E2E traces and metrics queryable by correlation_id + lane.

Tasks:
- Ensure OTEL spans set attributes: lane, correlation_id, request_id, provider, rule_name across orchestrator→context→memory.
- Standardize Prom labels: lane, component, operation, provider. Avoid high-cardinality IDs.
- Add promtool test files: alerts/rules_with_tests.yaml; burn rate 2%/1h and 0.1%/6h for routing latency p95>250ms, memory p95>100ms.
- Add tests/observability/test_label_contracts.py to assert metrics carry required labels.

Acceptance:
- promtool tests pass; “metrics label contract” test green.
```

### 5) Security hardening proof for crypto/tokens

**Why it matters:** T4/0.01% peers expect misuse prevention proof.
**Signal:** Token/ΛID present; add bandit/semgrep guards and negative tests (alg=none, timing attacks, padding oracle not applicable but constant-time compare enforced).

**Agent Prompt (drop-in):**

```
Goal: Enforce crypto hygiene & prove it.

Tasks:
- Add semgrep ruleset: crypto-misuse.yaml; CI fails on md5/sha1, random.SystemRandom misuse, jwt.decode(verify=False), etc.
- Unit tests:
  - tests/identity/test_jwt_misuse_blocks.py (alg=none, “none” kid tricks, unicode normalization attacks).
  - tests/identity/test_constant_time_compare.py (side-channel microbench: variance within noise band).
- Ensure secrets never logged; add test that logs scrub tokens.

Acceptance:
- CI security gate blocks intentional misuse; logs contain redacted tokens only.
```

---

# 🧪 Quick win checks to run now (no code changes)

1. **Lane conformance grep**

```
git grep -nE '"(candidate|lukhas|MATRIZ|integration|production|canary|experimental)"' \
  | grep -v guardian_schema.json
```

→ Any mismatches: fix to use schema registry (see #2).

2. **Promtool sanity**

```
promtool check rules alerts/rules_with_tests.yaml
promtool test rules alerts/rules_with_tests.yaml
```

3. **OIDC surface smoke (local)**

```
curl /.well-known/openid-configuration | jq .issuer,.jwks_uri
curl /jwks.json | jq .keys[0].kid
```

→ Ensure stable `issuer`, valid JWKS and kid rotation path.

---

# 🟢 Bottom line

* **MATRiZ readiness:** Nearly there. Orchestrator + cognitive + Guardian schema look solid.
* **Blockers to clear next:** Memory lifecycle E2E, lane enum unification, OIDC conformance/security tests, and observability label/alert contracts.

Knock out the four prompts above and you’re genuinely T4/0.01%-ready to flip MATRiZ on for a canary.
