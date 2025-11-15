# 🔀 Mandatory Worktree Policy for Claude Code Agents

**Status**: ✅ Enforced  
**Effective Date**: 2025-11-06  
**Applies To**: ALL Claude Code agents and automated workflows

---

## 🚨 Core Rule

**ALL commits MUST be made in worktrees. NO EXCEPTIONS.**

This policy prevents conflicts when multiple agents work in parallel and protects the main working directory.

---

## Worktree Workflow

### 1. Create Worktree (REQUIRED before any commits)
```bash
git worktree add ../Lukhas-<task-name> -b <branch-type>/<descriptive-name>
cd ../Lukhas-<task-name>
```

### 2. Branch Naming Conventions
- **Features**: `feat/feature-name` → `../Lukhas-feature-name`
- **Fixes**: `fix/issue-description` → `../Lukhas-fix-issue`
- **Docs**: `docs/update-name` → `../Lukhas-docs-update`
- **Refactor**: `refactor/component` → `../Lukhas-refactor-component`
- **Branding**: `feat/branding-topic` → `../Lukhas-branding-topic`

### 3. Work in Worktree
```bash
# Make changes
git add .
git commit -m "type(scope): description"

# Create PR when ready
gh pr create --title "Title" --body "Description"
```

### 4. Cleanup After Merge
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git worktree remove ../Lukhas-<task-name>
git branch -d <branch-name>  # if needed
```

---

## Exceptions (NO COMMITS)

ONLY skip worktrees for:
- **Reading**: Files, documentation, code review
- **Linting**: Running linters without fixing
- **Reports**: Generating analysis without changes

**If making ANY commit → MUST use worktree**

---

## Current Active Worktrees

Check before creating new worktrees:
```bash
git worktree list
```

As of 2025-11-06:
- `Lukhas-branding-compliance` - Branding governance compliance fixes
- `Lukhas-audit-2025` - Pre-launch audit
- `Lukhas-claude-dev` - PR review system
- `Lukhas-dtz003-worktree` - Import fixes
- `Lukhas-github-issues` - Issues audit
- `Lukhas-import-fixes` - Quick wins
- `Lukhas-t4-autofix` - T4 lint automation
- `Lukhas-test-audit` - Test coverage
- `Lukhas-website-phase2` - Website updates
- `Lukhas-worktrees/wkt-shim` - MATRIZ tests

---

## Why This Matters

### Benefits
1. **Parallel Work**: Multiple agents/humans work simultaneously
2. **Conflict Prevention**: Isolated workspaces prevent collisions
3. **Main Protection**: Never break the primary working directory
4. **Clean PRs**: Each feature gets isolated branch and review
5. **Enterprise Grade**: Professional development workflow

### Risks of Direct Commits to Main
- ❌ Conflicts between agents
- ❌ Breaking active work-in-progress
- ❌ Lost changes from parallel sessions
- ❌ Difficulty tracking who changed what
- ❌ No isolated PR review

---

## Enforcement

**Automated Checks** (future):
- Pre-commit hook detecting direct main commits
- CI/CD validation of branch naming
- Worktree usage reporting in metrics

**Current Enforcement**:
- Documentation in CLAUDE.md (global instructions)
- This policy file (project-specific)
- Agent training and reminders
- Code review requirements

---

## Related Documentation

- [CLAUDE.md](/Users/agi_dev/CLAUDE.md) - Global agent instructions
- [Git Workflow Guide](docs/development/README.md) - Developer workflows
- [PR Templates](.github/PULL_REQUEST_TEMPLATE/) - PR creation

---

**Remember**: Worktrees aren't optional—they're mandatory for professional multi-agent development.

