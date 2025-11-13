# Autonomous Execution Guides - Index

**Purpose:** Step-by-step guides for AI agents (Claude Code, Codex, GitHub Copilot) to execute complex codebase improvements autonomously

**Created:** 2025-10-28
**Status:** Ready for Execution

---

## 📌 Canonicalization Note (2025-10-28)

A duplicate file (`Untitled-2.md`) that replicated the Candidate Lane Cleanup guide was removed to avoid drift. The **canonical** Candidate Lane Cleanup guide is:

`AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md`

All references in this README have been updated to point to the canonical guide. If you want a different file to be canonical, tell me and I will reconcile and update references.

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
**Goal:** Fix E402 "import not at top" violations in production lanes
**Priority:** ⭐⭐ Medium
**Time:** ~6-8 hours
**Difficulty:** Easy-Medium
**Risk:** Low (ruff --fix is safe)

**Quick Summary:**
- Auto-fix safe cases with `ruff check --fix`
- Manual fix complex cases (runtime imports)
- Add `# noqa: E402` for legitimate exceptions (with justification and TTL)
- Focus on production lane first (`lukhas/`, `core/`, `serve/`)

**When to Execute:** Can start immediately, good for AI auto-fix

---

### 4. [Test Coverage Expansion](AUTONOMOUS_GUIDE_TEST_COVERAGE.md)
**Goal:** Achieve target coverage for `lukhas/` production lane
**Priority:** ⭐⭐⭐⭐ High (Long-term)
**Time:** ~20-30 hours over multiple sprints
**Difficulty:** Medium-High
**Risk:** Low (additive only)

**Quick Summary:**
- **Phase 1:** Fix test collection errors (CRITICAL)
- **Phase 2:** Measure current coverage baseline
- **Phase 3:** Prioritize gaps (core, api, identity, consciousness)
- **Phase 4:** Write missing tests (15-20 hours)
- **Phase 5:** Add integration tests

**When to Execute:** Start with Phase 1 immediately (collection errors blocking progress)

---

### 5. [Candidate Lane Cleanup](AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md)
**Goal:** Clean `candidate/` modules for promotion to `core/`
**Priority:** ⭐ Low (Only when promoting)
**Time:** ~2-4 hours per module
**Difficulty:** Medium
**Risk:** Medium (requires careful validation)

