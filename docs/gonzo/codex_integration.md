#!/usr/bin/env python3
"""
Comprehensive plan for integrating "Codex" LLM-driven code change operator into Lukhas T
4 platform.

Deliverables:

1. A precise design for “Codex” (production-ready) — responsibilities and guarantees.
2. A **Codex adapter** implementation (`tools/ci/codex_adapter.py`) that plugs into your `llm_policy` and `ai_suggester` flows.
3. How to wire Codex into the other Lukhas modules: Intent API, Codemod library, AI suggester, Parallel Batches, Dashboard, and Policy Client. Exact code snippets + DB fields.
4. Safety, audit, and verification flows — the full patch → verify → PR lifecycle.
5. Tests, metrics and rollout steps.
6. A suggested short edit to the Summaries file: the exact paragraph to replace your Codex section with. (Paste this into the file later.)

I keep the tone T4: strict about safety, practical, and built to scale. Let’s go.

---

## 1) Codex: production responsibilities & guarantees (short)

**Purpose:** Codex is the LLM *code-change* subsystem that proposes deterministic code patches (git unified-diff) for lint fixes, codemods, micro-refactors and small feature stubs. It must:

* Return only structured JSON with `patch`, `explanation`, `confidence`, `metadata`.
* Never merge automatically — always produce a human-review PR (or a draft PR).
* Integrate with your `llm_policy.py` so quotas/costs/limits and token accounting are enforced.
* Provide a unique `codex_suggestion_id` and be recorded in the Intent Registry and `ai_suggestions.jsonl`.
* Support multi-backend LLMs via a pluggable adapter (OpenAI, Anthropic, local LLM).
* Support deterministic reruns: same prompt + model → same patch when `temperature=0.0`.
* Support a verification loop: apply patch to a temp branch, run tests + ruff + typechecks. If verification fails, record failure and optionally ask LLM to repair once (configurable).

**Non-functional**: rate-limited, audited, cost-tracked, and has a `confidence` heuristic that combines LLM-provided value with internal heuristics (patch size, tests passed).

---

## 2) `tools/ci/codex_adapter.py` — implementation (drop-in)

This adapter wraps `llm_policy` and produces strict JSON, plus a small prompt template and helper for parsing. It also adds light heuristics for patch size checks.

**File:** `tools/ci/codex_adapter.py`

```python
#!/usr/bin/env python3
"""
Codex adapter: high-safety wrapper for LLM-driven code patches.

Responsibilities:
- Build structured prompt for a given finding (file/line/code/context)
- Call tools.ci.llm_policy.call_openai_chat(...) to get a result (with cost/accounting)
- Parse and validate the returned JSON with fields {patch, explanation, confidence, meta}
- Enforce size and file-change limits and return a well-formed dict to ai_suggester
"""
from __future__ import annotations
import re, json, os, time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from tools.ci import llm_policy
from datetime import datetime

# Config
MAX_FILES_CHANGED = int(os.environ.get("T4_CODEX_MAX_FILES", "5"))
MAX_LINES_CHANGED = int(os.environ.get("T4_CODEX_MAX_LINES", "200"))
DEFAULT_MODEL = os.environ.get("CODEX_MODEL", "gpt-4o-mini")

def build_codex_prompt(file_path: str, line: int, code: str, context: str, instructions: str) -> str:
    """
    Compose a careful prompt that requires a JSON response. Keep instructions explicit.
    """
    prompt = f"""
You are a high-precision code fixer. Input:
- file: {file_path}
- line: {line}
- linter_code: {code}

Context (surrounding lines):
---BEGIN CONTEXT---
{context}
---END CONTEXT---

