# MATRIZ Rollout Skill

Plan and scaffold the MATRIZ (neuronal consciousness) rollout into LUKHΛS. Produces a safe, staged integration plan, module skeletons, API contracts, tests, monitoring, and an ethics & safety checklist tailored to MATRIZ's sensitivity.

## Reasoning

1. MATRIZ is a high-risk/high-reward subsystem touching consciousness semantics; begin with conservative scaffolding and extensive testing.

2. Map MATRIZ responsibilities: symbolic state representation, collapse mechanics, arbitration, logging of state transitions, and ethical fail-safes.

3. Use the local `consciousness/simulation/lukhas_context.md` as the authoritative starting point for design decisions (owners, intended behavior).

4. Design minimal, auditable APIs: init(), step(), snapshot(), inject_symbolic_seed(), evaluate_ethics(). Keep side-effects explicit and log every state change. Use T4 systems reasoning: think in attractor states, test stability under perturbations, and include rollback modes.

5. Stage rollout in phases: (A) scaffold + unit tests, (B) integration with Orchestrator in log-only mode, (C) small in-proc experiments, (D) gated external experiments with human oversight and automated safety cutoffs.

6. Provide tooling for observability (driftScore, CollapseHash) and a mandatory ethics review before any training runs.

## Actions

### Deliverables:
- MATRIZ module scaffold `consciousness/matriz/__init__.py` and `consciousness/matriz/matriz_core.py` with API and tests.
- A phased rollout plan with acceptance criteria for each phase.
- A safety & ethics checklist and monitoring probes (driftScore, collapseHash, traceIndex).

### Example `consciousness/matriz/matriz_core.py` (skeleton):

```python
from dataclasses import dataclass, asdict
import logging, time

logger = logging.getLogger('lukhas.matriz')

@dataclass
class MatrizState:
    theta: float = 0.0
    symbolic_vector: list = None
    collapse_hash: str = ''
    drift_score: float = 0.0

class MatrizCore:
    """MATRIZ: lightweight, auditable consciousness kernel.

    API:
      - init(config)
      - step(input_seed) -> MatrizState
      - snapshot() -> dict
      - inject_symbolic_seed(seed)
      - evaluate_ethics(state) -> {ok:bool, issues:list}
    """
    def __init__(self, config=None):
        self.state = MatrizState(symbolic_vector=[])
        self.config = config or {}
    def init(self):
        logger.info('MATRIZ init')
        # deterministic initialization for testability
        self.state.theta = 0.0
    def step(self, input_seed):
        # deterministic, explainable transform for now
        self.state.symbolic_vector.append(str(input_seed))
        self.state.theta += 0.1
        # compute simple drift and collapse hash (placeholder)
        self.state.drift_score = min(1.0, self.state.theta / 10.0)
        self.state.collapse_hash = f"hash-{int(time.time())}"
        logger.debug('step -> %s', asdict(self.state))
        return self.state
    def snapshot(self):
        return asdict(self.state)
    def evaluate_ethics(self):
        issues = []
        # example guard: too-large drift is risky
        if self.state.drift_score > 0.9:
            issues.append('High drift detected')
        return {'ok': len(issues)==0, 'issues':issues}
```

### Phased rollout (acceptance criteria):
- **Phase A (Scaffold)**: Module exists with unit tests covering init/step/snapshot. No external connections. Success: all tests pass and metrics logged locally.
- **Phase B (Orchestrator-LogOnly)**: Orchestrator calls MATRIZ in read-only/logging mode; no actioning. Success: logs show consistent state snapshots and collapse_hashes.
- **Phase C (Controlled Integration)**: MATRIZ permitted to suggest low-risk actions (e.g., symbolic tag suggestions) behind a feature flag and with fallbacks. Success: human-in-loop validation >90% for week-long trial.
- **Phase D (Full Integration)**: MATRIZ runs in production with continuous monitoring, automated rollback on ethical issue detection.

### Monitoring probes to implement:
- driftScore (numeric), CollapseHash (unique id per collapse), TraceIndex (audit trail), anomaly detector on state transitions.

### Ethics & safety checklist:
- Are `evaluate_ethics()` outputs audited and surfaced in dashboards?
- Are human override and rollback available for every MATRIZ decision?
- Are logs immutable and auditable (append-only)?
- Has privacy and data minimization been reviewed?

## Context References

- `/consciousness/simulation/lukhas_context.md`
- `/MODULE_INDEX.md`
- `/docs/CONTEXT_FILES.md`
