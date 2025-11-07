# Claude Code Web Session Prompt

Copy and paste this entire prompt into a new Claude Code session at https://claude.ai/code

---

## Context

I need you to perform surgical refactoring on 10 high-priority files in the LUKHAS AI platform. You are working as part of a multi-agent orchestration workflow.

**Repository**: LukhasAI/Lukhas
**Branch**: Create new branch `refactor/provider-pattern-surgical`
**Your Role**: Claude Code - Surgical Refactoring Specialist
**Mission**: Eliminate import-time dependencies from production → labs

## Your Complete Task Pack

Read and follow the instructions in this file:
`docs/agents/tasks/CLAUDE_CODE_PACK.md`

This ~800-line document contains:
- Executive summary of the lane isolation initiative
- What you've learned about LUKHAS architecture
- 10 detailed tasks with full specifications
- File templates and code examples
- Validation steps and acceptance criteria
- Common issues and solutions

## Quick Architecture Context

**Lane System** (3-tier architecture):
```
candidate/  → Development lane (2,877 files) - Experimental research
core/       → Integration lane (253 files) - Testing/validation
lukhas/     → Production lane (692 files) - Battle-tested systems
```

**Critical Rule**: `lukhas/` MUST NOT import from `candidate/` (legacy labs)

**Current Problem**: 147 files have `from labs.* import ...` violations

**Your Mission**: Fix 10 high-priority files manually with precision

## Task Execution Pattern

For each of the 10 tasks in CLAUDE_CODE_PACK.md:

1. **Read the task specification** completely
2. **Create the branch** (if first task): `git checkout -b refactor/provider-pattern-surgical`
3. **Read the target file** to understand current implementation
4. **Apply the refactoring** following the exact pattern in the task
5. **Create import-safety test** in `tests/integration/test_<filename>_importsafe.py`
6. **Validate** with commands provided in task
7. **Commit** with format: `refactor(scope): eliminate labs import in <filename>`
8. Move to next task

## Your 10 Tasks (High-Level Overview)

### Priority 1 (P1) - Core Orchestration
1. **Task 01**: `core/colony/gpt_colony_orchestrator.py` - Provider pattern
2. **Task 02**: `core/orchestration/brain/consciousness_core.py` - Lazy loader
3. **Task 03**: `core/orchestration/brain/neural/cognitive_core.py` - Lazy loader

### Priority 2 (P2) - Critical Systems
4. **Task 04**: `core/governance/unified_constitutional_ai.py` - Provider pattern
5. **Task 05**: `core/identity/lambda_id.py` - Lazy proxy
6. **Task 06**: `core/observability/telemetry_manager.py` - Stub provider

### Priority 3 (P3) - Supporting Systems
7. **Task 07**: `serve/api/routes/consciousness.py` - Provider pattern
8. **Task 08**: `serve/api/routes/memory.py` - Provider pattern
9. **Task 09**: `lukhas_website/backend/api.py` - Lazy loader
10. **Task 10**: `lukhas_website/frontend/components/ConsciousnessMonitor.tsx` - Stub provider

## Validation Commands (Run After Each Task)

```bash
# 1. Syntax check
python3 -m py_compile <modified_file.py>

# 2. Import safety test
pytest tests/integration/test_<filename>_importsafe.py -v

# 3. Lane guard validation
make lane-guard

# 4. Related unit tests
pytest tests/unit/test_<component>*.py -v

# 5. Smoke tests (quick health check)
make smoke
```

## Example: Task 01 Implementation

**File**: `core/colony/gpt_colony_orchestrator.py`

**Before** (❌ Bad - import-time dependency):
```python
from labs.openai import OpenAI

class GPTColonyOrchestrator:
    def orchestrate_colony(self, prompt: str):
        client = OpenAI()
        response = client.chat.completions.create(...)
```

**After** (✅ Good - runtime dependency):
```python
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _get_openai_provider():
    """Get OpenAI provider via registry (runtime injection)."""
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

class GPTColonyOrchestrator:
    def orchestrate_colony(self, prompt: str):
        provider = _get_openai_provider()
        response = provider.chat.completions.create(...)
```

**Import Safety Test** (create `tests/integration/test_gpt_colony_orchestrator_importsafe.py`):
```python
"""Import safety test for gpt_colony_orchestrator module."""

def test_gpt_colony_orchestrator_import_safety():
    """Verify module imports without labs dependencies."""
    try:
        from core.colony import gpt_colony_orchestrator
        assert gpt_colony_orchestrator is not None
    except ImportError as e:
        if "labs" in str(e):
            raise AssertionError(f"Module still depends on labs: {e}")
        raise
```

## Critical Safety Rules

1. **Never auto-commit** - Always review changes before committing
2. **Test after every change** - Run all validation commands
3. **Preserve functionality** - Don't change business logic, only reshape imports
4. **Human-in-loop** - Ask for clarification if task is ambiguous
5. **Lane boundaries** - Never introduce new candidate/ imports in lukhas/
6. **Import safety** - Every refactored module needs import-safety test

