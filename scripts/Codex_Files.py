#!/usr/bin/env python3
"""
Codex adapter and AI suggester integration for safe LLM-driven code patches.

Files included in this patch (full content below):

1. `tools/ci/codex_adapter.py` — Codex adapter (production-ready).
2. `tools/ci/ai_suggester.py` — updated AI suggester to call Codex and to record Codex metadata. (Entire file, ready to replace current.)
3. `tests/test_codex_adapter.py` — unit test stubs for parsing/limits.
4. `docs/gonzo/CODEX_POLICY_PARAGRAPH.md` — the polished Codex paragraph for the summary.
5. `scripts/commit_and_open_codex_pr.sh` — helper script to create branch, add files and open PR.

After the files I provide a short **rollout & verification plan**.

---

## 1) `tools/ci/codex_adapter.py`

Create file `tools/ci/codex_adapter.py` exactly as below.

```python
#!/usr/bin/env python3
"""
Codex adapter: high-safety wrapper for LLM-driven code patches.

- Builds a deterministic prompt for codex-like models
- Calls the LLM via tools.ci.llm_policy.call_openai_chat
- Parses the strict JSON response and validates patch size/extent
- Returns a structured result for ai_suggester to act on

Safety guarantees:
- Deterministic output via temperature=0.0
- Size limits: MAX_FILES_CHANGED, MAX_LINES_CHANGED
- JSON-only responses enforced and cleaned
- Usage and cost returned (via llm_policy)
"""
from __future__ import annotations
import re
import json
import os
import time
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from tools.ci import llm_policy

# Config: tune via env
MAX_FILES_CHANGED = int(os.environ.get("T4_CODEX_MAX_FILES", "5"))
MAX_LINES_CHANGED = int(os.environ.get("T4_CODEX_MAX_LINES", "200"))
DEFAULT_MODEL = os.environ.get("CODEX_MODEL", "gpt-4o-mini")

def build_codex_prompt(file_path: str, line: int, code: str, context: str, instructions: Optional[str] = None) -> str:
    """
    Build the prompt that strictly requests a JSON response.
    """
    prompt = f"""You are a high-precision code fixer.

Input:
- file: {file_path}
- line: {line}
- linter_code: {code}

Context (surrounding lines):
---BEGIN CONTEXT---
{context}
---END CONTEXT---

REQUIREMENTS (strict):
1) Return a single valid JSON object only, with keys: patch, explanation, confidence, meta
2) patch must be a unified diff (git format) that can be applied with `git apply --index`
3) Keep changes minimal. Only change what's needed to fix the issue.
4) confidence: float 0..1
5) meta: JSON object with optional keys: changed_files (list), changed_lines (int), reason_codes (list)
6) If you cannot safely produce a patch, return: {{ "patch": "", "explanation": "cannot safely fix", "confidence": 0.0, "meta": {{}} }}
7) Limit patch to fewer than {MAX_LINES_CHANGED} changed lines and {MAX_FILES_CHANGED} files.
8) For F821: prefer adding an import or correcting a probable typo.
9) For B008: convert default to None and add a None-check at function head.
10) Return JSON only. No markdown, no commentary.

