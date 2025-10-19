# CODEX: Jules Documentation Tasks - Execution Brief

**Created**: 2025-10-19
**Executor**: ChatGPT Codex (with Claude Code semantic review for J-02, J-04)
**Estimated Time**: 3-4 hours (sequential) | 2.5 hours (with parallelization)
**Branch**: `feat/jules-docs-pass`
**Success Metric**: 85%+ docstring coverage, 5 validated OpenAPI specs, CI enforcement

---

## Executive Summary

**Objective**: Complete Phase 4 documentation quality polish for LUKHAS AI platform.

**Codex Role**: Execute J-01, J-03, J-05, J-06 end-to-end + scaffold J-02/J-04
**Claude Code Role**: Semantic review of J-02 (critical script docstrings) and J-04 (OpenAPI examples/errors)

**Why Codex?**
- ✅ Boilerplate generation (module docstrings, OpenAPI scaffolds)
- ✅ CI wiring and lint/validate loops
- ✅ Artifact plumbing and PR automation
- ⚠️ Needs reviewer for semantic depth (Args/Returns/Raises nuances)

---

## Prerequisites (One-Time Setup)

### Python Tools (required)
```bash
pip install pydocstyle interrogate jsonschema pytest
```

### npm Tools (required)
```bash
npm i -g @apidevtools/swagger-cli @stoplight/spectral-cli redoc-cli
```

### Validation
```bash
# Confirm tools installed
pydocstyle --version
interrogate --version
swagger-cli --version
spectral --version
redoc-cli --version

# Confirm CI workflow exists
ls -la .github/workflows/matriz-validate.yml
```

### Repository Assumptions
- ✅ Direct pushes allowed on feature branch `feat/jules-docs-pass`
- ✅ `workflow_dispatch` runs permitted
- ✅ Docstring style = Google (Args/Returns/Raises format)

---

## Task Execution Runbook (Copy-Paste Ready)

### Phase 1: Branch & Seed (J-01)

**Task**: Seed module docstrings for 347 scripts
**Executor**: Codex (100% autonomous)
**Time**: 30 minutes

```bash
# Step 1.1: Create branch
git checkout -b feat/jules-docs-pass

# Step 1.2: Seed module docstrings
python scripts/seed_module_docstrings.py

# Step 1.3: Generate coverage artifacts
interrogate -v --fail-under 85 -o docs/audits/docstring_coverage.json scripts api || true
pydocstyle scripts api | tee docs/audits/docstring_offenders.txt || true

# Step 1.4: Commit
git add -A
git commit -m "docs(seed): add module docstrings for 347 scripts

Problem:
- 347 scripts in scripts/ and api/ lacked module-level docstrings
- No baseline coverage metrics for documentation quality
- CI had no enforcement gates

Solution:
- Generated module docstrings using seed_module_docstrings.py
- Captured interrogate coverage (JSON format)
- Captured pydocstyle offenders (line-numbered errors)

Impact:
- Baseline docstring coverage established
- Foundation for J-02 critical script enhancements
- Audit artifacts ready for CI integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Acceptance Criteria**:
- [ ] `docs/audits/docstring_coverage.json` exists
- [ ] `docs/audits/docstring_offenders.txt` exists
- [ ] Coverage ≥85% (fail-under threshold met)
- [ ] All 347 files have module docstrings

---

### Phase 2: Critical Scripts Deep Docstrings (J-02)

**Task**: Add comprehensive function docstrings to 30 critical scripts
**Executor**: Codex (scaffolding) + Claude Code (semantic review)
**Time**: 2 hours (Codex 90 min + Claude 30 min review)

**Critical Files** (30 scripts):
```
scripts/generate_module_manifests.py
scripts/validate_module_manifests.py
scripts/validate_contract_refs.py
scripts/phase4_build_canary.py
scripts/phase4_run_set.sh
scripts/emit_metrics.py
scripts/gen_coverage_dashboard.py
scripts/add_spdx_headers.py
scripts/validate_docstring_semantics.py
scripts/seed_module_docstrings.py
api/app.py
api/endpoints/identity.py
api/endpoints/consciousness.py
api/endpoints/governance.py
api/endpoints/monitoring.py
api/middleware/auth.py
api/middleware/metrics.py
api/models/requests.py
api/models/responses.py
api/dependencies.py
matriz/core/engine.py
matriz/nodes/base.py
matriz/adapters/registry.py
lukhas/core/coordinator.py
lukhas/consciousness/processor.py
lukhas/governance/guardian.py
lukhas/identity/auth.py
lukhas/api/router.py
tools/dev_server.py
tools/audit_runner.py
```

#### Codex Workflow (90 minutes)

```bash
# For each critical file:
# 1. Expand all public functions with Google-style docstrings:
#    - Summary line (imperative, <80 chars)
#    - Extended description (optional)
#    - Args: (with types and descriptions)
#    - Returns: (with type and description)
#    - Raises: (exception types and conditions)
#    - Example: (usage example for complex functions)

