---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# 🎯 T4 Unused Imports System - User Guide

**⚛️ LUKHAS AI Constellation Framework - Transforming Technical Debt into Documented Intent**

The T4 Unused Imports System is a sophisticated code quality management framework that converts F401 "unused import" errors into explicitly documented intent, maintaining clean production lanes while preserving future development flexibility.

## 🧠 Philosophy: Technical Debt → Value

Instead of blindly removing unused imports (losing context and intent), T4 transforms them into **documented technical assets**:

- **F401 Errors** → **Annotated TODOs** with contextual reasoning
- **Technical Debt** → **Implementation Roadmap** 
- **Code Cleanup** → **Intent Preservation**

## 🏗️ System Architecture

### Production Lane Focus
T4 operates on **production lanes only**, excluding experimental code:

**✅ Production Lanes (Enforced)**
- `lukhas/` - Core LUKHAS modules
- `core/` - Shared symbolic logic
- `api/` - FastAPI backends
- `consciousness/` - Consciousness systems
- `memory/` - Memory and persistence
- `identity/` - Identity management
- `MATRIZ/` - MATRIZ subsystems

**⚪ Experimental Lanes (Excluded)**
- `candidate/` - Experimental development
- `archive/` - Legacy code storage
- `quarantine/` - Broken or deprecated code

### Constellation Framework Integration
T4 aligns with the LUKHAS AI Constellation Framework:

- **⚛️ Identity**: Maintains module identity while documenting purpose
- **🧠 Consciousness**: Preserves developer intent and future planning  
- **🛡️ Guardian**: Protects against accidental deletion of future-needed imports

## 🛠️ Core Components

### 1. T4 Annotator (`tools/ci/mark_unused_imports_todo.py`)

**Purpose**: Converts unused imports into annotated TODOs with smart contextual reasoning.

**Usage**:
```bash
# Annotate all production lanes (default)
python3 tools/ci/mark_unused_imports_todo.py

# Annotate specific paths
python3 tools/ci/mark_unused_imports_todo.py --paths lukhas core

# Custom reason override
python3 tools/ci/mark_unused_imports_todo.py --reason "kept for Q4 API expansion"
```

**Smart Contextual Reasoning**:
- **MATRIZ imports** → "kept for MATRIZ-R2 trace integration"
- **Agent/orchestration** → "kept for multi-AI agent coordination"
- **Consciousness/Trinity** → "kept for Constellation Framework consciousness evolution"
- **API modules** → "kept for API expansion (document or implement)"
- **Core infrastructure** → "kept for core infrastructure (review and implement)"
- **Bio/quantum** → "kept for bio-inspired/quantum systems development"

### 2. T4 Validator (`tools/ci/check_unused_imports_todo.py`)

**Purpose**: Enforces zero unannotated F401 errors in production lanes.

**Usage**:
```bash
# Validate all production lanes
python3 tools/ci/check_unused_imports_todo.py

# CI/CD integration (fails on violations)
make todo-unused-check
```

**Policy Enforcement**:
- ✅ **Annotated imports**: `# TODO[T4-UNUSED-IMPORT]: reason` - ALLOWED
- ✅ **Waived imports**: Listed in `AUDIT/waivers/unused_imports.yaml` - ALLOWED
- ❌ **Unannotated F401**: No annotation or waiver - **BLOCKED**

### 3. Waivers System (`AUDIT/waivers/unused_imports.yaml`)

**Purpose**: Configuration for intentional unused import exemptions.

**Structure**:
```yaml
# T4 Unused Imports Waivers Configuration
waivers:
  - file: "lukhas/experimental_api.py"
    line: 15
    reason: "Import reserved for MATRIZ-R2 integration"
    expires: "2025-12-31"
    
  - file: "consciousness/trinity_core.py" 
    line: 0  # 0 = entire file waived
    reason: "Constellation Framework development imports"
    reviewer: "consciousness-architect"
```

