---
title: "SEO Technical Hygiene Guide for LUKHAS Multi-Domain Ecosystem"
domain: lukhas.com
owner: @web-architect
audience: [developers, content-creators, web-team]
tone:
  poetic: 0.10
  user_friendly: 0.60
  academic: 0.30
canonical: https://lukhas.com/governance/seo-guide
source: governance
last_reviewed: "2025-11-08"
claims_approval: true
claims_verified_by: ['@web-architect', '@content-lead']
seo:
  description: "Comprehensive guide for implementing SEO technical hygiene across 5 LUKHAS domains including schema.org markup, canonical URLs, and sitemaps."
  keywords: ["SEO", "schema.org", "canonical URLs", "sitemaps", "hreflang", "multi-domain"]
  og_image: /assets/og-images/governance-seo-guide.png
---

# SEO Technical Hygiene Guide

## Overview

This guide provides comprehensive documentation for implementing and maintaining SEO technical hygiene across the LUKHAS multi-domain ecosystem (lukhas.ai, lukhas.dev, lukhas.com, lukhas.eu, lukhas.app).

### Key Objectives

- **Eliminate duplicate content penalties** through proper canonicalization
- **Enhance search visibility** with schema.org rich snippets
- **Maintain SEO health** through automated validation
- **Optimize cross-domain content** with hreflang tags
- **Provide search engine guidance** through XML sitemaps

## Schema.org Markup

### Overview

Schema.org provides a vocabulary for structured data that helps search engines understand content and display rich snippets in search results.

### Template System

The LUKHAS ecosystem uses JSON-LD templates for common page types:

**Location**: `branding/templates/schema/`

**Available Templates**:
- `product_page.json` - Software products and applications
- `article.json` - Technical articles and blog posts
- `organization.json` - Organization-wide metadata

### Product Page Schema

Used for product pages and software application descriptions.

**Template**: `branding/templates/schema/product_page.json`

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

**Implementation**:
1. Copy template to page directory
2. Replace `{{ product_name }}` with actual product name
3. Replace `{{ seo_description }}` with meta description
4. Update rating and review_count if available
5. Include in HTML `<head>` as `<script type="application/ld+json">`

### Article Schema

Used for technical articles, research papers, and blog posts.

**Template**: `branding/templates/schema/article.json`

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

**Implementation**:
1. Replace `{{ title }}` with article headline
2. Replace `{{ seo_description }}` with article description
3. Set `{{ published_date }}` to publication date (ISO 8601 format)
4. Set `{{ last_reviewed }}` to last modification date from front-matter

### Organization Schema

Used for organization-wide metadata, typically on homepage and about pages.

**Template**: `branding/templates/schema/organization.json`

**Implementation**: Include this markup on primary pages to establish organization identity.

### Validation

Test schema.org markup using:
- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Schema.org Validator**: https://validator.schema.org/

## Canonical URLs

### Purpose

Canonical URLs prevent duplicate content penalties when the same content appears on multiple domains or URLs.

### Strategy

The LUKHAS ecosystem uses a **primary domain** strategy:

- **lukhas.ai** - Primary domain for AI technology and MATRIZ
- **lukhas.dev** - Primary domain for developer documentation
- **lukhas.com** - Primary domain for corporate and identity
- **lukhas.eu** - Regional variant (Europe)
- **lukhas.app** - Application/product landing pages

### Canonical Mapping

**Location**: `branding/seo/canonical_map.yaml`

This file defines canonical URL relationships for duplicate content:

```yaml
canonical_mappings:
  # MATRIZ cognitive engine mentioned on 3 domains
  - duplicates:
      - https://lukhas.ai/matriz
      - https://lukhas.eu/matriz
      - https://lukhas.app/matriz
    canonical: https://lukhas.ai/matriz
```

### Implementation

Add canonical URL to page front-matter:

```yaml
---
canonical: https://lukhas.ai/matriz
---
```

In HTML `<head>`:

```html
<link rel="canonical" href="https://lukhas.ai/matriz" />
```

### Validation

Run SEO validator to check canonical URLs:

```bash
make seo-validate
```

Checks performed:
- All pages have canonical URLs
- No duplicate canonical URLs across domains
- Canonical URLs match mapping in `canonical_map.yaml`

## Hreflang Tags

### Purpose

Hreflang tags indicate language and regional variants of content to search engines.

### Usage in LUKHAS

The LUKHAS ecosystem uses hreflang for regional content:

- `en-US` - United States (lukhas.com)
- `en-EU` - European Union (lukhas.eu)

### Implementation

Define hreflang groups in `branding/seo/canonical_map.yaml`:

