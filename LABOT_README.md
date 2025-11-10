# ΛBot - Stage A Test Orchestration Agent

**Version**: v0.1
**Status**: 🟢 **READY**
**Purpose**: Systematic test enrichment with zero production code changes

---

## What is ΛBot?

ΛBot is a **small, opinionated Stage-A orchestration agent** that:
1. **Scouts** the repo for high-value test targets (low coverage + high activity)
2. **Prepares** agent-ready prompts (specialized per module type)
3. **Opens** PR shells for Claude Code Web or Jules to fill with tests
4. **Enforces** zero production code changes (tests only)

**Philosophy**: Maximum leverage with minimal drama. ΛBot doesn't write tests - it orchestrates human/AI test creation systematically.

---

## Quick Start

### 1. Find Top Test Targets

```bash
# Find top 15 targets (default)
make labot-plan

# Find top 5 targets
python3 tools/labot.py --mode plan --top 5
```

**Output**: `reports/evolve_candidates.json`
```json
[
  {
    "score": 87.45,
    "path": "serve/main.py",
    "coverage": 35.2,
    "hot_lines": 456,
    "tier": 1
  },
  ...
]
```

**Scoring**: `0.55 * (100 - coverage) + 0.30 * hotness + 0.15 * tier_bonus`
- **Low coverage**: 65% weight (prefers untested code)
- **Hotness**: 30% weight (git blame line count as proxy for activity)
- **Tier**: 15% weight (serve/lukhas > matriz > core)

### 2. Generate Agent-Ready Prompts

```bash
# Generate prompts + PR shells for all targets
make labot-gen

# Or use the script
./scripts/run_labot.sh
```

**Creates**:
- `prompts/labot/<slug>.md` - Specialized test surgeon prompts
- `requests/labot/<slug>.pr.yml` - PR title/body templates
- `reports/evolve_candidates.json` - Ranked targets

### 3. Use the Prompts

**Option A: Manual (Copy-Paste to Claude.ai)**
```bash
# Read the prompt
cat prompts/labot/serve_main.md

# Copy to Claude.ai or Claude Code Web
# Paste the full prompt and let it create tests
```

**Option B: PR Shell (Automated Workflow)**
```bash
# Open a PR shell for a specific target
make labot-open slug=serve_main

# This creates:
# 1. New branch: labot/tests/serve_main
# 2. Docs placeholder: docs/labot/serve_main.md
# 3. PR with test requirements
# 4. Claude Code Web can then add tests to the PR
```

---

## Configuration

**File**: `.labot/config.yml`

```yaml
# Protected files (requires two-key approval for changes)
protected_globs:
  - "serve/identity_api.py"
  - "serve/middleware/strict_auth.py"
  - "lukhas/identity/**"
  - "core/security/**"

# Scoring weights (0..1)
weights:
  low_coverage: 0.55    # Prefer low-coverage files
  hotness: 0.30         # Prefer high-activity files
  tier_bias: 0.15       # Prefer Tier 1 modules

# Tiers (1=highest priority)
tiers:
  serve: 1
  lukhas: 1
  matriz: 2
  core: 3

# Planning
plan:
  top_n: 15             # How many targets per run
  exclude_globs: []     # Optional: ["**/migrations/**"]
```

---

## Prompt Templates

ΛBot generates **specialized prompts** based on module type:

### SERVE modules (FastAPI endpoints)
```markdown
# LUKHΛS Test Surgeon — SERVE module

**File:** `serve/main.py`
**Goal:** 85%+ coverage, deterministic, no network

## Must test
- All FastAPI routes and methods
- Auth/headers/middleware (401/403, CORS)
- Request validation (invalid payloads)
- Response schema (OpenAPI compatibility)
- Streaming / SSE if applicable

## Constraints
- No sleeps; freeze time and pin seeds
- Mock external services (LLMs, stores)
```

### LUKHAS modules (Identity/Auth)
```markdown
# LUKHΛS Test Surgeon — LUKHAS module

**File:** `lukhas/identity/core.py`
**Goal:** 85%+ coverage, deterministic, no network

Focus:
- WebAuthn / JWT flows (positive + negative)
- Feature flags CRUD & evaluation
- Privacy-preserving analytics (no PII)

Constraints:
- No auth weakening; no snapshot loosening
- Mock external backends
```

### MATRIZ modules (Cognitive Engine)
```markdown
# LUKHΛS Test Surgeon — MATRIZ module

**File:** `matriz/core/engine.py`
**Goal:** ≥70% coverage with metamorphic checks

Focus:
- Pipeline invariants (consistent phase transitions)
- Round-trips / idempotence for symbolic structures
- Error handling for degenerate inputs

Constraints:
- No network; freeze time; pin seeds
- Mock LLM/vector store calls
```

