# Launch Types Reference

> **📚 Classification and requirements for different launch types**

**Version**: 1.0
**Last Updated**: 2025-11-08
**Status**: Active - Reference for all launches

---

## Overview

LUKHAS AI has four primary launch types, each with specific requirements, timelines, and stakeholder involvement. Understanding the launch type is critical for selecting the right playbook, checklist, and timeline.

**Launch Types**:
1. **Major Product Launch** - New product or significant capability (e.g., Reasoning Lab)
2. **Feature Launch** - New feature within existing product (e.g., new API endpoint)
3. **Infrastructure Launch** - Backend/platform improvements (e.g., new region, CDN)
4. **Content Launch** - Educational/marketing content (e.g., evidence pages, documentation)

---

## 1. Major Product Launch

### Definition

A major product launch introduces a **new product** or **significant new capability** that fundamentally expands LUKHAS AI's value proposition. This is typically a market-facing event with significant press, marketing, and customer impact.

### Examples

- **Reasoning Lab** - Interactive consciousness tracing interface
- **MATRIZ Engine v2.0** - Complete rewrite with new architecture
- **Identity System** - Lambda-Inspired Digital Identity framework
- **Enterprise Console** - New B2B dashboard for organizations
- **API Platform** - Public API marketplace

### Timeline

**Typical Duration**: 8-12 weeks (kickoff to launch)

**Key Milestones**:
- T-90 days: Kickoff and planning
- T-60 days: Requirements and design finalized
- T-30 days: Alpha release (internal)
- T-14 days: Beta release (external, selected users)
- T-7 days: Legal/security final approval
- T-1 day: Go/no-go decision
- T-0: Launch day
- T+7 days: Week-1 review
- T+30 days: Month-1 review

### Stakeholder Involvement

**Required Stakeholders**:
- Executive Sponsor (CEO/CPO)
- Product Lead
- Engineering Lead
- Marketing Lead
- Design Lead
- Legal Counsel
- Security Lead
- Analytics Lead
- DevOps/SRE Lead
- Customer Support Lead
- Community Lead (if open-source component)

**RACI**: All stakeholders have active roles (see [PLAYBOOK_TEMPLATE.md](PLAYBOOK_TEMPLATE.md))

### Checklist Requirements

**Must Complete**:
- ✅ All sections of [FEATURE_CHECKLIST.md](FEATURE_CHECKLIST.md)
- ✅ Technical readiness (100%)
- ✅ Marketing readiness (100%)
- ✅ Legal/compliance readiness (100%)
- ✅ Security readiness (100%)
- ✅ Analytics readiness (100%)
- ✅ Accessibility readiness (100%)

**No Exceptions**: Major product launches cannot skip any checklist items.

### Marketing Requirements

**Required Marketing Assets**:
- [ ] **Landing page** - Dedicated product page (SEO optimized)
- [ ] **Blog post** - Launch announcement (800-1200 words)
- [ ] **Press release** - For newsworthy launches
- [ ] **Social media campaign** - Multi-platform (Twitter/X, LinkedIn, Discord)
- [ ] **Email campaign** - Segmented by user type
- [ ] **Demo video** - 2-3 minute product walkthrough
- [ ] **Documentation** - Quickstart, tutorials, API reference
- [ ] **FAQ** - Comprehensive troubleshooting
- [ ] **Case studies** - If applicable
- [ ] **Partnership announcements** - If applicable

**Go-to-Market Strategy**: Full GTM plan required, including target audience, messaging framework, and competitive positioning.

### Legal/Compliance Requirements

**Required Approvals**:
- [ ] **Claims approval** - All performance/operational claims reviewed
- [ ] **Evidence pages** - Created and linked for all claims
- [ ] **Vocabulary compliance** - No forbidden terms (see `branding_vocab_lint.py`)
- [ ] **Privacy review** - DPIA if handling new PII
- [ ] **Terms of Service** - Updated if new user obligations
- [ ] **Data Processing Agreement** - Template ready for enterprise customers
- [ ] **Trademark clearance** - Product name available

### Success Metrics

**Required KPIs**:
- Adoption rate (% of users who try new product)
- Engagement rate (DAU/WAU)
- Retention rate (D1, D7, D30)
- Conversion rate (free → paid, if applicable)
- NPS (Net Promoter Score)
- CSAT (Customer Satisfaction)
- Revenue impact (if monetized)
- Media coverage (press mentions)

**Target Setting**: All KPIs must have quantitative targets before launch.

### Rollback Plan

**Required**: Full rollback procedure documented and tested. Feature flags preferred for gradual rollout.

**Rollback Criteria**: Defined thresholds for automatic rollback (error rate, latency, uptime).

---

## 2. Feature Launch

### Definition