```yaml
hreflang_groups:
  - canonical: https://lukhas.com/about
    alternates:
      - url: https://lukhas.eu/about
        lang: en-EU
      - url: https://lukhas.com/about
        lang: en-US
```

In HTML `<head>`:

```html
<link rel="alternate" hreflang="en-US" href="https://lukhas.com/about" />
<link rel="alternate" hreflang="en-EU" href="https://lukhas.eu/about" />
<link rel="canonical" href="https://lukhas.com/about" />
```

### Best Practices

1. **Always include canonical**: Every hreflang group should have a canonical URL
2. **Self-referential tags**: Each page should reference itself in hreflang
3. **Bidirectional links**: If page A links to page B, page B must link to page A
4. **Use region codes**: Use `en-US`, `en-EU` rather than just `en`

## Meta Descriptions and Titles

### Meta Description

**Purpose**: Appears in search results below page title

**Length**: 150-160 characters (optimal)

**Implementation** in front-matter:

```yaml
seo:
  description: "LUKHAS AI consciousness simulation platform with quantum-inspired algorithms and bio-inspired computing architecture."
```

**Best Practices**:
- Include primary keywords naturally
- Make it compelling (call-to-action oriented)
- Unique for each page
- Stay within character limit (truncated at ~160 chars)

### Title Tags

**Purpose**: Primary element in search results, browser tabs, social shares

**Length**: 50-60 characters (optimal)

**Implementation** in front-matter:

```yaml
title: "MATRIZ Cognitive Engine - LUKHAS AI"
```

**Best Practices**:
- Include primary keyword
- Include brand name (LUKHAS AI)
- Front-load important words
- Keep concise and descriptive
- Unique for each page

### Validation

Run SEO validator to check meta descriptions and titles:

```bash
make seo-validate
```

Checks performed:
- Meta descriptions are 150-160 characters
- Titles are 50-60 characters
- All pages have both meta description and title

## XML Sitemaps

### Purpose

XML sitemaps help search engines discover and crawl all pages in a domain.

### Generation

**Tool**: `tools/generate_sitemaps.py`

**Command**:

```bash
make sitemaps
```

This generates XML sitemaps for all 5 domains:
- `branding/websites/lukhas.ai/sitemap.xml`
- `branding/websites/lukhas.dev/sitemap.xml`
- `branding/websites/lukhas.com/sitemap.xml`
- `branding/websites/lukhas.eu/sitemap.xml`
- `branding/websites/lukhas.app/sitemap.xml`

### Sitemap Structure

Each sitemap entry includes:

```xml
<url>
  <loc>https://lukhas.ai/matriz</loc>
  <lastmod>2025-11-08</lastmod>
  <priority>0.8</priority>
  <changefreq>yearly</changefreq>
</url>
```

**Priority Values**:
- `1.0` - Homepage
- `0.8` - Product and feature pages
- `0.6` - Research and blog posts
- `0.5` - Other pages

**Change Frequency**:
- `weekly` - Homepage
- `monthly` - Blog posts
- `yearly` - Static content

### Metadata Source

The sitemap generator reads metadata from markdown front-matter:

```yaml
---
canonical: https://lukhas.ai/matriz
last_reviewed: "2025-11-08"
---
```

### Submission

Submit sitemaps to search engines:

**Google Search Console**:
1. Verify domain ownership
2. Navigate to "Sitemaps" section
3. Submit sitemap URL: `https://lukhas.ai/sitemap.xml`

**Bing Webmaster Tools**:
1. Verify domain ownership
2. Navigate to "Sitemaps" section
3. Submit sitemap URL: `https://lukhas.ai/sitemap.xml`

### Validation

Validate sitemap XML syntax:
- **Google Search Console**: Upload and check for errors
- **XML Sitemap Validator**: https://www.xml-sitemaps.com/validate-xml-sitemap.html

## Robots.txt Configuration

### Purpose

Controls which pages search engines can crawl and where to find sitemaps.

### Standard Configuration

**Location**: Root of each domain (e.g., `lukhas.ai/robots.txt`)

```txt
User-agent: *
Allow: /

# Block admin and internal pages
Disallow: /admin/
Disallow: /api/internal/
Disallow: /_dev/

# Sitemap location
Sitemap: https://lukhas.ai/sitemap.xml
```

### Domain-Specific Configurations

**lukhas.ai** (AI technology):
```txt
User-agent: *
Allow: /
Disallow: /admin/
Sitemap: https://lukhas.ai/sitemap.xml
```

**lukhas.dev** (Developer docs):
```txt
User-agent: *
Allow: /
Disallow: /api/internal/
Sitemap: https://lukhas.dev/sitemap.xml
```

