# LUKHAS 90-Day Strategic Roadmap

> **📅 Week-by-Week Execution Plan for T4 Audit Gaps**

**Version**: 1.0
**Date**: 2025-11-06
**Duration**: 90 days (12 weeks)
**Source**: [T4 Strategic Audit & Roadmap](../../../docs/gonzo/T4%20Strategic%20Audit%20%26%20Roadmap.md)
**Status**: ✅ Canonical

---

## Overview

This roadmap addresses **19 missing components** identified in the T4 audit. By end of 90 days:
- ✅ Hardened content governance pipeline with signed evidence
- ✅ Safer Reasoning Lab with privacy controls
- ✅ Developer reproducibility and 5-minute demos
- ✅ Initial enterprise onboarding packs
- ✅ Measurable KPIs and growth dashboard

---

## Week 0 (Immediate)

**Status**: ✅ **COMPLETED**

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Merge Assistive & Content-lint PRs | @web-architect | ✅ Done | Multiple PRs merged |
| Add CODEOWNERS + PR templates | @devops | ✅ Done | Governance established |
| Create Evidence Page template | @web-architect | ✅ Done | [evidence_page.md](../../templates/evidence_page.md) |
| Generate claims registry | @web-architect | ✅ Done | `release_artifacts/claims_registry.yaml` |

---

## Weeks 1–2: Foundations

**Goal**: Complete P0 infrastructure that unblocks everything else

| Week | Task | Owner | Deliverable | Est. Hours |
|------|------|-------|-------------|------------|
| W1 | **A1**: Implement Evidence Pages for top 10 claims | @web-architect + @content-lead | 10 evidence pages in `release_artifacts/evidence/` | 16h |
| W1 | **D9**: Implement Signed Artifact CI | @infra | CI step with GPG signing | 8h |
| W1 | **H19**: SEO Technical Hygiene | @web-architect | Schema.org + hreflang setup | 8h |
| W2 | **H18**: Event Taxonomy + Dashboard | @analytics | `event-spec.json` + Metabase dashboard | 12h |
| W2 | **D10**: Deploy Content-lint + A11y CI | @devops | Full pipeline with Percy/Chromatic | 12h |

**Milestone**: Evidence infrastructure operational, SEO foundation, telemetry tracking

---

## Weeks 3–4: Product Experience

**Goal**: Ship developer-facing improvements and Reasoning Lab safety

| Week | Task | Owner | Deliverable | Est. Hours |
|------|------|-------|-------------|------------|
| W3 | **B4**: Reasoning Lab redaction slider prototype | @product + @frontend | React component with 3-mode toggle | 16h |
| W3 | **B6**: Developer reproducible demo | @dev-experience | Quickstart improvements + sandbox dataset | 12h |
| W4 | **A3**: Launch Playbooks | @product-manager | `templates/launch_playbook.md` + 2 examples | 8h |
| W4 | **B4**: Reasoning Lab safety controls (complete) | @product + @frontend | Full implementation with redaction | 12h |

**Milestone**: Reasoning Lab demo-ready, Developer onboarding converts >20% faster

---

## Weeks 5–8: Trust & Legal

**Goal**: Enterprise readiness and compliance

| Week | Task | Owner | Deliverable | Est. Hours |
|------|------|-------|-------------|------------|
| W5 | **E12**: DPA/DPIA templates | @legal + @product | Legal templates + generator script | 16h |
| W5 | **E13**: Privacy-first analytics | @product + @devops | Fathom/Plausible integration | 8h |
| W6 | **F15**: Enterprise onboarding kit | @sales + @product | `enterprise_onboarding_kit.zip` | 12h |
| W6 | **D11**: Runtime monitoring + canary | @sre | Synthetic tests + Prometheus alerts | 12h |
| W7 | **E12**: Legal review of DPA/DPIA | @legal | Approved templates | 8h |
| W8 | **F15**: Audit pack builder | @infra + @product | `tools/build_audit_pack.py` (complete) | 8h |

**Milestone**: Enterprise sales-ready, EU compliant, production monitoring active

---

## Weeks 9–12: Scale & Growth

**Goal**: Content scale, measurement, and market expansion

| Week | Task | Owner | Deliverable | Est. Hours |
|------|------|-------|-------------|------------|
| W9 | **A2**: SEO pillar pages (3 pillars) | @content-lead | Explainable AI, MATRIZ, Reasoning Lab pages | 20h |
| W9 | **H18**: KPI dashboard (phase 2) | @analytics | Quickstart, assistive adoption, claims health | 8h |
| W10 | **A2**: Content cluster (6 articles) | @content-lead | Technical posts + case studies | 24h |
| W10 | **C7**: Assistive workflow automation | @content-lead + @devops | Editorial flow + GitHub automation | 12h |
| W11 | **B5**: Feature flags for content | @devops | LaunchDarkly/Config integration | 8h |
| W11 | **C7**: Assistive user testing (1st batch) | @ux-research | Recruit + run usability tests | 16h |
| W12 | **G16**: Localization pipeline (if EU) | @content-lead | Crowdin/Locale setup + QA | 16h |
| W12 | **Retrospective & Phase 2 planning** | All | Document lessons, plan next 90 days | 4h |

