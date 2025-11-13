Artifacts directory: release_artifacts/repo_audit_v2
Config: {"flatten_strategy":"shim-first","dry_run":true,"max_pr_files":25,"required_checks":["verify-syntax-zero","pytest-matriz","ruff"],"reviewers":["@LukhasAi"],"author":"LukhasAI-bot","full_audit":true,"allow_deletion_recommendations":true,"max_proposal_items":50}

**CURRENT CONTEXT (2025-11-05):**
- Comprehensive smoke test work completed: 54 passing tests in 2.3s (100% pass rate)
- Phase 2 smoke tests documented in `release_artifacts/repo_audit_v2/PHASE_2_COMPLETION.md`
- 25 audit artifacts organized under `release_artifacts/repo_audit_v2/` (see GPT_PRO_AUDIT_INDEX.md)
- Smoke tests are complete and validated - focus is now on MATRIZ flattening audit

T4 / 0.01% PROMPT — FULL AUDIT + MATRIZ READINESS (DRY RUN)
You are GPT-Pro. Operate under the T4 lens: be skeptical, evidence-first, and ruthlessly practical. Every claim must include exact commands and the outputs that support it. Prefer reversible, low-risk moves. When in doubt, pick the safer option and mark the decision for human review.

**CONSTRAINTS (must obey)**
- **DRY RUN**: `dry_run=true` — Do NOT push branches, create PRs, tag, or delete anything. Produce patches, scripts, and PR bodies only.
- Use artifacts from `release_artifacts/repo_audit_v2/` as inputs (discovery outputs, flatten_map draft, verification logs).
- Use `.venv` if present. If tools missing, include exact install commands.
- **No destructive deletions**: you may *recommend* deletions/merges but do not perform them. Provide a safe simulate/preview script that runs in a temp branch and does not push.
- **Audit-first**: Before producing patches, run the full audit below and produce a final prioritized recommendation list. Do not propose flatten patches for the entire repo before the audit is reviewed.

---

## Primary mission (order of operations)
1. **Full Audit (Core)** — run a repo-wide forensic audit and produce `release_artifacts/repo_audit_v2/full_audit.md` and structured JSONs:
   - `full_audit_summary.json`
   - `redundant_dirs.csv` (path, reason, evidence_cmd, bytes, file_count)
   - `duplicate_dirs.csv` (pairs or clusters of directories with high duplication score; evidence: file hashes and counts)
   - `unused_dirs.csv` (directories with zero inbound imports, evidence via `import` scan and usage counts)
   - `import_cycles.csv` (detected import cycles with minimal repro commands)
   - `alignment_issues.md` (OpenAI alignment & governance observations)
   - `naming_and_api_issues.md` (public API instability, ambiguous names, E741 hotspots)
2. **Flatten Plan Assessment** — evaluate the existing `flatten_map.csv` and the shim-first strategy.
   - Validate whether the `move_strategy` choices make sense.
   - Propose an **alternative ordering** if it yields lower risk (e.g., flatten low-centrality modules first; or cluster by dependency trees).
   - Produce `flatten_plan_assessment.md` with a ranked suggested plan (PR ordering).
3. **Redundancy & Duplicate Detection (detailed)** — identify:
   - duplicate directories (same contents or large overlap)
   - redundant directories (old, archived, generated, or quarantined directories with no imports or activity)
   - packaging issues: `setup.py`, `pyproject.toml` mismatches, duplicates in `packages = [...]`
   - For each redundant/duplicate directory, provide: `exact_find_command`, `du -sh`, `git log -- <path> | head -n 5`, `rg import usage | wc -l`, and a recommendation: ignore / consolidate / delete / archive.
4. **OpenAI-style Alignment Audit** — produce `alignment_tips.md` with:
   - Quick checklist for safety & governance: model/adapter privilege boundaries, data handling, PII risks, exposure via entrypoints, usage of external APIs (OpenAI, Anthropic), secrets management.
   - Concrete TODOs to improve alignment and auditability (e.g., add sandboxing for adapters, contract tests for ethical policies, deterministic logging for audit trails).
   - Prioritize items by risk to privacy, safety, or misclassification; assign `estimated_effort_minutes`.
   - Provide exact commands or code snippets to produce evidence (e.g., find all places that call OpenAI: `rg "openai\." -n`).
5. **Flattening Plan Refinement** — for the top 50 candidates (use existing `flatten_map.csv`), create:
   - `flatten_map_refined.csv` (updated move_strategy, manual_review flag, reason, estimated_risk, estimated_review_time_minutes)
   - For top 5 candidates: produce dry-run patches (shim or move), PR templates, and per-candidate TODOs (exact shell/AST commands, verification, rollback). Save patches under `release_artifacts/repo_audit_v2/patches/`.
6. **Comprehensive TODO list** — produce `todo_list_full.md` combining flattening tasks, redundancy cleanup tasks, alignment tasks, and CI/packaging tasks. Each TODO must be structured (same format as earlier TODO items) with:
   - exact commands, expected outputs, verification, rollback, estimated effort, priority, owner suggestion.
