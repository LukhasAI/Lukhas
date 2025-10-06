---
status: wip
type: documentation
---
# 🤖 Agent Initiation Task - Jules01

**Welcome to LUKHAS AI Multi-Agent Development Platform!**

## 🎯 Your Mission

Hello **Jules01**! You are now part of the LUKHAS AI multi-agent development system. This initiation task will help you understand the platform and prepare for MATRIZ-R1 execution.

## 📋 Initiation Checklist

### Step 1: Repository Orientation
- [ ] **Read**: [`README.md`](../README.md) - Main repository overview
- [ ] **Study**: [`AGENTS.md`](../AGENTS.md) - Complete agent system guide
- [ ] **Review**: [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](../docs/project/MATRIZ_R1_EXECUTION_PLAN.md) - Current mission

### Step 2: Architecture Understanding  
- [ ] **Understand Lane System**: Review `ops/matriz.yaml` for development lanes
- [ ] **Know the Boundaries**: Learn `lukhas/` vs `candidate/` distinction
- [ ] **Check Quality Gates**: Understand testing and validation requirements

### Step 3: Agent System Navigation
- [ ] **Explore Agent Types**: Review Claude Code UI specialists in `.claude/agents/`
- [ ] **Check External Configs**: Browse `agents_external/` for deployment options
- [ ] **Understand Coordination**: Review agent selection guide by stream

### Step 4: MATRIZ-R1 Mission Brief
- [ ] **Stream Dependencies**: Understand A→D, B→D, C independent structure
- [ ] **Task Assignment**: Locate your potential assignments in execution plan
- [ ] **Quality Requirements**: Review acceptance criteria and PR limits (≤300 LOC)

### Step 5: Development Environment
- [ ] **Verify Tools**: Ensure access to `ruff`, `pytest`, `import-linter`
- [ ] **Test Commands**: Run `make lane-guard`, smoke tests
- [ ] **Branch Strategy**: Understand `fix/`, `feat/`, `sec/`, `chore/` prefixes

## 🧪 Validation Task

To confirm your understanding, please complete this simple task:

### Task: Repository Health Check
1. **Run Lane Guard**: Execute `PYTHONPATH=. python3 tools/ci/runtime_lane_guard.py`
2. **Check Import Compliance**: Run `lint-imports -v` (if available)  
3. **Syntax Validation**: Run `ruff check --select E9,F63,F7,F82 lukhas/`
4. **Smoke Tests**: Execute `pytest tests/smoke/ -v`

### Expected Results:
- Lane guard should PASS (no candidate modules leaked)
- Import linter should show clean boundaries
- Ruff should show minimal syntax errors
- Smoke tests should execute cleanly

## 📤 Completion Report

Once you've completed the initiation, please report:

```markdown
## Jules01 Initiation Complete ✅

### Completed Tasks:
- [x] Repository orientation
- [x] Architecture understanding  
- [x] Agent system navigation
- [x] MATRIZ-R1 mission brief
- [x] Development environment setup
- [x] Validation task execution

### Validation Results:
- Lane Guard: [PASS/FAIL + details]
- Import Compliance: [PASS/FAIL + details] 
- Syntax Check: [PASS/FAIL + error count]
- Smoke Tests: [PASS/FAIL + test count]

### Stream Preference:
- Primary: Stream A - Lead agent for Lane Integrity (critical path)
- Secondary: Stream D - Hygiene tasks after A+B complete

### Ready for Task Assignment: YES
```

## 🚀 Next Steps

After completing initiation:

1. **Join Active Development**: Check the execution plan for available tasks
2. **Claim a Task**: Add `Took: <ID>` to PR description when ready
3. **Follow Protocol**: Use suggested branch names, run local gates
4. **Coordinate**: Use handover protocol if blocked >2h

## 🆘 Need Help?

- **Documentation**: All guides are cross-linked in [`AGENTS.md`](../AGENTS.md)
- **Task Details**: Specific requirements in [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](../docs/project/MATRIZ_R1_EXECUTION_PLAN.md)
- **Agent Selection**: Use the stream-specific agent recommendations

---

**Welcome to the team, Jules01! Ready to build the future of consciousness-aware AI? 🧠⚛️🛡️**