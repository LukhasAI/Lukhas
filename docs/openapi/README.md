# LUKHAS OpenAPI Specifications

**Status**: Production | **Version**: v1 | **Updated**: 2025-10-18

---

## Overview

This directory contains comprehensive OpenAPI 3.1 specifications for the LUKHAS AI Platform's core API ecosystem. These specifications provide machine-readable contracts for identity, consciousness, guardian, MATRIZ cognitive engine, and orchestration systems.

**Constellation Framework Coverage**:
- ⚛️ **Identity**: Authentication, authorization, ΛID management
- 🧠 **Consciousness**: Stream processing, state synthesis, memory folds
- 🛡️ **Guardian**: Drift detection, ethics validation, constitutional AI
- 🧬 **MATRIZ**: Cognitive DNA engine, reasoning chains, provenance
- 🌸 **Orchestration**: Multi-system workflows, task routing, service mesh

---

## API Specifications

### 1. Identity API (`identity_api.openapi.yaml`)

**Purpose**: Lambda Identity (ΛID) authentication and authorization  
**Base Path**: `/v1/identity`  
**Endpoints**: 6 (login, logout, refresh, tier management, QR entropy, sessions)

**Key Features**:
- JWT Bearer token authentication
- 6-tier access control (Tier 0-5)
- QR code steganographic entropy generation
- Cross-device token synchronization
- Session lifecycle management

**Authentication Flow**:
```bash
# Step 1: Login
curl -X POST https://api.lukhas.ai/v1/identity/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "secure_password"}'

# Returns: {"access_token": "eyJ...", "refresh_token": "eyJ...", "user_tier": 3}

# Step 2: Use Bearer token for all other APIs
curl -X POST https://api.lukhas.ai/v1/consciousness/process \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"input": "Analyze this thought", "context": {...}}'
```

---

### 2. Consciousness API (`consciousness_api.openapi.yaml`)

**Purpose**: Consciousness processing and state management  
**Base Path**: `/v1/consciousness`  
**Endpoints**: 7 (process, state, synthesize, memory folds, awareness)

**Key Features**:
- Asynchronous stream processing
- Multi-state synthesis with conflict resolution
- Memory fold creation and traversal
- Awareness metrics tracking (level, coherence, integration)
- Temporal state transitions

**Example Usage**:
```bash
# Process consciousness stream
curl -X POST https://api.lukhas.ai/v1/consciousness/process \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Analyze this thought pattern",
    "context": {"user_id": "U-12345", "session_id": "S-67890"},
    "processing_mode": "deep",
    "stream": true
  }'

# Returns: {"state_id": "CS-abc123", "status": "processing", "estimated_completion": "2025-10-18T14:35:00Z"}
```

---

### 3. Guardian API (`guardian_api.openapi.yaml`)

**Purpose**: Constitutional AI, ethics enforcement, system monitoring  
**Base Path**: `/v1/guardian`  
**Endpoints**: 6 (drift analysis, drift repair, ethics validation, audit trails, health)

**Key Features**:
- Real-time drift detection and severity analysis
- Automated drift repair with surgical precision
- Constitutional AI ethics validation
- Λ-trace audit trail with provenance tracking
- System health monitoring with service mesh status

**Example Usage**:
```bash
# Analyze system drift
curl -X POST https://api.lukhas.ai/v1/guardian/drift/analyze \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "component": "consciousness",
    "scope": "full",
    "reference_baseline": "v1.0.0"
  }'

# Returns: {"drift_detected": true, "severity": "medium", "affected_areas": ["state_synthesis", "memory_fold"], "repair_plan": {...}}
```

---

### 4. MATRIZ API (`matriz_api.openapi.yaml`)

**Purpose**: MATRIZ cognitive DNA engine with node-based reasoning  
**Base Path**: `/v1/matriz`  
**Endpoints**: 8 (nodes, execute, reasoning chains, provenance, semantic links)

**Key Features**:
- Dynamic node registration and management
- Multi-node reasoning chain coordination
- Complete provenance tracking (TraceRouter)
- Semantic link creation between cognitive nodes
- Memory-backed node persistence

