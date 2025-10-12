# GitHub Copilot Task Briefs - Phase 2 OpenAI Alignment

**For**: GitHub Copilot Agent (Mechanical & Docs)
**Focus**: Scripts, documentation, configuration, CI workflows
**Total Tasks**: 15 (B6-B12, C13-C15, E19-E20, G23-G24, H26)

---

## Quick Start

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create your branch
git checkout -b chore/task-name  # or docs/task-name or security/task-name

# Verify changes
make lint
git status
```

---

## B6. Fix Manifest Stats Reporter Crash & Add Totals

**Branch**: `fix/manifest-stats-reporter`
**Priority**: HIGH (Quick win)
**Time**: 1 hour

### Problem

`scripts/report_manifest_stats.py` crashes on dict/str shape inconsistencies when processing manifests.

### What to Fix

1. Add defensive checks for missing fields
2. Handle both list and single manifest inputs
3. Add error handling for malformed JSON
4. Generate both JSON and Markdown outputs

### File to Update

- `scripts/report_manifest_stats.py`

### Fix Template

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path
from typing import Any, Dict, List

def load_manifest(path: Path) -> Dict[str, Any]:
    """Load manifest with error handling."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: Failed to load {path}: {e}", file=sys.stderr)
        return {}

def extract_stats(manifest: Dict[str, Any]) -> Dict[str, int]:
    """Extract stats with defensive checks."""
    return {
        "capabilities": len(manifest.get("capabilities", [])),
        "dependencies": len(manifest.get("dependencies", [])),
        "tests": len(manifest.get("tests", [])),
        "has_schema": "schema" in manifest,
    }

def main():
    # ... existing arg parsing ...

    manifests = list(Path("manifests").rglob("module.manifest.json"))
    all_stats = []

    for mf in manifests:
        data = load_manifest(mf)
        if not data:
            continue
        stats = extract_stats(data)
        stats["path"] = str(mf.relative_to(Path.cwd()))
        all_stats.append(stats)

    # Write JSON
    out_json = Path(args.out) / "manifest_stats.json"
    out_json.write_text(json.dumps(all_stats, indent=2), encoding="utf-8")

    # Write Markdown
    out_md = Path(args.out) / "manifest_stats.md"
    # ... generate table ...

    print(f"[stats] Processed {len(all_stats)} manifests")
```

### Acceptance Criteria

- [ ] `python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits` succeeds
- [ ] Writes both `manifest_stats.json` and `manifest_stats.md`
- [ ] No crashes on edge cases (empty, missing fields)
- [ ] Workflow step passes

### Verification

```bash
python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits
cat docs/audits/manifest_stats.md
```

---

## B7. Docs: OpenAI Dev Quickstart

**Branch**: `docs/openai-quickstart`
**Priority**: HIGH
**Time**: 2 hours

### What to Write

Comprehensive quickstart guide for developers coming from OpenAI SDK.

### File Already Created

- `docs/openai/QUICKSTART.md` ✅ (created, review and enhance)

### Enhancements Needed

1. Add JavaScript/TypeScript examples
2. Add curl examples for all endpoints
3. Add troubleshooting section
4. Add migration guide from OpenAI to Lukhas
5. Test all examples locally

### Additional Examples to Add

**JavaScript/Node.js**:
```javascript
// Using fetch
const response = await fetch('http://localhost:8000/v1/responses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer dummy'
  },
  body: JSON.stringify({
    input: 'hello lukhas',
    tools: []
  })
});

const data = await response.json();
console.log(data.output.text);

// Using OpenAI SDK
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'dummy'
});

const response = await client.chat.completions.create({
  model: 'lukhas-matriz',
  messages: [{ role: 'user', content: 'hello lukhas' }]
});
```