**Management**:
```bash
# Validate waivers configuration
python3 -c "import yaml; yaml.safe_load(open('AUDIT/waivers/unused_imports.yaml'))"

# Apply waivers (automatic during T4 operations)
# Manual editing of AUDIT/waivers/unused_imports.yaml
```

## 🚀 Developer Workflows

### Daily Development

#### 1. **Before Committing**
```bash
# Check for new F401 violations
make todo-unused-check

# If violations found, annotate them
make todo-unused

# Verify clean state
make todo-unused-check
```

#### 2. **Code Review Process**
```bash
# Reviewer: Check T4 annotations quality
grep -r "TODO\[T4-UNUSED-IMPORT\]" lukhas/ core/ api/

# Validate annotation reasons are specific and actionable
# Update generic reasons with implementation plans
```

#### 3. **Implementation Planning**
```bash
# Monthly: Review and implement annotated imports
grep -r "TODO\[T4-UNUSED-IMPORT\]" . | awk -F: '{print $1}' | sort | uniq

# Update TODO reasons with specific implementation dates
# Remove annotations when imports are actually used
```

### CI/CD Integration

#### Pre-commit Hooks
T4 is integrated into pre-commit hooks for automatic validation:

```bash
# Install pre-commit hooks (includes T4)
pre-commit install

# Manual T4 annotation trigger
pre-commit run t4-unused-imports-annotate --hook-stage manual -a

# Automatic validation on commit
# (T4 validation runs automatically)
```

#### GitHub Actions
T4 validation runs in CI pipeline:

```yaml
# Automatic on push/PR to production lanes
- name: T4 Unused Imports Policy Check
  run: python3 tools/ci/check_unused_imports_todo.py

# Manual annotation workflow dispatch
# Manual comprehensive reporting
```

## 📊 Monitoring & Reporting

### Audit Trail
All T4 operations are logged to `reports/todos/unused_imports.jsonl`:

```json
{
  "timestamp": "2025-09-12T15:30:00Z",
  "file": "lukhas/consciousness/core.py", 
  "line": 25,
  "reason": "kept for Constellation Framework consciousness evolution",
  "message": "'numpy' imported but unused",
  "tool": "T4-unused-imports-annotator"
}
```

### Metrics Tracking
```bash
# Count current annotations
wc -l reports/todos/unused_imports.jsonl

# View recent activity
tail -10 reports/todos/unused_imports.jsonl | jq -r '"\(.file):\(.line) - \(.reason)"'

# Breakdown by reason category
cat reports/todos/unused_imports.jsonl | jq -r '.reason' | sort | uniq -c | sort -nr
```

### Make Targets
```bash
# Production operations
make todo-unused          # Annotate all production lanes
make todo-unused-core     # Annotate lukhas/ only  
make todo-unused-check    # Validate zero violations

# Legacy aliases
make t4-annotate         # Alias for todo-unused
make t4-check           # Alias for todo-unused-check
```

## 🔧 Configuration & Customization

### Ruff Integration
T4 leverages ruff configuration in `pyproject.toml`:

```toml
[tool.ruff.lint]
select = [
    "F401",  # unused imports (T4 system)
    # ... other rules
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow in package init files
"candidate/*" = ["F401"]  # Exclude experimental code
"archive/*" = ["F401"]    # Exclude legacy code
"quarantine/*" = ["F401"] # Exclude broken code
```

### Path Configuration
Default production lanes can be customized:

```python
# In tools/ci/mark_unused_imports_todo.py
default_paths = ["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"]

# Override via command line
python3 tools/ci/mark_unused_imports_todo.py --paths custom_module other_module
```

## 🧪 Testing & Validation

### System Health Check
```bash
# Validate T4 system components
python3 -m py_compile tools/ci/mark_unused_imports_todo.py
python3 -m py_compile tools/ci/check_unused_imports_todo.py
python3 -c "import yaml; yaml.safe_load(open('AUDIT/waivers/unused_imports.yaml'))"

# Test T4 operation (dry run)
python3 tools/ci/mark_unused_imports_todo.py --paths lukhas
```

