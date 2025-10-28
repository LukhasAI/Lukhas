# Migration Tools Documentation

**Status**: Production-Ready | **Updated**: 2025-10-28

## Overview

Two production-grade migration tools for systematic repository refactoring:

1. **`rewrite_matriz_imports.py`**: AST-safe import rewriter (matriz → MATRIZ)
2. **`replace_todos_with_issues.py`**: TODO → GitHub issue link replacement

## Tool 1: MATRIZ Import Rewriter

**Path**: `scripts/consolidation/rewrite_matriz_imports.py`

### Features

- **AST-Based Rewriting**: Uses `libcst` for safe import transformation
- **Patch Generation**: Creates git-applyable unified-diff patches
- **Artifacts**:
  - Per-file patches: `artifacts/patches/*.patch`
  - Aggregated patch: `artifacts/matriz_migration.patch`
  - Migration summary: `artifacts/migration-summary.md`
  - Manifest: `artifacts/matriz_manifest.json`
- **Safety-First**:
  - Dry-run mode (default)
  - `--apply` requires `--confirm-apply` flag
  - Creates `.bak` backups
  - `--git-apply` mode with clean working tree verification
- **Lane-Aware**: Defaults to production/test lanes (lukhas, core, serve, tests)
- **Exclusions**: Skips .git, .venv, build, dist, artifacts, third_party

### Requirements

```bash
pip install libcst
```

### Usage Examples

```bash
# Dry run (preview changes, generate patches)
python scripts/consolidation/rewrite_matriz_imports.py --dry-run

# Dry run with verbose output
python scripts/consolidation/rewrite_matriz_imports.py --dry-run --verbose

# Apply changes to specific lane (creates .bak files)
python scripts/consolidation/rewrite_matriz_imports.py --path lukhas --apply --confirm-apply

# Safe git-apply mode (creates branch, applies via git)
python scripts/consolidation/rewrite_matriz_imports.py --git-apply

# Custom paths
python scripts/consolidation/rewrite_matriz_imports.py --path core tests --dry-run
```

### Workflow

1. **Dry-Run**: Generate patches and review
   ```bash
   python scripts/consolidation/rewrite_matriz_imports.py --dry-run
   ```

2. **Review Artifacts**:
   ```bash
   cat artifacts/migration-summary.md
   cat artifacts/matriz_manifest.json
   ls -la artifacts/patches/
   ```

3. **Apply via Git** (Recommended):
   ```bash
   python scripts/consolidation/rewrite_matriz_imports.py --git-apply
   # Creates branch: migration/matriz-YYYYMMDDTHHMMSSZ
   # Applies: git apply --index artifacts/matriz_migration.patch
   ```

4. **Review & Commit**:
   ```bash
   git diff --staged
   git commit -m "fix(imports): migrate matriz → MATRIZ"
   ```

### Output Structure

```
artifacts/
├── patches/
│   ├── lukhas__identity__adapter.py.patch
│   ├── core__symbolic__processor.py.patch
│   └── ... (one per changed file)
├── matriz_migration.patch          # Aggregated patch
├── migration-summary.md             # Human-readable summary
└── matriz_manifest.json             # Machine-readable manifest
```

### Error Handling

- **Syntax Errors**: Skipped with warning
- **Read Errors**: Logged and skipped
- **Parse Errors**: Logged and skipped
- **Git Errors**: Fails noisily with stderr output

---

## Tool 2: TODO → GitHub Issue Replacer

**Path**: `scripts/todo_migration/replace_todos_with_issues.py`

### Features

- **Path Normalization**: Supports absolute/relative paths in mapping
- **Mapping-Driven**: Uses JSON mapping file (path:line → issue)
- **Safety**:
  - Dry-run mode (default)
  - Creates `.bak` backups when `--apply` is used
  - Fails noisily on missing files/lines
- **Indentation Preservation**: Maintains original TODO indentation
- **Auditable**: Creates `artifacts/replace_todos_log.json`

### Mapping Format

**File**: `artifacts/todo_to_issue_map.json`

```json
{
  "core/identity/adapter.py:42": {
    "issue": 123,
    "repo": "LukhasAI/Lukhas",
    "title": "Implement WebAuthn support"
  },
  "lukhas/consciousness/processor.py:156": {
    "issue": 124,
    "repo": "LukhasAI/Lukhas",
    "title": "Add Dream state validation"
  }
}
```

