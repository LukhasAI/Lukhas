# LUKHAS Branding — Website Content Templates

> **📋 DUPLICATE - USE CANONICAL VERSION**
>
> **Status**: DUPLICATE OF HIOMEPAGE_&_CASE_STUDY.md (2025-11-06)
>
> This file is a duplicate. The canonical version has been moved to:
> - **[branding/templates/HOMEPAGE_CASESTUDY_TEMPLATES.md](../../branding/templates/HOMEPAGE_CASESTUDY_TEMPLATES.md)**
>
> **This document will be removed in cleanup.** For template usage, refer to the canonical location above.

---

This document provides canonical templates for LUKHAS website content, specifically for homepages and case studies. Each template includes front-matter metadata, content structure, and authoring guidelines to ensure consistency, accessibility, and compliance across all LUKHAS domains.

You can copy each template directly into your repo under `branding/websites/<domain>/` (or into `branding/templates/` so authors reuse them). I also include a tiny checklist for authors & reviewers.

---

## A — Homepage template (canonical)

**File suggestion:** `branding/templates/homepage.md`
(Authors should copy into `branding/websites/<domain>/homepage.md` and create `homepage.assistive.md` or declare `variants.assistive`.)

````markdown
---
title: "{{PAGE_TITLE}}"                # e.g. "LUKHAS — Consciousness AI Platform"
domain: "lukhas.ai"                   # domain id: lukhas.ai | lukhas.dev | ...
owner: "@gonzalo"                     # content owner for CODEOWNERS
audience: "general"                   # general|developers|enterprise|regulators
tone:
  poetic: 0.40
  user_friendly: 0.40
  academic: 0.20
canonical: true
source: "branding/templates/homepage.md"
variants:
  assistive: "homepage.assistive.md"  # optional; required for critical pages
evidence_links:
  - "release_artifacts/perf/2025-10-26-matriz-smoke.json"
claims_verified_by:
  - "@web-architect"
claims_verified_date: "2025-11-06"
claims_approval: false                # must be true for production claims
seo:
  title: "LUKHAS — {{SEO_TITLE}}"
  description: "{{SEO_DESC}}"
  keywords: ["Matriz","explainable AI","LUKHAS"]
hreflang: ["en-US"]
last_reviewed: "2025-11-06"
tags: ["homepage","product","matriz"]
---

# HERO — Lead (short + clear)
**H1 (short)**  
Where digital minds learn to explain themselves.

**H2 (one-line subhead)**  
MΛTRIZ — cognitive DNA for explainable AI. Try a safe demo or see the developer quickstart.

