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
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"hello lukhas","tools":[]}'
```

## Example: JavaScript

```javascript
const response = await fetch('http://localhost:8000/v1/responses', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'hello lukhas', tools: [] })
});

const data = await response.json();
console.log(data.output.text);
```

## Dreams API (Lukhas-Specific)

The Dreams endpoint provides scenario generation and self-critique capabilities:

```python
response = client.post('/v1/dreams', json={
  'seed': 'labyrinth under starlight',
  'constraints': {'length': 'short'}
})

print(response.json()['traces'])
```

## Troubleshooting

### Connection Refused
- Ensure the façade is running: `uvicorn lukhas.adapters.openai.api:get_app --reload`
- Check the port (default: 8000)

### Authentication Errors
- The stub façade accepts any API key for development
- In production, set `LUKHAS_API_TOKEN` in `.env`

### Rate Limiting
- Default limits: 20 requests/sec for responses, 50 for embeddings
- Configure in `configs/runtime/reliability.yaml`
- Responses include `Retry-After` header on 429

## Next Steps

- Review [API Error Shapes](../API_ERRORS.md)
- Explore [SLO Budgets](../ops/SLOs.md)
- Check [Why Matriz](../matriz/WHY_MATRIZ.md) for architecture overview