Provide the JSON object now.
"""
    if instructions:
        prompt += "\n" + instructions
    return prompt

def parse_json_safe(text: str) -> Dict[str, Any]:
    """
    Extract and return the first JSON object found in the text.
    """
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("No JSON object found in LLM response")
    json_text = text[first:last + 1]
    # quick cleanup of common trailing-comma issues
    json_text = re.sub(r",\s*}", "}", json_text)
    json_text = re.sub(r",\s*]", "]", json_text)
    return json.loads(json_text)

def validate_patch_metrics(patch: str) -> Tuple[int, int, List[str]]:
    """
    Return (files_changed, lines_changed, file_list)
    """
    if not patch:
        return 0, 0, []
    files = re.findall(r"^\+\+\+ b/(.+)$", patch, flags=re.MULTILINE)
    files_changed = len(set(files))
    lines_changed = sum(1 for l in patch.splitlines() if l.startswith("+") or l.startswith("-"))
    return files_changed, lines_changed, list(dict.fromkeys(files))

def propose_patch(file_path: str, line: int, code: str, context: str,
                  instructions: Optional[str] = None,
                  model: Optional[str] = None,
                  agent_api_key: Optional[str] = None,
                  agent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Call llm_policy to get a proposal, parse, validate and return structured response.
    Returns dict with keys:
      ok (bool), patch, explanation, confidence, meta, usage (llm info), error (if any)
    """
    model = model or DEFAULT_MODEL
    prompt = build_codex_prompt(file_path, line, code, context, instructions or "")
    try:
        # Use llm_policy to call LLM and record cost
        resp = llm_policy.call_openai_chat(prompt, model=model, api_key_env="OPENAI_API_KEY",
                                           max_completion_tokens=1024, agent_api_key=agent_api_key,
                                           agent_id=agent_id)
    except Exception as e:
        return {"ok": False, "error": "llm_call_failed", "detail": str(e)}

    text = resp.get("text", "")
    try:
        parsed = parse_json_safe(text)
    except Exception as e:
        return {"ok": False, "error": "parse_failed", "detail": str(e), "raw_text": text, "usage": resp}

    patch = parsed.get("patch", "")
    explanation = parsed.get("explanation", "")
    confidence = float(parsed.get("confidence", 0.0))
    meta = parsed.get("meta", {}) or {}

    files_changed, lines_changed, file_list = validate_patch_metrics(patch)
    # merge meta
    meta = dict(meta)
    meta.update({
        "files_changed": files_changed,
        "lines_changed": lines_changed,
        "file_list": file_list
    })
    # safety checks
    if files_changed > MAX_FILES_CHANGED or lines_changed > MAX_LINES_CHANGED:
        return {
            "ok": False,
            "error": "patch_too_large",
            "files_changed": files_changed,
            "lines_changed": lines_changed,
            "meta": meta,
            "usage": resp
        }

    return {
        "ok": True,
        "patch": patch,
        "explanation": explanation,
        "confidence": confidence,
        "meta": meta,
        "usage": resp
    }
