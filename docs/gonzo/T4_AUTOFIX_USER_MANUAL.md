# 🎯 T4 AutoFix System - User Manual

**LUKHAS AI Agent Army - T4 Cursor-Aware QuickFix System**
**Deputy Assistant Authority: GitHub Copilot**

## 🚀 Overview

The T4 AutoFix System provides LLM-powered, cursor-aware code fixes with comprehensive safety controls. This system integrates seamlessly with VS Code, providing instant fixes for TODO[T4-AUTOFIX] annotations through keyboard shortcuts and interactive workflows.

## 🎮 Quick Start

### VS Code Integration (Recommended)

**Primary Workflow:**
1. Place cursor on any TODO[T4-AUTOFIX] line
2. Press **⌘⇧Q** to generate LLM patch
3. Review the generated patch in new VS Code tab
4. Press **⌘⇧W** to apply patch with reality checks

**Alternative Shortcuts:**
- **⌘⇧T**: List all TODOs in Problems panel
- **⌘⇧Y**: Open nightly summary report

### Command Line Usage

```bash
# Basic quickfix at cursor position
tools/dev/t4_quickfix.py --cursor-line 42 src/file.py

# Generate and auto-open patch in VS Code
tools/dev/t4_quickfix.py --open src/file.py

# Safe mode with policy validation only
tools/dev/t4_quickfix.py --safe-only src/file.py

# Custom LLM model
T4_LLM_MODEL=codellama tools/dev/t4_quickfix.py src/file.py
```

## 🔧 System Components

### Core Files
- **`.t4autofix.toml`** - Central policy configuration
- **`tools/dev/t4_quickfix.py`** - Interactive LLM-powered fixes
- **`tools/ci/auto_fix_safe.py`** - Safe transformation engine
- **`tools/ci/run_autofix.sh`** - Local automation runner

### Hygiene Components (NEW)
- **`tools/ci/debt_ratchet.py`** - Prevent lint debt regression
- **`tools/ci/owners_from_codeowners.py`** - Map files to owners
- **`tools/ci/needs_golden.py`** - Detect coverage gaps
- **`tools/reports/weekly_hygiene.py`** - Generate trend dashboards

### VS Code Integration
- **`.vscode/tasks.json`** - Task definitions
- **`.vscode/keybindings.json`** - Keyboard shortcuts
- **Command Palette**: "Tasks: Run Task" → T4 operations

### GitHub Actions
- **`.github/workflows/nightly-autofix.yml`** - Scheduled maintenance
- **`.github/workflows/ci-autofix-label.yml`** - PR merge protection
- **`.github/workflows/ci-debt-ratchet.yml`** - Lint debt prevention
- **`.github/workflows/weekly-hygiene.yml`** - Weekly dashboard generation

## ⚙️ Configuration

### Policy Configuration (.t4autofix.toml)

```toml
[scope]
allow_patterns = ["src/**", "lib/**", "tools/**", "core/**"]
deny_patterns = ["**/test*", "**/__pycache__", "**/.*", "archive/**"]

[transformations.safe]
list_comprehensions = true
f_string_conversion = true
unused_imports = true
pathlib_migration = true
type_hints = true

[transformations.experimental]
async_await_optimization = false
complex_refactoring = false

[llm]
model = "deepseek-coder"
timeout_seconds = 30
max_context_lines = 100
fallback_mode = "stub"
```

### Environment Variables

```bash
# Override default LLM model
export T4_LLM_MODEL="codellama"

# Extend timeout for complex fixes
export T4_LLM_TIMEOUT=60

# Enable debug mode
export T4_DEBUG=1
```

## 🛡️ Safety Features

### Policy Validation
- **Allow/Deny Patterns**: Fine-grained file filtering
- **Transformation Rules**: Only safe, reversible changes
- **Single-file Patches**: Prevents multi-file complexity
- **Interface Protection**: Respects protected patterns

### Reality Testing
- **Import Validation**: Ensures imports remain functional
- **Integration Testing**: Runs relevant test suites
- **Golden Test Compliance**: Validates against known good states
- **Auto-revert**: Automatic rollback on test failures

### Staged-file Awareness
- Works with locally staged files
- Preserves existing changes
- Conflict detection and resolution