A feature launch introduces a **new capability within an existing product**. This is typically less disruptive than a major product launch but still requires cross-functional coordination.

### Examples

- **New API endpoint** - `/v1/reasoning/explain`
- **Export functionality** - Download reasoning traces as JSON/PDF
- **Webhook support** - Real-time event notifications
- **Dark mode** - UI theme switching
- **Multi-language support** - i18n for Spanish, French, German
- **SSO integration** - SAML/OIDC enterprise authentication

### Timeline

**Typical Duration**: 4-6 weeks (kickoff to launch)

**Key Milestones**:
- T-30 days: Kickoff and requirements
- T-21 days: Design complete
- T-14 days: Development complete
- T-7 days: Testing and legal approval
- T-1 day: Go/no-go decision
- T-0: Launch day
- T+7 days: Week-1 review

### Stakeholder Involvement

**Required Stakeholders**:
- Product Lead
- Engineering Lead
- Marketing Lead (reduced involvement)
- Legal Counsel (if claims made)
- Security Lead (if touching auth/data)
- Analytics Lead

**Optional Stakeholders**:
- Design Lead (if UI changes)
- Customer Support Lead (if user-facing)

### Checklist Requirements

**Must Complete**:
- ✅ Technical readiness (100%)
- ✅ Security readiness (100%)
- ✅ Analytics readiness (100%)
- 🟡 Marketing readiness (reduced scope - blog post, social, email)
- 🟡 Legal/compliance readiness (if claims made)
- 🟡 Accessibility readiness (if UI changes)

**Flexible**: Feature launches can skip extensive marketing if incremental improvement.

### Marketing Requirements

**Minimum Marketing Assets**:
- [ ] **Blog post** - Feature announcement (400-600 words)
- [ ] **Social media** - 1-2 posts across platforms
- [ ] **Email** - In-app notification or changelog email
- [ ] **Documentation** - Updated to reflect new feature
- [ ] **Changelog** - Entry in product changelog

**No Landing Page Required**: Feature launches typically don't need dedicated landing pages (unless strategic).

### Legal/Compliance Requirements

**Conditional Requirements**:
- [ ] **Claims approval** - Only if making performance claims
- [ ] **Evidence pages** - Only if claims require evidence
- [ ] **Vocabulary compliance** - Always required
- [ ] **Privacy review** - Only if handling new PII
- [ ] **Terms of Service** - Only if new user obligations

### Success Metrics

**Required KPIs**:
- Feature adoption rate (% of users who enable/use feature)
- Feature engagement (interactions per user)
- Feature satisfaction (in-app survey)

**Optional KPIs**:
- Conversion lift (if impacts monetization)
- Support ticket volume (should not increase significantly)

### Rollback Plan

**Required**: Feature flag strongly recommended for easy rollback.

---

## 3. Infrastructure Launch

### Definition

An infrastructure launch deploys **backend/platform improvements** that may not be directly visible to users but impact performance, reliability, or scalability.

### Examples

- **New AWS region** - Expand to eu-west-2 (London)
- **CDN migration** - Switch from Cloudflare to Fastly
- **Database upgrade** - PostgreSQL 14 → 16
- **Kubernetes upgrade** - 1.28 → 1.30
- **Monitoring platform** - Migrate to Datadog
- **CI/CD pipeline** - GitHub Actions → GitLab CI
- **Load balancer upgrade** - NGINX → Envoy

### Timeline

**Typical Duration**: 2-4 weeks (planning to deployment)

**Key Milestones**:
- T-14 days: Technical design and testing plan
- T-7 days: Staging deployment and testing
- T-3 days: Security and performance validation
- T-1 day: Go/no-go decision
- T-0: Production deployment
- T+1 day: Monitoring and stability verification

### Stakeholder Involvement

**Required Stakeholders**:
- Engineering Lead
- DevOps/SRE Lead
- Security Lead (if security-related)

**Optional Stakeholders**:
- Product Lead (informed only)
- Analytics Lead (if monitoring changes)

**No Marketing Involvement**: Infrastructure launches are typically not user-facing.

### Checklist Requirements

**Must Complete**:
- ✅ Technical readiness (100%)
- ✅ Security readiness (100%)
- ✅ Infrastructure & monitoring readiness (100%)
- ✅ Rollback plan (critical for infra changes)

**Not Required**:
- ❌ Marketing readiness
- ❌ Legal/compliance (unless regulatory impact)
- ❌ Accessibility readiness

### Marketing Requirements

**No Marketing**: Infrastructure launches are silent to users unless they improve performance/reliability (in which case, changelog entry may be warranted).

**Exception**: If infrastructure enables new capabilities (e.g., new region = GDPR compliance), then marketing may be involved.

