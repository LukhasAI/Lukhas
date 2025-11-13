# GPT-Pro MATRIZ Flattening Prompt (Dry-Run Mode)

**Artifacts directory:** `release_artifacts/matriz_readiness_v1`

**Config:**
```json
{
  "flatten_strategy": "shim-first",
  "dry_run": true,
  "max_pr_files": 25,
  "required_checks": ["verify-syntax-zero", "pytest-matriz", "ruff"],
  "reviewers": ["@gonzalordm"],
  "author": "Gonzalo Roberto Dominguez Marchan"
}
```

---

## T4 / 0.01% PROMPT — Operate in DRY-RUN Mode

**CRITICAL:** Do not push branches or create PRs. Produce patches, PR bodies, and a plan only.

You are GPT-Pro. Follow the T4 lens: be skeptical, auditable, and precise. Use artifacts in `release_artifacts/matriz_readiness_v1/` as inputs. Produce outputs in the same directory. Record all commands and outputs as files.

---

## Primary Immediate Tasks

### 1) TODO-01: Generate Initial Flatten Map (COMPLETED)

✅ **Status:** `flatten_map.csv` already generated with 49 candidates
✅ **Status:** `flatten_map_summary.json` created

**Key Findings:**
- All 49 candidates are low-risk
- All use "move" strategy (no high-centrality modules detected)
- Top 7 are MATRIZ nodes (critical cognitive components)
- Import counts may be undercounted - manual review recommended

### 2) Run Verification Baseline (COMPLETED)

✅ **Status:** Baseline verification completed
- `verification/compile_log.txt` created (archive/quarantine errors expected)
- Active codebase: syntax-zero (v0.9.1 baseline maintained)

### 3) Produce Dry-Run Patches for Top 5 Candidates

For the **top 5** candidates in `flatten_map.csv`:

**Top 5 Priority List:**
1. `candidate/core/matrix/nodes/memory_node.py` → `MATRIZ/candidate_core_matrix_nodes_memory_node.py`
2. `candidate/core/matrix/nodes/attention_node.py` → `MATRIZ/candidate_core_matrix_nodes_attention_node.py`
3. `candidate/core/matrix/nodes/thought_node.py` → `MATRIZ/candidate_core_matrix_nodes_thought_node.py`
4. `candidate/core/matrix/nodes/risk_node.py` → `MATRIZ/candidate_core_matrix_nodes_risk_node.py`
5. `candidate/core/matrix/nodes/intent_node.py` → `MATRIZ/candidate_core_matrix_nodes_intent_node.py`

**For each candidate, produce:**

#### For "move" strategy files:
1. **Patch file** showing:
   - `git mv` command
   - AST-based import rewrite commands using `scripts/rewrite_imports_libcst.py`
   - Exact mapping JSON for import rewriter
   - Expected diff output
   - Save to: `patches/<n>_move_<subsystem>.patch`

2. **PR template** containing:
   - Full PR body with checklist
   - Verification commands (compile, ruff, pytest)
   - Rollback commands
   - `restoration_audit.csv` row suggestion (with blank SHAs)
   - Save to: `pr_templates/<n>_move_<subsystem>.md`

3. **Verification simulation:**
   - Run `python3 -m compileall` on the new path (simulate on copies if needed)
   - Run `scripts/rewrite_imports_libcst.py --help` to verify tool works
   - Document exact commands in patch file

#### For "shim" strategy files (if any detected during manual review):
1. **Patch file** showing:
   - New file content at `new_path` with implementation
   - Shim content at `old_path` that re-exports public symbols
   - AST-based import adjustments
   - Save to: `patches/<n>_shim_<subsystem>.patch`

2. **PR template** (same format as move strategy)

### 4) Generate Updated todo_list.md

Create concrete commands for applying the top 5 patches:
- One TODO per candidate
- Exact shell commands (idempotent)
- Expected outputs for verification steps
- Rollback commands

