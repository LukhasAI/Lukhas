# LUKHAS ΛiD API Reference

**Version:** 2.0.0  
**Base URL:** `https://api.lukhas.ai/v2/lambda-id`  
**Last Updated:** July 5, 2025

---

## Authentication

All API endpoints require authentication. Choose one of the following methods:

### API Key Authentication
```http
X-API-Key: your_api_key_here
```

### Bearer Token Authentication
```http
Authorization: Bearer your_jwt_token_here
```

### User Context
Many endpoints require user context information:
```json
{
  "user_context": {
    "user_id": "user123",
    "tier": 2,
    "geo_location": {"lat": 37.7749, "lng": -122.4194},
    "commercial_account": false,
    "brand_prefix": null
  }
}
```

---

## Rate Limiting

Rate limits are applied per API key/user based on tier:

| Tier | Requests/Hour | Burst Limit |
|------|---------------|-------------|
| 0-1  | 100           | 10          |
| 2-3  | 500           | 25          |
| 4-5  | 2000          | 100         |
| Commercial | Custom | Custom |

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 487
X-RateLimit-Reset: 1625097600
```

---

## Core Endpoints

### Generate ΛiD

Generate a new ΛiD for a user.

#### Request
```http
POST /generate
Content-Type: application/json

{
  "user_context": {
    "user_id": "user123",
    "tier": 2,
    "geo_location": {"lat": 37.7749, "lng": -122.4194}
  },
  "options": {
    "symbolic_preference": "🔮",
    "entropy_target": 2.5,
    "validation_level": "full",
    "enable_portability": true
  }
}
```

#### Response
```json
{
  "success": true,
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "generation_time": "2025-07-05T10:30:00Z",
  "entropy_score": 2.8,
  "tier": 2,
  "validation_result": {
    "valid": true,
    "checks_passed": ["format", "tier", "collision", "entropy"],
    "warnings": [],
    "recommendations": []
  },
  "portability_package": {
    "qr_geo_code": "data:image/png;base64,iVBOR...",
    "emergency_codes": ["A1B2-C3D4-E5F6", "G7H8-I9J0-K1L2"],
    "recovery_phrase": "abandon ability able about above absent absorb..."
  },
  "metadata": {
    "generation_duration_ms": 45,
    "validation_duration_ms": 12,
    "collision_checks": 3
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate ΛiD",
    "details": {
      "reason": "Tier limit exceeded",
      "current_count": 5,
      "max_allowed": 5,
      "reset_time": "2025-07-05T11:30:00Z"
    }
  },
  "timestamp": "2025-07-05T10:30:00Z",
  "request_id": "req_123456789"
}
```

---

### Validate ΛiD

Validate an existing ΛiD with specified validation level.

#### Request
```http
POST /validate
Content-Type: application/json

{
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "validation_level": "full",
  "context": {
    "geo_code": "USA",
    "commercial_account": false,
    "check_expiry": true
  }
}
```

#### Response
```json
{
  "success": true,
  "validation_result": {
    "valid": true,
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "tier": 2,
    "validation_level": "full",
    "checks": {
      "format_valid": true,
      "tier_compliant": true,
      "collision_free": true,
      "entropy_valid": true,
      "commercial_valid": true,
      "geo_code_valid": true,
      "emoji_combo_valid": true
    },
    "errors": [],
    "warnings": [
      "Entropy below recommended threshold for tier 2"
    ],
    "recommendations": [
      "Consider using higher-entropy symbolic characters"
    ],
    "metadata": {
      "entropy_score": 1.8,
      "entropy_requirements": {
        "minimum": 1.2,
        "recommended": 1.8
      },
      "collision_checks": 2,
      "validation_duration_ms": 8
    }
  }
}
```

---

### Batch Operations

#### Batch Generate
```http
POST /batch/generate
Content-Type: application/json

{
  "user_contexts": [
    {
      "user_id": "user123",
      "tier": 2
    },
    {
      "user_id": "user124", 
      "tier": 3
    }
  ],
  "count": 10,
  "options": {
    "validation_level": "standard"
  }
}
```

#### Batch Validate
```http
POST /batch/validate
Content-Type: application/json

