---
status: active
type: agent-prompts
ai_tool: gemini-code-assist
last_updated: 2025-11-08
---

# Gemini Code Assist - LUKHAS AI Platform Prompts

**Repository Navigation:**
- **Master Context**: [`claude.me`](../../claude.me) / [`lukhas_context.md`](../../lukhas_context.md) - Complete system architecture (7,000+ files)
- **Symbolic Domain**: [`symbolic/claude.me`](../claude.me) / [`symbolic/lukhas_context.md`](../lukhas_context.md) - Symbolic processing context
- **Dual Format Docs**: All directories contain both `claude.me` (Claude Desktop) and `lukhas_context.md` (vendor-neutral) with identical content

**Current Repository Status (2025-11-08):**
- Branch: `main`
- Total Python files: ~7,000
- Testing: 775+ tests across tier-based framework
- Active development: T4 Intent-Driven Platform, F821 cleanup campaign

---

## Current System Status

**Security:**
* **1 vulnerability**: `CVE-2025-50181` in `urllib3 1.26.20` → upgrade to `>= 2.5.0`
* Bandit internal errors in `archive/quarantine_*` - needs scoped re-run

**Code Quality:**
* Ruff: 12,169 errors (E402: 3,672 | invalid-syntax: 1,977 | UP035: 1,350 | F821: 622)
* ~703 auto-fixable issues available

**Testing:**
* Smoke tests: 54 passed, 11 skipped (100% pass rate)
* Integration: 189/345 passed (requires docker infra)

---

## Gemini Code Assist Task Prompts (Prioritized)

### Category: Security (P0)

#### Prompt 1: Upgrade urllib3 to remediate CVE-2025-50181

```bash
git checkout -b chore/upgrade-urllib3-dryrun
poetry add "urllib3>=2.5.0" --lock
pip-audit -r pyproject.toml > release_artifacts/checks/security/pip_audit_after.txt || true
git add pyproject.toml poetry.lock requirements.txt || true
git commit -m "chore(deps): bump urllib3 >=2.5.0 to remediate CVE-2025-50181 (dry-run)"
git format-patch -1 --stdout > release_artifacts/checks/security/patch_upgrade_urllib3_committed.patch
```

**Target files:** `pyproject.toml`, `requirements.txt`, `poetry.lock`
**Expected output:** `pip_audit_after.txt` with CVE removed, patch file, draft PR
**Effort:** 15–45m

---

#### Prompt 2: Scoped Bandit security scan

```bash
bandit -r . -f json -o release_artifacts/checks/security/bandit_scoped.json \
  --exclude .venv,venv,build,dist,archive,quarantine,node_modules || true

python3 - <<'PY'
import json,csv
r=json.load(open('release_artifacts/checks/security/bandit_scoped.json'))
rows=[['file','severity','issue_text']]
for i in r.get('results',[]):
  rows.append([i['filename'],i['issue_severity'],i['issue_text'].replace('\n',' ')[:300]])
csv.writer(open('release_artifacts/checks/security/bandit_scoped_summary.csv','w',newline='')).writerows(rows)
PY
```

**Target files:** `release_artifacts/checks/security/bandit_scoped.json`, `bandit_scoped_summary.csv`
**Expected output:** Clean security report with prioritized HIGH/MEDIUM items
**Effort:** 15–60m

---

### Category: Code Quality (P1)

#### Prompt 3: Ruff batch fixes for E402, F821, UP035

```bash

```bash
ruff check --format json . > release_artifacts/checks/quality/ruff_full.json || true
# Select first 50 files for E402 batch
xargs -a release_artifacts/checks/quality/e402_batch1_files.txt -r isort
xargs -a release_artifacts/checks/quality/e402_batch1_files.txt -r ruff check --fix

