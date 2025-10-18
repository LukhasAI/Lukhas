# GitHub Copilot Task C: CI/CD Integration for Flat Structure

**Status**: Ready for Delegation
**Priority**: High
**Estimated Time**: 2-3 hours
**Complexity**: High
**Model Recommendation**: GPT-4 or Claude 3.5 Sonnet (strong CI/CD experience)

---

## 🎯 Objective

Update CI/CD workflows for Phase 5B flat directory structure:
1. Update all GitHub Actions workflow paths
2. Add manifest validation to CI pipeline
3. Integrate star promotion checks
4. Add T1 enforcement rules
5. Optimize workflow performance

---

## 📋 Task Breakdown

### Task 1: Audit Current Workflows (30 min)

**Goal**: Identify all workflows needing updates

**Files to Review**:
```bash
ls -la .github/workflows/

# Expected workflows:
# - ci.yml (main CI pipeline)
# - tests.yml (test suite)
# - lint.yml (linting)
# - security.yml (security scans)
# - deploy.yml (deployment)
```

**Check for**:
- Hardcoded `lukhas/` paths
- Old `candidate/` references
- Missing manifest validation
- Missing contract checks

---

### Task 2: Update Path References (45 min)

**Goal**: Replace old paths with flat structure paths

**Path Migrations**:
```yaml
# OLD PATH PATTERNS → NEW PATTERNS

# Python package imports
lukhas/consciousness/**  →  consciousness/**
lukhas/identity/**       →  identity/**
lukhas/api/**            →  api/**

# Test paths
tests/unit/lukhas/**     →  tests/unit/**
candidate/tests/**       →  labs/tests/**

# Manifest paths
lukhas/**/module.manifest.json  →  manifests/**/module.manifest.json

# Config paths
lukhas/configs/**        →  configs/**
```

**Workflow Update Template**:
```yaml
# Example: ci.yml before
jobs:
  test:
    steps:
      - name: Run tests
        run: pytest tests/unit/lukhas/

# Example: ci.yml after
jobs:
  test:
    steps:
      - name: Run tests
        run: pytest tests/unit/
```

**Files to Update**:
- `.github/workflows/ci.yml`
- `.github/workflows/tests.yml`
- `.github/workflows/lint.yml`
- `.github/workflows/security.yml`

---

### Task 3: Add Manifest Validation Job (30 min)

**Goal**: Fail CI if manifests are invalid or have broken links

**New Workflow Job**:
```yaml
# Add to .github/workflows/ci.yml

  validate-manifests:
    name: Validate Module Manifests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Validate manifest schema
        run: |
          python scripts/validate_module_manifests.py --strict

      - name: Check contract references
        run: |
          python scripts/validate_contract_refs.py --check-all --fail-on-error

      - name: Verify T1 contracts
        run: |
          python scripts/validate_contract_refs.py --enforce-t1-contracts

      - name: Check orphan modules
        run: |
          python scripts/validate_module_manifests.py --check-orphans --max-orphans 5
```

---

### Task 4: Add Star Promotion Checks (30 min)

**Goal**: Prevent unauthorized star promotions

**New Workflow Job**:
```yaml
# Add to .github/workflows/ci.yml

  check-star-promotions:
    name: Check Star Promotions
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for diff

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Detect star promotions
        run: |
          python scripts/detect_star_promotions.py \
            --base origin/main \
            --head HEAD \
            --fail-on-unapproved

      - name: Verify promotion approvals
        run: |
          # Check for approval comments or OWNERS approval
          python scripts/check_promotion_approvals.py
```

**Create Helper Script** (`scripts/detect_star_promotions.py`):
```python
#!/usr/bin/env python3
"""Detect star promotions between commits."""

import json
import sys
from pathlib import Path
from subprocess import check_output

def get_manifest_stars(commit):
    """Get all star assignments at a commit."""
    try:
        output = check_output(
            ["git", "show", f"{commit}:manifests/"],
            text=True
        )
    except:
        return {}

    stars = {}
    for manifest_file in Path("manifests").rglob("module.manifest.json"):
        try:
            content = check_output(
                ["git", "show", f"{commit}:{manifest_file}"],
                text=True
            )
            data = json.loads(content)
            module = str(manifest_file.parent.relative_to("manifests"))
            stars[module] = data.get("constellation_star", "Supporting")
        except:
            continue

    return stars

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--fail-on-unapproved", action="store_true")
    args = parser.parse_args()

    base_stars = get_manifest_stars(args.base)
    head_stars = get_manifest_stars(args.head)

    promotions = []
    star_rank = {"Supporting": 0, "Flow": 1, "Trail": 2, "Anchor": 3,
                 "Watch": 4, "Horizon": 5, "Oracle": 6, "Living": 7, "Drift": 8}

    for module, head_star in head_stars.items():
        base_star = base_stars.get(module, "Supporting")
        if star_rank.get(head_star, 0) > star_rank.get(base_star, 0):
            promotions.append(f"{module}: {base_star} → {head_star}")

    if promotions:
        print(f"🔍 Detected {len(promotions)} star promotions:")
        for p in promotions:
            print(f"  - {p}")

        if args.fail_on_unapproved:
            print("\n❌ Star promotions require approval")
            sys.exit(1)
    else:
        print("✅ No star promotions detected")

if __name__ == "__main__":
    main()
```