{
  "lambda_ids": [
    "Λ2-A1B2-🔮-C3D4",
    "Λ3-E5F6-⟐-G7H8",
    "Λ1-I9J0-○-K1L2"
  ],
  "validation_level": "full"
}
```

---

### ΛiD Information

Get detailed information about a ΛiD.

#### Request
```http
GET /info/Λ2-A1B2-🔮-C3D4
```

#### Response
```json
{
  "success": true,
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "info": {
    "tier": 2,
    "created_at": "2025-07-05T10:30:00Z",
    "is_active": true,
    "owner": {
      "user_id": "user123",
      "tier": 2
    },
    "components": {
      "tier_component": "2",
      "timestamp_hash": "A1B2",
      "symbolic_character": "🔮",
      "entropy_hash": "C3D4"
    },
    "entropy_analysis": {
      "overall_score": 2.8,
      "base_entropy": 2.1,
      "boost_factors": {
        "unicode_symbolic": 1.3,
        "pattern_complexity": 1.1
      },
      "entropy_level": "high"
    },
    "validation_status": {
      "last_validated": "2025-07-05T10:30:00Z",
      "validation_level": "full",
      "valid": true
    },
    "portability": {
      "recovery_methods_available": ["qr_geo", "emergency_code", "recovery_phrase"],
      "cross_device_sync_enabled": true,
      "backup_available": true
    }
  }
}
```

---

## Tier Management

### Get Tier Information

#### Request
```http
GET /tiers/2
```

#### Response
```json
{
  "success": true,
  "tier": {
    "number": 2,
    "name": "Family",
    "description": "Enhanced access with emoji support and recovery features",
    "permissions": {
      "max_lambda_ids": 50,
      "generation_cooldown": 300,
      "symbolic_chars": ["🌀", "✨", "🔮", "◊", "⟐"],
      "features": {
        "emoji_support": true,
        "geo_encoding": true,
        "cross_device_sync": true,
        "commercial_branding": false,
        "bulk_operations": false
      }
    },
    "rate_limits": {
      "requests_per_hour": 500,
      "burst_limit": 25
    },
    "entropy_thresholds": {
      "minimum": 1.2,
      "recommended": 1.8
    },
    "upgrade_options": {
      "next_tier": 3,
      "upgrade_cost": "$19.99",
      "upgrade_benefits": ["Advanced entropy features", "Commercial branding"]
    }
  }
}
```

### Upgrade ΛiD Tier

#### Request
```http
POST /upgrade
Content-Type: application/json

{
  "lambda_id": "Λ1-A1B2-○-C3D4",
  "target_tier": 2,
  "payment_proof": {
    "transaction_id": "txn_123456789",
    "amount": 19.99,
    "currency": "USD",
    "payment_method": "stripe"
  },
  "user_context": {
    "user_id": "user123",
    "current_tier": 1
  }
}
```

#### Response
```json
{
  "success": true,
  "upgrade_result": {
    "old_lambda_id": "Λ1-A1B2-○-C3D4",
    "new_lambda_id": "Λ2-A1B2-🔮-C3D4",
    "tier_upgraded": {
      "from": 1,
      "to": 2
    },
    "upgrade_time": "2025-07-05T10:30:00Z",
    "new_features_unlocked": [
      "Emoji symbolic characters",
      "QR-G recovery",
      "Cross-device sync"
    ],
    "portability_package_updated": true
  }
}
```

---

## Entropy Analysis

### Analyze ΛiD Entropy

#### Request
```http
POST /entropy/analyze
Content-Type: application/json

