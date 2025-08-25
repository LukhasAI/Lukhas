---
# Content Classification
doc_type: "api"
update_frequency: "fixed"
last_updated: "2025-08-25"
next_review: "2026-08-25"

# Audience Targeting
audience: ["developers", "agents"]
technical_level: "intermediate"

# Agent Routing
agent_relevance:
  supreme_consciousness_architect: 0.7
  consciousness_architect: 0.7
  consciousness_developer: 0.9
  github_copilot: 0.8
  api_interface_colonel: 1.0
  security_compliance_colonel: 0.5
  testing_validation_colonel: 0.8
  devops_guardian: 0.8
  documentation_specialist: 1.0
  guardian_engineer: 0.5
  velocity_lead: 0.6

# Trinity Framework
trinity_component: ["identity", "consciousness", "guardian"]
search_keywords: ["api", "openapi", "swagger", "json", "redoc", "documentation", "export"]

# Priority Classification
priority: "critical"
category: "api"
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