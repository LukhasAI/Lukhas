⸻
# GPT-Pro Confirmation Request - MATRIZ Flattening Audit

**Date:** 2025-11-03T14:15:00Z (Updated: 2025-11-05)
**Mode:** DRY-RUN (no destructive operations)
**Target Repo:** github.com/LukhasAI/Lukhas

---

## Context / Connectors

I have enabled the GitHub connector(s) for:
- **github.com/LukhasAI/Lukhas** (primary)
- **github.com/LukhasAI/LUKHAS-MCP** (MCP servers)

**CURRENT STATE (2025-11-05):**
- Comprehensive smoke test suite completed: 54 passing tests (100% pass rate, 2.3s runtime)
- 7 new smoke test suites added covering: secrets, memory, guardian, ACL, routing, dependencies, lifecycle
- 25 audit artifacts organized and accessible in `release_artifacts/repo_audit_v2/`
- Full Phase 2 completion documented in `PHASE_2_COMPLETION.md`
- Smoke tests validated and NOT the focus - ready for MATRIZ flattening audit

We will perform a **full, T4-grade audit** and (shim-first) flattening readiness analysis on the Lukhas repo. Operate in **DRY-RUN** mode (do not push branches, create PRs, delete files, tag, or modify the live repo) until I explicitly flip to apply mode. Save all outputs under: `release_artifacts/repo_audit_v2/`.

**Policy / operational knobs:**
- reviewers = ["@LukhasAI"]
- required_checks = ["verify-syntax-zero", "pytest-matriz", "ruff"]
- max_automerge_files = 300  # agent must not propose auto-applying changes > this threshold
- dry_run = true (do not push)
- strategy = shim-first
- author = "LukhasAI-bot"

Before you start the full audit, please **confirm** the following and run the exact checks below. Save each command and stdout/stderr under `release_artifacts/repo_audit_v2/discovery/` with meaningful filenames.

---

## 1) Repository Root Access

Please confirm whether you can access the **repository root** recursively for inspection. Run these commands and save outputs:

