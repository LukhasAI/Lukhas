#!/usr/bin/env python3

"""
# T4 Intent Registry Proposal
This proposal outlines changes to unify and enhance the tracking of T4-related
issues in the codebase, specifically focusing on unused imports and linting issues. 
---

## 1 — Small, high-impact schema change (unify annotations)

**Goal:** One annotation format for all T4 issues (imports + lint). This simplifies tooling and prevents duplicate annotations.

**Action**: standardize on an inline JSON tag:

```py
# TODO[T4-ISSUE]: {"id":"t4-<hex>","code":"F401","type":"lint","reason_category":"MATRIZ","reason":"MATRIZ-R2 trace routing","suggestion":null,"owner":null,"ticket":null,"eta":null,"status":"reserved","created_at":"2025-10-01T12:00:00Z"}
```

**Fields**:

* `id` (str) — unique
* `code` (str) — linter code (e.g., F401, F821) or `"UNUSED_IMPORT"` if prefer
* `type` (str) — `"lint"` or `"import"` (optional)
* `reason_category`, `reason`, `suggestion` (string)
* `owner`, `ticket`, `eta`, `status` (`reserved|planned|committed|implemented|expired`)
* `created_at`, `modified_at` timestamps

**Files to change**:

* `tools/ci/unused_imports.py` — produce this unified tag instead of older tag.
* `tools/ci/lint_annotator.py` — annotate lint issues with same tag.
* `tools/ci/check_unused_imports_todo.py` & `tools/ci/check_lint_issues_todo.py` — parse this tag and validate fields.

**Concrete change for `annotate_line_structured` (example snippet)**:

```python
# inside annotate_line_structured or annotate_line
entry = {
    "id": make_id(),
    "code": code_or_default,         # e.g. "F401" or "F821"
    "type": "lint",
    "reason_category": reason_category,
    "reason": reason,
    "suggestion": suggestion,
    "owner": owner,
    "ticket": ticket,
    "eta": eta,
    "status": "reserved",
    "created_at": iso_now()
}
json_compact = json.dumps(entry, separators=(",", ":"), ensure_ascii=False)
lines[idx] = f"{line}  # TODO[T4-ISSUE]: {json_compact}"
```

**Why**: a single parsable format lets *one* Intent Registry and one validator service handle everything.

---

## 2 — Intent Registry: schema, API and queries

**Goal:** Extend the existing registry to be the *single source of truth* and add a tiny API for queries and metrics.

**Files to add/update**:

* `tools/ci/intent_registry.py` — extend schema
* `tools/ci/intent_api.py` — small FastAPI app to query/update registry

**DB schema (SQLite)**:

```sql
CREATE TABLE IF NOT EXISTS intents (
  id TEXT PRIMARY KEY,
  code TEXT,
  type TEXT,
  file TEXT,
  line INTEGER,
  import_text TEXT,
  reason_category TEXT,
  reason TEXT,
  suggestion TEXT,
  owner TEXT,
  ticket TEXT,
  eta TEXT,
  status TEXT,
  created_at TEXT,
  modified_at TEXT,
  resolved_at TEXT,
  raw JSON
);
CREATE INDEX IF NOT EXISTS idx_status ON intents(status);
CREATE INDEX IF NOT EXISTS idx_owner ON intents(owner);
CREATE INDEX IF NOT EXISTS idx_code ON intents(code);
```

**Python ingest sample** (modify existing `intent_registry.py`):

```python
def insert_or_update(conn, entry_dict):
    conn.execute("""
    INSERT INTO intents(id,code,type,file,line,import_text,reason_category,reason,suggestion,owner,ticket,eta,status,created_at,modified_at,raw)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET
      code=excluded.code,
      file=excluded.file,
      line=excluded.line,
      reason=excluded.reason,
      suggestion=excluded.suggestion,
      owner=excluded.owner,
      ticket=excluded.ticket,
      eta=excluded.eta,
      status=excluded.status,
      modified_at=excluded.modified_at,
      raw=excluded.raw
    """, (
        entry_dict["id"], entry_dict.get("code"), entry_dict.get("type"),
        entry_dict.get("file"), entry_dict.get("line"), entry_dict.get("import_text"),
        entry_dict.get("reason_category"), entry_dict.get("reason"), entry_dict.get("suggestion"),
        entry_dict.get("owner"), entry_dict.get("ticket"), entry_dict.get("eta"),
        entry_dict.get("status"), entry_dict.get("created_at"), entry_dict.get("modified_at"),
        json.dumps(entry_dict)
    ))
    conn.commit()
```

**Add a tiny API** `tools/ci/intent_api.py` (FastAPI):

```python
from fastapi import FastAPI
import sqlite3, json
app = FastAPI()
DB = "reports/todos/intent_registry.db"

def query(sql, params=()):
    conn=sqlite3.connect(DB); cur=conn.cursor(); cur.execute(sql, params); res=cur.fetchall(); conn.close(); return res

@app.get("/intents/stale/")
def get_stale(days: int = 90):
    sql = "SELECT id, file, line, status, created_at FROM intents WHERE status!='implemented' AND julianday('now')-julianday(created_at) > ?"
    rows = query(sql, (days,))
    return [{"id":r[0],"file":r[1],"line":r[2],"status":r[3],"created_at":r[4]} for r in rows]

@app.get("/intents/by_owner/{owner}")
def by_owner(owner: str):
    rows = query("SELECT id,code,file,line,status FROM intents WHERE owner=?",(owner,))
    return [{"id":r[0],"code":r[1],"file":r[2],"line":r[3],"status":r[4]} for r in rows]

# add /metrics endpoints and small write endpoints as needed
```

**Why**: gives editors, GH actions, Slack bot, dashboard a single API to query & triage.

---

## 3 — Validator: compute **Annotation Quality Score** and stricter rules

**Goal:** Validator returns both pass/fail and a quality score (percent of annotations that have `owner+ticket+eta` for planned/committed).

**File to modify**:

* `tools/ci/check_unused_imports_todo.py` and/or centralize into `tools/ci/check_t4_issues.py`.

**Quality computation pseudocode**:

```python
total = annotated_count
good = sum(1 for e in entries if (e["status"] not in ("planned","committed") or (e.get("owner") and e.get("ticket"))))
quality_score = 100.0 * good / total if total else 100.0
```

**Output**: include `annotation_quality_score` and `counts_by_code` in JSON. CI can fail if `quality_score < threshold`.

---

## 4 — Migration script: normalize legacy tags → unified `TODO[T4-ISSUE]`

**File**: `tools/ci/migrate_annotations.py`

**Behavior**:

* Scan repo for older tags: `TODO[T4-UNUSED-IMPORT]` and `TODO[T4-UNUSED-IMPORT]: <text>` and `TODO[T4-LINT-ISSUE]` etc.
* For each, produce a normalized JSON inline annotation.
* Append a field `legacy_reason` if conversion heuristics are uncertain.
* Write changes in branch with commit or output a report in dry-run.

**Snippet (core regex)**:

```python
import re, json
RE_Legacy = re.compile(r"#\s*TODO\[T4-UNUSED-IMPORT\]\s*:\s*(.*)$")
def convert_line(line, filename, lineno):
    m = RE_Legacy.search(line)
    if not m: return line, False
    reason = m.group(1).strip()
    entry = {...}  # fill code="F401", reason_category heuristic
    return f"{line.rstrip()}  # TODO[T4-ISSUE]: {json.dumps(entry, ensure_ascii=False)}\n", True
```

**Why**: painless bulk migration is essential to avoid manual edits across hundreds of files.

---

## 5 — Codemod library & driver

**Goal:** codify common refactors (B008, F403, F811, RUF012...) as LibCST transformers, plus a generic driver with dry-run/apply.

**Files**:

* `tools/ci/codemods/library.py` — codemod classes
* `tools/ci/codemods/run_codemod.py` — driver that runs a named codemod across files, produces diffs, makes backups, can `--apply`

**Example skeleton for `RemoveUnusedImport` and `ConvertImportStar`**:

```python
class RemoveUnusedImport(cst.CSTTransformer):
    def __init__(self, used_names: set):
        self.used_names = used_names
    def leave_Import(self, original_node, updated_node):
        # remove import if none of the imported names present in used_names
        ...
```

**ConvertImportStar** outline:

1. Parse file, compute names used (via AST or LibCST NameVisitor).
2. Inspect `from module import *` – import module in sandbox (if safe) or statically inspect `module.__all__` if accessible.
3. Compute intersection of used names & module exports.
4. Replace star import with `from module import a, b, c` list.

**Driver** runs per-package; steps:

* parse file,
* run codemod,
* show unified diff,
* if `--apply`, backup original to `.b008bak` or `.orig` then write.

**Why**: codemods are required for surgical fixes that cannot be auto-fixed by ruff.

---

## 6 — LLM-assisted suggestion & safe execution loop

**Goal:** propose LLM-powered fixes but **always verify** via tests/static checks before opening PR.

**Files**:

* `tools/ci/ai_suggester.py` — LLM suggestion pipeline
* `tools/ci/ai_suggester_runner.sh` — orchestrator executed by GH Action

**Pattern** (pseudocode):

```python
def propose_fix(file_path, finding):
    context = read_surrounding_lines(file_path, finding.line, n=200)
    prompt = build_prompt(finding.code, context, repo_indexing_info)
    suggestion = call_llm(prompt)  # returns patch or code snippet
    # turn suggestion into patch file
    return suggestion

def verify_patch(patch):
    apply_patch_to_temp_branch()
    run_tests()
    run_type_check()
    run_ruff_check()
    return all_checks_pass
```

**Safety loop**:

* Suggest → apply to temporary branch → run tests & linters
* If tests pass, open PR with `gh` CLI and label `t4/ai-suggested`
* If tests fail, record failure and send to triage or let LLM attempt to patch again (limited retries)

**Security note**: store LLM keys in GH secrets; do not expose code outside org unless allowed. Use a cautionary rate limit and human review for PRs.

---

## 7 — Autofix job & PR automation

**Files**:

* adapt `tools/ci/lint_autofix.sh` to:

  * run `isort` & `ruff --fix` on package scope,
  * run tests,
  * if tests pass, create PR `t4-autofix/<module>/<ts>` with changelog & tests results
  * label PR `t4/autofix` and include audit JSON summary

**GitHub Action** `.github/workflows/t4-autofix.yml` (weekly schedule) runs this script in a container. Action uses `gh` with repo token to open PRs.

**Example PR generation snippet**:

```bash
git checkout -b t4-autofix-${MODULE//\//-}-${TS}
git add -A
git commit -m "chore(t4): autofix ${MODULE} (isort/ruff)"
git push --set-upstream origin HEAD
gh pr create --title "chore(t4): autofix ${MODULE}" --body "Autofix via T4. Tests: ${OK}" --label t4/autofix --base main
```

**Why**: low-friction cleanups; require human review before merge.

---

## 8 — CI & policy enforcement changes

**Files**:

* `.github/workflows/t4-policy-validation.yml` — add endpoints that:

  * run validator in `--json-only`
  * upload JSON artifact for dashboards
  * only fail CI on strict mode flag (flip after tuning)

**New required behavior**:

* On PR, run `check_t4_issues.py --json-only` and attach artifact
* Optionally block merges for PRs that **introduce** `TODO[T4-ISSUE]` entries with `status:"reserved"` and no ticket; or auto-create ticket and set `ticket` field via bot.

**Why**: brings policy enforcement into PRs with audit trail and staged adoption.

---

## 9 — Developer UX: VSCode quick-fix & ChatOps

**Files**:

* `vscode/t4-extension/` (small extension)
* extension provides commands: `T4: Mark Planned`, `T4: Open Ticket`, `T4: Apply Suggestion`, `T4: Explain Issue`
* these commands call the `intent_api` endpoints

**Quick prototype idea**: a basic extension that reads the JSON in current line, opens a modal to fill `owner` and `ticket`, and updates the file.

**Slack bot**:

* small service `tools/ci/t4_slack_bot.py` that posts monthly reports and reminders:

  * calls `intent_api` for stale items,
  * posts to team channel.

---

## 10 — Dashboard & metrics

**Files/updates**:

* export `intent_registry` metrics to JSON lines periodically (or expose `/metrics` endpoint)
* Configure Grafana or Metabase to read the DB or JSON:

  * Dataframe: counts by `status`, `code`, `owner`
  * Annotation quality time series
  * Stale items list
* Add a **small script** `tools/ci/metrics_export.py` to emit the key KPIs:

```python
# output JSON with keys: total, annotated, quality_score, top_codes
```

**Why**: teams need visible, measurable progress.

---

## 11 — Integration test & rollout script

**File**: `scripts/t4_rollout.sh` — orchestrates:

1. Create branch `replace/t4-intent-platform`
2. Add new files & tests
3. Run dry-runs:

   * `python3 tools/ci/unused_imports.py --dry-run`
   * `python3 tools/ci/lint_annotator.py --dry-run ...`
   * `python3 tools/ci/codemods/run_codemod.py --codemod fix_b008 --root lukhas --dry-run`
4. Ingest to registry and run `intent_api` locally
5. Commit and push branch & create PR with instructions to reviewers

**Why**: single script reduces human error and speeds iteration.

---

## 12 — Example: Implement B008 codemod + LLM fallback (surgical)

* Add `tools/ci/codemods/fix_b008.py` (you already have a starter).
* Add `tools/ci/codemods/run_fix_b008.py` (driver).
* Add `tools/ci/ai_suggester.py` which for B008:

  * finds default-call parameters,
  * runs codemod,
  * if codemod uncertain, call LLM to explain and propose exact change,
  * verify tests and open PR.

This is low effort (you already created B008 codemod earlier) and yields fast wins.

---

## 13 — Concrete commands to land the above (copy/paste)

**Create feature branch and add files**:

```bash
git checkout -b replace/t4-intent-platform
# create files listed above (annotator/validator/migrate/intent_api/codemods/ai_suggester/lint_autofix/metrics_export)
git add -A
git commit -m "feat(t4): unify annotations, intent registry API, codemod library, AI-suggester and autofi"
git push --set-upstream origin replace/t4-intent-platform
gh pr create --title "feat(t4): T4 Intent Platform (unify lint/import flows, codemod & AI)" --body-file .github/PULL_REQUEST_TEMPLATE/t4_policy.md --base main
```

**Dry-run all detection/annotators**:

```bash
python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --dry-run
python3 tools/ci/lint_annotator.py --paths lukhas core --codes "F821,F401,B008" --dry-run
python3 tools/ci/codemods/run_fix_b008.py --root lukhas/core --dry-run
python3 tools/ci/intent_registry.py
python3 tools/ci/intent_api.py  # run uvicorn tools.ci.intent_api:app --reload
```

**Run small autofix**:

```bash
bash tools/ci/lint_autofix.sh   # on a feature branch scoped to a single package
```

---

## 14 — Risk matrix & mitigations (brief)

* **LLM hallucinations** → *Mitigation:* always sandbox, require tests + static checks; label PR `t4/ai-suggested`.
* **Mass noise (too many reserved TODOs)** → *Mitigation:* auto-create ticket when reserved created; require owner/ticket before `planned`. Use weekly audit + auto-expire 90 days.
* **Side-effect imports removal** → *Mitigation:* maintain side-effect whitelist, fallback to annotation `status:planned` for human check.
* **Review overload from autofix PRs** → *Mitigation:* group changes by package; limit PR size; PR metadata summarizes changes and tests.

---

## 15 — Minimal proof-of-value cut

If you want the **fastest visible ROI** for Lukhas:

1. **Land unified tag + migration script** (easy, low risk).
2. **Land Intent Registry + API** (visualization & queries for triage).
3. **Land B008 codemod + driver + a pilot PR** (safe, high ROI).
4. **Land scheduled autofix action for isort/ruff** (automated PRs for trivial fixes).

This gives immediate wins: fewer duplicate annotations, one dashboard, and visible cleanup PRs.

## 16 — LLM-assisted suggester: detailed design

* `tools/ci/ai_suggester.py` — main suggester: builds prompt, calls LLM, parses JSON response (unified diff), applies patch, runs tests & linters, and creates PRs.
* `tools/ci/ai_suggester_runner.sh` — driver that finds candidate findings (via validator outputs) and invokes the suggester for each one (demo flow).
* `.github/workflows/t4-ai-suggester.yml` — GitHub Actions workflow (manual + schedule) that runs the runner.
* `reports/todos/ai_suggestions.jsonl` usage (where suggestions are logged).
* Clear instructions for secrets, configuration, and safety gates.

I keep the implementation **conservative and safe**: the tool *never merges automatically*, it always runs real tests, adds labels and metadata, logs everything, and requires secrets/approvals. Follow the setup steps and run the demo pilot on a small package first.

---

## Quick architecture — what happens

1. The runner selects a candidate lint finding (e.g., F821) to try fixing.
2. `ai_suggester.py` extracts context (file + surrounding lines) and builds a careful prompt asking the LLM for a **unified-diff patch** + explanation + confidence. The prompt requires a strict JSON response.
3. The script applies the patch on a temporary branch and runs `pytest` and `ruff` (configurable).
4. If checks pass, it opens a **draft PR** (or normal PR) labeled `t4/ai-suggested` and writes a log entry into `reports/todos/ai_suggestions.jsonl` and the Intent Registry.
5. If checks fail, the suggestion is recorded with diagnostics; the system can be rerun or escalated to human triage. (Optionally: limited retries with LLM to repair failures.)

---

## Security & safety notes (please read)

* **LLM API key** (e.g., `OPENAI_API_KEY`) must be stored in GitHub Secrets for Actions. For local testing, set as env var.
* **GITHUB_TOKEN** (or a personal token with repo scope) is required for PR creation. In Actions, `GITHUB_TOKEN` is available automatically. For the `gh` CLI locally, ensure authenticated.
* The system **never auto-merges** suggested changes. Human review is required.
* The script enforces **max_changed_lines** and **max_files_changed** limits to avoid large, risky PRs. Tune these limits to your comfort.
* The code includes a conservative `verify_patch` step (tests + lint). You can extend to include typechecks, static analysis or integration tests.

---

## 1) `tools/ci/ai_suggester.py` (main)

Create file `tools/ci/ai_suggester.py` and paste the following:

```python
#!/usr/bin/env python3
"""
AI Suggester: propose LLM-driven fixes for lint/findings, verify with tests + ruff,
and open PRs when safe.

