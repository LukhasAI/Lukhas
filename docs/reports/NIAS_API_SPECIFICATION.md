# NIΛS Dream Commerce API Specification v1.0

## Base URL
```
Production: https://api.nias.ai/v1
Staging: https://staging-api.nias.ai/v1
Sandbox: https://sandbox-api.nias.ai/v1
```

## Authentication
All API requests require authentication using API keys in the header:
```
X-API-Key: {your_api_key}
X-API-Secret: {your_api_secret}
```

## API Endpoints

### 1. User Management

#### Register User
```http
POST /users/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "age": 25,
  "location": "US",
  "preferences": {
    "language": "en",
    "timezone": "America/New_York"
  }
}
```

**Response:**
```json
{
  "user_id": "user_abc123",
  "status": "active",
  "tier": "T0",
  "consent_url": "https://consent.nias.ai/user/user_abc123",
  "created_at": "2024-12-01T10:00:00Z"
}
```

#### Update Consent
```http
POST /users/{user_id}/consent
```

**Request Body:**
```json
{
  "consent_level": "dream_aware",
  "data_sources": [
    "email",
    "shopping_history",
    "calendar"
  ],
  "ai_generation": {
    "narrative": true,
    "image": true,
    "video": false
  },
  "vendor_permissions": {
    "vendor_123": {
      "allowed": true,
      "data_sources": ["shopping_history"]
    }
  }
}
```

### 2. Vendor Management

#### Onboard Vendor
```http
POST /vendors/onboard
```

**Request Body:**
```json
{
  "company_name": "Dream Boutique",
  "domains": ["dreamboutique.com"],
  "categories": ["fashion", "lifestyle"],
  "tier": "basic",
  "contact": {
    "email": "partner@dreamboutique.com",
    "phone": "+1234567890"
  }
}
```

**Response:**
```json
{
  "vendor_id": "vendor_xyz789",
  "api_key": "vk_a1b2c3d4e5f6",
  "api_secret": "secret_key_here",
  "tier": "basic",
  "webhook_url": "https://api.nias.ai/vendor/vendor_xyz789/webhook",
  "sdk_download": "https://sdk.nias.ai/download",
  "max_seeds": 100
}
```

#### Create Dream Seed
```http
POST /vendors/{vendor_id}/seeds
```

**Request Body:**
```json
{
  "type": "seasonal",
  "title": "Winter Dreams Collection",
  "narrative": "As snowflakes dance outside your window, imagine wrapping yourself in clouds of cashmere...",
  "emotional_triggers": {
    "joy": 0.7,
    "calm": 0.8,
    "stress": 0.0,
    "longing": 0.5
  },
  "product_data": {
    "id": "PROD-001",
    "name": "Cloud Cashmere Sweater",
    "price": 189.99,
    "category": "apparel",
    "images": ["https://cdn.example.com/sweater1.jpg"]
  },
  "offer_details": {
    "discount_percentage": 20,
    "promo_code": "WINTER20",
    "valid_until": "2024-02-29T23:59:59Z"
  },
  "targeting_criteria": {
    "interests": ["fashion", "comfort", "luxury"],
    "age_range": {"min": 25, "max": 55},
    "location": ["US", "CA"],
    "season": "winter"
  },
  "affiliate_link": "https://dreamboutique.com/buy/PROD-001",
  "one_click_data": {
    "shipping_included": true,
    "express_checkout": true,
    "payment_methods": ["card", "paypal", "applepay"]
  }
}
```

### 3. Dream Generation

#### Generate Dream
```http
POST /dreams/generate
```

**Request Body:**
```json
{
  "user_id": "user_abc123",
  "vendor_seed_id": "seed_xyz789",
  "mood": "serene",
  "context": {
    "bio_rhythm": "evening_wind",
    "recent_activity": ["browsing_winter_fashion"],
    "upcoming_events": ["holiday_party"]
  },
  "generation_options": {
    "include_image": true,
    "max_narrative_length": 300,
    "style": "poetic"
  }
}
```

