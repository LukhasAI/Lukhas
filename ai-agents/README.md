# AI Agents Workspace

> **External AI agent coordination and documentation for LUKHAS development**
>
> Last Updated: 2025-11-11

---

## 🎯 Purpose

This directory contains documentation, session tracking, and coordination materials for **external AI agents** working on LUKHAS development:

- **Claude Code** (Anthropic) - Code editing, testing, documentation
- **Jules** (Google) - Autonomous PR generation, test creation
- **GitHub Copilot** - Code completion and suggestions
- **Other agents** - Future AI development tools

**⚠️ Important**: This is for **external AI agent documentation ONLY**. For LUKHAS's internal agent system code, see [`../agent/`](../agent/).

---

## 📂 Directory Structure

```
ai-agents/
├── README.md              # This file - workspace overview
├── claude-code/           # Claude Code sessions and context
│   ├── sessions/         # Session tracking
│   ├── context/          # Claude-specific context files
│   └── completed/        # Archived completed sessions
├── jules/                 # Jules session tracking
│   ├── active/           # Active Jules sessions
│   ├── completed/        # Completed PRs and sessions
│   └── templates/        # Jules prompt templates
├── copilot/               # GitHub Copilot tasks
│   ├── suggestions/      # Copilot-generated suggestions
│   └── accepted/         # Accepted and merged suggestions
└── coordination/          # Multi-agent coordination
    ├── handoffs/         # Agent-to-agent handoff docs
    ├── conflicts/        # Conflict resolution
    └── workflows/        # Multi-agent workflows
```

---

## 🚀 Quick Start

### For AI Agents

**Before starting any LUKHAS work:**

1. **Read the rules**: `cat TODO/RULES_FOR_AGENTS.md`
2. **Check master log**: `cat TODO/MASTER_LOG.md`
3. **Check your tasks**: `cat TODO/by-agent/{your-agent}.md`
4. **Review context**: Read relevant `agent/context/` files for LUKHAS architecture

### For Humans

**Track AI agent work:**
- Claude Code sessions in `claude-code/sessions/`
- Jules PRs in `jules/active/` and `jules/completed/`
- Multi-agent coordination in `coordination/workflows/`

---

## 🤖 Agent Profiles

### Claude Code
**Specialty**: Code editing, testing, documentation, analysis
**Use for**: Complex refactoring, test authoring, documentation updates, code review
**Session tracking**: `claude-code/sessions/`
**Context files**: `agent/context/claude.me`

### Jules
**Specialty**: Autonomous PR generation, comprehensive test creation
**Use for**: Large test suites, bug fixes, coverage improvements
**Quota**: 100 sessions/day (MUST USE THEM ALL)
**API**: See [JULES_API_COMPLETE_REFERENCE.md](../JULES_API_COMPLETE_REFERENCE.md)
**Session tracking**: `jules/active/`

### GitHub Copilot
**Specialty**: Code completion, inline suggestions, boilerplate
**Use for**: Repetitive code, mechanical edits, docstrings
**Tracking**: `copilot/suggestions/`

---

## 📋 Agent Task Assignment

### CODEX (Deep System Infrastructure) - 19 tasks
**Focus**: Python infrastructure, registries, orchestrator, performance
**Priority tasks**: Guardian DSL enforcement, MATRIZ nodes, orchestrator timeouts
**View tasks**: `TODO/by-agent/codex.md`

### Jules (DevOps/Observability) - 16 tasks
**Focus**: CI/CD, observability, security, monitoring
**Priority tasks**: Guardian rollout, secret scanning, OpenTelemetry tracing
**View tasks**: `TODO/by-agent/jules.md`

### Claude Code (Testing/Documentation) - 17 tasks
**Focus**: Test authoring, DSL validation, documentation, edge cases
**Priority tasks**: Safety tag tests, chaos testing, incident response plans
**View tasks**: `TODO/by-agent/claude-code.md`

### Copilot (Mechanical Edits) - 5 tasks
**Focus**: Repetitive edits, docstrings, cleanup
**Priority tasks**: Orchestrator documentation, API docs, context updates
**View tasks**: `TODO/by-agent/copilot.md`

---

## 🔄 Workflows

### Single Agent Workflow

1. **Pick task** from `TODO/by-agent/{your-agent}.md`
2. **Read context** from `agent/context/` for domain knowledge
3. **Update MASTER_LOG** to mark task `IN_PROGRESS`
4. **Complete work** following LUKHAS standards
5. **Create PR** linking to task ID (e.g., "fix(guardian): resolve T20251111001")
6. **Update MASTER_LOG** to mark task `COMPLETED` with PR link

### Multi-Agent Handoff

When handing off work between agents:

1. **Document handoff** in `coordination/handoffs/YYYY-MM-DD-{task-id}.md`
2. **Update task owner** in `TODO/MASTER_LOG.md`
3. **Provide context**: Include what was done, what remains, any gotchas
4. **Link resources**: Previous PRs, relevant docs, test results

**Template**: Use `coordination/handoffs/_TEMPLATE.md`

### Conflict Resolution