**Example Usage**:
```bash
# Create reasoning chain
curl -X POST https://api.lukhas.ai/v1/matriz/reasoning/chains \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "chain_name": "Ethical Decision Chain",
    "nodes": [
      {"node_id": "N-fact-001", "type": "FactNode"},
      {"node_id": "N-val-002", "type": "ValidatorNode"},
      {"node_id": "N-math-003", "type": "MathNode"}
    ],
    "reasoning_goal": "Evaluate ethical implications of action X"
  }'

# Returns: {"chain_id": "RC-xyz789", "status": "created", "node_count": 3}
```

---

### 5. Orchestration API (`orchestration_api.openapi.yaml`)

**Purpose**: Multi-system workflow orchestration and service coordination  
**Base Path**: `/v1/orchestration`  
**Endpoints**: 8 (workflows, execute, task routing, services, monitoring)

**Key Features**:
- Multi-system workflow definitions (DAG-based)
- Asynchronous workflow execution with state tracking
- Dynamic task routing to specialized agents
- Service mesh management with health checks
- Performance monitoring with Prometheus metrics

**Example Usage**:
```bash
# Create and execute workflow
curl -X POST https://api.lukhas.ai/v1/orchestration/workflows \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Consciousness Processing Pipeline",
    "steps": [
      {"step_id": "1", "service": "consciousness", "action": "process"},
      {"step_id": "2", "service": "matriz", "action": "reason"},
      {"step_id": "3", "service": "guardian", "action": "validate"}
    ],
    "dependencies": [
      {"from": "1", "to": "2"},
      {"from": "2", "to": "3"}
    ]
  }'

# Returns: {"workflow_id": "WF-123", "status": "ready"}

# Execute workflow
curl -X POST https://api.lukhas.ai/v1/orchestration/workflows/WF-123/execute \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"thought": "Analyze this"}}'

# Returns: {"execution_id": "EX-456", "status": "running"}
```

---

## Validation

### Prerequisites

Install OpenAPI validation tools:

```bash
# Option 1: Swagger CLI (Node.js)
npm install -g @apidevtools/swagger-cli

# Option 2: OpenAPI Generator CLI (Java)
brew install openapi-generator

# Option 3: Spectral (Node.js - advanced linting)
npm install -g @stoplight/spectral-cli
```

### Validate Individual Specs

```bash
# Using Swagger CLI
swagger-cli validate docs/openapi/identity_api.openapi.yaml
swagger-cli validate docs/openapi/consciousness_api.openapi.yaml
swagger-cli validate docs/openapi/guardian_api.openapi.yaml
swagger-cli validate docs/openapi/matriz_api.openapi.yaml
swagger-cli validate docs/openapi/orchestration_api.openapi.yaml

# Using OpenAPI Generator
openapi-generator-cli validate -i docs/openapi/identity_api.openapi.yaml
openapi-generator-cli validate -i docs/openapi/consciousness_api.openapi.yaml
openapi-generator-cli validate -i docs/openapi/guardian_api.openapi.yaml
openapi-generator-cli validate -i docs/openapi/matriz_api.openapi.yaml
openapi-generator-cli validate -i docs/openapi/orchestration_api.openapi.yaml

# Using Spectral (with custom ruleset)
spectral lint docs/openapi/identity_api.openapi.yaml
spectral lint docs/openapi/consciousness_api.openapi.yaml
spectral lint docs/openapi/guardian_api.openapi.yaml
spectral lint docs/openapi/matriz_api.openapi.yaml
spectral lint docs/openapi/orchestration_api.openapi.yaml
```

### Validate All Specs (Batch)

```bash
# Create validation script
cat > validate_all_apis.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Validating LUKHAS OpenAPI Specifications..."
echo ""

for spec in docs/openapi/*_api.openapi.yaml; do
  echo "Validating $(basename $spec)..."
  swagger-cli validate "$spec"
  echo "✅ $(basename $spec) is valid"
  echo ""
done

echo "✨ All OpenAPI specifications validated successfully!"
EOF

chmod +x validate_all_apis.sh
./validate_all_apis.sh
```

### Bundle Specs (Single File)

