# M1 Parallel Agent Coordination Pack

**Target**: M1 Branch Laptop Coordination  
**Purpose**: Orchestrate parallel work streams while main laptop continues development  
**Timeline**: 1.5 hours total  
**Safety Level**: T4-Safe (all work isolated, human-gated)

---

## 🎯 Mission Overview

Execute two parallel work streams on M1 laptop while main laptop continues development:

1. **Primary**: Codex automation (codemod dry-run + filtering)
2. **Secondary**: Claude Code surgical edits (2 specific files)

Both streams produce artifacts for human review before integration.

## 📋 Work Stream Coordination

### Stream A: Codex Automation (1 hour)
- **Pack**: [`M1_PARALLEL_CODEX_PACK.md`](./M1_PARALLEL_CODEX_PACK.md)
- **Output**: `/tmp/codemod_batch1_patches.tgz`
- **Safety**: Dry-run only, no auto-apply
- **Dependencies**: None (standalone)

### Stream B: Claude Code Edits (30 min each)
- **Pack 1**: [`M1_PARALLEL_CLAUDE_IDENTITY_PACK.md`](./M1_PARALLEL_CLAUDE_IDENTITY_PACK.md)
- **Pack 2**: [`M1_PARALLEL_CLAUDE_TAGS_PACK.md`](./M1_PARALLEL_CLAUDE_TAGS_PACK.md)
- **Output**: 2 small PRs with validation artifacts
- **Safety**: Single-file edits, reversible
- **Dependencies**: Sequential (avoid IDE conflicts)

## ⚡ Execution Timeline

```
Hour 0:00 - 0:30  │ Setup + Codex automation (codemod + filter)
Hour 0:30 - 1:00  │ Claude Code: core/identity.py
Hour 1:00 - 1:30  │ Claude Code: core/tags/__init__.py
Hour 1:30+        │ Upload artifacts, coordinate with main laptop
```

## 🤖 Agent Assignment

### Codex Agent
- **Primary responsibility**: Codemod automation
- **Pack**: M1_PARALLEL_CODEX_PACK.md
- **Deliverable**: Patch archive + summary report
- **Constraints**: No auto-apply, human review required

### Claude Code Agent  
- **Primary responsibility**: Surgical imports fixes
- **Pack 1**: M1_PARALLEL_CLAUDE_IDENTITY_PACK.md
- **Pack 2**: M1_PARALLEL_CLAUDE_TAGS_PACK.md
- **Deliverable**: 2 PRs with validation artifacts
- **Constraints**: One file per PR, validation required

## 🛡️ Safety Protocols

### Absolute Rules
1. **Base everything on `M1` branch** - no rebasing of feat/* branches from main laptop
2. **Never commit `.importlinter` or `.venv` changes**
3. **One file per Claude PR** - keep surgical and focused
4. **Codex dry-run only** - no automatic patch application
5. **Upload all artifacts** - validation reports, patch archives

### File Coordination
- **M1 Laptop Files**: `core/identity.py`, `core/tags/__init__.py`
- **Main Laptop**: Avoid these files while M1 PRs are open
- **Run Lock**: Add files to daily coordination issue

### PR Labels
- **Codex work**: `agent:codex-M1`
- **Claude work**: `agent:claude-M1`
- **Branch prefix**: `task/` for all M1 branches

## 📦 Expected Deliverables

### From Codex Stream
- [ ] `/tmp/codemod_batch1_patches.tgz` - Safe patch archive
- [ ] JSON summary report (total, safe, flagged counts)
- [ ] Upload confirmation to coordination channel

### From Claude Streams
- [ ] PR: `task/claude-lazy-load-identity-M1` 
- [ ] PR: `task/claude-lazy-init-tags-M1`
- [ ] Validation artifacts: ruff, mypy, pytest, lane-guard logs
- [ ] Import-safety tests added and passing

## 🔄 Validation Gates

### Codex Validation
```bash
# Patch count verification
echo "Total: $(ls -1 /tmp/codmod_patches | wc -l)"
echo "Safe: $(ls -1 /tmp/codmod_batches/batch1.safe | wc -l)"

# Pattern verification (spot check)
for p in /tmp/codmod_batches/batch1.safe/*.patch; do
  grep -q "importlib\|_importlib" "$p" && \
  grep -q "getattr.*_mod" "$p" && \
  echo "✅ $p: Safe pattern confirmed"
done | head -5
```

### Claude Validation
```bash
# Per-file validation suite
python -m py_compile <target_file>
ruff check <target_file> --select E,F,W,C
mypy <target_file> --ignore-missing-imports  
pytest tests/core/<test_file> -q
./scripts/run_lane_guard_worktree.sh
```

## 📋 Escalation Triggers

**Stop and ask human if**:
- Lane-guard shows transitive path to `labs` after changes
- Codex filter produces 0 safe patches (unexpected)
- Claude needs to modify >1 file to make code work
- Any validation fails unexpectedly
- Import contracts are broken

## 🔗 Integration Handoff

### To Main Laptop Team
1. **Codex Archive**: `/tmp/codemod_batch1_patches.tgz` ready for review
2. **Claude PRs**: 2 small PRs with complete validation
3. **Coordination**: File locks updated, conflicts avoided
4. **Next Phase**: Main team applies safe patches after review

### Success Criteria
- [ ] All deliverables produced within timeline
- [ ] No conflicts with main laptop work
- [ ] Validation artifacts complete and attached
- [ ] Human review gates respected
- [ ] Coordination documented

---

**Status**: Ready for parallel execution  
**Next**: Deploy Codex + Claude agents → Monitor progress → Handoff to main team