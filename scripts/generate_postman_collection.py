#!/usr/bin/env python3
"""
Module: generate_postman_collection.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Convert OpenAPI specification to Postman Collection v2.1

Usage:
    python scripts/generate_postman_collection.py

Requires:
    pip install openapi-to-postmanv2 pyyaml
"""

import json
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Ensure required packages are installed."""
    try:
        import yaml
    except ImportError:
        print("❌ Missing dependency: pyyaml")
        print("Install with: pip install pyyaml")
        sys.exit(1)
    
    # Check if openapi2postmanv2 CLI is available (optional)
    try:
        result = subprocess.run(
            ["openapi2postmanv2", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  openapi2postmanv2 not found, will use fallback generation")
    return False

def convert_openapi_to_postman(
    openapi_path: Path,
    output_path: Path,
    collection_name: str = "LUKHAS API"
):
    """Convert OpenAPI spec to Postman collection using CLI tool."""
    print(f"🔄 Converting {openapi_path} to Postman collection...")
    
    # Use openapi2postmanv2 CLI
    result = subprocess.run(
        [
            "openapi2postmanv2",
            "-s", str(openapi_path),
            "-o", str(output_path),
            "-p"  # Pretty print
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Conversion failed: {result.stderr}")
        return False
    
    print(f"✅ Postman collection created: {output_path}")
    return True

def enhance_postman_collection(collection_path: Path):
    """Enhance generated collection with LUKHAS-specific examples and tests."""
    with open(collection_path) as f:
        collection = json.load(f)
    
    # Add collection-level info
    collection["info"]["name"] = "LUKHAS OpenAI-Compatible API"
    collection["info"]["description"] = (
        "Postman collection for LUKHAS AI Platform OpenAI-compatible API.\n\n"
        "## Features\n"
        "- Consciousness stream generation (`/v1/responses`)\n"
        "- Vector embeddings (`/v1/embeddings`)\n"
        "- Dream state processing (`/v1/dreams`)\n"
        "- OpenAI-compatible endpoints\n\n"
        "## Setup\n"
        "1. Import `lukhas-api-environment.json` for environment variables\n"
        "2. Set `base_url` (default: `http://localhost:8000`)\n"
        "3. Set `api_key` (your LUKHAS API key)\n\n"
        "## Documentation\n"
        "- [API Quickstart](../openai/QUICKSTART.md)\n"
        "- [Error Handling](../openai/API_ERRORS.md)\n"
        "- [SLOs](../openai/SLOs.md)"
    )
    
    # Add authentication to all requests
    for item in collection.get("item", []):
        if "request" in item:
            add_auth_and_examples(item["request"])
        elif "item" in item:  # Folder with sub-items
            for subitem in item["item"]:
                if "request" in subitem:
                    add_auth_and_examples(subitem["request"])
    
    # Save enhanced collection
    with open(collection_path, "w") as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Enhanced collection with authentication and examples")

def add_auth_and_examples(request: dict):
    """Add authentication headers and example tests to a request."""
    # Add Authorization header using environment variable
    if "header" not in request:
        request["header"] = []
    
    request["header"].append({
        "key": "Authorization",
        "value": "Bearer {{api_key}}",
        "type": "text"
    })
    
    # Add example test script
    request["event"] = [{
        "listen": "test",
        "script": {
            "type": "text/javascript",
            "exec": [
                "// Basic response validation",
                "pm.test(\"Status code is 200\", function () {",
                "    pm.response.to.have.status(200);",
                "});",
                "",
                "pm.test(\"Response time is acceptable\", function () {",
                "    pm.expect(pm.response.responseTime).to.be.below(500); // SLO: p95 < 500ms",
                "});",
                "",
                "pm.test(\"Response has valid JSON\", function () {",
                "    pm.response.to.be.json;",
                "});"
            ]
        }
    }]
    
    # Add pre-request script for logging
    request["event"].append({
        "listen": "prerequest",
        "script": {
            "type": "text/javascript",
            "exec": [
                "// Log request details",
                "console.log('Request URL:', pm.request.url.toString());",
                "console.log('Request Method:', pm.request.method);",
                "console.log('Timestamp:', new Date().toISOString());"
            ]
        }
    })

def create_postman_environment(output_path: Path):
    """Create Postman environment file with LUKHAS variables."""
    environment = {
        "id": "lukhas-api-env",
        "name": "LUKHAS API Environment",
        "values": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "default",
                "enabled": True
            },
            {
                "key": "api_key",
                "value": "your_api_key_here",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "model",
                "value": "lukhas-consciousness-v1",
                "type": "default",
                "enabled": True
            },
            {
                "key": "max_tokens",
                "value": "100",
                "type": "default",
                "enabled": True
            },
            {
                "key": "temperature",
                "value": "0.7",
                "type": "default",
                "enabled": True
            }
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_at": "2025-01-08T00:00:00.000Z",
        "_postman_exported_using": "Postman/10.0.0"
    }
    
    with open(output_path, "w") as f:
        json.dump(environment, f, indent=2)
    
    print(f"✅ Postman environment created: {output_path}")

def create_example_requests(output_dir: Path):
    """Create example request bodies for testing."""
    examples = {
        "chat_completion": {
            "model": "{{model}}",
            "messages": [
                {"role": "system", "content": "You are a consciousness-aware AI assistant."},
                {"role": "user", "content": "Explain the concept of consciousness."}
            ],
            "max_tokens": "{{max_tokens}}",
            "temperature": "{{temperature}}"
        },
        "response_generation": {
            "input": "What is the nature of consciousness?",
            "tools": [],
            "stream": False
        },
        "embeddings": {
            "model": "lukhas-embeddings-v1",
            "input": "Consciousness is the state of being aware of one's surroundings and thoughts."
        },
        "dream_generation": {
            "seed": "consciousness exploration",
            "depth": 5,
            "mode": "symbolic"
        }
    }
    
    examples_dir = output_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    for name, body in examples.items():
        example_path = examples_dir / f"{name}.json"
        with open(example_path, "w") as f:
            json.dump(body, f, indent=2)
        print(f"✅ Example created: {example_path}")

def main():
    """Main conversion workflow."""
    print("=" * 70)
    print("LUKHAS Postman Collection Generator")
    print("=" * 70)
    
    # Paths
    repo_root = Path(__file__).parent.parent
    openapi_path = repo_root / "docs" / "openapi" / "lukhas-openai.yaml"
    output_dir = repo_root / "docs" / "postman"
    output_dir.mkdir(exist_ok=True)
    
    collection_path = output_dir / "lukhas-api-collection.json"
    environment_path = output_dir / "lukhas-api-environment.json"
    
    # Check dependencies
    has_cli = check_dependencies()
    
    # Convert OpenAPI to Postman
    if not openapi_path.exists():
        print(f"❌ OpenAPI spec not found: {openapi_path}")
        sys.exit(1)
    
    if has_cli:
        success = convert_openapi_to_postman(openapi_path, collection_path)
        if not success:
            print("⚠️  CLI conversion failed, using fallback...")
            create_minimal_collection(collection_path)
    else:
        print("🔧 Using manual collection generation...")
        create_minimal_collection(collection_path)
    
    # Enhance collection
    enhance_postman_collection(collection_path)
    
    # Create environment
    create_postman_environment(environment_path)
    
    # Create example requests
    create_example_requests(output_dir)
    
    # Create README
    create_postman_readme(output_dir)
    
    print("\n" + "=" * 70)
    print("✅ Postman collection generation complete!")
    print("=" * 70)
    print(f"\nFiles created:")
    print(f"  📄 Collection:  {collection_path}")
    print(f"  🌍 Environment: {environment_path}")
    print(f"  📁 Examples:    {output_dir / 'examples'}/")
    print(f"  📖 README:      {output_dir / 'README.md'}")
    print(f"\nImport these files into Postman to get started!")

def create_minimal_collection(output_path: Path):
    """Create a minimal Postman collection manually (fallback)."""
    collection = {
        "info": {
            "name": "LUKHAS OpenAI-Compatible API",
            "description": "API collection for LUKHAS AI Platform",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/health",
                        "host": ["{{base_url}}"],
                        "path": ["health"]
                    }
                }
            },
            {
                "name": "List Models",
                "request": {
                    "method": "GET",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{api_key}}"}
                    ],
                    "url": {
                        "raw": "{{base_url}}/v1/models",
                        "host": ["{{base_url}}"],
                        "path": ["v1", "models"]
                    }
                }
            },
            {
                "name": "Create Response",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "Authorization", "value": "Bearer {{api_key}}"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "input": "What is consciousness?",
                            "tools": [],
                            "stream": False
                        }, indent=2)
                    },
                    "url": {
                        "raw": "{{base_url}}/v1/responses",
                        "host": ["{{base_url}}"],
                        "path": ["v1", "responses"]
                    }
                }
            }
        ]
    }
    
    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Minimal collection created: {output_path}")

def create_postman_readme(output_dir: Path):
    """Create README for Postman collection usage."""
    readme_content = """# LUKHAS Postman Collection

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

newman run lukhas-api-collection.json \\
  -e lukhas-api-environment.json \\
  --reporters cli,json \\
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
"""
    
    readme_path = output_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    print(f"✅ Postman README created: {readme_path}")

if __name__ == "__main__":
    main()
