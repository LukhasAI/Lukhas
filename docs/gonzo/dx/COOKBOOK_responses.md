# 🍳 Cookbook — Responses API

> Drop-in OpenAI alignment with envelopes, tracing, and rate-limit headers.

## cURL (non-stream)

```bash
curl -sS -H "Authorization: Bearer sk-test" -H "Content-Type: application/json" \
  -d '{"model":"lukhas","input":"Hello"}' \
  http://localhost:8000/v1/responses | jq .
```

## JavaScript (streaming)

```js
import EventSource from "eventsource";
const body = { model: "lukhas", input: "stream this", stream: true };
const es = new EventSource("http://localhost:8000/v1/responses", {
  headers: { Authorization: "Bearer sk-test", "Content-Type": "application/json" },
  method: "POST",
  payload: JSON.stringify(body),
});
es.onmessage = (e) => console.log("chunk:", e.data);
es.onerror = (e) => console.error("stream error:", e);
```

## Python (sync)

```python
import requests, json
r = requests.post(
  "http://localhost:8000/v1/responses",
  headers={"Authorization":"Bearer sk-test","Content-Type":"application/json"},
  json={"model":"lukhas","input":"hello world"}
)
print(r.status_code, r.headers.get("X-Trace-Id"))
print(json.dumps(r.json(), indent=2))
```

## Expected Headers

* `X-Trace-Id` / `X-Request-Id` — W3C trace correlation (dual headers for OpenAI compatibility)
* `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` — LUKHAS-style rate limits
* `x-ratelimit-limit-requests`, `x-ratelimit-remaining-requests`, `x-ratelimit-reset-requests` — OpenAI-style aliases

## Multi-Tenant Routing (Optional)

Pass org/project headers for multi-tenant routing:

```bash
curl -sS -H "Authorization: Bearer $API_KEY" \
  -H "OpenAI-Organization: $ORG_ID" \
  -H "OpenAI-Project: $PROJECT_ID" \
  http://localhost:8000/v1/models
```

## Reading Headers

### Node.js
```js
const reqId = res.headers.get('x-request-id') ?? res.headers.get('X-Request-Id');
const limit = res.headers.get('x-ratelimit-limit-requests');
const remaining = res.headers.get('x-ratelimit-remaining-requests');
const reset = res.headers.get('x-ratelimit-reset-requests');
console.log(`Request ${reqId}: ${remaining}/${limit} remaining, resets at ${reset}`);
```

### Python
```python
req_id = r.headers.get('X-Request-Id') or r.headers.get('x-request-id')
limit = r.headers.get('x-ratelimit-limit-requests')
remaining = r.headers.get('x-ratelimit-remaining-requests')
reset = r.headers.get('x-ratelimit-reset-requests')
print(f"Request {req_id}: {remaining}/{limit} remaining, resets at {reset}")
