# Guardian Policy Validation API

## Overview

The Guardian Policy Validation API provides comprehensive policy enforcement, action validation, and policy management for the LUKHAS system. It integrates with the Guardian system, Constitutional AI, and provides extensive audit logging for compliance.

## Implementation Details

### Module Location
- **Implementation**: `serve/guardian_api.py`
- **Tests**: `tests/unit/serve/test_guardian_api.py`

### API Endpoints

#### 1. POST `/guardian/validate`
Validate action against Guardian policies with comprehensive logging.

**Request Body:**
```json
{
  "action": "string",
  "context": {
    "key": "value"
  }
}
```

**Response:**
```json
{
  "valid": true,
  "score": 0.95,
  "violations": [],
  "explanation": "Action evaluated by Guardian system.",
  "veto": false,
  "validation_id": "uuid",
  "timestamp": "2025-11-15T12:00:00Z"
}
```

**Features:**
- User identity from JWT token (prevents spoofing)
- Guardian system integration
- Constitutional AI compliance checking
- Policy drift detection
- Comprehensive audit logging
- Unique validation ID for trail

**Validation Flow:**
1. Extract user from authenticated JWT token
2. Initialize Guardian system
3. Create governance action
4. Evaluate ethics via Guardian
5. Check Constitutional AI constraints (if available)
6. Calculate compliance score
7. Detect policy drift
8. Determine veto status
9. Log comprehensive audit trail
10. Return validation response

#### 2. GET `/guardian/policies`
List Guardian policies with optional filtering.

**Query Parameters:**
- `active_only` (boolean, default: true) - Return only active policies

**Response:**
```json
[
  {
    "policy_id": "guardian-ethics-001",
    "name": "Ethical Action Validation",
    "description": "Validates all actions against constitutional AI ethics framework",
    "active": true,
    "severity": "high"
  }
]
```

**Core Policies:**
1. **guardian-ethics-001**: Ethical Action Validation (high)
2. **guardian-drift-002**: Policy Drift Detection (medium)
3. **guardian-safety-003**: Safety Validation (critical)
4. **guardian-audit-004**: Audit Trail Logging (high)
5. **guardian-constitutional-005**: Constitutional AI Compliance (critical)

#### 3. GET `/guardian/health`
Guardian system health check (no auth required).

