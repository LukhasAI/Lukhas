# Codex PR Comment: T4 Try-Except Codemod

**Use this after creating a PR, comment with @codex**

---

## GitHub PR Comment Template

```
@codex Please execute the T4 Batch2D try-except codemod:

**Task**: Convert try-except ImportError patterns to importlib.util.find_spec guards

**Script to Run**:
```bash
# Generate candidates
./scripts/t4_batch2d_runner.sh

# Apply codemod
./scripts/t4_batch2d_beta_runner.sh --apply
```

**Pattern Conversion**:
```python
# Before
try:
    import optional_module
except ImportError:
    optional_module = None

# After
import importlib.util
if importlib.util.find_spec('optional_module'):
    import optional_module
else:
    optional_module = None
```

**Safety Requirements**:
- ✅ Create backups before modification
- ✅ Verify syntax after transformation
- ✅ Run ruff cleanup
- ✅ All files must compile
- ✅ Review diffs before commit

**Expected Output**:
- Modified files with converted patterns
- Backup files in codemod_backups/
- Commit with T4 message format
- All files compile successfully

**Verification**:
```bash
# After transformation
python3 -m py_compile <modified_files>
pytest tests/
```

Please execute and commit the changes following T4 standards.
```

---

## How to Use This

1. **Create a branch**:
   ```bash
   git checkout -b fix/t4-batch2d-beta-codemod
   git push -u origin fix/t4-batch2d-beta-codemod
   ```

2. **Create a draft PR**:
   ```bash
   gh pr create \
     --title "fix(t4): Batch2D-Beta - Try-except import conversion" \
     --body "Converting try-except patterns to importlib.util.find_spec" \
     --draft
   ```

3. **Comment on the PR** with the template above

4. **Codex will**:
   - Execute the script
   - Review results
   - Commit changes
   - Update PR with results

---

## Alternative: Create PR with Script First

```bash
# Run script to create PR automatically
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
./scripts/t4_batch2d_beta_runner.sh --apply

# Then comment @codex on the created PR for additional review/fixes
```