```bash
# Bundle all specs into single file for easier distribution
swagger-cli bundle docs/openapi/identity_api.openapi.yaml \
  --outfile docs/openapi/bundled/identity_api.bundle.yaml \
  --dereference

# Repeat for other APIs...
```

---

## Code Generation

### Generate Client Libraries

```bash
# Python client for Identity API
openapi-generator-cli generate \
  -i docs/openapi/identity_api.openapi.yaml \
  -g python \
  -o generated/python-client/identity \
  --additional-properties=packageName=lukhas_identity,projectName=lukhas-identity-client

# TypeScript client for Consciousness API
openapi-generator-cli generate \
  -i docs/openapi/consciousness_api.openapi.yaml \
  -g typescript-axios \
  -o generated/typescript-client/consciousness \
  --additional-properties=npmName=@lukhas/consciousness-client

# Go client for Guardian API
openapi-generator-cli generate \
  -i docs/openapi/guardian_api.openapi.yaml \
  -g go \
  -o generated/go-client/guardian \
  --additional-properties=packageName=guardian

# Java client for MATRIZ API
openapi-generator-cli generate \
  -i docs/openapi/matriz_api.openapi.yaml \
  -g java \
  -o generated/java-client/matriz \
  --additional-properties=groupId=ai.lukhas,artifactId=matriz-client

# Rust client for Orchestration API
openapi-generator-cli generate \
  -i docs/openapi/orchestration_api.openapi.yaml \
  -g rust \
  -o generated/rust-client/orchestration \
  --additional-properties=packageName=lukhas_orchestration
```

### Generate Server Stubs

```bash
# Python FastAPI server stubs
openapi-generator-cli generate \
  -i docs/openapi/identity_api.openapi.yaml \
  -g python-fastapi \
  -o generated/server-stubs/identity \
  --additional-properties=packageName=lukhas_identity_api

# Node.js Express server stubs
openapi-generator-cli generate \
  -i docs/openapi/consciousness_api.openapi.yaml \
  -g nodejs-express-server \
  -o generated/server-stubs/consciousness \
  --additional-properties=packageName=lukhas-consciousness-api
```

### Generate Documentation

```bash
# HTML documentation (Redoc)
npx @redocly/cli build-docs docs/openapi/identity_api.openapi.yaml \
  --output docs/openapi/html/identity_api.html

# Markdown documentation
openapi-generator-cli generate \
  -i docs/openapi/identity_api.openapi.yaml \
  -g markdown \
  -o docs/openapi/markdown/identity

# Postman collection
openapi-generator-cli generate \
  -i docs/openapi/identity_api.openapi.yaml \
  -g postman-collection \
  -o docs/openapi/postman/identity
```

---

## Testing

### Manual API Testing

```bash
# Test Identity login endpoint
curl -X POST https://api.lukhas.ai/v1/identity/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@lukhas.ai", "password": "Test123!"}' \
  -v

# Test Consciousness processing (requires valid token)
curl -X POST https://api.lukhas.ai/v1/consciousness/process \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"input": "Test thought", "context": {}, "processing_mode": "fast"}' \
  -v

# Test Guardian health check
curl -X GET https://api.lukhas.ai/v1/guardian/health \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -v
```

### Contract Testing (Prism Mock Server)

```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Start mock server for Identity API
prism mock docs/openapi/identity_api.openapi.yaml --port 4010

# Start mock server for Consciousness API
prism mock docs/openapi/consciousness_api.openapi.yaml --port 4011

# Test against mock server
curl -X POST http://localhost:4010/v1/identity/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@lukhas.ai", "password": "Test123!"}'

# Prism will return example responses from the OpenAPI spec
```

### Automated Contract Testing (Schemathesis)

```bash
# Install Schemathesis
pip install schemathesis

# Run automated tests against Identity API
schemathesis run docs/openapi/identity_api.openapi.yaml \
  --base-url https://api.lukhas.ai \
  --checks all \
  --hypothesis-max-examples=100

# Run tests with authentication
export LUKHAS_AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
schemathesis run docs/openapi/consciousness_api.openapi.yaml \
  --base-url https://api.lukhas.ai \
  --header "Authorization: Bearer $LUKHAS_AUTH_TOKEN" \
  --checks all
```