### 5) Create verification_summary.json

Summarize:
```json
{
  "verification_baseline": {
    "compile_ok": true,
    "smoke_tests_ok": true,
    "ruff_errors_active_codebase": 0,
    "e741_remaining": "TBD"
  },
  "dry_run_simulation": {
    "patches_produced": 5,
    "estimated_total_review_time_minutes": 120,
    "highest_risk_item": "memory_node (critical MATRIZ component)"
  }
}
```

### 6) Generate flat_preview_branch_list.txt

Suggested branch names for top 5 patches:
```
refactor/flatten-matriz-memory-node-v1
refactor/flatten-matriz-attention-node-v1
refactor/flatten-matriz-thought-node-v1
refactor/flatten-matriz-risk-node-v1
refactor/flatten-matriz-intent-node-v1
```

---

## Constraints and Behavior

- **DRY RUN:** Do not create, push, or merge branches. Produce patches and PR bodies only.
- Use `.venv` if present (mention when used)
- If `black` or `ruff` not found, print exact pip install lines:
  - `python3 -m pip install black ruff libcst`
- For import rewriting, use `scripts/rewrite_imports_libcst.py`
- Always run `python3 -m compileall` on modified/new files
- If relative imports can't be safely rewritten, mark as `manual_review` in `flatten_map.csv`
- Estimate `estimated_risk` and `estimated_review_time_minutes` per candidate

---

## Output Expectations (Exact Files to Create)

- ✅ `flatten_map.csv` (already created, 49 candidates)
- ✅ `flatten_map_summary.json` (already created)
- ⏳ `patches/01_move_matriz_memory_node.patch`
- ⏳ `patches/02_move_matriz_attention_node.patch`
- ⏳ `patches/03_move_matriz_thought_node.patch`
- ⏳ `patches/04_move_matriz_risk_node.patch`
- ⏳ `patches/05_move_matriz_intent_node.patch`
- ⏳ `pr_templates/01_move_matriz_memory_node.md`
- ⏳ `pr_templates/02_move_matriz_attention_node.md`
- ⏳ `pr_templates/03_move_matriz_thought_node.md`
- ⏳ `pr_templates/04_move_matriz_risk_node.md`
- ⏳ `pr_templates/05_move_matriz_intent_node.md`
- ⏳ `todo_list_updated.md` (with top 5 concrete commands)
- ⏳ `verification/verification_summary.json`
- ⏳ `flat_preview_branch_list.txt`
- ⏳ `artifact_bundle_todo01.tar.gz`

---

## Final Instruction

Work stepwise, document each command run (stdout/stderr), include exact command lines in artifacts. For any ambiguity, choose the safer option (shim-first) and document reasoning.

**Start with producing the 5 patches for the top 5 MATRIZ nodes. Report back when dry-run artifacts are produced.**

End with a brief 5-line executive note summarizing:
1. Risk assessment
2. Next steps
3. Which PRs to open first when switching to `dry_run=false`
4. Any manual review items flagged
5. Estimated timeline for implementation

---

## Rollback Capability

**Backup branch:** `backup/pre-flatten-2025-11-03-1316`

**Rollback command:**
```bash
git reset --hard backup/pre-flatten-2025-11-03-1316
git push -f origin main
```

---

## Notes for Human Review

⚠️ **IMPORTANT:** All 49 candidates show `import_count=0` in discovery, which suggests the import analysis may be incomplete. Before proceeding with actual moves:

1. Manually inspect top 5 files for import dependencies
2. Run targeted import analysis: `rg "from candidate.core.matrix.nodes" --type py`
3. Consider whether shim-first is safer for MATRIZ nodes (critical components)
4. Review verification logs for any hidden dependencies

The discovery heuristic may have missed dynamic imports, conditional imports, or imports in test files. Conservative approach: treat all MATRIZ nodes as high-centrality and use shim strategy.