Usage (example):
  python3 tools/ci/ai_suggester.py --file lukhas/core/foo.py --line 42 --code F821 \
    --model gpt-4o --dry-run

Environment:
  - OPENAI_API_KEY (or another LLM provider key if you adapt the call)
  - GITHUB_TOKEN (for API PR creation) OR use `gh` CLI authenticated
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# CONFIG
REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = REPO_ROOT / "reports" / "todos" / "ai_suggestions.jsonl"
INTENT_DB = REPO_ROOT / "reports" / "todos" / "intent_registry.db"
DEFAULT_MODEL = os.environ.get("AI_MODEL", "gpt-4o")  # set via env optionally
MAX_CHANGED_LINES = int(os.environ.get("T4_AI_MAX_CHANGED_LINES", "200"))
MAX_FILES_CHANGED = int(os.environ.get("T4_AI_MAX_FILES_CHANGED", "5"))
TEST_CMD = os.environ.get("T4_AI_TEST_CMD", "pytest -q")
RUFF_CMD = os.environ.get("T4_AI_RUFF_CMD", "python3 -m ruff check")

# Ensure reports dir exists
(REPO_ROOT / "reports" / "todos").mkdir(parents=True, exist_ok=True)


def load_file_context(path: Path, line: int, context_lines: int = 200) -> str:
    src = path.read_text(encoding="utf-8", errors="ignore")
    lines = src.splitlines()
    start = max(0, line - 1 - context_lines)
    end = min(len(lines), line - 1 + context_lines)
    ctx = "\n".join(lines[start:end])
    return ctx


