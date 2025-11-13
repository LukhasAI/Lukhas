# 🎯 T4 Annotation Action Guide for Matriz Team

**How to Act on T4 Annotations - Practical Workflow**

## 📋 Overview

T4 annotations document **intentional decisions** and **planned work**. They serve as:
- 🗺️ **Navigation markers** for code quality
- 📝 **Technical debt tracking** with context
- 🎯 **Prioritized work queues** for refactoring
- 🛡️ **Protection** against false-positive linting errors

## 🔍 Understanding Annotation Status

### ✅ Accepted (271 violations - 59%)
**Meaning:** These are **intentional patterns** that violate lint rules for good architectural reasons.

**Action:** **NO ACTION NEEDED** - Keep as-is, annotations justify the pattern.

**Examples:**
```python
# B018: __all__ validation for dynamic module loading
try:
    __all__  # TODO[T4-ISSUE]: {"status":"accepted","reason":"Module export validation..."}
except NameError:
    __all__ = []

# B008: FastAPI dependency injection (required pattern)
async def get_user(
    db: Session = Depends(get_db)  # TODO[T4-ISSUE]: {"status":"accepted","reason":"FastAPI Depends()..."}
):
    ...

# RUF006: Fire-and-forget consciousness tasks
asyncio.create_task(process_consciousness_stream())  # TODO[T4-ISSUE]: {"status":"accepted","reason":"Background consciousness..."}
```

**Why accepted?**
- B018: Dynamic `__all__` is consciousness module pattern
- B008: FastAPI requires `Depends()` in parameter defaults
- RUF006: Consciousness streams run independently

### 📋 Planned (164 violations - 36%)
**Meaning:** These **should be refactored** when time permits.

**Action:** **ADD TO WORK QUEUE** - Prioritize based on estimate/priority fields.

## 🛠️ Acting on Planned Annotations

### Step 1: Query Work Items by Priority

```bash
# Get high-priority planned items
python3 << 'EOF'
import json
import subprocess

result = subprocess.run(
    ["python3", "tools/ci/check_t4_issues.py", "--json-only"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

# Filter planned annotations
for file_data in data.get("quality_breakdown", {}).get("files_by_quality", []):
    print(f"\n📁 {file_data['file']} (weight: {file_data['weight']})")
EOF

# Or use jq for quick filtering
python3 tools/ci/check_t4_issues.py --json-only | \
  jq -r '.metrics.counts_by_status'
```

### Step 2: Find Specific Violation Types

```bash
# Find all RUF012 (mutable class attributes) to add ClassVar
ruff check . --select RUF012 --output-format=json | \
  jq -r '.[] | "\(.filename):\(.location.row): \(.message)"'

# Find all B904 (exception chaining) to fix
ruff check . --select B904 --output-format=json | \
  jq -r '.[] | "\(.filename):\(.location.row)"'

# Find all SIM105 (contextlib.suppress opportunities)
ruff check . --select SIM105 --output-format=json | \
  jq -r '.[] | "\(.filename):\(.location.row)"'
```

### Step 3: Refactor Examples

#### RUF012: Add ClassVar Annotations (27 planned)

**Before:**
```python
class ConsciousnessEngine:
    active_streams = []  # TODO[T4-ISSUE]: {"code":"RUF012","status":"planned",...}
```

**After:**
```python
from typing import ClassVar

class ConsciousnessEngine:
    active_streams: ClassVar[list] = []  # Shared across all instances
```

#### B904: Add Exception Chaining (57 planned)

**Before:**
```python
try:
    process_consciousness()
except ProcessingError:  # TODO[T4-ISSUE]: {"code":"B904","status":"planned",...}
    raise ValueError("Consciousness processing failed")
```

**After:**
```python
try:
    process_consciousness()
except ProcessingError as e:
    raise ValueError("Consciousness processing failed") from e
```

#### SIM105: Use contextlib.suppress (9 planned)

**Before:**
```python
try:  # TODO[T4-ISSUE]: {"code":"SIM105","status":"planned",...}
    __all__
except NameError:
    pass
```

**After:**
```python
from contextlib import suppress

with suppress(NameError):
    __all__
```

#### E702: Split Compound Statements (7 planned)

