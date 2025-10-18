# GitHub Copilot Task B: Contract Registry Hardening

**Status**: Ready for Delegation
**Priority**: High
**Estimated Time**: 1-2 hours
**Complexity**: Medium
**Model Recommendation**: Claude 3.5 Sonnet or GPT-4

---

## 🎯 Objective

Harden the contract registry by:
1. Validating all contract references in manifests
2. Fixing broken contract links
3. Ensuring all T1 modules have contracts
4. Creating missing contract stubs

---

## 📋 Task Breakdown

### Task 1: Validate Existing Contract References (20 min)

**Goal**: Find all broken contract links in manifests

**Command**:
```bash
python scripts/validate_contract_refs.py --check-all
```

**Expected Output**:
- List of manifests with broken contract refs
- List of contract files that don't exist
- Statistics on contract coverage by tier

**Sample Output**:
```
✅ Valid contracts: 450
❌ Broken references: 23
⚠️  T1 modules without contracts: 8
```

---

### Task 2: Analyze Broken References (30 min)

**Goal**: Categorize broken references by issue type

**Categories**:
1. **Path Issues**: Contract file moved/renamed
2. **Missing Files**: Contract never created
3. **Invalid Format**: Contract exists but path wrong in manifest

**Process**:
```bash
# Extract all contract references
jq -r '.contracts[]?' manifests/**/module.manifest.json | sort -u > /tmp/contract_refs.txt

# Check which exist
while read contract; do
  if [ ! -f "$contract" ]; then
    echo "MISSING: $contract"
  fi
done < /tmp/contract_refs.txt
```

**Output**: Categorized list of issues

---

### Task 3: Fix Path Issues (30 min)

**Goal**: Update manifest contract paths for moved files

**Common Path Patterns**:
- Old: `lukhas/contracts/...` → New: `contracts/...`
- Old: `candidate/contracts/...` → New: `labs/contracts/...`
- Old: `core/contracts/...` → New: `contracts/...`

**Script Template**:
```python
import json
from pathlib import Path

def fix_contract_path(old_path):
    """Fix common path patterns"""
    # Remove lukhas/ prefix
    new_path = old_path.replace("lukhas/contracts/", "contracts/")
    # Update candidate → labs
    new_path = new_path.replace("candidate/contracts/", "labs/contracts/")
    # Remove core/ prefix
    new_path = new_path.replace("core/contracts/", "contracts/")
    return new_path

# Find all manifests
for manifest_file in Path("manifests").rglob("module.manifest.json"):
    with open(manifest_file) as f:
        data = json.load(f)

    if "contracts" in data:
        updated = False
        new_contracts = []

        for contract in data["contracts"]:
            new_path = fix_contract_path(contract)
            if Path(new_path).exists():
                new_contracts.append(new_path)
                if new_path != contract:
                    print(f"Fixed: {contract} → {new_path}")
                    updated = True
            else:
                new_contracts.append(contract)  # Keep original if fix didn't work

        if updated:
            data["contracts"] = new_contracts
            with open(manifest_file, 'w') as f:
                json.dump(data, f, indent=2)
```

---

### Task 4: Create Missing Contract Stubs (30 min)

**Goal**: Generate contract stubs for T1 modules without contracts

**Contract Stub Template**:
```markdown
# <MODULE_NAME> Contract

**Version**: 1.0.0
**Status**: Draft
**Tier**: T1
**Owner**: triage@lukhas

---

## Purpose

<Brief description of module purpose>

---

## Public Interface

### Functions
- `function_name(args) -> return_type`: Description

### Classes
- `ClassName`: Description

---

## Guarantees

- **Input Validation**: All inputs are validated
- **Error Handling**: All errors are caught and logged
- **Type Safety**: Full type annotations

---

## Dependencies

- List key dependencies

---

## Breaking Changes

None (initial version)

---

## Migration Guide

N/A (initial version)

---

**Last Updated**: <DATE>
**Maintained By**: <OWNER>
```

**Process**:
```bash
# Find T1 modules without contracts
python -c "
import json
from pathlib import Path

for manifest_file in Path('manifests').rglob('module.manifest.json'):
    with open(manifest_file) as f:
        data = json.load(f)

    if data.get('tier') == 'T1' and not data.get('contracts'):
        module_path = manifest_file.parent.relative_to('manifests')
        print(f'T1 without contract: {module_path}')
"
```

For each T1 module without contract:
1. Create contract file in `contracts/<module_path>/CONTRACT.md`
2. Add contract reference to manifest
3. Populate stub with module info

---

### Task 5: Validate All Fixes (10 min)

**Goal**: Ensure all fixes pass validation

**Commands**:
```bash
# Re-run validator
python scripts/validate_contract_refs.py --check-all

# Ensure no broken refs
python scripts/validate_contract_refs.py --strict

# Check T1 coverage
python -c "
import json
from pathlib import Path

t1_total = 0
t1_with_contracts = 0

for manifest_file in Path('manifests').rglob('module.manifest.json'):
    with open(manifest_file) as f:
        data = json.load(f)

    if data.get('tier') == 'T1':
        t1_total += 1
        if data.get('contracts'):
            t1_with_contracts += 1

coverage = (t1_with_contracts / t1_total * 100) if t1_total > 0 else 0
print(f'T1 Contract Coverage: {coverage:.1f}% ({t1_with_contracts}/{t1_total})')
"
```

**Success Criteria**:
- 0 broken contract references
- 100% T1 modules have contracts

---

## 📁 Key Files

- **Validator**: `scripts/validate_contract_refs.py`
- **Manifests**: `manifests/**/module.manifest.json`
- **Contracts**: `contracts/**/CONTRACT.md`
- **Schema**: `schemas/module.manifest.schema.json`

---

## ✅ Acceptance Criteria

1. [ ] All contract references point to existing files
2. [ ] All T1 modules have at least one contract
3. [ ] All fixes validated by `validate_contract_refs.py`
4. [ ] Contract stubs follow template format
5. [ ] Commit message follows T4 standards

---

## 📝 Commit Message Template

```
fix(contracts): harden contract registry and ensure T1 coverage

**Problem**
- <N> manifests had broken contract references
- <M> T1 modules lacked contracts
- Contract paths outdated after directory restructuring

**Solution**
- Fixed <N> broken contract paths (lukhas/ → root, candidate/ → labs/)
- Created <M> contract stubs for T1 modules
- Validated all contract references

**Impact**
- ✅ 0 broken contract references (was <N>)
- ✅ 100% T1 contract coverage (was <X>%)
- ✅ All manifests pass contract validation
- Created contracts: <M>
- Fixed paths: <N>

🤖 Generated with GitHub Copilot

Co-Authored-By: Copilot <noreply@github.com>
```

---

## 🚨 Important Notes

1. **Don't Delete Contracts**: If a contract file exists, don't delete it even if not referenced
2. **Validate Paths**: Ensure all paths are relative from repository root
3. **T1 Priority**: T1 modules MUST have contracts before commit
4. **Stub Quality**: Contract stubs should be complete even if brief
5. **Backup First**: Consider backing up manifests before mass edits

---

## 🤝 Handoff Instructions

When complete:
1. Create report in `docs/audits/contract_hardening_<DATE>.md`
2. Commit with message template above
3. Create summary with:
   - Before/after broken references count
   - T1 contract coverage %
   - List of created contracts
   - Validation output
