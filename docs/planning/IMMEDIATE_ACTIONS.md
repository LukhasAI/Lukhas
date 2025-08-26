# 🚀 Immediate Action Items - GitHub Copilot Tasks
*High-priority fixes that can be automated or scripted*

## 🔧 Critical Fixes (Week 1)

### 1. Import Path Analysis & Fixes
**Priority**: 🔴 CRITICAL
**Estimated Time**: 2-3 hours
**Tools Needed**: `grep_search`, `file_search`, `replace_string_in_file`

#### Issues to Fix:
- [ ] `governance.identity` import namespace mismatches
- [ ] `IdentityClient` broken imports in consciousness module
- [ ] `VoiceProcessor` missing imports
- [ ] `PersonaManager` failed imports

#### Search Commands:
```bash
# Find all broken identity imports
grep -r "from identity\." governance/
grep -r "import identity\." governance/

# Find all failed imports in consciousness
grep -r "ImportError\|ModuleNotFoundError" core/consciousness/

# Find all TODO/FIXME related to imports
grep -r "TODO.*import\|FIXME.*import" .
```

#### Action Steps:
1. Scan all import statements
2. Identify namespace mismatches
3. Fix path references
4. Create missing bridge files if needed
5. Test imports with `python -c "import module"`

---

### 2. Duplicate Code Cleanup
**Priority**: 🔴 CRITICAL
**Estimated Time**: 1-2 hours

#### Target Files:
- [ ] `core/communication/model_communication_engine.py` (9 duplicate classes)
- [ ] Multiple `cognitive_adapter` files
- [ ] Overlapping identity logic

#### Action Steps:
1. Identify duplicate class definitions
2. Consolidate into single canonical version
3. Remove or rename conflicting definitions
4. Update all references

---

### 3. Security Hardening
**Priority**: 🔴 CRITICAL
**Estimated Time**: 1 hour

#### Checklist:
- [ ] Remove hardcoded API keys
- [ ] Set up environment variable loading
- [ ] Audit log content for sensitive data
- [ ] Add input validation to API endpoints
- [ ] Implement rate limiting

#### Files to Check:
```
config/
api/
*.py files containing "api_key", "secret", "token"
```

---

### 4. Empty Directory Cleanup
**Priority**: 🟡 HIGH
**Estimated Time**: 30 minutes

#### Directories to Remove/Consolidate:
- [ ] `core/agent_modeling/` (empty)
- [ ] `core/emotion_engine/` (empty)
- [ ] `core/external_interfaces/` (empty)
- [ ] `core/ethics/` (empty subfolder)

#### Commands:
```bash
# Find empty directories
find . -type d -empty

# Find directories with only __init__.py
find . -type d -exec sh -c 'ls -la "$1" | grep -v "^total" | wc -l' _ {} \; | grep " 3$"
```

---

### 5. Configuration Consolidation
**Priority**: 🟡 HIGH
**Estimated Time**: 1 hour

#### Issues:
- [ ] `core/config/lukhas_settings.py` is just a string pointer
- [ ] Multiple config systems
- [ ] Inconsistent configuration loading

#### Action Steps:
1. Consolidate all config into `config/` directory
2. Create unified configuration loader
3. Remove redundant config files
4. Update all config references

---

## 🛠️ File Structure Improvements (Week 1-2)

### 6. Namespace Organization
**Priority**: 🟡 HIGH
**Estimated Time**: 2-3 hours

#### Current Issues:
- Split identity modules (`governance.identity` vs `core.identity`)
- Inconsistent module hierarchies
- Missing `__init__.py` files

#### Action Plan:
1. Map current namespace structure
2. Identify logical groupings
3. Move files to consistent hierarchy
4. Update all import statements
5. Add proper `__init__.py` files

---

### 7. Dead Code Removal
**Priority**: 🟢 MEDIUM
**Estimated Time**: 1-2 hours