**Before:**
```python
if condition: return value  # TODO[T4-ISSUE]: {"code":"E702","status":"planned",...}
```

**After:**
```python
if condition:
    return value
```

#### SIM102: Collapse Nested Conditions (5 planned)

**Before:**
```python
if consciousness_active:  # TODO[T4-ISSUE]: {"code":"SIM102","status":"planned",...}
    if stream_ready:
        process()
```

**After:**
```python
if consciousness_active and stream_ready:
    process()
```

### Step 4: Automated Refactoring Script

```bash
# Create a refactoring helper
cat > scripts/refactor_planned_t4.py << 'EOF'
"""
Automated refactoring helper for planned T4 annotations.
"""

import json
import subprocess
from pathlib import Path

def get_planned_by_code(code: str):
    """Get all planned annotations for a specific violation code."""
    result = subprocess.run(
        ["ruff", "check", ".", f"--select={code}", "--output-format=json"],
        capture_output=True, text=True
    )
    if result.returncode in (0, 1):
        violations = json.loads(result.stdout) if result.stdout else []
        return [v for v in violations if v['code'] == code]
    return []

def show_planned_work():
    """Show planned work organized by code and priority."""
    codes = ["RUF012", "B904", "SIM105", "E702", "SIM102"]
    
    print("📋 PLANNED REFACTORING WORK\n")
    for code in codes:
        violations = get_planned_by_code(code)
        if violations:
            print(f"\n{code} ({len(violations)} items):")
            for v in violations[:5]:  # Show first 5
                print(f"  • {v['filename']}:{v['location']['row']}")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more")

if __name__ == "__main__":
    show_planned_work()
EOF

python3 scripts/refactor_planned_t4.py
```

## 📊 Prioritization Strategy

### High Priority (Do First)
1. **Files with high weight** (many violations)
   - `core/__init__.py` (50 violations)
   - `consciousness/__init__.py` (36 violations)
   - `api/feedback_api.py` (28 violations)

2. **Quick wins** (low estimate, high impact)
   - E702: ~5 min each (7 total = 35 min)
   - SIM102: ~5 min each (5 total = 25 min)
   - SIM105: ~10 min each (9 total = 90 min)

3. **Type safety improvements**
   - RUF012: ~15 min each (27 total = 6.75 hours)

### Medium Priority
1. **Exception handling quality**
   - B904: ~15 min each (57 total = 14.25 hours)

2. **Lazy loading patterns**
   - F821: ~30 min each (43 total = 21.5 hours)

## 🔄 Workflow Integration

### Pre-Commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
python3 tools/ci/check_t4_issues.py --json-only | \
  jq -e '.summary.quality_issues == 0' || {
    echo "❌ T4 quality issues found! Run: python3 tools/ci/check_t4_issues.py"
    exit 1
  }
```

### CI/CD Integration
```yaml
# .github/workflows/t4-quality.yml
name: T4 Quality Check
on: [push, pull_request]

jobs:
  t4-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check T4 Annotations
        run: |
          python3 tools/ci/check_t4_issues.py --json-only
          # Fail if quality score < 95
          python3 -c "
          import json, sys
          with open('t4_results.json') as f:
              data = json.load(f)
              score = data['metrics']['annotation_quality_score']
              if score < 95:
                  print(f'❌ Quality score {score} < 95')
                  sys.exit(1)
          "
```

### Sprint Planning
```bash
# Generate sprint-ready work items
python3 << 'EOF'
import json
import subprocess

