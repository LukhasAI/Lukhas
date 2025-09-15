# Group C1: CRITICAL-CORE-INFRASTRUCTURE Agent Instructions

**Agent:** JULES-11
**Domain:** CRITICAL-CORE-INFRASTRUCTURE
**Batch File:** `.lukhas_runs/2025-09-15/batches_clean/BATCH-JULES11-2025-09-15-01.json`

## Mission
You are assigned to complete **Group C1** from the UNALLOCATED_TODO_GROUPS.md strategic plan. Your focus is on core system initialization, critical imports, and undefined name fixes that are blocking system stability.

## Your Specific Task List
Your 35 concrete tasks are defined in your batch file:
```bash
# Your task list is here:
cat .lukhas_runs/2025-09-15/batches_clean/BATCH-JULES11-2025-09-15-01.json
```

## Key Focus Areas
Based on your batch analysis, your tasks include:

### 1. F821 Undefined Name Fixes (High Priority)
- Fix 19 F821 undefined name errors in `candidate/core/framework_integration.py`
- Fix QI/quantum entanglement undefined references in `candidate/qi/qi_entanglement.py`
- Fix service integration patterns in `candidate/orchestration/openai_modulated_service.py`
- Fix governance drift dashboard visualization errors

### 2. MATRIZ-R2 Trace Integration (Critical)
- Identity consciousness namespace isolation integration
- Constitutional AI compliance trace integration
- Consciousness coherence monitor trace integration

### 3. Core Infrastructure Implementation
- Lambda ID generator configuration and logging
- Identity manager core infrastructure review
- Guardian system integration points

### 4. Trinity Framework Consciousness Evolution
- Governance identity core systems
- Swarm hub tier-aware systems
- QI identity manager consciousness evolution

## Working Process

### Step 1: Load Your Tasks
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 -c "
import json
with open('.lukhas_runs/2025-09-15/batches_clean/BATCH-JULES11-2025-09-15-01.json', 'r') as f:
    batch = json.load(f)

print(f'You have {len(batch[\"tasks\"])} tasks to complete:')
for i, task in enumerate(batch['tasks'], 1):
    print(f'{i:2d}. {task[\"task_id\"]} - {task[\"title\"]}')
    print(f'    File: {task[\"file\"]}')
    print(f'    Priority: {task[\"priority\"]} | Risk: {task[\"risk\"]}')
    print()
"
```

### Step 2: Work Through Tasks Systematically
- Start with highest priority (critical) tasks
- Focus on mechanical fixes first (F821 errors)
- Then move to integration tasks
- Finally handle logic implementation tasks

### Step 3: Maintain Evidence Trail
Each task completion requires:
- Code changes with proper commit
- Grep evidence that TODO is resolved
- Test verification where applicable

## Success Criteria
- [ ] All 35 tasks marked as completed in batch file
- [ ] All F821 undefined name errors resolved
- [ ] Core infrastructure systems properly integrated
- [ ] Trinity Framework consciousness evolution points implemented
- [ ] Evidence trail maintained for each completion

## Risk Management
- **High-risk tasks:** Guardian integration, quantum entanglement fixes
- **Medium-risk tasks:** Most MATRIZ integration and core infrastructure
- **Low-risk tasks:** Basic import fixes and service patterns

## Next Steps
1. Load and review your complete task list from the batch file
2. Create a working branch: `feat/jules11/critical_core_infrastructure`
3. Start with the first critical task and work systematically
4. Update the batch file as you complete each task
5. Maintain atomic commits with proper TaskID references

---
**Generated:** 2025-09-15
**System:** T4-Compliant Agent Instructions
**Status:** Ready for agent execution