**lukhas.com** (Corporate):
```txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /internal/
Sitemap: https://lukhas.com/sitemap.xml
```

### Best Practices

1. **Include sitemap**: Always reference sitemap URL
2. **Be permissive**: Use `Allow: /` unless specific reasons to block
3. **Block sensitive paths**: Admin, API, development paths
4. **Test before deployment**: Use Google Search Console robots.txt tester

## Automated Validation

### SEO Validator

**Tool**: `tools/validate_seo.py`

**Command**:

```bash
make seo-validate
```

**Checks**:
- ✅ All pages have canonical URLs
- ✅ Meta descriptions are 150-160 characters
- ✅ Titles are 50-60 characters
- ✅ No duplicate canonical URLs across domains

**Output**:

```
✅ SEO validation passed (27 pages checked)
```

Or:

```
❌ SEO Validation Errors:
  - branding/websites/lukhas.ai/matriz.md: Missing canonical URL

⚠️  SEO Validation Warnings:
  - branding/websites/lukhas.com/about.md: Meta description 142 chars (target: 150-160)
```

### CI Integration

Add SEO validation to CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Validate SEO
  run: make seo-validate
```

This prevents SEO regressions in pull requests.

## Workflow

### Adding New Content

1. **Write content** with proper front-matter:

```yaml
---
title: "New Feature Page - LUKHAS AI"
domain: lukhas.ai
canonical: https://lukhas.ai/new-feature
last_reviewed: "2025-11-08"
seo:
  description: "Comprehensive guide to new feature in LUKHAS AI platform with quantum-inspired algorithms and consciousness simulation."
  keywords: ["feature", "LUKHAS", "AI"]
---
```

2. **Validate SEO compliance**:

```bash
make seo-validate
```

3. **Regenerate sitemaps**:

```bash
make sitemaps
```

4. **Add schema.org markup** (if applicable):
   - Choose appropriate template from `branding/templates/schema/`
   - Fill in template variables
   - Include in page HTML

5. **Test in Google Rich Results** (for schema.org):
   - Visit https://search.google.com/test/rich-results
   - Enter page URL
   - Verify markup is detected

### Maintaining Existing Content

1. **Update `last_reviewed` date** in front-matter when content changes
2. **Regenerate sitemaps** after updates:

```bash
make sitemaps
```

3. **Re-validate SEO** after bulk changes:

```bash
make seo-validate
```

## Common Issues

### Duplicate Canonical URLs

**Problem**: Multiple pages claim the same canonical URL

**Solution**: Review `canonical_map.yaml` and ensure each duplicate page references the correct canonical URL

**Detection**:

```bash
make seo-validate
```

### Missing Meta Descriptions

**Problem**: Pages without SEO meta descriptions

**Solution**: Add `seo.description` to front-matter:

```yaml
seo:
  description: "150-160 character description here"
```

### Schema.org Validation Errors

**Problem**: Google Rich Results Test shows errors

**Solution**:
1. Validate JSON-LD syntax (check for missing commas, quotes)
2. Ensure all required fields are present
3. Use validator: https://validator.schema.org/

### Sitemap Not Updating

**Problem**: New pages don't appear in sitemap

**Solution**:
1. Ensure page has `canonical` in front-matter
2. Regenerate sitemaps: `make sitemaps`
3. Check that page is in correct domain directory (`branding/websites/{domain}/`)

## Resources

### Tools

- **Sitemap Generator**: `tools/generate_sitemaps.py`
- **SEO Validator**: `tools/validate_seo.py`
- **Canonical Mapping**: `branding/seo/canonical_map.yaml`
- **Schema Templates**: `branding/templates/schema/`

### External Validators

- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Google Search Console**: https://search.google.com/search-console
- **Schema.org Validator**: https://validator.schema.org/
- **XML Sitemap Validator**: https://www.xml-sitemaps.com/validate-xml-sitemap.html
- **Robots.txt Tester**: https://support.google.com/webmasters/answer/6062598

### Documentation

- **Schema.org Documentation**: https://schema.org/docs/documents.html
- **Google Search Central**: https://developers.google.com/search/docs
- **Hreflang Guidelines**: https://developers.google.com/search/docs/specialty/international/localized-versions

## Changelog

### 2025-11-08
- Initial SEO technical hygiene infrastructure
- Schema.org templates for products, articles, organization
- Sitemap generator for all 5 domains
- Canonical URL mapping system
- SEO validator with automated checks
- Makefile targets: `sitemaps`, `seo-validate`

## Contact

For questions or issues with SEO technical hygiene:
- **Owner**: @web-architect
- **Contributors**: @content-lead, @web-team
- **GitHub Issues**: https://github.com/LukhasAI/Lukhas/issues
