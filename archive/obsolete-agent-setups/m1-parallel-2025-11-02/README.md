# M1 Parallel Agent Setup - LUKHAS Development

**Purpose**: Coordinate parallel development streams between M1 laptop and main development machine  
**Safety Level**: T4-Safe (isolated, human-gated, reversible)  
**Timeline**: 1.5 hours total execution  

---

## 🎯 Overview

This agent pack system enables the M1 laptop to run parallel work streams while the main laptop continues development, maximizing throughput while maintaining safety and coordination.

## 📦 Agent Packs Available

### Primary Automation Pack
- **[M1_PARALLEL_CODEX_PACK.md](./M1_PARALLEL_CODEX_PACK.md)**
  - **Agent**: Codex (automation)
  - **Task**: Codemod dry-run + conservative filtering
  - **Output**: Safe patch archive for human review
  - **Timeline**: 1 hour
  - **Safety**: Dry-run only, no auto-apply

### Secondary Surgical Packs  
- **[M1_PARALLEL_CLAUDE_IDENTITY_PACK.md](./M1_PARALLEL_CLAUDE_IDENTITY_PACK.md)**
  - **Agent**: Claude Code
  - **Task**: Lazy-load labs in `core/identity.py`
  - **Output**: Single-file PR with validation
  - **Timeline**: 30 minutes

- **[M1_PARALLEL_CLAUDE_TAGS_PACK.md](./M1_PARALLEL_CLAUDE_TAGS_PACK.md)**
  - **Agent**: Claude Code  
  - **Task**: Lazy proxy in `core/tags/__init__.py`
  - **Output**: Single-file PR with validation
  - **Timeline**: 30 minutes

### Coordination Pack
- **[M1_PARALLEL_COORDINATION_PACK.md](./M1_PARALLEL_COORDINATION_PACK.md)**
  - **Purpose**: Orchestrate all parallel streams
  - **Timeline**: Full 1.5 hour coordination
  - **Safety protocols**: File locks, validation gates
  - **Integration**: Handoff procedures to main team

## 🚀 Quick Start

### For M1 Laptop Execution

1. **Read Coordination Pack First**:
   ```bash
   cat docs/agents/tasks/M1_PARALLEL_COORDINATION_PACK.md
   ```

2. **Execute in Order**:
   - Start Codex automation (primary)
   - Run Claude identity fix (secondary)  
   - Run Claude tags fix (secondary)
   - Upload all artifacts

3. **Validation Required**:
   - All packs include validation commands
   - Artifacts must be uploaded for review
   - Human gates respected throughout

### For Main Laptop Coordination

1. **File Lock Setup**: Avoid `core/identity.py` and `core/tags/__init__.py` while M1 PRs open
2. **Review Queue**: Monitor for M1 artifacts and PRs
3. **Integration**: Apply Codex patches after human review
4. **Conflict Resolution**: Coordinate via shared channels

## 🛡️ Safety Framework

### T4-Safe Principles Applied
- **Small**: Single-file edits, focused patches
- **Auditable**: Complete validation artifacts
- **Reversible**: All changes can be reverted
- **Human-in-loop**: No auto-apply, review gates

### Isolation Guarantees  
- **Branch Isolation**: M1 uses `task/*` branches only
- **File Isolation**: Coordinated file locks
- **Process Isolation**: Dry-run only for automation
- **Review Isolation**: Human review required for integration

## 📊 Expected Outcomes

### Deliverables
- [ ] **Codex Archive**: `/tmp/codemod_batch1_patches.tgz` (safe patches)
- [ ] **Claude PR 1**: `task/claude-lazy-load-identity-M1` 
- [ ] **Claude PR 2**: `task/claude-lazy-init-tags-M1`
- [ ] **Validation Reports**: Complete artifact suites
- [ ] **Coordination**: File locks and handoff documentation

### Success Metrics
- **Timeline**: Complete within 1.5 hours
- **Quality**: All validation gates pass
- **Safety**: No conflicts with main laptop
- **Integration**: Smooth handoff to main team

## 🔄 Workflow Integration

```
M1 Laptop                    Main Laptop
    │                            │
    ├─ Codex automation          ├─ Continue development
    ├─ Claude identity fix       ├─ Avoid locked files  
    ├─ Claude tags fix           ├─ Monitor M1 artifacts
    └─ Upload artifacts          └─ Review & integrate
            │                            │
            └──── Coordination ─────────┘
```

## 📋 Agent Assignment Matrix

| Agent | Pack | Timeline | Output | Safety Level |
|-------|------|----------|--------|--------------|
| Codex | Codex Pack | 1h | Patch archive | T4-Safe (dry-run) |
| Claude | Identity Pack | 30m | Single PR | T4-Safe (reversible) |
| Claude | Tags Pack | 30m | Single PR | T4-Safe (reversible) |
| Human | Coordination | 1.5h | Review & integration | Manual oversight |

## 🔗 References

- **Base Instructions**: [Untitled-1.md](../../../Untitled-1.md) - Original M1 parallel work plan
- **Agent Guidelines**: [AGENTS.md](../../../AGENTS.md) - Overall agent coordination
- **Safety Standards**: T4 compliance throughout all packs

---

**Status**: Agent packs ready for deployment  
**Next**: Execute coordination pack → Deploy agents → Monitor progress → Integrate results