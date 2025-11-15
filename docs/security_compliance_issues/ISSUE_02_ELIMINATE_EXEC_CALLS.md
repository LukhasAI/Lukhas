# Security Issue 2: Eliminate All exec() Calls (CRITICAL)

## Priority: P0 - CRITICAL Security Pattern
## Estimated Effort: 10 days
## Target: Eliminate all 28 exec() occurrences

---

## 🎯 Objective

Eliminate all 28 `exec()` calls to prevent arbitrary code execution vulnerabilities. Like eval(), exec() poses a CRITICAL security risk as it can execute arbitrary Python code from strings.

## 📊 Current State

- **Total exec() occurrences**: 28
- **Risk Level**: CRITICAL
- **Security Impact**: Code injection, remote code execution
- **Data Source**: `reports/analysis/high_risk_patterns.json` → `.patterns.exec_usage.occurrences`

## 🔍 Background

The `exec()` function executes Python statements dynamically, which is dangerous when:
- Processing untrusted input
- Loading plugins or extensions
- Generating code dynamically
- Running configuration scripts

## 📋 Deliverables

### 1. Complete Inventory
```bash
jq '.patterns.exec_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > exec_locations.json
```

### 2. Remediation Strategies

**For Plugin Systems** (recommended):
```python
# ❌ BEFORE (CRITICAL RISK)
exec(dynamic_code)

# ✅ AFTER (SAFE - Plugin System)
import importlib.util
from pathlib import Path
from typing import Any, Optional

def load_plugin_safely(plugin_path: Path, plugin_name: str) -> Optional[Any]:
    """Load plugin from controlled directory only."""
    # Validate plugin is in allowed directory
    allowed_dir = Path("/path/to/plugins").resolve()
    if not plugin_path.resolve().is_relative_to(allowed_dir):
        raise ValueError(f"Plugin must be in {allowed_dir}")
    
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
```

**For Dynamic Class Creation**:
```python
# ❌ BEFORE
exec(class_definition_string)

# ✅ AFTER - Use metaclasses or factory functions
def create_class(name: str, bases: tuple, attrs: dict):
    """Safe dynamic class creation."""
    return type(name, bases, attrs)
```

**For Code Generation**:
```python
# ❌ BEFORE
exec(generated_code)

# ✅ AFTER - Use Jinja2 templates
from jinja2 import Template

template = Template(code_template)
generated_code = template.render(**context)
# Save to file and import normally
```

**For Test/Demo Code**:
```python
# Remove entirely or use controlled fixtures
```

### 3. Security Testing
- [ ] Unit tests for all replacements
- [ ] Path traversal prevention tests
- [ ] Module import validation tests

### 4. Documentation
- [ ] Create `docs/security/EXEC_ELIMINATION_REPORT.md`
- [ ] Plugin system documentation
- [ ] Safe code generation guidelines

## ✅ Acceptance Criteria

- [ ] All 28 exec() calls eliminated or secured
- [ ] Whitelist-based plugin system if needed
- [ ] Security audit of all dynamic code paths
- [ ] Zero exec() in production code
- [ ] Complete documentation

## 🏷️ Labels: `security`, `critical`, `p0`, `code-injection`

---

**Estimated Days**: 10 days | **Phase**: Security Phase 1
