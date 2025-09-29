---
name: matrix-validate
goal: Run full MATRIZ pack: presence, schema, identity, OPA, telemetry
danger_level: low
---

## Prompt
Execute the full validation loop. Do not modify artifacts beyond tool outputs.

## Shell
```bash
set -euo pipefail
make validate-matrix-all
make authz-run
make coverage-report
```

## Acceptance

* CI-equivalent passes locally
* `tests/matrix_coverage_report.md` updated