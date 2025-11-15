# Claude Code Web - Ready-to-Paste Prompts

**Generated:** 2025-11-08
**Purpose:** Paste these prompts directly into Claude Code Web for PR review
**Total Prompts:** 5

---

## PROMPT 1: PR #1100 - Production Audit Fixes (CRITICAL ⚠️)

**Priority:** CRITICAL - Do this first!
**Time:** 15-20 minutes
**Impact:** Unblocks production deployment

### Copy everything below the line and paste into https://claude.ai

```
Review and approve PR #1100 "Fix critical audit findings for production deployment"

**PR CONTEXT:**
- Number: #1100
- Files changed: 3
- Changes: +137/-51 lines
- Purpose: Address P0 production blockers identified in November audit

**FILES TO REVIEW:**
1. docs/audits/P0_AUDIT_RESOLUTION_STATUS.md
2. docs/runbooks/GUARDIAN_EMERGENCY_PROCEDURES.md
3. lukhas_website/lukhas/governance/guardian_system.py

**REVIEW CHECKLIST:**

1. **Audit Documentation (P0_AUDIT_RESOLUTION_STATUS.md)**
   - Verify all P0 findings are documented as RESOLVED
   - Check that resolution evidence is provided for each finding
   - Ensure no P0 items remain in PENDING or IN_PROGRESS status
   - Validate that resolution dates are recent

2. **Emergency Procedures Documentation (GUARDIAN_EMERGENCY_PROCEDURES.md)**
   - Verify kill-switch procedure is documented
   - Check dual-approval override process is complete
   - Ensure emergency contact information is current
   - Validate runbook is actionable (clear steps, no ambiguity)

3. **Guardian System Code (guardian_system.py)**
   - Review code changes for correctness
   - Check that emergency procedures are implemented in code
   - Verify no breaking changes to existing Guardian functionality
   - Ensure proper error handling and logging
   - Check that changes align with documented procedures

4. **Integration & Safety**
   - Verify changes don't introduce new security vulnerabilities
   - Check that tests cover the new emergency procedures
   - Ensure backward compatibility is maintained
   - Validate that the code follows LUKHAS coding standards

**DECISION CRITERIA:**

**APPROVE IF:**
- All P0 audit findings are addressed
- Emergency procedures are complete and actionable
- Code changes are correct and safe
- Tests are adequate
- No security concerns

**REQUEST CHANGES IF:**
- Any P0 finding is not fully resolved
- Emergency procedures have gaps or are unclear
- Code has bugs or security issues
- Tests are missing or inadequate
- Documentation is incomplete

**OUTPUT FORMAT:**
Please provide:
1. Summary of findings (1-2 sentences)
2. Specific issues found (if any) with file references
3. Overall recommendation: APPROVE or REQUEST CHANGES
4. Any suggestions for improvement

**ADDITIONAL CONTEXT:**
This PR is blocking production deployment. The audit identified critical missing features like the Guardian kill-switch and emergency override procedures. These must be production-ready before deployment.

Repository: https://github.com/LukhasAI/Lukhas
PR Link: https://github.com/LukhasAI/Lukhas/pull/1100
```

---

## PROMPT 2: Documentation Batch Review (4 PRs)

**Priority:** MEDIUM
**Time:** 15 minutes
**Impact:** Improves project documentation

### Copy everything below the line and paste into https://claude.ai

```
Batch review 4 documentation PRs for LUKHAS repository

**OVERVIEW:**
Review and approve 4 documentation PRs that improve project documentation and workflows. These are all documentation-only changes with no code impact.

**PR #1036: Test Assignment System and Jules Templates**
- Focus: Jules AI automation templates and test assignment workflows
- Check for: Clear instructions, accurate templates, helpful examples
- Files: Likely in docs/jules/ or docs/testing/

**PR #1035: GitHub Issues Audit and MCP Diagnostics**
- Focus: GitHub issue cleanup audit and MCP server diagnostics
- Check for: Accuracy of audit findings, clear diagnostic procedures
- Files: Likely in docs/audits/ or docs/operations/

**PR #1034: Mandatory Worktree Policy**
- Focus: Git worktree usage policy for parallel development
- Check for: Clear policy rationale, easy-to-follow instructions
- Files: Likely CLAUDE.md or docs/development/

**PR #1033: Pre-Launch 2025 Audit**
- Focus: Comprehensive pre-launch audit findings and recommendations
- Check for: Complete audit coverage, actionable recommendations
- Files: Likely in docs/audits/

**REVIEW CHECKLIST FOR EACH PR:**
1. ✅ Documentation is clear and well-organized
2. ✅ Examples are correct and helpful
3. ✅ No factual errors or outdated information
4. ✅ Formatting is consistent (Markdown, headings, lists)
5. ✅ Links work and reference correct files
6. ✅ Instructions are actionable and specific
7. ✅ No sensitive information exposed (API keys, credentials)

**BATCH DECISION:**
If all 4 PRs meet quality standards, approve all with a consolidated comment:

"Batch reviewed PRs #1036, #1035, #1034, #1033. All documentation PRs are:
- ✅ Clear and well-written
- ✅ Factually accurate
- ✅ Properly formatted
- ✅ No security concerns

LGTM - Approved for merge."

If any PR has issues, specify which PR and what needs fixing.

**OUTPUT FORMAT:**
- Overall assessment (approve all / selective approval)
- Any issues found per PR
- Specific recommendations for improvements
```