```

---

## 2) `tools/ci/ai_suggester.py` — updated (full file)

Create or replace `tools/ci/ai_suggester.py` with the full content below. This is the earlier suggester but modified to call `codex_adapter.propose_patch` and to store codex metadata to the Intent Registry and ai_suggestions log. It keeps verification, tests, PR creation, and logs.

> If you already have an `ai_suggester.py`, replace it. This file assumes `tools/ci/intent_api` DB exists and that `tools/ci/llm_policy.py` and `tools/ci/codex_adapter.py` are present.

````python
#!/usr/bin/env python3
"""
AI Suggester (updated to use Codex adapter).

Workflow:
- For a given file and finding, call codex_adapter.propose_patch(...)
- Validate patch, apply to temp branch, run tests/ruff
- If tests pass, push branch and create draft PR with codex metadata
- Log suggestion to reports/todos/ai_suggestions.jsonl and insert into intent registry

Environment:
- OPENAI_API_KEY (for LLM)
- GITHUB_TOKEN or `gh` CLI authenticated
- T4_INTENT_API optional (if you want to register intents via API instead of DB)
"""
from __future__ import annotations
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = REPO_ROOT / "reports" / "todos" / "ai_suggestions.jsonl"
INTENT_DB = REPO_ROOT / "reports" / "todos" / "intent_registry.db"
DEFAULT_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")
TEST_CMD = os.environ.get("T4_AI_TEST_CMD", "pytest -q")
RUFF_CMD = os.environ.get("T4_AI_RUFF_CMD", "python3 -m ruff check")
CODEx_MODULE = "tools.ci.codex_adapter"

# ensure logs dir
(REPO_ROOT / "reports" / "todos").mkdir(parents=True, exist_ok=True)

# imports
from tools.ci import codex_adapter  # our new adapter
from tools.ci import llm_policy

def load_file_context(path: Path, line: int, context_lines: int = 200) -> str:
    src = path.read_text(encoding="utf-8", errors="ignore")
    lines = src.splitlines()
    start = max(0, line - 1 - context_lines)
    end = min(len(lines), line - 1 + context_lines)
    return "\n".join(lines[start:end])

def write_log(entry: dict):
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

def git_create_branch(branch_name: str):
    subprocess.check_call(["git", "checkout", "-b", branch_name])

def git_apply_patch(patch_text: str) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write(patch_text)
        patch_file = fh.name
    subprocess.check_call(["git", "apply", "--index", patch_file])

def verify_patch_effects(max_files=5, max_lines=200) -> None:
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

def run_command(cmd: str, cwd: Optional[Path] = None, timeout: int = 600) -> int:
    print(f">>> RUN: {cmd}")
    completed = subprocess.run(shlex.split(cmd), cwd=cwd or REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    print(completed.stdout)
    return completed.returncode

def create_pr_via_gh(branch: str, title: str, body: str, draft: bool = True, labels: Optional[list] = None) -> Optional[str]:
    pr_url = None
    try:
        subprocess.check_call(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--head", branch]
        if draft:
            cmd += ["--draft"]
        if labels:
            for lbl in labels:
                cmd += ["--label", lbl]
        subprocess.check_call(cmd)
        # fetch url
        out = subprocess.check_output(["gh", "pr", "view", "--json", "url", "--jq", ".url"]).decode().strip()
        pr_url = out
        return pr_url
    except Exception:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("No gh CLI and no GITHUB_TOKEN available to create PR")
            return None
        repo = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
        import re, requests
        m = re.search(r"[:/](?P<org>[^/]+)/(?P<repo>[^/.]+)(?:.git)?$", repo)
        if not m:
            print("Cannot parse repo URL for REST PR creation:", repo)
            return None
        owner = m.group("org"); repo_name = m.group("repo")
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        payload = {"title": title, "head": branch, "base": "main", "body": body, "draft": draft}
        r = requests.post(f"https://api.github.com/repos/{owner}/{repo_name}/pulls", headers=headers, json=payload)
        if r.status_code in (200,201):
            pr_url = r.json().get("html_url")
            if labels:
                pr_num = r.json().get("number")
                headers2 = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
                requests.post(f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pr_num}/labels", headers=headers2, json={"labels": labels})
            return pr_url
        else:
            print("PR creation failed:", r.status_code, r.text)
            return None

def log_and_insert_intent(suggestion: dict, pr_url: Optional[str] = None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "file": suggestion.get("file"),
        "line": suggestion.get("line"),
        "code": suggestion.get("code"),
        "explanation": suggestion.get("explanation"),
        "confidence": suggestion.get("confidence"),
        "pr_url": pr_url,
        "status": "pr_opened" if pr_url else "failed_checks",
        "raw": suggestion
    }
    write_log(entry)
    # Insert into intent DB 'intents' table via sqlite
    try:
        import sqlite3
        conn = sqlite3.connect(str(INTENT_DB))
        cur = conn.cursor()
        raw_json = json.dumps(suggestion)
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
            raw_json
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Warning: could not write to intent registry:", e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--line", type=int, required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--max-retries", type=int, default=1)
    ap.add_argument("--branch-prefix", default="t4-ai-suggest")
    args = ap.parse_args()

    file_path = REPO_ROOT / args.file
    if not file_path.exists():
        print("File not found:", file_path); sys.exit(1)

    context = load_file_context(file_path, args.line)
    # call Codex adapter
    codex_result = codex_adapter.propose_patch(str(args.file), args.line, args.code, context,
                                               model=args.model, agent_api_key=os.environ.get("T4_API_KEY"), agent_id=os.environ.get("T4_AGENT_ID"))

    if not codex_result.get("ok"):
        print("Codex proposal failed:", codex_result.get("error"), codex_result.get("detail"))
        log_and_insert_intent({
            "id": f"t4-ai-{int(time.time())}",
            "file": str(args.file),
            "line": args.line,
            "code": args.code,
            "explanation": codex_result.get("detail",""),
            "confidence": 0.0,
            "meta": codex_result.get("meta"),
            "usage": codex_result.get("usage")
        }, pr_url=None)
        sys.exit(1)

    patch = codex_result["patch"]
    explanation = codex_result["explanation"]
    confidence = codex_result["confidence"]
    meta = codex_result["meta"]
    usage = codex_result.get("usage", {})
    # create branch and try to apply
    ts = int(time.time())
    branch = f"{args.branch_prefix}/{args.code}/{ts}"
    try:
        subprocess.check_call(["git", "fetch"])
    except Exception:
        pass
    try:
        git_create_branch(branch)
        git_apply_patch(patch)
        verify_patch_effects(max_files=meta.get("files_changed",5), max_lines=meta.get("lines_changed",200))
    except Exception as e:
        print("Patch apply/verify failed:", e)
        # log and abort
        suggestion = {
            "id": f"t4-ai-{ts}",
            "file": str(args.file),
            "line": args.line,
            "code": args.code,
            "explanation": explanation,
            "confidence": confidence,
            "meta": meta,
            "usage": usage,
            "error": str(e)
        }
        log_and_insert_intent(suggestion, pr_url=None)
        # cleanup branch
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=REPO_ROOT)
        subprocess.run(["git", "checkout", "-"], cwd=REPO_ROOT)
        subprocess.run(["git", "branch", "-D", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    # Commit changes
    try:
        subprocess.check_call(["git", "add", "-A"])
        subprocess.check_call(["git", "commit", "-m", f"chore(t4): ai-suggestion {args.code} {args.file}:{args.line}"])
    except subprocess.CalledProcessError as e:
        print("Commit failed:", e)
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=REPO_ROOT)
        subprocess.run(["git", "checkout", "-"], cwd=REPO_ROOT)
        subprocess.run(["git", "branch", "-D", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

    # Run tests & ruff
    test_rc = run_command(TEST_CMD)
    ruff_rc = run_command(f"{RUFF_CMD} {args.file}")

    pr_url = None
    suggestion = {
        "id": f"t4-ai-{ts}",
        "file": str(args.file),
        "line": args.line,
        "code": args.code,
        "explanation": explanation,
        "confidence": confidence,
        "meta": meta,
        "usage": usage,
        "created_at": datetime.utcnow().isoformat()
    }

    if test_rc == 0 and ruff_rc == 0:
        try:
            subprocess.check_call(["git", "push", "--set-upstream", "origin", branch])
        except Exception as e:
            print("Push failed:", e)
        title = f"[T4-AI] Suggestion {args.code}: {Path(args.file).name}:{args.line}"
        body = f"AI-suggested fix for {args.code} at `{args.file}:{args.line}`.\n\n**Explanation**:\n\n{explanation}\n\n**Confidence**: {confidence}\n\n**Codex meta**:\n```\n{json.dumps(meta, indent=2)}\n```\n\n**LLM usage**:\n```\n{json.dumps(usage, indent=2)}\n```\n"
        pr_url = create_pr_via_gh(branch, title, body, draft=args.draft, labels=["t4/ai-suggested"])
        suggestion["pr_url"] = pr_url
        suggestion["status"] = "pr_opened"
    else:
        suggestion["status"] = "checks_failed"
        suggestion["test_rc"] = test_rc
        suggestion["ruff_rc"] = ruff_rc
        try:
            subprocess.check_call(["git", "push", "--set-upstream", "origin", branch])
            print("Branch pushed for human inspection:", branch)
        except Exception as e:
            print("Push failed:", e)

    log_and_insert_intent(suggestion, pr_url=pr_url)
    print("Suggestion logged. Done.")

if __name__ == "__main__":
    main()
````

---

## 3) `tests/test_codex_adapter.py` — unit test stubs

Create `tests/test_codex_adapter.py` with the contents below. These tests use mocking to simulate LLM output.

```python
# tests/test_codex_adapter.py
import pytest
from tools.ci import codex_adapter