**curl**:
```bash
# Responses
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"input":"hello lukhas","tools":[]}'

# Models
curl http://localhost:8000/v1/models

# Embeddings
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"embed this text"}'

# Dreams (Lukhas-specific)
curl -X POST http://localhost:8000/v1/dreams \
  -H "Content-Type: application/json" \
  -d '{"seed":"quantum garden","constraints":{"length":"short"}}'
```

### Acceptance Criteria

- [ ] All examples tested and working
- [ ] Linked from main README and Phase 2 docs
- [ ] Covers Python, JavaScript, curl
- [ ] Includes troubleshooting tips
- [ ] Migration guide from OpenAI included

### Verification

```bash
# Start façade
uvicorn lukhas.adapters.openai.api:get_app --reload

# Test examples
python3 -c "from openai import OpenAI; client = OpenAI(base_url='http://localhost:8000/v1', api_key='dummy'); print(client.models.list())"
```

---

## B8. Update Star Canon Everywhere (Ambiguous → Oracle)

**Branch**: `chore/star-canon-oracle`
**Priority**: MEDIUM
**Time**: 1 hour

### What to Update

Replace all mentions of "Ambiguity (Quantum)" with "Oracle (Quantum)" except in backward-compat aliases.

### Search and Replace Strategy

```bash
# Find all mentions
rg 'Ambiguity.*Quantum' -n

# Expected changes:
# - README files
# - Documentation
# - Constellation diagrams
# - Star rules configs

# Keep as alias only in:
# - configs/star_rules.json (alias field)
# - Migration guides
```

### Files to Update

Run the search command above and update each file. Key areas:
- `README.md`
- `docs/architecture/**`
- `docs/matriz/**`
- `branding/**`
- `*.md` files referring to the 8-star system

### Acceptance Criteria

- [ ] `rg 'Ambiguity \(Quantum\)' -n` returns 0 hits outside aliases
- [ ] `configs/star_rules.json` maintains canonical Oracle name
- [ ] Backward-compat alias documented
- [ ] All constellation diagrams updated

### Verification

```bash
rg 'Ambiguity' -n | grep -v alias | grep -v migration
# Should return minimal results (only in historical docs)
```

---

## B9. PR Template Nudge for "Matriz Readiness"

**Branch**: `chore/pr-template-matriz`
**Priority**: LOW
**Time**: 30 minutes

### What to Add

Update PR template to include MATRIZ discipline pack checklist.

### File to Update

- `.github/PULL_REQUEST_TEMPLATE.md` (or `PULL_REQUEST_TEMPLATE.md` at root)

### Template Addition

```markdown
## 🎯 MATRIZ Readiness

**Required for all PRs touching `lukhas/`, `matriz/`, or `core/`**:

- [ ] Smoke tests passing locally (`make smoke`)
- [ ] Lane boundaries respected (`make lane-guard`)
- [ ] No hardcoded secrets (`make security-scan`)
- [ ] Evals accuracy ≥ 0.70 (if applicable)
- [ ] Documentation updated for new features
- [ ] Tests added for new functionality

**CI Artifacts** (automatically uploaded):
- [ ] `evals_report.md` - Eval results
- [ ] `manifest_stats.md` - Manifest health
- [ ] `star_rules_coverage.md` - Star rule coverage
- [ ] `linkcheck.txt` - Documentation links
- [ ] `sbom.cyclonedx.json` - Supply chain bill of materials

## 🧊 FREEZE Checklist (for RC/release PRs only)

- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Version bumped in `pyproject.toml` and `lukhas/__init__.py`
- [ ] SBOM generated and attached
- [ ] All CI checks passing
- [ ] No breaking changes without migration guide
```

### Acceptance Criteria

- [ ] Template renders checklist in new PRs
- [ ] Links to relevant docs (MATRIZ_GUIDE.md, etc.)
- [ ] FREEZE section clearly marked as optional
- [ ] All checklist items testable

### Verification

- Create test PR and verify template renders
- Check that checklist items match actual CI jobs

---

