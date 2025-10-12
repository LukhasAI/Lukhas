# API Error Shapes

All errors from the Lukhas OpenAI façade follow OpenAI-compatible JSON shapes.

## 401 Unauthorized

**When**: Missing or invalid Bearer token

```json
{
  "error": {
    "type": "unauthorized",
    "message": "missing or invalid token"
  }
}
```

**Headers**: None

**Resolution**: Include valid `Authorization: Bearer <token>` header

---

## 429 Rate Limit Exceeded

**When**: Request rate exceeds configured limits

```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "rate limit exceeded"
  }
}
```

**Headers**:
- `Retry-After: <seconds>` - How long to wait before retrying

**Resolution**:
- Implement exponential backoff with jitter
- Respect `Retry-After` header
- See `configs/runtime/reliability.yaml` for current limits

---

## 500 Internal Server Error

**When**: Unexpected server error

```json
{
  "error": {
    "type": "internal_server_error",
    "message": "unexpected error"
  }
}
```

**Headers**: None

**Resolution**:
- Check server logs
- Retry with exponential backoff
- Report persistent issues to platform team

---

## Error Handling Best Practices

### 1. Always Check Status Codes

```python
response = requests.post(url, json=payload)
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # retry request
elif response.status_code >= 500:
    # exponential backoff
    time.sleep(min(60, 2 ** attempt))
    # retry request
```

### 2. Implement Exponential Backoff

Use jittered exponential backoff for retries:

```python
from lukhas.core.reliability.backoff import jittered_exponential

base = 0.1  # 100ms base delay
factor = 2.0  # double each attempt
attempt = 3
lo, hi = jittered_exponential(base, factor, attempt, jitter=0.1)
sleep_time = random.uniform(lo, hi)
```

### 3. Handle Partial Failures Gracefully

For streaming responses, handle disconnections:

```python
try:
    for chunk in stream:
        process(chunk)
except requests.exceptions.ChunkedEncodingError:
    # Resume from last received chunk
    resume_streaming(last_chunk_id)
```

---

## Rate Limit Configuration

See [configs/runtime/reliability.yaml](../configs/runtime/reliability.yaml:5) for current limits:

- `/v1/responses`: 20 requests/second
- `/v1/embeddings`: 50 requests/second

Contact platform team to request limit increases for production use cases.
