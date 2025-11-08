---
title: "Privacy-First Analytics Integration Guide V2"
domain: lukhas.ai
owner: @web-architect
audience: [developers, frontend-engineers]
tone:
  poetic: 0.0
  user_friendly: 0.60
  academic: 0.40
canonical: https://lukhas.ai/analytics/integration-guide-v2
source: branding
last_reviewed: "2025-11-08"
evidence_links: []
claims_approval: false
claims_verified_by: []
seo:
  description: "Complete integration guide for LUKHAS privacy-first analytics with code examples, consent management, and GDPR compliance"
  keywords: ["LUKHAS analytics", "privacy-first tracking", "custom events", "GDPR compliance"]
  og_image: /assets/og-images/analytics-integration-v2.png
---

# Privacy-First Analytics Integration Guide V2

## Overview

This guide covers the implementation of LUKHAS privacy-first analytics with:

- ✅ **Zero PII collection** by design
- ✅ **Consent-first tracking** (GDPR compliant)
- ✅ **Self-hosted** (no third parties)
- ✅ **Cookie-free** (localStorage only)
- ✅ **Automatic PII redaction**
- ✅ **Aggregation-only** (no raw event storage)

## Quick Start

### 1. Install Dependencies

```bash
# Python backend
pip install fastapi uvicorn pydantic

# Frontend (React/TypeScript)
npm install react
```

### 2. Add Consent Banner

```tsx
// app/layout.tsx
import { ConsentBanner } from '@/components/ConsentBanner';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <ConsentBanner privacyPolicyUrl="/privacy" />
      </body>
    </html>
  );
}
```

### 3. Initialize Analytics Client

```typescript
// lib/analytics.ts
import { PrivacyAnalyticsClient } from '@/lib/privacy-client';

export const analytics = new PrivacyAnalyticsClient({
  endpoint: 'https://analytics.lukhas.ai/events',
  batchSize: 10,
  batchTimeout: 300,
});
```

### 4. Track Events

```typescript
// pages/matriz.tsx
import { analytics } from '@/lib/analytics';
import { useConsent } from '@/components/ConsentBanner';

export default function MatrizPage() {
  const consent = useConsent();

  useEffect(() => {
    // Track page view (only if consent granted)
    if (consent?.analytics) {
      analytics.track('page_view', {
        domain: 'lukhas.ai',
        path: '/matriz',
      });
    }
  }, [consent]);

  return <div>MATRIZ Content</div>;
}
```

## Event Tracking Examples

### Page View

```typescript
analytics.track('page_view', {
  domain: 'lukhas.ai',
  path: '/matriz',
  variant: 'assistive',  // Optional
  referrer: document.referrer,  // Auto-redacted if contains PII
});
```

### Quickstart Started

```typescript
// On quickstart page load
analytics.track('quickstart_started', {
  domain: 'lukhas.dev',
  language: 'python',
  quickstart_id: 'matriz-hello-world',
});
```

### Quickstart Completed

```typescript
// On successful completion
analytics.track('quickstart_completed', {
  domain: 'lukhas.dev',
  language: 'python',
  quickstart_id: 'matriz-hello-world',
  duration_seconds: 120,
  success: true,
});
```

### Reasoning Trace Viewed

```typescript
// On reasoning lab interaction
analytics.track('reasoning_trace_viewed', {
  domain: 'lukhas.ai',
  trace_type: 'symbolic_dna',
  interaction_depth: 3,
});
```

### Assistive Mode Viewed

```typescript
// On assistive mode toggle
analytics.track('assistive_variant_viewed', {
  domain: 'lukhas.ai',
  page: '/matriz',
  trigger: 'toggle',  // 'toggle', 'preference', or 'auto'
});
```

### Assistive Audio Played

```typescript
// On audio playback
analytics.track('assistive_audio_played', {
  domain: 'lukhas.ai',
  page: '/matriz',
  duration_seconds: 45,
});
```

### Evidence Artifact Requested

```typescript
// On evidence link click
analytics.track('evidence_artifact_requested', {
  domain: 'lukhas.ai',
  claim_page: '/performance',
  evidence_id: 'matriz-p95-latency-2025-q3',
});
```

### Demo Interaction

```typescript
// On demo start
analytics.track('demo_interaction', {
  domain: 'lukhas.ai',
  demo_type: 'matriz_reasoning',
  action: 'start',  // 'start', 'step', or 'complete'
});
```

### CTA Clicked

```typescript
// On CTA click
analytics.track('cta_clicked', {
  domain: 'lukhas.ai',
  cta_text: 'Try MATRIZ Now',
  cta_location: 'homepage_hero',
});
```

## Complete Integration Examples

