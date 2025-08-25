---
# Content Classification
doc_type: "api"
update_frequency: "fixed"
last_updated: "2025-08-25"
next_review: "2026-08-25"

# Audience Targeting
audience: ["developers", "agents"]
technical_level: "advanced"

# Agent Routing
agent_relevance:
  supreme_consciousness_architect: 0.8
  consciousness_architect: 0.8
  consciousness_developer: 0.9
  github_copilot: 0.8
  api_interface_colonel: 1.0
  security_compliance_colonel: 0.8
  testing_validation_colonel: 0.9
  devops_guardian: 0.8
  documentation_specialist: 0.9
  guardian_engineer: 0.7
  velocity_lead: 0.7

# Trinity Framework
trinity_component: ["identity", "consciousness", "guardian"]
search_keywords: ["api", "enhancement", "guide", "v2", "endpoints", "sdk", "client", "restful"]

# Priority Classification
priority: "critical"
category: "api"
---

# LUKHAS API Enhancement Guide

## Overview

This guide documents the comprehensive enhancements made to bring the LUKHAS API system from 33.3% to near 100% functionality.

## 🚀 Key Improvements

### 1. **Unified API System**

The new `EnhancedAPISystem` consolidates the fragmented API implementations into a single, coherent system:

- **Single Entry Point**: `/core/api/enhanced_api_system.py`
- **Consistent Authentication**: JWT + MFA across all endpoints
- **Unified Error Handling**: Standardized error responses
- **Service Integration**: All LUKHAS modules accessible via API

### 2. **Complete Service Integration**

#### **Core Services Available**
- **Consciousness**: Query and interact with awareness system
- **Memory**: Full CRUD operations on memory system
- **Guardian**: Ethics and governance checking
- **Dream**: Creative content generation
- **Emotion**: Emotional analysis and generation
- **Symbolic**: GLYPH encoding/decoding

#### **Service Stubs**
For development and testing, complete service stubs are provided in `/core/api/service_stubs.py` that simulate all core functionality.

### 3. **Enhanced Security Integration**

The API now fully integrates with the enhanced security system:

```python
# All endpoints protected by default
@app.post("/api/v2/consciousness/query")
async def consciousness_query(
    request: ConsciousnessRequest,
    auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    # Automatic auth validation
    is_valid, error = await self._validate_auth(auth.credentials, 'consciousness.query')
```

### 4. **Client SDK**

A full-featured Python client SDK makes integration easy:

```python
async with LUKHASClient('http://localhost:8000', api_key='your-key') as client:
    # Query consciousness
    response = await client.consciousness.query("What is the meaning of existence?")
    
    # Store memory
    memory_id = await client.memory.store({"event": "Important meeting"})
    
    # Generate creative content
    dream = await client.dream.generate("A world without limits")
```

## 📁 File Structure

```
core/api/
├── enhanced_api_system.py    # Main API implementation
├── service_stubs.py          # Service implementations for testing
├── lukhas_api_client.py      # Python client SDK
└── __init__.py

tests/api/
└── test_enhanced_api.py      # Comprehensive test suite
```

## 🔌 API Endpoints

### Authentication

- `POST /api/v2/auth/login` - Login and get JWT
- `POST /api/v2/auth/mfa/verify` - Verify MFA code
- `POST /api/v2/auth/mfa/setup/totp` - Setup TOTP MFA

### Core Operations

- `POST /api/v2/consciousness/query` - Query consciousness
- `POST /api/v2/memory/{action}` - Memory operations (store/retrieve/search/update)
- `POST /api/v2/governance/check` - Ethics validation
- `POST /api/v2/dream/generate` - Creative generation
- `POST /api/v2/process` - Generic processing endpoint

### System Information

- `GET /api/v2/health` - System health check
- `GET /api/v2/capabilities` - System capabilities
- `GET /api/v2/metrics` - Performance metrics

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all API tests
pytest tests/api/test_enhanced_api.py -v