---

## Workflow Examples

### Example 1: Manual Test Creation with Claude.ai

```bash
# 1. Generate prompts
make labot-gen

# 2. Review top targets
cat reports/evolve_candidates.json | jq -r '.[:5][] | "\(.path) - \(.coverage)%"'

# 3. Copy prompt for top target
cat prompts/labot/serve_main.md

# 4. Paste into Claude.ai
# "Here's a test surgeon prompt for serve/main.py..."

# 5. Claude creates test file
# tests/unit/serve/test_main.py

# 6. Create PR manually
git checkout -b test/serve-main
git add tests/unit/serve/test_main.py
git commit -m "test(serve): add comprehensive tests for main.py"
gh pr create --title "test(serve): add tests for main.py"
```

### Example 2: Automated PR Shell

```bash
# 1. Generate prompts
make labot-gen

# 2. Open PR shell for serve/main.py
make labot-open slug=serve_main

# This automatically:
# - Creates branch: labot/tests/serve_main
# - Creates docs placeholder
# - Opens PR with requirements
# - PR body contains link to prompt

# 3. Claude Code Web sees the PR
# 4. Reads prompt from prompts/labot/serve_main.md
# 5. Adds test file to the PR
# 6. All tests pass → merge
```

### Example 3: Batch Processing with Jules

```python
from bridge.llm_wrappers.jules_wrapper import JulesClient
import json

# Read top 5 targets
with open("reports/evolve_candidates.json") as f:
    targets = json.load(f)[:5]

async with JulesClient() as jules:
    for target in targets:
        slug = target["path"].replace("/", "_").replace(".py", "")
        prompt = open(f"prompts/labot/{slug}.md").read()

        session = await jules.create_session(
            prompt=prompt,
            source_id="sources/github/LukhasAI/Lukhas",
            automation_mode="AUTO_CREATE_PR"
        )
        print(f"Created Jules session for {target['path']}")
```

---

## Directory Structure

```
.labot/
  config.yml                 # ΛBot configuration

prompts/labot/              # Auto-generated prompts
  serve_main.md             # Test surgeon prompt for serve/main.py
  serve_identity_api.md     # Test surgeon prompt for serve/identity_api.py
  ...

requests/labot/             # PR shells
  serve_main.pr.yml         # PR title/body for serve/main.py
  ...

docs/labot/                 # PR placeholders
  serve_main.md             # Created when opening PR shell
  ...

reports/
  evolve_candidates.json    # Ranked test targets

tools/
  labot.py                  # ΛBot core planner/generator

scripts/
  run_labot.sh              # Quick start script

.github/workflows/
  labot_plan.yml            # Nightly CI planner
```

---

## Makefile Targets

```bash
make labot-plan       # Find top test targets
make labot-gen        # Generate prompts + PR shells
make labot-all        # Alias for labot-gen
make labot-open slug=<slug>  # Open PR shell
```

---

## CI Integration

**Workflow**: `.github/workflows/labot_plan.yml`

**Schedule**: Daily at 02:23 UTC

**What it does**:
1. Generate coverage report
2. Run ΛBot planner
3. Upload candidates as artifact
4. Review artifact to see top targets

**Manual trigger**:
```bash
gh workflow run "ΛBot Planner"
```

---

## Guardrails

### ✅ Stage A Rules (Enforced by ΛBot)

- **Tests only**: No production code changes
- **Protected files**: No modifications to identity/auth modules
- **Deterministic**: Freeze time, pin seeds, no sleeps
- **Mocked IO**: No network calls, mock LLMs/stores
- **Coverage targets**: 85% for serve/lukhas, 70% for matriz

### ❌ NOT Allowed