### Legal/Compliance Requirements

**Conditional Requirements**:
- [ ] **Privacy review** - Only if data residency changes (e.g., new region)
- [ ] **Compliance review** - Only if regulatory impact (e.g., SOC 2, ISO 27001)

### Success Metrics

**Required KPIs**:
- System uptime (should not degrade)
- Error rate (should not increase)
- P95 latency (should improve or stay same)
- Cost efficiency (infrastructure cost per user)

**Deployment Success**:
- Zero customer-facing incidents during deployment
- Rollback not required

### Rollback Plan

**Critical**: Infrastructure launches must have immediate rollback capability (blue/green deployment, canary deployment, or instant revert).

**Testing**: Rollback must be tested in staging before production deployment.

---

## 4. Content Launch

### Definition

A content launch publishes **educational, marketing, or governance content** that doesn't involve code deployment. This includes documentation, blog posts, evidence pages, and branding materials.

### Examples

- **Evidence pages** - Performance claim documentation
- **Documentation overhaul** - Redesigned developer docs
- **Blog series** - "Reasoning at Scale" 5-part series
- **Case study** - Customer success story
- **Whitepaper** - Technical deep-dive on MATRIZ architecture
- **Governance policies** - Legal templates, DPA/DPIA
- **Branding refresh** - Updated visual identity, messaging

### Timeline

**Typical Duration**: 1-3 weeks (content creation to publication)

**Key Milestones**:
- T-14 days: Content outline and approval
- T-7 days: First draft complete
- T-3 days: Legal and technical review
- T-1 day: Final edits and SEO optimization
- T-0: Publication
- T+7 days: Performance analysis (traffic, engagement)

### Stakeholder Involvement

**Required Stakeholders**:
- Content Lead / Writer
- Marketing Lead (if promotional content)
- Legal Counsel (if making claims)
- Web Architect (if SEO-critical)

**Optional Stakeholders**:
- Technical Reviewer (if technical content)
- Design Lead (if visual assets needed)

### Checklist Requirements

**Must Complete**:
- ✅ Legal/compliance readiness (if claims made)
- ✅ SEO optimization (canonical URL, meta description, keywords)
- ✅ Accessibility readiness (alt text, heading hierarchy, Flesch-Kincaid)
- 🟡 Marketing readiness (social promotion)

**Not Required**:
- ❌ Technical readiness (no code deployment)
- ❌ Security readiness (no infrastructure changes)
- ❌ Analytics readiness (standard page view tracking sufficient)

### Marketing Requirements

**Minimum Marketing Assets**:
- [ ] **SEO optimization** - Meta tags, canonical URL, schema.org
- [ ] **Social media** - 1-2 promotional posts
- [ ] **Email** - Newsletter feature (if significant content)
- [ ] **Internal link structure** - Link from related pages

**Amplification Strategy**: Identify distribution channels (Twitter/X, LinkedIn, Hacker News, Reddit, Discord).

### Legal/Compliance Requirements

**Always Required**:
- [ ] **Claims approval** - If making performance/operational claims
- [ ] **Evidence links** - If claims made
- [ ] **Vocabulary compliance** - No forbidden terms

**Content-Specific**:
- [ ] **Plagiarism check** - Ensure original content
- [ ] **Image licensing** - All images properly licensed
- [ ] **Fact-checking** - Technical accuracy verified

### Success Metrics

**Required KPIs**:
- Page views (organic + referral)
- Time on page (engagement)
- Social shares
- Backlinks (SEO value)

**Optional KPIs**:
- Conversions (if CTA present)
- Lead generation (if gated content)

### Rollback Plan

**Easy**: Content can be unpublished or edited instantly. No complex rollback needed.

---

## Launch Type Selection Matrix

Use this table to determine which launch type applies:

| Question | Product | Feature | Infrastructure | Content |
|----------|---------|---------|----------------|---------|
| **Is this a new product?** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Is this user-facing?** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Does it require code deployment?** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Does it require marketing?** | ✅ Yes | 🟡 Maybe | ❌ No | 🟡 Maybe |
| **Does it require legal review?** | ✅ Yes | 🟡 If claims | 🟡 If regulatory | ✅ If claims |
| **Timeline** | 8-12 weeks | 4-6 weeks | 2-4 weeks | 1-3 weeks |
| **Stakeholders** | 10+ | 5-7 | 2-4 | 2-4 |
| **Rollback complexity** | High | Medium | High | Low |

---

## Cross-Launch Type Requirements

### Universal Requirements (All Launch Types)