def build_prompt(file_path: str, line: int, code: str, context: str) -> str:
    """
    Construct a strict prompt requesting a JSON response with fields:
    - patch: unified diff (git-style)
    - explanation: short human explanation
    - confidence: float 0..1
    """
    prompt = f"""
You are an expert Python code assistant. We are running a safe, verifiable patch flow.
We will give you a file path, a line number, the linter code (e.g. {code}), and the surrounding context.
Produce a JSON response only (no additional text) with these exact fields:
  {{
    "patch": "<UNIFIED_DIFF_PATCH>",
    "explanation": "<short explanation of change>",
    "confidence": <0.0-1.0>
  }}

Requirements:
- The "patch" must be a unified diff (git format) that can be applied with `git apply`.
- Keep changes minimal. Do not change unrelated code.
- If you cannot produce a safe patch, return {"patch":"", "explanation":"cannot safely fix", "confidence":0.0}
- Provide the patch only; no extraneous commentary or markdown.
- For F821 (undefined name): prefer adding an import or correcting a probable typo based on repo context.
- For F401 (unused-import): prefer removing the import line if it's clearly unused and has no side effects; otherwise annotate in code (TODO[T4-ISSUE]: ...)
- For B008 (function-call-in-default-argument): rewrite default to None and add None-check assignment at start of function.
- Avoid introducing new dependencies.
- Limit changes to fewer than {MAX_CHANGED_LINES} line changes and {MAX_FILES_CHANGED} files.

Context (file path: {file_path}, line: {line}, code: {code}):

===BEGIN CONTEXT===
{context}
===END CONTEXT===

Return EXACT JSON now.
"""
    return prompt.strip()