```bash
git fetch --all
git rev-parse --show-toplevel > release_artifacts/repo_audit_v2/discovery/repo_root.txt 2>&1 || true
ls -la $(git rev-parse --show-toplevel) > release_artifacts/repo_audit_v2/discovery/top_level_ls.txt 2>&1 || true
find $(git rev-parse --show-toplevel) -name "*.py" | wc -l > release_artifacts/repo_audit_v2/discovery/python_file_count.txt 2>&1 || true

If you cannot recurse the repo root, reply with ACCESS_LIMITED and explain the exact scope you can inspect (for example: candidate/, MATRIZ/, scripts/).

Also verify GitHub connector permissions:

gh repo view LukhasAI/Lukhas --json name,visibility,permissions > release_artifacts/repo_audit_v2/discovery/gh_repo_lukhas.json 2>&1 || true
gh repo view LukhasAI/LUKHAS-MCP --json name,visibility,permissions > release_artifacts/repo_audit_v2/discovery/gh_repo_mcp.json 2>&1 || true


⸻

2) Directory Inspection and Exclusion Policy

IMPORTANT CLARIFICATION:
	•	Inspect ALL directories including archive/ and products/ during audit
	•	Exclude from deletion/flattening does NOT mean exclude from inspection
	•	GPT-Pro must audit archive/ to identify modules for potential restoration
	•	GPT-Pro must audit products/ as they use matriz components

Directories to INSPECT but NEVER delete/flatten:
	•	archive/ - ✅ MUST AUDIT for restoration candidates (8 high-value memory modules documented)
	•	products/ - ✅ MUST AUDIT as they use matriz components for runtime
	•	**/quarantine/**, **/quarantine_*/** - Known syntax errors (excluded from v0.9.1 milestone)
	•	dreamweaver_helpers_bundle/** - Helper utilities (in project excludes)
	•	**/generated/**, **/migrations/** - Auto-generated code
	•	.venv/, venv/, build/, dist/, node_modules/ - Build artifacts
	•	docs/openapi, manifests/ - API specifications and release artifacts
	•	Any directories containing model snapshots, checkpoints or datasets (require explicit human approval)
	•	Any path flagged “legacy” or “golden” - Treat as archival reference
	•	Any directory listed in .gitignore or in pyproject.toml exclude

Key Policy Points:
	1.	archive/lanes_experiment/ contains 8 Priority 1 modules that MUST be assessed for restoration
	2.	products/ contains production deployments using matriz - audit for flatten candidates
	3.	quarantine/ contains syntax errors - skip these entirely (out of scope)
	4.	All other directories are fair game for inspection and flattening assessment

Run and save these checks (place outputs in discovery/):

Show which of these exist and size (robust recursive search):

mkdir -p release_artifacts/repo_audit_v2/discovery
for p in generated migrations .venv venv build dist node_modules archive quarantine products dreamweaver_helpers_bundle "docs/openapi" manifests legacy golden data datasets; do
  echo "=== CHECK: $p ===" >> release_artifacts/repo_audit_v2/discovery/safe_dirs.txt
  find . -type d -name "$(basename $p)" -print -exec du -sh {} \; >> release_artifacts/repo_audit_v2/discovery/safe_dirs.txt 2>&1 || true
done

Also list pyproject excludes:

python3 - <<'PY' > release_artifacts/repo_audit_v2/discovery/pyproject_excludes.txt 2>&1
import tomllib, sys
try:
    d=tomllib.loads(open("pyproject.toml","rb").read().decode())
    ex=d.get("tool",{}).get("ruff",{}).get("exclude",[])
    print(ex)
except Exception as e:
    print("ERROR", e)
PY

If you find additional directories that should be considered sacrosanct (e.g., large legacy datasets or private model stores), list them and mark them SAFE.

⸻

3) Existing Artifacts to Use as Inputs

**CURRENT ARTIFACTS (2025-11-05):**
The following artifacts are already organized in `release_artifacts/repo_audit_v2/`:
- **GPT_PRO_AUDIT_INDEX.md** - Complete navigation guide for all 25 audit files
- **FILE_MANIFEST.txt** - Organized list of all audit artifacts by category
- **PHASE_2_COMPLETION.md** - Comprehensive smoke test Phase 2 report (54 tests)
- **SMOKE_TEST_IMPROVEMENTS_SUMMARY.md** - Smoke test implementation details
- **ci/** - GitHub Actions workflow and branch protection configs
- **security/** - LLM adapter isolation scan results
- **tests/** - Smoke test documentation and Makefile targets
- **discovery/** - Repository discovery outputs

To explore these artifacts, reference: `release_artifacts/repo_audit_v2/GPT_PRO_AUDIT_INDEX.md`

**For MATRIZ flattening audit**, if these files exist under an older artifact directory, confirm their presence:
	•	flatten_map.csv
	•	discovery/top_python_files.txt
	•	discovery/from_imports.txt
	•	discovery/simple_imports.txt
	•	scripts/rewrite_imports_libcst.py
	•	scripts/verify_and_collect.sh
	•	gptpro_config.json and strategy.txt
	•	manifest.txt
	•	todo_list.md

Run and save:

ART="release_artifacts/repo_audit_v2"
for f in flatten_map.csv discovery/top_python_files.txt discovery/from_imports.txt discovery/simple_imports.txt scripts/rewrite_imports_libcst.py scripts/verify_and_collect.sh gptpro_config.json strategy.txt manifest.txt todo_list.md; do
  echo "=== FILE: $f ===" > $ART/discovery/$(basename $f).head.txt 2>&1
  if [ -f "$ART/$f" ]; then head -n 60 "$ART/$f" >> $ART/discovery/$(basename $f).head.txt 2>&1; else echo "MISSING" >> $ART/discovery/$(basename $f).head.txt; fi
done

If flatten_map.csv (initial draft) exists, state whether the agent should use it as-is, or regenerate it with the generator script; otherwise generate it and save as release_artifacts/repo_audit_v2/flatten_map.csv.

⸻

4) Environment & Tools

Check tools and list missing ones (do not install without confirmation). At minimum, report presence/absence of:
	•	black, ruff, libcst, rg (ripgrep), jq, pytest, python3, git, gh

Run:

for cmd in python3 git gh rg black ruff pytest jq; do
  which $cmd >/dev/null 2>&1 && echo "$cmd: OK" || echo "$cmd: MISSING"
done > release_artifacts/repo_audit_v2/discovery/tool_check.txt

python3 -c "import libcst; print('libcst: OK')" 2>&1 >> release_artifacts/repo_audit_v2/discovery/tool_check.txt || echo "libcst: MISSING" >> release_artifacts/repo_audit_v2/discovery/tool_check.txt

If tools are missing, recommend exact pip commands but do not run them without explicit confirmation (e.g., python3 -m pip install black ruff libcst).

⸻

5) Rules & Human Gates (I Require These)
	•	dry_run=true: do not push, create PRs, delete, rename, tag, or otherwise change the live repo. Produce patches only.
	•	Approval gate: After the Full Audit, return an executive summary + ranked top-5 recommendations. Do not create patches until I say “Proceed to patch generation.”
	•	For any destructive recommendation, produce a SIMULATE_SCRIPT that runs only on a disposable branch and prints the changes; do not modify the live tree.
	•	SIMULATE_SCRIPT MUST accept --simulate (default) and --apply; the agent SHALL NEVER run with --apply in dry_run=true.
	•	Mark proposed deletions of model/data with HIGH_RISK and require explicit human approval.

⸻

6) Deliverable for the Audit Start

When starting, create release_artifacts/repo_audit_v2/discovery/audit_start.json with:

{
  "timestamp": "2025-11-05T00:00:00Z",
  "repo": "LukhasAI/Lukhas",
  "connectors": ["LukhasAI/Lukhas", "LUKHAS-MCP"],
  "dry_run": true,
  "strategy": "shim-first",
  "checks_ran": ["list of the exact commands you ran above"],
  "tool_status_file": "release_artifacts/repo_audit_v2/discovery/tool_check.txt",
  "safe_dirs_file": "release_artifacts/repo_audit_v2/discovery/safe_dirs.txt",
  "backup_branch": "backup/pre-flatten-2025-11-05",
  "prior_work": {
    "smoke_tests": "54 passing tests (100% pass rate, 2.3s runtime)",
    "smoke_test_suites": ["identity_auth", "secrets_config", "memory_roundtrip", "guardian_ethics", "api_acl", "routing_negative", "external_deps", "app_lifecycle", "llm_adapter_scan"],
    "artifacts_location": "release_artifacts/repo_audit_v2/",
    "documentation": ["GPT_PRO_AUDIT_INDEX.md", "PHASE_2_COMPLETION.md", "SMOKE_TEST_IMPROVEMENTS_SUMMARY.md"]
  }
}


⸻

Wrap-Up

Once you confirm:
	•	repo root access (or allowed subpath),
	•	acknowledged SAFE directories,
	•	confirmed existing artifact inputs,

begin the Full Audit and produce:
	•	full_audit.md (T4 narrative),
	•	CSV artifacts: redundant_dirs.csv, duplicate_dirs.csv, unused_dirs.csv, import_cycles.csv, flatten_map_refined.csv,
	•	alignment_tips.md,
	•	todo_list_full.md, impact_matrix.csv, and artifact_bundle_full_audit.tar.gz.

Start by returning the confirmation outputs requested above and a one-paragraph executive summary + a ranked top-5 list of recommended next steps. If you lack permissions, reply ACCESS_LIMITED and include failed commands and stderr.

⸻

Ready to proceed? Confirm the 6 items above, then await my approval before generating patches.

