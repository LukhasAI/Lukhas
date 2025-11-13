---
title: "Privacy-First Analytics Implementation Guide"
domain: lukhas.ai
owner: @privacy-team
audience: [developers, compliance-officers, privacy-advocates]
tone:
  poetic: 0.0
  user_friendly: 0.50
  academic: 0.50
canonical: https://lukhas.ai/analytics/privacy-implementation
source: branding
last_reviewed: "2025-11-08"
evidence_links: []
claims_approval: true
claims_verified_by: ["@privacy-team"]
seo:
  description: "Complete guide to LUKHAS privacy-first analytics implementation with GDPR compliance, consent management, and zero PII collection"
  keywords: ["privacy-first analytics", "GDPR compliance", "consent management", "PII redaction", "privacy by design"]
  og_image: /assets/og-images/privacy-analytics.png
---

# Privacy-First Analytics Implementation Guide

## Overview

This document describes the privacy-first analytics implementation for LUKHAS, designed with **privacy by design** principles and full GDPR compliance.

### Key Principles

1. **Zero PII Collection**: No personal data collected by design
2. **Consent First**: No tracking without explicit consent
3. **Local First**: User preferences stored locally (no cookies)
4. **Aggregation Only**: Server stores aggregated metrics, not raw events
5. **User Control**: Easy opt-out and data deletion

## Architecture

```
┌─────────────┐
│   Browser   │
│             │
│ ┌─────────┐ │
│ │ Consent │ │ ← User grants/denies consent
│ │ Banner  │ │
│ └─────────┘ │
│      ↓      │
│ ┌─────────┐ │
│ │Privacy  │ │ ← Checks consent, redacts PII
│ │ Client  │ │
│ └─────────┘ │
│      ↓      │
│ ┌─────────┐ │
│ │  Batch  │ │ ← Collects events locally
│ │  Queue  │ │
│ └─────────┘ │
└──────┬──────┘
       │
       ↓
┌──────────────┐
│   Server     │
│              │
│ ┌──────────┐ │
│ │Rate      │ │ ← Limits requests
│ │Limiter   │ │
│ └──────────┘ │
│      ↓       │
│ ┌──────────┐ │
│ │Aggregator│ │ ← Aggregates without storing raw events
│ └──────────┘ │
│      ↓       │
│ ┌──────────┐ │
│ │Metrics   │ │ ← Stores only aggregated data
│ │ Store    │ │
│ └──────────┘ │
└──────────────┘
```

## Consent Management

### How It Works

1. **Banner Display**: When user first visits, consent banner is shown
2. **User Choice**: User can accept all, reject all, or customize
3. **Storage**: Preference stored in `localStorage` (not cookies)
4. **Enforcement**: Analytics client checks consent before tracking

### Consent Categories

| Category | Default | Description | Can Disable? |
|----------|---------|-------------|--------------|
| Analytics | Denied | Usage tracking | ✅ Yes |
| Marketing | Denied | Marketing content | ✅ Yes |
| Functional | Granted | Essential features | ❌ No |

### Implementation

```typescript
// Check if user has granted analytics consent
import { useConsentManager } from './components/ConsentBanner';

const { hasAnalyticsConsent } = useConsentManager();

if (hasAnalyticsConsent) {
  // Track event
  analytics.track('page_view', { domain: 'lukhas.ai' });
}
```

### Legal Basis

- **GDPR Article 6(1)(a)**: Consent
- **Consent Requirements**:
  - ✅ Freely given (can reject without consequences)
  - ✅ Specific (granular categories)
  - ✅ Informed (clear explanation)
  - ✅ Unambiguous (explicit action required)
  - ✅ Withdrawable (opt-out anytime)

## PII Redaction

### What is PII?

Personally Identifiable Information (PII) is any data that can identify an individual:

- ❌ Email addresses
- ❌ Phone numbers
- ❌ IP addresses (stored)
- ❌ User IDs
- ❌ Names
- ❌ Addresses
- ❌ Credit card numbers
- ❌ Social security numbers

### Automatic Detection

The analytics client automatically detects and redacts PII using pattern matching:

```python
from lukhas.analytics import PrivacyAnalyticsClient

client = PrivacyAnalyticsClient(endpoint="https://analytics.lukhas.ai/events")

# This event contains PII
client.track("page_view", {
    "domain": "lukhas.ai",
    "path": "/matriz",
    "referrer": "user@example.com"  # PII!
})

# PII is automatically redacted:
# {"referrer": "[EMAIL_REDACTED]"}
```

### Detection Patterns

| PII Type | Pattern | Redacted Value |
|----------|---------|----------------|
| Email | `user@example.com` | `[EMAIL_REDACTED]` |
| Phone | `+1-555-0100` | `[PHONE_REDACTED]` |
| IP | `192.168.1.1` | `[IP_REDACTED]` |
| Credit Card | `4111-1111-1111-1111` | `[CC_REDACTED]` |
| SSN | `123-45-6789` | `[SSN_REDACTED]` |