{
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "tier": 2
}
```

#### Response
```json
{
  "success": true,
  "entropy_analysis": {
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "overall_score": 2.8,
    "base_entropy": 2.1,
    "boost_factors": {
      "unicode_symbolic": 1.3,
      "pattern_complexity": 1.1,
      "character_diversity": 1.05
    },
    "entropy_level": "high",
    "component_scores": {
      "shannon_entropy": 2.1,
      "timestamp_entropy": 1.9,
      "symbolic_strength": 2.5,
      "entropy_hash_quality": 2.0,
      "pattern_complexity": 0.7
    },
    "strengths": [
      "High base entropy",
      "Unicode symbolic character boost",
      "Good pattern complexity"
    ],
    "weaknesses": [],
    "recommendations": [
      "Entropy score exceeds recommended threshold",
      "Strong symbolic character choice"
    ],
    "tier_compliance": {
      "tier": 2,
      "meets_minimum": true,
      "meets_recommended": true,
      "minimum_threshold": 1.2,
      "recommended_threshold": 1.8,
      "score_gap": 0,
      "recommendation_gap": 0
    }
  }
}
```

### Live Entropy Scoring (Tier 4+ Only)

#### Request
```http
POST /entropy/live
Content-Type: application/json

{
  "partial_id": "Λ4-A1B2",
  "tier": 4,
  "user_context": {
    "user_id": "user123",
    "tier": 4
  }
}
```

#### Response
```json
{
  "success": true,
  "live_entropy": {
    "current_entropy": 2.1,
    "target_entropy": 2.5,
    "progress_percentage": 84,
    "entropy_level": "medium",
    "suggestions": [
      "Consider using more diverse characters",
      "Add Unicode symbolic characters for boost"
    ],
    "next_character_boost": {
      "high_entropy_chars": ["⟐", "◈", "⬟", "⬢"],
      "medium_entropy_chars": ["🌀", "✨", "🔮"],
      "avoid_chars": ["A", "1", "B", "2"],
      "boost_potential": 0.5
    },
    "optimization_tips": [
      "Unicode symbols provide 1.3x entropy boost",
      "Avoid repeating character patterns",
      "Mix different character types for diversity"
    ]
  }
}
```

---

## Recovery & Portability

### Generate QR-G Recovery Code

#### Request
```http
POST /recovery/qr-geo
Content-Type: application/json

{
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "geo_location": {
    "lat": 37.7749,
    "lng": -122.4194,
    "accuracy": 10
  },
  "security_level": "high",
  "expiry_days": 365
}
```

#### Response
```json
{
  "success": true,
  "qr_recovery": {
    "qr_code_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "qr_code_url": "https://api.lukhas.ai/qr/recovery/abc123",
    "geo_payload": "GEO:eyJsYW1iZGFfaWQiOiLOm...",
    "location": {
      "lat": 37.7749,
      "lng": -122.4194
    },
    "security_level": "high",
    "expiry": "2026-07-05T10:30:00Z",
    "recovery_instructions": [
      "Scan QR code with LUKHAS app",
      "Verify your current location matches the original",
      "Complete additional verification if prompted",
      "Your ΛiD will be restored automatically"
    ]
  }
}
```

### Recover from QR-G Code

#### Request
```http
POST /recovery/qr-geo/restore
Content-Type: application/json

{
  "qr_payload": "GEO:eyJsYW1iZGFfaWQiOiLOm...",
  "current_location": {
    "lat": 37.7750,
    "lng": -122.4195
  },
  "device_info": {
    "device_id": "device123",
    "platform": "ios",
    "app_version": "2.0.0"
  }
}
```

#### Response
```json
{
  "success": true,
  "recovery_attempt": {
    "attempt_id": "rec_20250705_103000_abc123",
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "method": "qr_geo",
    "status": "success",
    "timestamp": "2025-07-05T10:30:00Z",
    "geo_location": {
      "lat": 37.7750,
      "lng": -122.4195
    },
    "success_factors": [
      "QR payload decoded successfully",
      "ΛiD found in recovery database",
      "Geographic verification passed",
      "Package not expired"
    ],
    "security_checks": {
      "proximity": {
        "valid": true,
        "distance_km": 0.05,
        "max_allowed_km": 50
      }
    }
  }
}
```

### Generate Emergency Recovery Codes

#### Request
```http
POST /recovery/emergency-codes
Content-Type: application/json