**Response:**
```json
{
  "status": "healthy",
  "active_policies": 5,
  "last_check": "2025-11-15T12:00:00Z",
  "drift_detected": false,
  "guardian_available": true,
  "constitutional_ai_available": true
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some systems unavailable
- `down`: Guardian system unavailable

#### 4. POST `/guardian/veto`
Record policy veto with explanation for audit trail.

**Request Body:**
```json
{
  "action_id": "action_123",
  "reason": "policy_violation",
  "explanation": "Detailed explanation of veto"
}
```

**Response:**
```json
{
  "veto_id": "uuid",
  "action_id": "action_123",
  "recorded_at": "2025-11-15T12:00:00Z",
  "status": "recorded"
}
```

### Legacy Endpoints (Backward Compatibility)

The API also includes legacy endpoints for backward compatibility:

- POST `/api/v1/guardian/validate` - Legacy validation
- GET `/api/v1/guardian/audit` - Legacy audit log
- GET `/api/v1/guardian/drift-check` - Legacy drift check

These endpoints maintain compatibility with existing tests and clients.

## Security

### Authentication
- All endpoints (except `/health`) require JWT authentication
- User identity extracted from validated JWT token via `get_current_user` dependency
- Client cannot spoof user_id via request body (OWASP A01 mitigation)
- StrictAuthMiddleware validates tokens before reaching endpoints

### Authorization
- User tier and permissions checked via JWT claims
- Rate limiting and throttling applied based on user tier
- Comprehensive logging of all user actions

### Audit Logging
All validation decisions are logged with:
- Validation ID (unique identifier)
- User ID (from JWT token)
- Action being validated
- Validation result (valid/invalid)
- Compliance score
- Veto status
- Ethical severity level
- Timestamp
- Duration

Example audit log:
```
AUDIT: Guardian validation - validation_id=abc-123, user_id=user_456,
action=user_login, result=True, score=0.950, veto=False,
ethical_severity=low
```

## Integration Points

### Guardian System
- **Module**: `governance.guardian.guardian_impl.GuardianSystemImpl`
- **Functions Used**:
  - `evaluate_ethics()` - Ethical evaluation
  - `detect_drift()` - Drift detection
  - `check_safety()` - Safety validation
  - `get_status()` - System status

### Constitutional AI
- **Module**: `governance.ethics.constitutional_ai.ConstitutionalAI`
- **Functions Used**:
  - `critique()` - Constitutional critique of actions

### Core Types
- **Module**: `governance.guardian.core`
- **Types Used**:
  - `EthicalSeverity` - Severity levels
  - `GovernanceAction` - Action representation
  - `EthicalDecision` - Evaluation result
  - `DriftResult` - Drift detection result

### Authentication
- **Module**: `lukhas.governance.auth.dependencies`
- **Functions Used**:
  - `get_current_user()` - Extract authenticated user from JWT

## Error Handling

### Graceful Degradation
When Guardian system is unavailable:
- Returns permissive result with warning
- Logs warning for monitoring
- Allows action to proceed with caution
- Sets score to 0.5 (neutral)
- Includes violation: "Guardian system unavailable"

### Error Responses
All errors return standardized format:
```json
{
  "error": {
    "message": "Description of error",
    "type": "error_type",
    "code": "error_code",
    "validation_id": "uuid"
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful validation/operation
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Guardian system error

## Testing

### Test Coverage
- **Legacy endpoints**: Full compatibility tests
- **New endpoints**: Comprehensive test suite including:
  - Authentication requirements
  - Response structure validation
  - Active policy filtering
  - Health check responses
  - Veto recording
  - Integration workflows
  - Audit trail logging

### Running Tests
```bash
pytest tests/unit/serve/test_guardian_api.py -v
```

### Test Classes
1. `TestValidate` - Legacy validate endpoint
2. `TestAudit` - Legacy audit endpoint
3. `TestDriftCheck` - Legacy drift check endpoint
4. `TestNewValidateEndpoint` - New validation endpoint
5. `TestNewPoliciesEndpoint` - Policies listing
6. `TestNewHealthEndpoint` - Health check
7. `TestNewVetoEndpoint` - Veto recording
8. `TestIntegrationScenarios` - End-to-end workflows

## Performance

### Response Times
- **Validation**: < 100ms typical, < 250ms p99
- **Policies**: < 50ms typical
- **Health**: < 100ms typical
- **Veto**: < 50ms typical

### Concurrency
- All endpoints are async (using FastAPI async handlers)
- Support concurrent requests
- Thread-safe singleton pattern for Guardian system
- Lazy loading of Guardian and Constitutional AI

### Logging Performance
- Structured logging with correlation IDs
- Non-blocking I/O for log writes
- Configurable log levels via environment

## Usage Examples

### Python Client
```python
import requests

# Authenticate
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}

# Validate action
response = requests.post(
    "https://api.lukhas.ai/guardian/validate",
    headers=headers,
    json={
        "action": "data_access",
        "context": {"resource": "/sensitive/data"}
    }
)
validation = response.json()
print(f"Valid: {validation['valid']}, Score: {validation['score']}")

# List policies
policies = requests.get(
    "https://api.lukhas.ai/guardian/policies",
    headers=headers
).json()

# Check health
health = requests.get("https://api.lukhas.ai/guardian/health").json()
print(f"Status: {health['status']}")
```

### cURL Examples
```bash
# Validate action
curl -X POST https://api.lukhas.ai/guardian/validate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "user_login", "context": {"ip": "127.0.0.1"}}'

# List active policies
curl https://api.lukhas.ai/guardian/policies?active_only=true \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Health check
curl https://api.lukhas.ai/guardian/health

# Record veto
curl -X POST https://api.lukhas.ai/guardian/veto \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "action_123",
    "reason": "policy_violation",
    "explanation": "Action violated ethical guidelines"
  }'
```

## Configuration

### Environment Variables
- `GUARDIAN_ACTIVE`: Enable/disable Guardian system (default: false)
- `LUKHAS_API_KEY`: API key for protected endpoints
- `LUKHAS_POLICY_MODE`: Policy enforcement mode (strict/permissive)

### Router Configuration
```python
from serve.guardian_api import router, legacy_router

app = FastAPI()

# Include new Guardian API
app.include_router(router)

# Include legacy API for backward compatibility
app.include_router(legacy_router)
```

## Monitoring & Observability

### Metrics
The API emits the following metrics (when Prometheus available):
- `lukhas_guardian_policy_evaluations_total` - Total policy evaluations
- `lukhas_guardian_policy_evaluation_latency_seconds` - Evaluation latency
- `lukhas_guardian_active_policies_total` - Number of active policies

### Logs
Structured JSON logs with fields:
- `validation_id` - Unique validation identifier
- `user_id` - Authenticated user
- `action` - Action being validated
- `result` - Validation result
- `score` - Compliance score
- `veto` - Veto status
- `duration_ms` - Processing duration

### Tracing
OpenTelemetry spans for distributed tracing:
- Validation flow end-to-end
- Guardian system calls
- Constitutional AI calls
- Database operations (when implemented)

## Future Enhancements

### Planned Features
1. **Database Persistence**: Store validation history and veto records
2. **Policy Management**: CRUD operations for policies via API
3. **Real-time Notifications**: WebSocket support for policy violations
4. **Advanced Analytics**: Trend analysis and reporting
5. **Policy Versioning**: Track policy changes over time
6. **A/B Testing**: Compare policy configurations
7. **Machine Learning**: Learn from validation patterns

### Migration Path
The dual-router approach (new + legacy) allows gradual migration:
1. Phase 1: Deploy both routers (current)
2. Phase 2: Migrate clients to new endpoints
3. Phase 3: Deprecate legacy endpoints
4. Phase 4: Remove legacy router

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: https://github.com/LukhasAI/Lukhas/issues
- Documentation: https://docs.lukhas.ai/guardian-api
- Email: support@lukhas.ai