### IP Anonymization

IP addresses are **anonymized** (not redacted) for geolocation:

- **IPv4**: Last octet removed → `192.168.1.0`
- **IPv6**: Last 64 bits removed → `2001:db8:85a3:8d3::0`

This allows country/region analytics while preventing user identification.

### User-Agent Normalization

Full User-Agent strings are **not stored**. Only browser family:

- `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...` → `chrome`
- `Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)...` → `safari`

## Data Retention

### Storage Duration

| Data Type | Retention Period | Reason |
|-----------|-----------------|--------|
| Raw Events | **Not stored** | Privacy by design |
| Aggregated Metrics | 90 days | Business analytics |
| Session Data | 24 hours | Rate limiting |
| Consent Records | 7 years | Legal requirement |

### Automatic Cleanup

The server automatically deletes old data:

```python
# Runs every hour
aggregator.cleanup_old_data(hours=24)
```

### Manual Deletion

Users can request data deletion (GDPR right to erasure):

```bash
# API endpoint
DELETE /data?session_id=abc123

# Response
{
  "status": "deleted",
  "message": "User data deleted (aggregated metrics unaffected)"
}
```

## User Rights (GDPR)

### Right to Access

Users can export their analytics data:

```python
client = PrivacyAnalyticsClient(...)

data = client.export_data()
# Returns all events queued for sending
```

### Right to Deletion

Users can clear all local data:

```python
client.clear_data()
# Removes all pending events
```

### Right to Portability

Data exported in JSON format (machine-readable):

```json
{
  "events": [
    {
      "event": "page_view",
      "properties": {"domain": "lukhas.ai", "path": "/matriz"},
      "timestamp": "2025-11-08T12:00:00Z"
    }
  ],
  "consent": {
    "analytics": "granted",
    "marketing": "denied",
    "functional": "granted"
  },
  "exported_at": "2025-11-08T12:05:00Z"
}
```

### Right to Objection

Users can opt-out anytime:

1. Click "Privacy Settings" in footer
2. Toggle analytics off
3. Consent withdrawn immediately

### Right to Rectification