**Quick Summary:**
- **DO NOT** clean all of `candidate/` (it's experimental by design)
- **ONLY** clean when promoting a module to `core/`
- Per-module: fix syntax → add tests → validate → move to `core/`
- Requires **>=90% module-level unit-test coverage** for promoted modules (see canonical guide)

**When to Execute:** Only when promoting specific modules, not as bulk cleanup

---

## 🎯 Recommended Execution Order

### Immediate Priority (Start Now)
1. **Test Coverage - Phase 1** - Fix test collection errors (CRITICAL blocker)
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

### Agent Assignments

Each Autonomous Guide is mapped to a **primary agent** (owner) and **secondary agents** (reviewers/auditors):

#### MATRIZ Migration Completion
- **Primary:** **Codex** (AST codemods, patch generation)
- **Secondary:** Claude HaikuGPT-5 / GPT-5 Preview (risk & ethics), Grok Code Fast (log/bench parsing), Claude Conner 4.5 (policy)
- **Canonical scripts:** `scripts/consolidation/rewrite_matriz_imports.py`
- **Run (dry-run):** `python3 scripts/consolidation/rewrite_matriz_imports.py --path lukhas core tests --dry-run --verbose`
- **Apply (safe):** `python3 scripts/consolidation/rewrite_matriz_imports.py --path core tests --git-apply`
- **CI workflow:** `.github/workflows/migration-dryrun.yml`
- **Autonomy:** Dry-run only → human review → git-apply on new branch (human merge)

#### TODO Cleanup Campaign
- **Primary:** **GitHub Copilot** (interactive edits, test writing)
- **Secondary:** Codex (automation scripts), Claude Conner 4.5 / Sonnet 4 (triage), Grok Code Fast (inventory parsing)
- **Canonical scripts:** `scripts/todo_migration/create_issues.py`, `scripts/todo_migration/replace_todos_with_issues.py`
- **Run (dry-run):** `python3 scripts/todo_migration/create_issues.py --input todo_inventory.csv --repo org/repo --dry-run`  
  `python3 scripts/todo_migration/replace_todos_with_issues.py --map artifacts/todo_to_issue_map.json --dry-run`
- **CI workflow:** `.github/workflows/todo-dryrun.yml`
- **Autonomy:** Conservative: dry-run → small PRs (≤20 files) → human approvals for bulk (>100)

#### Import Organization (E402)
- **Primary:** **Codex** (AST transformers, per-file patches)
- **Secondary:** GitHub Copilot (manual fixes & `noqa` justifications), Claude Conner 4.5 (security), Grok Code Fast
- **Canonical scripts:** `scripts/consolidation/rewrite_matriz_imports.py` (reuse/mode for E402 work)
- **Run (dry-run):** `python3 scripts/consolidation/rewrite_matriz_imports.py --path lukhas core serve --dry-run --verbose`
- **CI workflow:** Use `import-health` job to upload `artifacts/patches` and run `scripts/import_health/fail_on_delta.py`
- **Autonomy:** Dry-run + human review; `noqa` only with documented issue & TTL

#### Test Coverage Expansion
- **Primary:** **GitHub Copilot** (assisted test authoring inside VSCode)
- **Secondary:** Codex (test harness generation), Claude HaikuGPT-5 / GPT-5 Preview (adversarial test design)
- **Run:** `make smoke`, `pytest --maxfail=1`, coverage checks
- **Autonomy:** Human-led; Copilot accelerates writing tests. PRs limited to small batches.

#### Candidate Lane Cleanup (Promotion Path)
- **Primary:** **GitHub Copilot** (interactive fixes & tests)
- **Secondary:** Codex (promotion scripts), Claude Conner 4.5 (ethics), Grok Code Fast (logs)
- **Workflow:** Follow `AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md` → require `PROMOTE.md` and two approvals
- **Autonomy:** Human-in-the-loop only; no autopromotion

---

### Operational Runbook

**For all automated operations:**

1. **Always start with dry-run** for automated scripts. Inspect `artifacts/*` before any write.  
2. **Create a feature branch** for any `git-apply` operation: migrations should land on `migration/*` or `promote/*` branches.  
3. **Run smoke tests** and targeted test suites after applying patches locally (before opening PR).  
4. **Upload artifacts** in PR for reviewer inspection (per-file patches, migration summary, manifest).  
5. **Reviewer gate:** Tech + Security approvals required for all production-lane changes.  
6. **Canary & Monitor:** For services, require 48–72 hours observation and automated rollback triggers.

---

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
| Import Organization | E402 violations | ~1,978 | <=1 | ~100% reduction in production lanes |
| Test Coverage | lukhas/ coverage | Unknown | Target (see coverage guide) | High confidence |
| Candidate Cleanup | Syntax errors | 1,095 (candidate/) | Varies per module | Per-module

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

**Many metrics are skewed by `candidate/`. Focus on production lane health.**

---

## 📝 Documentation Created This Session

1. ✅ [CODEBASE_STATUS_2025-10-28.md](CODEBASE_STATUS_2025-10-28.md) - Comprehensive health report
2. ✅ [AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md](AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md)
3. ✅ [AUTONOMOUS_GUIDE_TODO_CLEANUP.md](AUTONOMOUS_GUIDE_TODO_CLEANUP.md)
4. ✅ [AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md](AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md)
5. ✅ [AUTONOMOUS_GUIDE_TEST_COVERAGE.md](AUTONOMOUS_GUIDE_TEST_COVERAGE.md)
6. ✅ [AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md](AUTONOMOUS_GUIDE_CANDIDATE_CLEANUP.md)
7. ✅ [README_AUTONOMOUS_GUIDES.md](README_AUTONOMOUS_GUIDES.md)

**Total:** ~1,186 lines of autonomous execution guidance

---

## 🎓 Lessons from Session 2025-10-28

**What Worked:**
- AST-safe automated tooling (MATRIZ rewriter)
- Small, focused PRs (1-23 imports each)
- Test-first validation (smoke tests before commit)
- Detailed autonomous plans (high-quality automation scripts)

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

## 🔗 Related Documentation

- **[AGENTS.md](AGENTS.md)** - Agent coordination system with navigation guidance
- **[CLAUDE.md](CLAUDE.md)** - Project-specific instructions and lane architecture
- **[claude.me](claude.me)** - Master system architecture (7,000+ files)
- **Infrastructure:**
  - [candidate/PROMOTE.md](candidate/PROMOTE.md) - Promotion template
  - [.github/PULL_REQUEST_TEMPLATE/](\.github/PULL_REQUEST_TEMPLATE/) - PR templates
  - [.github/workflows/](\.github/workflows/) - CI/CD workflows
  - [ETHICS_ASSESSMENT_TEMPLATE.md](ETHICS_ASSESSMENT_TEMPLATE.md) - Ethics framework

---

**Last Updated:** 2025-10-28
**Maintained By:** LUKHΛS Autonomous Guides
**Status:** Production-Ready
