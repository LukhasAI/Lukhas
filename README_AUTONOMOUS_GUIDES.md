# Autonomous Execution Guides - Index

**Purpose:** Step-by-step guides for AI agents (Claude Code, Codex, GitHub Copilot) to execute complex codebase improvements autonomously

**Created:** 2025-10-28
**Status:** Ready for Execution

---

## 📚 Available Guides

### 1. [MATRIZ Migration Completion](AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md)
**Goal:** Complete remaining 35 MATRIZ import migrations
**Priority:** ⭐⭐⭐ Medium (Q1 2026)
**Time:** ~4 hours active work over 1 week
**Difficulty:** Medium
**Risk:** Low

**Quick Summary:**
- Migrate 6 remaining groups: benchmarks, performance, e2e, website, examples, tools
- Use AST-safe rewriter for guaranteed correctness
- Enable CI enforcement after 100% completion
- Small PRs, test-first validation

**When to Execute:** Q1 2026, after current work stabilizes

---

### 2. [TODO Cleanup Campaign](AUTONOMOUS_GUIDE_TODO_CLEANUP.md)
**Goal:** Reduce TODO debt from 6,876 to <1,000
**Priority:** ⭐⭐ Medium (Ongoing)
**Time:** ~14 hours over 3-4 sessions
**Difficulty:** Medium-High
**Risk:** Low (if validated frequently)

**Quick Summary:**
- Strategy A: Delete obsolete TODOs (~2,000 items)
- Strategy B: Convert to GitHub issues (~1,500 items)
- Strategy C: Fix simple TODOs (~1,000 items)
- Strategy D: Exclude candidate/ lane (~1,500 items)

**When to Execute:** Can start immediately, execute incrementally

---

### 3. [Import Organization (E402)](AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md)
**Goal:** Fix 1,978 "import not at top" violations
**Priority:** ⭐⭐ Medium
**Time:** ~6-8 hours
**Difficulty:** Easy-Medium
**Risk:** Low (ruff --fix is safe)

**Quick Summary:**
- Auto-fix safe cases with `ruff check --fix`
- Manual fix complex cases (runtime imports)
- Add `# noqa: E402` for legitimate exceptions
- Focus on production lane first (lukhas/, core/, serve/)

**When to Execute:** Can start immediately, good for AI auto-fix

---

### 4. [Test Coverage Expansion](AUTONOMOUS_GUIDE_TEST_COVERAGE.md)
**Goal:** Achieve 75%+ coverage for lukhas/ production lane
**Priority:** ⭐⭐⭐⭐ High (Long-term)
**Time:** ~20-30 hours over multiple sprints
**Difficulty:** Medium-High
**Risk:** Low (additive only)

**Quick Summary:**
- **Phase 1:** Fix 223 test collection errors (CRITICAL)
- **Phase 2:** Measure current coverage baseline
- **Phase 3:** Prioritize gaps (core, api, identity, consciousness)
- **Phase 4:** Write missing tests (15-20 hours)
- **Phase 5:** Add integration tests

**When to Execute:** Start with Phase 1 immediately (collection errors blocking progress)

---

### 5. [Candidate Lane Cleanup](AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md)
**Goal:** Clean candidate/ modules for promotion to core/
**Priority:** ⭐ Low (Only when promoting)
**Time:** ~2-4 hours per module
**Difficulty:** Medium
**Risk:** Medium (requires careful validation)

