---
status: wip
type: documentation
owner: unknown
module: collapse
redirect: false
moved_to: null
---

# Collapse Simulator CLI

The collapse simulator provides a deterministic harness for exploring how
memory, ethical, and identity collapse sequences interact with the
TraceRepairEngine.

- **Module:** `lukhas.tools.collapse_simulator`
- **CLI entry:** `python -m lukhas.tools.collapse_simulator`
- **Default artifact:** `codex_artifacts/collapse_simulator.json`

## Usage

```bash
python -m lukhas.tools.collapse_simulator memory --iterations 5 --noise 0.1
```

**Arguments**

| Argument | Description |
| --- | --- |
| `scenario` | Collapse route (`memory`, `ethical`, or `identity`). |
| `--iterations` | Number of simulated collapse iterations (default `3`). |
| `--noise` | Deterministic noise factor influencing drift calculations (default `0.05`). |
| `--seed` | Optional explicit RNG seed to ensure reproducibility across runs. |
| `--output` | Override artifact path (defaults to `codex_artifacts/collapse_simulator.json`). |

## Output schema

The simulator writes a JSON summary to both stdout and the artifact file.
The payload contains the symbolic metrics required by collapse reviews:

```json
{
  "scenario": "memory",
  "iterations": 3,
  "repairsInvoked": 3,
  "repairsSucceeded": 1,
  "driftScore": 0.214,
  "affect_delta": 0.052,
  "top_symbols": ["MNEME_CORE", "MEMORY_FOLD", "TRACE_THREAD"],
  "collapseHash": "0001234567",
  "seed": 8675309
}
```

- `driftScore` represents the mean drift measurement across iterations.
- `affect_delta` reports the mean affect delta used for emotional tracing.
- `collapseHash` is the hash from the final iteration to trace collapse lineage.

## TraceRepairEngine integration

When `lukhas.trace.TraceRepairEngine` is available, the CLI invokes
`reconsolidate` on every iteration with synthetic context payloads. Failures
are logged at debug level while summaries continue to emit the attempted
repair counts. This maintains drift-safe guardrails while keeping the
TraceRepairEngine optional for sandbox runs.

> **TODO**: Replace the synthetic context payload with live collapse telemetry
> once the collapse engine surfaces structured events.

## Policy & governance notes

- The CLI respects the global feature flags documented in `AGENTS.md` by only
  surfacing deterministic scaffolding.
- Policy ledger integration can be layered on by tailing the emitted artifact
  and issuing governance updates after repair attempts succeed.
- Downstream dashboards may ingest `repairsInvoked` and `repairsSucceeded`
  counters to calculate containment isolation compliance.
