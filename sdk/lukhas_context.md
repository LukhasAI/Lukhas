---
status: wip
type: documentation
---
> **Note**: This is a vendor-neutral version of claude.me for compatibility with any AI tool or development environment.


# SDK Module - LUKHAS Software Development Kits

**Module**: sdk
**Lane**: L2 Integration
**Team**: Core
**Purpose**: Software Development Kits for LUKHAS AI integration in Python, TypeScript, and other languages

---

## Overview

The sdk module provides official Software Development Kits (SDKs) for integrating LUKHAS AI capabilities into external applications. Currently supports Python and TypeScript/JavaScript, with additional language support planned.

**Key Features**:
- Python SDK for LUKHAS AI integration
- TypeScript/JavaScript SDK
- Publisher tools for SDK distribution
- Merchant integration utilities
- Type-safe API clients
- Authentication helpers

---

## Architecture

### Module Structure

```
sdk/
├── README.md                    # Module overview
├── module.manifest.json         # Module metadata
├── python/                      # Python SDK
│   ├── lukhas_sdk/             # SDK package
│   └── setup.py                # Package configuration
├── typescript/                  # TypeScript SDK
│   ├── src/                    # Source code
│   └── package.json            # NPM configuration
├── ts/                         # Additional TypeScript utilities
├── publisher/                   # SDK publishing tools
├── merchant/                    # Merchant integration tools
├── docs/                        # SDK documentation
└── tests/                       # SDK tests
```

---

## Python SDK

**Installation**:
```bash
pip install lukhas-sdk
```

**Basic Usage**:
```python
from lukhas_sdk import LUKHASClient

# Initialize client
client = LUKHASClient(
    api_key="your_api_key",
    endpoint="https://api.lukhas.ai",
)

# Consciousness API
response = client.consciousness.process(
    input="User message",
    awareness_level=0.75,
)

# Memory API
memory = client.memory.create(
    content="Important information",
    fold_id="conversation_123",
)

# Identity API
session = client.identity.authenticate(
    credentials=credentials,
)
```

**Features**:
- Type hints for IDE support
- Async/await support
- Automatic retry logic
- Built-in rate limiting
- Error handling
- Request/response logging

---

## TypeScript SDK

**Installation**:
```bash
npm install @lukhas/sdk
# or
yarn add @lukhas/sdk
```

**Basic Usage**:
```typescript
import { LUKHASClient } from '@lukhas/sdk';

// Initialize client
const client = new LUKHASClient({
  apiKey: 'your_api_key',
  endpoint: 'https://api.lukhas.ai',
});

// Consciousness API
const response = await client.consciousness.process({
  input: 'User message',
  awarenessLevel: 0.75,
});

// Memory API
const memory = await client.memory.create({
  content: 'Important information',
  foldId: 'conversation_123',
});

// Identity API
const session = await client.identity.authenticate({
  credentials,
});
```

**Features**:
- Full TypeScript type definitions
- Promise-based async API
- Browser and Node.js support
- Automatic type inference
- Built-in error types
- Request interceptors

---

## SDK Components

### 1. API Clients
- **ConsciousnessClient**: Consciousness processing APIs
- **MemoryClient**: Memory management APIs
- **IdentityClient**: Authentication and identity APIs
- **GuardianClient**: Safety and compliance APIs
- **MATRIZClient**: Pipeline orchestration APIs

### 2. Authentication
```python
# API Key authentication
client = LUKHASClient(api_key="key")

# OAuth2 authentication
client = LUKHASClient(
    oauth_client_id="id",
    oauth_client_secret="secret",
)

# JWT token authentication
client = LUKHASClient(jwt_token="token")
```

### 3. Error Handling
```python
from lukhas_sdk.exceptions import (
    LUKHASError,
    AuthenticationError,
    RateLimitError,
    APIError,
)

try:
    response = client.consciousness.process(input)
except AuthenticationError:
    # Handle authentication failure
    pass
except RateLimitError as e:
    # Handle rate limit
    retry_after = e.retry_after
except APIError as e:
    # Handle API error
    status_code = e.status_code
    message = e.message
```

---

## Publisher Tools

**Purpose**: Tools for publishing and distributing LUKHAS SDKs.

**Features**:
- Automated version management
- Multi-platform distribution (PyPI, NPM)
- Changelog generation
- Documentation building
- Release automation

---

## Merchant Integration

**Purpose**: Tools for integrating LUKHAS into e-commerce and merchant platforms.

**Features**:
- Payment processing integration
- Subscription management
- Usage tracking
- Billing integration

---

## Configuration

```yaml
sdk:
  python:
    version: "1.0.0"
    min_python_version: "3.9"
    dependencies:
      - "requests>=2.28.0"
      - "pydantic>=2.0.0"

  typescript:
    version: "1.0.0"
    target: "ES2020"
    module: "ESNext"

  publishing:
    pypi:
      enabled: true
      repository: "https://pypi.org/simple"
    npm:
      enabled: true
      registry: "https://registry.npmjs.org"
```

---

## Development

### Building Python SDK
```bash
cd sdk/python
python setup.py sdist bdist_wheel
```

### Building TypeScript SDK
```bash
cd sdk/typescript
npm run build
```

### Running Tests
```bash
# Python SDK tests
pytest sdk/python/tests

# TypeScript SDK tests
npm test --prefix sdk/typescript
```

---

## Observability

**Required Spans**:
- `lukhas.sdk.operation`

**Metrics**:
- SDK usage by version
- API call count by SDK
- Error rate by SDK version

---

## Related Modules

- **api/**: Backend APIs that SDKs consume
- **identity/**: Authentication endpoints
- **serve/**: API serving infrastructure

---

## Quick Reference

| SDK | Language | Installation | Package |
|-----|----------|-------------|---------|
| Python | Python 3.9+ | `pip install lukhas-sdk` | PyPI |
| TypeScript | TypeScript/JavaScript | `npm install @lukhas/sdk` | NPM |

---

**Module Status**: L2 Integration
**Schema Version**: 3.0.0
**Last Updated**: 2025-10-18
**Philosophy**: SDKs should make the complex simple—provide excellent developer experience above all.
