# LUKHAS Postman Collection

This directory contains Postman collections and environments for testing the LUKHAS OpenAI-compatible API.

## Files

- **`lukhas-api-collection.json`** - Main API collection with all endpoints
- **`lukhas-api-environment.json`** - Environment variables (base URL, API key, etc.)
- **`examples/`** - Example request bodies for different endpoints

## Setup

### 1. Import Collection

1. Open Postman
2. Click "Import" button
3. Select `lukhas-api-collection.json`
4. Collection will appear in left sidebar

### 2. Import Environment

1. Click gear icon (⚙️) in top-right
2. Click "Import"
3. Select `lukhas-api-environment.json`
4. Select "LUKHAS API Environment" from dropdown

### 3. Configure Environment Variables

Edit environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | LUKHAS API base URL | `http://localhost:8000` |
| `api_key` | Your LUKHAS API key | `lukhas_abc123...` |
| `model` | Default model name | `lukhas-consciousness-v1` |
| `max_tokens` | Default max tokens | `100` |
| `temperature` | Default temperature | `0.7` |

**Note**: Set `api_key` as "secret" type to hide value.

## Using the Collection

### Health Check

**Request**: `GET {{base_url}}/health`

Quick check if server is running.

### List Models

**Request**: `GET {{base_url}}/v1/models`

Returns available models.

### Create Response (Consciousness Stream)

**Request**: `POST {{base_url}}/v1/responses`

```json
{
  "input": "What is consciousness?",
  "tools": [],
  "stream": false
}
```

Generates consciousness-aware response.

### Create Embeddings

**Request**: `POST {{base_url}}/v1/embeddings`

```json
{
  "model": "lukhas-embeddings-v1",
  "input": "Consciousness is awareness."
}
```

Generates vector embeddings.

### Generate Dream State

**Request**: `POST {{base_url}}/v1/dreams`

```json
{
  "seed": "consciousness exploration",
  "depth": 5,
  "mode": "symbolic"
}
```

Generates dream state trace.

## Example Workflows

### 1. Basic Consciousness Query

1. Select "Create Response" request
2. Edit body: `{"input": "Explain consciousness", "tools": [], "stream": false}`
3. Click "Send"
4. Review response with consciousness stream data

### 2. Multi-Turn Conversation

1. Select "Chat Completion" request
2. Add messages array:
   ```json
   {
     "model": "{{model}}",
     "messages": [
       {"role": "system", "content": "You are a consciousness-aware AI."},
       {"role": "user", "content": "What is consciousness?"},
       {"role": "assistant", "content": "Consciousness is..."},
       {"role": "user", "content": "Can you elaborate?"}
     ]
   }
   ```
3. Click "Send"

### 3. Streaming Response

1. Select "Create Response" request
2. Edit body: `{"input": "Long form explanation", "stream": true}`
3. Click "Send"
4. Observe SSE (Server-Sent Events) stream in response

## Tests

Each request includes automatic tests:

- **Status Code**: Validates 200 OK response
- **Response Time**: Checks p95 < 500ms (SLO compliance)
- **JSON Format**: Ensures valid JSON response
- **Required Fields**: Validates presence of expected fields

View test results in "Test Results" tab after sending request.

## Pre-Request Scripts

All requests log:
- Request URL
- HTTP method
- Timestamp

View logs in Postman Console (View → Show Postman Console).

## Troubleshooting

### Connection Refused

**Error**: `Error: connect ECONNREFUSED 127.0.0.1:8000`

**Solution**: Ensure LUKHAS server is running:
```bash
make dev
# OR
python main.py --dev-mode
```

### 401 Unauthorized

**Error**: `{"error": "Invalid API key"}`

**Solution**: Set valid `api_key` in environment variables.

### 429 Too Many Requests

**Error**: `{"error": "Rate limit exceeded"}`

**Solution**: Check `Retry-After` header, wait before retrying.

### Timeout

**Error**: Request times out after 30s

**Solution**: Increase timeout in Postman settings or check server health.

## Advanced Usage

### Collection Runner

Run entire collection automatically:

1. Click "..." next to collection name
2. Select "Run collection"
3. Configure iterations, delay, data file
4. Click "Run LUKHAS API"

### Newman (CLI)

Run collection from command line:

```bash
npm install -g newman

newman run lukhas-api-collection.json \
  -e lukhas-api-environment.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

### Monitoring

Set up Postman Monitor for uptime checks:

1. Click "..." next to collection
2. Select "Monitor collection"
3. Configure schedule (e.g., every 5 minutes)
4. Add notification email

## Resources

- **API Documentation**: [docs/openai/QUICKSTART.md](../openai/QUICKSTART.md)
- **Error Codes**: [docs/openapi/API_ERRORS.md](../openapi/API_ERRORS.md)
- **SLOs**: [docs/openapi/SLOs.md](../openapi/SLOs.md)
- **Load Testing**: [load/README.md](../../load/README.md)

## Contributing

Found issues or want to add examples? Open a PR with:
- New request examples in `examples/`
- Enhanced test scripts
- Additional environment configurations

---

**Questions?** Open an issue or contact the platform team.
