# LUKHAS Branding Templates

> **📋 Content Templates for Multi-Domain LUKHAS Ecosystem**

**Last Updated**: 2025-11-06
**Status**: Active - Canonical Templates

---

## Overview

This directory contains canonical markdown templates for creating consistent, accessible, and evidence-backed content across all LUKHAS web properties.

---

## Available Templates

### 1. Product Templates

**File**: [PRODUCT_TEMPLATES.md](PRODUCT_TEMPLATES.md)

**Contains**:
- **Reasoning Lab Page Template** - Interactive demo page for MΛTRIZ reasoning
- **Product Page Template** - Standard product overview page
- **Quickstart Template** - 5-minute developer quickstart guide

**Use for**:
- New product launches
- Feature pages
- Developer onboarding guides
- Interactive demos

---

### 2. Homepage & Case Study Templates

**File**: [HOMEPAGE_CASESTUDY_TEMPLATES.md](HOMEPAGE_CASESTUDY_TEMPLATES.md)

**Contains**:
- **Homepage Template** - Canonical homepage structure with evidence requirements
- **Case Study Template** - Customer success story template with legal compliance

**Use for**:
- Domain homepages (lukhas.ai, lukhas.dev, etc.)
- Customer case studies
- Success stories
- Enterprise testimonials

---

### 3. Assistive Mode Implementation

**File**: [../design/ASSISTIVE_MODE_IMPLEMENTATION.md](../design/ASSISTIVE_MODE_IMPLEMENTATION.md)

**Contains**:
- Assistive Mode content checklist
- CI validation tools (`tools/assistive_validate.py`)
- GitHub Actions workflow
- Sample assistive homepage
- Design tokens (dark/light/assistive themes)

**Use for**:
- Creating accessible content variants
- Implementing assistive mode for critical pages
- Setting up automated accessibility validation

---

## How to Use Templates

### Step 1: Copy Template

```bash
# For a product page
cp branding/templates/PRODUCT_TEMPLATES.md branding/websites/lukhas.ai/my-product.md
```

### Step 2: Replace Placeholders

Templates use placeholder syntax:
- `{{PRODUCT_NAME}}` - Replace with actual product name
- `{{PAGE_TITLE}}` - Replace with page title
- `{{SEO_DESC}}` - Replace with SEO description
- etc.

### Step 3: Add Front Matter

Ensure YAML front matter is complete:

```yaml
---
title: "Your Product Name"
domain: "lukhas.ai"           # Target domain
owner: "@your-handle"
audience: "general|developers|enterprise"
tone:
  poetic: 0.25
  user_friendly: 0.45
  academic: 0.30
canonical: true
evidence_links:
  - "release_artifacts/..."   # Required for claims
claims_approval: false        # Must be true for production
---
```

### Step 4: Create Assistive Variant

For critical pages (homepage, pricing, checkout, identity flows):

```bash
cp your-page.md your-page.assistive.md
# Edit assistive variant:
# - Shorter sentences (FK grade ≤ 8)
# - Clear step-by-step instructions
# - Explicit CTAs
# - No metaphors
```

### Step 5: Validate

Run local validation:

```bash
python3 tools/branding_vocab_lint.py
python3 tools/assistive_validate.py
```

### Step 6: Submit PR

- Follow checklist in template
- Request reviews from `@content-lead`, `@web-architect`
- Ensure CI passes

---

## Template Requirements

### All Templates Must Include:

1. **YAML Front Matter**
   - Complete metadata
   - Tone distribution matching domain config
   - Evidence links for all claims

2. **Accessibility**
   - Alt text for all images
   - Assistive variants for critical pages
   - Keyboard navigation support

3. **Evidence**
   - Claims backed by `evidence_links`
   - `claims_approval: true` for production claims
   - Signed artifacts in `release_artifacts/`

4. **Tone Compliance**
   - Match domain tone ratios (see [tone/configs/](../tone/configs/))
   - Use approved vocabulary
   - Follow 3-layer tone system

---

## Domain-Specific Tone Ratios

Reference these when setting `tone:` in front matter:

| Domain | Poetic | User-Friendly | Academic |
|--------|--------|---------------|----------|
| lukhas.ai | 35% | 45% | 20% |
| lukhas.id | 20% | 40% | 40% |
| lukhas.dev | 15% | 25% | 60% |
| lukhas.store | 30% | 50% | 20% |
| lukhas.com | 15% | 40% | 45% |

See [config/domain_registry.yaml](../config/domain_registry.yaml) for complete list.

---

## Validation Tools

### Vocabulary Linter

```bash
python3 tools/branding_vocab_lint.py
```

Checks:
- Forbidden terms (e.g., "production-ready" without approval)
- Brand consistency (LUKHAS AI vs LUKHAS PWM)
- Vocabulary family usage

### Assistive Validator

```bash
python3 tools/assistive_validate.py
```

Checks:
- Assistive variants exist for critical pages
- Flesch-Kincaid grade ≤ 8
- Front matter compliance

---

## CI Integration

Templates are automatically validated in CI:

**Workflow**: `.github/workflows/assistive-validate.yml`

**Runs on**:
- Pull requests
- Weekly schedule (Mondays)

**Checks**:
- Vocabulary compliance
- Assistive mode presence
- Readability scores
- Evidence links validity

---

## Quick Reference

### Critical Pages Requiring Assistive Variants

1. Homepage (`homepage.md`)
2. Pricing (`pricing.md`)
3. Reasoning Lab (`reasoning_lab.md`)
4. Checkout (`checkout.md`)
5. Identity Flows (`identity_flows.md`)

### Evidence Requirements

- All numeric claims must have `evidence_links`
- Evidence files stored in `release_artifacts/`
- Claims require `claims_approval: true` for production
- Legal consent required for case studies

### Tone Distribution Quick Guide

- **High Poetic** (30-40%): lukhas.ai, lukhas.store
- **High Academic** (40-60%): lukhas.dev, lukhas.id, lukhas.com
- **Balanced**: Most domains use 40-50% user-friendly as base

---

## Resources

- **Main Branding Guide**: [../BRAND_GUIDELINES.md](../BRAND_GUIDELINES.md)
- **Tone System**: [../tone/LUKHAS_3_LAYER_TONE_SYSTEM.md](../tone/LUKHAS_3_LAYER_TONE_SYSTEM.md)
- **Domain Registry**: [../config/domain_registry.yaml](../config/domain_registry.yaml)
- **Design System**: [../design/](../design/)
- **Navigation Hub**: [../README.md](../README.md)

---

## Questions?

- **Content Questions**: content@lukhas.ai
- **Template Issues**: brand@lukhas.ai
- **Technical Support**: dev@lukhas.ai

---

**🎯 Remember**: Templates are starting points. Always customize for your specific domain, audience, and use case while maintaining brand consistency.