**Required for ALL launches**:
- [ ] **Launch playbook** - Copy and customize [PLAYBOOK_TEMPLATE.md](PLAYBOOK_TEMPLATE.md)
- [ ] **Timeline** - Define milestones and dependencies
- [ ] **Owner assigned** - Single launch lead accountable
- [ ] **Go/no-go decision** - Formal sign-off before launch
- [ ] **Post-launch review** - Retrospective within 7 days

**Exception**: Trivial content updates (e.g., fixing a typo) don't require formal playbook.

### Vocabulary Compliance (All Launch Types)

**Always Enforce**:
- ❌ NO "true AI" (use "quantum-inspired AI")
- ❌ NO "sentient AI" (use "bio-inspired consciousness")
- ❌ NO "production-ready" without approval (requires evidence)
- ❌ NO "AGI" (use "LUKHAS AI", "advanced AI system")

**Tool**: Run `make branding-vocab-lint` before every launch.

### Evidence & Claims (Product, Feature, Content Launches)

**If making any claims** (percentages, latencies, counts, operational):
- [ ] Evidence artifact generated (JSON, PDF, benchmark)
- [ ] Evidence page created (`release_artifacts/evidence/[claim].md`)
- [ ] Evidence linked in front-matter (`evidence_links: [...]`)
- [ ] Legal approval obtained (`claims_approval: true`)
- [ ] Claims registry updated (`make claims-registry`)

**No claims, no evidence required.**

---

## Launch Type Templates

### Quick Start

1. **Identify launch type** using selection matrix above
2. **Copy template** from table below
3. **Customize** for your specific launch

| Launch Type | Template | Checklist | Timeline |
|-------------|----------|-----------|----------|
| **Product** | [PLAYBOOK_TEMPLATE.md](PLAYBOOK_TEMPLATE.md) | [FEATURE_CHECKLIST.md](FEATURE_CHECKLIST.md) (all sections) | [TIMELINE_TEMPLATE.md](TIMELINE_TEMPLATE.md) (8-12 weeks) |
| **Feature** | [PLAYBOOK_TEMPLATE.md](PLAYBOOK_TEMPLATE.md) | [FEATURE_CHECKLIST.md](FEATURE_CHECKLIST.md) (reduce marketing) | [TIMELINE_TEMPLATE.md](TIMELINE_TEMPLATE.md) (4-6 weeks) |
| **Infrastructure** | [PLAYBOOK_TEMPLATE.md](PLAYBOOK_TEMPLATE.md) | [FEATURE_CHECKLIST.md](FEATURE_CHECKLIST.md) (tech only) | [TIMELINE_TEMPLATE.md](TIMELINE_TEMPLATE.md) (2-4 weeks) |
| **Content** | Simplified playbook | SEO + Legal checklist only | 1-3 weeks (no template needed) |

---

## Examples

See [examples/](examples/) directory for real-world launch playbooks:

- **[reasoning_lab_launch.md](examples/reasoning_lab_launch.md)** - Major product launch example

---

## Decision Tree

**Use this flowchart to select launch type**:

```
START
  ↓
Is this a new product or major capability?
  ↓ YES → MAJOR PRODUCT LAUNCH
  ↓ NO
  ↓
Does it require code deployment?
  ↓ YES → Is it user-facing?
  │         ↓ YES → FEATURE LAUNCH
  │         ↓ NO → INFRASTRUCTURE LAUNCH
  ↓ NO
  ↓
CONTENT LAUNCH
```

---

## Appendix: Launch Type History

Track all LUKHAS AI launches by type:

### 2025 Launches

| Date | Launch Name | Type | Status | Link |
|------|-------------|------|--------|------|
| TBD | Reasoning Lab Beta | Product | 🟡 Planned | [Playbook](examples/reasoning_lab_launch.md) |
| TBD | MATRIZ v2.0 | Product | 🔴 Planned | TBD |
| TBD | Identity System | Product | 🔴 Planned | TBD |
| 2025-11-08 | Evidence Pages (Top 20) | Content | ✅ Complete | PR #1128 |
| 2025-11-08 | SEO Front-Matter (55 pages) | Content | ✅ Complete | PR #1129 |

### 2024 Launches

| Date | Launch Name | Type | Status | Link |
|------|-------------|------|--------|------|
| [Past launches TBD] | | | | |

---

**Launch Types Version**: 1.0
**Last Updated**: 2025-11-08
**Owner**: @web-architect
**Maintained By**: Product & Engineering Leadership

---

**Related Documents**:
- [Launch Playbook Template](PLAYBOOK_TEMPLATE.md)
- [Feature Checklist](FEATURE_CHECKLIST.md)
- [Timeline Template](TIMELINE_TEMPLATE.md)
- [Evidence System](../tools/EVIDENCE_SYSTEM.md)
- [Claims Policy](../policies/CLAIMS_POLICY.md)
- [SEO Guide](../SEO_GUIDE.md)