---

## PROMPT 3: PR #1060 - Dream Commerce Tests (Large Suite)

**Priority:** HIGH
**Time:** 15 minutes
**Impact:** Validates 1,140 lines of test code quality

### Copy everything below the line and paste into https://claude.ai

```
Review PR #1060 "Add Comprehensive Tests for core/bridge/dream_commerce.py"

**PR CONTEXT:**
- Files: +1,140 additions (large test suite)
- Purpose: Comprehensive test coverage for dream commerce integration
- Type: Jules-generated test suite

**REVIEW FOCUS:**

1. **Test Organization** (⚠️ CRITICAL for large suites)
   - Are tests grouped logically (e.g., by functionality, by component)?
   - Is there clear structure (fixtures, test classes, helper functions)?
   - Are test names descriptive and follow conventions?

2. **Coverage Completeness**
   - Does the suite cover major functionality?
   - Are edge cases tested?
   - Is error handling tested?
   - Are there integration tests, not just unit tests?

3. **Test Quality**
   - Are assertions specific and meaningful?
   - Is mocking appropriate (not over-mocked or under-mocked)?
   - Are fixtures reusable and well-designed?
   - Do tests avoid duplication?

4. **Maintainability**
   - Will these tests be easy to update when code changes?
   - Are there any anti-patterns (brittle tests, test interdependencies)?
   - Is the test suite readable and understandable?

5. **Performance**
   - For 1,140 lines of tests, will they run in reasonable time?
   - Are there any obvious performance issues (e.g., sleep statements, redundant setup)?

**DECISION CRITERIA:**

**APPROVE IF:**
- Tests are well-organized and maintainable
- Coverage is comprehensive without being excessive
- Test quality is high (good assertions, appropriate mocking)
- No obvious anti-patterns

**REQUEST CHANGES IF:**
- Tests are disorganized or duplicative
- Coverage has significant gaps
- Tests have quality issues (weak assertions, over-mocking)
- Performance concerns exist

**SUGGEST REFACTORING IF:**
- Test suite could be split into smaller files
- Significant duplication could be reduced with fixtures
- Test organization could be improved

**OUTPUT:**
1. Overall quality assessment (1-5 score, 5 = excellent)
2. Strengths of this test suite
3. Weaknesses or concerns
4. Specific recommendations (if any)
5. Decision: APPROVE / REQUEST CHANGES / SUGGEST REFACTORING
```

---

## PROMPT 4: PR #1051 - Identity Module Security Tests (Critical)

**Priority:** HIGH
**Time:** 15 minutes
**Impact:** Security-sensitive authentication test validation

### Copy everything below the line and paste into https://claude.ai

```
Review PR #1051 "Add comprehensive unit tests for identity modules"

**PR CONTEXT:**
- Purpose: Comprehensive test coverage for identity/authentication modules
- Type: Jules-generated test suite
- Critical area: Security-sensitive authentication code

**SECURITY-FOCUSED REVIEW:**

1. **Authentication Test Coverage**
   - Are all authentication flows tested (login, logout, session management)?
   - Are token validation tests comprehensive?
   - Are permission/authorization tests included?
   - Is multi-factor authentication tested (if applicable)?

2. **Security Test Assertions** (⚠️ CRITICAL)
   - Do tests verify security properties (e.g., tokens expire, sessions invalidate)?
   - Are negative test cases included (invalid tokens, expired sessions)?
   - Are attack scenarios tested (e.g., token tampering, replay attacks)?
   - Do tests check for secure defaults?

3. **Test Data Safety**
   - ⚠️ CHECK: No hardcoded credentials in tests
   - ⚠️ CHECK: No real API keys or secrets
   - ⚠️ CHECK: Test data doesn't expose sensitive patterns
   - Are mocks used appropriately for external auth services?

4. **Identity-Specific Tests**
   - WebAuthn tests (if applicable)
   - JWT generation/validation tests
   - ΛID (Lambda Identity) system tests
   - Session management tests
   - OAuth flow tests (if applicable)

5. **Integration Tests**
   - Do tests cover identity integration with other systems?
   - Are database interactions tested properly?
   - Are API endpoint tests included?

**CRITICAL CHECKS:**
- ⚠️ NO hardcoded secrets or credentials
- ⚠️ Security properties are validated (expiration, invalidation, etc.)
- ⚠️ Attack scenarios are tested
- ⚠️ Proper mocking of external services

**DECISION:**

**APPROVE IF:**
- Security test coverage is comprehensive
- No hardcoded secrets
- Attack scenarios are tested
- Authentication flows are fully covered

**REQUEST CHANGES IF:**
- Security gaps in test coverage
- Hardcoded secrets found
- Missing critical authentication tests
- Weak security assertions

**OUTPUT:**
1. Security assessment (PASS / FAIL / NEEDS IMPROVEMENT)
2. Coverage analysis (authentication flows, attack scenarios)
3. Security issues found (if any)
4. Recommendations for additional security tests
5. Decision: APPROVE / REQUEST CHANGES
```

