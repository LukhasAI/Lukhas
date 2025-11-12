# TODO by Agent Views

> **Agent-specific task views from MASTER_LOG.md**
>
> Last Updated: 2025-11-11

---

## Purpose

This directory contains **auto-generated** task views for each AI agent working on LUKHAS.

**⚠️ DO NOT EDIT THESE FILES MANUALLY**

These files are automatically synced from `TODO/MASTER_LOG.md` using:

```bash
python3 scripts/todo/sync_agents.py
```

---

## Agent Views

| Agent | File | Tasks | Specialty |
|-------|------|-------|-----------|
| **CODEX** | [codex.md](codex.md) | 19 | Python infrastructure, orchestrator, performance |
| **Jules** | [jules.md](jules.md) | 16 | CI/CD, observability, security, monitoring |
| **Claude Code** | [claude-code.md](claude-code.md) | 18 | Testing, documentation, DSL validation |
| **Human** | [human.md](human.md) | - | Strategic decisions, architecture review |

---

## How to Use

### For AI Agents

1. **Check your task list**: `cat TODO/by-agent/{your-agent}.md`
2. **Pick highest priority task**: Start with P0, then P1
3. **Read full details**: Check `TODO/MASTER_LOG.md` for complete context
4. **Update status**: Mark task `IN_PROGRESS` in MASTER_LOG
5. **Complete work**: Follow LUKHAS standards
6. **Update completion**: Mark `COMPLETED` with PR link in MASTER_LOG
7. **Sync views**: Run `python3 scripts/todo/sync_agents.py`

### For Humans

1. **Review agent workload**: Check task distribution across agents
2. **Assign tasks**: Add new tasks to MASTER_LOG with appropriate owner
3. **Monitor progress**: Track completion rates per agent
4. **Rebalance**: Reassign tasks if one agent is overloaded

---

## Syncing

### Automatic Sync

Views are automatically synced when:
- MASTER_LOG.md is updated
- Pre-commit hook runs
- Daily cron job executes

### Manual Sync

Sync all agents:
```bash
python3 scripts/todo/sync_agents.py
```

Sync specific agent:
```bash
python3 scripts/todo/sync_agents.py --agent jules
```

Dry run (preview changes):
```bash
python3 scripts/todo/sync_agents.py --dry-run
```

---

## Workload Distribution

Current distribution:

```
CODEX:       19 tasks (32.8%)  - Python infrastructure
Jules:       16 tasks (27.6%)  - CI/CD, observability
Claude Code: 18 tasks (31.0%)  - Testing, documentation
Copilot:      5 tasks ( 8.6%)  - Mechanical edits
```

**Health**: ✅ Well-balanced (no agent >40%)

---

## Related Documentation

- **[TODO/MASTER_LOG.md](../MASTER_LOG.md)** - Single source of truth for all tasks
- **[TODO/RULES_FOR_AGENTS.md](../RULES_FOR_AGENTS.md)** - Mandatory rules for agents
- **[scripts/todo/README.md](../../scripts/todo/README.md)** - Automation scripts
- **[ai-agents/README.md](../../ai-agents/README.md)** - External AI agent workspace

---

## Troubleshooting

### My view is out of date

Run sync script:
```bash
python3 scripts/todo/sync_agents.py
```

### I don't see my tasks

Check that tasks in MASTER_LOG have your agent name in the Owner column:
```bash
grep "your-agent" TODO/MASTER_LOG.md
```

### Tasks are missing

Sync script only includes tasks with:
- Valid agent owner (jules|claude-code|codex|human)
- Task in a priority section (P0/P1/P2/P3)

---

**Maintained by**: Auto-sync from MASTER_LOG.md
**Last Sync**: Run `python3 scripts/todo/sync_agents.py` to update
**Questions?**: See [TODO/RULES_FOR_AGENTS.md](../RULES_FOR_AGENTS.md)

