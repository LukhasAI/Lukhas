# ⚠️ LEGACY NOTICE - docs/web/

**Status**: Legacy Pre-MATRIZ Content
**Last Updated**: November 5, 2025
**Migration Target**: `branding/websites/`

---

## Content Migration Notice

This directory (`docs/web/`) contains **legacy website content** created before the MATRIZ cognitive DNA rollout emphasis. As of November 2025, **all website content development has moved to the canonical location**:

### 📍 New Canonical Location

```
/branding/websites/
├── lukhas.ai/          # Consciousness gateway (MATRIZ-powered)
├── lukhas.app/         # Application platform
├── lukhas.cloud/       # Managed cloud services
├── lukhas.com/         # Enterprise hub
├── lukhas.dev/         # Developer platform
├── lukhas.eu/          # EU market (research, grants, compliance)
├── lukhas.id/          # Identity & authentication
├── lukhas.io/          # API gateway & infrastructure
├── lukhas.lab/         # Research & innovation
├── lukhas.store/       # Lambda app marketplace
├── lukhas.team/        # Team collaboration
├── lukhas.us/          # American market
└── lukhas.xyz/         # Experimental features
```

---

## Why This Migration?

### Pre-MATRIZ Era (docs/web/)
- Content created October 2025 and earlier
- References MATRIZ but doesn't emphasize it as core differentiator
- Generic "consciousness-aware AI" positioning
- Scattered between `docs/web/content/domains/` and `branding/websites/`

### Post-MATRIZ Era (branding/websites/)
- **MATRIZ cognitive DNA front-and-center** across all domains
- Explainability and transparency as unique value proposition
- Production metrics (87% complete, <250ms latency, 99.7% Guardian compliance)
- Reasoning graph visualization emphasis
- Unified content location for all 13 domains

---

## What to Do with docs/web/

### ✅ Keep for Reference
- **Historical content examples** showing evolution of messaging
- **Technical depth** from comprehensive landing pages (8,000+ words with code examples)
- **Code samples** in Python, TypeScript, Go, Rust that can be extracted and reused
- **Pricing tier comparisons** and technical specifications
- **Strategic planning documents** in `docs/web/content/plans/`

### 🔄 Selectively Extract and Integrate
Valuable technical content from docs/web should be extracted and integrated into branding/websites/ MATRIZ-ready content:
- API code examples and SDK integration patterns
- Pricing tables and tier comparisons
- Technical architecture deep dives
- Performance specifications and benchmarks

### ❌ Do NOT Use as Primary Source
- All new website content should be created in `branding/websites/`
- Do NOT update domain landing pages in docs/web/
- Do NOT reference docs/web as canonical for website deployment

---

## Content That Should Be Preserved

### Shared Resources (Keep Active)
- `docs/web/content/shared/CONTENT_MANAGEMENT_GUIDE.md` - Editorial guidelines
- `docs/web/content/shared/vocabulary-usage/VOCABULARY_STANDARDS_QUICK_REFERENCE.md` - Terminology standards

### Strategic Planning (Keep Active)
- `docs/web/content/plans/` - Planning documents, roadmaps, strategies
- `docs/web/LUKHAS_ECOSYSTEM_WEBSITE_PLANS.md` - Master ecosystem planning
- `docs/web/DOMAIN_STRATEGY_REVIEW_2025-10-26.md` - Strategy reviews

### General Documentation (Keep Active)
- Technical guides unrelated to website content
- Internal process documentation
- Design system specifications

---

## Migration History

### Phase 1: Initial MATRIZ Content (PR #933 - Nov 5, 2025)
Migrated MATRIZ-ready content for 4 priority domains to branding/websites/:
- ✅ lukhas.ai - Updated homepage and architecture (MATRIZ-powered consciousness)
- ✅ lukhas.dev - Developer platform with SDK emphasis
- ✅ lukhas.com - Enterprise explainability positioning
- ✅ lukhas.us - Minimal updates (already aligned)

### Phase 2: EU Research & Grant Content (Nov 5, 2025)
Created comprehensive lukhas.eu content:
- ✅ 5 peer-reviewed research papers (cognitive DNA, constitutional validation, ΛiD, distributed consciousness, parallel dreams)
- ✅ Grant support hub (Horizon Europe integration)
- ✅ Research partnerships portal (PhD positions, collaborations)
- ✅ Compliance dashboard (EU AI Act, GDPR validation)

### Future Phases
- Extract valuable technical content from docs/web domains
- Integrate code examples and pricing tables into branding/websites/
- Complete remaining domains (app, cloud, id, io, lab, store, team, xyz)
- Archive docs/web/content/domains/ as historical reference

---

## For Content Contributors

### Creating New Website Content
```bash
# CORRECT - Use branding/websites/
vim /Users/agi_dev/LOCAL-REPOS/Lukhas/branding/websites/lukhas.ai/new_page.md

# INCORRECT - Don't use docs/web for new website content
vim /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/web/content/domains/lukhas-ai/new_page.md
```

### Finding Current Website Content
```bash
# Find domain content
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/branding/websites/lukhas.*/

# Check what exists for specific domain
ls /Users/agi_dev/LOCAL-REPOS/Lukhas/branding/websites/lukhas.eu/
```

### Content Development Workflow
1. Create/update content in `branding/websites/<domain>/`
2. Follow MATRIZ-ready standards (cognitive DNA emphasis, transparency positioning)
3. Reference legacy docs/web for technical depth inspiration if needed
4. Commit to main repo with clear documentation

---

## Questions?

If you're uncertain about:
- Where to create new website content → **Use branding/websites/**
- Whether to update docs/web → **No, use branding/websites/ instead**
- How to handle docs/web content → **Reference for inspiration, develop in branding/websites/**

**Migration Lead**: Engineering team
**Contact**: dev@lukhasai.com
**Documentation**: This file + branding/websites/README.md (if exists)

---

*This directory remains available for reference, technical content extraction, and strategic planning documents. All website content development has moved to branding/websites/ as the canonical source of truth.*

**Last Updated**: November 5, 2025
**Migration Status**: Phase 2 Complete (lukhas.eu research content)
**Next Review**: Post-MATRIZ 100% rollout (Q4 2025/Q1 2026)
