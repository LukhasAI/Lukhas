# GPT-Pro Confirmation Request - MATRIZ Flattening Audit

**Date:** 2025-11-03T14:15:00Z
**Mode:** DRY-RUN (no destructive operations)
**Target Repo:** github.com/LukhasAI/Lukhas

---

## Context / Connectors

I have enabled the GitHub connector(s) for:
- **github.com/LukhasAI/Lukhas** (primary)
- **github.com/LukhasAI/LUKHAS-MCP** (MCP servers)

We will perform a **full, T4-grade audit** and (shim-first) flattening readiness analysis on the Lukhas repo. Operate in **DRY-RUN** mode (do not push branches, create PRs, delete files, or tag) until I explicitly flip to apply mode. Save all outputs under: `release_artifacts/matriz_readiness_v1/`.

Before you start the full audit, please **confirm** the following and run the exact checks below. Save each command and stdout/stderr under `release_artifacts/matriz_readiness_v1/discovery/` with meaningful filenames.

---

## 1) Repository Root Access

Please confirm whether you can access the **repository root** recursively for inspection. Run these commands and save outputs:

### Confirm git root
```bash
git rev-parse --show-toplevel > release_artifacts/matriz_readiness_v1/discovery/repo_root.txt 2>&1 || true
```

### Show top-level contents
```bash
ls -la $(git rev-parse --show-toplevel) > release_artifacts/matriz_readiness_v1/discovery/top_level_ls.txt 2>&1 || true
```

### Quick count of Python files
```bash
find $(git rev-parse --show-toplevel) -name "*.py" | wc -l > release_artifacts/matriz_readiness_v1/discovery/python_file_count.txt 2>&1 || true
```

**If you cannot recurse the repo root**, reply with `ACCESS_LIMITED` and explain the exact scope you *can* inspect (for example: `candidate/`, `MATRIZ/`, `scripts/`).

---

## 2) Directory Inspection and Exclusion Policy

**IMPORTANT CLARIFICATION:**
- **Inspect ALL directories** including archive/ and products/ during audit
- **Exclude from deletion/flattening** does NOT mean exclude from inspection
- GPT-Pro must audit archive/ to identify modules for potential restoration
- GPT-Pro must audit products/ as they use matriz components

### Directories to INSPECT but NEVER delete/flatten:
- **`archive/`** - ✅ MUST AUDIT for restoration candidates (8 high-value memory modules documented)
- **`products/`** - ✅ MUST AUDIT as they use matriz components for runtime
- `**/quarantine/**`, `**/quarantine_*/**` - Known syntax errors (excluded from v0.9.1 milestone)
- `dreamweaver_helpers_bundle/**` - Helper utilities (in project excludes)
- `**/generated/**`, `**/migrations/**` - Auto-generated code
- `.venv/`, `venv/`, `build/`, `dist/`, `node_modules/` - Build artifacts
- `docs/openapi`, `manifests/` - API specifications and release artifacts
- Any directories containing **model snapshots, checkpoints or datasets** (require explicit human approval)
- Any path flagged "legacy" or "golden" - Treat as archival reference
- Any directory listed in `.gitignore` or in `pyproject.toml` `exclude`