# 2. Template for function docstrings:
"""
Brief description of what this function does.

Extended description if needed, explaining algorithm,
design decisions, or important context.

Args:
    param1 (str): Description of param1.
    param2 (int, optional): Description of param2. Defaults to 0.
    param3 (dict[str, Any]): Description of param3.

Returns:
    bool: True if successful, False otherwise.

Raises:
    ValueError: If param1 is empty or invalid.
    RuntimeError: If external dependency fails.

Example:
    >>> result = my_function("input", param2=42)
    >>> print(result)
    True
"""

# 3. After each batch of 5 files, validate:
pydocstyle scripts api
interrogate -q --fail-under 85 scripts api

# 4. Commit batch:
git add -A
git commit -m "docs(critical): add deep docstrings for batch 1 (5 scripts)"
```

#### Claude Code Review Checklist (30 minutes)

**Spot-check 5 scripts for semantic accuracy**:
1. `scripts/generate_module_manifests.py` - Verify Args/Returns match actual code
2. `api/endpoints/identity.py` - Check Raises matches error handling
3. `matriz/core/engine.py` - Validate Example is executable
4. `lukhas/governance/guardian.py` - Confirm edge cases documented
5. `tools/audit_runner.py` - Ensure async patterns described

**Review Focus**:
- ✅ Args types match function signature (use `rg "def function_name"` to verify)
- ✅ Returns accurately describes all code paths (check for early returns)
- ✅ Raises lists all exceptions (grep for `raise` statements)
- ✅ Examples use realistic inputs (not placeholder "foo", "bar")

**Claude Code Commands**:
```bash
# Quick validation
python -m doctest scripts/generate_module_manifests.py -v
python -m mypy scripts/generate_module_manifests.py --strict

# If issues found, leave inline comment:
# TODO(claude-review): Args missing `preserve_tier` parameter
```

**Acceptance Criteria**:
- [ ] All 30 files have function docstrings (Args/Returns/Raises)
- [ ] Claude Code reviewed 5 scripts (sign-off in commit message)
- [ ] `pydocstyle scripts api` passes (0 errors)
- [ ] `interrogate -q --fail-under 85 scripts api` passes

---

### Phase 3: CI Enforcement (J-03)

**Task**: Add docstring + OpenAPI validation to CI
**Executor**: Codex (100% autonomous)
**Time**: 45 minutes

```bash
# Step 3.1: Add docstring-quality job to .github/workflows/matriz-validate.yml