## 🎯 Workflow Examples

### Interactive Development

```bash
# 1. Find issues
tools/ci/mark_todos.py --scan src/

# 2. Navigate to TODO in VS Code
# Place cursor on TODO[T4-AUTOFIX] line

# 3. Generate fix
# Press ⌘⇧Q

# 4. Review generated patch
# Patch opens automatically in VS Code

# 5. Apply with safety checks
# Press ⌘⇧W or run:
tools/dev/t4_quickfix.py --apply /tmp/t4_patch_*.patch
```

### Automated Maintenance

```bash
# Run comprehensive nightly-style fixes
tools/ci/run_autofix.sh

# Generate TODO analysis report
tools/ci/mark_todos.py --report-only --output reports/todos/

# Safe bulk processing
find src/ -name "*.py" -exec tools/dev/t4_quickfix.py --safe-only {} \;
```

## 🧹 Hygiene System (NEW)

The T4 Hygiene system provides 5 automated quality assurance features that maintain code health over time.

### 1. Debt Ratchet - Prevent Lint Regression

**Purpose**: Block CI if allowlist lint issues increase in touched packages

```bash
# Test locally
python tools/ci/debt_ratchet.py

# Manual package check
python -c "
from tools.ci.debt_ratchet import count_by_pkg, load_allowed
load_allowed()
print('Current lint debt by package')
"
```

**How it works**:
- Compares allowlist lint counts between PR and main branch
- Only fails for packages you actually touched (lukhas/, candidate/, universal_language/)
- Prevents technical debt from growing while allowing fixes

### 2. Ownership Routing - Auto-mention Owners

**Purpose**: Automatically route TODO files to relevant CODEOWNERS in nightly PR bodies

```bash
# Test ownership mapping
python -c "
from tools.ci.owners_from_codeowners import map_files_to_owners
files = ['lukhas/core/test.py', 'tools/ci/script.py']
mapping = map_files_to_owners(files)
for f, owners in mapping.items():
    print(f'{f}: {\" \".join(owners)}')
"
```

**Integration**: Nightly PRs automatically include ownership tables for faster review routing.

### 3. Golden Coverage Nudge - Test Gap Detection

**Purpose**: Tag PRs with `needs-golden` when quickfixes touch uncovered code

```bash
# Check coverage gaps
python tools/ci/needs_golden.py

# Generate mock coverage data for testing
mkdir -p reports/autofix
echo '{"files": {"src/uncovered.py": {"summary": {"percent_covered": 0}}}}' > reports/autofix/coverage.json
```

**Workflow**: Nightly fixes that modify 0% covered files get flagged for test attention.

### 4. LLM Provenance - Patch Traceability

**Purpose**: Add traceable headers to all AI-generated patches

**Features**:
- Model name and version tracking
- Timeout settings documentation
- UTC timestamps for audit trails

**Example header**:
```
# T4-QuickFix provenance: model=deepseek-coder timeout=30s ts=2025-08-26T22:06:53.935191Z
```

### 5. Weekly Hygiene Dashboard - Trend Visualization

**Purpose**: Generate weekly metrics with unicode sparklines

```bash
# Generate dashboard locally
python tools/reports/weekly_hygiene.py
cat reports/autofix/weekly.md
```

**Output example**:
```markdown
# Weekly Hygiene

* TODO count: 15 ▁▂▃▄▅
* Allowlist lint debt: 8 ▂▃▄
* Nightly PRs (7d): 3 ▁▂▃
```

**Schedule**: Runs Mondays at 03:23 UTC, creates PR with dashboard for review.

## 🔍 Troubleshooting

### Common Issues

**LLM Timeout Issues:**
```bash
# Check Ollama status
ollama list | grep deepseek-coder

# Test LLM connectivity
echo "def hello(): pass" | ollama run deepseek-coder

# Use fallback mode
tools/dev/t4_quickfix.py --fallback-only src/file.py
```

**Policy Violations:**
```bash
# Validate configuration
python -c "import tomli; print(tomli.load(open('.t4autofix.toml', 'rb')))"

# Check file against policy
tools/dev/t4_quickfix.py --policy-check src/file.py

# Debug allow/deny patterns
T4_DEBUG=1 tools/dev/t4_quickfix.py src/file.py
```

