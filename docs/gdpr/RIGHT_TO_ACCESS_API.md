# GDPR Right to Access API (Article 15)

## Overview

The Right to Access API allows users to retrieve all personal data that LUKHAS holds about them, as required by **GDPR Article 15**.

This is a **P0 legal requirement** with fines up to **4% of annual revenue or €20 million** (whichever is higher) for non-compliance.

## Endpoint

```
GET /api/v1/data-rights/users/{user_id}/data
```

### Parameters

- `user_id` (path parameter, required): User identifier (ΛID) or "me" for current user

## Authentication

Requires authentication via one of:
- **Bearer token**: `Authorization: Bearer <token>`
- **API key**: `x-api-key: <api-key>`

## Authorization

- **Users** can access only their own data
- **Admins** can access any user's data
- Attempting to access another user's data (non-admin) returns `403 Forbidden`

## Response

Returns a comprehensive JSON object containing all personal data:

### Response Schema

```json
{
  "requested_at": "2025-11-15T12:00:00Z",
  "user_id": "user123",
  "identity": {
    "lambda_id": "user123",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-11-15T00:00:00Z",
    "profile": {
      "display_name": "User Name",
      "avatar_url": null,
      "bio": null
    },
    "preferences": {
      "theme": "dark",
      "language": "en",
      "notifications_enabled": true
    },
    "verification_status": {
      "email_verified": true,
      "phone_verified": false,
      "identity_verified": false
    }
  },
  "memory": {
    "total_folds": 0,
    "memory_folds": [],
    "consciousness_states": [],
    "embeddings_count": 0,
    "memory_usage_mb": 0.0,
    "oldest_memory": null,
    "newest_memory": null
  },
  "consciousness": {
    "consciousness_level": "basic",
    "reflection_logs": [],
    "reasoning_traces": [],
    "symbolic_states": [],
    "glyph_interactions": []
  },
  "interactions": [],
  "processing_purposes": [
    "Providing AI consciousness services",
    "Memory fold creation and retrieval",
    "Personalization and user experience optimization",
    "Service improvement and feature development",
    "Security, fraud prevention, and abuse detection",
    "Legal compliance and regulatory requirements",
    "Customer support and communication",
    "Analytics and performance monitoring"
  ],
  "retention_periods": {
    "identity_data": "Account lifetime + 30 days after deletion",
    "memory_folds": "90 days (user configurable, max 365 days)",
    "consciousness_states": "90 days or until deletion",
    "interaction_logs": "180 days",
    "api_logs": "90 days",
    "audit_logs": "6 years (legal requirement)",
    "security_logs": "1 year",
    "analytics_data": "14 months (aggregated only)"
  },
  "third_parties": [
    "Cloud infrastructure providers (AWS, GCP) - hosting and storage",
    "Email service provider (SendGrid) - transactional emails",
    "Analytics providers (if opted in) - usage analytics",
    "Payment processors (if applicable) - billing",
    "CDN providers (Cloudflare) - content delivery"
  ],
  "export_format": "JSON",
  "controller": "LUKHAS AI Platform",
  "data_protection_officer": "dpo@lukhas.com"
}
```

## Examples

### Request Your Own Data

```bash
curl -X GET "https://api.lukhas.ai/api/v1/data-rights/users/me/data" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Request Specific User Data (Admin)

```bash
curl -X GET "https://api.lukhas.ai/api/v1/data-rights/users/user123/data" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Using API Key

```bash
curl -X GET "https://api.lukhas.ai/api/v1/data-rights/users/me/data" \
  -H "x-api-key: luk_prod_your_api_key_here"
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Data retrieved |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Cannot access other user's data |
| 404 | Not Found - User does not exist |
| 500 | Internal Server Error - Data retrieval failed |

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Authentication required. Provide x-api-key header or Authorization Bearer token."
}
```

### 403 Forbidden

```json
{
  "detail": "Can only access own data unless admin"
}
```

### 404 Not Found

```json
{
  "detail": "User user123 not found"
}
```

## GDPR Article 15 Compliance

