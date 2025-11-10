# Self-Evolution Framework - Beyond Self-Healing

**Status**: 🟡 **READY FOR STAGE A** (2025-11-10)

---

## Philosophy

**Self-healing** fixes what's broken. **Self-evolution** improves what works.

But evolution without guardrails is chaos. This framework provides a **staged progression** from safe test enrichment to controlled algorithmic improvement, with hard red lines preventing unbounded autonomy.

---

## The Four Stages

### Stage A — Autodidactic Test Enrichment ✅ SAFE

**Scope**: Add tests only. NO production code changes.

**What it does**:
- Mine uncovered hot paths → open "add tests" PRs
- Generate metamorphic tests (round-trip, idempotence, schema invariants)
- Promote repeated human fixes into deterministic playbooks (no LLM)

**Guardrails**:
- ✅ Only creates test files in `tests/`
- ✅ No changes to production code (`lukhas/`, `matriz/`, `core/`, `serve/`)
- ✅ No changes to protected files
- ✅ Max 2 test files per PR

**Tools**:
- `tools/evolve_candidates.py` - Find low-coverage + high-hotness modules
- `make artifacts` - Generate coverage reports
- JUnit events from `tests/conftest.py` - Learn from failures

**Example**:
```bash
# Find top 50 evolution candidates
python tools/evolve_candidates.py > reports/evolve_candidates.json

# Review candidates
jq -r '.[] | "\(.file) - coverage: \(.coverage_score), lines: \(.lines)"' reports/evolve_candidates.json | head -10

# Delegate to Claude.ai or Jules
# Prompt: "Add comprehensive tests for the top 5 candidates with lowest coverage"
```

**Success Metrics**:
- Coverage increases: lukhas/serve (50% → 75%), matriz (30% → 60%)
- No production code modified
- All new tests pass
- Mutation score improves (mutmut)

---

### Stage B — Safe Refactor Evolution 🟡 CONTROLLED

**Scope**: Syntactic refactors & dead-code deletions behind equivalence checks.

**What it does**:
- Rename variables/functions for clarity
- Extract repeated code into helper functions
- Remove unreachable code (detected by coverage)
- Simplify complex boolean expressions
- Convert to modern Python idioms (list comprehensions, f-strings)

**Guardrails**:
- ✅ Require unchanged public API (no signature changes)
- ✅ Coverage must stay equal or increase
- ✅ Mutation score must stay ≥ baseline
- ✅ Max 2 files, ≤40 LOC per PR
- ✅ No changes to protected modules
- ✅ Must pass all existing tests

**Pre-conditions**:
- Stage A completed (coverage ≥50% for target module)
- Golden tests exist (deterministic trace validation)
- Mutation baseline recorded

**Example**:
```python
# Before (refactor candidate)
def process_data(x):
    if x is not None:
        if x > 0:
            return x * 2
        else:
            return 0
    else:
        return 0

# After (Stage B refactor)
def process_data(x: int | None) -> int:
    """Double positive values, return 0 otherwise."""
    return x * 2 if x and x > 0 else 0
```

**Success Metrics**:
- Code complexity reduced (cyclomatic complexity ≤10)
- Maintainability index improved
- No behavior changes (golden tests pass)
- No performance regression

---

### Stage C — Algorithmic Evolution 🔴 SANDBOXED

**Scope**: Performance/robustness improvements in non-critical modules.

**What it does**:
- Optimize hot paths (replace O(n²) with O(n log n))
- Add caching/memoization
- Parallelize independent operations
- Improve error handling (replace broad except with specific)
- Add retry logic with exponential backoff

**Guardrails**:
- ✅ Offline benches required (pytest-benchmark/asv)
- ✅ Merge only if:
  - All invariants hold (golden tests pass)
  - Mutation score ≥ baseline
  - Performance budget improved (e.g., −15% p95 latency)
  - Blast radius low (non-critical module)
  - ADR (Architecture Decision Record) written
  - Two-key human review
- ✅ Canary deployment to 10% before full rollout
- ✅ Auto-rollback if canary fails

**Pre-conditions**:
- Stage B completed (clean, well-tested code)
- Benchmark harness exists
- Performance baseline recorded
- Rollback plan documented

**Example**:
```python
# Before (performance candidate)
def find_duplicates(items: list[str]) -> set[str]:
    dups = set()
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other:
                dups.add(item)
    return dups

# After (Stage C optimization)
from collections import Counter

def find_duplicates(items: list[str]) -> set[str]:
    """Find duplicates in O(n) time using Counter."""
    return {item for item, count in Counter(items).items() if count > 1}
```

**Success Metrics**:
- p95 latency reduced by ≥15%
- Memory usage reduced or stable
- Throughput increased ≥10%
- All invariants preserved
- Canary deployment successful