---

### Task 5: Add T1 Enforcement (20 min)

**Goal**: Fail CI if T1 modules lack OWNERS or contracts

**New Workflow Step**:
```yaml
      - name: Enforce T1 requirements
        run: |
          python -c "
import json
from pathlib import Path

errors = []

for manifest_file in Path('manifests').rglob('module.manifest.json'):
    with open(manifest_file) as f:
        data = json.load(f)

    if data.get('tier') == 'T1':
        module = str(manifest_file.parent.relative_to('manifests'))

        # Check OWNERS.toml
        owners_file = manifest_file.parent / 'OWNERS.toml'
        if not owners_file.exists():
            errors.append(f'{module}: Missing OWNERS.toml')

        # Check contracts
        if not data.get('contracts'):
            errors.append(f'{module}: Missing contracts')

if errors:
    print('❌ T1 Enforcement Failures:')
    for e in errors:
        print(f'  - {e}')
    exit(1)
else:
    print('✅ All T1 modules comply with requirements')
"
```

---

### Task 6: Optimize Workflow Performance (30 min)

**Goal**: Speed up CI runs

**Optimizations**:

1. **Cache Dependencies**:
```yaml
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

2. **Parallel Jobs**:
```yaml
jobs:
  lint:
    # ...
  test:
    # ...
  validate:
    # Run in parallel
    # ...
```

3. **Conditional Runs**:
```yaml
      - name: Run tests
        if: contains(github.event.head_commit.message, '[skip-tests]') == false
```

---

## 📁 Key Files

- **Workflows**: `.github/workflows/*.yml`
- **Scripts**: `scripts/validate_module_manifests.py`, `scripts/validate_contract_refs.py`
- **New Scripts**: `scripts/detect_star_promotions.py`, `scripts/check_promotion_approvals.py`

---

## ✅ Acceptance Criteria

1. [ ] All workflow paths updated for flat structure
2. [ ] Manifest validation runs on every PR
3. [ ] Star promotion detection works
4. [ ] T1 enforcement prevents non-compliant merges
5. [ ] CI runs pass on current main branch
6. [ ] Workflow runtime reduced by ≥20%

---

## 📝 Commit Message Template

```
ci(workflows): integrate manifest validation and flat structure support

**Problem**
- CI workflows referenced old lukhas/ directory structure
- No manifest validation in CI pipeline
- Star promotions went undetected
- T1 modules could merge without OWNERS/contracts

**Solution**
- Updated all workflow paths for Phase 5B flat structure
- Added manifest validation job (schema + contracts)
- Added star promotion detection with approval checks
- Added T1 enforcement (OWNERS.toml + contracts required)
- Optimized CI with caching and parallel jobs

**Impact**
- ✅ CI validates flat structure paths
- ✅ Broken manifests blocked at PR time
- ✅ Star promotions require approval
- ✅ T1 compliance enforced automatically
- ⚡ CI runtime reduced by ~X%

Updated workflows:
- ci.yml: Added validation jobs, updated paths
- tests.yml: Updated test paths
- lint.yml: Updated source paths
- security.yml: Updated scan paths

New scripts:
- scripts/detect_star_promotions.py
- scripts/check_promotion_approvals.py

🤖 Generated with GitHub Copilot

Co-Authored-By: Copilot <noreply@github.com>
```

---

## 🚨 Important Notes

1. **Test Locally First**: Run `act` or test workflows before pushing
2. **Backwards Compatibility**: Ensure workflows work on existing PRs
3. **Fail Fast**: Validation jobs should fail early to save CI time
4. **Clear Errors**: Validation failures should show exactly what's wrong
5. **Don't Break Main**: Test on a branch first

---

## 🤝 Handoff Instructions

When complete:
1. Test workflows locally with `act` (GitHub Actions local runner)
2. Create test PR to verify all jobs pass
3. Document any breaking changes
4. Create summary with:
   - Before/after CI runtime
   - List of updated workflows
   - New validation checks added
   - Test results
