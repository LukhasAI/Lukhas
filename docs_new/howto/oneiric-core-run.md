---
title: Run Oneiric Core
status: stable
owner: core-runtime
tags: [howto, runtime]
facets:
  layer: [orchestration]
  audience: [dev]
---

## Quickstart
1. `uv venv` or `python -m venv .venv`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

## Troubleshooting
- Ports, env vars, DB migrations.