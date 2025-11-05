# Quick Issue Assignment - One-Liner Prompts

Use these one-liner prompts to instantly assign any issue to an agent. Just copy, paste, and change the issue number.

---

## 📋 Standard Assignment Prompt (Copy & Customize)

```
Fix ISSUE-XXX from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find ISSUE-XXX section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: ISSUE-XXX". Report when done.
```

---

## 🎯 Copy-Paste Examples (Just Change Number)

### Example 1: Assign ISSUE-009 (MATRIZ Integration)
```
Fix ISSUE-009 from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find ISSUE-009 section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: ISSUE-009". Report when done.
```

### Example 2: Assign ISSUE-008 (Dreams API)
```
Fix ISSUE-008 from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find ISSUE-008 section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: ISSUE-008". Report when done.
```

### Example 3: Assign ISSUE-015 (Security Audit)
```
Fix ISSUE-015 from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find ISSUE-015 section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: ISSUE-015". Report when done.
```

### Example 4: Assign ISSUE-006 (Import Path)
```
Fix ISSUE-006 from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find ISSUE-006 section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: ISSUE-006". Report when done.
```

---

## 🚀 Ultra-Short Format

If you prefer even shorter:

```
Fix ISSUE-XXX: read bug_report.md, follow all steps, commit with T4.
```

(The agent will reference bug_report.md which has all context, commands, and solutions)

---

## 📊 All Available Issues (Quick Reference)

| Priority | Issue | One-Liner |
|----------|-------|-----------|
| 🔴 P1 | ISSUE-006 | `Fix ISSUE-006 from bug_report.md...` |
| 🔴 P1 | ISSUE-007 | `Fix ISSUE-007 from bug_report.md...` |
| 🔴 P1 | ISSUE-008 | `Fix ISSUE-008 from bug_report.md...` |
| 🔴 P1 | ISSUE-009 | `Fix ISSUE-009 from bug_report.md...` |
| 🔴 P1 | ISSUE-010 | `Fix ISSUE-010 from bug_report.md...` |
| 🔴 P1 | ISSUE-011 | `Fix ISSUE-011 from bug_report.md...` |
| 🔴 P1 | ISSUE-012 | `Fix ISSUE-012 from bug_report.md...` |
| 🔴 P1 | ISSUE-013 | `Fix ISSUE-013 from bug_report.md...` |
| 🔴 P1 | ISSUE-014 | `Fix ISSUE-014 from bug_report.md...` |
| 🔴 P1 | ISSUE-015 | `Fix ISSUE-015 from bug_report.md...` |
| 🟡 P2 | ISSUE-001 | `Fix ISSUE-001 from bug_report.md...` |
| 🟡 P2 | ISSUE-002 | `Fix ISSUE-002 from bug_report.md...` |
| 🟡 P2 | ISSUE-003 | `Fix ISSUE-003 from bug_report.md...` |
| 🟡 P2 | ISSUE-016 | `Fix ISSUE-016 from bug_report.md...` |
| 🟡 P2 | ISSUE-017 | `Fix ISSUE-017 from bug_report.md...` |
| 🟡 P2 | ISSUE-018 | `Fix ISSUE-018 from bug_report.md...` |
| 🟡 P2 | ISSUE-019 | `Fix ISSUE-019 from bug_report.md...` |
| 🟡 P2 | ISSUE-020 | `Fix ISSUE-020 from bug_report.md...` |
| 🟢 P3 | ISSUE-005 | `Fix ISSUE-005 from bug_report.md...` |
| 🟢 P3 | ISSUE-021 | `Fix ISSUE-021 from bug_report.md...` |
| 🟢 P3 | ISSUE-022 | `Fix ISSUE-022 from bug_report.md...` |
| 🟢 P3 | ISSUE-023 | `Fix ISSUE-023 from bug_report.md...` |
| 🟢 P3 | ISSUE-024 | `Fix ISSUE-024 from bug_report.md...` |
| 🟢 P3 | ISSUE-025 | `Fix ISSUE-025 from bug_report.md...` |

---

## 💡 Why This Works

The bug_report.md contains everything the agent needs:
- ✅ Complete issue description
- ✅ Agent context (which files to read)
- ✅ Quick Start commands (reproduction steps)
- ✅ Proposed solution (implementation guide)
- ✅ Validation commands (testing steps)
- ✅ Architecture rules and constraints

By referencing bug_report.md, the agent gets:
1. 📍 Navigation to correct directories
2. 📚 Context files to read first
3. 🔧 Exact commands to reproduce
4. 💡 Solution approach
5. ✅ Validation steps
6. 📝 Commit format requirements

---

## 🎯 Recommended Assignment Order (by Priority)

### Week 1: Critical Infrastructure
1. `Fix ISSUE-007 from bug_report.md...` (Lane guard - enables validation)
2. `Fix ISSUE-006 from bug_report.md...` (Import paths - unblocks 12+ files)
3. `Fix ISSUE-010 from bug_report.md...` (Auth - security critical)

### Week 1: Core API
4. `Fix ISSUE-013 from bug_report.md...` (Error envelopes - affects all endpoints)
5. `Fix ISSUE-009 from bug_report.md...` (MATRIZ - core engine)
6. `Fix ISSUE-012 from bug_report.md...` (Responses API - primary endpoint)

### Week 2: Additional APIs
7. `Fix ISSUE-008 from bug_report.md...` (Dreams API)
8. `Fix ISSUE-011 from bug_report.md...` (Models API)
9. `Fix ISSUE-016 from bug_report.md...` (Embeddings API)

### Week 2: Infrastructure & Security
10. `Fix ISSUE-014 from bug_report.md...` (lz4 dependency)
11. `Fix ISSUE-015 from bug_report.md...` (Security audit - 430 files)
12. `Fix ISSUE-017 from bug_report.md...` (Rate limiting)

### Week 3: Observability & Testing
13. `Fix ISSUE-018 from bug_report.md...` (Metrics/health)
14. `Fix ISSUE-001 from bug_report.md...` (MCP tests)

### Week 4: Refinement
15. Remaining P2 and P3 issues as needed

---

## 📝 Template for Creating GitHub Issues

If you want to create GitHub issues from these:

```markdown
**Title**: {Issue Title from bug_report.md}

**Priority**: P1/P2/P3

**Description**:
See `/Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md` section for {ISSUE_NUMBER}

**Assignment**:
```
Fix {ISSUE_NUMBER} from bug_report.md. Read /Users/agi_dev/LOCAL-REPOS/Lukhas/bug_report.md, find {ISSUE_NUMBER} section, read all context files listed in "Agent Context", follow "Quick Start" commands to reproduce, implement "Proposed Solution", run "Validation" commands, ensure all tests pass, commit with T4 format including "Closes: {ISSUE_NUMBER}". Report when done.
```

**Labels**: bug, {priority}, {component}
```
