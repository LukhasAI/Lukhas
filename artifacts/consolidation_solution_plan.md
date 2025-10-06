---
status: wip
type: documentation
---
# Consolidation Solution Implementation Plan

## Problem Summary
- **3,216 files** expect `from lukhas.*` imports
- **2,436 Python files** remain in candidate/
- **Core modules** like `matriz_consciousness_integration.py` are missing from root

## Proposed Solution: Smart Merge Strategy

### Phase 1: Analyze & Map (What we need to do)

```bash
# 1. Identify truly unique files in candidate/core
find candidate/core -name "*.py" -type f | while read file; do
    rootfile="${file/candidate\//}"
    if [ ! -f "$rootfile" ]; then
        echo "UNIQUE: $file -> $rootfile"
    fi
done > artifacts/unique_candidate_files.txt

# 2. Count the damage
echo "Unique files to move: $(cat artifacts/unique_candidate_files.txt | wc -l)"
echo "Import statements to fix: 3,216"
```

### Phase 2: Strategic Migration

#### Step 1: Move Critical Missing Files
```bash
# Move the critical matriz_consciousness_integration.py
git mv candidate/core/matriz_consciousness_integration.py core/

# Move other missing core files
for file in bootstrap minimal_actor fault_tolerance integrated_system integration_hub; do
    git mv "candidate/core/${file}.py" "core/${file}.py"
done
```

#### Step 2: Merge candidate/core Subdirectories
```bash
# For each subdirectory in candidate/core
for dir in candidate/core/*/; do
    dirname=$(basename "$dir")
    if [ -d "core/$dirname" ]; then
        # Merge contents
        find "$dir" -name "*.py" -exec git mv {} "core/$dirname/" \;
    else
        # Move entire directory
        git mv "$dir" "core/$dirname"
    fi
done
```

### Phase 3: Fix Imports

#### Option A: Update to Flat Structure (Clean but invasive)
```python
# Script: fix_imports.py
import os
import re

def fix_imports(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace lukhas.X with X
    content = re.sub(r'from lukhas\.([a-z_]+)', r'from \1', content)
    content = re.sub(r'import lukhas\.([a-z_]+)', r'import \1', content)

    with open(filepath, 'w') as f:
        f.write(content)

# Run on all Python files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            fix_imports(os.path.join(root, file))
```

#### Option B: Add PYTHONPATH Shim (Quick but temporary)
```python
# Add to all entry points and test files
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create lukhas symlink
os.symlink('.', 'lukhas', target_is_directory=True)
```

### Phase 4: Validate

```bash
# Test critical imports
python3 -c "
try:
    # Test with current structure
    from core import matriz_consciousness_integration
    print('✅ Direct import works')
except:
    print('❌ Direct import failed')

try:
    # Test if we need lukhas package
    from lukhas.core import matriz_consciousness_integration
    print('✅ Package import works')
except:
    print('❌ Package import failed')
"

# Run key tests
pytest tests/capabilities/test_backpressure_decimation.py -v
pytest tests/candidate/qi/test_qi_entanglement.py -v
```

## Decision Matrix

| Approach | Effort | Risk | Cleanliness | Recommendation |
|----------|--------|------|-------------|----------------|
| Complete flat-root + fix imports | High (3-4 hours) | Medium | Very Clean | ⭐⭐⭐⭐⭐ Best long-term |
| Create lukhas/ package | Medium (1-2 hours) | Low | Adds nesting | ⭐⭐⭐ Safest |
| PYTHONPATH shim | Low (30 min) | Low | Hacky | ⭐⭐ Quick fix |
| Selective migration | Medium (2 hours) | Medium | Partial | ⭐⭐⭐⭐ Pragmatic |

## Recommended Approach: Selective Migration + Import Compatibility

1. **Move only missing critical files** (30 min)
   - matriz_consciousness_integration.py
   - Other files needed by failing tests

2. **Create compatibility layer** (15 min)
   - Add `lukhas` symlink to root
   - This allows both import styles to work

3. **Fix failing tests** (30 min)
   - Update imports in test files only
   - Verify tests pass

4. **Document the structure** (15 min)
   - Create ARCHITECTURE.md explaining the layout
   - Add migration notes for future cleanup

## Immediate Action Items

```bash
# 1. Move the critical missing file
git mv candidate/core/matriz_consciousness_integration.py core/

# 2. Create compatibility symlink
ln -s . lukhas

# 3. Test the fix
python3 -c "from lukhas.core.matriz_consciousness_integration import create_matriz_consciousness_system; print('✅ Import works!')"

# 4. Run the failing test
pytest tests/capabilities/test_backpressure_decimation.py -v
```

## Success Criteria

- [ ] Tests that were failing with import errors now pass
- [ ] Both `from core.X` and `from lukhas.core.X` work
- [ ] No duplicate files between candidate/ and root
- [ ] Clear documentation of the structure

## Risk Mitigation

- **Backup before major changes**: `git stash` or new branch
- **Test incrementally**: Move and test one module at a time
- **Keep candidate/ intact initially**: Don't delete until verified
- **Document decisions**: Update README with structure explanation

---

Status: Ready for Implementation
Estimated Time: 1-2 hours for pragmatic approach
Risk Level: Medium (mitigated by git version control)