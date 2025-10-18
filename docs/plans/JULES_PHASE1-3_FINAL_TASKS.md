---
title: Jules - Phase 1-3 Final Tasks Brief
date: 2025-10-18
status: ready-for-jules
priority: medium
branch: feat/phase1-3-completion
assigned: Jules Agent
parent_brief: PHASE1-3_REMAINING_TASKS_BRIEF.md
---

# Jules Agent - Phase 1-3 Final Tasks

## Mission Brief for Jules

Complete the remaining 2 tasks from Phase 1-3 to achieve 100% completion before moving to Phase 5.

## Current Status

**Branch**: `feat/phase1-3-completion` (already exists)
**Progress**: 4/6 tasks complete (66.7%)
**Completed by parallel agent**:
- ✅ Task 1.3: Artifact Audit (8 new manifests)
- ✅ Task 1.2: Schema Enhancement (80+ properties documented)
- ✅ Task 2.1: OpenAPI Specifications (5 APIs, 35 endpoints)
- ✅ Task 2.2: Contract Validator Enhancement

**Your tasks** (remaining 2):
- ⏳ Task 1.1: Context File Enhancements (42 files)
- ⏳ Task 3.1: Script Documentation (10+ scripts)

## Task 1.1: Context File Enhancements

**Priority**: Medium
**Time Estimate**: 4-6 hours
**Files**: 42 context markdown files

### Objective
Standardize all context markdown files with YAML front matter, cross-links, and contract references.

### Find Files
```bash
# All context files in the repository
find docs/lukhas_context -name "*.md" -type f 2>/dev/null
find . -name "lukhas_context.md" -type f 2>/dev/null
find . -name "claude.me" -type f 2>/dev/null
```

### For Each Context File

#### 1. Add YAML Front Matter (if missing)

Check if file starts with `---`. If not, add:

```yaml
---
domain: [consciousness|memory|governance|bio|dream|identity|vision|ethics]
stars: [Flow|Trail|Anchor|Watch|Horizon|Oracle|Living|Drift]
tier: [T1|T2|T3|T4]
contracts: [list contract IDs if applicable]
updated: 2025-10-18
status: active
---
```

**How to determine values**:
- `domain`: Look at directory path (e.g., `consciousness/` → domain: consciousness)
- `stars`: Check corresponding manifest's constellation.stars field
- `tier`: Check corresponding manifest's module.tier field
- `contracts`: Check manifest's contracts array

**Example**:
```yaml
---
domain: consciousness
stars: [Flow, Anchor, Oracle]
tier: T1
contracts: [CON-001-CONSCIOUSNESS, CON-002-REFLECTION]
updated: 2025-10-18
status: active
---
```

#### 2. Add Contract Links Section (if module has contracts)

After the front matter and main title, add:

```markdown
## 📜 Contracts

This module implements the following contracts:
- [CON-001-CONSCIOUSNESS](../../contracts/CON-001-CONSCIOUSNESS.md) - Core consciousness processing contract
- [CON-002-REFLECTION](../../contracts/CON-002-REFLECTION.md) - Reflective introspection interface
```

**How to find contracts**:
```bash
# Check the module's manifest
cat manifests/consciousness/core/module.manifest.json | jq -r '.contracts[]'
```

If no contracts, skip this section.

#### 3. Add Cross-References Section

Add a section linking to related modules:

```markdown
## 🔗 Related Modules

- [Memory System](../memory/lukhas_context.md) - Persistent state storage
- [Guardian](../governance/guardian/lukhas_context.md) - Ethical oversight
- [Dream Engine](../consciousness/dream/lukhas_context.md) - Creative synthesis
```

**How to identify related modules**:
- Check manifest `dependencies` array
- Look at imports in module's code
- Use common sense (consciousness relates to memory, ethics, dream, etc.)

#### 4. Add/Update Constellation Alignment (if not present)

```markdown
## ⭐ Constellation Stars

This module aligns with:

### Flow (Consciousness) ⚛️
Implements core consciousness processing, enabling reflective awareness and cognitive stream management.

### Anchor (Watch) 🛡️
Provides stability through ethical guardrails and constitutional AI patterns.

### Oracle (Horizon) 🔮
Enables future-state prediction and strategic decision-making capabilities.
```

**How to write explanations**:
- Read the module's README or docstrings
- Check manifest's `description` field
- Explain HOW the module contributes to each star

### Validation Commands

After updating files:

```bash
# Check all context files have front matter
for f in $(find . -name "lukhas_context.md" -o -name "claude.me"); do
  head -1 "$f" | grep -q "^---$" || echo "❌ Missing front matter: $f"
done

# Check front matter is valid YAML
for f in $(find . -name "lukhas_context.md" -o -name "claude.me"); do
  python3 - <<PY
import yaml
content = open("$f").read()
if content.startswith("---"):
    front_matter = content.split("---")[1]
    try:
        yaml.safe_load(front_matter)
        print("✅ $f")
    except:
        print("❌ Invalid YAML: $f")
PY
done

# Check for broken markdown links
for f in $(find . -name "lukhas_context.md" -o -name "claude.me"); do
  grep -o '\[.*\](.*)' "$f" | grep -v "^http" | while read link; do
    path=$(echo "$link" | sed 's/.*(\(.*\)).*/\1/')
    dir=$(dirname "$f")
    if [ ! -f "$dir/$path" ]; then
      echo "❌ Broken link in $f: $path"
    fi
  done
done
```

