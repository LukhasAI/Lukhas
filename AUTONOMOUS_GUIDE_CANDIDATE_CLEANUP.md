# Autonomous Guide: Candidate Lane Cleanup

**Goal:** Reduce syntax errors and improve candidate/ lane health for promotion to core/
**Priority:** Low (When promoting to core/)
**Estimated Time:** 30-40 hours
**Compatible With:** Claude Code, Codex, Copilot

---

## Context

The candidate/ lane contains **experimental code** with:
- 1,095 syntax errors (expected)
- Many incomplete implementations
- Research prototypes

**This is by design.** Cleanup is only needed when promoting code to core/.

---

## When to Execute

**Trigger:** When promoting candidate code to core/ or lukhas/

**NOT before:** Candidate is intentionally experimental

---

## Execution Strategy

### Phase 1: Identify Promotion Candidates (1 hour)
```bash
# Find mature candidate/ modules
find candidate/ -name "*.py" -type f | \
  xargs wc -l | sort -rn | head -20

# Check test coverage
find tests/unit/candidate/ -name "test_*.py" | wc -l

# Identify stable modules (have tests, low TODO count)
```

### Phase 2: Fix Syntax Errors (Per Module, 2-4 hours each)
```bash
# Check syntax for target module
python3 -m py_compile candidate/consciousness/dream_engine.py

# Fix errors iteratively
python3 -m ruff check candidate/consciousness/dream_engine.py --fix

# Run tests
pytest tests/unit/candidate/consciousness/test_dream_engine.py

# Validate
make smoke
```

### Phase 3: Promote to core/ (Per Module)
```bash
git checkout -b promote/dream-engine-$(date +%Y-%m-%d)

# Move module
mv candidate/consciousness/dream_engine.py core/consciousness/
mv tests/unit/candidate/consciousness/test_dream_engine.py tests/unit/core/consciousness/

# Update imports throughout codebase
# Fix any broken references

# Validate
make smoke
pytest tests/unit/core/consciousness/test_dream_engine.py

git add .
git commit -m "feat(core): promote dream_engine from candidate/ to core/"
```

---

## Success Criteria (Per Promotion)
- ✅ 0 syntax errors in promoted module
- ✅ 75%+ test coverage
- ✅ Smoke tests 10/10 PASS
- ✅ All imports updated
- ✅ Documentation complete

**Timeline:** Ongoing, per-module basis
**Risk:** Medium (requires careful validation)

---

## Important: DON'T Clean All of candidate/

**Rationale:** candidate/ is an **experimental sandbox**. It SHOULD contain:
- Broken prototypes
- Research code
- Incomplete implementations

Only clean when promoting to core/.
