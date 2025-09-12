# 🎯 T4 Unused Imports System

**Transform Technical Debt into Documented Intent**

The T4 Unused Imports System is a comprehensive policy enforcer that eliminates unexplained F401 (unused import) violations in production code lanes while maintaining clear documentation of intentional imports kept for future implementation.

## 🎯 Mission

**Zero unexplained F401 violations in production lanes (`lukhas/`, `MATRIZ/`) with full audit trail and developer-friendly workflows.**

## 🏗️ System Architecture

### Core Components

```
T4 Unused Imports System
├── tools/ci/unused_imports.py          # Unified policy enforcer
├── AUDIT/waivers/unused_imports.yaml   # Exemption management
├── reports/todos/unused_imports.jsonl  # Complete audit trail
├── Makefile targets                    # Developer workflows
├── .pre-commit-config.yaml            # Git hook integration
└── .github/workflows/                  # CI/CD enforcement
```

### Production Scope

- **Included**: `lukhas/`, `MATRIZ/` (production code lanes)
- **Excluded**: `candidate/`, `archive/`, `quarantine/`, `.venv/`, `node_modules/`, `reports/`, `.git/`

## 🚀 Quick Start

### Basic Usage

```bash
# 1. Annotate any new F401s in production lanes
python3 tools/ci/unused_imports.py --paths lukhas MATRIZ

# 2. Enforce strict policy (fail if any unannotated F401s remain)
python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --strict

# 3. Preview changes without modifying files
python3 tools/ci/unused_imports.py --dry-run --paths lukhas MATRIZ
```

### Makefile Integration

```bash
# Annotate unused imports
make lint-unused

# Enforce zero unannotated F401s (CI mode)
make lint-unused-strict
```

## 📋 How It Works

### 1. Detection Phase
- Scans specified paths using `ruff --select F401`
- Filters out excluded directories automatically
- Checks against waivers configuration

### 2. Annotation Phase
- Adds inline TODO tags: `# TODO[T4-UNUSED-IMPORT]: <reason>`
- Ensures header block exists in files with annotations
- Logs all actions to audit trail

### 3. Validation Phase
- Strict mode fails if any unannotated F401s remain
- Used in CI/CD to enforce policy compliance

## 🎨 Annotation Examples

### Before (F401 violation)
```python
import os
import sys
from typing import Dict

def main():
    print("Hello world")
```

### After (T4 annotated)
```python
# ---
# TODO[T4-UNUSED-IMPORT]: This file contains intentionally kept unused imports.
# Provide a reason per line or remove when implemented.
# ---
import os  # TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ wiring (document or remove)
import sys  # TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ wiring (document or remove)
from typing import Dict  # TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ wiring (document or remove)

def main():
    print("Hello world")
```

## ⚙️ Configuration

### Command Line Options

```bash
python3 tools/ci/unused_imports.py [OPTIONS]

Options:
  --paths PATHS [PATHS ...]    Roots to scan (default: lukhas MATRIZ)
  --reason REASON             Custom reason for TODO annotations
  --strict                    Exit non-zero if any unannotated F401s remain
  --dry-run                   Preview changes without modifying files
  --help                      Show help message
```

### Custom Reasons

```bash
# Use specific reason for annotations
python3 tools/ci/unused_imports.py --reason "reserved for Trinity Framework expansion"

# Context-aware reasons
python3 tools/ci/unused_imports.py --reason "MATRIZ-R2 integration point"
```

## 🛡️ Waivers System

### Configuration File: `AUDIT/waivers/unused_imports.yaml`

```yaml
waivers:
  # File-level waiver (exempts entire file)
  - file: lukhas/experimental_module.py
    line: 0
    reason: "Experimental module under active development"
  
  # Line-specific waiver
  - file: lukhas/core/framework.py
    line: 42
    reason: "Reserved for Trinity Framework consciousness evolution"
  
  # MATRIZ integration points
  - file: MATRIZ/router.py
    line: 15
    reason: "MATRIZ-R2 activation point - do not remove"
```

### Waiver Types

- **File-level** (`line: 0`): Exempts entire file from T4 processing
- **Line-specific** (`line: N`): Exempts specific import line
- **Reason required**: All waivers must include clear justification

## 🔄 Development Workflow

### 1. Local Development

```bash
# Before committing new code
make lint-unused

# Check if ready for CI
make lint-unused-strict
```

### 2. Pre-commit Integration

The system automatically runs during git workflows:

- **On commit**: Auto-annotates new F401s
- **On push**: Enforces zero unannotated F401s

### 3. CI/CD Integration

GitHub Actions workflow validates:
- T4 system components exist and compile
- Production lanes have zero unannotated F401s
- Waivers configuration is valid YAML

## 📊 Audit Trail

### Log File: `reports/todos/unused_imports.jsonl`