**Milestone**: Organic traffic growing, assistive adoption measured, ready for EU expansion

---

## Optional Extensions (If Capacity Available)

These are P1/P2 items that can be added if teams have extra capacity:

| Task | Owner | Est. Effort | When |
|------|-------|-------------|------|
| **C8**: Privacy-first personalization | @product | 2 weeks | W10–W11 |
| **F14**: Developer community program | @community | 3 weeks | W10–W12 |
| **G17**: Component library + Storybook | @frontend | 2 weeks | W11–W12 |

---

## Success Metrics (90-Day Targets)

| Metric | Baseline | Target | How Measured |
|--------|----------|--------|--------------|
| **Evidence Coverage** | 0% | 100% of high-risk claims | Count of evidence pages |
| **Developer Conversion** | Unknown | >20% Quickstart→integration | Event taxonomy (H18) |
| **Assistive Adoption** | 0% | >10% users enable assistive mode | Analytics (E13) |
| **Enterprise Pipeline** | 0 | 5+ qualified leads | Sales reports + audit pack downloads |
| **SEO Organic Traffic** | Baseline | +50% to pillar pages | Google Analytics |
| **Production Uptime** | Unknown | 99.9% p95 <250ms | Monitoring (D11) |
| **Legal Readiness** | Not ready | EU compliant, DPA ready | Legal sign-off (E12) |

---

## Weekly Check-in Agenda

**Every Monday 10am**:
1. **Review last week**: What shipped? What's blocked?
2. **This week's goals**: Confirm owners and deliverables
3. **Risks & dependencies**: Surface blockers early
4. **Metrics update**: Track progress toward 90-day targets
5. **Scope adjustments**: Add/remove tasks based on capacity

**Participants**: @product-manager, @web-architect, @content-lead, @legal, @infra, @analytics

---

## Dependencies & Critical Path

```
Evidence Pages (W1) ─────────→ Audit Pack (W8) ─────────→ Enterprise Kit (W6)
       ↓                               ↓
Artifact Signing (W1) ────→ Runtime Monitoring (W6)
       ↓
Event Taxonomy (W2) ─────────→ KPI Dashboard (W9) ───→ Growth measurement

SEO Hygiene (W1) ─────────→ SEO Pillars (W9) ─────────→ Organic traffic
       ↓                               ↓
Content CI (W2) ─────────→ Assistive Workflow (W10) ──→ Scale
       ↓
Reasoning Lab (W3-W4) ───→ Developer Demo (W4) ───→ Conversion

DPA Templates (W5) ─────────→ Legal Review (W7) ───→ Enterprise ready
```

**Critical path items**: Evidence Pages → Artifact Signing → Event Taxonomy → SEO Hygiene → Reasoning Lab → DPA Templates

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Legal review delays | Medium | High | Start W5, budget 2 weeks |
| Reasoning Lab scope creep | High | Medium | Freeze scope at 3-mode toggle + redaction |
| Content production bandwidth | High | Medium | Hire contractor or extend W9–W10 |
| CI/CD pipeline conflicts | Medium | Low | Weekly sync with @devops |
| Enterprise sales not ready | Low | High | Audit pack ready W8 (buffer week) |

---

## Phase 2 Preview (Days 91–180)

After 90 days, focus shifts to:
1. **Visionary experiments**: Audit-as-a-Service, Reasoning Graph Marketplace
2. **Market expansion**: Full EU localization, enterprise case studies
3. **Developer ecosystem**: Community program, verified app marketplace
4. **Advanced personalization**: Cohort-based messaging, privacy-first recommendations

See [INNOVATION_PIPELINE.md](./INNOVATION_PIPELINE.md) for breakthrough ideas.

---

## Related Documents

- **Gaps Analysis**: [GAPS_ANALYSIS.md](./GAPS_ANALYSIS.md) - All 19 missing items
- **Strategic Audit**: [T4_STRATEGIC_AUDIT.md](./T4_STRATEGIC_AUDIT.md) - Full findings
- **Innovation Pipeline**: [INNOVATION_PIPELINE.md](./INNOVATION_PIPELINE.md) - Visionary ideas
- **Evidence System**: [../../templates/evidence_page.md](../../templates/evidence_page.md) - W1 deliverable

---

**Document Owner**: @product-manager
**Review Cycle**: Weekly Monday check-ins
**Last Updated**: 2025-11-06