### React Component with Consent

```tsx
import React, { useEffect } from 'react';
import { analytics } from '@/lib/analytics';
import { useConsentManager } from '@/components/ConsentBanner';

export function QuickstartComponent({ language, id }: Props) {
  const { hasAnalyticsConsent } = useConsentManager();
  const [startTime, setStartTime] = useState<number>(0);

  useEffect(() => {
    if (!hasAnalyticsConsent) return;

    // Track start
    const start = Date.now();
    setStartTime(start);

    analytics.track('quickstart_started', {
      domain: window.location.hostname,
      language,
      quickstart_id: id,
    });
  }, [hasAnalyticsConsent, language, id]);

  const handleComplete = () => {
    if (!hasAnalyticsConsent) return;

    const duration = Math.floor((Date.now() - startTime) / 1000);

    analytics.track('quickstart_completed', {
      domain: window.location.hostname,
      language,
      quickstart_id: id,
      duration_seconds: duration,
      success: true,
    });
  };

  return (
    <div>
      {/* Quickstart content */}
      <button onClick={handleComplete}>Complete</button>
    </div>
  );
}
```

### Next.js App Router Integration

```tsx
// app/providers.tsx
'use client';

import { ConsentBanner } from '@/components/ConsentBanner';
import { analytics } from '@/lib/analytics';
import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function AnalyticsProvider({ children }) {
  const pathname = usePathname();

  useEffect(() => {
    // Track page views on route change
    analytics.track('page_view', {
      domain: window.location.hostname,
      path: pathname,
    });
  }, [pathname]);

  return (
    <>
      {children}
      <ConsentBanner />
    </>
  );
}
```

```tsx
// app/layout.tsx
import { AnalyticsProvider } from './providers';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AnalyticsProvider>{children}</AnalyticsProvider>
      </body>
    </html>
  );
}
```

### Python Backend Integration

```python
# server.py
from lukhas.analytics import PrivacyAnalyticsClient

# Initialize client
analytics = PrivacyAnalyticsClient(
    endpoint="https://analytics.lukhas.ai/events",
    batch_size=10,
    retention_days=30,
)

# Set consent (from user preference)
from lukhas.analytics.privacy_client import ConsentCategory, ConsentMode

analytics.set_consent(ConsentCategory.ANALYTICS, ConsentMode.GRANTED)

# Track event
analytics.track("quickstart_completed", {
    "domain": "lukhas.dev",
    "language": "python",
    "quickstart_id": "matriz-hello-world",
    "duration_seconds": 120,
    "success": True,
})

# Flush pending events
analytics.flush()
```

## Privacy Features

### Automatic PII Redaction

The client **automatically redacts** PII from all event properties:

```typescript
// You send
analytics.track('page_view', {
  domain: 'lukhas.ai',
  path: '/contact',
  referrer: 'https://example.com?email=user@example.com',  // PII!
});

// Server receives
{
  "domain": "lukhas.ai",
  "path": "/contact",
  "referrer": "https://example.com?email=[EMAIL_REDACTED]"
}
```

### Consent Checking

Tracking only happens **with explicit consent**:

```typescript
const { hasAnalyticsConsent } = useConsentManager();

if (hasAnalyticsConsent) {
  analytics.track('page_view', { ... });
} else {
  console.log('Analytics disabled - no consent');
}
```

### User Data Export

Users can export their data (GDPR right to portability):

```python
# Python
data = analytics.export_data()
print(data)  # JSON with all queued events

# TypeScript
const data = analytics.exportData();
console.log(data);
```

### User Data Deletion

Users can delete their data (GDPR right to erasure):

```python
# Python
analytics.clear_data()

# TypeScript
analytics.clearData();
```

## Server Setup

### FastAPI Endpoint

```python
# main.py
from lukhas.api.analytics import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile="/path/to/cert.pem",
        ssl_keyfile="/path/to/key.pem",
    )
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lukhas/ lukhas/

CMD ["uvicorn", "lukhas.api.analytics:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  analytics:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANALYTICS_RETENTION_DAYS=30
      - RATE_LIMIT_PER_HOUR=1000
    restart: unless-stopped
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/analytics
server {
    listen 443 ssl http2;
    server_name analytics.lukhas.ai;

    ssl_certificate /etc/letsencrypt/live/analytics.lukhas.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analytics.lukhas.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Testing

### Consent Flow Testing

```bash
# Run consent flow tests
python3 tools/test_consent_flows.py

# Output
✅ Consent banner shows on first visit
✅ Accept all enables tracking
✅ Reject all disables tracking
✅ Customize saves granular preferences
✅ Opt-out works correctly
```

### PII Validation

```bash
# Validate sample events for PII
python3 tools/validate_analytics_privacy.py --events sample_events.json