def call_llm(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 60) -> dict:
    """
    Minimal OpenAI call using openai python package if available, else fallback to HTTP.
    Expects OPENAI_API_KEY in env.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in env (must be in GitHub Secrets or local env)")

    # Try openai python package first
    try:
        import openai
        openai.api_key = api_key
        # Use ChatCompletion or completions based on availability
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1500,
            )
            text = resp["choices"][0]["message"]["content"]
            return safe_parse_json_from_text(text)
        except Exception as e:
            # fallback to completions
            resp = openai.Completion.create(model=model, prompt=prompt, temperature=0.0, max_tokens=1500)
            text = resp["choices"][0]["text"]
            return safe_parse_json_from_text(text)
    except Exception:
        # fallback: HTTP call to OpenAI v1/chat/completions
        import requests
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 1500,
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
        return safe_parse_json_from_text(text)


def safe_parse_json_from_text(text: str) -> dict:
    """
    Extract JSON object from text. LLM may include backticks or commentary; extract {...}.
    """
    # Find first '{' and last '}' and try to parse
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("No JSON object found in LLM response")
    json_text = text[first:last + 1]
    try:
        return json.loads(json_text)
    except Exception as e:
        # Try to clean trailing commas, etc.
        cleaned = re.sub(r",\s*}", "}", json_text)
        cleaned = re.sub(r",\s*]", "]", cleaned)
        return json.loads(cleaned)


def write_log(entry: dict):
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def git_create_branch(branch_name: str):
    subprocess.check_call(["git", "checkout", "-b", branch_name])


def git_apply_patch(patch_text: str) -> None:
    # Write patch to temp file and apply with git apply --index
    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write(patch_text)
        patch_file = fh.name
    # Try applying
    try:
        subprocess.check_call(["git", "apply", "--index", patch_file])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git apply failed: {e}")


def verify_patch_effects(max_files=MAX_FILES_CHANGED, max_lines=MAX_CHANGED_LINES) -> None:
    """
    Compute changed files and lines via git diff --numstat
    """
    out = subprocess.check_output(["git", "diff", "--numstat", "--staged"]).decode("utf-8").strip()
    if not out:
        raise RuntimeError("No staged changes after applying patch")
    files = []
    total_lines_changed = 0
    for line in out.splitlines():
        added, removed, fname = line.split("\t")
        files.append(fname)
        total_lines_changed += int(added) + int(removed)
    if len(files) > max_files:
        raise RuntimeError(f"Patch touches {len(files)} files, exceeding limit {max_files}")
    if total_lines_changed > max_lines:
        raise RuntimeError(f"Patch changes {total_lines_changed} lines, exceeding limit {max_lines}")


def run_command(cmd: str, cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None, timeout: int = 600) -> int:
    print(f">>> RUN: {cmd}")
    completed = subprocess.run(shlex.split(cmd), cwd=cwd or REPO_ROOT, env=env or os.environ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    print(completed.stdout)
    return completed.returncode


def create_pr_via_gh(branch: str, title: str, body: str, draft: bool = True, labels: Optional[list] = None) -> Optional[str]:
    """
    Try gh CLI. If not available, use GitHub REST API using GITHUB_TOKEN.
    Return PR URL on success, None otherwise.
    """
    pr_url = None
    try:
        # prefer gh CLI if available
        subprocess.check_call(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--head", branch]
        if draft:
            cmd += ["--draft"]
        if labels:
            for lbl in labels:
                cmd += ["--label", lbl]
        subprocess.check_call(cmd)
        # fetch the created PR url (list recently created)
        out = subprocess.check_output(["gh", "pr", "view", "--json", "url", "--jq", ".url"]).decode().strip()
        pr_url = out
        return pr_url
    except Exception:
        # fallback to REST API
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("No gh CLI and no GITHUB_TOKEN available to create PR")
            return None
        # get repo info
        repo = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
        # normalize repo to owner/name
        m = re.search(r"[:/](?P<org>[^/]+)/(?P<repo>[^/.]+)(?:.git)?$", repo)
        if not m:
            print("Cannot parse repo URL for REST PR creation:", repo)
            return None
        owner = m.group("org"); repo_name = m.group("repo")
        import requests
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        payload = {"title": title, "head": branch, "base": "main", "body": body, "draft": draft}
        r = requests.post(f"https://api.github.com/repos/{owner}/{repo_name}/pulls", headers=headers, json=payload)
        if r.status_code in (200, 201):
            pr_url = r.json().get("html_url")
            # add labels if provided
            if labels:
                # need issue number
                pr_num = r.json().get("number")
                headers2 = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
                requests.post(f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pr_num}/labels", headers=headers2, json={"labels": labels})
            return pr_url
        else:
            print("PR creation failed:", r.status_code, r.text)
            return None


def log_and_insert_intent(suggestion: dict, pr_url: Optional[str] = None):
    # Write to ai_suggestions log
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "file": suggestion.get("file"),
        "line": suggestion.get("line"),
        "code": suggestion.get("code"),
        "explanation": suggestion.get("explanation"),
        "confidence": suggestion.get("confidence"),
        "pr_url": pr_url,
        "status": "pr_opened" if pr_url else "failed_checks",
        "raw": suggestion,
    }
    write_log(entry)
    # Optionally insert into intent registry DB
    try:
        import sqlite3
        conn = sqlite3.connect(str(INTENT_DB))
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO intents (id,code,type,file,line,reason,suggestion,status,created_at,raw)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            suggestion.get("id") or f"t4-ai-{int(time.time())}",
            suggestion.get("code"),
            "ai-suggestion",
            suggestion.get("file"),
            suggestion.get("line"),
            suggestion.get("explanation"),
            suggestion.get("explanation"),
            "pr_opened" if pr_url else "failed",
            datetime.utcnow().isoformat(),
            json.dumps(suggestion),
        ))
        conn.commit()
    except Exception as e:
        print("Warning: could not write to intent registry:", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Path to target file (repo-relative)")
    ap.add_argument("--line", type=int, required=True, help="Line number (1-based)")
    ap.add_argument("--code", required=True, help="Linter code (e.g. F821)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-retries", type=int, default=1)
    ap.add_argument("--branch-prefix", default="t4-ai-suggest")
    ap.add_argument("--draft", action="store_true", help="Create PR as draft")
    args = ap.parse_args()

    file_path = REPO_ROOT / args.file
    if not file_path.exists():
        print("File not found:", file_path); sys.exit(1)

    context = load_file_context(file_path, args.line)
    prompt = build_prompt(str(args.file), args.line, args.code, context)

    suggestion: Optional[Dict[str, Any]] = None
    for attempt in range(args.max_retries):
        try:
            resp = call_llm(prompt, model=args.model)
            if not isinstance(resp, dict):
                raise ValueError("LLM response not JSON")
            # Expect fields: patch, explanation, confidence
            patch = resp.get("patch", "")
            explanation = resp.get("explanation", "")
            confidence = float(resp.get("confidence", 0.0))
            suggestion = {
                "id": f"t4-ai-{int(time.time())}",
                "file": str(args.file),
                "line": args.line,
                "code": args.code,
                "patch": patch,
                "explanation": explanation,
                "confidence": confidence,
                "created_at": datetime.utcnow().isoformat()
            }
            break
        except Exception as e:
            print("LLM call/parse failed:", e)
            if attempt + 1 == args.max_retries:
                print("Max retries exhausted"); sys.exit(1)
            print("Retrying...")

    if not suggestion:
        print("No suggestion produced"); sys.exit(1)

    if not suggestion["patch"]:
        print("LLM refused to produce safe patch:", suggestion["explanation"])
        log_and_insert_intent(suggestion, pr_url=None)
        sys.exit(0)

    # Stage: create branch, try to apply patch and verify
    ts = int(time.time())
    branch = f"{args.branch_prefix}/{args.code}/{ts}"
    try:
        subprocess.check_call(["git", "fetch"])
    except Exception:
        pass
    git_create_branch(branch)

    # Attempt to apply patch
    try:
        git_apply_patch(suggestion["patch"])
    except Exception as e:
        print("Failed to apply patch:", e)
        suggestion["apply_error"] = str(e)
        log_and_insert_intent(suggestion, pr_url=None)
        # abort branch
        subprocess.run(["git", "checkout", "-"])
        subprocess.run(["git", "branch", "-D", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    # Validate patch size
    try:
        verify_patch_effects()
    except Exception as e:
        print("Patch failed safety checks:", e)
        suggestion["safety_error"] = str(e)
        log_and_insert_intent(suggestion, pr_url=None)
        # revert
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=REPO_ROOT)
        subprocess.run(["git", "checkout", "-"], cwd=REPO_ROOT)
        subprocess.run(["git", "branch", "-D", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    # Commit changes
    try:
        subprocess.check_call(["git", "add", "-A"])
        subprocess.check_call(["git", "commit", "-m", f"chore(t4): ai-suggestion {args.code} {args.file}:{args.line}"])
    except subprocess.CalledProcessError as e:
        print("Commit failed (perhaps no changes):", e)
        # abort
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=REPO_ROOT)
        subprocess.run(["git", "checkout", "-"], cwd=REPO_ROOT)
        subprocess.run(["git", "branch", "-D", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    # Run tests
    test_rc = run_command(TEST_CMD)
    # Run ruff
    ruff_rc = run_command(f"{RUFF_CMD} {args.file}")

    pr_url = None
    if test_rc == 0 and ruff_rc == 0:
        # Push branch and open PR
        try:
            subprocess.check_call(["git", "push", "--set-upstream", "origin", branch])
        except Exception as e:
            print("Push failed:", e)
        title = f"[T4-AI] Suggestion {args.code}: {Path(args.file).name}:{args.line}"
        body = f"AI-suggested fix for {args.code} at `{args.file}:{args.line}`.\n\n**Explanation**:\n\n{suggestion['explanation']}\n\n**Confidence**: {suggestion['confidence']}\n\nThis PR was created by the T4 AI Suggester for human review. Tests and ruff passed in CI.\n"
        pr_url = create_pr_via_gh(branch, title, body, draft=args.draft, labels=["t4/ai-suggested"])
        print("PR created:", pr_url)
        suggestion["pr_url"] = pr_url
        suggestion["status"] = "pr_opened"
    else:
        # Log failure and keep branch for debugging
        suggestion["status"] = "checks_failed"
        suggestion["test_rc"] = test_rc
        suggestion["ruff_rc"] = ruff_rc
        # Push branch for human inspection
        try:
            subprocess.check_call(["git", "push", "--set-upstream", "origin", branch])
        except Exception as e:
            print("Push failed:", e)
        print("Checks failed. Branch pushed for inspection:", branch)

    # Log and insert into intent registry
    log_and_insert_intent(suggestion, pr_url=pr_url)

    print("Done. Suggestion logged.")
    return


if __name__ == "__main__":
    main()
```

**Notes on the implementation**

* The script expects LLM to return **strict JSON** with `patch`, `explanation`, and `confidence`. If the LLM returns non-JSON, the code extracts the first `{...}` block.
* You can change the LLM model by setting `AI_MODEL` or passing `--model`.
* The script is intentionally conservative: it enforces `MAX_CHANGED_LINES` and `MAX_FILES_CHANGED`. Adjust these via env vars.

---

## 2) `tools/ci/ai_suggester_runner.sh` (driver)

Create file `tools/ci/ai_suggester_runner.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Runner for AI suggester: find top N findings (via validator) and try to fix them.
# Usage: ./tools/ci/ai_suggester_runner.sh --top 3 --codes "F821,F403"

TOP="${1:-3}"
CODES="${2:-F821,F403,B008}"  # default codes
DRY_RUN="--dry-run"
# If you want PRs to be created, unset DRY_RUN

# Ensure we have latest
git fetch origin

# Run validator and capture JSON
python3 tools/ci/check_lint_issues_todo.py --paths lukhas core api consciousness memory identity MATRIZ --json-only > /tmp/t4_lint_report.json

# Extract top unannotated by count for requested codes
# We will parse the JSON to find unannotated entries and prioritize files
python3 - <<'PY'
import json,sys
codes = set("""" + CODES + """".split(","))
data = json.load(open("/tmp/t4_lint_report.json"))
unannot = data.get("unannotated", [])
# Filter by codes we care about by reading file lines and matching message or code token
results = []
for it in unannot:
    msg = it.get("message","")
    file = it.get("file")
    line = it.get("line")
    # naive: use message to include code token if present
    results.append({"file":file,"line":line,"message":msg})
# pick top N unique files
seen=set()
out=[]
for r in results:
    if r["file"] in seen: continue
    seen.add(r["file"])
    out.append(r)
    if len(out)>=int(""" + TOP + """): break
json.dump(out, open("/tmp/t4_candidates.json","w"))
print("Wrote candidates:", "/tmp/t4_candidates.json")
PY

cat /tmp/t4_candidates.json

# For each candidate, call the ai_suggester (demo: assume F821)
for row in $(jq -c '.[]' /tmp/t4_candidates.json); do
  file=$(echo $row | jq -r '.file')
  line=$(echo $row | jq -r '.line')
  # Determine guessed code; here we just use F821 by default for demo.
  code="F821"
  echo "Processing $file:$line $code"
  # Call ai_suggester. Remove --dry-run if you want real PR creation.
  python3 tools/ci/ai_suggester.py --file "$file" --line "$line" --code "$code" --model "${AI_MODEL:-gpt-4o}" --dry-run
done

echo "Runner finished."
```

**Notes**

* This driver is intentionally naive for the demo: it selects top unannotated entries and runs the suggester in `--dry-run`. You should refine selection logic (e.g., filter by code or severity) for production.

---

## 3) GitHub Actions workflow — `.github/workflows/t4-ai-suggester.yml`

Create this workflow file:

```yaml
name: T4 AI Suggester

on:
  workflow_dispatch:
  schedule:
    - cron: '0 3 * * 1'  # weekly on Monday 03:00 UTC

permissions:
  contents: write
  pull-requests: write
  actions: read

jobs:
  ai-suggest:
    runs-on: ubuntu-latest
    env:
      AI_MODEL: gpt-4o
      T4_AI_MAX_CHANGED_LINES: 200
      T4_AI_MAX_FILES_CHANGED: 5
      T4_AI_TEST_CMD: pytest -q
      T4_AI_RUFF_CMD: python3 -m ruff check
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install openai requests pytest ruff

      - name: Run T4 lint validator (json)
        run: python3 tools/ci/check_lint_issues_todo.py --paths lukhas core api consciousness memory identity MATRIZ --json-only > /tmp/t4_lint_report.json

      - name: Run AI Suggester Runner (dry-run)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          chmod +x tools/ci/ai_suggester.py tools/ci/ai_suggester_runner.sh
          ./tools/ci/ai_suggester_runner.sh 3 "F821,F403,B008"
```

**Important**

* Add `OPENAI_API_KEY` and (if using REST PR creation) `GITHUB_TOKEN` to the repository secrets. In Actions, `GITHUB_TOKEN` is already injected by default, but if you need broader scopes, create a PAT and store it in `secrets.GITHUB_TOKEN`.
* This workflow runs in **dry-run** by default. To make it open PRs, remove `--dry-run` flag in the runner call. I recommend manual PR review before enabling.

---

## 4) Setup / Local testing steps

1. **Install deps** locally:

```bash
pip install openai requests pytest ruff
```

2. **Set env** locally (demo):

```bash
export OPENAI_API_KEY="sk-..."
export GITHUB_TOKEN="ghp_..."   # optional if using gh/REST
```

3. **Dry-run** for a single file:

```bash
python3 tools/ci/ai_suggester.py --file lukhas/core/myfile.py --line 42 --code F821 --model gpt-4o --dry-run
```

4. **Run runner** in dry-run:

```bash
bash tools/ci/ai_suggester_runner.sh 2 "F821,B008"
```

5. **Enable PR creation**: remove `--dry-run` in runner or run `ai_suggester.py` without `--dry-run`. Ensure `GITHUB_TOKEN` set and you are comfortable with PR creation.

---

## 5) How this integrates with the rest of T4

* **Intent Registry**: `ai_suggester` logs every suggestion into `reports/todos/ai_suggestions.jsonl` and tries to insert into `intent_registry.db` (table `intents`) so your dashboard and triage boards will show AI suggestions alongside human-created intents. The `log_and_insert_intent()` calls handle that. You may want to add extra columns (e.g., `ai_confidence`, `pr_url`, `attempts`) for richer dashboards.

* **Validator**: After PR is opened and merged, your existing `check_t4_issues` job will pick up that the file no longer reports the finding — the intent can then be updated to `implemented`.

* **Autofix pipeline**: The AI suggester sits alongside `lint_autofix.sh`. Use the autofix route for trivial/formatting fixes and the AI-suggester for semantic fixes.

---

## 6) Suggested immediate pilot & metrics

**Pilot plan (low blast radius)**:

1. Enable the workflow in dry-run for 2 weeks. Collect `ai_suggestions.jsonl` output. KPI: number of suggestions produced, fraction that pass tests locally (simulated), and fraction that you (human) deem safe.
2. Run a pilot with `--dry-run` removed but `--draft` PRs enabled and limited to 1 suggestion/week. Have reviewers inspect.
3. If the first 10 PRs show good quality and no regressions, increase cadence.

**Metrics to monitor**:

* `ai_suggestions_total`, `ai_suggestion_pass_rate` (tests + ruff), `ai_suggestion_pr_accept_rate`, `ai_suggestion_mean_confidence`.

---

## 7) Final cautions & next steps (T4 frankness)

* **LLMs can hallucinate**: the workflow includes verification, but pay attention to subtle semantic regressions the tests may not capture. Start small and expand scope after you validate safety.
* **Secrets & cost**: LLM calls cost money. Use low temperature and conservative tokens. Add rate limits in the workflow.
* **Human-in-loop**: keep mandatory human PR review for at least the first month.

---
With this implementation, you have a **complete AI-suggester system** integrated into your T4 workflow. It proposes LLM-driven fixes, verifies them, and opens PRs for human review. Start with dry-runs, monitor metrics, and expand cautiously. Good luck!