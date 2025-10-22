# Lukhas Audit Packet — 2025-10-22T212050Z

- Git SHA: bd7c5a7bc
- Audit Tag: audit-2025-10-22T210824Z
- OpenAPI: lukhas-openapi.json
- Health: latest.{json,md}
- Lint: ruff_statistics.txt
- Security: pip_audit.txt
- CI: matriz-validate.yml
- Env: .env.example / .env.audit
- Postman: ./postman/ (if available)
- RC Soak: ./rc_soak_results/ (if available)

## Audit Configuration

The system should be tested with the settings in `.env.audit`:
- LUKHAS_POLICY_MODE=strict (Guardian enforcement)
- LUKHAS_RL_KEYING=route_principal (Rate limiting)
- LUKHAS_RATE_RPS=10, LUKHAS_RATE_BURST=20
- LUKHAS_IDEMP_TTL=300 (Idempotency cache)
- LUKHAS_LOG_REDACT=1 (PII/token redaction)
- LUKHAS_TRACE_HEADERS=1 (X-Trace-Id emission)

## Auditor Quickstart

```bash
# Start API server
uvicorn serve.main:app --host 0.0.0.0 --port 8000 --reload

# Set audit environment
export $(grep -v '^#' .env.audit | xargs -I{} echo {})

# Verify health & headers
curl -i http://localhost:8000/healthz
curl -i -H "Authorization: Bearer test" http://localhost:8000/v1/models

# Validate OpenAPI
python3 -m pip install openapi-spec-validator
python3 - <<'PY'
import json; from openapi_spec_validator import validate
spec=json.load(open("lukhas-openapi.json"))
validate(spec); print("OpenAPI valid")
PY
```

## Key Endpoints

- `/healthz` - System health with service status
- `/v1/models` - OpenAI-compatible models list
- `/v1/embeddings` - OpenAI-compatible embeddings
- `/v1/chat/completions` - OpenAI-compatible chat

## Expected Response Headers

All endpoints should emit:
- X-Trace-Id: Unique request trace ID
- X-Request-Id: Request identifier
- X-RateLimit-Limit: Rate limit ceiling
- X-RateLimit-Remaining: Requests remaining
- X-RateLimit-Reset: Reset timestamp

## RC Soak Test Results

Recent RC soak validation (if included):
- 100% success rate on synthetic load tests
- OpenAI-compatible endpoints functional
- Health snapshot generation working
- See rc_soak_results/RC_SOAK_TEST_RESULTS.md for details

## Validation Checklist

- [ ] OpenAPI spec validates against OpenAPI 3.1 schema
- [ ] Health endpoint returns 200 with service status
- [ ] Models endpoint returns OpenAI-compatible list format
- [ ] Rate limiting headers present on all responses
- [ ] Trace headers present for request tracking
- [ ] Guardian policy enforcement in strict mode
- [ ] Log redaction working (no API keys/tokens in logs)
- [ ] Idempotency replay headers on cache hits