result = subprocess.run(
    ["python3", "tools/ci/check_t4_issues.py", "--json-only"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

# Group by estimate
by_estimate = {}
counts = data['metrics']['counts_by_code']

print("🎯 SPRINT PLANNING - PLANNED WORK\n")
print("Quick Wins (< 30 min):")
print(f"  • SIM102 (5 items × 5min = 25min)")
print(f"  • E702 (7 items × 5min = 35min)")
print(f"  • SIM105 (9 items × 10min = 90min)")
print(f"  Total: 21 items, ~2.5 hours\n")

print("Medium Effort (30 min - 2 hours):")
print(f"  • RUF012 (27 items × 15min = 6.75 hours)")
print(f"  • B904 (57 items × 15min = 14.25 hours)")
print(f"  Total: 84 items, ~21 hours\n")

print("Larger Refactoring (> 2 hours):")
print(f"  • F821 (43 items × 30min = 21.5 hours)")
print(f"  Total: 43 items, ~21.5 hours\n")

print("📊 TOTAL PLANNED WORK: 148 items, ~45 hours (~1 sprint)")
EOF
```

## 🎯 Team Assignments

### Based on Ownership in Annotations

```bash
# See which team owns what
python3 tools/ci/check_t4_issues.py --json-only | \
  jq -r '.metrics.counts_by_status'

# Matriz Team (271 accepted + some planned)
# - Maintain accepted patterns
# - Review planned items for matriz/ directory

# Consciousness Team (164 planned)
# - Refactor planned items
# - Update patterns in consciousness/ directory
```

## 📈 Tracking Progress

### Create GitHub Issues
```bash
# Auto-generate issues for planned work
cat > scripts/create_refactoring_issues.py << 'EOF'
"""Generate GitHub issues for planned T4 refactoring."""

import json
import subprocess

codes = {
    "RUF012": "Add ClassVar annotations for mutable class attributes",
    "B904": "Add exception chaining (raise...from)",
    "SIM105": "Refactor to contextlib.suppress",
    "E702": "Split compound statements",
    "SIM102": "Collapse nested conditionals"
}

for code, title in codes.items():
    result = subprocess.run(
        ["ruff", "check", ".", f"--select={code}", "--output-format=json"],
        capture_output=True, text=True
    )
    violations = json.loads(result.stdout) if result.stdout else []
    
    if violations:
        print(f"\n## {code}: {title}")
        print(f"**Count:** {len(violations)} violations")
        print(f"**Label:** `refactoring`, `code-quality`, `{code}`")
        print(f"\n**Files affected:**")
        files = set(v['filename'] for v in violations)
        for f in sorted(files)[:10]:
            print(f"- `{f}`")
        if len(files) > 10:
            print(f"- ... and {len(files) - 10} more files")

EOF

python3 scripts/create_refactoring_issues.py
```

## 🏆 Success Metrics

Track progress with:
```bash
# Weekly progress check
python3 tools/ci/check_t4_issues.py --json-only | jq '{
  total: .summary.total_findings,
  annotated: .summary.annotated,
  planned: .metrics.counts_by_status.planned,
  quality: .metrics.annotation_quality_score
}'

# Goal: Reduce "planned" count over time while maintaining quality score
```

## 🎓 Best Practices

### When to Act on Annotations

1. **Accepted annotations:** NEVER remove without discussion
   - These document intentional architectural decisions
   - Removing them reintroduces lint noise

2. **Planned annotations:** Act when:
   - Touching nearby code anyway (opportunistic refactoring)
   - During dedicated quality improvement sprints
   - File is being heavily modified (reduce conflicts)

3. **Legacy annotations:** Migrate to current format
   - Use `tools/ci/migrate_annotations.py`
   - Update to TODO[T4-ISSUE] format

### Adding New Annotations

When new violations appear:
```bash
# Use existing batch scripts as templates
python3 scripts/annotate_b018_batch.py  # Example pattern

# Or add manually with correct format:
# violation_line  # TODO[T4-ISSUE]: {"code":"X000","ticket":"GH-1234","owner":"team","status":"planned|accepted","reason":"specific reason","estimate":"15m","priority":"medium","dependencies":"none","id":"unique_id"}
```

## 📚 Additional Resources

- **T4 Platform Docs:** `docs/gonzo/T4_ONBOARD_AGENTS.md`
- **Annotation Scripts:** `scripts/annotate_*_batch.py`
- **Quality Checker:** `tools/ci/check_t4_issues.py`
- **Migration Tool:** `tools/ci/migrate_annotations.py`
- **Completion Summary:** `T4_ANNOTATION_COMPLETE_SUMMARY.md`

---

**Remember:** T4 annotations are **living documentation**. They tell the story of your codebase's intentional design decisions and planned improvements. Act on "planned" items to improve quality, and respect "accepted" items as architectural choices.

🎯 **Current Status:** 459/459 annotated (100%) | Quality: 100/100 | Planned: 164 items (~45 hours work)
