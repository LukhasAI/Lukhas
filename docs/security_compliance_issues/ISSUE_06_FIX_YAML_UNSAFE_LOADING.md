# Security Issue 6: Fix YAML Unsafe Loading (HIGH)

## Priority: P1 - HIGH Security Pattern
## Estimated Effort: 2 days
## Target: Replace all 3 yaml.unsafe_load() calls

---

## 🎯 Objective

Replace all 3 `yaml.unsafe_load()` calls with `yaml.safe_load()` to prevent arbitrary code execution during YAML parsing.

## 📊 Current State

- **yaml.unsafe_load() occurrences**: 3
- **Risk Level**: HIGH
- **Security Impact**: Remote code execution via malicious YAML

## 🔍 Background

`yaml.unsafe_load()` is dangerous because:
- Can execute arbitrary Python code via `!!python/object/apply`
- Allows instantiation of arbitrary Python objects
- No validation of YAML content
- Commonly exploited in configuration files

## 📋 Deliverables

### 1. Standard Fix

**Replace unsafe_load with safe_load**:
```python
# ❌ BEFORE (HIGH RISK - Code Execution)
import yaml

with open('config.yaml') as f:
    config = yaml.unsafe_load(f)  # DANGEROUS!

# ✅ AFTER (SAFE)
import yaml
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """Safely load YAML configuration."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)  # Only loads basic types
    return config
```

### 2. Handle Custom Types (if needed)

**If you need custom types**:
```python
# ✅ Use SafeLoader with custom constructors
import yaml

class SafeConfig:
    """Safe YAML loader with approved custom types."""
    
    @staticmethod
    def custom_constructor(loader, node):
        """Safely construct custom type."""
        # Only allow specific, validated custom types
        value = loader.construct_scalar(node)
        # Validate and return
        return validated_custom_type(value)
    
    @staticmethod
    def load(yaml_string: str) -> Any:
        """Load YAML with custom types safely."""
        yaml.add_constructor('!custom', SafeConfig.custom_constructor,
                           Loader=yaml.SafeLoader)
        return yaml.safe_load(yaml_string)
```

### 3. Validate All YAML Files

Check existing YAML files for dangerous constructs:
```python
import yaml

def scan_yaml_for_dangerous_tags(file_path: str) -> List[str]:
    """Scan YAML file for potentially dangerous tags."""
    dangerous_tags = [
        '!!python/object',
        '!!python/object/apply',
        '!!python/object/new',
    ]
    
    with open(file_path) as f:
        content = f.read()
        found = [tag for tag in dangerous_tags if tag in content]
        if found:
            print(f"WARNING: {file_path} contains: {found}")
        return found
```

### 4. Security Testing
```python
def test_yaml_code_execution_prevented():
    """Ensure YAML code execution attempts fail."""
    malicious_yaml = """
    !!python/object/apply:os.system
    args: ['rm -rf /']
    """
    
    # safe_load should raise error or ignore dangerous tags
    with pytest.raises((yaml.YAMLError, AttributeError)):
        yaml.safe_load(malicious_yaml)
```

### 5. Migration Checklist

For each yaml.unsafe_load():
- [ ] Identify the file location
- [ ] Check if custom Python objects are used
- [ ] If no: simply replace with safe_load
- [ ] If yes: implement SafeLoader with validators
- [ ] Test configuration loading
- [ ] Scan all YAML files for dangerous tags

### 6. Documentation
- [ ] Create `docs/security/YAML_LOADING_FIX_REPORT.md`
- [ ] Update YAML configuration guidelines

## ✅ Acceptance Criteria

- [ ] All 3 yaml.unsafe_load() replaced with yaml.safe_load()
- [ ] Custom types use SafeLoader with validation
- [ ] All YAML files scanned for dangerous tags
- [ ] Security tests pass
- [ ] Configuration loading still works
- [ ] Complete documentation

## 🏷️ Labels: `security`, `high`, `p1`, `yaml-injection`

---

**Estimated Days**: 2 days | **Phase**: Security Phase 1
