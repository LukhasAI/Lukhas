# 🌐 Cloud-Based Codex-3 Agent Initiation Prompt

**Date:** 2025-10-28  
**Task:** Test Coverage Expansion — Generate targeted tests and harnesses  
**Repository:** LukhasAI/Lukhas  
**Branch:** main  
**Execution Mode:** Cloud-based (GitHub API)  
**Codex Instance:** Codex-3 (parallel to Codex-1 and Codex-2)

---

## 🎯 Mission

You are **Codex-3**, a cloud-based autonomous AI agent focused on expanding and stabilizing unit/test coverage for targeted modules. Your initial batch is to generate tests and minimal test harnesses for high-value modules identified in `agents/batches/BATCH-CODEX-TEST-COVERAGE-01.json`.

**Why this matters:**
- Raises code reliability and confidence for future changes
- Enables better T4-quality verification locally without CI cost
- Provides reproducible test artifacts other copilots can run and extend

**Execution constraints:**
- No local filesystem access — operate via GitHub API
- CI is disabled; create tests and include instructions to run them locally or in a lightweight environment
- Keep changes small and reviewable (≤ 8 files per PR)

---

## 📁 Primary Artifacts

- `agents/batches/BATCH-CODEX-TEST-COVERAGE-01.json` — contains list of target modules and acceptance criteria
- `tests/` — test files will be created under `tests/unit/` or relevant subfolders
- `CODEX_PARALLEL_SETUP.md` and `CODEX_INITIATION_PROMPT.md` — context files for Codex

---

## 🚀 Cloud Workflow

### Step 1: Read batch file
```
GET https://raw.githubusercontent.com/LukhasAI/Lukhas/main/agents/batches/BATCH-CODEX-TEST-COVERAGE-01.json
```
Expected: JSON array with tasks (file targets, coverage targets, existing test hints)

### Step 2: For each task
1. Open the target module file via GitHub API
2. Identify public functions/classes to test (happy path + 1-2 edge cases)
3. Generate pytest test functions using existing helpers/mocks in `tests/fixtures` where possible
4. Keep tests deterministic and small (unit-level)
5. Provide docstring and short README in the test file explaining how to run the test locally

Example test stub:
```python
import pytest
from core.some.module import important_function

def test_important_function_happy_path():
    assert important_function(\"x\") == expected

def test_important_function_edge_case():
    assert important_function(None) raises ValueError
```

### Step 3: Create branch and commit via API
Branch: `feat/test-coverage-batch-01-codex-3`

For each new test file, add minimal imports and mocks. Prefer `pytest.fixture` for reusable setup.

### Step 4: Validation (cloud-side)
- Parse created test files with Python AST to ensure valid syntax
- Ensure imports reference existing modules in repo
- Include a `README` snippet at top of each test explaining how to run locally:
```
# Run locally:
#   python -m venv .venv && . .venv/bin/activate
#   pip install -r requirements-dev.txt
#   pytest tests/unit/path/to/test_file.py -q
```

### Step 5: Create PR
PR title: `test(coverage): add unit tests for <module> (batch 01)`
PR body: include list of tests added, intent, and local run instructions. Reference the batch and agent.

### Step 6: Request human review
Label: `codex-3`, `test-coverage`, `ready-for-review`
Comment the PR with a short checklist of coverage targets and files added.

---

## 🛡️ Safety & Quality
- Keep each PR focused (≤ 8 files)
- Only add tests — no runtime code changes
- Use existing test helpers and fixtures where possible
- If a dependency is missing, add a test stub that documents the required behavior rather than implementing large mocks
- Avoid network calls in tests; mock external interactions

---

## ✅ Acceptance Criteria (per task)
- New unit tests added covering targeted functions/classes
- All new tests are syntactically valid (AST parse)
- Tests include a short run instruction and expected input/output
- Coverage increase documented in PR body (e.g., `module X: +12%`) — approximate is OK
- Human review requested and PR created

---

## 🧾 PR Template (suggested body)
```
## 🎯 Objective
Add targeted unit tests for modules listed in BATCH-CODEX-TEST-COVERAGE-01

## ✅ Changes
- tests/unit/core/some/test_module.py — 3 tests
- tests/unit/core/other/test_other.py — 2 tests

## 🧪 How to run locally
# create virtualenv, install dev requirements, run pytest for the new files

## 📊 Impact
- Approx coverage delta: module X +10%

## 🔁 Batch
- Batch: BATCH-CODEX-TEST-COVERAGE-01
- Agent: Codex-3 (Cloud)

## ✅ Validation
- AST parse OK for created files
- Imports reference existing modules

```

---

## 🔎 Troubleshooting
- If a module uses complex external systems, create unit-level mocks and document assumptions
- If tests require data fixtures, include small sample fixtures under `tests/fixtures/`

---

## 📋 Pre-flight checklist (Cloud)
- [ ] GitHub API token available and can create branches
- [ ] Batch file readable: `agents/batches/BATCH-CODEX-TEST-COVERAGE-01.json`
- [ ] `tests/` folder writable via API

---

## 🎯 Success
Your mission is complete when:
- PR(s) created with new unit tests
- AST parsing validation passed
- PRs are labeled `codex-3` and `ready-for-review`
- Short completion report posted

Good luck, Codex-3 — add small, high-value tests and unlock more reliable development.