---

### Stage D — Emergent Behavior Discovery 🟣 RESEARCH MODE

**Scope**: Exploration. **NEVER auto-merge**.

**What it does**:
- Fuzzing + chaos with invariant oracles
- Log novel capabilities as hypotheses
- Explore unexpected interaction patterns
- Generate property-based test candidates
- Discover edge cases and corner conditions

**Guardrails**:
- ✅ Runs in isolated sandbox (no production access)
- ✅ All outputs are hypotheses, not proofs
- ✅ Human decides whether to harden into specs/tests
- ✅ Treat "emergence" as working theory, never fact
- ✅ Requires ADR + full system review before ANY code integration

**Tools**:
- Hypothesis (property-based testing)
- Atheris (fuzzing)
- Chaos Toolkit (chaos engineering)
- Custom invariant oracles

**Example Workflow**:
1. Fuzz API endpoints with random inputs
2. Log unexpected behaviors (e.g., "endpoint returns 200 for malformed JSON")
3. Human reviews logs and decides:
   - Is this a bug? → Create issue
   - Is this a feature? → Write spec + tests
   - Is this undefined? → Document as out-of-scope

**Success Metrics**:
- Novel edge cases discovered
- Coverage gaps identified
- Hypothesis catalog maintained
- Zero auto-merged code (100% human gate)

---

## Tools & Infrastructure

### 1. Drop-in Test Hooks (No Per-Test Edits)

**`tests/conftest.py`** provides automatic:
- ✅ Failure capture to NDJSON events
- ✅ Deterministic runs (seeded random, frozen time)
- ✅ Network blocking by default
- ✅ Signature hashing for deduplication

**Usage**:
```bash
# Deterministic run (default)
pytest -q --junitxml=reports/junit.xml

# Review events
cat reports/events.ndjson | jq .

# Override determinism
FREEZE_TIME=0 ALLOW_NET=1 pytest -q
```

**Event Schema**:
```json
{
  "ts": "2025-11-10T12:34:56Z",
  "suite": "unit",
  "test_id": "tests/unit/test_foo.py::test_bar",
  "file": "tests/unit/test_foo.py",
  "error_class": "AssertionError",
  "message": "assert 1 == 2",
  "stack": "...",
  "repro_cmd": "pytest -q tests/unit/test_foo.py::test_bar",
  "seed": 1337,
  "env": {
    "PYTHONHASHSEED": "0",
    "FREEZE_TIME": "1",
    "ALLOW_NET": "0"
  },
  "signature": "a1b2c3d4e5f6g7h8"
}
```

### 2. Evolution Candidates Finder

**`tools/evolve_candidates.py`** identifies:
- Low coverage modules (coverage_score ≤50)
- High hotness (many git blame lines = active development)

**Usage**:
```bash
# Find top 50 candidates
python tools/evolve_candidates.py > reports/evolve_candidates.json

# Review top 10
jq -r '.[:10][] | "\(.file) - coverage: \(.coverage_score)%, lines: \(.lines)"' reports/evolve_candidates.json

# Delegate to Claude.ai
# "Add tests for these 10 modules with lowest coverage"
```

### 3. Benchmark Harness (Stage C)

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "-q --disable-warnings --maxfail=1"

[tool.pytest-benchmark]
min_rounds = 10
warmup = true
```

Create `tests/bench/test_<module>_bench.py`:
```python
import pytest

def test_find_duplicates_performance(benchmark):
    items = ["a", "b", "c"] * 1000
    result = benchmark(find_duplicates, items)
    assert len(result) == 3