---

## Manifest Mappings

See `manifest_api_mapping.json` for the complete mapping between module manifests and API specifications. This file provides:

- **Manifest-to-API Links**: Which manifest corresponds to which OpenAPI spec
- **API Relationships**: How APIs depend on or integrate with each other
- **Authentication Flow**: Step-by-step JWT token acquisition and usage
- **Common Response Codes**: Standard HTTP status codes across all APIs
- **Versioning Strategy**: URI path versioning with deprecation policy

**Example Mapping**:
```json
{
  "manifest_path": "manifests/identity/module.manifest.json",
  "openapi_spec": "docs/openapi/identity_api.openapi.yaml",
  "api_base_path": "/v1/identity",
  "constellation_star": "⚛️ Identity"
}
```

---

## Server Endpoints

### Production
- **Base URL**: `https://api.lukhas.ai`
- **Environment**: Production
- **Region**: Global (multi-region)
- **SSL**: TLS 1.3

### Staging
- **Base URL**: `https://staging-api.lukhas.ai`
- **Environment**: Staging
- **Region**: US-West-2
- **SSL**: TLS 1.3

### Local Development
- **Base URL**: `http://localhost:8000`
- **Environment**: Development
- **Region**: Local
- **SSL**: None (HTTP only)

---

## Security

### Authentication
- **Method**: JWT Bearer tokens
- **Header**: `Authorization: Bearer {access_token}`
- **Token Lifespan**: 
  - Access Token: 1 hour
  - Refresh Token: 7 days

### Authorization
- **Tier-Based Access**: 6 levels (Tier 0-5)
- **Scope-Based Permissions**: Fine-grained resource access control
- **Rate Limiting**: 
  - Tier 0: 10 req/min
  - Tier 1-2: 100 req/min
  - Tier 3-4: 1000 req/min
  - Tier 5: Unlimited

### Best Practices
- Store tokens securely (never in localStorage for web apps)
- Use HTTPS for all API communication
- Implement token refresh before expiration
- Handle 401 errors with automatic re-authentication
- Implement exponential backoff for rate limit errors (429)

---

## Versioning

**Strategy**: URI Path Versioning  
**Current Version**: v1  
**Format**: `/v{major}/resource`  
**Deprecation Policy**: 6 months notice before version removal

**Example Evolution**:
- `/v1/identity/auth/login` (current)
- `/v2/identity/auth/login` (future - breaking changes)
- `/v1/identity/auth/login` (deprecated after 6 months of v2 availability)
- `/v1/identity/auth/login` (removed after deprecation period)

---

## Legacy OpenAPI Artifacts

- **Generated spec**: `docs/openapi/lukhas-openapi.json` (via `make openapi-spec`)
- **CI validation**: `make openapi-validate`
- **Note**: Legacy artifacts coexist with new v1 specifications during transition period

---

## Additional Resources

- **LUKHAS Architecture**: See `claude.me` for complete system overview
- **Module Manifests**: See `manifests/` directory for module metadata
- **Schema Definitions**: See `schemas/module.manifest.schema.json`
- **Context Files**: See `{domain}/claude.me` for domain-specific architecture

---

## Maintenance

### Update Checklist

When modifying API specifications:

- [ ] Update OpenAPI spec file with changes
- [ ] Validate spec with `swagger-cli validate`
- [ ] Update examples in README
- [ ] Regenerate client libraries if schema changes
- [ ] Update `manifest_api_mapping.json` if endpoints change
- [ ] Update module manifest if capabilities change
- [ ] Update integration tests
- [ ] Update API documentation website
- [ ] Announce changes via changelog
- [ ] Consider deprecation timeline if breaking changes

### Monitoring

- **API Health**: https://status.lukhas.ai
- **Performance Metrics**: Grafana dashboards
- **Error Tracking**: Sentry integration
- **Audit Trails**: Guardian Λ-trace system

---

**Last Updated**: 2025-10-18  
**Maintained By**: LUKHAS Platform Team  
**Contact**: api-support@lukhas.ai

*⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian · 🧬 MATRIZ · 🌸 Orchestration*

