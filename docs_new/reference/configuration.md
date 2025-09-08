---
title: Configuration
status: review
owner: docs-team
last_review: 2025-01-09
tags: [reference]
facets:
  layer: [gateway]
  domain: [symbolic]
  audience: [dev]
---

# LUKHΛS  OpenAPI / Swagger

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Raw OpenAPI JSON: `/openapi.json`

## Export locally

```bash
uvicorn lukhas.api.app:app --reload --port 8000 &
sleep 2
curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json
kill %1
```

## Publishing ideas
- Upload `out/openapi.json` as a CI artifact on each PR
- Optionally publish to an internal docs portal (Stoplight/Redocly) on main branch merges