- Modifying serve/*.py, lukhas/*.py, matriz/*.py files
- Changing protected files (identity_api, strict_auth)
- Adding new dependencies
- Widening try/except blocks
- Deleting existing tests
- Performance optimizations (Stage C only)

---

## Integration with Self-Healing Loop

ΛBot works seamlessly with the self-healing infrastructure:

1. **Event Capture**: Tests created by ΛBot prompts automatically capture failures to `reports/events.ndjson`
2. **Determinism**: All prompts enforce `PYTEST_SEED=1337` and frozen time
3. **Network Blocking**: Tests use `ALLOW_NET=0` by default
4. **Policy Enforcement**: `make policy` validates patch size and protected files
5. **Memory Healix**: Failed tests feed into the learning loop

**Workflow**:
```
ΛBot generates prompt → Claude creates tests → Tests run → Failures captured → Memory Healix learns → Future prompts improve
```

---

## Scoring Algorithm

ΛBot ranks files using a weighted score:

```python
score = (
    0.55 * (100 - coverage)  # Low coverage = high priority
    + 0.30 * min(hot_lines, 500) / 500 * 100  # High activity = high priority
    + 0.15 * (4 - tier) * 33.3  # Tier 1 > Tier 2 > Tier 3
)
```

**Example**:
```
serve/main.py:
  coverage = 35%
  hot_lines = 456
  tier = 1

score = 0.55 * (100 - 35) + 0.30 * (456/500) * 100 + 0.15 * 3 * 33.3
      = 0.55 * 65 + 0.30 * 91.2 + 15.0
      = 35.75 + 27.36 + 15.0
      = 78.11  (HIGH PRIORITY)
```

---

## Troubleshooting

### ΛBot doesn't find any targets

**Cause**: No coverage.xml file exists

**Fix**:
```bash
# Generate coverage manually
pytest --cov=. --cov-report=xml:reports/coverage.xml -q

# Then run ΛBot
make labot-plan
```

### Prompts are generic/not specialized

**Cause**: File path doesn't match tier patterns

**Fix**: Update `.labot/config.yml` tiers to match your directory structure

### PR shell creation fails

**Cause**: `gh` CLI not installed or not authenticated

**Fix**:
```bash
# Install gh CLI
brew install gh  # macOS
# or: sudo apt install gh  # Ubuntu

# Authenticate
gh auth login
```

### Coverage score seems wrong

**Cause**: coverage.xml format may vary by pytest-cov version

**Fix**: ΛBot uses line-rate from coverage.xml - check file format:
```bash
cat reports/coverage.xml | grep 'line-rate' | head -5
```

---

## Extending ΛBot

### Add New Prompt Template

Edit `tools/labot.py`:
```python
PROMPT_TEMPLATE_MY_MODULE = """\
# LUKHΛS Test Surgeon — MY MODULE

**File:** `{path}`
**Goal:** {cov_goal}%+ coverage

Custom instructions here...
"""

def prompt_template_for(path: str) -> tuple[str,str]:
    if path.startswith("mymodule/"):
        return PROMPT_TEMPLATE_MY_MODULE, "mymodule"
    # ... existing templates
```

### Change Scoring Weights

Edit `.labot/config.yml`:
```yaml
weights:
  low_coverage: 0.70  # Increase coverage weight
  hotness: 0.20       # Decrease activity weight
  tier_bias: 0.10     # Decrease tier weight
```

### Add Exclusions

Edit `.labot/config.yml`:
```yaml
plan:
  exclude_globs:
    - "**/migrations/**"
    - "**/legacy/**"
    - "tools/**"
```

---

## Metrics & Success

### Track Progress

```bash
# Check coverage improvements over time
pytest --cov=serve --cov-report=term | grep "^TOTAL"

# Before ΛBot: 35%
# After Batch 1: 55%
# After Batch 2: 75%
```

### Measure Impact

```bash
# Count tests created via ΛBot
find tests/ -name "*.py" -newer .labot/config.yml | wc -l

# Count PRs from ΛBot
gh pr list --label "labot" --state merged
```

---

## Relationship to Other Bots

| Bot | Purpose | Stage | Auto-Merge |
|-----|---------|-------|------------|
| **ΛBot** | Test orchestration | A | No (tests only) |
| **Jules** | Automated test writing | A | Yes (via API) |
| **CODEX** | Auto-fix code issues | B/C | Conditional |
| **Test Surgeon** | Manual test creation | A | No (human) |
| **Memory Healix** | Failure learning loop | - | No (learning) |

**ΛBot's role**: Orchestrate test creation by other agents/humans, not write tests itself.

---

## Next Steps

### Immediate (This Week)

1. Run `make labot-gen` to generate prompts
2. Review top 5 targets in `reports/evolve_candidates.json`
3. Copy prompt from `prompts/labot/` to Claude.ai
4. Create tests for serve/ modules
5. Track coverage improvements

### Short-Term (Next 2 Weeks)

1. Open PR shells for top 10 targets
2. Let Claude Code Web fill PRs with tests
3. Merge PRs as tests pass
4. Monitor coverage: serve/ 35% → 75%

### Medium-Term (Next Month)

1. Extend ΛBot to Stage B (refactor proposals)
2. Add mutation testing to scoring
3. Integrate with Jules for full automation
4. Set up nightly CI runs

---

## Status

🟢 **READY FOR PRODUCTION**

All files created and tested. ΛBot is ready to orchestrate systematic test enrichment.

**Next**: Run `make labot-gen` and start creating tests!

---

*Generated 2025-11-10 by Claude Code*
