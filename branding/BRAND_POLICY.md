# Brand Policy — Lukhas / MATRIZ

## Names

### Product Name (MΛTRIZ)
- **Display**: **MΛTRIZ** (Λ replaces first "A").
- **Plain**: **Matriz** (paragraphs, SEO, a11y, alt).
- **Slug**: **/matriz**
- **Legacy codename**: **MATADA** — internal only (schema/file names may keep `matada`).

### Company Name
- **Display**: **LUKHΛS** (Λ replaces the first "A")
- **Plain**: **Lukhas** (paragraphs, SEO, a11y, alt)
- **Λ Usage**: Display-only (logos/hero/wordmarks). Not allowed in URLs, alt text, body, or metadata.
- **A11y**: When Λ appears in display text, include aria-label="Lukhas".

## Λ Usage
- **Allowed**: logos, hero H1, wordmarks, promo lockups (SVG preferred).
- **Not allowed**: URLs, alt text, body copy, metadata.
- **A11y**: When Λ appears in text, include `aria-label` with plain name.

## Tone (Three-Layer)
- **Poetic** ≤ 40 words, no promises.
- **Technical** precise, factual, cite limits/assumptions.
- **Plain** grade 6–8, outcomes not implementation.

## OpenAI Alignment
- No implied endorsement. Factual references only.
- Avoid hype/superlatives; show uncertainty and limits.

## Enforcement Levels

### Blocking Rules (Build Failures)
These violations **fail builds** and **block deployments** (exit code 1):

**Lambda (Λ) Violations:**
- Λ in URLs or file paths
- Λ in alt text or aria-labels
- Missing aria-label when Λ appears in display text
- SVG text elements containing Λ (must use path)

**Deprecated Terms:**
- Public use of "MATADA" (legacy codename)
- Incorrect product name format

**Critical Banned Words:**
- "guaranteed", "flawless", "perfect"
- "zero-risk", "unbreakable"
- "magical", "miracle"

**Accessibility Violations:**
- Missing alt text on images
- Contrast ratios below 4.5:1
- Motion without prefers-reduced-motion support

### Human Review Required (Non-Blocking)
These claims **flag for review** but **don't block builds** (exit code 0):

**Performance Claims:**
- "revolutionary", "groundbreaking", "game-changing"
- "breakthrough", "cutting-edge", "world-class"
- "industry-leading", "state-of-the-art", "unparalleled"

**Market Positioning:**
- "first", "only", "best", "leading"
- "dominant", "superior"

**Technical Achievements:**
- "advanced", "sophisticated", "powerful"
- "robust", "scalable", "unlimited"

### Brand Decision Record (BDR) Process
When human review flags claims:

1. **Document Evidence**: Create BDR with supporting data
2. **Cite Sources**: Include benchmarks, studies, user feedback
3. **Add Footnotes**: Qualify claims with specific context
4. **Get Approval**: Minimum 2 stakeholder sign-offs
5. **Monitor Impact**: Track metrics post-deployment

**BDR Template**: `/branding/decisions/BDR-TEMPLATE.md`

### Policy Commands

```bash
# Blocking checks (fails CI if violations found)
make policy          # All blocking rules
make policy-brand    # Brand compliance only

# Non-blocking review (flags but doesn't fail)
make policy-review   # Claims requiring human review
```

### Legacy Enforcement
- **CI Integration**: Blocking rules run in GitHub Actions
- **PR Requirements**: Brand checklist must be completed
- **Weekly Scans**: Automated compliance monitoring
- **Brand Council**: Weekly approval for new Λ usage