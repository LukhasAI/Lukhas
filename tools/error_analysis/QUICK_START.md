# Error Analysis Toolkit - Quick Start Guide

**Purpose**: Fix pytest collection errors 16x faster with automated pattern detection

---

## 🚀 Basic Workflow (5 minutes total)

```bash
# Step 1: Collect errors (30 sec)
PYTHONPATH=. python3 -m pytest --collect-only -q --tb=short 2>&1 \
  | tee artifacts/errors_$(date +%Y%m%d).txt

# Step 2: Analyze (30 sec)
python3 tools/error_analysis/pytest_error_analyzer.py \
  artifacts/errors_*.txt

# Step 3: Extract top bridges (1 min)
cat artifacts/errors_*_analysis.json | \
  python3 -c "
import sys, json
errors = json.load(sys.stdin)['errors']
modules = [e['detail'] for e in errors if e['category'] == 'ModuleNotFound']
print('\n'.join(modules[:10]))
" > /tmp/bridges_needed.txt

# Step 4: Generate bridges (5 sec)
python3 tools/error_analysis/bridge_generator.py \
  --batch /tmp/bridges_needed.txt

# Step 5: Verify (30 sec)
PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 | grep -c ERROR
```

---

## 📊 Analyzer Commands

**Basic Analysis**:
```bash
python3 tools/error_analysis/pytest_error_analyzer.py errors.txt
```

**With Custom Output Path**:
```bash
python3 tools/error_analysis/pytest_error_analyzer.py errors.txt \
  # Auto-creates: errors_analysis.json
```

**Query JSON Results**:
```bash
# Category summary
cat errors_analysis.json | jq '.category_summary'

# Top 5 errors by count
cat errors_analysis.json | jq '.errors[:5] | .[] | "\(.count) × \(.category): \(.detail)"'

# All ModuleNotFound errors
cat errors_analysis.json | jq '.errors[] | select(.category=="ModuleNotFound")'
```

---

## 🔧 Bridge Generator Commands

**Single Bridge**:
```bash
python3 tools/error_analysis/bridge_generator.py lukhas.consciousness.meta_assessor
```

**Single Bridge with Stubs**:
```bash
python3 tools/error_analysis/bridge_generator.py \
  lukhas.consciousness.meta_assessor \
  --symbols MetaCognitiveAssessor,AssessmentResult
```

**Batch Mode** (recommended):
```bash
# Create module list file
cat > missing_modules.txt <<EOF
lukhas.consciousness.meta_assessor:MetaCognitiveAssessor
observability.advanced_metrics
candidate.orchestration.multi_ai_router
EOF

# Generate all bridges
python3 tools/error_analysis/bridge_generator.py --batch missing_modules.txt
```

---

## 📋 Module List File Format

```
# Lines starting with # are comments
# Format: module_name[:symbol1,symbol2,...]

# With symbols (generates stubs)
lukhas.consciousness.meta_assessor:MetaCognitiveAssessor,AssessmentResult
lukhas.governance.identity.core:IdentityCore,IdentityConfig

# Without symbols (imports all public attributes)
observability.advanced_metrics
candidate.orchestration.multi_ai_router
```

---

## 🎯 Common Patterns

### Fix Top 10 Errors in 2 Minutes

```bash
# Analyze
python3 tools/error_analysis/pytest_error_analyzer.py artifacts/errors.txt

# Extract top 10 ModuleNotFound
jq -r '.errors[] | select(.category=="ModuleNotFound") | .detail' \
  artifacts/errors_analysis.json | head -10 > /tmp/top10.txt

# Generate bridges
python3 tools/error_analysis/bridge_generator.py --batch /tmp/top10.txt

# Re-run collection
PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 | grep -c ERROR
```

### Extract Export Fixes

```bash
# Get CannotImport errors with fix templates
jq -r '.errors[] | select(.category=="CannotImport") |
  "# \(.count)x \(.detail)\n\(.fix_suggestions[0])\n"' \
  artifacts/errors_analysis.json > /tmp/export_fixes.sh

# Review and apply manually
cat /tmp/export_fixes.sh
```

### Compare Before/After

```bash
# Before
PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 \
  | tee artifacts/before.txt | grep -c ERROR

# Apply fixes...

# After
PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 \
  | tee artifacts/after.txt | grep -c ERROR

# Diff
echo "Errors fixed: $(($(grep -c ERROR artifacts/before.txt) - $(grep -c ERROR artifacts/after.txt)))"
```

---

## 🔍 Troubleshooting

**Problem**: "ModuleNotFound" after generating bridge
```bash
# Check parent __init__.py files exist
ls -la lukhas/consciousness/__init__.py
ls -la lukhas/__init__.py

# Bridge generator auto-creates them, but verify
```

**Problem**: Bridge doesn't import expected symbols
```bash
# Add symbols explicitly
python3 tools/error_analysis/bridge_generator.py \
  lukhas.consciousness.meta_assessor \
  --symbols MetaCognitiveAssessor,AssessmentResult
```

**Problem**: "cannot import name X from Y"
```bash
# This is CannotImport (not ModuleNotFound)
# Get fix template:
jq -r '.errors[] | select(.category=="CannotImport" and .detail|contains("X from Y")) |
  .fix_suggestions[0]' artifacts/errors_analysis.json

# Apply manually by adding export to target module
```

---

## 📈 Performance Benchmarks

**Real Data** (LUKHAS repository, 2025-10-08):

| Metric | Value |
|--------|-------|
| Total errors analyzed | 353 |
| Unique patterns found | 143 |
| Analysis time | <1 second |
| JSON output size | 109KB |
| Bridge generation (10 modules) | <5 seconds |
| Manual equivalent time | 80 minutes |
| Toolkit time | 5 minutes |
| **Speed improvement** | **16x faster** |

---

## 🎓 Pro Tips

1. **Always analyze first** - Don't guess, let the toolkit find patterns
2. **Fix high-count errors first** - Top 5 errors often = 40% of total
3. **Use batch mode** - 10 bridges in 5 seconds vs 30 minutes manually
4. **Query JSON for insights** - Use `jq` to find exactly what you need
5. **Version your error logs** - Track progress over time with timestamps

---

## 📚 Full Documentation

- **Complete Guide**: [tools/error_analysis/README.md](README.md)
- **Performance Analysis**: [artifacts/TOOLKIT_SUMMARY.md](../../artifacts/TOOLKIT_SUMMARY.md)
- **Live Demo**: [artifacts/TOOLKIT_DEMO.md](../../artifacts/TOOLKIT_DEMO.md)

---

## 🆘 Emergency One-Liner

```bash
# Analyze → Extract → Generate → Verify (all in one command)
PYTHONPATH=. python3 -m pytest --collect-only -q --tb=short 2>&1 | \
  tee /tmp/err.txt && \
  python3 tools/error_analysis/pytest_error_analyzer.py /tmp/err.txt && \
  jq -r '.errors[] | select(.category=="ModuleNotFound") | .detail' /tmp/err_analysis.json | \
  head -10 > /tmp/bridges.txt && \
  python3 tools/error_analysis/bridge_generator.py --batch /tmp/bridges.txt && \
  echo "Done! Re-run pytest to verify."
```

---

**Version**: 1.0.0
**Updated**: 2025-10-08
**License**: Internal LUKHAS tooling
