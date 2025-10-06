---
status: wip
type: documentation
---
# Simple Group Allocations

**Direct allocation from master TODO list (.lukhas_runs/2025-09-15/manifest_clean.json)**

## Group C1: CRITICAL-CORE-INFRASTRUCTURE (JULES-11)
**Agent:** JULES-11
**Task Range:** TODOs 1-35 from critical priority list
**Tasks:**
```
TODO-CRIT-BRANDING-PERSONAL_BRAND-1d64c1fd
TODO-CRIT-BRANDING-ENGINES-e42c9939
TODO-CRIT-CANDIDATE-CORE-8343b461
TODO-CRIT-CANDIDATE-CORE-b3a11d0a
TODO-CRIT-CANDIDATE-CORE-2a4beaf7
TODO-CRIT-CANDIDATE-CORE-38d8621b
TODO-CRIT-CANDIDATE-CORE-79c1e34f (line 32)
TODO-CRIT-CANDIDATE-CORE-79c1e34f (line 39)
TODO-CRIT-CANDIDATE-CORE-d93e946b (line 7)
TODO-CRIT-CANDIDATE-CORE-d93e946b (line 8)
TODO-CRIT-CANDIDATE-CORE-93d8a8ae
TODO-CRIT-CANDIDATE-CORE-9156b4ea
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-5111a350
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-1006456b
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-16efdefe
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-d24afa9f
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-1a3b92a0
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-18bf0af1
TODO-CRIT-CANDIDATE-CONSCIOUSNESS-df6dfed8
TODO-CRIT-CANDIDATE-QI-4eca379a
TODO-CRIT-CANDIDATE-QI-a24bd36a
TODO-CRIT-CANDIDATE-ORCHESTRATION-4d81575f
TODO-CRIT-CANDIDATE-GOVERNANCE-cf47a643
TODO-CRIT-CANDIDATE-GOVERNANCE-66824f12
TODO-CRIT-CANDIDATE-GOVERNANCE-2120dbf8
TODO-CRIT-CANDIDATE-GOVERNANCE-3853a416
TODO-CRIT-CANDIDATE-GOVERNANCE-e73e20ef
TODO-CRIT-CANDIDATE-GOVERNANCE-14cc8e78
TODO-CRIT-CANDIDATE-GOVERNANCE-522cb5b5
TODO-CRIT-CANDIDATE-GOVERNANCE-e49f4ab7
TODO-CRIT-CANDIDATE-GOVERNANCE-febfa200
TODO-CRIT-CANDIDATE-GOVERNANCE-b4790085
TODO-CRIT-CANDIDATE-GOVERNANCE-291f534f
TODO-CRIT-CANDIDATE-GOVERNANCE-4b35bb43
TODO-CRIT-CANDIDATE-GOVERNANCE-0a627034
```

## Group C2: CRITICAL-CONSCIOUSNESS-CORE (JULES-12)
**Agent:** JULES-12
**Task Range:** TODOs 36-70 from critical priority list
**Focus:** Consciousness system critical paths, AkaQualia core issues

## Group C3: CRITICAL-IDENTITY-AUTH (JULES-13)
**Agent:** JULES-13
**Task Range:** TODOs 71-105 from critical priority list
**Focus:** Identity system, authentication, Lambda ID critical issues

## Group H1: HIGH-API-INTEGRATION (CODEX-11)
**Agent:** CODEX-11
**Task Range:** TODOs 1-35 from high priority list
**Focus:** API implementations, service integrations, external connections

## Group M1: MEDIUM-REFACTORING (CODEX-12)
**Agent:** CODEX-12
**Task Range:** TODOs 1-35 from medium priority list
**Focus:** Code refactoring, structure improvements, maintainability

---

## How to Use This

**For Group C1 (JULES-11):**
```bash
# Get your task list
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 -c "
import json
with open('.lukhas_runs/2025-09-15/manifest_clean.json', 'r') as f:
    manifest = json.load(f)

# Filter critical TODOs and take first 35
critical_todos = [t for t in manifest['todos'] if t.get('priority') == 'critical' and t.get('status') == 'open'][:35]

print('=== GROUP C1: CRITICAL-CORE-INFRASTRUCTURE (35 tasks) ===')
for i, task in enumerate(critical_todos, 1):
    print(f'{i:2d}. {task[\"task_id\"]}')
    print(f'    {task[\"title\"]}')
    print(f'    {task[\"file\"]}')
    print()
"
```

**For any group:**
Just change the priority filter and slice range:
- Group C2: `critical_todos[35:70]`
- Group C3: `critical_todos[70:105]`
- Group H1: `high_todos[:35]`
- Group M1: `med_todos[:35]`