git checkout -b chore/lint/e402-batch1-dryrun
git add $(cat e402_batch1_files.txt)
git commit -m "chore(lint): e402 batch1 (dry-run)"
git format-patch -1 --stdout > release_artifacts/quality/e402_batch1.patch
```

**Target files:** Top 50 E402 violations
**Expected output:** Batch patch validated with `make smoke`
**Effort:** 1–3 hrs per batch

---

#### Prompt 4: Test failure → proposal converter

```bash
# Parse pytest logs and generate actionable proposals
python3 tools/error2proposal.py \
  --pytest-log release_artifacts/test_results_summary.txt \
  --output release_artifacts/proposals/proposals.json
```

**Target:** Integration test failures (lz4, meg_bridge, etc.)
**Expected output:** `proposals.json` with patch suggestions
**Effort:** 1–2 hrs

---

#### Prompt 5: Stabilize /v1/models endpoint (caching)

```python
# Add at module scope
_MODEL_LIST_CACHE = None

def _build_model_list():
    current_time = int(time.time())
    # ... existing logic
    
def get_models():
    global _MODEL_LIST_CACHE
    if _MODEL_LIST_CACHE is None:
        _MODEL_LIST_CACHE = _build_model_list()
    return {"object":"list","data": _MODEL_LIST_CACHE}
```

**Target file:** Models endpoint module (see PR #951)
**Expected output:** Deterministic, cacheable model list
**Effort:** 15–45m

---

#### Prompt 6: Docker-compose for integration tests

```yaml
# devtools/docker-compose.integration.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: test
  redis:
    image: redis:7-alpine
  minio:
    image: minio/minio
    command: server /data
```

**Target files:** `devtools/docker-compose.integration.yml`, `scripts/run_integration.sh`
**Expected output:** Reproducible test environment
**Effort:** 2–4 hrs

---

#### Prompt 7: OpenAI adapter migration (18 legacy calls)

```python
# Replace direct openai.* calls with adapter
from llm_adapter import openai_call

# Before:
# response = openai.Completion.create(...)

# After:
response = openai_call(..., engine='...')
```

**Target:** 18 files with `openai.*` imports (see `openai_unexpected.txt`)
**Expected output:** Shimmed adapters with dry-run patches
**Effort:** 3–6 hrs

---

### Category: Infrastructure (P2)

#### Prompt 8: Guardian kill-switch implementation

```python
# guardian/emergency.py
def trigger_kill_switch():
    open('/tmp/guardian_emergency_disable','w').close()

def is_kill_switch_set():
    return os.path.exists('/tmp/guardian_emergency_disable')
