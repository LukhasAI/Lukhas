# Quick Import Fix Guide

## How to Fix Import Errors

### Step 1: Identify the Import Error Pattern

When you see:
```
ModuleNotFoundError: No module named 'lukhas.X'
```

### Step 2: Determine Module Location

Use these commands to find the module:

```bash
# Find a specific module file
find /Users/agi_dev/LOCAL-REPOS/Lukhas -name "module_name.py" -type f | grep -v ".venv"

# Find a module directory
find /Users/agi_dev/LOCAL-REPOS/Lukhas -type d -name "module_name" | grep -v ".venv"

# Check if module exists at root
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/module_name

# Check if module exists in candidate
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/module_name
```

### Step 3: Apply the Correct Import Pattern

#### Pattern 1: Root-Level Module
If found at `/Users/agi_dev/LOCAL-REPOS/Lukhas/module_name/`:

```python
# Old (failing)
from lukhas.module_name import Something

# New (working)
from module_name import Something
```

#### Pattern 2: Candidate Module
If found at `/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/module_name/`:

```python
# Old (failing)
from lukhas.module_name import Something

# New (working)
from candidate.module_name import Something
```

#### Pattern 3: Module in lukhas/ Package
If module should be in lukhas/ but is missing:

```python
# Option A: Copy from source
cp /path/to/source/module.py /Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/

# Option B: Create compatibility import in lukhas/
# Edit /Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/module_name.py
from actual.location import *
```

## Common Module Locations

### Bridge Module
```python
# ✅ Correct
from bridge.api_gateway.route_handlers import RouteHandlers
from bridge.trace_logger import BridgeTraceLogger

# ❌ Wrong
from lukhas.bridge.api_gateway.route_handlers import RouteHandlers
```

### Emotion Module
```python
# ✅ Correct (full system in candidate)
from candidate.emotion.examples.basic import example
from candidate.emotion.mood_regulation import MoodRegulator

# ⚠️  Limited (basic root module)
from emotion import basic_function
```

### Governance Module
```python
# ✅ Correct (full system in candidate)
from candidate.governance.ethics.constitutional_ai import ConstitutionalFramework
from candidate.governance.consent.consent_manager import AdvancedConsentManager
from candidate.governance.identity.core.id_service.lambda_id_generator import LambdaIDGenerator

# ⚠️  Limited (basic root module)
from governance.guardian_system import GuardianSystem
from governance.guardian_policies import GuardianPolicies
```

### Consciousness Module
```python
# ✅ Correct (full system in candidate)
from candidate.consciousness.dream.expand.mesh import mesh_consensus
from candidate.consciousness.creativity.emotion import EmotionEngine

# ⚠️  Limited (basic root module)
from consciousness import basic_function
from consciousness.decision_engine import DecisionEngine
```

### Memory Module
```python
# ✅ Correct (lukhas package)
from lukhas.memory.adaptive_memory import AdaptiveMemorySystem
from lukhas.memory.embedding_index import EmbeddingIndex

# ✅ Also correct (root module)
from memory.folds import FoldSystem
from memory.indexer import MemoryIndexer
```

### Core Module
```python
# ✅ Correct (lukhas package)
from lukhas.core.trace import mk_crumb
from lukhas.core.common import BaseConfig

# ✅ Also correct (root compatibility bridge)
from core.trace import mk_crumb

# ❌ Missing (need to find or create)
from lukhas.core.ethics import EthicsEngine
from lukhas.core.orchestration.async_orchestrator import AsyncOrchestrator
```

### API Module
```python
# ✅ Correct (main app)
from lukhas.main import app

# ✅ Correct (bridge API)
from bridge.api.main import app as bridge_app

# ✅ Correct (candidate API)
from candidate.api.app import app as candidate_app
```

## Quick Fix Commands

### Fix Single Test File
```bash
# Open the test file
code /path/to/test_file.py

# Replace import pattern (example)
# Change: from lukhas.consciousness.dream import X
# To: from candidate.consciousness.dream import X
```

### Find and Replace Pattern (Use with caution!)
```bash
# Find all files with a specific import pattern
grep -r "from lukhas\.consciousness" tests/ --include="*.py"

# Replace pattern in multiple files (dry run first)
find tests/ -name "*.py" -exec grep -l "from lukhas\.consciousness" {} \;

# After verifying, use sed to replace (macOS):
find tests/ -name "*.py" -exec sed -i '' 's/from lukhas\.consciousness/from candidate.consciousness/g' {} \;
```

## Module Existence Quick Check

```bash
# Check if module has __init__.py (is a package)
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/module_name/__init__.py

# List module contents
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/module_name/

# Check module in Python
python -c "import module_name; print(module_name.__file__)"
```

## Troubleshooting

### Import Works in Python but Fails in Test
- Check if pytest is using correct Python environment
- Verify PYTHONPATH includes repository root
- Check for circular imports

### Module Exists but Import Fails
- Verify __init__.py exists in all parent directories
- Check for syntax errors in __init__.py
- Look for circular import issues

### "No module named 'core.__all__'"
This is a special error in core/__init__.py compatibility bridge:
```python
# The issue is here in core/__init__.py line 31
globals().update({name: getattr(_lukhas_core, name) for name in getattr(_lukhas_core, "__all__", [])})
```

Solution: Ensure lukhas.core has proper __all__ definition or fix the compatibility bridge.

## Testing Your Fix

```bash
# Test single file import
source .venv/bin/activate
python -c "from module.path import Something; print('Success')"

# Test pytest collection
pytest path/to/test_file.py --collect-only

# Run the actual test
pytest path/to/test_file.py -v
```

## Best Practices

1. **Always check module location before fixing**
2. **Prefer candidate.* imports for development features**
3. **Use root imports for stable, production modules**
4. **Never import from lukhas/ into candidate/ (lane violation)**
5. **Document any new compatibility layers created**
6. **Test the import before committing**

## Batch Fix Script Template

```bash
#!/bin/bash
# Fix imports in test files

# Example: Fix consciousness imports
find tests/ -name "*.py" -type f | while read file; do
    if grep -q "from lukhas\.consciousness\." "$file"; then
        echo "Fixing: $file"
        sed -i '' 's/from lukhas\.consciousness\./from candidate.consciousness./g' "$file"
    fi
done
```

## Status Tracking

After each fix:
1. Note the file path
2. Document the import pattern changed
3. Run pytest collection to verify
4. Update IMPORT_FIX_SUMMARY.md

## Need Help?

1. Check IMPORT_FIX_SUMMARY.md for known patterns
2. Use `grep -r "module_name" /Users/agi_dev/LOCAL-REPOS/Lukhas` to find module
3. Check MODULE_INDEX.md for official module locations (if exists)
4. Ask the team about module ownership
