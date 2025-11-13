---
title: "LUKHAS Analytics KPI Dashboard Specification"
domain: lukhas.ai
owner: @web-architect
audience: [developers, data-analysts, product-managers]
tone:
  poetic: 0.0
  user_friendly: 0.50
  academic: 0.50
canonical: https://lukhas.ai/analytics/kpi-dashboard-spec
source: branding
last_reviewed: "2025-11-08"
evidence_links: []
claims_approval: false
claims_verified_by: []
seo:
  description: "LUKHAS Analytics KPI Dashboard specification for privacy-first user journey tracking across 5 domains"
  keywords: ["LUKHAS analytics", "KPI dashboard", "privacy-first analytics", "GDPR compliance"]
  og_image: /assets/og-images/analytics-dashboard.png
---

# LUKHAS Analytics KPI Dashboard Specification

## Dashboard Overview

**Purpose**: Track user journeys and content effectiveness across 5 LUKHAS domains
**Update Frequency**: Real-time (1-minute lag)
**Retention**: 90 days rolling window
**Privacy**: GDPR-compliant, no PII

## Key Performance Indicators (KPIs)

### 1. Quickstart Success Rate
**Definition**: (Completed / Started) × 100%
**Target**: ≥50% success rate
**Alert**: <40% triggers investigation

**Breakdown**:
- By language (Python, JavaScript, Rust)
- By domain (lukhas.dev primary, lukhas.ai secondary)
- By quickstart type (MATRIZ hello-world, Identity integration, etc.)

**Visualization**: Line chart (daily) + breakdown table

### 2. Assistive Mode Adoption Rate
**Definition**: (Assistive views / Total views) × 100%
**Target**: ≥2% adoption for high-traffic pages
**Alert**: <1% suggests poor discoverability

**Breakdown**:
- By domain (lukhas.ai, lukhas.dev, etc.)
- By page type (homepage, product, docs)
- By trigger (toggle, preference, auto)

**Visualization**: Stacked bar chart (weekly)

### 3. Reasoning Lab Engagement
**Definition**: (Users viewing traces / Total visitors) × 100%
**Target**: ≥15% engagement rate
**Alert**: <10% suggests low interest or discoverability issues

**Breakdown**:
- By trace type (symbolic DNA, quantum reasoning, etc.)
- By interaction depth (1 node, 2+ nodes, full graph)
- By domain (lukhas.ai, lukhas.eu)

**Visualization**: Funnel chart (entry → view → interact)

### 4. Evidence Transparency Engagement
**Definition**: (Evidence clicks / Claims displayed) × 100%
**Target**: ≥5% click-through rate
**Alert**: <2% suggests evidence links not prominent enough

**Breakdown**:
- By evidence type (performance, security, compliance)
- By domain
- By claim type (percentage, latency, count)

**Visualization**: Heatmap of claim → evidence click patterns

### 5. Demo Completion Rate
**Definition**: (Demos completed / Demos started) × 100%
**Target**: ≥60% completion rate
**Alert**: <45% suggests demo too complex

**Breakdown**:
- By demo type (MATRIZ reasoning, Guardian system, etc.)
- By step drop-off (where users abandon)
- By domain

**Visualization**: Sankey diagram (start → steps → complete)

### 6. CTA Conversion Rate
**Definition**: (CTA clicks / Page views) × 100%
**Target**: Varies by CTA location (hero: ≥3%, sidebar: ≥1%)
**Alert**: <50% of target triggers review

**Breakdown**:
- By CTA text ("Try Now", "Learn More", "Get Started")
- By page location (hero, sidebar, footer)
- By domain

**Visualization**: Bar chart with target lines

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│ LUKHAS Analytics Dashboard                    [Last 30 Days]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Quickstart Success: 52.3% (Target: ≥50%)                   │
│  Assistive Adoption: 2.1% (Target: ≥2%)                     │
│  Reasoning Engagement: 17.8% (Target: ≥15%)                 │
│  Evidence Clicks: 6.2% (Target: ≥5%)                        │
│  Demo Completion: 58.1% (Target: ≥60%)                      │
│  CTA Conversion: 2.8% (Hero target: ≥3%)                    │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Quickstart Funnel          Assistive Adoption (Weekly)     │
│  ┌─────────────────┐        ┌─────────────────┐            │
│  │ Started: 1,243  │        │ lukhas.ai: 2.4% │            │
│  │ Step 1: 1,089   │        │ lukhas.dev: 1.8%│            │
│  │ Step 2: 892     │        │ lukhas.com: 2.7%│            │
│  │ Completed: 650  │        │ lukhas.eu: 1.9% │            │
│  └─────────────────┘        └─────────────────┘            │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Top Performing Content          Alerts                     │
│  1. /matriz (2.3K views)         Demo drop-off at Step 3   │
│  2. /quickstart (1.8K)           CTA hero below target     │
│  3. /reasoning-lab (1.2K)        All others on target      │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

1. **Analytics Platform**: Plausible Analytics (privacy-first) OR Fathom Analytics
2. **Event Stream**: Custom events sent via JavaScript SDK
3. **Claims Registry**: Generated from `branding/governance/claims_registry.json`
4. **Content Metadata**: Front-matter from all branding markdown files

## Implementation Notes

- Use Plausible custom events API: https://plausible.io/docs/custom-event-goals
- Aggregate data in 1-hour buckets, retain raw events for 30 days
- Export weekly CSV reports for long-term analysis
- Dashboard hosted on Grafana or custom Next.js app
