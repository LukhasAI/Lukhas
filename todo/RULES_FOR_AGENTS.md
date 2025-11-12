# Mandatory Rules for All AI Agents Working with TODO/

> **🚨 CRITICAL: Every AI agent (Claude Code, Jules, Copilot, etc.) MUST follow these rules**
>
> Failure to follow these rules will result in task conflicts, lost work, and confusion.

---

## Table of Contents

1. [When Adding New TODO](#when-adding-new-todo)
2. [When Completing TODO](#when-completing-todo)
3. [When Changing Priority](#when-changing-priority)
4. [Priority Criteria (T4/0.01% Standards)](#priority-criteria)
5. [Task ID Format](#task-id-format)
6. [Effort Estimation](#effort-estimation)
7. [Automation Hooks](#automation-hooks)
8. [Emergency Procedures](#emergency-procedures)

---

## When Adding New TODO

### 🚨 MANDATORY STEPS (Do NOT skip):

1. **Check for duplicates FIRST**
   ```bash
   # Search MASTER_LOG for similar tasks
   grep -i "your task description" TODO/MASTER_LOG.md
   ```

2. **Generate unique ID**: `T{YYYY}{MM}{DD}{sequential}`
   - Example: `T20251111001` (first task on Nov 11, 2025)
   - Sequential number resets daily (001-999)
   - Check MASTER_LOG.md for last used number today

3. **Assign Priority**: P0/P1/P2/P3 using criteria below
   - **P0 (Critical)**: System down, security breach, data loss, blocks all work
   - **P1 (High)**: Blocks next release, high-value feature, critical bug
   - **P2 (Medium)**: Important but not blocking, tech debt, refactoring
   - **P3 (Low)**: Nice-to-have, polish, future work, research

4. **Estimate Effort**: S/M/L
   - **S (Small)**: <4 hours, single file, straightforward
   - **M (Medium)**: 4-16 hours, multiple files, moderate complexity
   - **L (Large)**: >16 hours, system-wide, high complexity

5. **Update MASTER_LOG.md**: Add to appropriate priority section
   ```markdown
   | T20251111001 | Fix Guardian policy bug | Jules | IN_PROGRESS | M | #1234 |
   ```

6. **Create detail file** (if complex): `active/P{N}_{TASK_ID}.md`
   - Use `/TODO/inbox/_TEMPLATE.md` as starting point
   - Include context, acceptance criteria, affected files

7. **Assign Owner**: codex|jules|claude-code|human
   - Consider agent strengths (see by-agent/README.md)

8. **Update stats at top of MASTER_LOG.md**:
   ```markdown
   **Total Tasks**: 157
   **Completed**: 89 | **Active**: 45 | **Blocked**: 3
   ```

9. **Commit your changes**:
   ```bash
   git add TODO/MASTER_LOG.md TODO/active/P1_T20251111001.md
   git commit -m "feat(todo): add Guardian policy bug fix task (T20251111001)"
   ```

### Quick Add (for simple tasks):

Can use inbox system for quick drops, then process later:

```bash
cp TODO/inbox/_TEMPLATE.md TODO/inbox/$(date +%Y-%m-%d)-task-name.md
# Edit file
# Run: python scripts/todo/process_inbox.py
```

---

## When Completing TODO

### 🚨 MANDATORY STEPS:

1. **Mark complete in MASTER_LOG.md**:
   - Move row from priority section to "Completed (Last 30 Days)" section
   - Add completion date

2. **Add PR link**:
   ```markdown
   | T20251111001 | Fix Guardian policy bug | Jules | ✅ MERGED | M | #1234 | 2025-11-11 |
   ```

3. **Archive detail file** (if exists):
   ```bash
   mv TODO/active/P1_T20251111001.md TODO/completed/2025-11-11-T20251111001.md
   ```

4. **Update stats** at top of MASTER_LOG.md:
   - Decrement Active count
   - Increment Completed count

5. **Commit**:
   ```bash
   git add TODO/MASTER_LOG.md TODO/completed/
   git commit -m "chore(todo): complete Guardian policy bug fix (T20251111001)"
   ```

---

## When Changing Priority

### 🚨 MANDATORY STEPS:

1. **Justify in commit message**:
   ```
   chore(todo): escalate task T20251111001 from P2 → P0

   Reason: Discovered this bug is blocking production deployment.
   Impact: Cannot release v2.0 until fixed.
   ```

2. **Update MASTER_LOG.md**: Move between priority sections

3. **Notify team** (if collaborative):
   - Comment in relevant PR/Issue
   - Post in team chat if urgent

4. **Rename detail file** (if exists):
   ```bash
   mv TODO/active/P2_T20251111001.md TODO/active/P0_T20251111001.md
   ```

---

## Priority Criteria (T4/0.01% Standards)

### P0 (Critical) - Drop Everything

**Criteria**:
- System down or unstable
- Security breach or vulnerability
- Data loss or corruption risk
- Blocks ALL other work
- Legal/compliance violation

**Examples**:
- ✅ `T20251111001 | Production API returning 500 errors`
- ✅ `T20251111002 | SQL injection vulnerability in auth endpoint`
- ✅ `T20251111003 | User data exposed in logs (GDPR violation)`

**Response Time**: Immediate (within 1 hour)

### P1 (High) - This Sprint

**Criteria**:
- Blocks next release
- High-value feature
- Critical bug (not system-down)
- Significant technical debt
- User-facing issue

**Examples**:
- ✅ `T20251111004 | Guardian not enforcing policies (major feature broken)`
- ✅ `T20251111005 | Memory leak causing performance degradation`
- ✅ `T20251111006 | Add OAuth support (required for v2.0 release)`

**Response Time**: This week (within 7 days)

### P2 (Medium) - Next Sprint

**Criteria**:
- Important but not blocking
- Tech debt that should be addressed
- Refactoring for maintainability
- Performance optimization
- Documentation gaps

**Examples**:
- ✅ `T20251111007 | Refactor circular imports in core/`
- ✅ `T20251111008 | Add integration tests for MATRIZ engine`
- ✅ `T20251111009 | Document ΛiD authentication flow`

**Response Time**: Next 2-4 weeks

### P3 (Low) - Backlog

**Criteria**:
- Nice-to-have features
- Polish and UX improvements
- Future work / research
- Low-impact bugs
- Experimental features

**Examples**:
- ✅ `T20251111010 | Add dark mode to admin UI`
- ✅ `T20251111011 | Research quantum-inspired algorithms for consciousness`
- ✅ `T20251111012 | Improve CLI help text formatting`

**Response Time**: When capacity allows (months)

---

## Task ID Format

### Format: `T{YYYY}{MM}{DD}{sequential}`

### Examples:
- `T20251111001` - First task on Nov 11, 2025
- `T20251111042` - 42nd task on Nov 11, 2025
- `T20251112001` - First task on Nov 12, 2025

### Rules:
1. **YYYY**: 4-digit year
2. **MM**: 2-digit month (01-12)
3. **DD**: 2-digit day (01-31)
4. **Sequential**: 3-digit daily counter (001-999)
5. **Reset daily**: Counter starts at 001 each day
6. **Never reuse IDs**: Even if task is deleted

### Finding Next ID:
```bash
# Find last task ID for today
grep "T$(date +%Y%m%d)" TODO/MASTER_LOG.md | tail -1

# Example output: | T20251111042 | Some task | ...
# Next ID: T20251111043
```

---

## Effort Estimation

### S (Small) - < 4 hours

**Characteristics**:
- Single file changes
- Straightforward logic
- Well-defined scope
- No dependencies

**Examples**:
- Add a new config parameter
- Fix typo in documentation
- Add logging statement
- Update error message

### M (Medium) - 4-16 hours

**Characteristics**:
- Multiple file changes
- Moderate complexity
- Some dependencies
- Requires testing

**Examples**:
- Add new API endpoint
- Refactor module structure
- Implement feature flag
- Add integration tests

### L (Large) - > 16 hours

**Characteristics**:
- System-wide changes
- High complexity
- Many dependencies
- Extensive testing needed
- May need to be broken down

**Examples**:
- Redesign authentication system
- Implement new consciousness module
- Major refactoring across codebase
- Complete feature with frontend + backend

**⚠️ Warning**: L tasks should usually be broken into smaller tasks (M or S)

---

## Automation Hooks

### Pre-commit Hook

Validates MASTER_LOG.md before commit:

```bash
# Located at: .git/hooks/pre-commit
python scripts/todo/validate_master_log.py

# Checks:
# - All IDs are unique
# - Totals match counts
# - No duplicate tasks
# - Valid priority levels
# - Valid status values
```

### PR Merge Hook

Auto-updates MASTER_LOG.md when PR is merged:

```yaml
# Located at: .github/workflows/todo-sync.yml
# Triggers on: pull_request (closed + merged)
# Actions:
#   1. Parse PR title for task ID (e.g., "fix(guardian): resolve T20251111001")
#   2. Mark task as completed in MASTER_LOG.md
#   3. Move detail file to completed/
#   4. Update stats
#   5. Commit changes
```

### GitHub Issues Sync

Bi-directional sync with GitHub Issues:

```bash
# Sync P0/P1 tasks to GitHub Issues
python scripts/todo/sync_github_issues.py --push

# Update MASTER_LOG from closed Issues
python scripts/todo/sync_github_issues.py --pull
```

---

## Emergency Procedures

### Corrupted MASTER_LOG.md

1. **Don't panic** - it's under version control
2. **Restore from backup**:
   ```bash
   git checkout HEAD~1 TODO/MASTER_LOG.md
   ```
3. **Or restore from last good commit**:
   ```bash
   git log --oneline TODO/MASTER_LOG.md  # Find last good commit
   git checkout <commit-hash> TODO/MASTER_LOG.md
   ```
4. **Validate**:
   ```bash
   python scripts/todo/validate_master_log.py
   ```

### Duplicate Task IDs

1. **Find duplicates**:
   ```bash
   python scripts/todo/find_duplicate_ids.py
   ```
2. **Assign new ID to newer task**:
   - Keep older task's ID
   - Generate new ID for newer task
   - Update all references
3. **Commit fix**:
   ```bash
   git commit -m "fix(todo): resolve duplicate task ID T20251111042"
   ```

### Conflicting Priorities

If two agents assign different priorities to same task:

1. **Higher priority wins** (P0 > P1 > P2 > P3)
2. **If both same level**: Discuss in PR comments
3. **If urgent**: Escalate to human for decision

### Lost Work

If work was done but not tracked:

1. **Add task retroactively**:
   - Use completion date for task ID
   - Mark as completed immediately
   - Link to PR
2. **Document in "Completed" section**
3. **Learn**: Always create task BEFORE starting work

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│  QUICK REFERENCE: TODO System                               │
├──────────────────────────────────────────────────────────────┤
│  ADD TASK:                                                   │
│    1. Check for duplicates                                   │
│    2. Generate ID: T{YYYY}{MM}{DD}{###}                     │
│    3. Assign priority (P0/P1/P2/P3)                         │
│    4. Estimate effort (S/M/L)                               │
│    5. Update MASTER_LOG.md                                   │
│    6. Update stats                                           │
│    7. Commit                                                 │
│                                                              │
│  COMPLETE TASK:                                              │
│    1. Mark complete in MASTER_LOG.md                        │
│    2. Add PR link                                            │
│    3. Archive detail file                                    │
│    4. Update stats                                           │
│    5. Commit                                                 │
│                                                              │
│  PRIORITY LEVELS:                                            │
│    P0 = Critical (drop everything, <1 hour)                 │
│    P1 = High (this week, <7 days)                           │
│    P2 = Medium (next sprint, 2-4 weeks)                     │
│    P3 = Low (backlog, months)                               │
│                                                              │
│  EFFORT LEVELS:                                              │
│    S = Small (<4 hours, single file)                        │
│    M = Medium (4-16 hours, multiple files)                  │
│    L = Large (>16 hours, system-wide)                       │
│                                                              │
│  FILES:                                                      │
│    TODO/MASTER_LOG.md         - Single source of truth      │
│    TODO/RULES_FOR_AGENTS.md   - This file (read it!)       │
│    TODO/active/               - Detailed task files         │
│    TODO/by-agent/             - Agent-specific views        │
│    TODO/inbox/                - Quick drop zone             │
└──────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Status**: ACTIVE - All agents must follow

**Maintained by**: LUKHAS AI Team
**Questions?**: Create issue with label `question:todo-system`