```

**Target files:** `guardian/*`, `docs/runbooks/guardian_override_playbook.md`
**Expected output:** Emergency override system + runbook
**Effort:** 1–2 hrs

---

#### Prompt 9: CODEOWNERS + branch protections

```
# .github/CODEOWNERS
/memory/* @memory-team
/guardian/* @security-team
/identity/* @identity-team
```

**Target files:** `.github/CODEOWNERS`, `docs/governance/branch_protection.md`
**Expected output:** Code ownership rules + gh API commands
**Effort:** 30–60m

---

#### Prompt 10: Smoke test stability CI job

```yaml
# .github/workflows/smoke-stability.yml
name: Smoke Test Stability
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
jobs:
  stability:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        run: [1, 2, 3]
    steps:
      - uses: actions/checkout@v3
      - run: make smoke
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: smoke-run-${{ matrix.run }}
          path: test-results/
```

**Target file:** `.github/workflows/smoke-stability.yml`
**Expected output:** Nightly 3× smoke runs with flakiness detection
**Effort:** 30–60m

---

### Category: Documentation & Governance (P3)

#### Prompt 11: PR template with checklists

```markdown
## Changes
<!-- Describe your changes -->

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Smoke tests pass (`make smoke`)

## Security
- [ ] No new vulnerabilities
- [ ] Bandit scan clean
- [ ] Secrets not hardcoded

## References
- Runbook: <!-- link if applicable -->
- Related PR: <!-- link if applicable -->
```

**Target file:** `.github/pull_request_template.md`
**Effort:** 15–30m

---

#### Prompt 12: Coverage badge + gate
```

**Files:** `release_artifacts/checks/quality/ruff_full.json`, `e402_batch1.patch`.
**Expected:** Batch patch; `make smoke` validates.
**Effort:** medium per batch (1–3 hrs). **Priority: P1**.

---

### 4) P1 — Convert top failing integration tests into proposals (error→proposal)

**Goal:** Turn integration test failures into precise TODOs/patches for developers.
**Why Gemini:** can parse pytest logs and propose scaffolding fixes or mocks (e.g., missing `lz4`, `meg_bridge`).
**Approach:**

* Use `error2proposal.py` to parse `pytest` logs and produce `release_artifacts/proposals/proposals.json`.
* For each proposal Gemini generates a patch (if low-risk) or a draft PR body.
  **Expected output:** `release_artifacts/proposals/*.json` and patch files.
  **Effort:** medium (1–2 hrs). **Priority: P0/P1**.

---

### 5) P1 — Diagnose & fix Bandit internal errors (TypeError: unhashable type: 'dict')

**Goal:** Make bandit scan stable and actionable.
**Why Gemini:** it can search for patterns causing Bandit plugin to fail (literal sets/unhashable dicts) and propose small code-safe workarounds or re-run with a more stable Bandit version.
**Approach:**

* Identify the exact offending files (from bandit stdout) in `products/experience/voice/*`.
* For each file, create a safe parsing stub (or skip rule) so bandit will not execute problematic plugin test, or update to Bandit latest; create scoped exceptions for product code if necessary.
  **Expected output:** `bandit_scoped_summary.csv` with actionable items, no internal plugin errors.
  **Effort:** medium (1–3 hrs). **Priority: P1**.

---

### 6) P1 — Stabilize `/v1/models` endpoint (remove per-request timestamp)

**Goal:** Make models endpoint deterministic and cacheable.
**Why Gemini:** small refactor is trivial for Gemini, with tests to validate effect.
**Patch snippet (exact):**

```python
# at module scope
_MODEL_LIST_CACHE = None
def _build_model_list():
    current_time = int(time.time())
    ...
def get_models():
    global _MODEL_LIST_CACHE
    if _MODEL_LIST_CACHE is None:
        _MODEL_LIST_CACHE = _build_model_list()
    return {"object":"list","data": _MODEL_LIST_CACHE}
```

**Files:** the module that implements models endpoint (PR #951 referenced).
**Expected output:** Deterministic model list; `pytest` caching tests pass.
**Effort:** small (15–45m). **Priority: P1**. 

---

### 7) P1 — Create docker-compose for integration test infra

**Goal:** Provide reproducible local infra (Postgres, Redis, S3-minio) for integration tests so they pass locally and in CI.
**Why Gemini:** can author `docker-compose.yml`, health-check scripts, and CI step to spin up the stack, run tests, and tear down.
**Expected:** `devtools/docker-compose.integration.yml` + `scripts/run_integration.sh`.
**Effort:** medium (2–4 hrs). **Priority: P1**.

---

### 8) P1 — Automatic `openai.*` adapter migration shims (18 legacy hits)

**Goal:** Replace the 18 legacy `openai.*` raw calls with `llm_adapter.call(...)` shims (dry-run patches).
**Why Gemini:** excellent at large-scale code transformations with AST tools (libcst / bowler). It can produce safe, reversible shim patches.
**Approach:**

* Find all `openai.` hits (we already have `openai_unexpected.txt`).
* For each file, create a small wrapper `from llm_adapter import openai_call` and replace `openai.Completion.create(...)` with `openai_call(..., engine='...')`.
  **Expected:** `release_artifacts/proposals/llm_adapter_shims/*.patch`.
  **Effort:** medium-high (3–6 hrs). **Priority: P1**. 

---

### 9) P2 — Auto-generate runbook snippets / guardian kill-switch implementation

**Goal:** Implement the documented kill-switch and a short operator runbook.
**Why Gemini:** easy to implement the code-pattern and generate runbook text.
**Patch snippet:**

```python
# guardian/emergency.py
def trigger_kill_switch():
    open('/tmp/guardian_emergency_disable','w').close()

def is_kill_switch_set():
    return os.path.exists('/tmp/guardian_emergency_disable')
# Guardian middleware checks is_kill_switch_set() at request entry.
```

**Files:** `guardian/*`, `docs/runbooks/guardian_override_playbook.md`.
**Effort:** small-medium (1–2 hrs). **Priority: P1**. 

---

### 10) P2 — Create Lukhas.dev proposal card generator & static prototype

**Goal:** Convert `proposals.json` → static cards on Lukhas.dev with “Create Draft PR” & “Open Issue” buttons (backend stub).
**Why Gemini:** great at generating front-end templates and simple API endpoints.
**Files / Output:** `ui/proposals/index.html`, `api/proposals` (static json), `scripts/deploy_proposals.sh`.
**Effort:** small (1–2 hrs). **Priority: P2**.

---

### 11) P2 — Build `error2proposal.py` enhancements (confidence scoring + patch validation)

**Goal:** Add confidence scoring and automated `py_compile`/`ruff` validation of generated patches.
**Why Gemini:** can enrich proposals with static validation and LLM-summarized rationale.
**Expected:** enhanced `release_artifacts/proposals/proposals.json`.
**Effort:** medium (1–3 hrs). **Priority: P2**.

---

### 12) P2 — Generate CODEOWNERS & apply branch protections template

**Goal:** Add `CODEOWNERS` for `memory/*`, `guardian/*`, `identity/*` and create branch-protection template for `main`.
**Why Gemini:** can create correct CODEOWNERS and `gh api` commands for protection.
**Files / Commands:** `.github/CODEOWNERS`, `docs/governance/branch_protection.md`.
**Effort:** small (30–60m). **Priority: P1**.

---

### 13) P2 — Migrate archive/ cleanup plan and salvage audit

**Goal:** Create an `archive_review.csv` and a script to compare each archived item with current docs; generate restoration proposals for high-value modules.
**Why Gemini:** parse tree + heuristics to surface candidate files for restoration/migration.
**Expected:** `release_artifacts/archive/archive_review.csv`, `release_artifacts/archive/restore_proposals/*.md`.
**Effort:** medium (2–4 hrs). **Priority: P2**. 

---

### 14) P2 — Create unit-test skeletons for top failing modules

**Goal:** For high-failure areas (e.g., `test_models.py`, `test_matriz_integration.py`), generate minimal test harnesses/mocks to make integration tests runnable in CI.
**Why Gemini:** can produce test scaffolding and `pytest` fixtures.
**Files:** `tests/fixtures/docker_integration.md`, `tests/test_models_integration.py` skeleton.
**Effort:** medium (2–4 hrs). **Priority: P1**. 

---

### 15) P2 — Add smoke-stability job (3× runs) to CI

**Goal:** Add a nightly GitHub Action that runs smoke 3× to detect flakiness and upload artifacts.
**Why Gemini:** easy to author workflow YAML and artifact upload.
**Files:** `.github/workflows/smoke-stability.yml`.
**Effort:** small (30–60m). **Priority: P1**.

---

### 16) P3 — Bulk `noqa` cleanup & `# noqa` rationalization (RUF100)

**Goal:** Reduce `RUF100` unused `# noqa` by auditing and removing bogus `noqa` comments.
**Why Gemini:** can identify `# noqa` uses and propose removal where safe.
**Effort:** medium (1–3 hrs). **Priority: P2**.

---

### 17) P3 — Generate coverage badge + coverage gate

**Goal:** Add coverage to CI and show badge in README.
**Why Gemini:** config generation & CI change trivial.
**Effort:** small (30–60m). **Priority: P2**.

---

### 18) P3 — Automate PR body templates for audits

**Goal:** Create standard PR template that includes security checklist, testing checklist, and runbook references.
**Why Gemini:** quick to generate consistent PR templates.
**Files:** `.github/pull_request_template.md`.
**Effort:** small (15–30m). **Priority: P3**.

---

### 19) P3 — Generate runbook snippets for GA/rollback sections

**Goal:** Extract the “Emergency Abort Criteria” and produce a short, actionable runbook page.
**Why Gemini:** great at summarizing long runbooks into checklists with commands.
**Effort:** small (30–60m). **Priority: P2**. 

---

### 20) P3 — Create a small “adopted changes” dashboard

**Goal:** Show acceptance/merge rate of audit proposals and open auto-proposals.
**Why Gemini:** data aggregation + frontend generation is trivial for it.
**Effort:** medium (2–4 hrs). **Priority: P3**.

---

### 21) P3 — Lint & formatting CI ratchet

**Goal:** Add a pre-merge check that prevents new Ruff violations of the top N codes.
**Why Gemini:** can create the check and YAML.
**Effort:** small (30–60m). **Priority: P2**.

---

### 22) P3 — Generate a privacy-safe LLM prompt audit pipeline

**Goal:** Add tooling that ensures prompts are hashed & redacted before logging.
**Why Gemini:** produce wrappers & unit tests to ensure no raw prompt leakage.
**Effort:** medium (1–3 hrs). **Priority: P1**.

---


```bash
# .github/workflows/coverage.yml
pytest --cov=lukhas --cov-report=xml
codecov upload-coverage
```

**Target files:** `.github/workflows/coverage.yml`, README badge
**Expected output:** Coverage badge + CI gate at 70%
**Effort:** 30–60m

---

#### Prompt 13: Lint ratchet (prevent new violations)

```bash
# Pre-merge check: only allow fixes, not new E402/F821
ruff check --select E402,F821 --diff > /tmp/ruff_diff.txt
if grep '^+' /tmp/ruff_diff.txt; then
  echo "ERROR: New violations added"
  exit 1
fi
```

**Target file:** `.github/workflows/lint-ratchet.yml`
**Expected output:** CI gate preventing regression
**Effort:** 30–60m

---

#### Prompt 14: PR template with checklists

```markdown
## Testing
- [ ] Unit tests added/updated
- [ ] Smoke tests pass (`make smoke`)

## Security
- [ ] Bandit scan clean
- [ ] No hardcoded secrets
```

**Target file:** `.github/pull_request_template.md`
**Effort:** 15–30m

---

#### Prompt 15: Runbook snippets generator

```python
# Extract emergency procedures from docs/runbooks/*.md
def extract_runbook_commands(path):
    # Parse markdown, find ```bash blocks
    # Generate checklist with copy-pasteable commands
```

**Target:** `docs/runbooks/emergency_procedures.md`
**Expected output:** Operator-friendly checklist
**Effort:** 30–60m

---

### Category: Archive & Cleanup (P3)

#### Prompt 16: Archive salvage audit

```bash
# Compare archive/ with current docs
find archive/ -name "*.py" | while read f; do
  basename_f=$(basename "$f")
  if ! find . -path ./archive -prune -o -name "$basename_f" -print | grep -q .; then
    echo "$f,candidate_for_restoration" >> archive_review.csv
  fi
done
```

**Target:** `archive_review.csv` with restoration candidates
**Effort:** 2–4 hrs

---

#### Prompt 17: Bulk noqa cleanup (RUF100)

```bash
# Remove unused # noqa comments
ruff check --select RUF100 --fix
git diff > noqa_cleanup.patch
```

**Target:** All files with unused `# noqa`
**Expected output:** Clean patch, validated with `make smoke`
**Effort:** 1–3 hrs

---

#### Prompt 18: Adopted changes dashboard

```python
# Parse proposals.json, count merged PRs
proposals = json.load(open('proposals.json'))
adoption_rate = sum(p['status']=='merged' for p in proposals) / len(proposals)
# Generate HTML dashboard
```

**Target:** `lukhas.dev/dashboard/proposals.html`
**Expected output:** Proposal tracking dashboard
**Effort:** 2–4 hrs

---

### Category: Privacy & Security (P1)

#### Prompt 19: LLM prompt audit pipeline

```python
# Hash prompts before logging
import hashlib

def log_prompt_hash(prompt: str):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    logger.info(f"prompt_hash={prompt_hash[:16]}")
```

**Target files:** All LLM adapter modules
**Expected output:** No raw prompts in logs
**Effort:** 1–3 hrs

---

## Workflow: Gemini Code Assist Execution

### 1. Local IDE Integration
```bash
# Copy prompt to Gemini Code Assist chat
# Example: "Execute Prompt 1: urllib3 upgrade"
```

### 2. Batch Mode
```bash
# Run multiple prompts sequentially
for i in {1..5}; do
  gemini-assist execute "Prompt $i" --validate --dry-run
done
```

### 3. Validation Pipeline
```bash
# After Gemini generates code:
make smoke                    # Smoke tests
ruff check --fix              # Linting
pytest tests/unit/            # Unit tests
```

### 4. PR Creation
```bash
# Gemini can auto-generate PR body
git checkout -b chore/gemini-prompt-N
git add .
git commit -m "$(gemini-assist generate-commit-msg)"
gh pr create --fill
```

---

## Success Criteria

- **P0 (Security):** All CVEs patched, Bandit clean
- **P1 (Quality):** E402 <500, F821 <300, smoke tests stable
- **P2 (Infrastructure):** Docker-compose integration, CI gates
- **P3 (Governance):** CODEOWNERS, PR templates, dashboards

---

## References

- **Main docs:** [`lukhas_context.md`](../../lukhas_context.md), [`claude.me`](../../claude.me)
- **T4 Platform:** [`docs/gonzo/T4_ONBOARD_AGENTS.md`](../../docs/gonzo/T4_ONBOARD_AGENTS.md)
- **Test framework:** [`tests/README.md`](../README.md)
- **Makefile targets:** `make help` (50+ targets)

---

**Last updated:** 2025-01-08
**Status:** Prompts ready for Gemini Code Assist execution

1. **Pick a P0/P1 task** (e.g., `urllib3` bump, Bandit re-run, Ruff batch).
2. **Issue an automated-run prompt** to Gemini that includes:

   * `DRY_RUN=true` (no pushes), target branch name, and which artifacts must be written to `release_artifacts/...`.
   * Required tools/versions and test commands (we already specified `make smoke` as canonical).
3. **Gemini** will produce:

   * One or more patch files in `release_artifacts/` (or commits on a dry-run branch),
   * Validation artifacts (pip_audit_after.txt, bandit_scoped_summary.csv, ruff_error_counts.txt, pytest outputs),
   * A draft PR body (if requested) and a short checklist for human review.
4. **Human review** the patch(s); after approval, run the same steps with `apply=true` to open draft PRs (still require human merge).
5. **Iterate**: after each batch is green, continue to the next priority.

---
S
## D — Suggested immediate execution plan (my pick)

1. **Run Gemini to perform tasks 1–3** (urllib3 bump, Bandit scoped re-run, Ruff batch1 dry-run). These unlock security + get us a clear lint plan.
2. **Run testing fixes (task 4)**: convert failing tests into proposals.
3. **Run adapter migration (task 8)** in parallel but in small subsystems.

If you want, I’ll **generate the Gemini prompts** for the top 6 tasks (1–6 above) and the exact `DRY_RUN` instructions (branch names, outputs). Or I can start executing the lower-level actions with the GitHub connector (create dry-run branches + patches). Which do you prefer?
