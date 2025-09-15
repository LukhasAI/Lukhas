# LUKHAS TODO Agent Allocations

**Complete allocation of all 1,118 TODOs across 31 agent batches**

## 🎯 How to Use Your Allocation

### If you're told "You are JULES-01"
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
cat docs/agent-allocations/JULES-01.json
```

### If you're told "You are CODEX-05"
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
cat docs/agent-allocations/CODEX-05.json
```

### Simple Task List Command
```bash
# Get your task list (replace AGENT-ID):
python3 -c "
import json
with open('docs/agent-allocations/JULES-01.json', 'r') as f:
    data = json.load(f)
print(f'=== {data[\"agent_id\"]}: {data[\"specialty\"]} ===')
print(f'Focus: {data[\"focus\"]}')
print(f'Tasks: {data[\"task_count\"]}')
print()
for i, task in enumerate(data['tasks'], 1):
    print(f'{i:2d}. {task[\"task_id\"]}')
    print(f'    {task[\"title\"]}')
    print(f'    {task[\"file\"]}')
    print()
"
```

## 📋 Available Agent Files

### 🟦 JULES Agents (Critical/High Priority)
- **JULES-01.json** - Identity Core (30 critical tasks)
- **JULES-02.json** - Consent/Scopes (30 critical tasks)
- **JULES-03.json** - SSO/Biometrics (25 critical tasks)
- **JULES-04.json** - Awareness Protocol (25 critical tasks)
- **JULES-05.json** - Guardian Ethics (25 critical tasks)
- **JULES-06.json** - QRG Generator (30 high tasks)
- **JULES-07.json** - Wallet/QI Bridges (30 high tasks)
- **JULES-08.json** - Quantum Entropy (30 high tasks)
- **JULES-09.json** - Dashboards (30 high tasks)
- **JULES-10.json** - Tests/Integration (30 high tasks)

### 🟨 CODEX Agents (High/Med/Low Priority)
- **CODEX-01.json** - High Priority Batch 1 (40 tasks)
- **CODEX-02.json** - High Priority Batch 2 (40 tasks)
- **CODEX-03.json** - High Priority Batch 3 (40 tasks)
- **CODEX-04.json** - High Priority Batch 4 (40 tasks)
- **CODEX-05.json** - High Priority Batch 5 (40 tasks)
- **CODEX-06.json** - High Priority Batch 6 (40 tasks)
- **CODEX-07.json** - Medium Priority Batch 1 (40 tasks)
- **CODEX-08.json** - Medium Priority Batch 2 (40 tasks)
- **CODEX-09.json** - Medium Priority Batch 3 (40 tasks)
- **CODEX-10.json** - Low Priority Batch (40 tasks)

### 🟩 REMAINING Batches (Mixed Priority)
- **REMAINING-01.json** through **REMAINING-11.json** (40 tasks each)

## ✅ Complete Workflow

### Step 1: Get Your Assignment
```bash
# Example: You are assigned JULES-01
export AGENT_ID="JULES-01"
cat docs/agent-allocations/$AGENT_ID.json | jq '.specialty, .focus, .task_count'
```

### Step 2: Create Your Branch
```bash
# From the JSON: "branch_prefix": "feat/jules-01/identity-core-batch"
git checkout -b feat/jules-01/identity-core-batch01
```

### Step 3: Work Through Tasks
```bash
# Get task 1
python3 -c "
import json
with open('docs/agent-allocations/$AGENT_ID.json', 'r') as f:
    data = json.load(f)
task = data['tasks'][0]  # First task
print(f'TaskID: {task[\"task_id\"]}')
print(f'File: {task[\"file\"]}')
print(f'Title: {task[\"title\"]}')
print(f'Priority: {task[\"priority\"]} | Risk: {task[\"risk\"]}')
"

# Work on the task, then commit
git add .
git commit -m "feat(identity): implement missing functionality (TODO-CRIT-BRANDING-PERSONAL_BRAND-1d64c1fd)"
```

### Step 4: Continue Systematically
- Work through each task in your JSON file
- One TaskID per commit
- Run checks: `ruff check . && pytest -q`

## 🔍 Task Structure
Each task in your JSON contains:
```json
{
  "task_id": "TODO-CRIT-CANDIDATE-CORE-8343b461",
  "priority": "critical",
  "title": "kept for core infrastructure (review and implement)",
  "file": "./candidate/core/identity/matriz_consciousness_identity_signals.py",
  "module": "candidate/core",
  "trinity": "Identity",
  "line_hint": 2,
  "risk": "med",
  "type": "logic",
  "size": "S",
  "evidence": {
    "grep": "search_result_or_null",
    "last_commit": "commit_sha"
  }
}
```

## 📊 Allocation Summary
- **Total TODOs**: 1,118
- **Allocated**: 1,116 (99.8%)
- **Agent Files**: 31 total
- **Coverage**: Complete system coverage from critical to low priority

---
**Generated**: 2025-09-15
**Source**: PLANNING_TODO.md + manifest_clean.json
**Usage**: Load your agent JSON file and work through tasks systematically
