# START Claude Code Web Session
**Master orchestration prompt for Claude Code Web agents**

---

## 🚀 Quick Start

Copy-paste this entire prompt into Claude Code Web to begin a session:

```
I am Claude Code Web, and I'm starting a new LUKHAS development session.

STEP 1: Read the Master System Prompt
Read file: /Users/agi_dev/LOCAL-REPOS/Lukhas/CLAUDE_CODE_WEB_MASTER_PROMPT.md

This file contains:
- LUKHAS Test Surgeon system prompt (MANDATORY - apply to ALL tasks)
- T4 guidelines (Sam, Dario, Steve, Demis principles)
- Security requirements (90+/100 target from audits)
- 9 stop conditions and escalation rules
- PR templates and artifact requirements

STEP 2: Read the Task-Specific Prompts
Read file: /Users/agi_dev/LOCAL-REPOS/Lukhas/PROMPTS_FOR_CLAUDE_CODE_WEB.md

This file contains:
- Tasks 3-8 (Production API Routes, Parallel Dreams, Drift, Glyphs, Performance Testing)
- Current state summary and context
- Specific implementation instructions for each task

STEP 3: Execute Task Selection
Based on the task prompts file, ask the user which task(s) to execute:
- Task 3: Production API Routes (dreams, drift, glyphs)
- Task 4: Wire Parallel Dreams Feature Flag
- Task 5: Wire Vivox Drift into User Profiles
- Task 6: Create GLYPH Bind Endpoints
- Task 8: Performance and Chaos Testing

STEP 4: Apply LUKHAS Test Surgeon Rules
For EVERY task, follow these rules exactly:
✅ Tests-first (failing test before code)
✅ Draft PRs only (labot + claude:web labels)
✅ No protected files (.lukhas/protected-files.yml)
✅ Deterministic tests (freeze time/seeds, no network)
✅ Artifacts required (junit.xml, coverage.xml, events.ndjson, mutmut)
✅ Security checklist (auth, user isolation, tier access, rate limiting, 6 test types)

STEP 5: Create Worktree for Each Task
MANDATORY: Use git worktree for each task:

```bash
# Example for Task 3
git worktree add ../Lukhas-task3-api-routes -b feat/production-api-routes
cd ../Lukhas-task3-api-routes
# Do work, commit, create PR
```

STEP 6: Execution Guidelines
- ONE task at a time (complete before moving to next)
- Create Draft PR for each task with proper labels
- Attach all required artifacts (junit.xml, coverage.xml, events.ndjson)
- Run guard_patch before pushing
- Run mutmut for tier-1 modules
- Document confidence level (0.0-1.0) and assumptions in PR body

STEP 7: Stop Conditions
STOP immediately and escalate if:
- Task requires editing protected files
- Complex nested types or PQC/crypto changes detected
- Ambiguous requirements need clarification
- Any of the 9 stop conditions from master prompt apply

READY: I have read both files and am ready to execute tasks following LUKHAS Test Surgeon principles.

Which task should I start with? (or specify "all" for sequential execution)
```

---

## 📋 For Manual Task Selection

If you want to execute a specific task directly, use this format:

```
I am Claude Code Web executing Task X for LUKHAS.

1. I have read CLAUDE_CODE_WEB_MASTER_PROMPT.md (Test Surgeon rules + security requirements)
2. I have read PROMPTS_FOR_CLAUDE_CODE_WEB.md (Task X details)
3. I am following T4 principles (Sam/Dario/Steve/Demis alignment)

Task: [Copy specific task prompt from PROMPTS_FOR_CLAUDE_CODE_WEB.md]

Applying LUKHAS Test Surgeon rules:
- Tests-first approach
- Draft PR only
- Worktree: ../Lukhas-taskX-[description]
- Artifacts: junit.xml, coverage.xml, events.ndjson, mutmut report
- Security: auth + user isolation + tier access + rate limiting + 6 test types

Beginning execution...
```

---

## 🎯 Session Goals

**Primary Objective**: Complete remaining Core Wiring tasks (3-8) with:
- 90+/100 security score (vs current 55-70/100)
- 80%+ test coverage
- T4-aligned implementation
- Production-ready Draft PRs

**Key Deliverables per Task**:
1. Code changes (minimal, safe, tests-first)
2. Comprehensive tests (6 types: success, 401, 403, cross-user, 429, 422)
3. CI artifacts (junit.xml, coverage.xml, events.ndjson, mutmut report)
4. Draft PR with proper labels and confidence scoring
5. Documentation updates (if applicable)

---

## 🔗 Document Relationships

```
START_CLAUDE_CODE_WEB_SESSION.md (this file)
    ↓
    ├── CLAUDE_CODE_WEB_MASTER_PROMPT.md (system-level guidance)
    │   ├── LUKHAS Test Surgeon system prompt
    │   ├── T4 guidelines
    │   ├── Security requirements (from audits)
    │   ├── Stop conditions
    │   └── PR templates
    │
    └── PROMPTS_FOR_CLAUDE_CODE_WEB.md (task-specific prompts)
        ├── Task 3: Production API Routes
        ├── Task 4: Parallel Dreams Feature Flag
        ├── Task 5: Vivox Drift Integration
        ├── Task 6: GLYPH Bind Endpoints
        └── Task 8: Performance & Chaos Testing
```

---

## 📊 Success Metrics

Each completed task should achieve:
- ✅ Draft PR created with `labot`, `claude:web`, domain labels
- ✅ All tests pass (pytest + guard_patch + ruff + mypy)
- ✅ Coverage ≥80% for changed modules
- ✅ Mutation score not decreased (tier-1 modules)
- ✅ Security checklist 100% complete
- ✅ Artifacts attached to PR
- ✅ Confidence level documented (0.0-1.0)
- ✅ Rollback plan included

---

## 🚨 Emergency Procedures

**If session gets stuck**:
1. STOP current work
2. Document current state (what was attempted, what failed)
3. Create ADR (Architecture Decision Record) if ambiguity detected
4. Request steward/human decision
5. DO NOT push unverified changes

**If protected files needed**:
1. STOP immediately
2. Create ADR explaining why protected file change is needed
3. Request two-key approval
4. Wait for explicit authorization

**If security gaps detected**:
1. DO NOT proceed with insecure implementation
2. Refer to security patterns in MASTER_PROMPT
3. Apply mandatory patterns (auth, user isolation, tier access)
4. If unclear, escalate to steward

---

## 🎓 Learning Resources

- **Security Audits**: See `docs/audits/` for completed audit reports
  - User ID Integration Audit (score: 55/100)
  - Endocrine System Audit (score: 65/100)
  - User Feedback System Audit (score: 70/100)
- **GPT-5 Pro Review**: See `docs/audits/GPT5_PRO_REVIEW_PROMPT.md` for code review template
- **Architecture Context**: See `claude.me` and `lukhas_context.md` files throughout repo

---

**Prepared by**: Claude Code (Autonomous AI Agent)
**Last Updated**: 2025-11-10
**Purpose**: Master orchestration prompt for starting Claude Code Web sessions
**Usage**: Copy-paste into Claude Code Web to begin task execution with proper context