#### Target Categories:
- [ ] `.py` files that are actually documentation
- [ ] Experimental features marked as inactive
- [ ] Old setup/installation scripts
- [ ] Commented-out code blocks

#### Files to Review:
- `core/communication/personality_communication_engine.py` (pseudocode)
- Quantum-related metaphorical code
- Colony/swarm code not in main loop
- Dream authentication stubs

---

## 🧪 Testing & Validation (Week 2)

### 8. Import Testing Script
**Priority**: 🟡 HIGH
**Estimated Time**: 1 hour

Create automated script to test all imports:

```python
#!/usr/bin/env python3
"""Test all module imports in LUKHAS"""

import importlib
import sys
from pathlib import Path

def test_imports():
    """Test all Python modules can be imported"""
    errors = []

    # Find all .py files
    for py_file in Path('.').rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        # Convert path to module name
        module_name = str(py_file).replace('/', '.').replace('.py', '')

        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            errors.append((module_name, str(e)))
            print(f"❌ {module_name}: {e}")

    return errors

if __name__ == "__main__":
    errors = test_imports()
    if errors:
        print(f"\n🚨 {len(errors)} import errors found!")
        sys.exit(1)
    else:
        print("\n🎉 All imports successful!")
```

---

### 9. Configuration Validation
**Priority**: 🟡 HIGH
**Estimated Time**: 30 minutes

#### Validation Checklist:
- [ ] All required environment variables documented
- [ ] Configuration files have valid syntax
- [ ] Default values provided for optional settings
- [ ] No sensitive data in config files

---

## 📋 Documentation Updates (Week 2)

### 10. README Consolidation
**Priority**: 🟡 HIGH
**Estimated Time**: 1 hour

#### Current State:
- Multiple README files with overlapping content
- Legacy information mixed with current
- Missing quick start guide

#### Action Items:
- [ ] Merge all README content
- [ ] Remove outdated information
- [ ] Add clear quick start section
- [ ] Update architecture overview
- [ ] Document current vs experimental features

---

### 11. API Documentation
**Priority**: 🟢 MEDIUM
**Estimated Time**: 2 hours

#### Auto-generate Documentation:
```bash
# Install documentation tools
pip install sphinx autodoc

# Generate API docs
sphinx-apidoc -o docs/ .
```

#### Manual Documentation:
- [ ] Core module interfaces
- [ ] Signal system API
- [ ] Configuration options
- [ ] Deployment guide

---

## 🎯 Automation Scripts

### Quick Fix Script
```bash
#!/bin/bash
# quick_fixes.sh - Automated cleanup script

echo "🚀 Starting LUKHAS quick fixes..."

# 1. Remove empty directories
echo "📁 Removing empty directories..."
find . -type d -empty -delete

# 2. Fix common import issues
echo "🔗 Fixing import statements..."
# Add specific sed/awk commands for known fixes

# 3. Remove hardcoded secrets (placeholder detection)
echo "🔒 Checking for hardcoded secrets..."
grep -r "api_key\s*=\s*['\"]" . || echo "No hardcoded API keys found"

# 4. Validate Python syntax
echo "🐍 Checking Python syntax..."
find . -name "*.py" -exec python -m py_compile {} \;

echo "✅ Quick fixes complete!"
```

---

## 📊 Progress Tracking

### Completion Checklist:
- [ ] All import errors resolved
- [ ] Duplicate classes consolidated
- [ ] Security scan passed
- [ ] Empty directories cleaned
- [ ] Configuration unified
- [ ] Documentation updated
- [ ] Test suite passing

### Success Criteria:
1. **Zero import errors** when running test script
2. **Clean security scan** with no hardcoded secrets
3. **Unified configuration** system working
4. **Updated documentation** reflecting current state
5. **All tests passing** without errors

---

*These tasks prepare the foundation for Claude Code to implement the advanced features like Signal Bus and Colony architecture.*