# Output
✅ No PII detected in 100 events
✅ All events have valid consent
✅ All properties within length limits
```

### Manual Testing

```typescript
// In browser console
localStorage.clear();  // Reset consent
location.reload();     // Should show banner

// Accept consent
// Then track an event
analytics.track('page_view', { domain: 'lukhas.ai', path: '/test' });

// Check if event was queued
console.log(analytics._current_batch);
```

## Privacy Validation

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python3 tools/validate_analytics_privacy.py
if [ $? -ne 0 ]; then
    echo "❌ PII detected in analytics events"
    exit 1
fi
```

### CI/CD Integration

```yaml
# .github/workflows/privacy-check.yml
name: Privacy Check

on: [push, pull_request]

jobs:
  privacy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate Analytics Privacy
        run: make analytics-privacy-check
```

## Debugging

### Enable Debug Mode

```typescript
// JavaScript
localStorage.setItem('lukhas_analytics_debug', 'true');

// Check console for detailed logs
analytics.track('page_view', { ... });
// Output: [Analytics] Tracking page_view with consent: granted
```

```python
# Python
import logging
logging.basicConfig(level=logging.DEBUG)

analytics.track('page_view', {...})
# Output: DEBUG: Checking consent for analytics: granted
```

### Common Issues

#### Events not tracked

```typescript
// Check consent
const { hasAnalyticsConsent } = useConsentManager();
console.log('Has consent:', hasAnalyticsConsent);

// Check DNT
console.log('DNT enabled:', navigator.doNotTrack === '1');
```

#### PII detected

```bash
# Run validation
python3 tools/validate_analytics_privacy.py --events events.json

# Fix: Remove PII from event properties
# BAD
{ "user_email": "test@example.com" }

# GOOD
{ "domain": "lukhas.ai" }
```

#### Rate limit exceeded

```typescript
// Add debouncing for frequent events
import { debounce } from 'lodash';

const trackPageView = debounce(() => {
  analytics.track('page_view', { ... });
}, 1000);  // Max 1 per second
```

## Best Practices

### 1. Check Consent Before Tracking

```typescript
// ✅ Good
if (hasAnalyticsConsent) {
  analytics.track('page_view', { ... });
}

// ❌ Bad
analytics.track('page_view', { ... });  // No consent check
```

### 2. Use Event Taxonomy

```typescript
// ✅ Good - Event from taxonomy
analytics.track('quickstart_started', { ... });

// ❌ Bad - Custom event not in taxonomy
analytics.track('my_custom_event', { ... });  // Will throw error
```

### 3. No PII in Properties

```typescript
// ✅ Good
analytics.track('page_view', {
  domain: 'lukhas.ai',
  path: '/matriz',
});

// ❌ Bad - Contains PII
analytics.track('page_view', {
  domain: 'lukhas.ai',
  user_email: 'user@example.com',  // PII!
});
```

### 4. Batch Events

```typescript
// ✅ Good - Events are batched automatically
analytics.track('event1', { ... });
analytics.track('event2', { ... });
analytics.track('event3', { ... });
// Sent in single batch

// ❌ Bad - Manual sending
analytics.track('event1', { ... });
analytics.flush();  // Unnecessary
```

### 5. Handle Errors Gracefully

```typescript
try {
  analytics.track('page_view', { ... });
} catch (error) {
  console.error('Analytics error:', error);
  // Don't block user experience
}
```

## Migration from Plausible

If you're migrating from Plausible Analytics:

```diff
// Before (Plausible)
- plausible('page_view');

// After (Privacy-First)
+ analytics.track('page_view', {
+   domain: window.location.hostname,
+   path: window.location.pathname,
+ });
```

```diff
// Before (Plausible)
- plausible('quickstart_started', {
-   props: { language: 'python' }
- });

// After (Privacy-First)
+ analytics.track('quickstart_started', {
+   domain: window.location.hostname,
+   language: 'python',
+   quickstart_id: 'matriz-hello-world',
+ });
```

## References

- [Privacy Implementation Guide](./PRIVACY_IMPLEMENTATION.md)
- [Event Taxonomy](./event_taxonomy.json)
- [Analytics Configuration](./config.yaml)
- [GDPR Compliance Guide](https://gdpr-info.eu/)

## Support

For questions or issues:

- **GitHub**: https://github.com/LukhasAI/Lukhas/issues
- **Email**: privacy@lukhas.ai
- **Docs**: https://lukhas.ai/docs/analytics

---

**Last Updated**: 2025-11-08
**Version**: 2.0
**Status**: Production Ready