INSTRUCTIONS (strict):
1) Return a strictly valid JSON object with keys: patch, explanation, confidence, meta
2) patch: a unified-diff (git format). It MUST apply with `git apply --index`.
3) Keep edits minimal: change only the necessary lines and avoid refactors beyond the immediate fix.
4) confidence: a float between 0 and 1 indicating your confidence.
5) meta: object with optional fields: changed_files (list), changed_lines (int), reason_codes (list)
6) If you cannot safely produce a patch, return {"patch":"", "explanation":"cannot safely fix", "confidence":0.0, "meta":{}}
7) Do not add or remove tests; only code changes are accepted.
8) Limit patch to fewer than {MAX_LINES_CHANGED} line changes and fewer than {MAX_FILES_CHANGED} files.
9) For F821: prefer adding an import or correcting a probable typo. For B008: rewrite default to None + add None-check.
10) Return JSON only — no forum text.

Provide the JSON now.
"""
    if instructions:
        prompt += "\n" + instructions
    return prompt

def parse_json_safe(text: str) -> Dict[str, Any]:
    # find outermost JSON object
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("No JSON found in LLM response")
    s = text[first:last+1]
    # basic cleanup
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)
    return json.loads(s)

def validate_patch_metrics(patch: str) -> Tuple[int, int, list]:
    """
    Return (files_changed, lines_changed, file_list)
    """
    # count files by unified diff headers:
    files = re.findall(r"^\+\+\+ b/(.+)$", patch, flags=re.MULTILINE)
    files_changed = len(set(files))
    # lines changed (approx): count lines starting with + or -
    lines_changed = sum(1 for l in patch.splitlines() if l.startswith("+") or l.startswith("-"))
    return files_changed, lines_changed, list(set(files))

def propose_patch(file_path: str, line: int, code: str, context: str, instructions: Optional[str]=None,
                  model: Optional[str]=None, agent_api_key: Optional[str]=None, agent_id: Optional[str]=None) -> Dict[str, Any]:
    model = model or DEFAULT_MODEL
    prompt = build_codex_prompt(file_path, line, code, context, instructions or "")
    # call llm_policy wrapper
    res = llm_policy.call_openai_chat(prompt, model=model, api_key_env="OPENAI_API_KEY", max_completion_tokens=1024,
                                      agent_api_key=agent_api_key, agent_id=agent_id)
    text = res.get("text", "")
    # parse JSON
    try:
        parsed = parse_json_safe(text)
    except Exception as e:
        return {"ok": False, "error": "parse_failed", "detail": str(e), "raw_text": text, "usage": res}
    patch = parsed.get("patch","")
    explanation = parsed.get("explanation","")
    confidence = float(parsed.get("confidence", 0.0))
    meta = parsed.get("meta", {})
    # compute internal metrics
    files_changed, lines_changed, file_list = validate_patch_metrics(patch) if patch else (0,0,[])
    # safety checks
    if files_changed > MAX_FILES_CHANGED or lines_changed > MAX_LINES_CHANGED:
        return {"ok": False, "error": "patch_too_large", "files_changed": files_changed, "lines_changed": lines_changed, "patch": patch}
    # attach llm usage
    return {
        "ok": True,
        "patch": patch,
        "explanation": explanation,
        "confidence": confidence,
        "meta": {
            **meta,
            "files_changed": files_changed,
            "lines_changed": lines_changed,
            "file_list": file_list
        },
        "usage": res
    }
```

**Notes on usage**:

* `ai_suggester.py` should call `codex_adapter.propose_patch(...)` instead of calling llm directly. `ai_suggester` can then run the verification steps already implemented.

---

## 3) Wire Codex into Lukhas modules (exact steps & snippets)

### 3.1 Replace LLM calling in `ai_suggester.py`

Modify `ai_suggester.py` to import `codex_adapter` and call `propose_patch()` rather than `call_llm` directly. The rest of the flow (apply patch → verify → commit → PR) is unchanged.

**Patch snippet**:

```python
# at top
from tools.ci import codex_adapter

# replace building prompt and calling llm with:
result = codex_adapter.propose_patch(str(args.file), args.line, args.code, context, instructions=None, model=args.model, agent_api_key=request_state_agent_key, agent_id=request_state_agent_id)
if not result.get("ok"):
    print("Codex proposal failed:", result.get("error"), result.get("detail"))
    # log and exit...
patch = result["patch"]
explanation = result["explanation"]
confidence = result["confidence"]
usage = result.get("usage")
# continue with apply/verify...
```

### 3.2 Record Codex metadata in Intent Registry and ai_suggestions.jsonl

When logging suggestions or inserting into `intents`, add fields:

* `codex_suggestion`: `{id, model, cost, prompt_tokens, completion_tokens}`
* `ai_agent`: e.g., `"claude-agent-1"` or `"codex-via-openai"`

**Example** (in `log_and_insert_intent`):

```python
suggestion["codex_suggestion_id"] = suggestion.get("id")
suggestion["codex_model"] = model
suggestion["codex_cost"] = usage.get("cost")
# insert into intents.raw
```

This gives you traceability from intent → codex suggestion → PR.

### 3.3 Intent API: add fields & query for codex suggestions

Update `intent_api` to allow queries like `GET /intents?codex_suggestion_id=...` and add `codex_suggestion` object in the stored `raw` column. (Your Intent API already stores `raw`.)

### 3.4 Codemod library: make a `verify_patch` helper

Add `tools/ci/codemods/verify_patch.py` or a helper in `codex_adapter` to run `git apply --index`, `git commit`, test, and rollback on failure. The ai_suggester probably already does this; ensure it calls a central helper.

**Implementation** (pseudo):

```python
def apply_and_verify(patch_text, test_cmds, max_files=5):
    # write patch file, git apply --index
    # git add -A, git commit -m...
    # run tests/test_cmds, run ruff
    # if pass: return True
    # else: git reset --hard HEAD~1 and return failure reason
```

### 3.5 Parallel Batches: add Codex phase

`script/t4_parallel_batches.sh` should optionally run Codex suggestions for each candidate in a controlled loop (dry-run by default). For each candidate: call ai_suggester with codex adapter; open draft PRs only if tests pass.

Add `--codex` flag to the script and limit concurrency.

### 3.6 Dashboard: surface Codex analytics

Add panels to `t4_dashboard.py`:

* `Codex Suggestions`: count of successful suggestions, success rate, avg confidence, avg estimated cost.
* `Top Codex Agents` by count & acceptance.
* `Codex cost` timeseries.

Add SQL queries:

```sql
SELECT COUNT(*) FROM intents WHERE raw LIKE '%"codex_suggestion_id"%';
SELECT AVG(CAST(json_extract(raw, '$.codex_cost') AS REAL)) FROM intents WHERE raw LIKE '%"codex_cost"%';
```

(Your SQLite may need `json_extract` depending on version; otherwise store cost in an indexed column.)

---

## 4) Safety & verification flow (detailed)

Implement this exact flow for every Codex proposal:

1. **Request**: Agent calls Intent API to register the intent (or ai_suggester does it automatically) — `status=reserved`.
2. **Propose**: ai_suggester → codex_adapter.propose_patch(...) returns `patch`, `explanation`, `confidence`, `usage`.
3. **Sanity checks (fast)**:

   * `files_changed <= MAX_FILES_CHANGED`
   * `lines_changed <= MAX_LINES_CHANGED`
   * changed files are within allowed paths (no vendor/third_party)
4. **Apply to temp branch**: `git checkout -b t4-codex/<id>`; `git apply --index patch`
5. **Staging verification**:

   * Run `python -m ruff check`
   * Run `pytest -q` or `T4_AI_TEST_CMD`; run only the relevant test subset if configured
   * Run `mypy` or `pyright` if type-checking is enforced
6. **Outcomes**:

   * **Pass**: push branch, open *draft PR* labeled `t4/ai-suggested`. Add PR body with codex metadata (`usage`, `cost`, `confidence`, `explanation`) and link to Intent.
   * **Fail**: record failure into `ai_suggestions.jsonl` and Intent `raw`, keep branch for human inspection or optionally invoke LLM auto-repair once with appended failure logs (limited retries).
7. **Human review**: reviewer merges after manual check. Upon merge, mark Intent `status=implemented` and record resolved_at.

**Automated retries**: if you implement auto-repair, limit to `max_retries=1` and require `confidence>=0.7` to attempt repair.

**Rollback**: if post-merge regressions found, `regression_detector` finds reintroduced issues and opens a revert PR.

---

## 5) Tests & metrics

**Unit tests**:

* `test_codex_parse.py`: feed mock LLM responses and ensure `parse_json_safe` accepts only correct outputs.
* `test_codex_limits.py`: ensure too-large patches are rejected.

**Integration tests**:

* Mock `llm_policy.call_openai_chat` to return a small unified diff; run full ai_suggester flow, confirm `git apply` + tests pass/fail behavior.

**Dashboard metrics**:

* Add these KPIs:

  * `codex_suggestions_total`
  * `codex_suggestions_passed_verification`
  * `codex_suggestions_pr_opened`
  * `codex_suggestions_pr_merged`
  * `codex_suggestions_avg_confidence`
  * `codex_cost_total` (daily)

---

## 6) Suggested edit to the SUMMARY file (Codex paragraph)

Paste this polished paragraph into `LUKHAS_AI_AGENT_AUTOMATION_IMPLEMENTATION_SUMMARY.md` replacing the existing Codex section. It’s concise, technical and integrates with the T4 platform language:

> **Codex — deterministic LLM-driven code change operator**
> Codex is the LLM-driven code-change subsystem for T4. It accepts a single source of truth (an Intent) and returns *a strict JSON response* that contains a `patch` (git unified-diff), `explanation`, `confidence` and `meta` (files changed, lines changed). All Codex calls flow through `tools/ci/llm_policy.py` for quota and cost accounting. Codex proposals are validated by an automated verification pipeline: apply patch to a temporary branch, run `ruff`, `pytest` and type checks, and reject or open a draft PR if verification fails or passes respectively. Every suggestion is audited in the Intent Registry (linked via `codex_suggestion_id`) and recorded in `reports/todos/ai_suggestions.jsonl` with usage and cost details. Key guarantees: deterministic output (`temperature=0.0`), size limits, single-JSON responses, one-repair retry, mandatory human review before merge, and full audit trail. Codex is pluggable (OpenAI, Anthropic, local) and exposes `tools/ci/codex_adapter.py` as the repository-level interface so other Lukhas modules (ai_suggester, parallel-batches, codemod driver) can reuse the same safety and verification semantics.

---

## 7) Rollout plan (exact)

1. **Feature branch**: `feat/t4-codex-integration`
2. **Add files**: `codex_adapter.py`, modify `ai_suggester.py`, update `intent_api` to store codex metadata. Add tests.
3. **Staging**: deploy Intent API in staging, set `OPENAI_API_KEY` -> dev test key, start `uvicorn`.
4. **Dry-run**: run ai_suggester in `--dry-run` mode over 10 candidates. Collect metrics.
5. **Pilot**: enable draft PR creation for 5 suggestions/week, monitor dashboard and cost.
6. **Wider rollout**: after 2 weeks of pilot and acceptance (>60% pass + no regressions), expand scope and allow more agents.
7. **Lock-in**: once Codex stable and auditable, make agent policy require `codex_adapter` and mark agents `certified`.

---

## 8) Final checklist for your PR

* [ ] Add `tools/ci/codex_adapter.py`
* [ ] Modify `ai_suggester.py` to use adapter
* [ ] Add unit tests for parsing + limits
* [ ] Update Intent API insert to include `codex_suggestion` fields
* [ ] Update `t4_dashboard.py` to include Codex panels
* [ ] Document in `docs/gonzo` and Summaries file (paste paragraph above)
* [ ] Run staging: `uvicorn tools.ci.intent_api:APP --reload`, `python3 tools/ci/ai_suggester.py --dry-run`

---