## Success Metrics (Track These)

- **Files Refactored**: 0/10 → 10/10
- **Import Violations**: 10 files → 0 files (for your scope)
- **Test Coverage**: Maintain or improve (currently 30%+)
- **Syntax Health**: No new syntax errors introduced
- **Lane Guard**: Zero violations after refactoring

## Integration with Other Agents

- **GitHub Copilot**: Will provide real-time suggestions (don't auto-accept)
- **Codex**: Will handle remaining 137 files via batch automation (after you finish)
- **Gemini**: Will monitor coverage and SLSA attestation (parallel work)

## Common Issues & Solutions

### Issue 1: Circular Import After Refactoring
**Solution**: Use lazy import pattern with `importlib.import_module()`

### Issue 2: Test Failures After Changing Import
**Solution**: Update test mocks to use new provider pattern

### Issue 3: Lane-Guard Violations
**Solution**: Check `pyproject.toml` import linter rules, ensure no candidate/ imports

### Issue 4: Import-Safety Test Failing
**Solution**: Verify no transitive labs dependencies remain

## When You're Done

After completing all 10 tasks:

1. **Create PR** with title: `refactor: eliminate labs imports in 10 high-priority files`
2. **PR Description** should include:
   - List of 10 files refactored
   - Validation results (all tests passing)
   - Lane-guard output (zero violations)
   - Import-safety test results
3. **Tag reviewers**: @security_team, @ops_team
4. **Attach artifacts**: Test output, lane-guard report
5. **Link related work**: Reference Codex issues #807-#810 for batch automation

## Questions to Ask Me (If Needed)

1. Is the ProviderRegistry already implemented in `core/adapters/provider_registry.py`?
2. Do the import-safety tests need to mock any external dependencies?
3. Should I create the branch now or wait for your approval?
4. Are there any files in the 10-task list that should be prioritized differently?

## Ready to Start?

1. **First**: Read `docs/agents/tasks/CLAUDE_CODE_PACK.md` completely
2. **Then**: Confirm you understand the provider pattern and lazy loader patterns
3. **Finally**: Ask me which task to start with (recommend Task 01)

Let's eliminate those import-time dependencies with surgical precision! 🔧

---

**Repository Context Files** (read these for deeper understanding):
- `claude.me` - System architecture overview
- `lukhas_context.md` - Alternative format for non-Claude AI tools
- `docs/agents/tasks/CLAUDE_CODE_PACK.md` - YOUR PRIMARY TASK PACK (800 lines)
- `docs/gonzo/AGENT_TASKS_TO_CREATE.md` - Original specifications
- `pyproject.toml` - Lane guard rules and import linter configuration

**Commands Cheat Sheet**:
```bash
# Navigate to repo
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create branch
git checkout -b refactor/provider-pattern-surgical

# Validate after changes
make lane-guard
make smoke
pytest tests/integration/test_*_importsafe.py -v

# Commit pattern
git commit -m "refactor(colony): eliminate labs import in gpt_colony_orchestrator"

# Create PR
gh pr create --title "refactor: eliminate labs imports in 10 high-priority files" \
  --body "$(cat <<'EOF'
## Summary
- Refactored 10 high-priority files to eliminate labs imports
- Applied provider pattern and lazy loader patterns
- Created import-safety tests for all modified modules

## Validation
- ✅ All syntax checks passing
- ✅ Lane-guard: Zero violations
- ✅ Import-safety tests: 10/10 passing
- ✅ Smoke tests: All passing
- ✅ Unit tests: No regressions

## Files Modified
1. core/colony/gpt_colony_orchestrator.py
2. core/orchestration/brain/consciousness_core.py
3. core/orchestration/brain/neural/cognitive_core.py
4. core/governance/unified_constitutional_ai.py
5. core/identity/lambda_id.py
6. core/observability/telemetry_manager.py
7. serve/api/routes/consciousness.py
8. serve/api/routes/memory.py
9. lukhas_website/backend/api.py
10. lukhas_website/frontend/components/ConsciousnessMonitor.tsx

## Tests Created
- tests/integration/test_gpt_colony_orchestrator_importsafe.py
- tests/integration/test_consciousness_core_importsafe.py
- tests/integration/test_cognitive_core_importsafe.py
- tests/integration/test_unified_constitutional_ai_importsafe.py
- tests/integration/test_lambda_id_importsafe.py
- tests/integration/test_telemetry_manager_importsafe.py
- tests/integration/test_consciousness_routes_importsafe.py
- tests/integration/test_memory_routes_importsafe.py
- tests/integration/test_website_api_importsafe.py
- tests/integration/test_website_monitor_importsafe.py

## Related Work
- Codex batch automation: #807 #808 #809 #810
- Gemini infrastructure: Coverage, SLSA, monitoring

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```
