# Lukhas × OpenAI Quickstart

## Getting Started

### 1. Start the Lukhas OpenAI Façade

```bash
uvicorn lukhas.adapters.openai.api:get_app --reload
```

### 2. Use with OpenAI SDK (Python)

```python
from openai import OpenAI

# Point the SDK at Lukhas
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

# Generate a response
out = client.responses.create(input="hello lukhas")
print(out.output.text)
```

### 3. Available Endpoints

- **Models**: `GET /v1/models` - List available models
- **Embeddings**: `POST /v1/embeddings` - Generate text embeddings
- **Responses**: `POST /v1/responses` - Generate AI responses (OpenAI-compatible)
- **Dreams (Drift)**: `POST /v1/dreams` - Generate dream traces (Lukhas-specific)
- **Health**: `/healthz`, `/readyz`, `/metrics` - Operational endpoints

## OpenAI Concept → Lukhas Mapping

| OpenAI Concept | Lukhas Equivalent | Notes |
|---------------|-------------------|-------|
| `gpt-4` model | `lukhas-matriz` | Powered by MATRIZ cognitive engine |
| `embeddings` | Memory orchestrator | Backed by vector memory system |
| `chat.completions` | `/v1/responses` | Compatible response format |
| `functions` | Tool schema | Exported from manifests |
| Streaming | SSE delta/step | OpenAI-compatible streaming |

## Example: curl

```bash
# List models
curl http://localhost:8000/v1/models

# Generate response
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"input":"hello lukhas","tools":[]}'

# Generate embeddings
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"input":"embed this text"}'

# Health check
curl http://localhost:8000/healthz

# Metrics
curl http://localhost:8000/metrics
```

## Example: JavaScript/Node.js

### Using Fetch API

```javascript
const response = await fetch('http://localhost:8000/v1/responses', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': 'Bearer dummy'
  },
  body: JSON.stringify({ input: 'hello lukhas', tools: [] })
});

const data = await response.json();
console.log(data.output.text);
```

### Using OpenAI SDK

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'dummy'
});

// Chat completions (mapped to /v1/responses)
const response = await client.chat.completions.create({
  model: 'lukhas-matriz',
  messages: [{ role: 'user', content: 'hello lukhas' }]
});

console.log(response.choices[0].message.content);

// Embeddings
const embedding = await client.embeddings.create({
  model: 'lukhas-memory',
  input: 'embed this text'
});

console.log(embedding.data[0].embedding);
```

## Example: TypeScript

```typescript
import OpenAI from 'openai';

interface LukhasConfig {
  baseURL: string;
  apiKey: string;
}

const config: LukhasConfig = {
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'dummy'
};

const client = new OpenAI(config);

async function generateResponse(input: string): Promise<string> {
  const response = await client.chat.completions.create({
    model: 'lukhas-matriz',
    messages: [{ role: 'user', content: input }]
  });
  
  return response.choices[0].message.content || '';
}

// Usage
const result = await generateResponse('hello lukhas');
console.log(result);
```

## Dreams API (Lukhas-Specific)

The Dreams endpoint provides scenario generation and self-critique capabilities:

### Python

```python
response = client.post('/v1/dreams', json={
  'seed': 'labyrinth under starlight',
  'constraints': {'length': 'short'}
})

print(response.json()['traces'])
```

### curl

```bash
curl -X POST http://localhost:8000/v1/dreams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"seed":"quantum garden","constraints":{"length":"short"}}'
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/v1/dreams', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer dummy'
  },
  body: JSON.stringify({
    seed: 'neural labyrinth',
    constraints: { length: 'medium' }
  })
});