**Quick Summary:**
- **DO NOT** clean all of candidate/ (it's experimental by design)
- **ONLY** clean when promoting module to core/
- Per-module: fix syntax → add tests → validate → move to core/
- Requires 75%+ coverage before promotion

**When to Execute:** Only when promoting specific modules, not as bulk cleanup

---

## 🎯 Recommended Execution Order

### Immediate Priority (Start Now)
1. **Test Coverage - Phase 1** - Fix 223 collection errors (CRITICAL blocker)
2. **Import Organization** - Auto-fix E402 with ruff (quick wins)

### Short-term (Next 1-2 Weeks)
3. **TODO Cleanup - Strategy A** - Delete obsolete TODOs (high impact)
4. **Test Coverage - Phase 2-3** - Measure and prioritize gaps

### Medium-term (Q1 2026)
5. **MATRIZ Migration Completion** - Final 35 imports
6. **TODO Cleanup - Strategies B-D** - Issues, fixes, exclusions
7. **Test Coverage - Phase 4-5** - Write missing tests

### Long-term (As Needed)
8. **Candidate Lane Cleanup** - Only when promoting modules

---

## 🤖 For AI Agents

### Prerequisites
All guides assume:
- Working directory: `/Users/agi_dev/LOCAL-REPOS/Lukhas`
- Branch: `main` (up to date)
- Tools available: `python3`, `pytest`, `ruff`, `git`, `gh` CLI
- Smoke tests passing before starting

### Execution Pattern
1. Read the full guide before starting
2. Follow phases sequentially
3. Validate after each phase (smoke tests 10/10 PASS)
4. Create small, focused PRs (not monolithic)
5. Report progress to user
6. Use rollback procedure if issues arise

### Success Signals
- ✅ Smoke tests: 10/10 PASS
- ✅ Metrics improved (coverage up, TODOs down, errors down)
- ✅ No production incidents
- ✅ All PRs documented

---

## 📊 Expected Impact

| Guide | Metric | Before | Target | Impact |
|-------|--------|--------|--------|--------|
| MATRIZ Completion | Legacy imports | 35 | 0 | 100% complete |
| TODO Cleanup | TODO count | 6,876 | <1,000 | 87% reduction |
| Import Organization | E402 violations | 1,978 | <100 | 95% reduction |
| Test Coverage | lukhas/ coverage | Unknown | 75%+ | High confidence |
| Candidate Cleanup | Syntax errors | 1,095 | Varies | Per-module |

**Total Expected Time:** 44-62 hours over 4-8 weeks

---

## ⚠️ Important Notes

### What These Guides Are
- ✅ Detailed, step-by-step autonomous execution plans
- ✅ Compatible with AI agents and manual execution
- ✅ Include rollback procedures and validation steps
- ✅ Based on T4 engineering standards

### What These Guides Are NOT
- ❌ Not requirements (execute at your discretion)
- ❌ Not all immediate priority (see execution order)
- ❌ Not replacing human judgment (AI should report blockers)

### Lane Architecture Reminder
The codebase uses **3-lane architecture**:
- **Production (`lukhas/`):** High quality, stable → prioritize cleanup
- **Integration (`core/`):** Moderate quality, tested → cleanup as needed
- **Development (`candidate/`):** Experimental, intentionally messy → DON'T cleanup unless promoting

**Many metrics are skewed by candidate/. Focus on production lane health.**

---

## 📝 Documentation Created This Session

1. ✅ [CODEBASE_STATUS_2025-10-28.md](CODEBASE_STATUS_2025-10-28.md) - Comprehensive health report
2. ✅ [AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md](AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md) - 130 lines
3. ✅ [AUTONOMOUS_GUIDE_TODO_CLEANUP.md](AUTONOMOUS_GUIDE_TODO_CLEANUP.md) - 240 lines
4. ✅ [AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md](AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md) - 74 lines
5. ✅ [AUTONOMOUS_GUIDE_TEST_COVERAGE.md](AUTONOMOUS_GUIDE_TEST_COVERAGE.md) - 130 lines
6. ✅ [AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md](AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md) - 98 lines
7. ✅ [README_AUTONOMOUS_GUIDES.md](README_AUTONOMOUS_GUIDES.md) - This file

**Total:** ~1,186 lines of autonomous execution guidance

---

## 🎓 Lessons from Session 2025-10-28

**What Worked:**
- AST-safe automated tooling (MATRIZ rewriter)
- Small, focused PRs (1-23 imports each)
- Test-first validation (smoke tests before commit)
- Detailed autonomous plans (463-line plan → 90/100 Codex success)

**What to Improve:**
- Task coordination (prevent duplicate TODO attempts)
- Pre-flight checks (verify file doesn't exist)
- Goal verification (check if already achieved)

**Success Rate:** 70% PR merge rate (100% excluding duplicates)

---

## 🚀 Quick Start

**For an AI Agent to get started:**

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout main && git pull origin main

# Option 1: Fix test collection errors (CRITICAL)
cat AUTONOMOUS_GUIDE_TEST_COVERAGE.md
# Execute Phase 1

# Option 2: Auto-fix imports (quick wins)
cat AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md
# Execute Phase 1

# Option 3: Clean up obsolete TODOs
cat AUTONOMOUS_GUIDE_TODO_CLEANUP.md
# Execute Strategy A
```

---

**Last Updated:** 2025-10-28
**Maintained By:** Claude Code (Sonnet 4.5)
**Status:** Production-Ready
