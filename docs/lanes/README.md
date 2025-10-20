# LUKHAS Lane System

This document describes lane definitions, generator usage, and CI gates for Phase 4.

- Lanes:
  - candidate: development/research
  - integration: shared infra and promoted modules
  - production: LUKHAS production lane

- Generator:
  - `python scripts/phase4_generate_lane_yaml.py --manifests manifests --prefer-labs --overwrite`
  - Idempotent: subsequent runs yield no diffs. CI enforces up-to-date lane YAMLs.

- CI Gates:
  - Schema validation: `schema/module.lane.schema.json`
  - Idempotency: regen lane YAMLs then `git diff --quiet`
  - Lane guard: forbid candidate→production and production→candidate imports (simple grep)

- Make targets:
  - `make phase4-preflight`
  - `make phase4-canary`
  - `make phase4-manifests`
  - `make phase4-validate`
  - `make phase4-all`

