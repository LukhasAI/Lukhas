# EPIC: MATRIZ Flattening Audit & Bridge Remediation

**Purpose:** Coordinate bridge remediation campaign to fix 211 collection errors.

**Discovery:**
✅ Root cause: 786 modules in labs/* lack bridge exports
✅ Files exist but bridges don't expose them
✅ Top 20 bridges cause 50% of failures
✅ Tools created: find_bridge_gaps.py, automation scripts

**Phases:**
- **Phase 1:** Fix top 5 bridges (211 → ~180 errors)
- **Phase 2:** Automate remaining 766 bridges (~180 → <50 errors)
- **Phase 3:** Fix test assertions (<50 → 0 errors, >90% passing)

**Timeline:**
- Week 1: Phase 1
- Week 2: Phase 2
- Week 3: Phase 3

**Success Criteria:**
- [ ] Collection errors: 211 → <10
- [ ] Tests collecting: 14/42 → 42/42
- [ ] Pass rate: Unknown → >90%
- [ ] All 786 gaps resolved
- [ ] Pre-commit hook for future prevention

**Documentation:**
- `BRIDGE_GAP_ANALYSIS.md`
- `SMOKE_TEST_FIX_BRIEF.md`
- `scripts/find_bridge_gaps.py`
- `scripts/full_smoke_fix_automation.py`

**Coordination:**
- Weekly updates in `BRIDGE_PROGRESS.md`
- Tag @codex in PR comments
- Final sign-off before merge to main