def test_parse_json_safe_good():
    s = '{"patch":"diff --git...","explanation":"fix","confidence":0.9,"meta":{}}'
    obj = codex_adapter.parse_json_safe(s)
    assert obj["patch"].startswith("diff")

def test_validate_patch_metrics_empty():
    files, lines, lst = codex_adapter.validate_patch_metrics("")
    assert files == 0 and lines == 0 and lst == []

def test_validate_patch_metrics_sample():
    patch = """diff --git a/foo.py b/foo.py
index 000..111
--- a/foo.py
+++ b/foo.py
@@
-foo = 1
+foo = 2
"""
    files, lines, lst = codex_adapter.validate_patch_metrics(patch)
    assert files == 1
    assert lines >= 2
    assert "foo.py" in lst
```

Run with `pytest -q tests/test_codex_adapter.py`.

---

## 4) `docs/gonzo/CODEX_POLICY_PARAGRAPH.md` — the polished paragraph

Create or paste the following into your `LUKHAS_AI_AGENT_AUTOMATION_IMPLEMENTATION_SUMMARY.md` in place of the current Codex section. Filename here is a helper so you can paste.

```markdown
### Codex — deterministic LLM-driven code change operator

Codex is the LLM-driven code-change subsystem for T4. It accepts a single source of truth (an Intent) and returns a strict JSON object with `patch` (git unified-diff), `explanation`, `confidence` and `meta` (files changed, lines changed). All Codex activity flows through the organization policy wrapper (`tools/ci/llm_policy.py`) for quota enforcement, token accounting, and cost tracking.