# Insert after existing jobs:
```

```yaml
  docstring-quality:
    name: Documentation Quality Gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install pydocstyle interrogate

      - name: Run interrogate (docstring coverage)
        run: |
          interrogate -v --fail-under 85 \
            -o docs/audits/docstring_coverage.json \
            scripts api matriz lukhas

      - name: Run pydocstyle (style enforcement)
        run: |
          pydocstyle scripts api matriz lukhas \
            | tee docs/audits/docstring_offenders.txt

      - name: Upload docstring artifacts
        uses: actions/upload-artifact@v4
        with:
          name: docstring-quality-artifacts
          path: |
            docs/audits/docstring_coverage.json
            docs/audits/docstring_offenders.txt
          retention-days: 14

  openapi-validation:
    name: OpenAPI Schema Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install OpenAPI tools
        run: |
          npm i -g @apidevtools/swagger-cli @stoplight/spectral-cli

      - name: Validate OpenAPI specs
        run: |
          for spec in docs/openapi/*.openapi.yaml; do
            echo "Validating $spec..."
            swagger-cli validate "$spec"
            spectral lint "$spec" --format junit \
              --output "docs/audits/$(basename $spec .yaml)_lint.xml"
          done

      - name: Upload OpenAPI artifacts
        uses: actions/upload-artifact@v4
        with:
          name: openapi-validation-artifacts
          path: docs/audits/*_lint.xml
          retention-days: 14
```

```bash
# Step 3.2: Test workflow locally (if act installed)
act -j docstring-quality

# Step 3.3: Commit
git add .github/workflows/matriz-validate.yml
git commit -m "ci(docs): add docstring and OpenAPI validation gates

Problem:
- No CI enforcement for documentation quality standards
- OpenAPI specs could drift from implementation
- No automated artifact retention for audits

Solution:
- Added docstring-quality job (interrogate + pydocstyle)
- Added openapi-validation job (swagger-cli + spectral)
- 14-day artifact retention for audit trails
- Fail-under 85% threshold for docstring coverage

Impact:
- Documentation regressions caught in PR reviews
- OpenAPI specs validated on every push
- Audit artifacts available for quality dashboards
- Foundation for T4+ documentation polish

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Acceptance Criteria**:
- [ ] `.github/workflows/matriz-validate.yml` has 2 new jobs
- [ ] Local test passes (or skipped if `act` unavailable)
- [ ] Workflow uses `python -m pip install --upgrade pip` (per user request)
- [ ] Artifacts uploaded with 14-day retention

---

### Phase 4: OpenAPI Specifications (J-04)

**Task**: Write 5 OpenAPI 3.1 specs for core APIs
**Executor**: Codex (scaffolding) + Claude Code (semantic review)
**Time**: 1.5 hours (Codex 60 min + Claude 30 min review)

#### Codex Workflow (60 minutes)

**Generate 5 specs**:
1. `docs/openapi/identity.openapi.yaml` - Authentication & ΛiD system
2. `docs/openapi/consciousness.openapi.yaml` - MATRIZ cognitive processing
3. `docs/openapi/governance.openapi.yaml` - Guardian & ethics enforcement
4. `docs/openapi/monitoring.openapi.yaml` - Metrics & health endpoints
5. `docs/openapi/lanes.openapi.yaml` - Development/Integration/Production APIs

**Template** (copy for each spec):

```yaml
openapi: 3.1.0
info:
  title: LUKHAS Identity API
  version: 1.0.0
  description: |
    Authentication and ΛiD (Lambda Identity) system for LUKHAS AI platform.

    Provides secure access control, namespace isolation, and credential management.
  contact:
    name: LUKHAS AI Support
    url: https://lukhas.ai/support
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.lukhas.ai/v1
    description: Production server

tags:
  - name: authentication
    description: User authentication and token management
  - name: identity
    description: ΛiD identity operations

paths:
  /auth/login:
    post:
      summary: Authenticate user
      operationId: loginUser
      tags:
        - authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            examples:
              basic:
                summary: Basic password login
                value:
                  username: "user@lukhas.ai"
                  password: "secure_password"
              passkey:
                summary: WebAuthn passkey login
                value:
                  username: "user@lukhas.ai"
                  credential_id: "AQIDBAUGBwgJ..."
      responses:
        '200':
          description: Authentication successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthToken'
              examples:
                success:
                  value:
                    access_token: "eyJhbGciOiJIUzI1NiIs..."
                    token_type: "bearer"
                    expires_in: 3600
        '401':
          description: Authentication failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                invalid_credentials:
                  value:
                    error: "invalid_credentials"
                    message: "Username or password incorrect"

components:
  schemas:
    LoginRequest:
      type: object
      required:
        - username
      properties:
        username:
          type: string
          format: email
          description: User email address
        password:
          type: string
          format: password
          description: User password (required for password auth)
        credential_id:
          type: string
          description: WebAuthn credential ID (required for passkey auth)

    AuthToken:
      type: object
      required:
        - access_token
        - token_type
        - expires_in
      properties:
        access_token:
          type: string
          description: JWT access token
        token_type:
          type: string
          enum: [bearer]
        expires_in:
          type: integer
          description: Token lifetime in seconds

    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          description: Machine-readable error code
        message:
          type: string
          description: Human-readable error message
        details:
          type: object
          additionalProperties: true
          description: Additional error context

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

**Key Points**:
- Mirror Pydantic models from `api/models/requests.py` and `api/models/responses.py`
- Add 1-2 realistic examples per endpoint (not "foo"/"bar")
- Document all error codes from `api/endpoints/*.py` (grep for `HTTPException`)
- Use `components/schemas` for reusable types
- Add security schemes for JWT/API keys

**Validation Loop**:
```bash
# After each spec:
swagger-cli validate docs/openapi/identity.openapi.yaml
spectral lint docs/openapi/identity.openapi.yaml

# Fix errors, iterate to 0 warnings
```

**Commit**:
```bash
git add docs/openapi/
git commit -m "docs(openapi): add 5 validated API specifications

Problem:
- No formal API contracts for identity, consciousness, governance, monitoring, lanes
- Integration partners lacked machine-readable specs
- No automated validation of request/response schemas

Solution:
- Created 5 OpenAPI 3.1 specs mirroring Pydantic models
- Added realistic examples for all endpoints
- Documented error codes and security schemes
- Validated with swagger-cli and spectral (0 errors)

Impact:
- API contracts enforceable in CI
- ReDoc/Swagger UI generation enabled
- Client SDK generation possible
- Foundation for API versioning strategy

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Claude Code Review Checklist (30 minutes)

**Spot-check 3 specs for semantic accuracy**:
1. `identity.openapi.yaml` - Verify error models match actual API responses
2. `consciousness.openapi.yaml` - Check examples use valid MATRIZ inputs
3. `governance.openapi.yaml` - Validate security schemes match implementation

**Review Focus**:
- ✅ Examples use real data types (not placeholders)
- ✅ Error responses match `HTTPException` codes (grep `api/endpoints/`)
- ✅ Schemas reference existing Python types (check `api/models/`)
- ✅ Security schemes match middleware (check `api/middleware/auth.py`)

**Claude Code Commands**:
```bash
# Validate against actual API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@lukhas.ai","password":"test"}' | jq .

# Compare with spec example
yq '.paths["/auth/login"].post.responses["401"].content["application/json"].examples.invalid_credentials.value' docs/openapi/identity.openapi.yaml
```

**Acceptance Criteria**:
- [ ] All 5 specs pass `swagger-cli validate`
- [ ] All 5 specs pass `spectral lint` (0 errors)
- [ ] Claude Code reviewed 3 specs (sign-off in commit)
- [ ] All `components/schemas` reference existing Python types or documented JSON equivalents
- [ ] Examples are realistic (not "foo", "bar", "123")

---

### Phase 5: API Index & Artifacts (J-05)

**Task**: Generate API documentation index and endpoint catalog
**Executor**: Codex (100% autonomous)
**Time**: 30 minutes

```bash
# Step 5.1: Create docs/apis/INDEX.md

cat > docs/apis/INDEX.md <<'EOF'
# LUKHAS API Documentation Index

**Last Updated**: 2025-10-19
**OpenAPI Version**: 3.1.0
**Base URL (dev)**: `http://localhost:8000/api/v1`
**Base URL (prod)**: `https://api.lukhas.ai/v1`

---

## Available APIs

### 1. Identity API
**Specification**: [identity.openapi.yaml](../openapi/identity.openapi.yaml)
**ReDoc Preview**: [identity.html](../openapi/site/identity.html) *(if generated)*

**Endpoints**:
- `POST /auth/login` - Authenticate user
- `POST /auth/logout` - Revoke token
- `GET /auth/me` - Get current user
- `POST /identity/register` - Register new ΛiD
- `GET /identity/{id}` - Get identity details

**Key Features**:
- WebAuthn passkey support
- Namespace isolation
- JWT token management

---

### 2. Consciousness API
**Specification**: [consciousness.openapi.yaml](../openapi/consciousness.openapi.yaml)
**ReDoc Preview**: [consciousness.html](../openapi/site/consciousness.html)

**Endpoints**:
- `POST /consciousness/process` - Submit cognitive task
- `GET /consciousness/status/{task_id}` - Check task status
- `POST /consciousness/matriz/execute` - Execute MATRIZ workflow

**Key Features**:
- MATRIZ cognitive DNA processing
- <250ms p95 latency
- Async task queue

---

### 3. Governance API
**Specification**: [governance.openapi.yaml](../openapi/governance.openapi.yaml)
**ReDoc Preview**: [governance.html](../openapi/site/governance.html)

**Endpoints**:
- `POST /governance/validate` - Validate action against constitutional AI
- `GET /governance/policies` - List active policies
- `POST /governance/drift/report` - Report ethical drift

**Key Features**:
- Guardian constitutional enforcement
- Ethical drift detection
- Policy versioning

---

### 4. Monitoring API
**Specification**: [monitoring.openapi.yaml](../openapi/monitoring.openapi.yaml)
**ReDoc Preview**: [monitoring.html](../openapi/site/monitoring.html)

**Endpoints**:
- `GET /monitoring/health` - System health check
- `GET /monitoring/metrics` - Prometheus metrics
- `GET /monitoring/constellation` - Constellation status

**Key Features**:
- Prometheus integration
- 8-star constellation monitoring
- Performance telemetry

---

### 5. Lanes API
**Specification**: [lanes.openapi.yaml](../openapi/lanes.openapi.yaml)
**ReDoc Preview**: [lanes.html](../openapi/site/lanes.html)

**Endpoints**:
- `GET /lanes/candidate` - List candidate components
- `POST /lanes/promote` - Promote component to integration
- `GET /lanes/production` - List production components

**Key Features**:
- Three-lane architecture (candidate/core/lukhas)
- Import boundary validation
- Promotion workflow

---

## Quick Start

### Authentication
```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@lukhas.ai","password":"secure_password"}'

# Use token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/identity/me
```

### Health Check
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

---

## Tools & Resources

- **Swagger UI**: `http://localhost:8000/docs` (auto-generated)
- **ReDoc**: `http://localhost:8000/redoc` (auto-generated)
- **OpenAPI Specs**: [../openapi/](../openapi/)
- **Endpoint Catalog**: [endpoint_catalog.json](endpoint_catalog.json)

---

## Development

### Validate Specs
```bash
swagger-cli validate docs/openapi/*.openapi.yaml
spectral lint docs/openapi/*.openapi.yaml
```

### Generate ReDoc Previews
```bash
for f in docs/openapi/*.openapi.yaml; do
  base=$(basename "$f" .openapi.yaml)
  redoc-cli build "$f" -o "docs/openapi/site/${base}.html"
done
```

### Update Endpoint Catalog
```bash
python scripts/gen_endpoint_catalog.py \
  --specs docs/openapi/*.openapi.yaml \
  --out docs/apis/endpoint_catalog.json
```

---

## Support

- **Issues**: https://github.com/yourusername/lukhas/issues
- **Discussions**: https://github.com/yourusername/lukhas/discussions
- **Email**: support@lukhas.ai
EOF

# Step 5.2: Create endpoint catalog generator script

cat > scripts/gen_endpoint_catalog.py <<'PYTHON'
#!/usr/bin/env python3
"""
Generate endpoint catalog JSON from OpenAPI specs.

SPDX-License-Identifier: MIT
Author: LUKHAS AI Team
"""

import argparse
import json
from pathlib import Path
import yaml


def extract_endpoints(spec_path: Path) -> list[dict]:
    """Extract endpoints from OpenAPI spec."""
    with spec_path.open() as f:
        spec = yaml.safe_load(f)

    endpoints = []
    base_url = spec.get("servers", [{}])[0].get("url", "")

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                endpoints.append({
                    "api": spec["info"]["title"],
                    "path": path,
                    "method": method.upper(),
                    "operation_id": details.get("operationId", ""),
                    "summary": details.get("summary", ""),
                    "tags": details.get("tags", []),
                    "base_url": base_url,
                })

    return endpoints


def main():
    parser = argparse.ArgumentParser(description="Generate endpoint catalog")
    parser.add_argument("--specs", nargs="+", required=True, help="OpenAPI spec paths")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    all_endpoints = []
    for spec_path in args.specs:
        all_endpoints.extend(extract_endpoints(Path(spec_path)))

    catalog = {
        "total_endpoints": len(all_endpoints),
        "apis": list({e["api"] for e in all_endpoints}),
        "endpoints": all_endpoints,
    }

    Path(args.out).write_text(json.dumps(catalog, indent=2))
    print(f"✅ Generated catalog with {len(all_endpoints)} endpoints → {args.out}")


if __name__ == "__main__":
    main()
PYTHON

chmod +x scripts/gen_endpoint_catalog.py

# Step 5.3: Generate endpoint catalog
python scripts/gen_endpoint_catalog.py \
  --specs docs/openapi/*.openapi.yaml \
  --out docs/apis/endpoint_catalog.json

# Step 5.4: Generate ReDoc previews (if specs exist)
mkdir -p docs/openapi/site
for f in docs/openapi/*.openapi.yaml; do
  base=$(basename "$f" .openapi.yaml)
  redoc-cli build "$f" -o "docs/openapi/site/${base}.html"
done

# Step 5.5: Commit
git add docs/apis/ scripts/gen_endpoint_catalog.py docs/openapi/site/
git commit -m "docs(apis): add API index and endpoint catalog

Problem:
- No centralized index for LUKHAS API documentation
- No machine-readable catalog of all endpoints
- ReDoc previews not generated for offline browsing

Solution:
- Created docs/apis/INDEX.md with all 5 APIs and quick start
- Generated endpoint_catalog.json (machine-readable)
- Built ReDoc static HTML previews for each spec
- Added gen_endpoint_catalog.py helper script

Impact:
- Single entry point for API documentation
- Endpoint catalog enables tooling (SDK gen, testing)
- ReDoc previews work offline and in CI artifacts
- INDEX.md includes links to previews if present (per user request)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Acceptance Criteria**:
- [ ] `docs/apis/INDEX.md` created with all 5 APIs
- [ ] `docs/apis/endpoint_catalog.json` exists
- [ ] ReDoc previews generated: `docs/openapi/site/*.html`
- [ ] INDEX.md includes ReDoc preview links (per user request)
- [ ] `gen_endpoint_catalog.py` script created and executable

---

### Phase 6: Final Validation & PR (J-06)

**Task**: Run smoke tests, validators, create PR
**Executor**: Codex (100% autonomous)
**Time**: 20 minutes

```bash
# Step 6.1: Run smoke tests
pytest -q -m smoke --maxfail=1 --disable-warnings

# Step 6.2: Run MATRIZ smoke tests
pytest -q -m matriz_smoke --maxfail=1

# Step 6.3: Validate manifests (strict mode)
python scripts/validate_module_manifests.py --strict

# Step 6.4: Generate T4+ unified metrics
python scripts/emit_metrics.py \
  --coverage docs/audits/docstring_coverage.json \
  --offenders docs/audits/docstring_offenders.txt \
  --spectral-junit docs/audits/openapi_lint_junit.xml \
  --out docs/audits/metrics.json

# Step 6.5: Generate coverage dashboard
python scripts/gen_coverage_dashboard.py \
  --metrics docs/audits/metrics.json \
  --out docs/audits/coverage_dashboard.md

# Step 6.6: Push branch
git push -u origin feat/jules-docs-pass

# Step 6.7: Create PR with template
gh pr create --title "Jules documentation completion (v2)" --body "$(cat <<'EOF'
## Summary
Complete Phase 4 documentation quality polish for LUKHAS AI platform.

**Tasks Completed**:
- ✅ J-01: Seeded module docstrings (347 scripts)
- ✅ J-02: Deep docstrings for 30 critical scripts
- ✅ J-03: CI enforcement (docstring + OpenAPI validation)
- ✅ J-04: 5 validated OpenAPI 3.1 specifications
- ✅ J-05: API index and endpoint catalog
- ✅ J-06: Final validation and PR creation

**Metrics**:
- Docstring coverage: **85%+** (interrogate)
- pydocstyle errors: **0** (scripts, api, matriz, lukhas)
- OpenAPI specs: **5** (all validated)
- Endpoints documented: **XX** (see endpoint_catalog.json)

**Artifacts**:
- 📊 [Coverage Dashboard](docs/audits/coverage_dashboard.md)
- 📄 [API Index](docs/apis/INDEX.md)
- 📋 [Endpoint Catalog](docs/apis/endpoint_catalog.json)
- 🔍 [Metrics JSON](docs/audits/metrics.json)

---

## Checklist

### J-01: Module Docstrings
- [ ] 347 scripts have module docstrings
- [ ] `docs/audits/docstring_coverage.json` exists
- [ ] Coverage ≥85%

### J-02: Critical Scripts
- [ ] 30 critical scripts have function docstrings
- [ ] Args/Returns/Raises documented
- [ ] Claude Code reviewed 5 scripts (semantic sign-off)

### J-03: CI Enforcement
- [ ] `docstring-quality` job added to CI
- [ ] `openapi-validation` job added to CI
- [ ] Artifacts uploaded with 14-day retention

### J-04: OpenAPI Specs
- [ ] 5 specs created and validated
- [ ] All specs pass `swagger-cli validate`
- [ ] All specs pass `spectral lint` (0 errors)
- [ ] Schemas reference existing Python types

### J-05: API Index
- [ ] `docs/apis/INDEX.md` created
- [ ] `endpoint_catalog.json` generated
- [ ] ReDoc previews built

### J-06: Final Validation
- [ ] Smoke tests pass
- [ ] MATRIZ smoke tests pass
- [ ] Manifest validation passes (strict mode)
- [ ] T4+ metrics generated
- [ ] Coverage dashboard created

---

## Testing

### Smoke Tests
\`\`\`bash
pytest -q -m smoke
pytest -q -m matriz_smoke
\`\`\`

### Docstring Validation
\`\`\`bash
interrogate -v --fail-under 85 scripts api matriz lukhas
pydocstyle scripts api matriz lukhas
\`\`\`

### OpenAPI Validation
\`\`\`bash
swagger-cli validate docs/openapi/*.openapi.yaml
spectral lint docs/openapi/*.openapi.yaml
\`\`\`

---

## Next Steps

After merge:
1. Update live API documentation site
2. Generate client SDKs from OpenAPI specs
3. Schedule Phase 5 (remaining 1,253 scripts)
4. Monitor CI for docstring regressions

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" --assignee @me

# Step 6.8: Output PR URL
echo "✅ PR created! Review checklist and merge when ready."
```

**Acceptance Criteria**:
- [ ] All smoke tests pass
- [ ] All validators pass (strict mode)
- [ ] T4+ metrics generated
- [ ] Coverage dashboard exists
- [ ] PR created with full checklist
- [ ] Artifacts attached to PR (via CI upload)

---

## Codex-Specific Enhancements (from User Feedback)

### 1. J-03 Commands Enhancement
Add pip upgrade step:
```bash
python -m pip install --upgrade pip
```
*(Already included in CI job above)*

### 2. J-04 Acceptance Criteria Enhancement
```markdown
- [ ] All components/schemas reference existing Python types or documented JSON Schema equivalents
```
*(Already included in Phase 4 acceptance criteria)*

### 3. J-05 Acceptance Criteria Enhancement
```markdown
- [ ] INDEX.md includes ReDoc preview links if present
```
*(Already included in INDEX.md template)*

---

## Risk Mitigation

### npm Tool Availability
**Risk**: npm tools not installed in CI or local env
**Mitigation**: Added install step in CI + prerequisites section

### OpenAPI Schema/Type Drift
**Risk**: Specs diverge from actual Pydantic models
**Mitigation**: Generate schemas from Python models, not manual typing

### Docstring False Positives
**Risk**: pydocstyle flags non-critical issues
**Mitigation**: Set ignores for D104, D203 in `.pydocstyle` config:
```ini
[pydocstyle]
ignore = D104,D203
match = .*\.py
```

### Long Edit Sessions
**Risk**: Large PRs hard to review
**Mitigation**: Split into 3 PRs if needed:
1. Seeding + CI (J-01, J-03)
2. Critical 30 scripts (J-02)
3. OpenAPI + index (J-04, J-05, J-06)

---

## Claude Code Collaboration Points

### When to Tag Claude Code
1. **J-02 Semantic Review** (after Codex scaffolds 30 scripts)
   - Review 5 scripts for Args/Returns/Raises accuracy
   - Check Examples are executable
   - Sign off in commit message

2. **J-04 Semantic Review** (after Codex generates 5 specs)
   - Verify error models match API responses
   - Check examples use realistic data
   - Validate security schemes match middleware

### How to Handoff
```bash
# Codex commits scaffolded work
git push origin feat/jules-docs-pass

# Notify Claude Code
# @claude-code Please review J-02 critical scripts (5 spot-checks):
# - scripts/generate_module_manifests.py
# - api/endpoints/identity.py
# - matriz/core/engine.py
# - lukhas/governance/guardian.py
# - tools/audit_runner.py
#
# Check: Args match signatures, Returns cover all paths, Raises match code
```

---

## Success Metrics

### Documentation Quality
- ✅ 85%+ docstring coverage (interrogate)
- ✅ 0 pydocstyle errors (scripts, api, matriz, lukhas)
- ✅ 5 validated OpenAPI specs
- ✅ XX total endpoints documented

### CI Integration
- ✅ 2 new CI jobs (docstring-quality, openapi-validation)
- ✅ 14-day artifact retention
- ✅ Fail-under 85% threshold enforced

### Developer Experience
- ✅ Single API index entry point
- ✅ ReDoc previews for offline browsing
- ✅ Machine-readable endpoint catalog
- ✅ T4+ quality dashboard

---

## Timeline Estimate

**Sequential Execution** (single agent):
- J-01: 30 min
- J-02: 2 hours (90 min Codex + 30 min Claude)
- J-03: 45 min
- J-04: 1.5 hours (60 min Codex + 30 min Claude)
- J-05: 30 min
- J-06: 20 min
- **Total**: ~5 hours

**Parallel Execution** (Codex + Claude):
- Phase 1: J-01 (30 min)
- Phase 2: J-02 Codex scaffold (90 min) → Claude review (30 min concurrent with J-03)
- Phase 3: J-03 (45 min) || Claude review (30 min)
- Phase 4: J-04 Codex scaffold (60 min) → Claude review (30 min concurrent with J-05)
- Phase 5: J-05 (30 min) || Claude review (30 min)
- Phase 6: J-06 (20 min)
- **Total**: ~3 hours

---

## References

- **Original Task Brief**: [JULES_COMPLETE_TASK_BRIEF_2025-10-19.md](JULES_COMPLETE_TASK_BRIEF_2025-10-19.md)
- **Task JSON v2**: [JULES_TASKS_v2.json](JULES_TASKS_v2.json)
- **Execution Strategy**: [JULES_EXECUTION_STRATEGY.md](JULES_EXECUTION_STRATEGY.md)
- **T4+ Polish Scripts**:
  - [scripts/emit_metrics.py](../../scripts/emit_metrics.py)
  - [scripts/gen_coverage_dashboard.py](../../scripts/gen_coverage_dashboard.py)
  - [scripts/add_spdx_headers.py](../../scripts/add_spdx_headers.py)
  - [scripts/validate_docstring_semantics.py](../../scripts/validate_docstring_semantics.py)

---

**Last Updated**: 2025-10-19
**Status**: Ready for Codex execution
**Contact**: LUKHAS AI Team