### Integration Testing
```bash
# Full T4 workflow test
make todo-unused          # Should annotate any new F401s
make todo-unused-check    # Should pass with clean status
git status                # Should show any new annotations
```

## 📋 Best Practices

### Annotation Quality
- **Be Specific**: Replace generic reasons with specific implementation plans
- **Set Timelines**: Include target implementation dates/milestones  
- **Review Regularly**: Monthly review of annotated imports
- **Document Context**: Explain why the import will be needed

**Good Examples**:
```python
from future_module import beta_feature  # TODO[T4-UNUSED-IMPORT]: reserved for Q4 2025 MATRIZ-R3 integration
import experimental_lib  # TODO[T4-UNUSED-IMPORT]: implementing bio-inspired algorithms by Dec 2025
```

**Poor Examples**:
```python
import unused_module  # TODO[T4-UNUSED-IMPORT]: kept for future use
from some_lib import thing  # TODO[T4-UNUSED-IMPORT]: might need later
```

### Waivers Management
- **Temporary Only**: Use waivers for short-term exceptions
- **Document Expiry**: Set expiration dates for waiver review
- **Specific Scope**: Line-level waivers preferred over file-level
- **Regular Cleanup**: Monthly waiver review and cleanup

### Implementation Workflow
1. **Annotate** new unused imports with T4 system
2. **Review** annotations for quality and specificity  
3. **Plan** implementation timelines and milestones
4. **Implement** or remove imports when purpose is fulfilled
5. **Monitor** via audit trail and metrics

## 🆘 Troubleshooting

### Common Issues

#### "T4 validator failing in CI"
```bash
# Check for unannotated F401s in production lanes
ruff check --select F401 lukhas core api consciousness memory identity MATRIZ

# Annotate violations
python3 tools/ci/mark_unused_imports_todo.py

# Verify fix
python3 tools/ci/check_unused_imports_todo.py
```

#### "Waivers not being applied"
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('AUDIT/waivers/unused_imports.yaml'))"

# Check file paths are correct (relative to repo root)
# Check line numbers match ruff output
```

#### "T4 annotations not being added"
```bash
# Check if import is already annotated
grep -n "TODO\[T4-UNUSED-IMPORT\]" file.py

# Check if file is in excluded directory
# Verify ruff detects the F401 error
ruff check --select F401 file.py
```

### Debug Mode
```bash
# Verbose T4 annotation output
python3 tools/ci/mark_unused_imports_todo.py --paths lukhas --reason "debug annotation"

# Check ruff output directly
ruff check --select F401 --output-format json lukhas/
```

## 🔄 Maintenance & Evolution

### Regular Tasks
- **Weekly**: Review new T4 annotations for quality
- **Monthly**: Implement or remove annotated imports  
- **Quarterly**: Clean up waivers and expired annotations
- **Annually**: Review T4 system configuration and policies

### System Updates
- **Ruff Updates**: Test T4 compatibility with new ruff versions
- **Path Changes**: Update default paths as project structure evolves
- **Policy Evolution**: Refine annotation reasons and categories

### Metrics & Reporting
- **Track**: Total annotations, annotation categories, implementation rate
- **Report**: Monthly T4 system health and cleanup progress  
- **Optimize**: Refine smart reasoning based on annotation patterns

---

## 🎯 T4 Success Metrics

- **Zero F401 Violations**: Production lanes maintain clean F401 status
- **Documented Intent**: All unused imports have explicit purpose documentation
- **Implementation Progress**: Regular conversion of TODOs to actual usage
- **Developer Adoption**: Team actively using T4 workflow patterns
- **System Health**: T4 components remain operational and up-to-date

**The T4 system transforms code quality from reactive cleanup to proactive intent management, maintaining the balance between clean code and future flexibility.**

---

*Generated by LUKHAS AI Constellation Framework - T4 Unused Imports System*
*Last Updated: September 12, 2025*