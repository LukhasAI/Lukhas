---
title: Gates Tails Addition 2025 09 04
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["testing", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic"]
  audience: ["dev"]
---

Quick gates appended 2025-09-04

- Import-linter: run (fail-open) — capture tail for triage if noisy.
- Focused coverage smoke: `tests/contract/test_healthz_voice_required.py` with coverage for `serve`.
- Ruff: run only on changed files between `origin/main` and `HEAD`.

Confirm `test-results.xml` is ignored/untracked and SUPPRESSIONS_LEDGER.md contains PERF203 waiver (expires 2026-03-01).