### Success Criteria
- ✅ All 42 context files have YAML front matter
- ✅ Front matter is valid YAML (parseable)
- ✅ Contract links present where applicable (check manifests)
- ✅ Cross-references to 2+ related modules per file
- ✅ Constellation alignment explanations present
- ✅ No broken links in documentation

### Commit Message
```
docs(context): enhance 42 context files with YAML front matter and cross-links

**Problem**
- Context files lacked standardized metadata
- No contract references or cross-module links
- Difficult to discover related modules
- Inconsistent documentation format

**Solution**
- Added YAML front matter to 42 context files
  - domain, stars, tier, contracts fields
  - All manifests cross-referenced
- Linked contract references (N files with contracts)
- Added cross-references between related modules
- Included constellation star alignments with explanations

**Impact**
- ✅ Standardized context file format
- ✅ Improved module discoverability
- ✅ Clear contract→implementation mapping
- ✅ Better navigation between related systems

Files updated: 42
Contracts linked: N
Cross-references added: N+

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Task 3.1: Script Documentation

**Priority**: Low
**Time Estimate**: 2-3 hours
**Files**: 10+ Python scripts in `scripts/`

### Objective
Add comprehensive docstrings and --help output to all CLI scripts.

### Priority Scripts (do these first)

1. `scripts/generate_module_manifests.py` - Main manifest generator
2. `scripts/validate_contract_refs.py` - Contract validator (already enhanced!)
3. `scripts/validate_module_manifests.py` - Manifest validator
4. `scripts/sync_t12_manifest_owners.py` - Owner sync tool
5. `scripts/dependency_scanner.py` - Dependency analysis
6. `scripts/normalize_imports.py` - Import normalization
7. `scripts/context_coverage_bot.py` - Context coverage checker (if exists)
8. `scripts/migrate_context_front_matter.py` - Front matter migration (if exists)

### For Each Script

#### 1. Add Module-Level Docstring

At the top of the file (after shebang and imports):

```python
#!/usr/bin/env python3
"""
Generate module manifests for LUKHAS components.

This script scans the repository for Python modules and generates
standardized manifest files containing metadata, dependencies, contracts,
and constellation star assignments.

Usage:
    python3 scripts/generate_module_manifests.py --all
    python3 scripts/generate_module_manifests.py --module-path core/memory
    python3 scripts/generate_module_manifests.py --star-from-rules --write-context

Examples:
    # Generate all manifests with star promotion
    python3 scripts/generate_module_manifests.py --all --star-from-rules

    # Regenerate single module
    python3 scripts/generate_module_manifests.py --module-path consciousness/core

    # Validate only (no writes)
    python3 scripts/generate_module_manifests.py --all --validate-only

Exit Codes:
    0: Success
    1: Validation errors found
    2: File I/O errors

See Also:
    - configs/schemas/module_manifest.schema.json - Manifest schema
    - docs/dashboards/CONSTELLATION_STATS.md - Star statistics
    - PHASE1-3_REMAINING_TASKS_BRIEF.md - Task context
"""

import sys
import argparse
# ... rest of imports
```

#### 2. Add Function Docstrings

For every function:

```python
def generate_manifest(module_path: str, star_from_rules: bool = False) -> dict:
    """
    Generate a manifest dictionary for the given module.

    Args:
        module_path: Relative path to module from repo root (e.g., 'core/memory')
        star_from_rules: If True, assign stars based on configs/star_rules.json

    Returns:
        Dictionary containing manifest data conforming to module_manifest.schema.json

    Raises:
        FileNotFoundError: If module_path doesn't exist
        ValidationError: If generated manifest doesn't pass schema validation

    Example:
        >>> manifest = generate_manifest('consciousness/core', star_from_rules=True)
        >>> manifest['module']['name']
        'Consciousness Core'
    """
    # ... implementation
```

**Format**:
- First line: One-sentence summary (ends with period)
- Blank line
- Args: List all parameters with descriptions
- Returns: Describe return value and type
- Raises: List exceptions that can be raised
- Example: Show realistic usage (optional but helpful)

#### 3. Enhance Argument Help Text

For argparse arguments:

```python
parser.add_argument(
    '--star-from-rules',
    action='store_true',
    help='Assign constellation stars based on configs/star_rules.json (requires confidence >= 0.70)'
)

parser.add_argument(
    '--module-path',
    type=str,
    metavar='PATH',
    help='Path to specific module (relative to repo root, e.g., "consciousness/core")'
)

parser.add_argument(
    '--write-context',
    action='store_true',
    help='Update lukhas_context.md files with generated manifest data'
)

parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Enable verbose output (shows progress for each module)'
)
```

**Make help text**:
- Explain what the flag does
- Give an example if helpful
- Mention defaults if applicable
- Use metavar for positional args

### Validation Commands

```bash
# Check all scripts have --help
for script in scripts/*.py; do
  python3 "$script" --help 2>&1 | grep -q "usage:" && echo "✅ $script" || echo "❌ $script"
done

# Check docstring coverage with pydocstyle (if installed)
pydocstyle scripts/*.py --count

# Or use this Python check
python3 - <<PY
import ast
from pathlib import Path

missing_module = []
missing_funcs = []

for script in Path("scripts").glob("*.py"):
    tree = ast.parse(script.read_text())

    # Check module docstring
    if not ast.get_docstring(tree):
        missing_module.append(script.name)

    # Check function docstrings
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not ast.get_docstring(node) and not node.name.startswith('_'):
                missing_funcs.append(f"{script.name}::{node.name}")

print(f"Scripts missing module docstrings: {len(missing_module)}")
for m in missing_module:
    print(f"  - {m}")

print(f"\nFunctions missing docstrings: {len(missing_funcs)}")
for f in missing_funcs[:10]:
    print(f"  - {f}")
PY
```

### Success Criteria
- ✅ All scripts have module-level docstrings (at least 8 priority scripts)
- ✅ All public functions have docstrings with Args/Returns
- ✅ All argparse arguments have help text
- ✅ `--help` output is comprehensive and shows usage examples
- ✅ No pydocstyle errors (if tool available)

### Commit Message
```
docs(scripts): add comprehensive docstrings to CLI tools

**Problem**
- Scripts lacked module-level documentation
- Function purposes unclear
- --help output missing or minimal
- No usage examples

**Solution**
- Added module docstrings to 10+ scripts
  - Usage examples
  - Exit codes
  - See Also references
- Documented all public functions
  - Args, Returns, Raises sections
  - Usage examples where helpful
- Enhanced argparse help text
  - Examples and defaults
  - Clear descriptions

**Impact**
- ✅ Self-documenting scripts
- ✅ Helpful --help output
- ✅ Clear usage examples
- ✅ Better developer experience

Scripts documented: 10+
Functions documented: N+
Help text enhanced: All argparse arguments

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Final Deliverables

When both tasks complete:

1. **Enhanced Context Files** (Task 1.1):
   - [ ] 42 context files with YAML front matter
   - [ ] Contract links where applicable
   - [ ] Cross-references between related modules
   - [ ] Constellation alignment explanations
   - [ ] No broken links

2. **Documented Scripts** (Task 3.1):
   - [ ] Module docstrings for 10+ scripts
   - [ ] Function docstrings for all public functions
   - [ ] Enhanced --help output
   - [ ] Usage examples included

3. **Final Commit & Merge**:
   - [ ] All changes committed (2 commits minimum)
   - [ ] Branch pushed to remote
   - [ ] Ready for PR or merge to main

## Getting Started

```bash
# 1. Checkout the existing branch
git checkout feat/phase1-3-completion
git pull origin feat/phase1-3-completion

# 2. Check current status
git log --oneline -5

# 3. Start with Task 1.1 (context files) - highest value
# Find all context files
find . -name "lukhas_context.md" -o -name "claude.me" | head -10

# 4. Then Task 3.1 (script docs)
ls scripts/*.py

# 5. Commit after each task
git add -A
git commit -m "[use template above]"

# 6. Push when done
git push origin feat/phase1-3-completion
```

## Time Budget

**Total**: 6-9 hours

- Task 1.1: Context files (4-6h)
  - 42 files × 5-8 min each = 3.5-5.5h
  - Testing & validation = 0.5-1h

- Task 3.1: Script docs (2-3h)
  - 10 scripts × 10-15 min each = 1.5-2.5h
  - Testing & validation = 0.5h

## Questions/Issues?

If you encounter:

1. **Missing contract files**: Some manifests reference contracts that don't exist - just skip linking those
2. **Duplicate context files**: Some modules have both `claude.me` and `lukhas_context.md` - update both for consistency
3. **Scripts without argparse**: Some scripts may not have CLI - add module docstring only
4. **Circular cross-references**: If A links to B and B links to A, that's fine

## Success Signals

You'll know you're done when:

- ✅ All validation commands pass
- ✅ No broken links in context files
- ✅ Every script shows helpful --help output
- ✅ All commits follow T4 standard
- ✅ Branch ready for merge

## After Completion

When both tasks done:
1. Push branch: `git push origin feat/phase1-3-completion`
2. Report completion in main conversation
3. Phase 1-3 will be 100% complete (6/6 tasks ✅)
4. Ready to move to Phase 5!

---

Good luck, Jules! These final tasks will complete the Phase 1-3 foundation. 🚀

**Parent Brief**: See `PHASE1-3_REMAINING_TASKS_BRIEF.md` for full context
**Branch**: `feat/phase1-3-completion` (already exists with 4/6 tasks done)
**Estimated Time**: 6-9 hours