{
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "count": 10,
  "security_level": "standard"
}
```

#### Response
```json
{
  "success": true,
  "emergency_codes": {
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "codes": [
      "A1B2-C3D4-E5F6",
      "G7H8-I9J0-K1L2",
      "M3N4-O5P6-Q7R8",
      "S9T0-U1V2-W3X4",
      "Y5Z6-A7B8-C9D0"
    ],
    "security_level": "standard",
    "usage_instructions": [
      "Each code can only be used once",
      "Store codes in a secure location",
      "Codes expire after 1 year",
      "Additional verification may be required"
    ],
    "expiry": "2026-07-05T10:30:00Z"
  }
}
```

### Cross-Device Sync

#### Request
```http
POST /sync/devices
Content-Type: application/json

{
  "lambda_id": "Λ2-A1B2-🔮-C3D4",
  "source_device": "device123",
  "target_devices": ["device456", "device789"],
  "sync_options": {
    "include_recovery_data": true,
    "include_analytics": false,
    "encryption_level": "high"
  }
}
```

#### Response
```json
{
  "success": true,
  "sync_result": {
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "source_device": "device123",
    "target_devices": ["device456", "device789"],
    "sync_timestamp": "2025-07-05T10:30:00Z",
    "successful_syncs": ["device456", "device789"],
    "failed_syncs": [],
    "sync_package_id": "sync_abc123",
    "encryption_used": "AES-256-GCM",
    "data_synced": {
      "portability_package": true,
      "recovery_methods": true,
      "user_preferences": true,
      "analytics_data": false
    }
  }
}
```

---

## Commercial Features

### Get Commercial Tier Info

#### Request
```http
GET /commercial/tiers
```

#### Response
```json
{
  "success": true,
  "commercial_tiers": {
    "business": {
      "name": "Business",
      "base_tier": 3,
      "monthly_cost": 99.99,
      "features": {
        "branded_prefixes": true,
        "bulk_generation": true,
        "custom_symbolic_chars": true,
        "management_dashboard": true,
        "api_rate_limit": 5000,
        "priority_support": true,
        "sla_guarantee": "99.9%"
      },
      "limits": {
        "max_lambda_ids": 1000,
        "max_brand_prefixes": 5,
        "max_users": 50
      }
    },
    "enterprise": {
      "name": "Enterprise",
      "base_tier": 4,
      "monthly_cost": 499.99,
      "features": {
        "branded_prefixes": true,
        "bulk_generation": true,
        "custom_symbolic_chars": true,
        "management_dashboard": true,
        "white_label_api": true,
        "dedicated_support": true,
        "custom_integrations": true,
        "sla_guarantee": "99.99%"
      },
      "limits": {
        "max_lambda_ids": 10000,
        "max_brand_prefixes": 20,
        "max_users": 500
      }
    }
  }
}
```

### Register Brand Prefix

#### Request
```http
POST /commercial/brand-prefix
Content-Type: application/json