```

Run benchmarks:
```bash
pytest tests/bench --benchmark-only --benchmark-json=reports/bench.json
```

Gate merges on p95 delta:
```bash
python tools/compare_bench.py --baseline reports/bench_baseline.json --current reports/bench.json
# Exit 1 if p95 regression >5%
```

---

## Red Lines (Never Cross)

### 🚫 NEVER Auto-Merge
- Behavior-changing patches in protected/public APIs
- Changes to identity, auth, security modules
- Schema migrations
- Database operations
- Network protocol changes

### 🚫 NEVER Skip
- Tests-first rule for anything beyond self-healing
- Two-key approval for protected modules
- ADR documentation for algorithmic changes
- Canary deployment for performance changes
- Rollback plan for risky changes

### 🚫 NEVER Trust
- Emergent behavior without invariant proofs
- LLM-generated code without human review
- Performance claims without benchmarks
- "It works on my machine" without CI validation

---

## Metrics Gates for Evolution

### Stage A: Test Enrichment
- ✅ Coverage increase ≥5% per PR
- ✅ All new tests pass
- ✅ No production code modified
- ✅ Mutation score improves or stays stable

### Stage B: Refactor Evolution
- ✅ Coverage ≥ baseline (no decrease)
- ✅ Mutation score ≥ baseline
- ✅ Cyclomatic complexity reduced
- ✅ All golden tests pass (no behavior change)
- ✅ Public API unchanged

### Stage C: Algorithmic Evolution
- ✅ All invariants hold (property-based tests pass)
- ✅ Mutation score ≥ baseline
- ✅ Performance budget improved:
  - p50 latency: ≤5% regression OK, ≥10% improvement required
  - p95 latency: ≤2% regression OK, ≥15% improvement required
  - p99 latency: ≤1% regression OK, ≥20% improvement required
  - Memory: ≤10% increase OK
  - Throughput: ≥10% increase required
- ✅ Blast radius: LOW (non-critical module)
- ✅ Canary: GREEN (10% rollout successful)
- ✅ Rollback: TESTED (can revert in <5 min)

### Stage D: Emergence Discovery
- ✅ 100% human gate (zero auto-merge)
- ✅ Hypothesis catalog maintained
- ✅ Novel behaviors documented
- ✅ Sandbox isolation verified

---

## Workflow Examples

### Stage A: Add Tests (Safe)

```bash
# 1. Find candidates
python tools/evolve_candidates.py > reports/evolve_candidates.json

# 2. Review top 10
jq -r '.[:10][] | "\(.file) - coverage: \(.coverage_score)%"' reports/evolve_candidates.json

# 3. Delegate to Claude.ai
cat <<EOF | pbcopy
I need comprehensive tests for these modules with low coverage:

$(jq -r '.[:10][] | "- \(.file) (coverage: \(.coverage_score)%)"' reports/evolve_candidates.json)

For each module:
1. Read the source code
2. Write unit tests covering:
   - Happy path (expected behavior)
   - Edge cases (empty, None, boundary values)
   - Error cases (invalid inputs, exceptions)
   - Integration tests if it interacts with other modules
3. Aim for 80%+ coverage
4. Use deterministic inputs (no random values)
5. Run pytest and verify all pass

Create 1 PR per module, max 2 test files per PR.
EOF

# 4. Paste into Claude.ai and let it work
```

### Stage B: Safe Refactor (Controlled)

```bash
# 1. Ensure coverage baseline exists
pytest --cov=lukhas.serve --cov-report=term --cov-report=json:reports/coverage_baseline.json

# 2. Ensure mutation baseline exists
mutmut run --paths-to-mutate=lukhas/serve
mutmut junitxml > reports/mutmut_baseline.xml

# 3. Create refactor PR
git checkout -b refactor/simplify-auth-logic

# 4. Make changes (extract helper, simplify conditionals)
# ... edit code ...

# 5. Validate metrics
pytest --cov=lukhas.serve --cov-report=json:reports/coverage_current.json
python tools/compare_coverage.py --baseline reports/coverage_baseline.json --current reports/coverage_current.json
# Must show: coverage ≥ baseline

mutmut run --paths-to-mutate=lukhas/serve
mutmut junitxml > reports/mutmut_current.xml
python tools/compare_mutmut.py --baseline reports/mutmut_baseline.xml --current reports/mutmut_current.xml
# Must show: mutation score ≥ baseline

# 6. Create PR
gh pr create --title "refactor(serve): simplify auth validation logic" \
  --body "Extracted helper functions, reduced cyclomatic complexity from 15 to 8. Coverage: 72% → 72%. Mutation score: 85% → 86%."
```

### Stage C: Performance Evolution (Sandboxed)

```bash
# 1. Baseline benchmark
pytest tests/bench/test_search_bench.py --benchmark-json=reports/bench_baseline.json

# 2. Implement optimization
git checkout -b perf/optimize-search-algorithm

# ... replace linear search with binary search ...

# 3. Benchmark new version
pytest tests/bench/test_search_bench.py --benchmark-json=reports/bench_current.json

# 4. Validate improvement
python tools/compare_bench.py --baseline reports/bench_baseline.json --current reports/bench_current.json
# Must show: p95 latency reduced ≥15%

# 5. Validate invariants
pytest tests/unit/test_search.py --hypothesis-show-statistics
# All property-based tests must pass

# 6. Write ADR
cat > docs/adr/0042-optimize-search-algorithm.md <<EOF
# ADR-0042: Optimize Search Algorithm

## Context
Linear search in hot path causing p95 latency of 250ms.

## Decision
Replace linear search with binary search (requires sorted input).

## Consequences
- p95 latency: 250ms → 15ms (-94%)
- Memory: stable (pre-sort overhead negligible)
- Requires sorted input (added validation)
- Breaking change: input must be sorted

## Rollback
Revert commit abc123, redeploy previous version.

