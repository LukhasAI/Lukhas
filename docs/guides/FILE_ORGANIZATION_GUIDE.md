# 📁 LUKHAS File Organization System

## Overview

The LUKHAS File Organization System automatically keeps the root directory clean and organized by moving files to their appropriate locations based on configurable rules.

## Why This Matters

A cluttered root directory:
- Makes it hard to find important files
- Slows down development
- Confuses new contributors
- Looks unprofessional

Our automated system ensures:
- ✅ Critical files stay in root (README, LICENSE, requirements.txt, etc.)
- ✅ Reports and documentation move to organized folders
- ✅ Backups are centralized
- ✅ One-off scripts don't clutter the root

## Quick Start

### Manual Organization

```bash
# See what would be organized (dry run)
make organize-dry

# Actually organize files
make organize

# Get suggestions for new rules
make organize-suggest
```

### Automatic Organization

The system runs automatically:
1. **GitHub Actions**: Weekly cleanup (Sundays at 2 AM UTC)
2. **Git Hooks**: After commits (if many report files detected)
3. **Watch Mode**: Continuous monitoring

## File Organization Rules

The rules are defined in `.file-organization.yaml`:

### Files That Stay in Root
- `README.md`, `LICENSE`, `CLAUDE.md`
- `requirements.txt`, `setup.py`, `pyproject.toml`
- `Makefile`, `Dockerfile`, `docker-compose.yml`
- Configuration files (`.gitignore`, `pytest.ini`, etc.)

### Where Files Go

| File Pattern | Destination | Examples |
|-------------|-------------|----------|
| `*_REPORT.md`, `*_STATUS.md` | `docs/completion_reports/` | TEST_SPECIALIST_REPORT.md |
| `AGENT_*.md`, `*_AGENT_*.md` | `docs/agent_reports/` | AGENT_IMPLEMENTATION_STATUS.md |
| `*_ANALYSIS.md`, `*_ASSESSMENT.md` | `docs/analysis/` | SECURITY_VULNERABILITY_ANALYSIS.md |
| `*_PLAN.md`, `*_ROADMAP.md` | `docs/planning/` | LUKHAS_CONSOLIDATION_PLAN.md |
| `MODULE_*.md` | `docs/modules/` | MODULE_STATUS_REPORT.md |
| `SECURITY_*.md` | `docs/security/` | SECURITY_AUTOMATION_SUMMARY.md |
| `*.backup` | `backups/` | requirements.txt.backup |
| `*_ORIGINAL*`, `*_LEGACY*` | `archive/legacy/` | README_ORIGINAL.md |
| `test_*.py`, `demo_*.py` | `scripts/one_off/` | test_client.py |
| `*.code-workspace` | `.vscode/workspaces/` | Lukhas.code-workspace |
| `*_CRASH*.md`, `*_RECOVERY*.md` | `docs/recovery/` | CLAUDE_CRASH_RECOVERY.md |

## Commands

### Makefile Targets

```bash
make organize          # Organize files now
make organize-dry      # Preview what would be moved
make organize-suggest  # Get suggestions for unmatched files
make organize-watch    # Start continuous monitoring
```

### Direct Script Usage

```bash
# Organize with options
python scripts/file-organizer.py organize --interactive

# Clean up old files (30+ days)
python scripts/file-organizer.py cleanup

# Watch mode with custom interval
python scripts/file-organizer.py watch --interval 600

# Restore a file to root
python scripts/file-organizer.py restore --file "REPORT.md"
```

## Configuration

Edit `.file-organization.yaml` to customize:

### Add New Rules

```yaml
organization_rules:
  - pattern: "^CUSTOM_.*\\.md$"
    destination: docs/custom/
    description: "Custom documentation"
```

### Exclude Files from Organization

```yaml
keep_in_root:
  - MY_IMPORTANT_FILE.md
  - another_critical_file.txt
```

### Set Archive Age

```yaml
cleanup:
  archive_after_days:
    "*.backup": 30      # Archive backups after 30 days
    "*_old.*": 60       # Archive old files after 60 days
```

## Automation

### GitHub Actions

The workflow runs weekly and:
1. Organizes files according to rules
2. Cleans up old files
3. Creates a PR with changes
4. Generates organization report

Trigger manually:
```bash
gh workflow run file-organization.yml
```

### Git Hooks

Enable post-commit organization:
```bash
git config core.hooksPath .githooks
```

### Continuous Monitoring

Run in background:
```bash
make organize-watch  # Check every 5 minutes
```

Or as a service:
```bash
# Add to crontab
*/10 * * * * cd /path/to/lukhas && python scripts/file-organizer.py organize
```

## Reports and Logs

### Organization Summary
Located at `docs/organization_summary.md`
- Shows files moved
- Organization statistics
- Recent activity

### Detailed Log
Located at `.file_organization_log.json`
- Complete history of moves
- Timestamps and destinations
- Used for file restoration

## Restoring Files

If a file was moved incorrectly:

```bash
# Restore specific file to root
python scripts/file-organizer.py restore --file "MY_FILE.md"

# Or manually check the log
cat .file_organization_log.json | jq '.[-10:]'
```

## Best Practices

1. **Review Before Committing**: Check organization summary after runs
2. **Update Rules Regularly**: Add patterns for new file types
3. **Use Descriptive Names**: Help the organizer with clear file naming
4. **Archive Old Files**: Don't delete, archive for history
5. **Test with Dry Run**: Always test new rules with `--dry-run`

## Troubleshooting

### Files Not Being Organized

1. Check if file matches any pattern:
```bash
python scripts/file-organizer.py suggest
```

2. Verify file isn't in `keep_in_root` list

3. Add new rule if needed

### File Moved Incorrectly

1. Restore from log:
```bash
python scripts/file-organizer.py restore --file "filename"
```

2. Add to `keep_in_root` or adjust pattern

### Organization Not Running

1. Check git hooks are enabled:
```bash
git config core.hooksPath
```

2. Verify Python and PyYAML installed:
```bash
pip install pyyaml
```

## Directory Structure After Organization

```
LUKHAS/
├── README.md                    # Stays in root
├── requirements.txt             # Stays in root
├── Makefile                     # Stays in root
├── docs/
│   ├── agent_reports/          # Agent implementation docs
│   ├── completion_reports/     # Status and completion reports
│   ├── implementation/         # Implementation guides
│   ├── analysis/              # Analysis documents
│   ├── planning/              # Plans and roadmaps
│   ├── modules/               # Module documentation
│   ├── security/              # Security docs
│   └── recovery/              # Crash recovery docs
├── backups/                    # All .backup files
├── archive/
│   └── legacy/                # Old and deprecated files
├── scripts/
│   └── one_off/              # Test and demo scripts
└── .vscode/
    └── workspaces/           # VSCode workspace files
```

## Future Enhancements

Planned improvements:
- [ ] Smart categorization using file content
- [ ] Integration with documentation generator
- [ ] Automatic README.md index updates
- [ ] File deduplication
- [ ] Compression of old archives

---

*Keep your root clean, keep your mind clear!* 🧹✨