**Response:**
```json
{
  "dream_id": "dream_abc123xyz",
  "narrative": "In the gentle glow of winter's embrace, soft cashmere whispers promises of warmth...",
  "image_url": "https://cdn.nias.ai/dreams/dream_abc123xyz.jpg",
  "visual_prompt": "A serene winter scene with soft cashmere textures and warm candlelight",
  "emotional_profile": {
    "joy": 0.6,
    "calm": 0.8,
    "stress": 0.0,
    "longing": 0.4
  },
  "symbolism": ["warmth", "comfort", "transformation"],
  "call_to_action": {
    "type": "seasonal",
    "text": "When winter calls to you...",
    "link": "https://quick.nias.ai/buy/dream_abc123xyz"
  },
  "ethical_score": 0.92,
  "generation_time_ms": 1250
}
```

#### Deliver Dream
```http
POST /dreams/{dream_id}/deliver
```

**Request Body:**
```json
{
  "user_id": "user_abc123",
  "channel": "visual",
  "timing": "immediate",
  "device": "mobile"
}
```

### 4. Interaction Tracking

#### Track Interaction
```http
POST /interactions/track
```

**Request Body:**
```json
{
  "dream_id": "dream_abc123xyz",
  "user_id": "user_abc123",
  "action": "click",
  "timestamp": "2024-12-01T15:30:00Z",
  "metadata": {
    "device": "iphone",
    "location": "home",
    "session_id": "sess_123"
  }
}
```

#### Track Conversion
```http
POST /conversions/track
```

**Request Body:**
```json
{
  "dream_id": "dream_abc123xyz",
  "user_id": "user_abc123",
  "vendor_id": "vendor_xyz789",
  "seed_id": "seed_xyz789",
  "amount": 151.99,
  "currency": "USD",
  "items": [
    {
      "product_id": "PROD-001",
      "quantity": 1,
      "price": 189.99,
      "discount": 38.00
    }
  ],
  "timestamp": "2024-12-01T15:35:00Z"
}
```

### 5. Analytics

#### Get Vendor Analytics
```http
GET /vendors/{vendor_id}/analytics?from=2024-12-01&to=2024-12-31
```

**Response:**
```json
{
  "vendor_id": "vendor_xyz789",
  "period": {
    "from": "2024-12-01",
    "to": "2024-12-31"
  },
  "metrics": {
    "total_impressions": 10000,
    "total_clicks": 500,
    "total_conversions": 50,
    "ctr": 5.0,
    "conversion_rate": 10.0,
    "revenue": {
      "total": 7599.50,
      "vendor_share": 5319.65,
      "nias_commission": 2279.85,
      "currency": "USD"
    }
  },
  "top_seeds": [
    {
      "seed_id": "seed_xyz789",
      "title": "Winter Dreams Collection",
      "conversions": 25,
      "revenue": 3799.75
    }
  ],
  "user_segments": {
    "age_25_35": 45,
    "age_36_45": 30,
    "age_46_55": 25
  }
}
```

#### Get User Journey
```http
GET /users/{user_id}/journey?dream_id={dream_id}
```

**Response:**
```json
{
  "user_id": "user_abc123",
  "dream_id": "dream_abc123xyz",
  "journey": [
    {
      "timestamp": "2024-12-01T15:00:00Z",
      "event": "dream_generated",
      "details": {"mood": "serene", "bio_rhythm": "evening_wind"}
    },
    {
      "timestamp": "2024-12-01T15:05:00Z",
      "event": "dream_delivered",
      "details": {"channel": "visual", "device": "mobile"}
    },
    {
      "timestamp": "2024-12-01T15:30:00Z",
      "event": "interaction",
      "details": {"action": "click"}
    },
    {
      "timestamp": "2024-12-01T15:35:00Z",
      "event": "conversion",
      "details": {"amount": 151.99, "items": 1}
    }
  ],
  "emotional_trajectory": [
    {"time": "15:00", "joy": 0.5, "calm": 0.7},
    {"time": "15:05", "joy": 0.6, "calm": 0.8},
    {"time": "15:30", "joy": 0.7, "calm": 0.7},
    {"time": "15:35", "joy": 0.8, "calm": 0.6}
  ]
}
```