Not applicable (we don't store personal data to correct).

### Right to Restriction

Users can pause tracking without deleting preferences:

```typescript
const { updateConsent } = useConsentManager();

// Temporarily disable analytics
updateConsent({ analytics: false });

// Re-enable later
updateConsent({ analytics: true });
```

## Rate Limiting

### Purpose

Prevent abuse and ensure fair usage.

### Limits

- **1000 events per hour** per session
- Configurable per event type (see `config.yaml`)

### Enforcement

```python
# Server checks rate limit before accepting events
if not aggregator.check_rate_limit(session_id, ip, limit=1000):
    return {"status": "rejected", "reason": "rate_limit"}
```

### Response

```json
{
  "status": "accepted",
  "events_processed": 10,
  "events_rejected": 2,
  "reason": "rate_limit"
}
```

## Circuit Breaker

### Purpose

Prevent cascading failures when server is down.

### States

1. **Closed**: Normal operation
2. **Open**: Too many failures, reject requests
3. **Half-Open**: Testing if server recovered

### Configuration

```yaml
circuit_breaker:
  failure_threshold: 5      # Open after 5 failures
  timeout_seconds: 60       # Stay open for 60s
  half_open_timeout: 30     # Test recovery after 30s
```

### Behavior

```
Closed → (5 failures) → Open → (60s) → Half-Open → (1 success) → Closed
                                      ↓
                                (1 failure) → Open
```

## Privacy Validation

### Tools

1. **PII Detection**: `tools/validate_analytics_privacy.py`
2. **Consent Flow Testing**: `tools/test_consent_flows.py`

### CI/CD Integration

Every PR checks for PII leakage:

```yaml
# .github/workflows/content-lint.yml
- name: Validate Analytics Privacy
  run: |
    make analytics-privacy-check
```

### Sample Validation

```bash
# Check sample events for PII
python3 tools/validate_analytics_privacy.py --events sample_events.json

# Output
✅ No PII detected in 1000 events
✅ All events have valid consent
✅ All properties within length limits
```

## Testing Consent Flows

### Manual Testing

1. Open website in incognito mode
2. Verify consent banner appears
3. Test each flow:
   - Accept all → verify tracking works
   - Reject all → verify no tracking
   - Customize → verify granular control
4. Check `localStorage`:
   ```javascript
   localStorage.getItem('lukhas_analytics_consent')
   ```

### Automated Testing

```bash
python3 tools/test_consent_flows.py

# Output
✅ Consent banner shows on first visit
✅ Accept all enables tracking
✅ Reject all disables tracking
✅ Customize saves granular preferences
✅ Opt-out works correctly
```

## GDPR Compliance Checklist

### Data Minimization

- ✅ Only collect necessary data
- ✅ No PII in event properties
- ✅ Anonymize IP addresses
- ✅ Normalize User-Agents

### Purpose Limitation

- ✅ Data used only for stated purposes (analytics)
- ✅ Not shared with third parties
- ✅ Not used for profiling

### Storage Limitation

- ✅ Raw events not stored
- ✅ Aggregated data retained 90 days
- ✅ Automatic cleanup implemented

### Lawfulness of Processing

- ✅ Legal basis: Consent (GDPR Art. 6(1)(a))
- ✅ Consent freely given
- ✅ Consent specific and informed
- ✅ Consent easily withdrawable

### Transparency

- ✅ Clear privacy policy
- ✅ Consent banner with explanation
- ✅ Privacy information endpoint (`/privacy`)

### Data Subject Rights

- ✅ Right to access (export data)
- ✅ Right to deletion (clear data)
- ✅ Right to portability (JSON export)
- ✅ Right to objection (opt-out)
- ✅ Right to restriction (pause tracking)

### Security

- ✅ HTTPS only
- ✅ No third-party scripts
- ✅ No cookies (localStorage)
- ✅ Rate limiting
- ✅ Circuit breaker

### Accountability

- ✅ Privacy policy documented
- ✅ Data Processing Agreement (if needed)
- ✅ Privacy impact assessment
- ✅ Audit trail (consent timestamps)

## Privacy by Design Principles

### 1. Proactive not Reactive

- **Before**: Third-party analytics with cookies
- **After**: Self-hosted, cookie-free, consent-first

### 2. Privacy as Default

- **Before**: Opt-out model (tracking by default)
- **After**: Opt-in model (no tracking without consent)

### 3. Privacy Embedded

- **Before**: Privacy added after implementation
- **After**: Privacy built into architecture

### 4. Full Functionality

- **Before**: "Privacy vs. Analytics" trade-off
- **After**: Privacy AND analytics (aggregation)

### 5. End-to-End Security

- **Before**: Data stored indefinitely
- **After**: Automatic deletion, no raw events

### 6. Visibility and Transparency

- **Before**: Hidden tracking
- **After**: Clear consent banner, privacy policy

### 7. Respect for User Privacy

- **Before**: Tracking without consent
- **After**: User control, easy opt-out

## Troubleshooting

### Events not tracked

**Symptom**: `track()` returns `False`

**Causes**:
1. ❌ No analytics consent
2. ❌ DNT header enabled
3. ❌ Event name not in taxonomy

**Solutions**:
```python
# Check consent
if not client.has_analytics_consent():
    print("User has not granted consent")

# Check DNT
if client.check_dnt():
    print("Do Not Track is enabled")

# Validate event name
if event_name not in client._allowed_events:
    print(f"Event '{event_name}' not allowed")
```

### PII detected in events

**Symptom**: Validation tool reports PII

**Cause**: Event properties contain PII

**Solution**:
```python
# PII is automatically redacted
# But you should fix the source

# Bad
track("page_view", {
    "user_email": "user@example.com"  # PII!
})

# Good
track("page_view", {
    "domain": "lukhas.ai",
    "path": "/matriz"
})
```

### Rate limit exceeded

**Symptom**: Server returns `events_rejected > 0`

**Cause**: Too many events from same session

**Solution**:
```python
# Reduce event frequency
# Use debouncing for rapid-fire events

import time

last_track_time = 0

def track_debounced(event, props):
    global last_track_time
    now = time.time()

    if now - last_track_time > 1:  # 1 second debounce
        client.track(event, props)
        last_track_time = now
```

## References

- [GDPR Official Text](https://gdpr-info.eu/)
- [Privacy by Design Framework](https://www.ipc.on.ca/wp-content/uploads/Resources/7foundationalprinciples.pdf)
- [LUKHAS Analytics Integration Guide](./INTEGRATION_GUIDE_V2.md)
- [Event Taxonomy](./event_taxonomy.json)
- [Analytics Configuration](./config.yaml)

## Contact

For privacy questions:
- Email: privacy@lukhas.ai
- Privacy Policy: https://lukhas.ai/privacy
- Data Protection Officer: dpo@lukhas.ai

## Changelog

### 2025-11-08 - Initial Release

- ✅ Privacy-first client implementation
- ✅ GDPR-compliant consent banner
- ✅ Server aggregation endpoint
- ✅ PII detection and redaction
- ✅ Rate limiting and circuit breaker
- ✅ Privacy validation tools
- ✅ CI/CD integration

---

**Last Updated**: 2025-11-08
**Version**: 1.0
**Status**: Production Ready
**Compliance**: GDPR, CCPA
