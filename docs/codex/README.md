# Codex Execution Packages

**Purpose**: Drop-in, zero-guesswork execution playbooks for Codex AI to implement features with surgical precision

---

## Available Packages

### 1. OpenAI Façade Fast-Track

**File**: [FACADE_FAST_TRACK.md](./FACADE_FAST_TRACK.md)

**Goal**: Implement OpenAI-compatible API endpoints (`/v1/models`, `/v1/embeddings`, `/v1/responses`) with rate limit headers and deterministic behavior

**Complexity**: Low (2-4 hours with Codex)

**Deliverables**:
- 3 new OpenAI-compatible endpoints
- Rate limit headers (X-RateLimit-* + OpenAI aliases)
- Deterministic hash-based embeddings
- /health alias for ops tooling
- Smoke test pass rate: 61% → 90%+

**Tools Used**: Read, Write, Edit, Bash, Glob, Grep

**Wave A** (Required):
- Create/update `serve/openai_routes.py`
- Mount router in `serve/main.py`
- Add `/health` alias
- Run verification tests

**Wave B** (Optional, only if modules exist):
- Wire `quota_resolver` into rate limits
- Enable SSE streaming via `async_orchestrator`

---

## Package Structure

Each execution package contains:

1. **Preflight Checks** - Detect repo structure and existing files
2. **Step-by-Step Patches** - Surgical diffs with exact tool invocations
3. **Verification Commands** - Smoke tests and acceptance gates
4. **T4 Commit Templates** - Production-ready commit messages
5. **Error Recovery** - Rollback strategies if patches fail
6. **Tool Reference** - Explicit Read/Write/Edit/Bash commands
7. **Success Metrics** - Before/after state with measurable targets

---

## Tool Reference Guide

### File Operations

**Read** - Read file contents before editing
```python
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py")
```

**Write** - Create new files (routers, scripts)
```python
Write(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py",
    content=<full_content>
)
```

**Edit** - Surgical patches to existing files
```python
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="<exact match from file>",
    new_string="<replacement text>"
)
```

**Glob** - Find files by pattern
```python
Glob(pattern="**/quota_resolver.py")
Glob(pattern="serve/**/*.py")
```

**Grep** - Search file contents
```python
Grep(pattern="CognitiveOrchestrator", output_mode="files_with_matches")
Grep(pattern="def healthz", path="serve/")
```

### Execution

**Bash** - Shell commands, tests, git operations
```bash
Bash(command="pytest tests/smoke/test_models_openai_shape.py -v")
Bash(command="git add serve/ && git commit -m '...'")
Bash(command="curl -s localhost:8000/v1/models | jq")
```

**Task** - Launch specialized agents for complex workflows
```python
Task(
    prompt="Integrate ethics_swarm_colony into core/colonies/",
    subagent_type="general-purpose"
)
```

---

## Codex Workflow Pattern

### 1. Detect Repo State

```bash
# TOOL: Bash
git status
git ls-files | grep -E '^serve/.*\.py$'
```

### 2. Read Before Editing

```python
# TOOL: Read
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py")
```

### 3. Make Surgical Changes

```python
# TOOL: Edit (for existing files)
Edit(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py",
    old_string="from fastapi import FastAPI",
    new_string="from fastapi import FastAPI\nfrom serve.openai_routes import router"
)

# TOOL: Write (for new files)
Write(
    file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/openai_routes.py",
    content=<content>
)
```

### 4. Verify Changes

```bash
# TOOL: Bash
python3 -c "from serve.main import app; print('✅ Imports work')"
pytest tests/smoke/test_models_openai_shape.py -v
```

### 5. Commit with T4 Format

```bash
# TOOL: Bash
git add serve/
git commit -m "feat(api): add OpenAI-compatible endpoints (Wave A)

Problem:
...

Solution:
...

Impact:
...

Artifacts:
...

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Guidelines for Codex

### Critical Rules

1. **Always Read Before Edit** - Use `Read()` to see current file state
2. **Exact String Matching** - Edit's `old_string` must match file exactly
3. **Verify Each Step** - Run Bash commands to validate changes
4. **Test Before Commit** - pytest smoke tests must pass
5. **Surgical Diffs Only** - Minimal changes, no refactoring
6. **Use Existing Modules Only** - Don't introduce deep dependencies
7. **T4 Commit Format** - Follow format in execution packages

### Error Recovery

If Edit fails:
```python
# Check current state
Bash(command="git diff serve/main.py")

# Reset if needed
Bash(command="git checkout -- serve/main.py")

# Read full file to understand structure
Read(file_path="/Users/agi_dev/LOCAL-REPOS/Lukhas/serve/main.py")

# Try different anchor point for Edit
```

### Testing Strategy

```bash
# Unit tests for specific endpoint
Bash(command="pytest tests/smoke/test_models_openai_shape.py -v")

# Full smoke suite
Bash(command="pytest tests/smoke/ -q")

# Curl smoke test
Bash(command="curl -s localhost:8000/v1/models | jq '.object'")

# Acceptance gates
Bash(command="/tmp/acceptance_gates.sh")
```

---

## Success Criteria

Each execution package defines:

**Before State**:
- Current test pass rate
- Missing features
- Known issues

**After State**:
- Target test pass rate
- Delivered features
- Fixed issues

**Measurable Metrics**:
- Test coverage %
- Smoke pass rate
- Performance targets
- API compliance

---

## Adding New Packages

To create a new Codex execution package:

1. **Create Package File**: `docs/codex/YOUR_FEATURE_NAME.md`

2. **Include Sections**:
   - 🎯 Goal (what to achieve)
   - 📋 Tools Reference (which tools to use)
   - 0️⃣ Preflight (detection scripts)
   - 1️⃣-N️⃣ Patches (step-by-step with tool commands)
   - 🧪 Verification (tests and gates)
   - 📝 Commit (T4 template)
   - 📊 Success Metrics (before/after)

3. **Update This README**: Add to "Available Packages" section

4. **Update AGENTS.md**: Add to "Codex Execution Packages" section

---

## Links

- **AGENTS.md**: [../AGENTS.md](../../AGENTS.md) - Agent coordination system
- **Integration Manifest**: [../audits/INTEGRATION_MANIFEST_SUMMARY.md](../audits/INTEGRATION_MANIFEST_SUMMARY.md) - 193 hidden gems
- **Audit Ready Summary**: [../audits/AUDIT_READY_SUMMARY_20251022.md](../audits/AUDIT_READY_SUMMARY_20251022.md) - Audit preparation

---

**Codex execution packages provide zero-guesswork, surgical playbooks for implementing features with explicit tool commands, verification steps, and measurable success criteria.**