**VS Code Integration Issues:**
1. Reload VS Code window (⌘R)
2. Check Command Palette for T4 tasks
3. Verify `.vscode/tasks.json` exists
4. Test keyboard shortcuts in Key Bindings editor

**Hygiene System Issues:**

*Debt Ratchet Failures:*
```bash
# Check what's causing ratchet failure
python tools/ci/debt_ratchet.py
cat reports/lints/ruff_pr.json | jq '.[] | select(.code | in({"UP006":1,"F841":1}))'

# View current allowlist rules
python -c "import tomllib; print(tomllib.loads(open('.t4autofix.toml','rb').read())['rules']['auto_fix'])"
```

*Coverage Detection Issues:*
```bash
# Verify coverage data exists
ls -la reports/autofix/coverage.json
python -c "import json; print(json.load(open('reports/autofix/coverage.json'))['files'].keys())"

# Test coverage collection manually
coverage run -m pytest tests/test_imports.py
coverage json -o reports/autofix/coverage.json
```

*Weekly Dashboard Problems:*
```bash
# Debug sparkline generation
python -c "from tools.reports.weekly_hygiene import spark; print([spark(i) for i in range(0,40,5)])"

# Check GitHub API access
gh pr list --label="autofix-nightly" --search="updated:>=-7days" --json number
```

### Error Recovery

**Failed Patches:**
```bash
# Check recent patches
ls -la /tmp/t4_patch_*

# Manual revert if needed
git checkout -- src/file.py

# Clear temporary files
rm -f /tmp/t4_patch_*
```

**System Reset:**
```bash
# Reset T4 configuration
cp .t4autofix.toml.example .t4autofix.toml

# Reload VS Code integration
code --install-extension ms-vscode.vscode-json
```

## 📊 Monitoring & Analytics

### Usage Reports
- **`reports/todos/summary.md`** - TODO analysis and trends
- **`reports/autofix/weekly.md`** - Weekly hygiene dashboard with sparklines
- **`reports/lints/ruff_*.json`** - Lint analysis for debt ratchet
- **`reports/autofix/coverage.json`** - Coverage data for golden detection
- **GitHub Actions logs** - Nightly automation results
- **VS Code Output panel** - Real-time execution logs

### Performance Metrics
- **LLM Response Time**: Target <30 seconds
- **Policy Validation**: Target <100ms
- **Reality Test Suite**: Target <5 seconds
- **End-to-End Workflow**: Target <60 seconds total
- **Debt Ratchet Check**: Target <10 seconds
- **Coverage Analysis**: Target <15 seconds
- **Weekly Dashboard**: Target <5 seconds

## 🎓 Best Practices

### Effective Usage
1. **Start Small**: Use cursor-aware fixes for individual TODOs
2. **Review Patches**: Always review generated patches before applying
3. **Test Incrementally**: Apply fixes in small batches
4. **Monitor Results**: Check reality test outcomes
5. **Policy Tuning**: Adjust `.t4autofix.toml` based on patterns

### Development Integration
- **Pre-commit**: Use T4 fixes before committing
- **PR Reviews**: Include T4 reports in pull requests
- **Team Training**: Share keyboard shortcuts and workflows
- **Policy Consensus**: Team agreement on transformation rules

### Hygiene Best Practices
- **Monitor Dashboards**: Review weekly hygiene reports regularly
- **Debt Awareness**: Address ratchet failures promptly
- **Coverage Gaps**: Prioritize needs-golden labeled PRs
- **Owner Routing**: Use CODEOWNERS for faster reviews
- **Provenance Tracking**: Keep AI-generated patch audit trails

## 🔗 Related Documentation

- **T4_QUICK_REFERENCE.md** - Quick reference card
- **T4-QUICKFIX-SYSTEM-COMPLETE.md** - Implementation details
- **CLAUDE.md** - Agent army coordination
- **`.t4autofix.toml`** - Configuration reference

---

**System Status**: ✅ OPERATIONAL (with Hygiene Enhancements)
**Last Updated**: August 26, 2025 - Added T4 Hygiene System
**Authority**: Deputy Assistant GitHub Copilot, LUKHAS AI Agent Army

*Part of the Constellation Framework (⚛️🧠🛡️) consciousness development system*