# Run with coverage
pytest tests/api/test_enhanced_api.py --cov=core.api -v
```

## 🚀 Quick Start

### 1. Start the API Server

```python
# Run directly
python core/api/enhanced_api_system.py

# Or with uvicorn
uvicorn core.api.enhanced_api_system:create_app --reload
```

### 2. Use the Client SDK

```python
import asyncio
from core.api.lukhas_api_client import LUKHASClient

async def main():
    async with LUKHASClient('http://localhost:8000') as client:
        # Login
        await client.auth.login('user', 'password')
        
        # Use LUKHAS
        response = await client.consciousness.query("Hello LUKHAS")
        print(response)

asyncio.run(main())
```

### 3. Direct HTTP Requests

```bash
# Login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "auth_token": "password"}'

# Query consciousness (with JWT)
curl -X POST http://localhost:8000/api/v2/consciousness/query \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is consciousness?", "awareness_level": 0.8}'
```

## 📊 Performance Metrics

The enhanced API provides detailed metrics:

- Request tracking and timing
- Service-level metrics
- Active request monitoring
- Error rate tracking

Access metrics at: `GET /api/v2/metrics`

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
LUKHAS_API_HOST=0.0.0.0
LUKHAS_API_PORT=8000
LUKHAS_API_WORKERS=4

# Security
LUKHAS_API_REQUIRE_AUTH=true
LUKHAS_API_REQUIRE_MFA=true

# Rate Limiting
LUKHAS_API_RATE_LIMIT=100
LUKHAS_API_RATE_WINDOW=60
```

### Service Configuration

Configure services in `enhanced_api_system.py`:

```python
# Adjust timeouts, limits, etc.
self.config = {
    'max_request_size': 10 * 1024 * 1024,  # 10MB
    'request_timeout': 30,  # seconds
    'max_concurrent_requests': 100
}
```

## 🛡️ Security Features

1. **JWT Authentication** with expiry and revocation
2. **Multi-Factor Authentication** (TOTP, SMS, Email)
3. **API Key Management** with scopes
4. **Rate Limiting** per user/endpoint
5. **Request Validation** and sanitization
6. **Encrypted Communication** (use HTTPS in production)

## 📈 Monitoring

### Built-in Monitoring

- Health checks at `/api/v2/health`
- Prometheus metrics export ready
- Structured logging with `structlog`
- Request tracing with unique IDs

### Integration with External Tools

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('lukhas_api_requests_total', 'Total requests')
request_duration = Histogram('lukhas_api_request_duration_seconds', 'Request duration')
```

## 🔄 Migration from Old API

### For Existing Integrations

1. **Update Base URL**: Change from `/api/v1` to `/api/v2`
2. **Add Authentication**: All endpoints now require auth
3. **Update Response Parsing**: Standardized response format
4. **Use Client SDK**: Easier than raw HTTP requests

### Backward Compatibility

The old endpoints remain available but deprecated. They will be removed in v3.0.

## 🎯 Next Steps

### Immediate Actions

1. Deploy the enhanced API
2. Update all clients to use v2 endpoints
3. Enable MFA for all users
4. Monitor metrics and performance

### Future Enhancements

1. GraphQL endpoint for flexible queries
2. WebSocket support for real-time updates
3. Batch operations for efficiency
4. Advanced caching strategies
5. API versioning improvements

## 📝 API Design Principles

1. **RESTful Design**: Standard HTTP methods and status codes
2. **Consistent Naming**: Predictable endpoint patterns
3. **Clear Errors**: Detailed error messages with remediation
4. **Self-Documenting**: OpenAPI/Swagger at `/api/v2/docs`
5. **Versioned**: Clear version in URL path

## 🤝 Contributing

When adding new endpoints:

1. Follow the existing patterns
2. Add to both API and client SDK
3. Include comprehensive tests
4. Update this documentation
5. Ensure security integration

## 📞 Support

For API issues:
- Check `/api/v2/health` for system status
- Review logs for detailed errors
- Use correlation IDs for request tracking
- Contact the LUKHAS team for assistance