---
status: wip
type: documentation
---
# Oneiric Drift Dream Test CLI

The **Drift Dream Test** CLI provides a light-touch way to sample symbolic drift
for a specific dream symbol without starting the full Oneiric stack.  The tool
lives in `oneiric_core/tools/drift_dream_test.py` and is meant to support
auditors operating in the candidate lane.

## Usage

```bash
export LUKHAS_EXPERIMENTAL=1
export LUKHAS_LANE=candidate
python oneiric_core/tools/drift_dream_test.py --symbol LOYALTY --user demo --seed 7
```

### Arguments

| Flag | Description |
| ---- | ----------- |
| `--symbol` | Symbolic token to probe. |
| `--user` | Requesting user identifier. |
| `--seed` | Optional deterministic seed for repeatable runs. |
| `--recursive` | Enable recursive traversal simulation. |

## Output

The CLI prints a JSON blob to stdout and writes the same payload to
`codex_artifacts/dream_drift_report.json`.  The payload contains the following
keys:

- `symbol`, `user`, `seed`, `recursive`, `timestamp`
- `driftDelta`, `driftScore`, `affect_delta`, `collapseHash`
- `top_symbols`: ranked related symbols surfaced by the probe
- `telemetry`: counters `{attempts, successes, denials}` and `p95_latency_ms`

These fields satisfy the drift guardrails defined for the Codex Batch Worker
plan, ensuring auditors have immediate access to drift deltas, affect deltas,
and the symbolic leaderboard for the requested token.

## Testing

Symbolic regression tests live in `tests/oneiric_core/test_drift_dream_test_cli.py`.
Run them with:

```bash
pytest -q tests/oneiric_core/test_drift_dream_test_cli.py
```

The suite confirms deterministic output when a seed is provided and validates
that reports are written to the expected artifact location.