## Canary Plan
Deploy to 10% traffic for 24h, monitor p95 latency and error rate.
EOF

# 7. Create PR with canary plan
gh pr create --title "perf(search): replace linear with binary search" \
  --body "See ADR-0042. p95: 250ms → 15ms (-94%). Canary: 10% for 24h."
```

### Stage D: Emergence Discovery (Research)

```bash
# 1. Run fuzzing in sandbox
docker run --rm -v $(pwd):/app lukhas-fuzzer \
  pytest tests/fuzz --hypothesis-seed=1337 --hypothesis-max-examples=10000

# 2. Review hypothesis database
cat .hypothesis/examples/* | jq -r '.examples[] | select(.status == "interesting")'

# 3. Log novel behaviors
cat > reports/emergence_2025-11-10.md <<EOF
# Emergence Discovery Log - 2025-11-10

## Novel Behavior 1: Unexpected 200 for Malformed JSON
**Input**: `{"user": {"name": "Alice", "age": "invalid"}}`
**Expected**: 400 Bad Request
**Actual**: 200 OK with `age=0`
**Hypothesis**: Age validation is silently coercing invalid strings to 0
**Action**: Bug or feature? Needs human review.

## Novel Behavior 2: Recursive Loop on Self-Reference
**Input**: `{"parent_id": "self"}`
**Expected**: Validation error
**Actual**: RecursionError after 998 iterations
**Hypothesis**: Missing self-reference check in parent resolution
**Action**: Add validation + test
EOF

# 4. Human review
# Read reports/emergence_2025-11-10.md
# Decide: bug fix, feature spec, or out-of-scope
```

---

## Configuration

### pytest.ini (Self-Healing Hooks)

Added to existing config:
```ini
junit_family = xunit2
timeout = 30
```

### pyproject.toml (Benchmark Support)

Add if using Stage C:
```toml
[tool.pytest.ini_options]
addopts = "-q --disable-warnings --maxfail=1"

[tool.pytest-benchmark]
min_rounds = 10
warmup = true
min_time = 0.001
```

---

## Current Status

| Stage | Status | Coverage Target | Tools Ready | Guardrails |
|-------|--------|----------------|-------------|------------|
| **A: Test Enrichment** | ✅ READY | 50% → 75% | ✅ evolve_candidates.py | ✅ Max 2 files |
| **B: Refactor Evolution** | 🟡 NEEDS COVERAGE | ≥50% baseline | 🟡 Need compare scripts | ✅ Metrics gates |
| **C: Algorithmic Evolution** | 🔴 NOT READY | ≥70% baseline | 🔴 Need benchmark harness | ✅ ADR + 2-key |
| **D: Emergence Discovery** | 🔴 RESEARCH ONLY | N/A | 🟡 Hypothesis ready | ✅ 100% human gate |

---

## Next Actions

### Immediate (Stage A - This Week)

1. ✅ Run `python tools/evolve_candidates.py`
2. ✅ Delegate top 10 to Claude.ai for test creation
3. ✅ Review PRs and merge
4. ✅ Track coverage improvements

### Short-Term (Stage B - Next 2 Weeks)

1. 🟡 Achieve 50%+ coverage on lukhas/serve
2. 🟡 Record mutation baseline with mutmut
3. 🟡 Create coverage/mutation comparison scripts
4. 🟡 Enable Stage B for low-risk refactors

### Medium-Term (Stage C - Next Month)

1. 🔴 Set up pytest-benchmark harness
2. 🔴 Record performance baselines
3. 🔴 Write ADR template for algorithmic changes
4. 🔴 Test canary deployment workflow

### Long-Term (Stage D - Research Track)

1. 🔴 Set up fuzzing sandbox
2. 🔴 Deploy Hypothesis property-based testing
3. 🔴 Create invariant oracle framework
4. 🔴 Establish hypothesis review process

---

## Related Documentation

- [SELF_HEALING_QUICKSTART.md](SELF_HEALING_QUICKSTART.md) - Self-healing infrastructure
- [SELF_HEAL_DEPLOYMENT_COMPLETE.md](SELF_HEAL_DEPLOYMENT_COMPLETE.md) - Deployment summary
- [MISSING_TESTS_DELEGATION_GUIDE.md](MISSING_TESTS_DELEGATION_GUIDE.md) - Test creation batches
- [tests/conftest.py](tests/conftest.py) - Drop-in test hooks
- [tools/evolve_candidates.py](tools/evolve_candidates.py) - Evolution candidates finder

---

**TL;DR**: Start with Stage A (add tests safely). Don't rush to Stage C (algorithmic changes). Treat Stage D (emergence) as hypothesis generation, never autopilot.

---

*Generated 2025-11-10 by Claude Code*
