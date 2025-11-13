---
title: "Analytics Integration Guide for LUKHAS Websites"
domain: lukhas.ai
owner: @web-architect
audience: [developers, frontend-engineers]
tone:
  poetic: 0.0
  user_friendly: 0.60
  academic: 0.40
canonical: https://lukhas.ai/analytics/integration-guide
source: branding
last_reviewed: "2025-11-08"
evidence_links: []
claims_approval: false
claims_verified_by: []
seo:
  description: "Privacy-first analytics integration guide using Plausible Analytics with custom event tracking for LUKHAS KPIs"
  keywords: ["LUKHAS analytics", "Plausible integration", "privacy-first tracking", "custom events"]
  og_image: /assets/og-images/analytics-integration.png
---

# Analytics Integration Guide for LUKHAS Websites

## Overview

This guide covers privacy-first analytics integration using Plausible Analytics (or Fathom) with custom event tracking for LUKHAS-specific KPIs.

## Setup

### 1. Install Plausible Script

Add to `<head>` of all branding pages:

```html
<script defer data-domain="lukhas.ai" src="https://plausible.io/js/script.js"></script>
```

For custom events:

```html
<script defer data-domain="lukhas.ai" src="https://plausible.io/js/script.tagged-events.js"></script>
```

### 2. Configure Custom Events

**Event Format**:
```javascript
plausible('event_name', {props: {property: 'value'}})
```

**Example - Quickstart Started**:
```javascript
plausible('quickstart_started', {
  props: {
    domain: 'lukhas.dev',
    language: 'python',
    quickstart_id: 'matriz-hello-world'
  }
})
```

**Example - Assistive Mode Viewed**:
```javascript
plausible('assistive_variant_viewed', {
  props: {
    domain: 'lukhas.ai',
    page: '/matriz',
    trigger: 'toggle'
  }
})
```

### 3. Event Tracking Code

**Quickstart Tracking**:
```javascript
// On quickstart page load
document.addEventListener('DOMContentLoaded', () => {
  plausible('quickstart_started', {
    props: {
      domain: window.location.hostname,
      language: getQuickstartLanguage(),
      quickstart_id: getQuickstartId()
    }
  });

  // On successful completion
  window.addEventListener('quickstart_complete', (e) => {
    plausible('quickstart_completed', {
      props: {
        domain: window.location.hostname,
        language: e.detail.language,
        quickstart_id: e.detail.id,
        duration_seconds: e.detail.duration,
        success: true
      }
    });
  });
});
```

**Assistive Mode Tracking**:
```javascript
// On assistive mode toggle
document.getElementById('assistive-toggle').addEventListener('click', () => {
  plausible('assistive_variant_viewed', {
    props: {
      domain: window.location.hostname,
      page: window.location.pathname,
      trigger: 'toggle'
    }
  });
});

// On assistive audio playback
document.querySelectorAll('.assistive-audio-player').forEach(player => {
  player.addEventListener('play', () => {
    plausible('assistive_audio_played', {
      props: {
        domain: window.location.hostname,
        page: window.location.pathname
      }
    });
  });
});
```

**Evidence Link Tracking**:
```javascript
// On evidence link click
document.querySelectorAll('a[data-evidence-id]').forEach(link => {
  link.addEventListener('click', (e) => {
    plausible('evidence_artifact_requested', {
      props: {
        domain: window.location.hostname,
        claim_page: window.location.pathname,
        evidence_id: e.target.dataset.evidenceId
      }
    });
  });
});
```

**Reasoning Lab Tracking**:
```javascript
// On reasoning trace view
function trackReasoningTrace(traceType, depth) {
  plausible('reasoning_trace_viewed', {
    props: {
      domain: window.location.hostname,
      trace_type: traceType,
      interaction_depth: depth
    }
  });
}

// Example usage
document.getElementById('symbolic-dna-trace').addEventListener('click', () => {
  trackReasoningTrace('symbolic_dna', 1);
});
```

**Demo Interaction Tracking**:
```javascript
// On demo start
function startDemo(demoType) {
  plausible('demo_interaction', {
    props: {
      domain: window.location.hostname,
      demo_type: demoType,
      action: 'start'
    }
  });
}

// On demo step
function stepDemo(demoType) {
  plausible('demo_interaction', {
    props: {
      domain: window.location.hostname,
      demo_type: demoType,
      action: 'step'
    }
  });
}

// On demo completion
function completeDemo(demoType) {
  plausible('demo_interaction', {
    props: {
      domain: window.location.hostname,
      demo_type: demoType,
      action: 'complete'
    }
  });
}
```

**CTA Click Tracking**:
```javascript
// Track all CTA clicks
document.querySelectorAll('[data-cta]').forEach(cta => {
  cta.addEventListener('click', (e) => {
    plausible('cta_clicked', {
      props: {
        domain: window.location.hostname,
        cta_text: e.target.textContent.trim(),
        cta_location: e.target.dataset.ctaLocation || 'unknown'
      }
    });
  });
});
```

## Privacy Compliance

### GDPR Requirements

1. **No PII**: Never track user IDs, emails, or names
2. **Respect DNT**: Honor Do Not Track header
3. **Cookie Consent**: Use essential cookies only (no tracking cookies)
4. **Data Retention**: 90 days aggregate, 30 days raw

### Configuration

```javascript
// Plausible respects DNT by default
// No additional configuration needed for GDPR compliance
```

### Cookie-Free Tracking

Plausible Analytics is cookie-free by default, making it GDPR-compliant without cookie consent banners. All tracking is anonymous and aggregated.

## Testing

### Local Testing

```javascript
// Enable debug mode
localStorage.plausible_ignore = 'false'

// Test event
plausible('quickstart_started', {props: {domain: 'lukhas.dev', language: 'test'}})

// Check browser console for event confirmation
```

### Verification

1. Open Plausible dashboard: https://plausible.io/lukhas.ai
2. Go to "Goal Conversions"
3. Trigger test events locally
4. Verify events appear in real-time (1-minute lag)

## Dashboard Access

- **Platform**: Plausible Analytics (https://plausible.io)
- **Dashboards**:
  - https://plausible.io/lukhas.ai
  - https://plausible.io/lukhas.dev
  - https://plausible.io/lukhas.com
  - https://plausible.io/lukhas.eu
  - https://plausible.io/lukhas.app
- **API**: https://plausible.io/docs/stats-api (for custom dashboards)

## Troubleshooting

**Q: Events not appearing in dashboard**
A: Check browser console for errors, verify script loaded, check domain matches

**Q: Too many events firing**
A: Add debouncing to rapid-fire events (clicks, scrolls)

**Q: Need to export data**
A: Use Plausible API or CSV export feature in dashboard

**Q: DNT header not being respected**
A: Plausible respects DNT by default; check browser DNT settings

## Implementation Checklist

- [ ] Install Plausible script on all domains
- [ ] Configure custom events in Plausible dashboard
- [ ] Implement event tracking code for all 9 events
- [ ] Test events in local environment
- [ ] Verify events in Plausible dashboard
- [ ] Set up KPI goals and alerts
- [ ] Document analytics setup in project README

## Next Steps

1. Set up Plausible account and add all 5 LUKHAS domains
2. Configure custom event goals in Plausible dashboard
3. Implement event tracking code in website templates
4. Set up weekly analytics review process
5. Create custom dashboard using Plausible API

## References

- [Plausible Analytics Documentation](https://plausible.io/docs)
- [Custom Events Guide](https://plausible.io/docs/custom-event-goals)
- [Event Taxonomy Specification](./event_taxonomy.json)
- [KPI Dashboard Specification](./kpi_dashboard_spec.md)