const data = await response.json();
console.log(data.traces);
```

## Migration Guide: OpenAI → Lukhas

### Step 1: Update Base URL

**Before (OpenAI)**:
```python
from openai import OpenAI
client = OpenAI(api_key="sk-...")
```

**After (Lukhas)**:
```python
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # or your Lukhas token
)
```

### Step 2: Model Name Mapping

| OpenAI Model | Lukhas Model | Notes |
|--------------|--------------|-------|
| `gpt-4` | `lukhas-matriz` | Full MATRIZ cognitive engine |
| `gpt-3.5-turbo` | `lukhas-matriz` | Same backend |
| `text-embedding-ada-002` | `lukhas-memory` | Memory orchestrator |
| `gpt-4-vision` | `lukhas-vision` | Vision pipeline (coming soon) |

### Step 3: API Changes

**Chat Completions** → **Responses**:
```python
# OpenAI style (still works)
response = client.chat.completions.create(
    model="lukhas-matriz",
    messages=[{"role": "user", "content": "hello"}]
)

# Lukhas native style (recommended)
response = client.responses.create(
    input="hello",
    tools=[]
)
```

**Function Calling** → **Tool Schema**:
```python
# OpenAI style
functions = [{
    "name": "get_weather",
    "parameters": {"type": "object", "properties": {...}}
}]

# Lukhas style (exported from manifests)
tools = client.get("/v1/tools").json()["data"]
```

### Step 4: Authentication

**Development**:
- Any API key works: `api_key="dummy"`

**Production**:
- Set `LUKHAS_API_TOKEN` in `.env`
- Use bearer token: `api_key=os.getenv("LUKHAS_API_TOKEN")`

### Step 5: Error Handling

```python
from openai import OpenAI, OpenAIError

try:
    response = client.chat.completions.create(...)
except OpenAIError as e:
    # Same error handling as OpenAI
    print(f"Error: {e.status_code} - {e.message}")
