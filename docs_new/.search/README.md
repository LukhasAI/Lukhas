---
title: Documentation Search Taxonomy
status: stable
owner: docs-team
last_review: 2025-01-09
tags: [reference, search, taxonomy]
facets:
  layer: [gateway]
  domain: [symbolic]
  audience: [dev]
---

# Documentation Search Taxonomy

This directory contains the controlled vocabulary and search taxonomy for LUKHΛS documentation.

## Files

- `taxonomy.json` - Complete controlled vocabulary definitions
- `README.md` - This documentation

## Controlled Vocabulary

### Status Values
- `draft` - Work in progress, may contain errors
- `review` - Ready for review, content may change
- `stable` - Reviewed and approved, minimal changes expected
- `deprecated` - No longer maintained, use alternatives

### Facets

#### Layer (Technical Stack)
- `gateway` - User-facing interfaces, entry points
- `orchestration` - Coordination, workflow management
- `integration` - External service connections  
- `storage` - Data persistence, databases
- `ui` - User interfaces, dashboards

#### Domain (Functional Area)
- `symbolic` - GLYPH processing, symbolic computation
- `identity` - Authentication, authorization, ΛiD system
- `ethics` - Guardian system, compliance, safety
- `time` - Temporal processing, UTC compliance
- `async` - Asynchronous operations, concurrency
- `metrics` - Monitoring, observability, performance
- `consciousness` - Awareness, decision-making systems
- `memory` - Memory folds, persistence patterns
- `quantum` - Quantum-inspired algorithms
- `bio` - Bio-inspired processing, adaptation
- `guardian` - Safety, protection, oversight

#### Audience (Target Users)
- `dev` - Software developers, engineers
- `ops` - Operations, DevOps, system administrators  
- `researcher` - AI researchers, consciousness theorists
- `product` - Product managers, business stakeholders

## Usage in Front-Matter

```yaml
---
title: Document Title
status: stable
owner: team-name
last_review: YYYY-MM-DD
tags: [curated, list, from, taxonomy]
facets:
  layer: [gateway, orchestration]
  domain: [consciousness, identity]
  audience: [dev, researcher]
---
```

## Maintenance

- Review taxonomy quarterly
- Update controlled vocabulary as system evolves
- Ensure all documentation uses approved terms
- Validate front-matter against taxonomy in CI/CD