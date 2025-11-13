# Agent Task Assignment Template

## Quick Assignment Format

Use this template to assign any issue from bug_report.md to an agent. Simply replace `{ISSUE_NUMBER}` with the desired issue (e.g., ISSUE-006, ISSUE-009, etc.).

---

## 🎯 AGENT TASK: Fix {ISSUE_NUMBER}

### Task Overview

You are assigned to resolve **{ISSUE_NUMBER}** from the LUKHAS bug report.

### Step 1: Read the Bug Report

**CRITICAL - Read this file first:**
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
cat bug_report.md
```

Find the section for **{ISSUE_NUMBER}** and read:
- Description
- Agent Context (context files to read)
- Files Affected
- Root Cause
- Proposed Solution
- Quick Start commands
- Validation steps

### Step 2: Read Required Context Files

Before writing any code, read ALL context files listed in the "Agent Context" section of {ISSUE_NUMBER}. These typically include:

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` (master context)
- Lane-specific context files (candidate/claude.me, lukhas/claude.me, etc.)
- Component-specific documentation

**Command:**
```bash
# Read master context
cat /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me

# Read additional context files listed in the issue
# (paths will be in the "Agent Context" section)
```

### Step 3: Understand Architecture Rules

Review these critical rules from bug_report.md:

**Lane-Based Development:**
- `candidate/` → Experimental, imports from `core/` and `matriz/` ONLY
- `lukhas/` → Production, imports from `core/`, `matriz/`, `universal_language/`
- **FORBIDDEN**: `candidate/` importing from `lukhas/`

**Quality Thresholds:**
- Test Coverage: 75%+ for production promotion
- Syntax Health: >95% files must compile
- Security: 0 hardcoded secrets
- Lane Violations: 0

### Step 4: Reproduce the Issue

Use the "Quick Start for Agents" commands from {ISSUE_NUMBER} to reproduce the problem.

Typical commands:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Run failing tests (specific command in bug report)
pytest tests/path/to/test.py -v

# Check current state
# (issue-specific commands in bug report)
```

**Document what you observe** - confirm the issue matches the description.

### Step 5: Implement the Fix

Follow the "Proposed Solution" from {ISSUE_NUMBER}.

**Important:**
- Follow lane isolation rules
- Write/update tests for your fix
- Maintain or improve test coverage
- No hardcoded secrets
- Add proper error handling
- Update documentation if needed

### Step 6: Validate the Fix

Use the "Validation" commands from {ISSUE_NUMBER}.

**Minimum validation required:**
```bash
# Run tests for the fixed component
pytest tests/path/to/test.py -v

# Run smoke tests
make smoke

# Check lane boundaries (if tool working)
make lane-guard

# Run relevant test tier
make test-tier1
```

**All tests must pass** before proceeding to commit.

### Step 7: Commit with T4 Standards

Use this commit message format:

```bash
git add .
git commit -m "$(cat <<'EOF'
<type>(<scope>): <imperative subject ≤72>

Problem:
- Issue description from {ISSUE_NUMBER}
- Impact on system (test failures, security, etc.)

Solution:
- Specific changes made
- Why this approach was chosen

Impact:
- What changed and benefits
- Test results (X tests passing)
- Coverage improvement if applicable

Validation:
- Tests passing: [list key tests]
- No lane violations
- No security issues introduced

Closes: {ISSUE_NUMBER}

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Type options**: fix, feat, docs, refactor, test, security, perf

**Scope options**:
- API layer: api, endpoints, middleware
- Core systems: core, matriz, identity, memory, governance
- Infrastructure: ops, build, ci, testing, security
- Documentation: docs, testing

### Success Criteria

✅ **Issue is resolved when:**
1. Root cause addressed
2. All tests passing (including previously failing ones)
3. No new test failures introduced
4. No lane boundary violations
5. No security issues introduced
6. Code follows LUKHAS architecture patterns
7. Documentation updated if needed
8. Committed with T4-compliant message
9. Changes pushed to main branch

### Reporting

After completing {ISSUE_NUMBER}, provide a summary:

**Issue**: {ISSUE_NUMBER}
**Status**: ✅ RESOLVED / ⚠️ BLOCKED / ❌ FAILED

**Summary**:
- What was broken: [brief description]
- What was fixed: [brief description]
- Tests affected: X tests now passing
- Files modified: [list key files]
- Commit SHA: [commit hash]

**Blockers** (if any):
- [List any blockers encountered]

**Recommendations**:
- [Any follow-up work or related issues discovered]

---

## 📚 Reference

- **Bug Report**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md`
- **Master Context**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me`
- **Known Issues**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/KNOWN_ISSUES.md`
- **Commit Standards**: See CLAUDE.md (T4 Minimal Standard)

---

## 🎯 Quick Reference: All Available Issues

### HIGH PRIORITY (P1) - Fix Immediately
- ISSUE-006: governance.schema_registry import broken
- ISSUE-007: Lane guard tool missing
- ISSUE-008: Dreams API missing (10 tests)
- ISSUE-009: MATRIZ-API integration (10 tests)
- ISSUE-010: Auth middleware broken (15+ tests)
- ISSUE-011: Models API metadata (7 tests)
- ISSUE-012: Responses API missing (15 tests)
- ISSUE-013: Error envelope format (20+ tests)
- ISSUE-014: Missing lz4 dependency
- ISSUE-015: Security audit (430 files)

### MEDIUM PRIORITY (P2) - Fix This Sprint
- ISSUE-001: MCP server tests (6 tests)
- ISSUE-002: Consent validation message
- ISSUE-003: Constitutional AI thresholds
- ISSUE-016: Embeddings API auth (4 tests)
- ISSUE-017: Rate limiting (5 tests)
- ISSUE-018: Metrics/observability (5 tests)
- ISSUE-019: Circular imports (45 files)
- ISSUE-020: Makefile duplicates

### LOW PRIORITY (P3) - Next Sprint
- ISSUE-005: Bio-symbolic coherence
- ISSUE-021: Memory indexing (17 tests skipped)
- ISSUE-022: Technical debt (1,624 TODOs)
- ISSUE-023: Consciousness tests (30 skipped)
- ISSUE-024: Dependencies documentation
- ISSUE-025: Python binary path

---

## Example Usage

To assign ISSUE-009 to an agent:

```
You are assigned to resolve ISSUE-009 from the LUKHAS bug report.

[Follow the 7 steps above, reading bug_report.md for ISSUE-009 specifics]
```

To assign ISSUE-015:

```
You are assigned to resolve ISSUE-015 from the LUKHAS bug report.

[Follow the 7 steps above, reading bug_report.md for ISSUE-015 specifics]
```

The agent will automatically:
1. Read bug_report.md and find ISSUE-015 details
2. Read required context files listed in the issue
3. Follow the Quick Start commands
4. Implement the Proposed Solution
5. Run the Validation commands
6. Commit with proper T4 format