**Keys**: `path:line` (supports relative or absolute paths)  
**Values**: `{"issue": int, "repo": "org/repo", "title": "..."}`

### Usage Examples

```bash
# Dry run (preview replacements)
./scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json \
  --dry-run

# Apply replacements (creates .bak files)
./scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json \
  --apply
```

### Replacement Example

**Before**:
```python
    # TODO: Implement rate limiting
    return process_request(data)
```

**After**:
```python
    # See: https://github.com/LukhasAI/Lukhas/issues/123
    return process_request(data)
```

### Workflow

1. **Generate Mapping**: Use `extract_todos.py` or manual mapping
   ```bash
   # Create mapping file
   cat > artifacts/todo_to_issue_map.json <<EOF
   {
     "core/api.py:15": {"issue": 101, "repo": "LukhasAI/Lukhas", "title": "Add auth"},
     "lukhas/processor.py:42": {"issue": 102, "repo": "LukhasAI/Lukhas", "title": "Optimize"}
   }
   EOF
   ```

2. **Dry-Run Preview**:
   ```bash
   ./scripts/todo_migration/replace_todos_with_issues.py \
     --map artifacts/todo_to_issue_map.json \
     --dry-run
   ```

3. **Apply Replacements**:
   ```bash
   ./scripts/todo_migration/replace_todos_with_issues.py \
     --map artifacts/todo_to_issue_map.json \
     --apply
   ```

4. **Review Log**:
   ```bash
   cat artifacts/replace_todos_log.json
   ```

5. **Commit Changes**:
   ```bash
   git add -A
   git commit -m "docs(todos): replace inline TODOs with GitHub issue links"
   ```

### Error Handling

- **Missing Mapping File**: Exits with error
- **Invalid Mapping Keys**: Skipped with warning
- **Missing Files**: Logged in `replace_todos_log.json`
- **Line Mismatch**: Logged as error

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: MATRIZ Migration Preview

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM UTC
  workflow_dispatch:

jobs:
  matriz-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install libcst
      
      - name: Generate MATRIZ migration patches
        run: |
          python scripts/consolidation/rewrite_matriz_imports.py --dry-run --verbose
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: matriz-migration-patches
          path: |
            artifacts/patches/
            artifacts/matriz_migration.patch
            artifacts/migration-summary.md
            artifacts/matriz_manifest.json
          retention-days: 30
```

---

## Safety Checklist

### Before Running

- [ ] Clean working tree (`git status --porcelain` returns empty)
- [ ] Run dry-run first
- [ ] Review generated patches/artifacts
- [ ] Backup critical files manually (if needed)
- [ ] Install required dependencies (`libcst`)

### After Running

- [ ] Review changes (`git diff`)
- [ ] Run tests (`make smoke && pytest`)
- [ ] Verify imports (`python -c "import MATRIZ; print('OK')"`)
- [ ] Check for syntax errors (`python -m py_compile <file>`)
- [ ] Review backup files (`.bak`)

---

## Troubleshooting

### Import Rewriter

**Issue**: `ModuleNotFoundError: No module named 'libcst'`  
**Fix**: `pip install libcst`

**Issue**: `git apply failed`  
**Fix**: Ensure working tree is clean, check patch format

**Issue**: Syntax errors in generated code  
**Fix**: Report as bug, use `--apply` mode instead of `--git-apply`

### TODO Replacer

**Issue**: `Mapping file not found`  
**Fix**: Create mapping file with correct path

**Issue**: `Warning: mapped file not found`  
**Fix**: Update mapping keys to use repo-relative paths

**Issue**: Indentation mismatch  
**Fix**: Check original TODO line format, ensure proper regex match

---

## Development

### Adding Unit Tests

```bash
# Test import rewriter
pytest tests/unit/scripts/test_rewrite_matriz_imports.py

# Test TODO replacer
pytest tests/unit/scripts/test_replace_todos_with_issues.py
```

### Extending Functionality

**Custom Transformations**: Modify `MatrizRewriter` class in `rewrite_matriz_imports.py`

**Custom Regex**: Update `TODO_REGEX` in `replace_todos_with_issues.py`

**New Artifacts**: Add to `ensure_artifacts()` and update output paths

---

## References

- **libcst Documentation**: https://libcst.readthedocs.io/
- **Git Apply**: https://git-scm.com/docs/git-apply
- **Unified Diff Format**: https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html

---

**Last Updated**: 2025-10-28  
**Maintainer**: LUKHAS Development Team  
**Status**: Production-Ready ✅