Each annotation creates a JSON log entry:

```json
{
  "file": "lukhas/core/module.py",
  "line": 15,
  "reason": "kept pending MATRIZ wiring (document or remove)",
  "message": "F401 unused import",
  "timestamp": "2025-09-12T06:11:23Z"
}
```

### Viewing Audit Trail

```bash
# Show recent annotations
tail -10 reports/todos/unused_imports.jsonl

# Count total annotations
wc -l reports/todos/unused_imports.jsonl

# Parse with jq for analysis
cat reports/todos/unused_imports.jsonl | jq '.reason' | sort | uniq -c
```

## 🎯 Best Practices

### 1. Annotation Quality

- **Be specific**: Replace generic reasons with implementation plans
- **Time-bound**: Include target dates when possible
- **Review regularly**: Monthly cleanup of obsolete annotations

### 2. Reason Guidelines

```python
# ❌ Generic (poor)
import unused_module  # TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ wiring

# ✅ Specific (good)
import matrix_router  # TODO[T4-UNUSED-IMPORT]: MATRIZ-R2 routing system (Q4 2025)

# ✅ Architectural (excellent)
from consciousness.trinity import Core  # TODO[T4-UNUSED-IMPORT]: Trinity Framework expansion point for consciousness evolution
```

### 3. Maintenance Workflow

```bash
# Monthly review: find annotations older than 30 days
grep -l "TODO\[T4-UNUSED-IMPORT\]" $(find lukhas MATRIZ -name "*.py") | xargs grep -l "$(date -d '30 days ago' '+%Y-%m')"

# Implement or remove outdated annotations
python3 tools/ci/unused_imports.py --dry-run  # Preview current state
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Tool not finding imports

```bash
# Ensure ruff is installed
pip install ruff

# Check if paths exist
ls -la lukhas/ MATRIZ/
```

#### 2. Permission errors

```bash
# Ensure write permissions
chmod +w lukhas/ MATRIZ/

# Check file encoding
file -bi lukhas/problematic_file.py
```

#### 3. YAML syntax errors

```bash
# Validate waivers file
python3 -c "import yaml; yaml.safe_load(open('AUDIT/waivers/unused_imports.yaml'))"
```

### Debug Mode

```bash
# Run with verbose ruff output
python3 -m ruff check --select F401 --output-format=json lukhas MATRIZ

# Check exact file processing
python3 tools/ci/unused_imports.py --dry-run --paths lukhas
```

## 🔗 Integration with LUKHAS AI

### Trinity Framework Compliance

The T4 system aligns with Trinity Framework principles:

- **⚛️ Identity**: Authentic code with documented intent
- **🧠 Consciousness**: Awareness of technical debt transformation
- **🛡️ Guardian**: Policy enforcement and drift prevention

### MATRIZ Integration

Special handling for MATRIZ-related imports:

```python
# Recognized MATRIZ patterns get contextual reasons
from MATRIZ.router import TraceRouter  # TODO[T4-UNUSED-IMPORT]: MATRIZ-R2 trace routing activation
```

## 📈 Metrics and Monitoring

### Key Performance Indicators

- **F401 Elimination Rate**: % of production files without unannotated F401s
- **Annotation Quality**: Review cycle completion rate
- **System Reliability**: CI/CD pass rate for T4 checks

### Monitoring Commands

```bash
# Production lane health check
python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --strict

# Annotation statistics
cat reports/todos/unused_imports.jsonl | jq -r '.file' | sort | uniq -c | sort -nr

# Reason distribution
cat reports/todos/unused_imports.jsonl | jq -r '.reason' | sort | uniq -c | sort -nr
```

## 🎓 Advanced Usage

### Custom Path Scanning

```bash
# Scan specific modules
python3 tools/ci/unused_imports.py --paths lukhas/core lukhas/api

# Single directory deep scan
python3 tools/ci/unused_imports.py --paths consciousness/trinity
```

### Integration with Other Tools

```bash
# Combine with other linting
make lint && make lint-unused-strict

# Chain with security scanning
make security && make lint-unused-strict
```

### Batch Operations

```bash
# Process multiple reasons
for module in core api consciousness; do
  python3 tools/ci/unused_imports.py --paths lukhas/$module --reason "kept for $module expansion"
done
```

## 📚 Related Documentation

- [Makefile User Guide](MAKEFILE_USER_GUIDE.md)
- [Pre-commit Hooks Guide](../ci/PRE_COMMIT_GUIDE.md)
- [Trinity Framework Documentation](../trinity/TRINITY_FRAMEWORK.md)
- [MATRIZ Integration Guide](../matriz/MATRIZ_INTEGRATION.md)

---

**Last Updated**: September 12, 2025  
**Maintainer**: LUKHAS AI Development Team  
**Status**: Production Ready ✅