# Jules Agent 5: Syntax & Import Fixing Specialist

## 🎯 Mission: Critical Syntax Error Resolution & Import Cleanup
**Focus**: Fix blocking syntax errors and resolve import dependencies

## 🔴 Priority Queue (Syntax & Import Fixes Only)

### Phase 1: Critical Syntax Errors (Blocking Issues)
1. **tools/scripts/system_status_comprehensive_report.py**
   - TODO[T4-AUTOFIX]: Remaining minor syntax issues
   - Fix malformed f-strings and list comprehensions
   - Resolve missing colons and broken syntax
   - **Status**: Only remaining TODO[T4-AUTOFIX] item

2. **Malformed F-strings**
   - Fix incorrect f-string syntax: `f"text {var` → `f"text {var}"`
   - Resolve nested quote issues in f-strings
   - Convert old-style formatting to f-strings where safe

3. **Missing Colons & Syntax Structure**
   - Fix missing colons in function/class definitions
   - Resolve incorrect indentation causing syntax errors
   - Fix malformed list/dict comprehensions

### Phase 2: Import Resolution (Dependency Issues)
4. **Missing Standard Library Imports**
   - Add missing `import logging`, `from datetime import datetime`
   - Fix `import os`, `import sys`, `import json` where needed
   - Resolve `from pathlib import Path` imports

5. **Third-Party Import Issues**
   - Fix FastAPI imports: `from fastapi import FastAPI, HTTPException`
   - Resolve Pydantic imports: `from pydantic import BaseModel`
   - Add missing OpenAI/Anthropic client imports

6. **Internal Module Import Fixes**
   - Resolve lukhas internal import paths
   - Fix circular import issues with lazy imports
   - Add missing candidate/core imports (safe modules only)

### Phase 3: Advanced Import Cleanup
7. **Dynamic Import Safety**
   - Add try/except blocks for optional imports
   - Create fallback stubs for missing dependencies
   - Use importlib for dynamic module loading

8. **Import Organization**
   - Group imports: standard lib → third party → local
   - Remove duplicate imports
   - Use absolute imports for clarity

## 🛡️ Safety Constraints
- **Branch**: Work on `feat/jules-syntax-fixes`
- **Patch Limit**: ≤20 lines per file per session
- **Critical Only**: Fix blocking syntax errors first
- **Avoid**: `candidate/aka_qualia/` (Wave C development)
- **Validation**: Each fix must pass Python syntax check
- **No Behavior Changes**: Only fix syntax, not logic

## 🔧 Systematic Approach
```bash
# Setup
source .venv/bin/activate

# Find syntax errors
python -m py_compile file.py  # Test individual files
ruff check . --select=E999    # Syntax errors
ruff check . --select=F821    # Undefined name errors

# Import analysis
python -c "import ast; ast.parse(open('file.py').read())"  # Validate syntax
python -m lukhas.module  # Test import success
```

## 📊 Common Fix Patterns
```python
# Before: Malformed f-string
message = f"Processing {data.name for data in items"

# After: Fixed f-string
message = f"Processing {', '.join(data.name for data in items)}"

# Before: Missing import causing NameError
def get_logger():
    return logger.getLogger(__name__)  # NameError: logger not defined

# After: Added import
import logging

def get_logger():
    return logging.getLogger(__name__)

# Before: Circular import issue
from lukhas.core.module import Component  # Creates circular dependency

# After: Lazy import
def get_component():
    from lukhas.core.module import Component
    return Component()
```

## 🧪 Validation Protocol
```bash
# Before fixing each file:
python -m py_compile [file]  # Syntax validation
python -c "import [module]"  # Import validation

# Apply fixes (≤20 lines per file)
# Edit file with syntax corrections

# Validate fix success  
python -m py_compile [file]  # Must pass
python -c "import [module]"  # Must import successfully
ruff check [file] --select=E999  # No syntax errors

# Runtime validation
pytest tests/[related_tests] -v  # Ensure no regressions
```

## 📊 High-Priority Target Files
Based on current status:
1. **tools/scripts/system_status_comprehensive_report.py** (TODO[T4-AUTOFIX])
2. Files with ruff E999 (syntax error) violations
3. Modules failing import due to missing dependencies
4. serve/ modules with import resolution issues
5. lukhas/ modules with internal import problems

## 🔍 Error Detection Commands
```bash
# Find syntax errors
find . -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -v __pycache__

# Find import errors
python -c "
import pkgutil
import importlib
for importer, modname, ispkg in pkgutil.walk_packages(['lukhas', 'serve']):
    try:
        importlib.import_module(modname)
        print(f'✓ {modname}')
    except Exception as e:
        print(f'✗ {modname}: {e}')
"
```

## 📈 Success Metrics
- **Syntax Errors**: Zero Python syntax errors (E999)
- **Import Success**: 95%+ modules import without errors
- **TODO[T4-AUTOFIX]**: Final item resolved
- **Blocking Issues**: All critical syntax problems fixed
- **Quality**: No runtime behavior changes

## 🎯 Expected Outcome
Agent 5 eliminates blocking syntax and import issues, ensuring all modules can be imported and executed without fundamental errors.

---
*Agent 5 Focus: Syntax & imports - Removing blockers for system functionality*