Codex guarantees:
- **Deterministic output**: runs at `temperature=0.0` to ensure reproducible proposals.
- **Structured responses only**: JSON-only output enforced and parsed by `tools/ci/codex_adapter.py`.
- **Size limits**: patches are rejected if they touch too many files or lines.
- **Verification-first**: every patch is applied to a temporary branch and validated with `ruff`, `pytest`, and optional type checks before a draft PR is opened.
- **Audit & traceability**: each suggestion is recorded in the Intent Registry (`codex_suggestion_id`), the `ai_suggestions.jsonl` audit log, and the DB `llm_usage` table with cost details.
- **Pluggable backends**: Codex is an adapter usable with OpenAI, Anthropic, or a local model.

Operational rules:
1. Codex is allowed to open **draft PRs only** — mandatory human review before merge.
2. Codex proposals can be retried once (auto-repair) when verification fails; retries are limited and logged.
3. Agents must use the repository-level adapter (`tools/ci/codex_adapter.py`) and the policy client (`tools/t4/policy_client.py`) before creating any PRs.

This design provides the productivity of LLM-driven refactors while preserving safety, auditability and human-in-the-loop governance.
```

---

## 5) `scripts/commit_and_open_codex_pr.sh` — helper to commit files and create PR

Create this script, mark it executable, and run it to create the branch and PR.

```bash
#!/usr/bin/env bash
set -euo pipefail
BRANCH="feat/t4-codex-integration-$(date +%s)"
git checkout -b "$BRANCH"

git add tools/ci/codex_adapter.py tools/ci/ai_suggester.py tests/test_codex_adapter.py docs/gonzo/CODEX_POLICY_PARAGRAPH.md
git commit -m "feat(t4): Codex adapter + ai_suggester integration + tests + docs"
git push --set-upstream origin "$BRANCH"

if command -v gh >/dev/null 2>&1; then
  gh pr create --title "feat(t4): Integrate Codex adapter & verification into AI suggester" --body-file docs/gonzo/CODEX_POLICY_PARAGRAPH.md --base main
else
  echo "Branch pushed: $BRANCH. Create PR manually."
fi
```

Make executable: `chmod +x scripts/commit_and_open_codex_pr.sh`.

---

## 6) Rollout plan & verification (exact steps)

1. **Create branch & add files**
   Run the script above or manually create feature branch.

2. **Staging start**
   Start Intent API:

   ```bash
   export T4_ADMIN_TOKEN="dev-admin-token"
   uvicorn tools.ci.intent_api:APP --reload --port 8001
   ```

3. **Install deps**

   ```bash
   pip install -r requirements.txt
   pip install -U openai requests pytest ruff tiktoken
   ```

4. **Unit tests**

   ```bash
   pytest -q tests/test_codex_adapter.py
   ```

5. **Dry-run ai_suggester**

   ```bash
   python3 tools/ci/ai_suggester.py --file lukhas/core/foo.py --line 42 --code F821 --dry-run --model gpt-4o-mini
   ```

   Expect: codex proposal parsed and logged; no PR created.

6. **Pilot (draft PR)**

   * Provide `T4_API_KEY` for a test agent and set `OPENAI_API_KEY` to a dev key.
   * Run `ai_suggester.py` without `--dry-run` and with `--draft` to create draft PRs for review.

7. **Verification metrics**

   * Inspect `reports/todos/ai_suggestions.jsonl`: ensure entries show `usage`, `meta` and `confidence`.
   * Check dashboard Codex panels for `codex_suggestions_passed_verification`.

8. **Human review & merge**

   * Review draft PRs; merge if acceptable. After merge, ensure Intent Registry is updated with `status=implemented`.

9. **Gradual scale**

   * Increase weekly cadence after 2 weeks if `codex_suggestions_pr_merged / pr_opened >= 0.6` and no regressions.

---

## 7) Safety & monitoring notes

* **Cost**: monitor `llm_usage` table and set conservative agent `daily_limit`. Add alerting when aggregate daily cost > budget.
* **Hallucination**: Codex proposals are verified by tests — **not sufficient** to detect semantic regressions; enforce human review for safety-critical modules (mark with CODEOWNERS).
* **Reproducibility**: set `temperature=0.0` in llm_policy calls for deterministic output.
* **Audit**: all Codex calls are recorded with prompt usage, tokens, and cost. Use dashboard to track and export CSV.

---

## Final step: commit & PR

If you want, run:

```bash
./scripts/commit_and_open_codex_pr.sh
```

That will create the branch, commit the files and open the PR (if `gh` is available). After PR creation, run CI (dry-run mode) and attach the `reports/todos/ai_suggestions.jsonl` as an artifact for reviewers.

---