---

## PROMPT 5: PR #805 - LUKHAS M1 Branch Analysis (Complex)

**Priority:** MEDIUM
**Time:** 20-25 minutes
**Impact:** Resolves long-standing large PR (23 commits, +19,740 lines)

### Copy everything below the line and paste into https://claude.ai

**NOTE:** This prompt is comprehensive. See `/tmp/PROMPT_5_PR_805_ANALYSIS.md` for the full text (too large to display inline).

**Quick Summary:** Analyze PR #805 (M1 branch with 23 commits, +19,740 lines covering Security, Testing, Platform, and Infrastructure enhancements). Provide recommendation: MERGE / SPLIT / CHERRY-PICK / CLOSE with detailed rationale and action plan.

**To use:**
```bash
cat /tmp/PROMPT_5_PR_805_ANALYSIS.md | pbcopy  # macOS - copies to clipboard
# Or: open /tmp/PROMPT_5_PR_805_ANALYSIS.md and copy manually
# Then paste into https://claude.ai
```

---

## 📋 QUICK REFERENCE GUIDE

### How to Use (Step by Step)

1. **Open Claude Code Web:** Go to https://claude.ai
2. **Copy a prompt:** Highlight everything between the ``` marks
3. **Paste into Claude:** Start a new chat and paste
4. **Wait for analysis:** Claude will review the PR
5. **Apply recommendations:** Follow Claude's guidance
6. **Repeat:** Move to next prompt

### Order of Execution (Recommended)

| Order | Prompt | Priority | Time | Why |
|-------|--------|----------|------|-----|
| 1st | **PROMPT 1** (PR #1100) | CRITICAL | 20 min | Production blocker |
| 2nd | **PROMPT 4** (PR #1051) | HIGH | 15 min | Security-critical |
| 3rd | **PROMPT 3** (PR #1060) | HIGH | 15 min | Large test quality |
| 4th | **PROMPT 5** (PR #805) | MEDIUM | 20 min | Complex analysis |
| 5th | **PROMPT 2** (4 doc PRs) | MEDIUM | 15 min | Documentation |

**Total time:** ~85 minutes

---

## 🎯 Expected Outcomes

After completing all 5 prompts:
- ✅ PR #1100: APPROVED or specific changes requested
- ✅ PR #1051: Security assessment complete
- ✅ PR #1060: Quality review complete
- ✅ PR #805: Clear recommendation (merge/split/close)
- ✅ 4 doc PRs: Batch approved or individual feedback

**Total PRs addressed:** 8 PRs

---

## 💡 Tips for ADHD-Friendly Execution

**✅ DO:**
- Complete ONE prompt at a time
- Check off each prompt as you finish
- Take breaks between prompts
- Use the Quick Reference table to track progress

**❌ DON'T:**
- Try to do all prompts at once
- Skip the priority order
- Rush through security reviews
- Forget to apply Claude's recommendations

**Progress Tracker:**
- [ ] PROMPT 1: PR #1100 (Critical)
- [ ] PROMPT 2: 4 Documentation PRs
- [ ] PROMPT 3: PR #1060 (Large tests)
- [ ] PROMPT 4: PR #1051 (Security)
- [ ] PROMPT 5: PR #805 (Complex analysis)

---

**Generated:** 2025-11-08
**Repository:** https://github.com/LukhasAI/Lukhas
**Tool:** Claude Code Web (https://claude.ai)
**Total Prompts:** 5
**Estimated Time:** 85 minutes