[Primary CTA: Try a Safe Demo](#reasoning-lab)  •  [Secondary CTA: Get started (Developers)](/lukhas.dev)

---

## Quick overview (3 short bullets)
- **Explainability:** See the reasoning steps behind every answer.  
- **Performance:** Sub-250ms P95 reasoning (evidence attached).  
- **Ethics & Safety:** Guardian enforces policy and audits reasoning chains.

---

## Feature section (repeatable card)
### Feature name — one sentence
Short supporting sentence (12–20 words).  
**Read more →** /features/<slug>

- **Icon**: `icons/feature-name.svg` (24–32px)
- **Short microcopy**: "Predictability + Auditability"

(Repeat 3–4 feature blocks: MATRIZ, Guardian, ΛiD, Marketplace)

---

## Interactive preview: Reasoning Lab (callout)
**Try the Reasoning Lab** — A safe demo that shows a reasoning graph in 4 steps: Memory → Attention → Thought → Decision.  
[Try the Safe Demo → /reasoning-lab]

> Microcopy: "Type a short question. Watch steps appear. Click 'Why?' beside any step."

---

## Evidence banner (structured)
**Performance**  
- Claim: p95 reasoning latency < 250ms  
- Proof: `release_artifacts/perf/2025-10-26-matriz-smoke.json` — signed & verified

**Compliance**  
- Claim: Guardian compliance 99.7%  
- Proof: `release_artifacts/audit/guardian-compliance-2025-Q3.pdf`

*(Include 1–3 short metric tiles and link to full evidence repo.)*

---

## Case studies / social proof
(Show 2-3 short case study cards: problem → result → CTA)

- **Example**: "Hospital X reduced diagnostic review time by 87% — read case study → /casestudies/hospital-x"

---

## Footer CTAs
- "Get an enterprise audit pack" — link to contact form  
- "Developers: 5-minute Quickstart" — link to /lukhas.dev

---

## Accessibility & assistive note
If the user has Assistive Mode enabled, deliver `homepage.assistive.md` (shorter sentences; step-by-step demo instructions; explicit evidence bullets). See `branding/ASSISTIVE_CHECKLIST.md` for authoring rules.

---

### Author guidance / placeholders
- Replace `{{PAGE_TITLE}}`, `{{SEO_TITLE}}`, `{{SEO_DESC}}` with live values.  
- Replace tile metrics with `evidence_links`. Each numeric claim in the body must be listed in `evidence_links` and have `claims_approval: true` if the claim is production-level.  
- Images: store at `branding/websites/<domain>/images/` with descriptive alt text. Example: `alt="Visualization of MATRIZ reasoning graph step: Memory"`.  
- If a feature uses a particle canvas, include a short text alternative paragraph under the hero describing the experience.

---

## Assistive homepage (brief example stub)

**File suggestion:** `branding/websites/lukhas.ai/homepage.assistive.md`  
(Already provided earlier; keep it concise and step-driven.)

---

## B. Microcopy examples for multiple domains (to paste quickly)
- **lukhas.ai** hero:  
  - H1: "Where digital minds learn to explain themselves."  
  - CTA: "Try a Safe Demo" / "Explore the Reasoning Lab"
- **lukhas.dev** hero:  
  - H1: "Build reasoning chains in 5 minutes."  
  - CTA: "Start Quickstart" / "Open SDK"
- **lukhas.com** hero:  
  - H1: "Transparent AI, trusted at scale."  
  - CTA: "Request Enterprise Audit" / "Download Audit Pack"

---

## Reviewer checklist for Homepage PR
- [ ] Front-matter present and valid (CI will check).  
- [ ] All numeric/performance claims have `evidence_links` and `claims_approval:true` or guarded conditional text.  
- [ ] Assistive variant exists for critical pages.  
- [ ] Alt text present for images and description for particle canvas.  
- [ ] Tone ratios roughly match domain (audit in content review).  
- [ ] SEO meta and hreflang set properly.

---

## B — Case Study template (canonical)

**File suggestion:** `branding/templates/case-study.md`  
(Authors will copy to `branding/websites/<domain>/casestudies/<slug>.md`)

```markdown
---
title: "{{CASE_TITLE}}"                 # e.g. "Hospital X: Faster Diagnostics with MATRIZ"
domain: "lukhas.ai"                    # domain under which published
owner: "@gonzalo"
audience: "enterprise"
tone:
  poetic: 0.20
  user_friendly: 0.50
  academic: 0.30
canonical: true
source: "branding/templates/case-study.md"
evidence_links:
  - "release_artifacts/case-studies/hospital-x/metrics.json"
claims_verified_by:
  - "@web-architect"
claims_verified_date: "2025-11-06"
claims_approval: false
seo:
  title: "Hospital X Case Study — LUKHAS"
  description: "How Hospital X used MΛTRIZ to reduce diagnostic review time by 87%."
tags: ["casestudy","enterprise","healthcare"]
customer:
  name: "Hospital X"
  industry: "Healthcare"
  anonymized: true
legal_consent: true                      # required: legal sign-off
---
# {{CASE_TITLE}}

**One-line summary / impact**  
Short sentence that gives the headline metric (e.g., "Reduced diagnostic review time by 87% while increasing accuracy by 12%.").

---

## Problem
Short paragraph (2–4 sentences) describing the customer's challenge in plain language. Avoid jargon where possible.

---

## Approach (MATRIZ + integration)
- **What we deployed:** brief bulleted list (MATRIZ pipeline + Guardian policies + memory folds etc.).  
- **How it was integrated:** short steps (1-3) describing integration architecture: data flow, authentication (ΛiD), privacy safeguards.

**Optional:** include a small architecture diagram (SVG) with alt text: "Architecture: client → Lukhas Cloud (MATRIZ) → Reasoning Lab → outputs".

---

## Results (measurable)
| Metric | Before | After | Proof |
|--------|--------:|------:|------|
| Diagnostic review time | 6 hours | 0.78 hours | `release_artifacts/case-studies/hospital-x/metrics.json` |
| Accuracy improvement | 72% | 84% | same artifact |

**Narrative:** 1–3 short sentences interpreting the numbers.

---

## Evidence
- **Primary evidence file:** `release_artifacts/case-studies/hospital-x/metrics.json` (hash: `<sha256>`)  
- **Audit:** `release_artifacts/case-studies/hospital-x/audit-report.pdf` (signed)  
- **Quote:** "LUKHAS helped us turn weeks into hours." — Dr. Name (consent on file)

---

## Technical appendix (toggle / collapsible)
- Brief architecture notes, data retention, security (links to docs).  
- Link: "Full developer appendix → /docs/web/..."  

---

## Legal & permissions
- Consent: `legal_consent: true` (front-matter required). Attach signed release in `release_artifacts/`.  
- PII: if any PII used, include DPA entry and proof of anonymization.

---

## Author & Reviewer checklist (case study)
- [ ] Legal consent documented in `release_artifacts`.  
- [ ] All metrics linked to evidence files.  
- [ ] Core technical appendix links included.  
- [ ] Assistive variant created if this is part of major homepage or marketing funnel.  
- [ ] Customer-identifying info reviewed by legal.

---

## How to use / quick steps

1. Copy `branding/templates/homepage.md` → `branding/websites/lukhas.ai/homepage.md`  
2. Replace placeholders and add images under `branding/websites/lukhas.ai/images/`  
3. Add `homepage.assistive.md` for the assistive variant (or declare `variants.assistive`)  
4. Run local validators:
   ```bash
   python3 tools/branding_vocab_lint.py
   python3 tools/assistive_validate.py
````

5. Open PR; ensure `claims_approval` is set to `true` only after legal & web-architect sign-off.

---

## Final notes (T4-style)

* **Be brutal with evidence.** Any headline metric on a homepage or case study must have a direct evidence file; no exceptions. If evidence is internal, publish a redacted artifact or an executive summary signed by engineering.
* **Keep the assistive variant human-written.** Automation can generate drafts, but a human editor must review them. The reading-grade rule is not an arbitrary constraint — it guarantees accessibility.
* **Don’t overload homepages with technical walls.** Use links and progressive disclosure. Make the homepage a funnel, not a dump.

---
