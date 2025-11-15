# Claude Code Web Prompt: T4 Try-Except Codemod

**Copy this entire prompt to paste into Claude Code web interface**

---

## Task: Execute T4 Batch2D Try-Except Import Conversion

**Repository**: `/Users/agi_dev/LOCAL-REPOS/Lukhas`

### Objective
Run the existing T4 Batch2D codemod to convert `try/except ImportError` patterns to `importlib.util.find_spec()` guards across the codebase.

### Context
We have a production-ready script that:
- Uses LibCST for safe AST transformations
- Creates backups before modification
- Verifies syntax after changes
- Runs cleanup (ruff, autoflake)
- Creates draft PR automatically

### Files to Execute

**Main Script**: `scripts/t4_batch2d_beta_runner.sh`

**Supporting Files**:
- `tools/ci/codemods/convert_try_except_imports.py` (LibCST codemod)
- `scripts/t4_batch2d_runner.sh` (generates candidate list)

### Pattern Being Converted

**Before**:
```python
try:
    import optional_module
except ImportError:
    optional_module = None
```

**After**:
```python
import importlib.util
if importlib.util.find_spec('optional_module'):
    import optional_module
else:
    optional_module = None
```

### Execution Steps

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Step 1: Generate candidate file list (if not exists)
./scripts/t4_batch2d_runner.sh

# Step 2: Run codemod in dry-run mode
./scripts/t4_batch2d_beta_runner.sh

# Step 3: Review results
cat /tmp/t4_batch2d_beta_codemod_results.json

# Step 4: If dry-run looks good, apply changes
./scripts/t4_batch2d_beta_runner.sh --apply
```

### What the Script Does Automatically

1. ✅ Backs up all files to `codemod_backups/`
2. ✅ Runs LibCST transformation
3. ✅ Verifies Python syntax
4. ✅ Runs ruff cleanup (F401 removal)
5. ✅ Creates git commit with T4 message format
6. ✅ Pushes to remote
7. ✅ Creates draft PR with detailed description

### Safety Checks Built-In

- Backups created before any modification
- Syntax verification (rolls back on error)
- Only processes files with try-except in import region (first 120 lines)
- Conservative transformation (simple patterns only)
- Draft PR for manual review before merge

### Expected Output

**Commit Message** (auto-generated):
```
fix(t4): Batch2D-Beta - Convert try-except imports to importlib.util.find_spec

Applied LibCST codemod to convert optional import patterns:
- try/except ImportError → if importlib.util.find_spec()
- Conservative transformation: only simple patterns in import region
- Files modified: N

Safety verification:
✅ All files compile successfully
✅ Ruff cleanup applied
✅ Backups created in codemod_backups/

Part of: Batch 2D systematic cleanup (try-except pattern conversions)
Strategy: Conservative AST transformation with manual review
```

**PR Title**: `fix(t4): Batch2D-Beta - Convert try-except imports (N files)`

### Verification Steps

After script completes:
1. Check all files compile: `python3 -m py_compile <files>`
2. Run tests on modified files: `pytest tests/`
3. Verify imports work: Test both with and without optional dependencies
4. Review PR diff in GitHub

### LUKHAS Conventions

- Follow T4 commit message standards
- Use academic tone (no hype words)
- Include Problem/Solution/Impact format
- Create draft PR for review
- Comprehensive safety checks

### If Issues Occur

**Syntax Errors**: Script auto-rolls back from backups
**Import Errors**: Check if transformation preserved semantics
**Test Failures**: Review transformed files, may need manual fixes

### Post-Completion

1. Review draft PR
2. Run full test suite
3. Merge if all checks pass
4. Update T4 tracking docs

---

**EXECUTE**: Run the commands above in the terminal and monitor progress.