This API satisfies all GDPR Article 15 requirements:

| Requirement | Implementation |
|-------------|----------------|
| ✅ Confirmation of data processing | Implicit by returning data |
| ✅ Access to personal data | `identity`, `memory`, `consciousness` fields |
| ✅ Processing purposes | `processing_purposes` field |
| ✅ Categories of data | Structured fields for each category |
| ✅ Recipients of data | `third_parties` field |
| ✅ Retention period | `retention_periods` field |
| ✅ Information about rights | (See related endpoints) |
| ✅ Right to lodge complaint | Contact DPO at `dpo@lukhas.com` |
| ✅ Source of data | Identity service, user input |
| ✅ Automated decision-making | Consciousness and reasoning traces |

## Privacy & Security

### Audit Logging

All data access requests are logged for audit purposes with:
- User ID making the request
- Target user ID
- Timestamp
- IP address
- Success/failure status

### Data Minimization

Only data necessary for the user is returned. System-internal IDs and technical metadata are excluded.

### Access Control

Strict authorization ensures:
- Users can only access their own data
- Admin access is logged and monitored
- Failed access attempts are logged

## Rate Limiting

- **User accounts**: 10 requests per hour
- **Admin accounts**: 100 requests per hour

Exceeding rate limits returns `429 Too Many Requests`.

## Data Export

The data is returned in **JSON format** which is:
- Machine-readable
- Human-readable
- Portable
- Standardized

Future versions may support additional formats:
- CSV (for tabular data)
- PDF (for human-readable reports)
- XML (for legacy systems)

## Integration

### For Frontend Applications

```javascript
// Fetch user data
const response = await fetch('https://api.lukhas.ai/api/v1/data-rights/users/me/data', {
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});

const userData = await response.json();
console.log('User data:', userData);
```

### For Backend Services

```python
import requests

def get_user_data(user_id: str, api_key: str):
    """Retrieve user data via GDPR API."""
    response = requests.get(
        f"https://api.lukhas.ai/api/v1/data-rights/users/{user_id}/data",
        headers={"x-api-key": api_key}
    )
    response.raise_for_status()
    return response.json()
```

## Development & Testing

### Local Development

```bash
# Start the API server
uvicorn interfaces.api.v1.rest.app:app --reload --port 8000

# Test the endpoint
curl -X GET "http://localhost:8000/api/v1/data-rights/users/me/data" \
  -H "Authorization: Bearer test_token"
```

### Running Tests

```bash
# Run all data rights tests
pytest tests/unit/core/interfaces/api/v1/v1/test_data_rights.py -v

# Run specific test
pytest tests/unit/core/interfaces/api/v1/v1/test_data_rights.py::TestGDPRCompliance -v

# Run with coverage
pytest tests/unit/core/interfaces/api/v1/v1/test_data_rights.py --cov=interfaces.api.v1.rest.routers.data_rights
```

### OpenAPI Documentation

Interactive API documentation is auto-generated and available at:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Next Steps

This API is part of a comprehensive GDPR compliance implementation:

1. ✅ **Issue #1588**: Right to Access (Article 15) - **THIS IMPLEMENTATION**
2. **Issue #1589**: Right to Rectification (Article 16) - Planned
3. **Issue #1590**: Right to Erasure (Article 17) - Planned
4. **Issue #1591**: Right to Data Portability (Article 20) - Planned
5. **Issue #1592**: Right to Object (Article 21) - Planned

## Support & Contact

### Data Protection Officer

**Email**: dpo@lukhas.com
**Response Time**: Within 30 days (as required by GDPR)

### Technical Support

For API integration questions:
- **Documentation**: https://docs.lukhas.ai
- **API Status**: https://status.lukhas.ai
- **Support**: support@lukhas.com

## Legal Disclaimer

This API is designed to comply with GDPR Article 15. However, legal compliance is an ongoing process that requires:
- Keeping data sources synchronized
- Regular audits
- User consent management
- Data retention enforcement
- Security updates

Consult with legal counsel to ensure full compliance with applicable data protection laws.

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
**Status**: Production
**Issue**: #1588
