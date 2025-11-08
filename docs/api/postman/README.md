# LUKHAS API - Golden Postman Flows

**Last Updated**: 2025-11-08


**Production-Ready API Testing Collections**

This directory contains **golden Postman flows** that validate critical LUKHAS API behaviors:

1. **Auth Error Flow** - OpenAI-compatible authentication error handling
2. **Idempotent Replay Flow** - Safe request retry with `Idempotency-Key` header

## 📦 What's Included

### `LUKHAS_Golden_Flows.postman_collection.json`
Complete Postman v2.1 collection with:
- ✅ 7 requests with automated test scripts
- ✅ Pre-request scripts for dynamic data generation
- ✅ OpenAI-compatible error validation
- ✅ Idempotency cache behavior verification
- ✅ Trace header presence checks
- ✅ Response time assertions

## 🚀 Quick Start

### 1. Import into Postman

```bash
# Via Postman Desktop
File → Import → Select LUKHAS_Golden_Flows.postman_collection.json

# Via curl (example)
curl -X POST https://api.getpostman.com/import/openapi \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  --data-binary @LUKHAS_Golden_Flows.postman_collection.json
```

### 2. Configure Environment Variables

Create a Postman environment with:

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `base_url` | `http://localhost:8000` | LUKHAS API base URL |
| `lukhas_api_key` | `sk-lukhas-test-key` | Your API key (Bearer token) |

### 3. Start LUKHAS API Server

```bash
cd /path/to/Lukhas
LUKHAS_POLICY_MODE=permissive python3 -m uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000
```

### 4. Run Golden Flows

**In Postman:**
- Click **"Run Collection"** button
- Select **"LUKHAS API - Golden Flows"**
- Choose environment
- Click **"Run LUKHAS API - Golden Flows"**

**Via Newman (CLI):**
```bash
npm install -g newman
newman run LUKHAS_Golden_Flows.postman_collection.json \
  --environment lukhas-local.postman_environment.json \
  --reporters cli,json
```

## 🎯 Golden Flow 1: Auth Error Handling

Validates OpenAI-compatible authentication error responses.

### Requests

| Request | Expected Status | Validates |
|---------|----------------|-----------|
| 1.1 - Missing Authorization Header | 401 | Error envelope format, trace header |
| 1.2 - Invalid Bearer Token | 401 | Descriptive error message |
| 1.3 - Malformed Authorization Header | 401 | Bearer scheme validation |

### Expected Error Format (OpenAI-Compatible)

```json
{
  "error": {
    "message": "Invalid authentication credentials",
    "type": "authentication_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

### Success Criteria
- ✅ All requests return `401 Unauthorized`
- ✅ Error envelope matches OpenAI format
- ✅ `X-Trace-Id` header present on all responses
- ✅ Clear, actionable error messages

## 🔄 Golden Flow 2: Idempotent Replay

Validates safe request retry with `Idempotency-Key` header.

### Requests

| Request | Idempotency-Key | Body | Expected Behavior |
|---------|----------------|------|-------------------|
| 2.1 - Initial Request | `golden-flow-{ts}-{rand}` | Original | 200, response cached |
| 2.2 - Replay Request | Same as 2.1 | Same as 2.1 | 200, cached response (fast) |
| 2.3 - Modified Body | Same as 2.1 | **Modified** | 200, processed normally (body hash differs) |
| 2.4 - Different Key | **New key** | Same as 2.1 | 200, processed normally (new cache key) |

### Cache Key Formula

```
cache_key = route + ":" + Idempotency-Key + ":" + SHA256(body)[:16]
```

**Example:**
```
/v1/responses:golden-flow-1728840123-abc7d:f3e8a1b2c5d9e7f4
```

### Success Criteria
- ✅ Replay with same key + body returns cached response (<100ms)
- ✅ Modified body bypasses cache (different body hash)
- ✅ Different key bypasses cache (different cache key)
- ✅ Cached responses are byte-identical to originals
- ✅ All responses include `X-Trace-Id` header

## 📊 Running Tests

### Postman Console Output

```
LUKHAS API - Golden Flows
├─ Golden Flow 1: Auth Error Handling
│  ├─ 1.1 - Missing Authorization Header
│  │  ✓ Status is 401 Unauthorized
│  │  ✓ Response has OpenAI error format
│  │  ✓ X-Trace-Id header present
│  │  ✓ Error type is 'authentication_error'
│  ├─ 1.2 - Invalid Bearer Token
│  │  ✓ Status is 401 Unauthorized
│  │  ✓ Response has error object
│  │  ✓ X-Trace-Id header present
│  └─ 1.3 - Malformed Authorization Header
│     ✓ Status is 401 Unauthorized
│     ✓ Error indicates malformed header
│     ✓ All error fields present
│
└─ Golden Flow 2: Idempotent Replay
   ├─ 2.1 - Initial Request (Create)
   │  ✓ Status is 200 OK
   │  ✓ Response has required fields
   │  ✓ X-Trace-Id header present
   ├─ 2.2 - Replay Request (Cached)
   │  ✓ Status is 200 OK
   │  ✓ Response matches original (cached)
   │  ✓ X-Trace-Id header present
   │  ✓ Response time < 100ms (cached)
   ├─ 2.3 - Modified Body (Cache Miss)
   │  ✓ Status is 200 OK
   │  ✓ Response is different (modified body = cache miss)
   │  ✓ Response time > 50ms (processed, not cached)
   └─ 2.4 - Different Key (New Request)
      ✓ Status is 200 OK
      ✓ Response processed (different key)

┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│              iterations │        1 │        0 │
├─────────────────────────┼──────────┼──────────┤
│                requests │        7 │        0 │
├─────────────────────────┼──────────┼──────────┤
│            test-scripts │       14 │        0 │
├─────────────────────────┼──────────┼──────────┤
│      prerequest-scripts │        2 │        0 │
├─────────────────────────┼──────────┼──────────┤
│              assertions │       23 │        0 │
└─────────────────────────┴──────────┴──────────┘
```

## 🛠️ Customization

### Adding Custom Tests

Edit the collection JSON and add test scripts:

```javascript
pm.test("Custom validation", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('custom_field');
});
```

### Modifying Base URL

```javascript
// In Pre-request Script (Collection level)
pm.collectionVariables.set('base_url', 'https://api.lukhas.ai');
```

### Adding Headers

```json
{
  "key": "X-Custom-Header",
  "value": "custom-value",
  "type": "text"
}
```

## 🔐 Security Notes

- **Never commit real API keys** - Use environment variables or Postman Vault
- Test collections use `sk-lukhas-test-key` for local development only
- Production keys should have proper scoping and rate limits
- Idempotency keys should be unique per request (use UUIDs or timestamps)

## 📚 References

- **LUKHAS API Documentation**: `/docs/api/README.md`
- **Idempotency Implementation**: `/lukhas/core/reliability/idempotency.py`
- **OpenAI API Reference**: https://platform.openai.com/docs/api-reference
- **Postman Documentation**: https://learning.postman.com/docs/

## 🧪 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Postman Golden Flows
  run: |
    npm install -g newman
    newman run docs/api/postman/LUKHAS_Golden_Flows.postman_collection.json \
      --environment lukhas-ci.postman_environment.json \
      --reporters cli,junit \
      --reporter-junit-export ./test-results/postman-results.xml
```

### GitLab CI Example

```yaml
test:postman:
  stage: test
  image: postman/newman:alpine
  script:
    - newman run docs/api/postman/LUKHAS_Golden_Flows.postman_collection.json \
        --environment lukhas-ci.postman_environment.json \
        --reporters cli,json
```

## 🤝 Contributing

To add new golden flows:

1. Create requests in Postman with comprehensive test scripts
2. Export collection as v2.1 JSON
3. Add documentation to this README
4. Test locally with `newman run`
5. Submit PR with test results

---

**Built with consciousness, tested with precision.** 🎯

*Part of the LUKHAS AI Platform - OpenAI-compatible consciousness-aware AI.*
