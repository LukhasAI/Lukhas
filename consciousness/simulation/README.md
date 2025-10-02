# Simulation Lane (T4/0.01%)

Sandboxed simulation lane for LUKHΛS consciousness: safe dream execution with compound defensive controls.

## Features

- **Feature Flag Gating**: `SIMULATION_ENABLED` env var must be explicitly enabled
- **Ethics Gate**: Blocks duress conditions, validates consent scopes, rejects unsafe goals
- **Adapter Isolation**: Zero imports from adapter layers (verified by canary test)
- **MATADA Envelope**: Structured nodes with `schemas/matriz_node_v1.json` validation
- **Deterministic Scoring**: Heuristic variants (optimistic/baseline/adversarial) for golden tests

## API

```python
from consciousness.simulation.api import schedule, status, collect, DreamSeed

# Schedule simulation
seed: DreamSeed = {
    "goal": "Evaluate onboarding flow for new ΛID users",
    "context": {"tenant": "demo", "redacted_user_count": 5},
    "constraints": {
        "budgets": {"tokens": 1500, "seconds": 1.0, "max_rollouts": 3},
        "consent": {"scopes": ["simulation.read_context"]},
        "flags": {"duress_active": False},
    },
}

job_id = await schedule(seed)

# Poll status
st = await status(job_id)  # {"state": "running", "progress": 0.5, ...}

# Collect results
result = await collect(job_id)
# {
#   "shards": [...],          # 3 dream shards with proposals
#   "scores": {...},          # aggregate utility/risk/novelty
#   "trace_id": "LT-abc123",
#   "matada_nodes": [...],    # validated MATRIZ nodes
#   "schema_ref": "lukhas://schemas/matriz_node_v1.json"
# }
```

## Ethics & Consent

**Required consent scope**: `simulation.read_context`

**Forbidden scopes**: `adapter.write`, `email.send`, `cloud.delete`

**Blocked conditions**:
- Duress/shadow active (`flags.duress_active`)
- Missing consent scope
- Unsafe goal keywords (e.g., "self-delete", "exfiltrate")

## MATADA Nodes

Each rollout emits a MATRIZ node with:
- Unique ID: `{trace_id}#N{order}`
- Type: `advisory.plan`
- Lane: `simulation`
- Provenance: generator, input keys, timestamp
- Payload: goal, assumptions, scores, plan steps

Validated against `schemas/matriz_node_v1.json`.

## Testing

```bash
# Run canary tests
SIMULATION_ENABLED=true make t4-sim-lane

# Tests cover:
# - Happy path (schedule → collect)
# - Consent denial
# - Duress detection
# - Feature flag enforcement
# - Adapter isolation (no forbidden imports)
```

## Commands

```bash
# Bootstrap (if not already done)
bash .claude/commands/91_sim_lane_bootstrap.yaml

# Apply CI env guards
bash .claude/commands/92_sim_lane_ci_env.yaml

# Scan for legacy dream callers (dry-run)
bash .claude/commands/93_sim_lane_refactor_callers.yaml

# Full validation suite
bash .claude/commands/94_sim_lane_validate.yaml
```

## Architecture

```
consciousness.simulation/
├── api.py              # Public interface (schedule, status, collect)
├── scheduler.py        # Async job queue with progress tracking
├── ethics_gate.py      # Consent + duress validation
├── world_model.py      # Scenario generation (3 variants)
├── evaluator.py        # Deterministic scoring
├── rollout.py          # Orchestrates scenarios + scoring
└── summarizer.py       # Builds dream shards + MATADA nodes
```

## Defensive Layers

1. **Feature flag**: Killswitch at API boundary
2. **Ethics gate**: Pre-flight validation (consent, duress, goal safety)
3. **Adapter isolation**: No side-effects (verified by test)
4. **Schema validation**: MATADA nodes checked against JSON schema
5. **Determinism**: Fixed heuristics enable golden tests

## Integration Points

- **MATRIZ**: Emits structured nodes for downstream processing
- **Λ-trace**: Assigns `LT-{uuid}` trace IDs for observability
- **CI**: GitHub Actions sets `SIMULATION_ENABLED=true` for test runs

## T4/0.01% Compliance

- **Reversible**: Feature flag + isolated module
- **Auditable**: Structured provenance in every node
- **Testable**: 5 canary tests with 100% coverage of ethics paths
- **Documented**: This README + inline docstrings
- **Monitored**: Λ-trace logs at schedule/collect boundaries

---

**Owner**: Consciousness Team
**Status**: Beta (T4/0.01% compliant)
**Lane**: L2 (Deliberation)
