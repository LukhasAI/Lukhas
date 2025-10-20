# LUKHAS API Documentation Index

Last Updated: 2025-10-19
OpenAPI Version: 3.1.0
Base URL (dev): `http://localhost:8000/api/v1`
Base URL (prod): `https://api.lukhas.ai/v1`

---

## Available APIs

- Identity API
  - Spec: docs/openapi/identity_api.openapi.yaml
  - ReDoc: docs/openapi/site/identity.html (if generated)
  - Endpoints (sample):
    - POST /auth/login — Authenticate user
    - GET /auth/me — Get current user

- Consciousness API
  - Spec: docs/openapi/consciousness_api.openapi.yaml
  - ReDoc: docs/openapi/site/consciousness.html

- Governance (Guardian) API
  - Spec: docs/openapi/guardian_api.openapi.yaml
  - ReDoc: docs/openapi/site/governance.html

- Monitoring API
  - Spec: docs/openapi/monitoring.openapi.yaml
  - ReDoc: docs/openapi/site/monitoring.html

- Lanes API
  - Spec: docs/openapi/lanes.openapi.yaml
  - ReDoc: docs/openapi/site/lanes.html

---

## Quick Start

Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@lukhas.ai","password":"secure_password"}'
```

Health Check
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

---

## Tools

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Specs: docs/openapi/
- Endpoint Catalog: docs/apis/endpoint_catalog.json