When agents have conflicting changes:

1. **Document conflict** in `coordination/conflicts/YYYY-MM-DD-{description}.md`
2. **Analyze differences**: What each agent changed and why
3. **Determine resolution**: Merge, rebase, or escalate to human
4. **Update affected tasks**: Reflect resolution in MASTER_LOG

---

## 📊 Session Tracking

### Claude Code Sessions

**Directory**: `claude-code/sessions/`

**File naming**: `YYYY-MM-DD-{session-name}.md`

**Template**:
```markdown
# Claude Code Session: {Task Description}

**Date**: YYYY-MM-DD
**Task ID**: T20251111001
**Agent**: Claude Code
**Status**: In Progress | Completed | Blocked

## Objective
[What this session aims to accomplish]

## Files Modified
- path/to/file1.py
- path/to/file2.py

## Changes Made
[Summary of changes]

## Next Steps
[What remains to be done]
```

### Jules Sessions

**Directory**: `jules/active/` → `jules/completed/` when merged

**Tracking**: Use Jules API scripts in `scripts/`
- `list_all_jules_sessions.py` - List all sessions
- `get_jules_session_activities.py` - Inspect session details
- `send_jules_message.py` - Send feedback to Jules
- `approve_waiting_jules_plans.py` - Approve plans

**File naming**: `jules-{session-id}.md`

---

## 🛡️ Rules and Standards

### Mandatory for All Agents

1. **Read RULES_FOR_AGENTS.md** before any work
2. **Update MASTER_LOG** when picking up or completing tasks
3. **Follow commit standards** from `CLAUDE.md`
4. **Respect lane boundaries** (candidate/core/lukhas)
5. **Test before committing** (make test, make lint)
6. **Link PRs to task IDs** in commit messages

### Jules-Specific Rules

- **Daily quota**: MUST use all 100 sessions/day (they don't roll over)
- **Approve plans programmatically** for non-critical tasks
- **Inspect activities** when sessions show COMPLETED but have questions
- **Respond immediately** to waiting sessions
- **Standard guidance**: Mock problematic imports, follow LUKHAS lane architecture

### Claude Code-Specific Rules

- **Use worktrees** for all parallel tasks (see CLAUDE.md)
- **Read context files** before editing any directory
- **Maintain test coverage** 75%+ for production lane
- **Document architecture** decisions in relevant READMEs

---

## 📈 Metrics and Reporting

### Agent Productivity

Track in `coordination/metrics/`:
- Tasks completed per agent
- Average completion time
- PR merge rate
- Test coverage improvements

### Session Analytics

Monitor:
- Claude Code session duration
- Jules session success rate (plan → PR → merge)
- Copilot suggestion acceptance rate
- Multi-agent handoff efficiency

---

## 🔗 Related Documentation

### LUKHAS Documentation
- **[TODO/MASTER_LOG.md](../TODO/MASTER_LOG.md)** - All active tasks
- **[TODO/RULES_FOR_AGENTS.md](../TODO/RULES_FOR_AGENTS.md)** - Mandatory agent rules
- **[agent/README.md](../agent/README.md)** - LUKHAS internal agent system
- **[CLAUDE.md](../CLAUDE.md)** - Project-wide Claude Code instructions

### Jules Documentation
- **[JULES_API_COMPLETE_REFERENCE.md](../JULES_API_COMPLETE_REFERENCE.md)** - Full API docs
- **[JULES_QUICK_REFERENCE.md](../JULES_QUICK_REFERENCE.md)** - Essential commands
- **[JULES_WAITING_SESSIONS.md](../JULES_WAITING_SESSIONS.md)** - Handle waiting sessions

### Architecture Context
- **[agent/context/claude.me](../agent/context/claude.me)** - Claude Code context
- **[agent/context/lukhas_context.md](../agent/context/lukhas_context.md)** - General LUKHAS context
- **[agent/context/gemini.md](../agent/context/gemini.md)** - Gemini-specific context

---

## 🆘 Troubleshooting

### "Where do I find my tasks?"
`cat TODO/by-agent/{your-agent}.md`

### "How do I know what to work on next?"
Check `TODO/MASTER_LOG.md` P0 and P1 sections, pick highest priority unassigned task

### "I completed a task, now what?"
1. Mark completed in MASTER_LOG with PR link
2. Archive session notes to appropriate completed/ directory
3. Pick next task

### "Multiple agents working on same file?"
Use `coordination/conflicts/` to document and resolve

### "Jules session stuck waiting?"
Run `python3 scripts/get_jules_session_activities.py <session-id>` to see what Jules is asking for

---

## 🤝 Contributing

When adding new AI agents to LUKHAS workflow:

1. Create subdirectory: `ai-agents/{agent-name}/`
2. Add agent profile to this README
3. Create task view: `TODO/by-agent/{agent-name}.md`
4. Document specialty and best-use cases
5. Add to coordination workflows

---

**Version**: 1.0
**Last Updated**: 2025-11-11
**Maintained by**: LUKHAS AI Team + all AI agents
**Questions?**: Create issue with label `question:ai-agents`