```

### Step 6: Streaming

```python
# OpenAI streaming (compatible)
stream = client.chat.completions.create(
    model="lukhas-matriz",
    messages=[{"role": "user", "content": "hello"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Step 7: Rate Limiting

Lukhas includes built-in rate limiting:
- Responses: 20 rps (default)
- Embeddings: 50 rps (default)
- Dreams: 5 rps (default)

Configure in `configs/runtime/reliability.yaml`

## Troubleshooting

### Connection Refused

**Symptom**: `ConnectionError: Connection refused`

**Solutions**:
1. Ensure the façade is running:
   ```bash
   uvicorn lukhas.adapters.openai.api:get_app --reload
   ```
2. Check the port (default: 8000)
3. Verify with: `curl http://localhost:8000/healthz`

### Authentication Errors

**Symptom**: `401 Unauthorized`

**Solutions**:
- Development: Use `api_key="dummy"` (any key works)
- Production: Set `LUKHAS_API_TOKEN` in `.env`
- Check headers: Must include `Authorization: Bearer <token>`

### Rate Limiting

**Symptom**: `429 Too Many Requests`

**Solutions**:
1. Check `Retry-After` header in response
2. Implement exponential backoff (see below)
3. Adjust limits in `configs/runtime/reliability.yaml`

**Backoff Example**:
```python
import time
from openai import RateLimitError

def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if i == max_retries - 1:
                raise
            wait = 2 ** i  # Exponential: 1s, 2s, 4s
            time.sleep(wait)
```

### Timeout Errors

**Symptom**: `TimeoutError` or `ReadTimeout`

**Solutions**:
1. Increase client timeout:
   ```python
   client = OpenAI(
       base_url="http://localhost:8000/v1",
       timeout=30.0  # seconds
   )
   ```
2. Adjust server timeouts in `configs/runtime/reliability.yaml`
3. Check network connectivity

### Invalid Response Format

**Symptom**: `JSONDecodeError` or unexpected response shape

**Solutions**:
1. Verify API version compatibility
2. Check request payload matches schema
3. Review API errors: See [API_ERRORS.md](../API_ERRORS.md)
4. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Model Not Found

**Symptom**: `404 Not Found` for model

**Solutions**:
1. List available models:
   ```bash
   curl http://localhost:8000/v1/models
   ```
2. Use correct model name: `lukhas-matriz`, `lukhas-memory`
3. Check model availability in deployment

### Performance Issues

**Symptom**: Slow response times (>5s)

**Solutions**:
1. Check metrics: `curl http://localhost:8000/metrics`
2. Review SLO targets: [SLOs.md](../ops/SLOs.md)
3. Enable caching for repeated queries
4. Check backend resource utilization

## Testing Your Integration

### Quick Health Check

```bash
#!/bin/bash
# test_integration.sh

BASE_URL="http://localhost:8000"

# 1. Health check
echo "Testing health..."
curl -f $BASE_URL/healthz || exit 1

# 2. List models
echo "Testing models..."
curl -f $BASE_URL/v1/models || exit 1

# 3. Test response
echo "Testing response..."
curl -f -X POST $BASE_URL/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"input":"ping","tools":[]}' || exit 1

# 4. Test embeddings
echo "Testing embeddings..."
curl -f -X POST $BASE_URL/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{"input":"test"}' || exit 1

echo "✅ All tests passed!"
```

### Python Integration Test

```python
#!/usr/bin/env python3
"""Integration test for Lukhas OpenAI façade."""
import sys
from openai import OpenAI

def main():
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="dummy"
    )
    
    # Test models
    print("Testing models...")
    models = client.models.list()
    assert len(models.data) > 0, "No models found"
    print(f"✅ Found {len(models.data)} models")
    
    # Test chat
    print("Testing chat...")
    response = client.chat.completions.create(
        model="lukhas-matriz",
        messages=[{"role": "user", "content": "ping"}]
    )
    assert response.choices[0].message.content, "No response"
    print(f"✅ Got response: {response.choices[0].message.content[:50]}")
    
    # Test embeddings
    print("Testing embeddings...")
    embedding = client.embeddings.create(
        model="lukhas-memory",
        input="test"
    )
    assert len(embedding.data[0].embedding) > 0, "Empty embedding"
    print(f"✅ Got embedding of dimension {len(embedding.data[0].embedding)}")
    
    print("\n🎉 All integration tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Advanced Features

### Streaming with Context

```python
def stream_with_context(client, messages, context=None):
    """Stream responses with optional context."""
    params = {
        "model": "lukhas-matriz",
        "messages": messages,
        "stream": True
    }
    
    if context:
        params["context"] = context
    
    stream = client.chat.completions.create(**params)
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)
    
    return full_response
```

### Batch Processing

```python
async def batch_process(client, inputs, batch_size=10):
    """Process multiple inputs in batches."""
    results = []
    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i + batch_size]
        batch_results = await asyncio.gather(*[
            client.chat.completions.create(
                model="lukhas-matriz",
                messages=[{"role": "user", "content": inp}]
            )
            for inp in batch
        ])
        results.extend(batch_results)
    return results
```

### Custom Tool Integration

```python
# Define custom tools
custom_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

# Use in request
response = client.chat.completions.create(
    model="lukhas-matriz",
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
    tools=custom_tools,
    tool_choice="auto"
)
```

## Next Steps

- **API Reference**: Review [API Error Shapes](../API_ERRORS.md) for error handling
- **Operations**: Explore [SLO Budgets](../ops/SLOs.md) for reliability targets
- **Architecture**: Check [Why MATRIZ](../matriz/WHY_MATRIZ.md) for system overview
- **Security**: Read [SECURITY.md](../../SECURITY.md) for security policies
- **Testing**: See [Testing Guide](../testing/) for integration tests
- **Deployment**: Review [Deployment Guide](../ops/) for production setup

## Resources

- **GitHub**: [LukhasAI/Lukhas](https://github.com/LukhasAI/Lukhas)
- **Documentation**: [docs/](../)
- **Examples**: [examples/](../../examples/)
- **Support**: Open an issue on GitHub

## License

Apache-2.0 - See [LICENSE](../../LICENSE) for details

---

**Last Updated**: 2025-10-12  
**Document Version**: 2.0 (Enhanced with comprehensive examples and migration guide)