7. **Risk & Impact Matrix** — produce `impact_matrix.csv` listing each recommended action and columns: `action_id,area,impact_level,risk_level,estimated_effort_minutes,confidence_percent`.
8. **Artifact bundle** — produce `artifact_bundle_full_audit.tar.gz` containing all new artifacts.

---

## Required outputs (files you must create under `release_artifacts/repo_audit_v2/`)
- full_audit.md (T4 narrative + tables)
- full_audit_summary.json
- redundant_dirs.csv
- duplicate_dirs.csv
- unused_dirs.csv
- import_cycles.csv
- alignment_tips.md
- naming_and_api_issues.md
- flatten_map_refined.csv
- patches/<1..5>_shim.patch or <1..5>_move.patch
- pr_templates/<candidate>.md (for top 5)
- todo_list_full.md
- impact_matrix.csv
- verification/ (logs from commands you ran)
- artifact_bundle_full_audit.tar.gz

All outputs must include the exact commands run and their stdout/stderr captured and saved (for example `full_audit.md` must show the command used to compute duplicate directories and the command output snippet as evidence).

---

## Tools and exact commands you are permitted to run (in dry-run)
- Read any file in repository.
- Run local analysis commands (simulated or real if your environment permits): `rg`, `git log -- <path>`, `git rev-parse`, `python3 -m compileall`, `ruff check`, `black --check`, `python -c` AST scripts, `libcst` scripts (we provided `scripts/rewrite_imports_libcst.py`).
- For simulations (e.g., previewing deletion), create a temp branch locally (but do not push). In dry-run you must not push. For preview scripts, place all actions in a script that **only** runs on a branch `simulate/xxx` and prints commands rather than executing destructive ones, or creates a patch file without changing the living tree.
- If you cannot run some command due to environment, include the exact command and a simulated expected output with clear label `SIMULATED_OUTPUT: true`.

---

## Specific checks I insist you perform (evidence required)
1. **Duplicate detection**: compute SHA256 hashes for all files under candidate directories and find directory clusters with >60% identical file hashes. Save a CSV of cluster membership and `rg` evidence showing imports pointing to both clusters (if any).
   - Command example:
     ```
     find candidate -type f -name '*.py' -print0 | xargs -0 sha256sum > /tmp/candidate_hashes.txt
     python3 - <<'PY' ...  # cluster by path prefix
     PY
     ```
2. **Redundant & Unused dirs**: run static import usage to list directories not imported by any other file. Evidence: `rg "from <dir>"` and `rg "import <dir>"` counts = 0. Also check `git log -- <dir>` activity.
3. **Import cycle detection**: use `import-linter`, `snakefood`, or a small AST import walker to detect cycles. Save minimal repro steps to recreate the cycle.
4. **Entry point audit**: list `project.entry-points` (from pyproject.toml) and map to files; ensure each entrypoint module exists and is not a shim pointing to broken code. Provide evidence for each mapping.
5. **OpenAI/External API exposure**: `rg -n "openai\.|anthropic\.|requests\.|aiohttp\.ClientSession" --hidden --no-ignore` and summarize where external calls occur, whether secrets are loaded via env or file, and any unguarded usages.
6. **Testing coverage sensitivity**: show tests (pytest markers) that touch MATRIZ and candidate modules; estimate the fraction of the flatten candidates covered by tests (use `pytest --collect-only -q -m "matriz or tier1"` and map tests to modules).
7. **E741 / naming hotspots**: run `ruff check --select E741 --statistics` and list files in the top 100 E741 hits. Suggest renames for top 20 automatically, but mark as manual where ambiguous.

---

## Recommendation format & human review gates
For every recommended destructive action (delete, remove, merge), produce:
- A one-liner `RISKED_ACTION` (why)
- `EVIDENCE_COMMANDS` (exact commands to validate)
- `SIMULATE_SCRIPT` (exact script that can be run on a disposable branch to show effect)
- `ROLLBACK_INSTRUCTIONS` (exact git commands)
- `APPROVAL_CHECKLIST` (reviewers and checks required before applying)

**For all recommendations produce a `confidence_percent`** (0–100) and `justification` (one paragraph).

---

## Final note (how to present the results)
- Mark every simulated or guessed output clearly as `SIMULATED_OUTPUT: true`.
- Keep the final executive summary short (3–5 sentences) — state the top 5 risks and the 3 highest-priority actions.
- Provide a **ranked list** of PRs to open first (names like `refactor/flatten-vivox-v1`) with `estimated_review_time_minutes` and `expected_diff_size` metrics.

---

**Begin now**. Start with the Full Audit (step 1) and produce the required artifacts. After producing the audit, pause and report a one-paragraph executive summary and the top 5 recommended actions before generating any patches. Remember: evidence and commands for everything. End with a short 5-line plan that says which PRs to open first when `dry_run=false`.