### 6. System Health

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "openai": "healthy",
    "cache": "healthy",
    "queue": "healthy"
  },
  "metrics": {
    "active_sessions": 1250,
    "queue_size": 45,
    "avg_generation_time_ms": 850,
    "uptime_hours": 720
  }
}
```

## Webhooks

### Vendor Webhooks

Vendors can subscribe to the following webhook events:

#### Dream Delivered
```json
{
  "event": "dream.delivered",
  "timestamp": "2024-12-01T15:05:00Z",
  "data": {
    "dream_id": "dream_abc123xyz",
    "seed_id": "seed_xyz789",
    "user_segment": "premium",
    "channel": "visual"
  }
}
```

#### Conversion Completed
```json
{
  "event": "conversion.completed",
  "timestamp": "2024-12-01T15:35:00Z",
  "data": {
    "dream_id": "dream_abc123xyz",
    "seed_id": "seed_xyz789",
    "amount": 151.99,
    "commission": 45.60,
    "vendor_earnings": 106.39
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "INVALID_CONSENT",
    "message": "User has not consented to this data source",
    "details": {
      "required_consent": "shopping_history",
      "current_consent": ["email", "calendar"]
    },
    "request_id": "req_abc123xyz"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid API credentials |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_CONSENT` | 403 | Missing required consent |
| `ETHICAL_VIOLATION` | 422 | Content failed ethical validation |
| `RATE_LIMIT` | 429 | Too many requests |
| `EMOTIONAL_BLOCK` | 422 | User emotional state prevents delivery |
| `QUOTA_EXCEEDED` | 402 | Vendor quota exceeded |
| `INVALID_REQUEST` | 400 | Malformed request |
| `SERVER_ERROR` | 500 | Internal server error |

## Rate Limits

| Tier | Requests/Hour | Burst Limit |
|------|--------------|-------------|
| Trial | 100 | 10 |
| Basic | 1,000 | 50 |
| Professional | 10,000 | 200 |
| Enterprise | 100,000 | 1,000 |
| Strategic | Unlimited | 5,000 |

## SDKs and Libraries

### Official SDKs
- Python: `pip install nias-dream-sdk`
- JavaScript/Node: `npm install @nias/dream-sdk`
- Ruby: `gem install nias-dream-sdk`
- PHP: `composer require nias/dream-sdk`
- Go: `go get github.com/nias-ai/dream-sdk-go`

### Example Usage (Python)
```python
from nias_dream_sdk import NIASDreamClient

client = NIASDreamClient(
    api_key="vk_your_api_key",
    api_secret="your_api_secret"
)

# Create a dream seed
seed = client.create_seed({
    "type": "seasonal",
    "title": "Summer Dreams",
    "narrative": "As sunlight dances on ocean waves...",
    "emotional_triggers": {
        "joy": 0.8,
        "calm": 0.7
    }
})

# Get analytics
analytics = client.get_analytics(
    from_date="2024-12-01",
    to_date="2024-12-31"
)
```

## Changelog

### Version 1.0.0 (December 2024)
- Initial release
- Core dream commerce functionality
- OpenAI integration (GPT-4, DALL-E 3)
- Vendor portal and SDK
- Consent management system
- Analytics and tracking

### Planned Features (v1.1.0)
- Sora video generation
- AR/VR dream experiences
- Voice assistant integration
- Blockchain consent ledger
- Advanced A/B testing

---

*NIΛS Dream Commerce API - Where Dreams Meet Commerce*  
*Documentation Version: 1.0.0*  
*Last Updated: December 2024*