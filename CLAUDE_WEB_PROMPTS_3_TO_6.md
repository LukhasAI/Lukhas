# Claude Code Web Prompts 3-6: Branding Governance Implementation

**Status**: Prompts 1-2 completed (#1102, #1104)
**Remaining**: Prompts 3-6 (Evidence Templates, SEO, Content CI, Analytics)

---

## LUKHAS Policies Header (Include at Top of Each Prompt)

```markdown
# LUKHAS Context & Policies

## Repository
- **Repo**: https://github.com/LukhasAI/Lukhas
- **Main Branch**: `main`
- **Working Directory**: `/Users/agi_dev/LOCAL-REPOS/Lukhas`

## Critical Policies

### Commit Standards (T4 Minimal)
- **Format**: `<type>(<scope>): <imperative subject ≤72>`
- **Types**: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security
- **Scopes**: core|matriz|identity|memory|governance|branding|tools|docs|ci
- **Body**: Problem/Solution/Impact bullets for non-trivial changes
- **Trailers**: Include `Closes:`, `Security-Impact:`, `LLM:` when relevant
- **Examples**:
  - ✅ `feat(branding): add evidence page template system with bidirectional linking`
  - ✅ `docs(governance): add SEO technical hygiene implementation guide`
  - ❌ `🎯 BREAKTHROUGH: Evidence System Complete!!!`

### Lane-Based Import Rules
- `lukhas/` ← can import from `core/`, `matriz/`, `universal_language/`
- `candidate/` ← can import from `core/`, `matriz/` ONLY (NO lukhas imports)
- Validate with: `make lane-guard`

### Testing Standards
- **Coverage Target**: 75%+ for production promotion
- **Test Markers**: unit, integration, contract, smoke, tier1
- **Exclusions**: Always exclude `.git`, `__pycache__`, `.pytest_cache`, `node_modules`, `venv`, `.venv`, `dist`, `build`, `*.egg-info`

### Branding Vocabulary Rules
- ✅ "LUKHAS AI" (never "LUKHAS AGI")
- ✅ "quantum-inspired algorithms" (never "quantum processing")
- ✅ "bio-inspired computing" (never "biological processing")
- ✅ "consciousness simulation" (never "true consciousness" or "sentient AI")
- ✅ "deployment-ready" or "validated production" (never "production-ready" without approval)
- Run: `python3 tools/branding_vocab_lint.py` to validate

### Front-Matter Requirements
All branding markdown files must include:
```yaml
---
title: "Page Title"
domain: lukhas.ai
owner: @content-lead
audience: [developers, enterprise, researchers]
tone:
  poetic: 0.25
  user_friendly: 0.50
  academic: 0.25
canonical: https://lukhas.ai/page-path
source: branding
last_reviewed: "2025-11-06"
evidence_links:
  - 'release_artifacts/evidence-artifact.json'
claims_approval: true
claims_verified_by: ['@web-architect', '@legal']
seo:
  description: "150-160 character meta description"
  keywords: ["consciousness AI", "MATRIZ", "symbolic reasoning"]
  og_image: /assets/og-images/domain-page.png
---
```

### Evidence & Claims Policy
- All numeric/operational claims MUST have `evidence_links` in front-matter
- Claims require `claims_approval: true` after review by @web-architect and @legal
- Evidence artifacts stored in `release_artifacts/` with JSON metadata
- Generate claims registry: `python3 tools/generate_claims_registry.py`
- Validate claims: `python3 tools/validate_claims.py`

### GitHub Workflow
- Create feature branch from `main`
- Push changes and open PR
- PR title format: `<type>(<scope>): <description>`
- Request reviewers: @web-architect, @content-lead, @legal (for claims)
- All CI checks must pass before merge
```

---

## Prompt 3: Evidence Page Template System (45 min, P0, GAPS A1)

```markdown
# Task: Evidence Page Template System for LUKHAS Branding

[PASTE LUKHAS POLICIES HEADER HERE]

## Objective
Create a standardized evidence page template system that provides structured, auditable backing for all numeric and operational claims across LUKHAS branding content.

## Background
- We have claims registry tools (PR #1104) that extract and validate claims
- We have 6 evidence artifacts (PR #1102) providing JSON/markdown evidence
- Missing: Bidirectional linking between claims and evidence pages
- Gap: A1 from GAPS_ANALYSIS.md

## Deliverables

### 1. Evidence Page Template (`branding/templates/evidence_page.md`)

Create a comprehensive template with:

**Front-Matter Requirements**:
```yaml
---
evidence_id: "matriz-p95-latency-2025-q3"
claim_type: "performance"  # performance|security|compliance|usage|accuracy
claim_statement: "<250ms p95 reasoning latency in MATRIZ cognitive engine"
domains: [lukhas.ai, lukhas.eu]
pages_using_claim:
  - 'branding/websites/lukhas.ai/homepage.md'
  - 'branding/websites/lukhas.eu/homepage_matriz_ready.md'
methodology:
  test_environment: "Production-like staging with 50K concurrent users"
  data_collection: "7-day continuous monitoring Oct 15-22, 2025"
  tools: ["Prometheus", "Grafana", "custom latency instrumentation"]
  sample_size: "3,042,156 reasoning operations"
artifacts:
  - path: 'release_artifacts/matriz-p95-latency-2025-q3.json'
    type: json
    hash: sha256-abc123...
  - path: 'release_artifacts/matriz-perf-dashboard-2025-q3.png'
    type: image
    hash: sha256-def456...
verified_by: ['@web-architect', '@qa-lead']
verified_date: "2025-10-23"
legal_approved: true
legal_approved_by: '@legal'
legal_approved_date: "2025-10-24"
next_review: "2026-01-15"
---
```

**Body Structure**:
```markdown
# Evidence: [Claim Statement]

## Claim Summary
- **Statement**: [Full claim text]
- **Type**: [performance|security|compliance|usage|accuracy]
- **Domains**: [List of domains using this claim]
- **Status**: ✅ Verified | ⚠️ Under Review | 🔴 Retracted

## Methodology

### Test Environment
[Description of production-like staging environment]

### Data Collection
[Time period, sample size, monitoring approach]

### Tools & Instrumentation
- Tool 1: [Purpose and configuration]
- Tool 2: [Purpose and configuration]

## Results

### Key Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| p50 latency | 87ms | <100ms | ✅ Pass |
| p95 latency | 243ms | <250ms | ✅ Pass |
| p99 latency | 312ms | <500ms | ✅ Pass |

### Statistical Confidence
- Sample size: [N operations]
- Confidence level: 95%
- Margin of error: ±X ms

## Artifacts

### Primary Evidence
1. **[artifact-name.json]** - Raw performance data
   - Path: `release_artifacts/...`
   - Hash: `sha256-...`
   - [Download link]

2. **[artifact-name.png]** - Dashboard screenshot
   - Path: `release_artifacts/...`
   - Hash: `sha256-...`
   - [View image]

### Third-Party Validation
- Auditor: [Company name]
- Report: [Link to audit PDF metadata]
- Date: [Audit date]

## Pages Using This Claim
- [lukhas.ai/homepage.md](../../websites/lukhas.ai/homepage.md#L42) - "MATRIZ delivers <250ms p95 reasoning"
- [lukhas.eu/homepage.md](../../websites/lukhas.eu/homepage_matriz_ready.md#L67) - "Sub-250ms production latency"

## Verification History
| Date | Verifier | Action | Notes |
|------|----------|--------|-------|
| 2025-10-23 | @web-architect | Initial verification | All targets met |
| 2025-10-24 | @legal | Legal approval | Wording approved for public use |

## Next Review
- **Scheduled**: 2026-01-15
- **Trigger**: Major MATRIZ version update or performance regression
- **Owner**: @qa-lead

---

**Last Updated**: 2025-11-06
**Evidence ID**: [evidence_id]
**Status**: ✅ Verified and Approved
```

### 2. Evidence Page Generator (`tools/generate_evidence_page.py`)

Create Python script that:

```python
#!/usr/bin/env python3
"""
tools/generate_evidence_page.py

Generates evidence page stubs from claims_registry.json with:
- Prefilled front-matter from claims data
- Skeleton methodology sections
- Links to artifact files
- Bidirectional page links
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

def generate_evidence_pages():
    """Generate evidence page stubs for all claims in registry."""

    registry_path = Path("branding/governance/claims_registry.json")
    if not registry_path.exists():
        print("Run 'make claims-registry' first to generate claims_registry.json")
        return

    registry = json.loads(registry_path.read_text())
    evidence_dir = Path("release_artifacts/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    template_path = Path("branding/templates/evidence_page.md")
    template = template_path.read_text()

    for claim in registry.get("claims", []):
        evidence_id = generate_evidence_id(claim)
        output_path = evidence_dir / f"{evidence_id}.md"

        if output_path.exists():
            print(f"⏭️  Skipping existing: {output_path}")
            continue

        # Prefill template with claim data
        page_content = prefill_template(template, claim, evidence_id)
        output_path.write_text(page_content)
        print(f"✅ Created: {output_path}")

def generate_evidence_id(claim):
    """Generate evidence ID from claim data."""
    # Extract domain and claim type
    domain = claim.get("domain", "unknown").replace(".", "-")
    claims_text = "-".join(claim.get("claims_found", [])[:2])
    # Sanitize for filename
    evidence_id = f"{domain}-{claims_text}-2025-q4"
    return evidence_id.lower().replace("%", "pct").replace("<", "lt")[:60]

def prefill_template(template, claim, evidence_id):
    """Prefill template with claim data."""
    # Replace placeholders with actual data
    # This is a simplified version - expand with full logic
    prefilled = template.replace("[evidence_id]", evidence_id)
    prefilled = prefilled.replace("[claim_statement]", claim.get("claims_found", [""])[0])
    prefilled = prefilled.replace("[domains]", str(claim.get("domain", "")))
    return prefilled

if __name__ == "__main__":
    generate_evidence_pages()
```

**Features**:
- Reads `branding/governance/claims_registry.json`
- Generates evidence page stub for each unique claim
- Prefills front-matter with claim metadata
- Creates bidirectional links to pages using claim
- Skips existing evidence pages (idempotent)

### 3. Update Makefile

Add targets:
```makefile
evidence-pages:  ## Generate evidence page stubs from claims registry
	python3 tools/generate_evidence_page.py

evidence-validate:  ## Validate evidence pages have required fields
	python3 tools/validate_evidence_pages.py
```

### 4. Documentation (`branding/governance/tools/EVIDENCE_SYSTEM.md`)

Create comprehensive guide covering:
- Evidence page template structure
- How to fill out methodology sections
- Artifact file naming conventions
- Third-party audit integration
- Legal approval workflow
- Evidence page lifecycle (creation → verification → approval → review)

## Testing & Validation

1. **Generate test evidence pages**:
   ```bash
   python3 tools/generate_claims_registry.py
   python3 tools/generate_evidence_page.py
   ```

2. **Verify output**:
   - Check `release_artifacts/evidence/*.md` created
   - Validate front-matter completeness
   - Confirm bidirectional links work

3. **Run vocabulary and front-matter linting**:
   ```bash
   python3 tools/branding_vocab_lint.py
   python3 tools/front_matter_lint.py
   ```

## Success Criteria

- ✅ Evidence page template created with all required sections
- ✅ Generator script creates valid evidence pages from claims registry
- ✅ Bidirectional linking between claims and evidence established
- ✅ Makefile targets added and documented
- ✅ EVIDENCE_SYSTEM.md guide created
- ✅ All vocabulary and front-matter checks pass
- ✅ PR created with 4-6 files, reviewers assigned

## PR Details

**Branch**: `feat/evidence-page-template-system`
**Title**: `feat(branding): add evidence page template system with bidirectional linking`
**Reviewers**: @web-architect, @content-lead, @legal

**PR Body**:
```markdown
## Summary
Implements evidence page template system (GAPS A1) to provide structured, auditable backing for all numeric and operational claims.

## Problem
- Claims registry (PR #1104) validates claims exist, but no standardized evidence documentation
- Evidence artifacts (PR #1102) provide raw data, but lack human-readable methodology
- No bidirectional linking between marketing claims and technical evidence

## Solution
- Evidence page template with methodology, artifacts, verification workflow
- Python generator creates evidence page stubs from claims registry
- Bidirectional links connect claims to evidence pages and back to usage pages

## Impact
- Legal can approve claims with confidence in evidence trail
- Engineers can efficiently document performance/security results
- Content creators can reference verified claims with one-click evidence access

## Files
- `branding/templates/evidence_page.md` - Template with front-matter + body structure
- `tools/generate_evidence_page.py` - Generator script (idempotent)
- `tools/validate_evidence_pages.py` - Validation tool for CI
- `branding/governance/tools/EVIDENCE_SYSTEM.md` - Complete guide
- `Makefile` - Added `evidence-pages` and `evidence-validate` targets

## Testing
- Generated 6 test evidence pages from claims registry
- All front-matter fields populated correctly
- Bidirectional links validated
- Vocabulary and front-matter linting: PASS

Closes: GAPS A1
```
```

---

## Prompt 4: SEO Technical Hygiene Implementation (60 min, P0, GAPS H19)

```markdown
# Task: SEO Technical Hygiene for LUKHAS Multi-Domain Ecosystem

[PASTE LUKHAS POLICIES HEADER HERE]

## Objective
Implement comprehensive SEO technical infrastructure for 5 LUKHAS domains (lukhas.ai, lukhas.dev, lukhas.com, lukhas.eu, lukhas.app) including schema.org markup, sitemaps, canonical URLs, and hreflang tags.

## Background
- 5 production domains with overlapping content (MATRIZ mentioned on .ai, .eu, .app)
- Risk of duplicate content penalties without proper canonicalization
- No structured data for rich snippets
- Missing: H19 from GAPS_ANALYSIS.md

## Deliverables

### 1. Schema.org Templates (`branding/templates/schema/`)

Create templates for common page types:

**`branding/templates/schema/product_page.json`**:
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{{ product_name }}",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "description": "{{ seo_description }}",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{ rating }}",
    "reviewCount": "{{ review_count }}"
  },
  "provider": {
    "@type": "Organization",
    "name": "LUKHAS AI",
    "url": "https://lukhas.com"
  }
}
```

**`branding/templates/schema/article.json`**:
```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "{{ title }}",
  "description": "{{ seo_description }}",
  "author": {
    "@type": "Organization",
    "name": "LUKHAS AI"
  },
  "publisher": {
    "@type": "Organization",
    "name": "LUKHAS AI",
    "logo": {
      "@type": "ImageObject",
      "url": "https://lukhas.com/assets/logo.png"
    }
  },
  "datePublished": "{{ published_date }}",
  "dateModified": "{{ last_reviewed }}"
}
```

**`branding/templates/schema/organization.json`**:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "LUKHAS AI",
  "url": "https://lukhas.com",
  "logo": "https://lukhas.com/assets/logo.png",
  "sameAs": [
    "https://twitter.com/LukhasAI",
    "https://github.com/LukhasAI",
    "https://linkedin.com/company/lukhas-ai"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "Customer Support",
    "email": "support@lukhas.com"
  }
}
```

### 2. Sitemap Generator (`tools/generate_sitemaps.py`)

Create Python script that:

```python
#!/usr/bin/env python3
"""
tools/generate_sitemaps.py

Generates XML sitemaps for all 5 LUKHAS domains with:
- Priority and changefreq based on page type
- lastmod from front-matter last_reviewed
- Cross-domain alternate links (hreflang)
"""
import yaml
import re
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

DOMAINS = {
    "lukhas.ai": "https://lukhas.ai",
    "lukhas.dev": "https://lukhas.dev",
    "lukhas.com": "https://lukhas.com",
    "lukhas.eu": "https://lukhas.eu",
    "lukhas.app": "https://lukhas.app"
}

def generate_sitemaps():
    """Generate sitemap.xml for each domain."""

    for domain_name, base_url in DOMAINS.items():
        pages = collect_pages(domain_name)
        sitemap_xml = build_sitemap(pages, base_url)

        output_path = Path(f"branding/websites/{domain_name}/sitemap.xml")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(sitemap_xml)
        print(f"✅ Generated: {output_path} ({len(pages)} pages)")

def collect_pages(domain_name):
    """Collect all markdown pages for domain."""
    domain_dir = Path(f"branding/websites/{domain_name}")
    if not domain_dir.exists():
        return []

    pages = []
    for md_file in domain_dir.rglob("*.md"):
        front_matter = read_front_matter(md_file)
        if not front_matter:
            continue

        # Extract SEO metadata
        canonical = front_matter.get("canonical", "")
        last_reviewed = front_matter.get("last_reviewed", "")
        priority = get_priority(md_file.name)
        changefreq = get_changefreq(md_file.name)

        pages.append({
            "loc": canonical,
            "lastmod": last_reviewed,
            "priority": priority,
            "changefreq": changefreq
        })

    return pages

def read_front_matter(path):
    """Read YAML front-matter from markdown file."""
    txt = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"YAML parse error in {path}: {e}")
        return {}

def get_priority(filename):
    """Determine priority based on page type."""
    if "homepage" in filename:
        return "1.0"
    elif "product" in filename or "feature" in filename:
        return "0.8"
    elif "research" in filename or "blog" in filename:
        return "0.6"
    else:
        return "0.5"

def get_changefreq(filename):
    """Determine change frequency based on page type."""
    if "homepage" in filename:
        return "weekly"
    elif "blog" in filename:
        return "monthly"
    else:
        return "yearly"

def build_sitemap(pages, base_url):
    """Build XML sitemap from page data."""
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url_elem = SubElement(urlset, "url")
        SubElement(url_elem, "loc").text = page["loc"]
        if page["lastmod"]:
            SubElement(url_elem, "lastmod").text = page["lastmod"]
        SubElement(url_elem, "priority").text = page["priority"]
        SubElement(url_elem, "changefreq").text = page["changefreq"]

    # Pretty print XML
    rough_string = tostring(urlset, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    generate_sitemaps()
```

### 3. Canonical URL Mapping (`branding/seo/canonical_map.yaml`)

Create canonical URL mapping for duplicate content:

```yaml
# Canonical URL mapping for cross-domain duplicate content
# Format: [duplicate_url] → [canonical_url]

canonical_mappings:
  # MATRIZ cognitive engine mentioned on 3 domains
  - duplicates:
      - https://lukhas.ai/matriz
      - https://lukhas.eu/matriz
      - https://lukhas.app/matriz
    canonical: https://lukhas.ai/matriz

  # Identity/authentication on 2 domains
  - duplicates:
      - https://lukhas.com/identity
      - https://lukhas.dev/identity
    canonical: https://lukhas.com/identity

  # Developer documentation
  - duplicates:
      - https://lukhas.ai/docs
      - https://lukhas.dev/docs
    canonical: https://lukhas.dev/docs

hreflang_groups:
  # Multi-language content groups
  - canonical: https://lukhas.com/about
    alternates:
      - url: https://lukhas.eu/about
        lang: en-EU
      - url: https://lukhas.com/about
        lang: en-US
```

### 4. SEO Validator (`tools/validate_seo.py`)

Create validation script:

```python
#!/usr/bin/env python3
"""
tools/validate_seo.py

Validates SEO compliance:
- All pages have canonical URLs
- Meta descriptions 150-160 characters
- Title tags 50-60 characters
- No duplicate canonical URLs across domains
- Schema.org markup present
"""
import yaml
import re
from pathlib import Path

def validate_seo():
    """Run SEO validation checks."""
    errors = []
    warnings = []

    # Check 1: All pages have canonical URLs
    for md_file in Path("branding/websites").rglob("*.md"):
        fm = read_front_matter(md_file)
        if not fm:
            continue

        canonical = fm.get("canonical", "")
        if not canonical:
            errors.append(f"{md_file}: Missing canonical URL")

        # Check 2: Meta description length
        seo = fm.get("seo", {})
        description = seo.get("description", "")
        if description:
            desc_len = len(description)
            if desc_len < 150 or desc_len > 160:
                warnings.append(f"{md_file}: Meta description {desc_len} chars (target: 150-160)")
        else:
            errors.append(f"{md_file}: Missing SEO meta description")

        # Check 3: Title length
        title = fm.get("title", "")
        if title:
            title_len = len(title)
            if title_len < 50 or title_len > 60:
                warnings.append(f"{md_file}: Title {title_len} chars (target: 50-60)")

    # Check 4: Duplicate canonical URLs
    canonical_urls = {}
    for md_file in Path("branding/websites").rglob("*.md"):
        fm = read_front_matter(md_file)
        if not fm:
            continue
        canonical = fm.get("canonical", "")
        if canonical:
            if canonical in canonical_urls:
                errors.append(f"Duplicate canonical: {canonical} in {md_file} and {canonical_urls[canonical]}")
            else:
                canonical_urls[canonical] = md_file

    # Report results
    if errors:
        print("❌ SEO Validation Errors:")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("⚠️  SEO Validation Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print(f"✅ SEO validation passed ({len(canonical_urls)} pages checked)")
        return 0
    else:
        return 1

def read_front_matter(path):
    """Read YAML front-matter from markdown file."""
    txt = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}

if __name__ == "__main__":
    import sys
    sys.exit(validate_seo())
```

### 5. Update Makefile

```makefile
sitemaps:  ## Generate XML sitemaps for all domains
	python3 tools/generate_sitemaps.py

seo-validate:  ## Validate SEO compliance (canonical URLs, meta descriptions)
	python3 tools/validate_seo.py
```

### 6. Documentation (`branding/governance/SEO_GUIDE.md`)

Create comprehensive guide covering:
- Schema.org markup best practices
- Canonical URL strategy for multi-domain content
- Hreflang implementation for EU vs US content
- Meta description and title optimization
- Sitemap maintenance workflow
- Robots.txt configuration

## Testing & Validation

1. **Generate sitemaps**:
   ```bash
   python3 tools/generate_sitemaps.py
   ```

2. **Validate SEO compliance**:
   ```bash
   python3 tools/validate_seo.py
   ```

3. **Check schema.org markup**:
   - Use Google Rich Results Test
   - Validate JSON-LD syntax

4. **Verify canonical URLs**:
   - No duplicate canonicals
   - All cross-domain duplicates properly mapped

## Success Criteria

- ✅ Schema.org templates created for 3+ page types
- ✅ Sitemap generator creates valid XML sitemaps for all 5 domains
- ✅ Canonical URL mapping established with hreflang groups
- ✅ SEO validator checks canonical, meta descriptions, title lengths
- ✅ SEO_GUIDE.md comprehensive documentation created
- ✅ All sitemaps validate with sitemap validators
- ✅ PR created with 10+ files, reviewers assigned

## PR Details

**Branch**: `feat/seo-technical-hygiene`
**Title**: `feat(branding): add SEO technical hygiene for multi-domain ecosystem`
**Reviewers**: @web-architect, @content-lead

**PR Body**:
```markdown
## Summary
Implements comprehensive SEO technical infrastructure (GAPS H19) for 5 LUKHAS domains including schema.org markup, sitemaps, canonical URLs, and hreflang tags.

## Problem
- 5 domains with overlapping content risk duplicate content penalties
- No structured data for rich snippets in search results
- Missing sitemaps and canonical URL strategy
- No automated SEO validation in CI

## Solution
- Schema.org JSON-LD templates for products, articles, organization
- Sitemap generator creates XML sitemaps from front-matter metadata
- Canonical URL mapping with hreflang for cross-domain duplicates
- SEO validator checks canonical URLs, meta descriptions, title lengths

## Impact
- Improved search rankings with rich snippets (schema.org markup)
- Eliminated duplicate content penalties with proper canonicalization
- Automated SEO hygiene in CI prevents regressions
- Comprehensive SEO guide for content creators

## Files
- `branding/templates/schema/*.json` - Schema.org templates (3 files)
- `tools/generate_sitemaps.py` - Sitemap generator for 5 domains
- `tools/validate_seo.py` - SEO compliance validator
- `branding/seo/canonical_map.yaml` - Cross-domain canonical mapping
- `branding/governance/SEO_GUIDE.md` - Complete SEO guide
- `Makefile` - Added `sitemaps` and `seo-validate` targets

## Testing
- Generated sitemaps for all 5 domains (27 pages total)
- SEO validation: PASS (0 errors, 3 warnings on title length)
- Schema.org markup validated with Google Rich Results Test
- Canonical URL mapping covers 8 duplicate content groups

Closes: GAPS H19
```
```

---

## Prompt 5: Content CI Workflow (60 min, P0, GAPS D10)

```markdown
# Task: Content Linting CI Workflow for LUKHAS Branding

[PASTE LUKHAS POLICIES HEADER HERE]

## Objective
Implement comprehensive GitHub Actions CI workflow for automated branding content validation including vocabulary linting, front-matter validation, evidence checking, and visual regression testing.

## Background
- We have standalone tools: `branding_vocab_lint.py`, `front_matter_lint.py`, `evidence_check.py`, `validate_claims.py`
- Missing: Automated CI execution on PRs and scheduled runs
- Need: Visual regression testing for branding pages
- Gap: D10 from GAPS_ANALYSIS.md

## Deliverables

### 1. Content Linting Workflow (`.github/workflows/content-lint.yml`)

Create comprehensive GitHub Actions workflow:

```yaml
name: Branding Content Lint & Governance

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'branding/**/*.md'
      - 'tools/*lint*.py'
      - 'tools/*validate*.py'
      - 'tools/generate_*.py'
  push:
    branches: [main]
    paths:
      - 'branding/**/*.md'
  schedule:
    - cron: '0 9 * * 1'  # Weekly Monday 9am UTC
  workflow_dispatch:  # Manual trigger

jobs:
  vocabulary-lint:
    name: Vocabulary Compliance
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run vocabulary linter
        run: |
          python3 tools/branding_vocab_lint.py
        continue-on-error: false

  front-matter-lint:
    name: Front-Matter Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Run front-matter linter
        run: |
          python3 tools/front_matter_lint.py
        continue-on-error: false

  evidence-validation:
    name: Claims & Evidence Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Generate claims registry
        run: |
          python3 tools/generate_claims_registry.py

      - name: Validate claims (non-strict)
        run: |
          python3 tools/validate_claims.py
        continue-on-error: false

      - name: Upload claims registry artifact
        uses: actions/upload-artifact@v4
        with:
          name: claims-registry
          path: branding/governance/claims_registry.json
          retention-days: 30

  seo-validation:
    name: SEO Technical Hygiene
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Validate SEO compliance
        run: |
          python3 tools/validate_seo.py
        continue-on-error: true  # Warnings allowed

  markdown-links:
    name: Broken Link Detection
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install markdown-link-check
        run: npm install -g markdown-link-check

      - name: Check branding links
        run: |
          find branding -name "*.md" -exec markdown-link-check {} \;
        continue-on-error: true

  visual-regression:
    name: Visual Regression Testing
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          npm install -g @chromatic-com/chromatic
          # Or: npm install -g percy

      - name: Build static site preview
        run: |
          # This assumes you have a build script for branding previews
          # Adjust based on your static site generator (Hugo, Jekyll, etc.)
          echo "Building static preview..."
          # npm run build:preview || true

      - name: Run visual regression (Chromatic)
        env:
          CHROMATIC_PROJECT_TOKEN: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
        run: |
          # chromatic --project-token=$CHROMATIC_PROJECT_TOKEN
          echo "Visual regression would run here with Chromatic or Percy"
          echo "Requires CHROMATIC_PROJECT_TOKEN secret in repo settings"
        continue-on-error: true

  evidence-artifacts:
    name: Evidence Artifact Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Validate evidence JSON files
        run: |
          for file in release_artifacts/*.json; do
            echo "Validating $file..."
            python3 -m json.tool "$file" > /dev/null || exit 1
          done

      - name: Check artifact hashes (future)
        run: |
          echo "Artifact signing validation would run here (D9 in progress)"
          # python3 tools/validate_artifact_signatures.py

  summary:
    name: Validation Summary
    runs-on: ubuntu-latest
    needs: [vocabulary-lint, front-matter-lint, evidence-validation, seo-validation]
    if: always()
    steps:
      - name: Check all jobs passed
        run: |
          echo "Vocabulary: ${{ needs.vocabulary-lint.result }}"
          echo "Front-Matter: ${{ needs.front-matter-lint.result }}"
          echo "Evidence: ${{ needs.evidence-validation.result }}"
          echo "SEO: ${{ needs.seo-validation.result }}"

          if [[ "${{ needs.vocabulary-lint.result }}" == "failure" ]] || \
             [[ "${{ needs.front-matter-lint.result }}" == "failure" ]] || \
             [[ "${{ needs.evidence-validation.result }}" == "failure" ]]; then
            echo "❌ Content validation failed - see job logs above"
            exit 1
          fi

          echo "✅ All critical content validations passed"
```

### 2. PR Required Status Checks (`.github/BRANCH_PROTECTION.md`)

Document branch protection rules:

```markdown
# Branch Protection Configuration

## Required Status Checks for `main` branch

### Critical (Must Pass)
- ✅ `vocabulary-lint` - Vocabulary compliance
- ✅ `front-matter-lint` - Front-matter validation
- ✅ `evidence-validation` - Claims and evidence validation

### Advisory (Can Warn)
- ⚠️ `seo-validation` - SEO technical hygiene
- ⚠️ `markdown-links` - Broken link detection
- ⚠️ `visual-regression` - Visual regression testing

## Configuration Steps

1. Go to GitHub repo → Settings → Branches
2. Edit branch protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Select required checks:
   - `vocabulary-lint`
   - `front-matter-lint`
   - `evidence-validation`
5. Enable "Require branches to be up to date before merging"
6. Save changes

## Manual Override

Repository admins can bypass checks in emergencies using:
- "Override required status checks" permission
- Document override reason in PR comments
```

### 3. Pre-commit Hook (`.github/hooks/pre-commit`)

Create optional local pre-commit hook:

```bash
#!/bin/bash
# .github/hooks/pre-commit
# Install: cp .github/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

echo "Running branding content pre-commit checks..."

# Check if branding files are staged
BRANDING_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '^branding/.*\.md$' || true)

if [ -z "$BRANDING_FILES" ]; then
    echo "No branding files staged, skipping checks"
    exit 0
fi

echo "Checking vocabulary compliance..."
python3 tools/branding_vocab_lint.py || {
    echo "❌ Vocabulary lint failed - fix forbidden terms and try again"
    exit 1
}

echo "Checking front-matter..."
python3 tools/front_matter_lint.py || {
    echo "❌ Front-matter validation failed - check YAML fields"
    exit 1
}

echo "✅ Pre-commit checks passed"
exit 0
```

### 4. Workflow Documentation (`.github/workflows/README.md`)

```markdown
# GitHub Actions Workflows for LUKHAS

## Content Linting Workflow

**File**: `content-lint.yml`
**Triggers**: PRs, pushes to main, weekly schedule, manual

### Jobs

1. **vocabulary-lint**: Forbidden vocabulary detection
2. **front-matter-lint**: YAML front-matter validation
3. **evidence-validation**: Claims registry generation and validation
4. **seo-validation**: SEO hygiene (canonical URLs, meta descriptions)
5. **markdown-links**: Broken link detection
6. **visual-regression**: Visual diff testing (requires Chromatic/Percy setup)
7. **evidence-artifacts**: JSON validation for evidence files

### Local Testing

Run checks locally before pushing:

```bash
# Vocabulary
python3 tools/branding_vocab_lint.py

# Front-matter
python3 tools/front_matter_lint.py

# Claims
python3 tools/generate_claims_registry.py
python3 tools/validate_claims.py

# SEO
python3 tools/validate_seo.py
```

### Secrets Required

- `CHROMATIC_PROJECT_TOKEN` (optional) - For visual regression with Chromatic
- `PERCY_TOKEN` (alternative) - For visual regression with Percy

### Troubleshooting

**Q: Workflow fails on vocabulary-lint**
A: Check `tools/branding_vocab_lint.py` output for forbidden terms, fix content

**Q: Front-matter validation fails**
A: Ensure all required YAML fields present (title, domain, owner, tone, canonical, evidence_links, etc.)

**Q: Evidence validation fails**
A: Add `evidence_links` in front-matter and set `claims_approval: true` after review

**Q: Visual regression not running**
A: Add `CHROMATIC_PROJECT_TOKEN` secret in repo settings → Secrets and variables → Actions
```

### 5. Makefile Integration

```makefile
ci-lint-local:  ## Run CI content linting checks locally
	python3 tools/branding_vocab_lint.py
	python3 tools/front_matter_lint.py
	python3 tools/generate_claims_registry.py
	python3 tools/validate_claims.py
	python3 tools/validate_seo.py

install-pre-commit:  ## Install pre-commit hook for branding checks
	cp .github/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed"
```

## Testing & Validation

1. **Test workflow locally with act**:
   ```bash
   # Install act: brew install act
   act pull_request -j vocabulary-lint
   act pull_request -j evidence-validation
   ```

2. **Create test PR**:
   - Make minor branding change
   - Push and verify all CI jobs run
   - Check job logs for expected behavior

3. **Verify required status checks**:
   - Try merging PR without passing checks (should block)
   - Fix issues and verify checks pass

## Success Criteria

- ✅ `content-lint.yml` workflow created with 7+ jobs
- ✅ Branch protection documentation created
- ✅ Pre-commit hook script created
- ✅ Workflow README with troubleshooting guide
- ✅ Makefile targets for local CI simulation
- ✅ All jobs run successfully on test PR
- ✅ PR created with 5+ files, reviewers assigned

## PR Details

**Branch**: `feat/content-ci-workflow`
**Title**: `ci(branding): add comprehensive content linting workflow`
**Reviewers**: @web-architect, @content-lead

**PR Body**:
```markdown
## Summary
Implements comprehensive GitHub Actions CI workflow (GAPS D10) for automated branding content validation including vocabulary linting, front-matter validation, evidence checking, and visual regression testing.

## Problem
- Manual content validation error-prone and slow
- No automated checks prevent vocabulary violations or missing evidence
- Visual regressions can slip through review
- No standardized CI for branding content

## Solution
- GitHub Actions workflow with 7 validation jobs
- Required status checks enforce critical validations
- Optional pre-commit hook for local validation
- Visual regression testing with Chromatic/Percy integration

## Impact
- Prevents forbidden vocabulary from reaching production
- Enforces evidence backing for all claims automatically
- Catches broken links and SEO issues in CI
- Reduces PR review time with automated checks

## Files
- `.github/workflows/content-lint.yml` - Main CI workflow (7 jobs)
- `.github/BRANCH_PROTECTION.md` - Required status checks documentation
- `.github/hooks/pre-commit` - Local pre-commit validation hook
- `.github/workflows/README.md` - Workflow guide with troubleshooting
- `Makefile` - Added `ci-lint-local` and `install-pre-commit` targets

## Testing
- Tested workflow with act locally: all jobs PASS
- Created test PR with vocabulary violation: correctly blocked
- Fixed violation, workflow passed, PR mergeable
- Pre-commit hook prevents local commits with violations

Closes: GAPS D10
```
```

---

## Prompt 6: Event Taxonomy & Analytics Integration (45 min, P0, GAPS H18)

```markdown
# Task: Privacy-First Event Taxonomy & Analytics for LUKHAS Ecosystem

[PASTE LUKHAS POLICIES HEADER HERE]

## Objective
Design and implement privacy-first analytics event taxonomy for tracking user journeys across 5 LUKHAS domains with GDPR-compliant tracking, KPI dashboard specification, and assistive mode adoption metrics.

## Background
- 5 production domains need unified analytics
- Must be privacy-first (no PII, GDPR-compliant)
- Need to track: quickstart completion, reasoning lab engagement, assistive mode adoption
- Gap: H18 from GAPS_ANALYSIS.md

## Deliverables

### 1. Event Taxonomy Specification (`branding/analytics/event_taxonomy.json`)

Create comprehensive event taxonomy:

```json
{
  "version": "1.0",
  "last_updated": "2025-11-06",
  "events": {
    "page_view": {
      "description": "User views a page",
      "properties": {
        "domain": {"type": "string", "required": true, "example": "lukhas.ai"},
        "path": {"type": "string", "required": true, "example": "/matriz"},
        "variant": {"type": "string", "required": false, "example": "assistive"},
        "referrer": {"type": "string", "required": false, "pii": false}
      },
      "privacy": "No PII collected - domain/path only"
    },
    "quickstart_started": {
      "description": "User begins quickstart tutorial",
      "properties": {
        "domain": {"type": "string", "required": true},
        "language": {"type": "string", "required": true, "example": "python"},
        "quickstart_id": {"type": "string", "required": true, "example": "matriz-hello-world"}
      },
      "kpi": "Quickstart conversion rate"
    },
    "quickstart_completed": {
      "description": "User successfully completes quickstart",
      "properties": {
        "domain": {"type": "string", "required": true},
        "language": {"type": "string", "required": true},
        "quickstart_id": {"type": "string", "required": true},
        "duration_seconds": {"type": "number", "required": false},
        "success": {"type": "boolean", "required": true}
      },
      "kpi": "Quickstart success rate (% completed / started)"
    },
    "reasoning_trace_viewed": {
      "description": "User views reasoning trace in Reasoning Lab",
      "properties": {
        "domain": {"type": "string", "required": true},
        "trace_type": {"type": "string", "required": true, "example": "symbolic_dna"},
        "interaction_depth": {"type": "number", "required": false, "example": 3}
      },
      "kpi": "Reasoning Lab engagement rate"
    },
    "assistive_variant_viewed": {
      "description": "User switches to assistive mode",
      "properties": {
        "domain": {"type": "string", "required": true},
        "page": {"type": "string", "required": true},
        "trigger": {"type": "string", "required": true, "example": "toggle|preference|auto"}
      },
      "kpi": "Assistive mode adoption rate"
    },
    "assistive_audio_played": {
      "description": "User plays audio description in assistive mode",
      "properties": {
        "domain": {"type": "string", "required": true},
        "page": {"type": "string", "required": true},
        "duration_seconds": {"type": "number", "required": false}
      },
      "kpi": "Assistive audio engagement"
    },
    "evidence_artifact_requested": {
      "description": "User clicks evidence link from claim",
      "properties": {
        "domain": {"type": "string", "required": true},
        "claim_page": {"type": "string", "required": true},
        "evidence_id": {"type": "string", "required": true, "example": "matriz-p95-latency-2025-q3"}
      },
      "kpi": "Evidence transparency engagement"
    },
    "demo_interaction": {
      "description": "User interacts with Safe Demo",
      "properties": {
        "domain": {"type": "string", "required": true},
        "demo_type": {"type": "string", "required": true, "example": "matriz_reasoning"},
        "action": {"type": "string", "required": true, "example": "start|step|complete"}
      },
      "kpi": "Demo completion rate"
    },
    "cta_clicked": {
      "description": "User clicks call-to-action",
      "properties": {
        "domain": {"type": "string", "required": true},
        "cta_text": {"type": "string", "required": true, "example": "Try MATRIZ Now"},
        "cta_location": {"type": "string", "required": true, "example": "homepage_hero"}
      },
      "kpi": "CTA conversion rate"
    }
  },
  "privacy_policy": {
    "pii_collected": false,
    "cookies": "Essential only (preferences, session)",
    "gdpr_compliant": true,
    "data_retention": "90 days aggregate, 30 days raw events",
    "user_controls": "Opt-out via Do Not Track header respected"
  }
}
```

### 2. KPI Dashboard Specification (`branding/analytics/kpi_dashboard_spec.md`)

```markdown
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
│  📊 Quickstart Success: 52.3% ✅ (Target: ≥50%)             │
│  🎯 Assistive Adoption: 2.1% ✅ (Target: ≥2%)               │
│  🔬 Reasoning Engagement: 17.8% ✅ (Target: ≥15%)           │
│  📖 Evidence Clicks: 6.2% ✅ (Target: ≥5%)                  │
│  🎮 Demo Completion: 58.1% ⚠️ (Target: ≥60%)                │
│  💡 CTA Conversion: 2.8% ⚠️ (Hero target: ≥3%)              │
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
│  1. /matriz (2.3K views)         ⚠️ Demo drop-off at Step 3 │
│  2. /quickstart (1.8K)           ⚠️ CTA hero below target   │
│  3. /reasoning-lab (1.2K)        ✅ All others on target    │
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
```

### 3. Analytics Integration Guide (`branding/analytics/INTEGRATION_GUIDE.md`)

```markdown
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
```

### 4. Event Validation Tool (`tools/validate_events.py`)

```python
#!/usr/bin/env python3
"""
tools/validate_events.py

Validates event tracking implementation:
- All events in taxonomy have corresponding tracking code
- No undefined events in tracking code
- Required properties present
"""
import json
import re
from pathlib import Path

def validate_events():
    """Validate event tracking implementation."""

    # Load event taxonomy
    taxonomy_path = Path("branding/analytics/event_taxonomy.json")
    if not taxonomy_path.exists():
        print("❌ event_taxonomy.json not found")
        return 1

    taxonomy = json.loads(taxonomy_path.read_text())
    defined_events = set(taxonomy["events"].keys())

    # Scan for plausible() calls in JS/HTML files
    tracked_events = set()
    for js_file in Path("branding/websites").rglob("*.js"):
        content = js_file.read_text()
        matches = re.findall(r"plausible\(['\"](\w+)['\"]", content)
        tracked_events.update(matches)

    # Check for undefined events
    undefined = tracked_events - defined_events
    if undefined:
        print(f"⚠️  Undefined events in tracking code: {undefined}")

    # Check for missing tracking
    missing = defined_events - tracked_events
    if missing:
        print(f"⚠️  Events in taxonomy but not tracked: {missing}")

    if not undefined and not missing:
        print(f"✅ Event validation passed ({len(defined_events)} events)")
        return 0
    else:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(validate_events())
```

### 5. Makefile Integration

```makefile
events-validate:  ## Validate event tracking implementation
	python3 tools/validate_events.py
```

## Testing & Validation

1. **Validate event taxonomy**:
   ```bash
   python3 -m json.tool branding/analytics/event_taxonomy.json
   ```

2. **Test event tracking locally**:
   - Add Plausible script to test page
   - Trigger events (quickstart, assistive toggle, etc.)
   - Verify in browser console

3. **Review KPI dashboard spec**:
   - Ensure all KPIs measurable with defined events
   - Validate target thresholds realistic

## Success Criteria

- ✅ Event taxonomy JSON with 8+ events created
- ✅ KPI dashboard specification with 6+ KPIs
- ✅ Analytics integration guide with code examples
- ✅ Event validation tool created
- ✅ All events privacy-compliant (no PII)
- ✅ Makefile target added
- ✅ PR created with 5+ files, reviewers assigned

## PR Details

**Branch**: `feat/analytics-event-taxonomy`
**Title**: `feat(branding): add privacy-first event taxonomy and analytics integration`
**Reviewers**: @web-architect, @content-lead, @data-privacy-lead

**PR Body**:
```markdown
## Summary
Implements privacy-first analytics event taxonomy (GAPS H18) for tracking user journeys across 5 LUKHAS domains with GDPR-compliant tracking, KPI dashboard specification, and assistive mode adoption metrics.

## Problem
- No unified analytics across 5 domains
- Missing KPIs for quickstart success, assistive adoption, reasoning lab engagement
- No privacy-compliant event tracking specification
- Can't measure content effectiveness or user journeys

## Solution
- Comprehensive event taxonomy with 8 privacy-first events
- KPI dashboard specification with 6 key metrics
- Analytics integration guide with Plausible/Fathom
- Event validation tool for CI

## Impact
- Data-driven content optimization based on real user behavior
- Measure assistive mode adoption to validate accessibility investment
- Track quickstart success rate to improve developer onboarding
- GDPR-compliant analytics with no PII collection

## Files
- `branding/analytics/event_taxonomy.json` - 8 privacy-first events
- `branding/analytics/kpi_dashboard_spec.md` - 6 KPI definitions with targets
- `branding/analytics/INTEGRATION_GUIDE.md` - Implementation guide with code
- `tools/validate_events.py` - Event tracking validation tool
- `Makefile` - Added `events-validate` target

## Testing
- Event taxonomy JSON validated
- Sample tracking code tested with Plausible sandbox
- All events confirmed no PII collection
- Event validator: PASS (8 events defined, 8 tracked)

Closes: GAPS H18
```
```

---

## Summary

**Prompts Ready for Claude Code Web**:

1. ✅ **Prompt 1**: GitHub Actions + Quick Win Tools (COMPLETED - PR #1102)
2. ✅ **Prompt 2**: Claims Registry & Validation (COMPLETED - PR #1104)
3. 📋 **Prompt 3**: Evidence Page Template System (45 min, P0, GAPS A1)
4. 📋 **Prompt 4**: SEO Technical Hygiene (60 min, P0, GAPS H19)
5. 📋 **Prompt 5**: Content CI Workflow (60 min, P0, GAPS D10)
6. 📋 **Prompt 6**: Event Taxonomy & Analytics (45 min, P0, GAPS H18)

**Total Estimated Time**: 210 minutes (~3.5 hours) for remaining 4 prompts

**Instructions for Claude Code Web**:
1. Copy entire prompt (including LUKHAS Policies Header)
2. Paste into Claude Code Web
3. Review PR when complete
4. Merge after validation

**Note**: Worktree sections removed as Claude Code Web works on cloud copy.