### Key Policy Points:
1. **archive/lanes_experiment/** contains 8 Priority 1 modules that MUST be assessed for restoration
2. **products/** contains production deployments using matriz - audit for flatten candidates
3. **quarantine/** contains syntax errors - skip these entirely (out of scope)
4. All other directories are fair game for inspection and flattening assessment

### Run and save these checks (place outputs in discovery/):

**Show which of these exist and size:**
```bash
for p in "generated" "migrations" ".venv" "venv" "build" "dist" "node_modules" "archive" "quarantine" "products" "dreamweaver_helpers_bundle" "docs/openapi" "manifests" "legacy" "golden" "data" "datasets"; do
  echo "=== CHECK: $p ===" >> release_artifacts/matriz_readiness_v1/discovery/safe_dirs.txt
  find . -path "./$p" -prune -print -exec du -sh {} \; >> release_artifacts/matriz_readiness_v1/discovery/safe_dirs.txt 2>&1 || true
done
```

**Also list pyproject excludes:**
```bash
python3 - <<'PY' > release_artifacts/matriz_readiness_v1/discovery/pyproject_excludes.txt 2>&1
import tomllib, sys
try:
    d=tomllib.loads(open("pyproject.toml","rb").read().decode())
    ex=d.get("tool",{}).get("ruff",{}).get("exclude",[])
    print(ex)
except Exception as e:
    print("ERROR", e)
PY
```

If you find additional directories that should be considered sacrosanct (e.g., large legacy datasets or private model stores), list them and mark them **SAFE**.

---

## 3) Existing Artifacts to Use as Inputs

Please confirm the presence and provide quick contents (head) of these initial artifact inputs under `release_artifacts/matriz_readiness_v1/`:

- `flatten_map.csv`
- `discovery/top_python_files.txt`
- `discovery/from_imports.txt`
- `discovery/simple_imports.txt`
- `scripts/rewrite_imports_libcst.py`
- `scripts/verify_and_collect.sh`
- `gptpro_config.json` and `strategy.txt`
- `manifest.txt`
- `todo_list.md`

**Run and save:**
```bash
for f in flatten_map.csv discovery/top_python_files.txt discovery/from_imports.txt discovery/simple_imports.txt scripts/rewrite_imports_libcst.py scripts/verify_and_collect.sh gptpro_config.json strategy.txt manifest.txt todo_list.md; do
  echo "=== FILE: $f ===" > release_artifacts/matriz_readiness_v1/discovery/$(basename $f).head.txt 2>&1
  if [ -f "release_artifacts/matriz_readiness_v1/$f" ]; then
    head -n 60 "release_artifacts/matriz_readiness_v1/$f" >> release_artifacts/matriz_readiness_v1/discovery/$(basename $f).head.txt 2>&1
  else
    echo "MISSING" >> release_artifacts/matriz_readiness_v1/discovery/$(basename $f).head.txt
  fi
done
```

If `flatten_map.csv` (initial draft) exists, state whether the agent should **use it as-is**, or **regenerate** it with the generator script; otherwise generate it and save as `release_artifacts/matriz_readiness_v1/flatten_map.csv`.

---

## 4) Environment & Tools

Before running analysis, list missing tools and provide exact install commands (do not install without my confirmation). At minimum, report presence/absence of:
- `black`, `ruff`, `libcst`, `rg` (ripgrep), `jq`, `pytest`, `python3`, `git`, `gh`

**Run:**
```bash
for cmd in python3 git gh rg black ruff pytest jq; do
  which $cmd >/dev/null 2>&1 && echo "$cmd: OK" || echo "$cmd: MISSING"
done > release_artifacts/matriz_readiness_v1/discovery/tool_check.txt

# Also check libcst (Python module)
python3 -c "import libcst; print('libcst: OK')" 2>&1 >> release_artifacts/matriz_readiness_v1/discovery/tool_check.txt || echo "libcst: MISSING" >> release_artifacts/matriz_readiness_v1/discovery/tool_check.txt
```

If a tool is missing and you need it to produce *reproducible* outputs, include exact `pip` commands to install it (e.g., `python3 -m pip install black ruff libcst`) and mark those as recommendations only; do not install or change the environment in dry-run.

---

## 5) Rules & Human Gates (I Require These)

- **DRY_RUN = true**: do not push, create PRs, delete, rename, or tag. Produce patches only.
- **Approval gate**: after the Full Audit is complete, return an executive summary + top-5 recommendations. **Do not** create any patches until I review and say "Proceed to patch generation".
- For any recommended destructive action (delete/merge), produce a `SIMULATE_SCRIPT` that runs only on a disposable branch and **prints** the changes; do not modify the live tree.
- For any proposed deletion of directories with model/data snapshots, mark with `HIGH_RISK` and require explicit human approval.

---

## 6) Deliverable for the Audit Start

When you start, produce a short `audit_start.json` containing:

```json
{
  "timestamp": "...",
  "repo": "LukhasAI/Lukhas",
  "connectors": ["LukhasAI/Lukhas", "LUKHAS-MCP"],
  "dry_run": true,
  "strategy": "shim-first",
  "checks_ran": ["list of the exact commands you ran above"],
  "tool_status_file": "release_artifacts/matriz_readiness_v1/discovery/tool_check.txt",
  "safe_dirs_file": "release_artifacts/matriz_readiness_v1/discovery/safe_dirs.txt"
}
```

---

## Wrap-Up

Once you have confirmed:
- Repository root access (or the allowed subpath),
- Listed and acknowledged the safe directories to exclude from deletion, and
- Confirmed the existing artifact inputs you will use,

Then begin the **Full Audit** and produce:
- `full_audit.md` (T4 narrative)
- CSV artifacts:
  - `redundant_dirs.csv`
  - `duplicate_dirs.csv`
  - `unused_dirs.csv`
  - `import_cycles.csv`
  - `flatten_map_refined.csv`
- `alignment_tips.md`

Save all command outputs and any `SIMULATED_OUTPUT: true` markers where tools or permissions prevented running a command.

**Start with the confirmation outputs requested above, then produce a one-paragraph executive summary and a ranked top-5 list of recommended next steps.**

If anything is unclear or you lack permission, reply with `ACCESS_LIMITED` and exact details of the limitation and the commands that failed.

---

**Ready to proceed?** Confirm the 6 items above, then await my approval before generating patches.