{
  "brand_code": "MSFT",
  "company_name": "Microsoft Corporation",
  "contact_email": "admin@microsoft.com",
  "commercial_tier": "enterprise",
  "verification_documents": {
    "trademark_certificate": "cert_url_here",
    "business_license": "license_url_here"
  }
}
```

#### Response
```json
{
  "success": true,
  "brand_registration": {
    "brand_code": "MSFT",
    "status": "pending_verification",
    "registration_id": "brand_reg_123456",
    "estimated_approval_time": "3-5 business days",
    "verification_requirements": [
      "Trademark verification",
      "Business license validation",
      "Contact verification"
    ],
    "next_steps": [
      "Await verification email",
      "Complete identity verification",
      "Setup billing information"
    ]
  }
}
```

---

## Analytics & Monitoring

### Get Usage Analytics

#### Request
```http
GET /analytics/usage?period=30d&user_id=user123
```

#### Response
```json
{
  "success": true,
  "analytics": {
    "period": "30d",
    "user_id": "user123",
    "summary": {
      "total_generations": 45,
      "total_validations": 234,
      "total_recovery_attempts": 2,
      "success_rate": 98.5
    },
    "generation_stats": {
      "by_tier": {
        "1": 5,
        "2": 35,
        "3": 5
      },
      "by_day": [
        {"date": "2025-06-05", "count": 2},
        {"date": "2025-06-06", "count": 3}
      ],
      "entropy_distribution": {
        "very_low": 0,
        "low": 2,
        "medium": 15,
        "high": 23,
        "very_high": 5
      }
    },
    "validation_stats": {
      "by_level": {
        "basic": 50,
        "standard": 120,
        "full": 60,
        "enterprise": 4
      },
      "success_rate": 96.2,
      "common_errors": [
        {"error": "collision_detected", "count": 3},
        {"error": "entropy_too_low", "count": 6}
      ]
    },
    "recovery_stats": {
      "methods_used": {
        "qr_geo": 1,
        "emergency_code": 1
      },
      "success_rate": 100
    }
  }
}
```

### System Health Check

#### Request
```http
GET /system/health
```

#### Response
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "timestamp": "2025-07-05T10:30:00Z",
    "version": "2.0.0",
    "uptime": "72h 34m 12s",
    "services": {
      "api": {
        "status": "healthy",
        "response_time_ms": 45
      },
      "database": {
        "status": "healthy",
        "connection_pool": "8/20 active"
      },
      "redis": {
        "status": "healthy",
        "memory_usage": "256MB/1GB"
      },
      "validation_engine": {
        "status": "healthy",
        "cache_hit_rate": 94.2
      },
      "entropy_engine": {
        "status": "healthy",
        "analysis_queue": 3
      }
    },
    "metrics": {
      "requests_per_minute": 150,
      "average_response_time": 67,
      "error_rate": 0.5,
      "cache_hit_rate": 89.3
    }
  }
}
```

---

## Error Codes

### Standard Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "specific_field_with_error",
      "value": "invalid_value",
      "expected": "expected_format"
    }
  },
  "timestamp": "2025-07-05T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Error Code Reference

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_FAILED` | 400 | ΛiD validation failed |
| `INVALID_FORMAT` | 400 | Invalid ΛiD format |
| `COLLISION_DETECTED` | 409 | ΛiD collision detected |
| `TIER_INSUFFICIENT` | 403 | Insufficient tier permissions |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `GENERATION_FAILED` | 400 | ΛiD generation failed |
| `ENTROPY_TOO_LOW` | 400 | Entropy below minimum threshold |
| `RECOVERY_FAILED` | 400 | Recovery attempt failed |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid authentication |
| `RESOURCE_NOT_FOUND` | 404 | ΛiD or resource not found |
| `COMMERCIAL_FEATURE_REQUIRED` | 402 | Commercial tier required |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## SDKs and Libraries

### Official SDKs

- **Python**: `pip install lukhas-lambda-id`
- **JavaScript/Node.js**: `npm install @lukhas/lambda-id`
- **iOS Swift**: Available via CocoaPods
- **Android Kotlin**: Available via Maven Central
- **React Native**: `npm install @lukhas/lambda-id-react-native`

### SDK Usage Example (Python)

```python
from lukhas_lambda_id import LambdaIDClient

client = LambdaIDClient(api_key="your_api_key")

# Generate ΛiD
result = client.generate_lambda_id(
    user_id="user123",
    tier=2,
    geo_location={"lat": 37.7749, "lng": -122.4194}
)

if result.success:
    print(f"Generated ΛiD: {result.lambda_id}")
    print(f"Entropy Score: {result.entropy_score}")
else:
    print(f"Error: {result.error}")
```

---

## Webhook Events

Subscribe to webhook events for real-time notifications:

### Available Events

- `lambda_id.generated`
- `lambda_id.validated`
- `lambda_id.upgraded`
- `recovery.attempted`
- `recovery.successful`
- `tier.upgraded`
- `commercial.brand_approved`

### Webhook Payload Example

```json
{
  "event": "lambda_id.generated",
  "timestamp": "2025-07-05T10:30:00Z",
  "data": {
    "lambda_id": "Λ2-A1B2-🔮-C3D4",
    "user_id": "user123",
    "tier": 2,
    "entropy_score": 2.8,
    "generation_time": "2025-07-05T10:30:00Z"
  },
  "metadata": {
    "webhook_id": "wh_123456789",
    "delivery_attempt": 1
  }
}
```

---

**© 2025 LUKHAS AI Systems. All rights reserved.**
