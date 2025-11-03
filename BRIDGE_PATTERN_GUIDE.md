# Bridge Pattern Guide for LUKHAS

## Purpose
This guide prevents duplicate PRs and wasted Codex token budget by documenting the correct bridge pattern and what has already been implemented.

## What Has Been Implemented ✅

### Commit 0706c3685 (Nov 3, 2025)
Created **160 actual bridge module files** across 11 directories using the correct pattern:
- api/ (8 modules)
- bio/ (6 modules)
- bridge/ (6 modules)
- consciousness/ (13 modules)
- core/ (90 modules)
- emotion/ (10 modules)
- governance/ (13 modules)
- memory/ (19 modules)
- orchestration/ (11 modules)
- tests/ (4 modules)
- tools/ (5 modules)

### Latest Enhancements (Nov 3, 2025)
Cherry-picked from PR #922:
- Added `labs.*` to bridge candidate paths
- Enhanced dynamic backend loading in bridge/__init__.py
- Maintained all 160 explicit bridge files

## The Correct Bridge Pattern

### ✅ CORRECT: Explicit Bridge Module Files

For each module that needs bridging, create an actual `.py` file:

```python
# Example: api/admin.py
"""Bridge module for api.admin → labs.api.admin"""
from __future__ import annotations

from labs.api.admin import *  # noqa: F401, F403
```

**Why This Works:**
- Supports `from api import admin` (attribute-style)
- Supports `import api.admin` (submodule-style)
- Python's module system recognizes it as a real module

### ❌ INCORRECT: Only __init__.py Exports

**DO NOT** only add exports to `__init__.py`:

```python
# WRONG: Only in __init__.py
try:
    from labs.api import admin
except ImportError:
    def admin(*args, **kwargs):
        return None
__all__.append("admin")
```

**Why This Fails:**
- Only works for `from api import admin`
- Breaks `import api.admin` with ModuleNotFoundError
- This was the issue in PRs #904, #906-922 (all closed)

## Complementary Patterns (Also Correct)

### Dynamic Backend Loading in __init__.py

For package-level exports, `__init__.py` can dynamically load backends:

```python
# bridge/__init__.py
_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.bridge",
    "labs.bridge",
    "candidate.bridge",
)

_backend = None
for _path in _CANDIDATES:
    try:
        _backend = import_module(_path)
    except Exception:
        continue
    else:
        break

if _backend is not None:
    for _name in _public_names(_backend):
        globals()[_name] = getattr(_backend, _name)
        __all__.append(_name)
```

**Use This For:**
- Package-level symbol exports
- Dynamic backend discovery
- Path manipulation for submodule search

**DO NOT Use As Replacement For:**
- Explicit bridge .py files for each module

## When to Add New Bridge Files

1. **Check if it exists first:**
   ```bash
   ls api/your_module.py  # Does the file exist?
   ```

2. **Use the generator script:**
   ```bash
   python3 scripts/create_bridge_files.py --dry-run --limit 10
   ```

3. **Verify both import styles work:**
   ```bash
   python3 -c "from api import your_module"  # Attribute
   python3 -c "import api.your_module"       # Submodule
   ```

## Lessons Learned (Nov 3, 2025)

### What Went Wrong
- Created 160 bridge files (correct)
- Codex created 18 PRs (#904-922) using incorrect pattern
- We initially closed all PRs without extracting value
- Wasted Codex token budget

### What We Fixed
- Cherry-picked valuable improvements from PR #922
- Added `labs.*` to candidate paths
- Enhanced dynamic loading
- Preserved all explicit bridge files

### Key Insight
**Don't just close PRs - extract value first!**

Even incorrect PRs may contain:
- Improved candidate lists
- Better fallback implementations
- Enhanced error handling
- Useful test cases

## Decision Tree for New PRs

```
New bridge PR arrives
├─ Does it DELETE existing bridge files?
│  └─ YES → Extract improvements, reject deletions
├─ Does it only modify __init__.py?
│  ├─ Is it adding to candidate lists? → MERGE (good)
│  └─ Is it replacing bridge files? → REJECT (bad)
└─ Does it create actual .py files?
   └─ YES → MERGE (correct pattern)
```

## Tools

- **Generator**: `scripts/create_bridge_files.py`
- **Gap Finder**: `scripts/find_bridge_gaps.py`
- **Bridge Utils**: `_bridgeutils.py`

## References

- Original implementation: commit 0706c3685
- Cherry-pick example: commit 1a4eefe8d
- Closed PRs with incorrect pattern: #904, #906-922
- Merged enhancement PR: #905

---

**Last Updated**: November 3, 2025
**Maintainer**: Claude Code + Human oversight
