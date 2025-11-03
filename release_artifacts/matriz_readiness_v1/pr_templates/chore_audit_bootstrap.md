## Summary (TL;DR)
This branch bootstraps the MATRIZ flattening audit by generating discovery artifacts and configuration required for the **Full T4 Audit** (dry-run). It **does not** change product code or apply any flattening — only adds planning and verification artifacts under `release_artifacts/matriz_readiness_v1/`.

**Key purpose:** give GPT-Pro and human reviewers a stable, auditable input set (flatten_map, discovery lists, config, and verification logs) prior to patch generation.

---

## Changes included
All files are added/updated under `release_artifacts/matriz_readiness_v1/`:

- `release_artifacts/matriz_readiness_v1/strategy.txt` — shim-first / dry_run config
- `release_artifacts/matriz_readiness_v1/gptpro_config.json` — GPT-Pro config (dry_run=true)
- `release_artifacts/matriz_readiness_v1/discovery/from_imports.txt` — repo "from" import scan
- `release_artifacts/matriz_readiness_v1/discovery/simple_imports.txt` — repo "import" scan
- `release_artifacts/matriz_readiness_v1/discovery/top_python_files.txt` — top nested python files
- `release_artifacts/matriz_readiness_v1/flatten_map.csv` — generated top-50 flatten candidates
- `release_artifacts/matriz_readiness_v1/verification/*` — logs from verification script (compile / ruff / black / smoke)
- Other supporting files already present: `scripts/rewrite_imports_libcst.py`, `scripts/verify_and_collect.sh`, `todo_list.md`, `manifest.txt`, `patches/`, `pr_templates/`

> Note: If any of these files are unexpectedly missing in the branch, please check the `chore/audit-bootstrap` branch history — this PR is intended to simply stage the audit inputs.

---

## Why this change
- GPT-Pro could not complete the initial Full Audit because several discovery artifacts were missing and the agent could not run recursive local commands. This PR provides those artifacts so GPT-Pro (and human auditors) can run a deterministic dry-run audit using the repo's content.
- Keeps all audit artifacts confined to `release_artifacts/matriz_readiness_v1/` (non-destructive).

---

## How to reproduce locally (reviewer steps)
Run from the repo root:

```bash
# 1. switch to PR branch
git fetch origin
git checkout -b chore/audit-bootstrap origin/chore/audit-bootstrap

# 2. inspect generated artifacts
ls -la release_artifacts/matriz_readiness_v1
head -n 20 release_artifacts/matriz_readiness_v1/flatten_map.csv
head -n 20 release_artifacts/matriz_readiness_v1/discovery/from_imports.txt
head -n 20 release_artifacts/matriz_readiness_v1/discovery/simple_imports.txt

# 3. run verification (optional — may require black/ruff)
chmod +x release_artifacts/matriz_readiness_v1/scripts/verify_and_collect.sh
release_artifacts/matriz_readiness_v1/scripts/verify_and_collect.sh || true

# 4. view verification logs
less release_artifacts/matriz_readiness_v1/verification/compile_log.txt
less release_artifacts/matriz_readiness_v1/verification/ruff_stats.txt
less release_artifacts/matriz_readiness_v1/verification/smoke_test_logs.txt
```

---

## What to check (PR review checklist)

* [ ] Repo connector permissions recorded in `discovery/gh_repo_lukhas.json`
* [ ] `flatten_map.csv`, `from_imports.txt`, `simple_imports.txt`, `gptpro_config.json`, `strategy.txt` exist
* [ ] `verification/compile_log.txt` contains no unrelated SyntaxErrors for active code
* [ ] `strategy.txt` and `gptpro_config.json` have `dry_run=true` and `strategy=shim-first`
* [ ] Backup `backup/pre-flatten-2025-11-03-1316` exists and is recorded

---

## Required checks

* `verify-syntax-zero` (ruff/compile baseline)
* `pytest-matriz` (smoke tests / MATRIZ subset)
* `ruff` (lint baseline)

---

## Risk & rollback

Low risk — non-destructive. To revert:

```bash
git checkout main
git branch -D chore/audit-bootstrap
git push origin --delete chore/audit-bootstrap
```

---

## Next steps after approval

1. Instruct GPT-Pro to re-run Full Audit (dry-run) with these artifact inputs.
2. Review `full_audit.md` + top-5 recommendations.
3. Approve patch generation (dry-run), then flip `dry_run=false` to apply PRs.

