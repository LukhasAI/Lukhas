# LUKHAS TODO System

> **Professional task management for 0.01% excellence**
>
> Organized • Trackable • Agent-Friendly • Human-Readable

---

## 🚀 Quick Start

### For AI Agents

**Before starting ANY work:**

```bash
# 1. Read the rules (MANDATORY)
cat TODO/RULES_FOR_AGENTS.md

# 2. Check current tasks
cat TODO/MASTER_LOG.md

# 3. Check your assigned tasks
cat TODO/by-agent/jules.md        # If you're Jules
cat TODO/by-agent/claude-code.md  # If you're Claude Code
cat TODO/by-agent/codex.md        # If you're Copilot

# 4. Pick a task, update MASTER_LOG, start work
```

### For Humans

```bash
# View all tasks by priority
cat TODO/MASTER_LOG.md

# Quick-drop a task
cp TODO/inbox/_TEMPLATE.md TODO/inbox/$(date +%Y-%m-%d)-my-task.md
# Edit file, then: python scripts/todo/process_inbox.py

# Check system health
python scripts/todo/health_check.py
```

---

## 📁 Directory Structure

```
TODO/
├── README.md                      # You are here
├── MASTER_LOG.md                  # 🔥 SINGLE SOURCE OF TRUTH
├── RULES_FOR_AGENTS.md           # 🚨 MANDATORY reading for agents
│
├── active/                        # Detailed task files (complex tasks only)
│   ├── P0_T20251111001.md        # Priority 0 task details
│   └── P1_T20251111042.md        # Priority 1 task details
│
├── by-agent/                      # Agent-specific task views
│   ├── README.md                  # How to use agent views
│   ├── jules.md                   # Jules' tasks
│   ├── claude-code.md            # Claude Code's tasks
│   ├── codex.md                   # Copilot's tasks
│   └── human.md                   # Human-assigned tasks
│
├── completed/                     # Archived completed tasks
│   ├── 2025-11-11-T20251111001.md # Completed task (with details)
│   └── 2025-11-10-T20251110034.md # Older completed task
│
├── inbox/                         # Quick-drop zone
│   ├── README.md                  # Inbox usage guide
│   ├── _TEMPLATE.md              # Task template (copy this)
│   ├── 2025-11-11-my-task.md     # Unprocessed task
│   └── processed/                 # Archived inbox items
│
├── prompts/                       # Implementation templates
│   ├── FEEDBACK_SYSTEM_PROMPTS.md   # 12 micro-PR prompts
│   ├── MEMORY_AUTH_PROMPTS.md        # 15 micro-PR prompts
│   └── INFRASTRUCTURE_PROMPTS.md     # 10 micro-PR prompts
│
├── context/                       # AI agent context files
│   ├── claude.me                  # Claude-specific context
│   ├── lukhas_context.md         # General LUKHAS context
│   └── gemini.md                  # Gemini-specific context
│
├── archive/                       # Old/obsolete plans
│   └── PHASE_2_SURGICAL_PLAN_2025-10-24.md
│
└── [Reference Files]              # Comprehensive task lists
    ├── AUDIT_TODO_TASKS.md        # 62 audit tasks (detailed)
    ├── AUDIT_TODO_TASKS.json      # Machine-readable version
    ├── AGENT_PENDING_TASKS.md     # Status tracking
    ├── CLAUDE_TASKS.md            # T4 Delta Plan
    ├── LUKHAS_MODULE_TODOS.md     # Module-specific tasks
    ├── T4_CONSCIOUSNESS_ENHANCEMENT_TASKS.md  # Background tasks
    ├── AUDITOR_CHECKLIST.md       # Quality checklist
    └── RUFF_ERROR_ANALYSIS_REPORT.md  # Current linting errors
```

---

## 🎯 Core Concepts

### Single Source of Truth

**MASTER_LOG.md** is the authoritative task list. All other files are:
- **References**: Detailed context (AUDIT_TODO_TASKS.md, CLAUDE_TASKS.md)
- **Views**: Filtered perspectives (by-agent/)
- **Staging**: Temporary holding (inbox/)
- **Archive**: Historical record (completed/, archive/)

### Priority System (T4/0.01% Standards)

| Priority | Name | Timeline | Criteria |
|----------|------|----------|----------|
| **P0** | Critical | <1 hour | System down, security breach, data loss |
| **P1** | High | <1 week | Blocks release, critical bug, high-value feature |
| **P2** | Medium | 2-4 weeks | Important but not blocking, tech debt |
| **P3** | Low | 1+ month | Nice-to-have, polish, research |

---

## 📝 Workflows

### Adding a Task (Quick Method - Inbox)
```bash
cp TODO/inbox/_TEMPLATE.md TODO/inbox/$(date +%Y-%m-%d)-task-name.md
# Edit file, then:
python scripts/todo/process_inbox.py
```

### Completing a Task
```bash
# 1. Update MASTER_LOG.md (mark complete, add PR link)
# 2. Archive: mv TODO/active/P1_T*.md TODO/completed/2025-11-11-T*.md
# 3. Commit changes
```

---

## 🤖 For AI Agents

### MANDATORY
1. Read **RULES_FOR_AGENTS.md** before ANY work
2. Check **MASTER_LOG.md** for duplicates
3. Update MASTER_LOG when adding/completing tasks
4. Link PRs to task IDs

### Agent Specializations
- **CODEX**: Python infrastructure, orchestrator, performance
- **Jules**: CI/CD, observability, security
- **Claude Code**: Testing, documentation, reasoning
- **Copilot**: Refactors, docstrings, mechanical edits

---

## 📊 Key Files

- **[MASTER_LOG.md](MASTER_LOG.md)** - All tasks (single source of truth)
- **[RULES_FOR_AGENTS.md](RULES_FOR_AGENTS.md)** - Mandatory agent rules
- **[inbox/README.md](inbox/README.md)** - Quick-drop usage guide
- **[AUDIT_TODO_TASKS.md](AUDIT_TODO_TASKS.md)** - Detailed 62-task audit

---

**Version**: 1.0 | **Updated**: 2025-11-11 | **Status**: Active