## B10. Nightly Star-Rules Coverage Trend

**Branch**: `ci/nightly-coverage`
**Priority**: LOW
**Time**: 1 hour

### What to Build

Duplicate `matriz-validate.yml` → `matriz-nightly.yml` with:
1. Schedule trigger (nightly at 5am UTC)
2. Re-use existing star rules scripts
3. Push coverage report to `docs/audits/star_rules_coverage.md`

### File to Create

- `.github/workflows/matriz-nightly.yml`

### Template

```yaml
name: MATRIZ Nightly Coverage

on:
  schedule:
    - cron: '0 5 * * *'  # 5am UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  star-rules-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run star rules lint
        run: python3 scripts/lint_star_rules.py

      - name: Generate coverage report
        run: python3 scripts/gen_rules_coverage.py --out docs/audits

      - name: Commit coverage report
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/audits/star_rules_coverage.md
          git diff --staged --quiet || git commit -m "chore(audit): nightly star rules coverage update"
          git push

      - name: Upload coverage artifact
        uses: actions/upload-artifact@v4
        with:
          name: star-rules-coverage
          path: docs/audits/star_rules_coverage.md
```

### Acceptance Criteria

- [ ] Workflow runs nightly at 5am UTC
- [ ] Coverage report committed to repo
- [ ] Artifact uploaded for download
- [ ] Can be triggered manually via workflow_dispatch

### Verification

```bash
# Trigger manually
gh workflow run matriz-nightly.yml

# Check run status
gh run list --workflow=matriz-nightly.yml
```

---

## B11. Lane Rename Doc Link Fixer

**Branch**: `chore/lane-rename-links`
**Priority**: MEDIUM (do AFTER Batch 3)
**Time**: 2 hours

### What to Build

Script that:
1. Updates links in `docs/**` and `*.md` from `candidate/` → `labs/`
2. Runs link checker locally
3. Generates `docs/audits/linkcheck.txt`

### File to Create

- `scripts/fix_lane_rename_links.py`

### Script Template

```python
#!/usr/bin/env python3
import re
from pathlib import Path

def fix_link(text: str, old: str, new: str) -> str:
    """Replace old lane path with new in markdown links."""
    # Match [text](path) and ![alt](path) patterns
    pattern = rf'\[([^\]]+)\]\(({old}[^\)]*)\)'
    repl = rf'[\1]({new}\2)'
    return re.sub(pattern, repl, text)

def main():
    old_lane = "candidate"
    new_lane = "labs"

    docs = list(Path(".").rglob("*.md"))
    fixed_count = 0

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        new_text = fix_link(text, old_lane, new_lane)

        if text != new_text:
            doc.write_text(new_text, encoding="utf-8")
            fixed_count += 1
            print(f"Fixed: {doc}")

    print(f"\n[link-fixer] Updated {fixed_count} files")

if __name__ == "__main__":
    main()
```

### Link Checker

Create or update `docs/check_links.py`:
```python
#!/usr/bin/env python3
import re, sys
from pathlib import Path

def check_links(root: Path):
    broken = []
    for doc in root.rglob("*.md"):
        text = doc.read_text(encoding="utf-8")
        # Find relative links: [text](path)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        for _, link in links:
            if link.startswith("http"):
                continue  # Skip external
            target = (doc.parent / link).resolve()
            if not target.exists():
                broken.append(f"{doc}:{link}")

    if broken:
        print(f"\n❌ {len(broken)} broken links:")
        for b in broken:
            print(f"  {b}")
        return 1
    print("✅ All links valid")
    return 0

if __name__ == "__main__":
    sys.exit(check_links(Path(".")))
```

### Acceptance Criteria

- [ ] `python3 scripts/fix_lane_rename_links.py` updates all docs
- [ ] `python3 docs/check_links.py --root .` returns 0
- [ ] `docs/audits/linkcheck.txt` shows clean
- [ ] External links validated (or noted as skip)

