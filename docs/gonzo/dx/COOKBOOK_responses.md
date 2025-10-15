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

* `X-Trace-Id` — W3C trace correlation
* `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
