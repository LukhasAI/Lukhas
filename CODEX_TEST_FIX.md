# 🔧 CODEX Test Dependencies - Quick Fix

**Issue**: Test collection errors in container/remote environment

**Solution**: Run this single command to fix all dependencies:

```bash
python3 tools/fix_test_dependencies.py
```

## What This Fixes

✅ **memory_noop import errors**: Fixes `from memory_noop import NoopMemory`  
✅ **RiskGauge missing**: Adds missing `RiskGauge` and `RiskSeverity` classes  
✅ **asgi_lifespan missing**: Installs `pip install asgi_lifespan`  
✅ **asyncpg missing**: Installs `pip install asyncpg`  
✅ **urllib3 compatibility**: Downgrades to resolve OpenSSL warnings  
✅ **enterprise symlink**: Creates enterprise → products/enterprise link

## Validation After Fix

```bash
# Test core functionality
python3 -m pytest tests/candidate/aka_qualia/test_simple.py -v

# Check datetime violations  
python3 -m ruff check . --select DTZ003,DTZ005 --quiet | wc -l

# Full validation dashboard
./tools/codex_validation.sh
```

## Expected Results

- **Before**: 5 test collection errors
- **After**: All core tests collect successfully
- **Ready for**: CODEX 1 UTC datetime fixes with proper validation

---

**📋 CODEX 1 Action**: Run the fixer, then proceed with systematic datetime UTC standardization across 80,908 violations.