### Verification

```bash
python3 scripts/fix_lane_rename_links.py
python3 docs/check_links.py --root . > docs/audits/linkcheck.txt
cat docs/audits/linkcheck.txt
```

---

## B12. Security: Add Gitleaks as Second Line

**Branch**: `security/gitleaks`
**Priority**: LOW
**Time**: 30 minutes

### What to Add

Add gitleaks CI step alongside detect-secrets for belt-and-braces secret detection.

### File to Update

- `.github/workflows/matriz-validate.yml`

### Step to Add

```yaml
- name: Gitleaks (warn-only)
  uses: zricethezav/gitleaks-action@v2
  with:
    args: "--no-git -v --source=."
  continue-on-error: true

- name: Upload gitleaks report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: gitleaks-report
    path: gitleaks-report.sarif
    if-no-files-found: ignore
```

### Acceptance Criteria

- [ ] Step runs in CI on every PR
- [ ] Warn-only mode (doesn't block PRs initially)
- [ ] Uploads `gitleaks-report.sarif` artifact
- [ ] Placed near other security steps

### Verification

- Push branch and check workflow run
- Download gitleaks-report artifact
- Verify it's SARIF format and valid

---

## C13. SBOM + Provenance

**Branch**: `security/sbom`
**Priority**: MEDIUM
**Time**: 2 hours

### What to Build

1. SBOM generation script using CycloneDX
2. CI step to upload SBOM artifact
3. GitHub provenance on release tags

### File Already Created

- `scripts/sbom.py` ✅ (created, test it)

### Test SBOM Script

```bash
python3 scripts/sbom.py
ls -la build/sbom.cyclonedx.json
# Validate against CycloneDX schema
```

### CI Step to Add

In `.github/workflows/matriz-validate.yml`:
```yaml
- name: Generate SBOM
  run: python3 scripts/sbom.py

- name: Upload SBOM artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: build/sbom.cyclonedx.json
```

### GitHub Provenance

In release workflow (or create new `.github/workflows/release.yml`):
```yaml
- name: Attest SBOM
  uses: actions/attest-build-provenance@v1
  with:
    subject-path: build/sbom.cyclonedx.json
```

### Acceptance Criteria

- [ ] Script generates valid SBOM
- [ ] CI uploads SBOM artifact
- [ ] Provenance attestation on release tags
- [ ] SBOM validates against CycloneDX schema

### Verification

```bash
python3 scripts/sbom.py
python3 -m pip install cyclonedx-bom-validator
cyclonedx-py validate --input-file build/sbom.cyclonedx.json
```

---

## C14. Dependency Vulns & Static Analysis

**Branch**: `security/dependency-scanning`
**Priority**: MEDIUM
**Time**: 1.5 hours

### What to Add

Two CI steps:
1. `pip-audit` for CVE scanning
2. `bandit` for Python static analysis

### CI Steps to Add

In `.github/workflows/matriz-validate.yml`:
```yaml
- name: Pip Audit (warn-only)
  run: |
    pip install pip-audit
    pip-audit -f json -o docs/audits/pip_audit.json || true
  continue-on-error: true

- name: Bandit Security Scan (warn-only)
  run: |
    pip install bandit
    bandit -r lukhas matriz core -f sarif -o docs/audits/bandit.sarif || true
  continue-on-error: true

- name: Upload security scan artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: security-scans
    path: |
      docs/audits/pip_audit.json
      docs/audits/bandit.sarif
    if-no-files-found: ignore
```

### Local Testing

```bash
pip install pip-audit bandit

pip-audit -f json -o docs/audits/pip_audit.json
bandit -r lukhas matriz core -f sarif -o docs/audits/bandit.sarif

# Review results
cat docs/audits/pip_audit.json | jq '.vulnerabilities | length'
cat docs/audits/bandit.sarif | jq '.runs[0].results | length'
```

### Acceptance Criteria

- [ ] Both tools run in CI
- [ ] Warn-only mode initially
- [ ] Artifacts uploaded on every run
- [ ] Documentation on fixing common issues

### Documentation

Create `docs/security/FIXING_VULNERABILITIES.md`:
```markdown
# Fixing Security Vulnerabilities

## Pip Audit Findings

Check `docs/audits/pip_audit.json` for CVEs in dependencies.

**Common fixes**:
- Update vulnerable package: `pip install --upgrade <package>`
- Check for patch: `pip show <package>`
- If no fix available: Document in `.pip-audit-ignore.json`

## Bandit Findings

Check `docs/audits/bandit.sarif` for Python security issues.

**Common issues**:
- B101: assert used - Use proper exceptions in production
- B301: pickle - Use JSON instead
- B603: subprocess without shell=False - Always set shell=False
```

---

## C15. License Hygiene & Headers

**Branch**: `chore/license-headers`
**Priority**: LOW
**Time**: 2 hours

### What to Build

1. License report using `pip-licenses`
2. Header check pre-commit hook
3. Generate `docs/audits/licenses.md`

### License Report Script

Create `scripts/check_licenses.py`:
```python
#!/usr/bin/env python3
import subprocess, json
from pathlib import Path

def main():
    # Run pip-licenses
    result = subprocess.run(
        ["pip-licenses", "--format=json"],
        capture_output=True,
        text=True
    )

    licenses = json.loads(result.stdout)

    # Approved licenses (adjust as needed)
    approved = {"MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC"}

    violations = [
        pkg for pkg in licenses
        if pkg["License"] not in approved
    ]

    # Write report
    out = Path("docs/audits/licenses.md")
    with open(out, "w") as f:
        f.write("# License Report\n\n")
        f.write(f"**Total Packages**: {len(licenses)}\n")
        f.write(f"**Violations**: {len(violations)}\n\n")

        if violations:
            f.write("## ⚠️ Unapproved Licenses\n\n")
            for v in violations:
                f.write(f"- {v['Name']} {v['Version']}: {v['License']}\n")

    print(f"[licenses] Report written to {out}")
    return 1 if violations else 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Pre-Commit Header Check

Create `.pre-commit-config.yaml` entry:
```yaml
- repo: local
  hooks:
    - id: check-license-headers
      name: Check license headers
      entry: python3 scripts/check_headers.py
      language: system
      types: [python]
```

### Header Check Script

Create `scripts/check_headers.py`:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

REQUIRED_HEADER = """
# Copyright (c) 2025 LUKHAS AI
# SPDX-License-Identifier: Apache-2.0
""".strip()

def check_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return REQUIRED_HEADER in text

def main():
    files = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    missing = [f for f in files if not check_file(f)]

    if missing:
        print("❌ Missing license headers:")
        for f in missing:
            print(f"  {f}")
        return 1

    print("✅ All files have license headers")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Acceptance Criteria

- [ ] License report generated: `docs/audits/licenses.md`
- [ ] Pre-commit hook blocks files without headers
- [ ] All Python files in `lukhas/` have SPDX headers
- [ ] CI checks license compliance

### Verification

```bash
python3 scripts/check_licenses.py
python3 scripts/check_headers.py lukhas/**/*.py
```

---

## E19. Quick k6/Locust Scenario for /v1/responses

**Branch**: `test/load-scenarios`
**Priority**: MEDIUM
**Time**: 2 hours

### File Already Created

- `load/resp_scenario.js` ✅ (created, test it)

### What to Add

1. Test the k6 script
2. Add Makefile target
3. Optional: Add locust alternative

### Test k6 Script

```bash
# Install k6
brew install k6  # macOS
# or: https://k6.io/docs/getting-started/installation/

# Start façade
uvicorn lukhas.adapters.openai.api:get_app --reload &

# Run load test
k6 run load/resp_scenario.js

# Should output p95, p99, error rate
```

### Makefile Target

```makefile
load-smoke: ## Quick load test (50 VUs, 2min)
\tk6 run load/resp_scenario.js || echo "k6 not installed"

load-extended: ## Extended load test (100 VUs, 10min)
\tk6 run --vus 100 --duration 10m load/resp_scenario.js
```

### Optional: Locust Alternative

Create `load/locustfile.py`:
```python
from locust import HttpUser, task, between

class LukhasFacadeUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def responses(self):
        self.client.post("/v1/responses", json={
            "input": "ping",
            "tools": []
        })
```

Run with: `locust -f load/locustfile.py --host http://localhost:8000`

### Acceptance Criteria

- [ ] k6 script runs successfully
- [ ] Reports p95, p99, error rate
- [ ] Makefile target works
- [ ] Nightly job runs (warn-only)

### CI Integration

In `.github/workflows/matriz-nightly.yml`:
```yaml
- name: Load test (warn-only)
  run: |
    uvicorn lukhas.adapters.openai.api:get_app &
    sleep 5
    make load-smoke || true
  continue-on-error: true
```

---

## E20. Timeouts/Backoff Knobs

**Branch**: `config/reliability-knobs`
**Priority**: LOW
**Time**: 1.5 hours

### File Already Created

- `configs/runtime/reliability.yaml` ✅ (created, document it)

### What to Add

1. Documentation on each config parameter
2. Tests validating config is loaded
3. README explaining how to tune

### Enhanced Config (with comments)

```yaml
# LUKHAS Reliability Configuration
# Tune these values based on your deployment environment

timeouts:
  # Connection timeout in milliseconds
  # Default: 1000ms (1 second)
  # Production: Consider 3000-5000ms for distributed systems
  connect_ms: 1000

  # Read timeout in milliseconds
  # Default: 10000ms (10 seconds)
  # Production: Adjust based on expected response times
  read_ms: 10000

backoff:
  # Base delay for exponential backoff in seconds
  # Default: 0.1s (100ms)
  base_s: 0.1

  # Exponential factor (delay = base * factor^attempt)
  # Default: 2.0 (doubles each retry)
  factor: 2.0

  # Jitter as fraction of window (0.1 = ±10%)
  # Prevents thundering herd
  jitter: 0.1

rate_limits:
  # Requests per second for /v1/responses
  # Default: 20 rps
  # Adjust based on backend capacity
  responses_rps: 20

  # Requests per second for /v1/embeddings
  # Default: 50 rps (embeddings are lighter)
  embeddings_rps: 50

  # Requests per second for /v1/dreams
  # Default: 5 rps (dreams are compute-intensive)
  dreams_rps: 5
```

### Documentation

Create `docs/ops/RELIABILITY_TUNING.md`:
```markdown
# Reliability Configuration Tuning

## Timeouts

**connect_ms**: How long to wait for initial connection
- Too low: Spurious failures on slow networks
- Too high: Slow failure detection
- Recommended: 1-3 seconds

**read_ms**: How long to wait for response
- Too low: Timeout before LLM finishes
- Too high: Stuck requests tie up resources
- Recommended: 10-30 seconds (depends on model)

## Backoff

Use jittered exponential backoff to avoid thundering herd.

**Example**:
- Attempt 1: 100ms * 2^0 ± 10ms = 90-110ms
- Attempt 2: 100ms * 2^1 ± 20ms = 180-220ms
- Attempt 3: 100ms * 2^2 ± 40ms = 360-440ms

## Rate Limits

Set based on backend capacity and SLO targets.

**Calculating limits**:
1. Measure backend capacity (requests/sec)
2. Multiply by target utilization (e.g., 0.7 for 70%)
3. Set limit to result
4. Monitor 429 rate and adjust

**Example**:
- Backend can handle 100 rps
- Target 70% utilization
- Set limit to 70 rps
```

### Test Config Loading

Create `tests/config/test_reliability_config.py`:
```python
import yaml
from pathlib import Path

def test_reliability_config_loads():
    config = yaml.safe_load(
        Path("configs/runtime/reliability.yaml").read_text()
    )
    assert "timeouts" in config
    assert "backoff" in config
    assert "rate_limits" in config

def test_reliability_values_reasonable():
    config = yaml.safe_load(
        Path("configs/runtime/reliability.yaml").read_text()
    )
    # Timeouts should be positive
    assert config["timeouts"]["connect_ms"] > 0
    assert config["timeouts"]["read_ms"] > 0

    # Backoff factor should be > 1
    assert config["backoff"]["factor"] >= 1.0

    # Rate limits should be positive
    for key, val in config["rate_limits"].items():
        assert val > 0, f"{key} must be positive"
```

### Acceptance Criteria

- [ ] Config loads successfully
- [ ] Tests validate config structure
- [ ] Documentation explains each parameter
- [ ] Tuning guide provided

---

## G23. Postman Collection + Examples

**Branch**: `docs/postman-collection`
**Priority**: MEDIUM
**Time**: 2 hours

### What to Create

1. Convert OpenAPI spec → Postman collection
2. Add example requests for all endpoints
3. Test import into Postman

### Tools

```bash
# Install openapi-to-postman
npm install -g openapi-to-postmanv2

# Convert
openapi2postmanv2 -s docs/openapi/lukhas-openai.yaml \
  -o docs/openapi/Postman_collection.json \
  -p
```

### Manual Enhancements

After conversion, add:
1. Environment variables (`{{base_url}}`, `{{api_key}}`)
2. Pre-request scripts (auth headers)
3. Test scripts (assertions)
4. Example responses

### Example Environment

Create `docs/openapi/Postman_environment.json`:
```json
{
  "name": "Lukhas Local",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "api_key",
      "value": "dummy",
      "enabled": true
    }
  ]
}
```

### Acceptance Criteria

- [ ] Collection imports cleanly into Postman
- [ ] All endpoints present
- [ ] Example requests work
- [ ] Environment variables configured

### Verification

1. Import `docs/openapi/Postman_collection.json` into Postman
2. Import environment
3. Run all requests
4. Verify responses

---

## G24. "Why Matriz" One-Pager

**Branch**: `docs/why-matriz`
**Priority**: LOW
**Time**: 3 hours

### File Already Created

- `docs/matriz/WHY_MATRIZ.md` ✅ (created, review and enhance)

### Enhancements Needed

1. Add diagrams (architecture, data flow)
2. Add concrete use case examples
3. Add competitive comparison table
4. Add FAQ section

### Diagrams to Add

**Architecture Diagram** (use Mermaid or ASCII):
```
┌─────────────────────────────────────────┐
│         OpenAI-Compatible API          │
│  /v1/responses  /v1/embeddings  /v1/dreams │
└──────────────┬──────────────────────────┘
               │
         ┌─────▼─────┐
         │  MATRIZ   │  ← Cognitive Engine
         │  (DNA)    │
         └─────┬─────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│ GPT  │  │Claude│  │Google│  ← Model Orchestration
└──────┘  └──────┘  └──────┘
```

### FAQ to Add

```markdown
## FAQ

**Q: Is MATRIZ a replacement for OpenAI?**
A: No, MATRIZ orchestrates OpenAI (and other models) while adding memory, ethics, and adaptation capabilities.

**Q: Can I use my existing OpenAI code?**
A: Yes! Just change the base_url to point at Lukhas. Most OpenAI SDK code works unchanged.

**Q: What's the performance overhead?**
A: <250ms p95 for orchestration + base model latency. Health checks show current performance.

**Q: How does MATRIZ handle sensitive data?**
A: Guardian policies enforce PII redaction, audit logging, and access control. See SECURITY.md.

**Q: Can MATRIZ run on-premises?**
A: Yes, via Docker. See Dockerfile and docker-compose.yml for deployment.
```

### Acceptance Criteria

- [ ] Linked from README and PR template
- [ ] Includes architecture diagram
- [ ] Has competitive comparison
- [ ] FAQ covers common questions
- [ ] Reviewed by product team

---

## H26. Memory Index Mgmt Endpoints

**Branch**: `feat/memory-indexes`
**Priority**: MEDIUM
**Time**: 4-5 hours

### What to Build

CRUD endpoints for memory indexes:
- `GET /v1/indexes` - List indexes
- `POST /v1/indexes` - Create index
- `DELETE /v1/indexes/{id}` - Delete index

### Files to Create

**New**:
- `lukhas/adapters/openai/routes/indexes.py`
- `tests/memory/test_indexes_api.py`

**Update**:
- `lukhas/adapters/openai/api.py` (include router)
- `docs/openapi/lukhas-openai.yaml` (add schemas)

### Implementation Template

```python
from fastapi import APIRouter, HTTPException
from lukhas.memory.orchestrator import MemoryOrchestrator

router = APIRouter(prefix="/v1/indexes")
memory = MemoryOrchestrator()

@router.get("")
async def list_indexes():
    """List all memory indexes."""
    indexes = await memory.list_indexes()
    return {"data": indexes}

@router.post("")
async def create_index(name: str, dimensions: int):
    """Create a new memory index."""
    index_id = await memory.create_index(
        name=name,
        dimensions=dimensions
    )
    return {"id": index_id, "name": name}

@router.delete("/{index_id}")
async def delete_index(index_id: str):
    """Delete a memory index."""
    await memory.delete_index(index_id)
    return {"deleted": index_id}
```

### RBAC Integration

```python
from lukhas.governance.policy_guard import require_permission

@router.post("")
@require_permission("memory:create")
async def create_index(...):
    # ...
```

### Tests

```python
from starlette.testclient import TestClient

def test_list_indexes():
    client = TestClient(get_app())
    r = client.get("/v1/indexes")
    assert r.status_code == 200
    assert "data" in r.json()

def test_create_index():
    client = TestClient(get_app())
    r = client.post("/v1/indexes", json={
        "name": "test-index",
        "dimensions": 1536
    })
    assert r.status_code == 200
    assert r.json()["id"]

def test_delete_index():
    client = TestClient(get_app())
    # Create then delete
    create = client.post("/v1/indexes", json={"name": "temp", "dimensions": 768})
    index_id = create.json()["id"]
    delete = client.delete(f"/v1/indexes/{index_id}")
    assert delete.status_code == 200
```

### Acceptance Criteria

- [ ] All CRUD operations work
- [ ] Tests pass: `pytest -q tests/memory/test_indexes_api.py`
- [ ] RBAC enforced via policy_guard
- [ ] Pagination support for list
- [ ] OpenAPI schema includes examples

---

## General Workflow

For each task:

1. **Create branch**: `git checkout -b type/task-name`
2. **Make changes**: Edit files as specified
3. **Test**: Run relevant tests/checks
4. **Commit**: Use T4 commit format
5. **PR**: Create PR with checklist

### T4 Commit Format

```
<type>(<scope>): <subject>

<optional body>
```

**Types**: feat, fix, docs, style, refactor, test, chore, security
**Scopes**: api, docs, security, ci, config, tests, ops

**Examples**:
- `fix(reports): harden report_manifest_stats against mixed shapes`
- `docs(openai): add quickstart with curl examples`
- `security(ci): add gitleaks as second secret detection line`

---

## Questions?

Check:
- Main planning doc: `PHASE_2_TASK_PLANNING.md`
- Claude Code tasks: `CLAUDE_CODE_TASKS.md` (for dependencies)
- Project conventions: `CLAUDE.md`, `.claude/CLAUDE.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
