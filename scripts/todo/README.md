# TODO Automation Scripts

> **Automation tools for LUKHAS TODO system**
>
> Last Updated: 2025-11-11

---

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| **validate_master_log.py** | Validate MASTER_LOG.md format | `python3 scripts/todo/validate_master_log.py` |
| **process_inbox.py** | Process quick-drop TODOs | `python3 scripts/todo/process_inbox.py` |
| **sync_agents.py** | Sync agent views from MASTER_LOG | `python3 scripts/todo/sync_agents.py` |
| **generate_reports.py** | Generate progress reports | `python3 scripts/todo/generate_reports.py --type weekly` |

---

## Quick Start

### Validate MASTER_LOG

Check that MASTER_LOG.md is properly formatted:

```bash
python3 scripts/todo/validate_master_log.py
```

**Checks**:
- All task IDs are unique
- Task totals match actual counts
- Valid priority/status/effort levels
- Proper task ID format

**Returns**: Exit code 0 if valid, 1 if errors found

---

### Process Inbox

Convert quick-drop TODOs into tracked tasks:

```bash
# Dry run (show what would happen)
python3 scripts/todo/process_inbox.py --dry-run

# Process all inbox files
python3 scripts/todo/process_inbox.py

# Override priority
python3 scripts/todo/process_inbox.py --priority P1
```

**Workflow**:
1. Scans `TODO/inbox/` for .md and .txt files
2. Parses task details (or uses defaults)
3. Generates task ID
4. Adds to MASTER_LOG in appropriate priority section
5. Moves processed files to `TODO/inbox/processed/`

---

### Sync Agent Views

Update agent-specific task views from MASTER_LOG:

```bash
# Sync all agents
python3 scripts/todo/sync_agents.py

# Sync specific agent
python3 scripts/todo/sync_agents.py --agent jules

# Dry run
python3 scripts/todo/sync_agents.py --dry-run
```

**Updates**:
- `TODO/by-agent/jules.md`
- `TODO/by-agent/claude-code.md`
- `TODO/by-agent/codex.md`
- `TODO/by-agent/human.md`

**Note**: Agent views are auto-generated. Do not edit manually.

---

### Generate Reports

Create progress and health reports:

```bash
# Weekly progress report
python3 scripts/todo/generate_reports.py --type weekly

# Health check report
python3 scripts/todo/generate_reports.py --type health

# Custom output directory
python3 scripts/todo/generate_reports.py --type weekly --output reports/
```

**Report Types**:
- **weekly**: Weekly progress summary
- **monthly**: Monthly summary (not yet implemented)
- **agent**: Agent productivity metrics (not yet implemented)
- **health**: System health check

---

## Automation Workflows

### Pre-commit Hook

Validate MASTER_LOG before committing:

```bash
# In .git/hooks/pre-commit
#!/bin/bash
python3 scripts/todo/validate_master_log.py || exit 1
```

### Daily Cron Job

Sync agent views daily:

```bash
# Add to crontab
0 9 * * * cd /path/to/Lukhas && python3 scripts/todo/sync_agents.py
```

### Weekly Reports

Generate weekly reports every Monday:

```bash
# Add to crontab
0 10 * * 1 cd /path/to/Lukhas && python3 scripts/todo/generate_reports.py --type weekly
```

---

## Development

### Adding New Scripts

When creating new TODO automation scripts:

1. **Follow naming convention**: `verb_noun.py` (e.g., `sync_agents.py`)
2. **Include docstring**: Document usage and options
3. **Add to this README**: Update scripts table
4. **Make executable**: `chmod +x scripts/todo/your_script.py`
5. **Add shebang**: `#!/usr/bin/env python3`
6. **Use argparse**: For command-line options
7. **Add colors**: Use ANSI codes for output

### Testing Scripts

Test with `--dry-run` option when available:

```bash
python3 scripts/todo/your_script.py --dry-run
```

---

## Troubleshooting

### Script not found

Ensure you're in the LUKHAS root directory:

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 scripts/todo/validate_master_log.py
```

### Permission denied

Make scripts executable:

```bash
chmod +x scripts/todo/*.py
```

### Import errors

Ensure you're using Python 3.7+:

```bash
python3 --version
```

### MASTER_LOG not found

Scripts expect to be run from LUKHAS root directory.

---

## Future Enhancements

### Planned Scripts

- **sync_github_issues.py** - Bi-directional sync with GitHub Issues
- **find_duplicate_ids.py** - Find and resolve duplicate task IDs
- **archive_completed.py** - Auto-archive completed tasks >30 days old
- **estimate_velocity.py** - Calculate team velocity and forecast

### Planned Features

- **GitHub Actions integration** - Auto-sync on PR merge
- **Slack notifications** - Weekly reports to Slack
- **Dashboard** - Web-based TODO dashboard
- **AI assistant** - Natural language TODO entry

---

## Related Documentation

- **[TODO/MASTER_LOG.md](../../TODO/MASTER_LOG.md)** - Main TODO log
- **[TODO/RULES_FOR_AGENTS.md](../../TODO/RULES_FOR_AGENTS.md)** - Agent rules
- **[TODO/README.md](../../TODO/README.md)** - TODO system guide

---

**Maintained by**: LUKHAS AI Team
**Questions?**: Create issue with label `question:todo-automation`
