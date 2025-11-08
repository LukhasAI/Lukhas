# Session 14: SEO Pillars + Content Clusters (GAPS A2)

**Status**: Ready to Execute
**Estimated Time**: 60 minutes
**Priority**: P0 (Content Strategy)
**GAPS Item**: A2 - SEO Pillars + Content Clusters

---

## Instructions

1. Copy the entire prompt text below
2. Open Claude Code Web: https://claude.ai/code
3. Paste the prompt
4. Wait for PR creation
5. Review and merge PR
6. Run validation: `make content-strategy-validate`

---

## Prompt Text (Copy Everything Below)

```
**LUKHAS Project Context**:

**Repository**: https://github.com/LukhasAI/Lukhas (LUKHAS AI consciousness platform)

**Critical Policies**:
- **Lane Isolation**: NEVER import from `candidate/` in `lukhas/` code (validate with `make lane-guard`)
- **Testing Standards**: Maintain 75%+ coverage for production promotion
- **Commit Format**: `<type>(<scope>): <imperative subject ≤72>` with Problem/Solution/Impact bullets
- **Vocabulary Compliance**: NO "true AI", "sentient AI", "production-ready" without approval
- **Branding**: Use "LUKHAS AI", "quantum-inspired", "bio-inspired" (never "AGI")
- **Evidence System**: Link all claims to `release_artifacts/evidence/` pages
- **SEO Standards**: Add canonical URLs, meta descriptions (150-160 chars), keywords
- **Analytics**: GDPR-first, privacy-preserving, consent-based tracking only
- **Feature Flags**: Use `lukhas/features/flags_service.py` for gradual rollouts
- **Launch Playbooks**: Follow `branding/governance/launch/` templates

**Key Commands**:
- `make test` - Run comprehensive test suite
- `make lint` - Run linting and type checking
- `make lane-guard` - Validate import boundaries
- `make seo-validate` - Validate SEO compliance
- `make claims-validate` - Validate claims have evidence
- `make flags-validate` - Validate feature flags
- `make analytics-privacy-check` - Check for PII leakage
- `make launch-validate` - Validate launch checklists

**Related Docs**:
- Evidence System: `branding/governance/tools/EVIDENCE_SYSTEM.md`
- SEO Guide: `branding/governance/SEO_GUIDE.md`
- Analytics Integration: `branding/analytics/INTEGRATION_GUIDE_V2.md`
- Privacy Implementation: `branding/analytics/PRIVACY_IMPLEMENTATION.md`
- Feature Flags Guide: `branding/features/FEATURE_FLAGS_GUIDE.md`
- Launch Playbooks: `branding/governance/launch/PLAYBOOK_TEMPLATE.md`
- 90-Day Roadmap: `branding/governance/strategic/90_DAY_ROADMAP.md`
- GAPS Analysis: `branding/governance/strategic/GAPS_ANALYSIS.md`

**Phase Progress**: 9/19 GAPS items complete (47.4%) - Phases 1 & 2 delivered 46,992 lines

---

**Task**: Design SEO Pillars + Content Clusters for GAPS A2

**Goal**: Create comprehensive content strategy with pillar pages, content clusters, and internal linking optimization to drive organic search traffic across 5 LUKHAS domains.

**Background**:
- 5 production domains need coordinated content strategy
- Current content is fragmented, no clear topic clustering
- Missing pillar pages for core topics
- Internal linking not optimized for SEO
- GAPS Item: A2 from GAPS_ANALYSIS.md

**Deliverables**:

1. **Content Strategy Document** (`branding/seo/CONTENT_STRATEGY.md`):
   - 5 pillar pages identified:
     - Pillar 1: "Consciousness-Inspired AI" (lukhas.ai)
     - Pillar 2: "MATRIZ Cognitive Engine" (lukhas.dev)
     - Pillar 3: "Enterprise AI Solutions" (lukhas.com)
     - Pillar 4: "Quantum-Bio Computing" (lukhas.eu)
     - Pillar 5: "AI Safety & Ethics" (lukhas.app)
   - Content cluster map (10-15 supporting articles per pillar)
   - Internal linking strategy
   - Keyword research (primary, secondary, long-tail)
   - Target personas and search intent

2. **Pillar Page Templates** (`branding/templates/pillar_page.md`):
   - Comprehensive structure (2000-3000 words):
     - Hero section with value proposition
     - Table of contents with anchor links
     - Core concept explanation
     - Sub-topic sections (link to cluster content)
     - Visual diagrams and infographics
     - Case studies and examples
     - FAQ section
     - Related resources
     - CTA (call-to-action)
   - Front-matter with SEO metadata
   - Schema.org markup for rich snippets

3. **Content Cluster Generator** (`tools/generate_content_cluster.py`):
   - Input: pillar topic, keyword, target word count
   - Generates:
     - Outline for pillar page
     - 10-15 cluster article ideas with titles
     - Keyword map (primary/secondary per article)
     - Internal linking suggestions
     - Content calendar (publishing schedule)
   - Output: YAML file with full cluster spec

4. **Internal Linking Optimizer** (`tools/optimize_internal_links.py`):
   - Analyzes existing content for linking opportunities
   - Suggests relevant internal links based on:
     - Keyword overlap
     - Topic relevance (NLP similarity)
     - User journey mapping
   - Generates anchor text suggestions (contextual, natural)
   - Validates link health (no broken links, orphan pages)
   - Output: Markdown report with suggested additions

5. **Keyword Research Tool** (`tools/keyword_research.py`):
   - Integrates with existing `branding/seo/canonical_map.yaml`
   - Generates keyword clusters:
     - Primary keywords (high volume, competitive)
     - Secondary keywords (medium volume, moderate difficulty)
     - Long-tail keywords (low volume, low competition, high intent)
   - Keyword difficulty scoring (1-100)
   - Search volume estimates
   - Competitor analysis (top 10 ranking pages)
   - Output: JSON with keyword data

6. **Content Cluster Tracker** (`branding/seo/content_clusters.yaml`):
   - YAML file tracking:
     - Pillar page status (draft, review, published)
     - Cluster articles (planned, in-progress, published)
     - Internal links added
     - Performance metrics (traffic, rankings, conversions)
   - Progress visualization (ASCII art progress bars)

7. **Pillar Page Examples** (`branding/websites/{domain}/pillars/`):
   - Create 1 complete pillar page per domain:
     - `lukhas.ai/pillars/consciousness_ai.md` - Consciousness-Inspired AI
     - `lukhas.dev/pillars/matriz_engine.md` - MATRIZ Cognitive Engine
     - `lukhas.com/pillars/enterprise_solutions.md` - Enterprise AI Solutions
     - `lukhas.eu/pillars/quantum_bio.md` - Quantum-Bio Computing
     - `lukhas.app/pillars/ai_safety.md` - AI Safety & Ethics
   - Each with:
     - 2000+ words
     - 10+ internal links
     - Schema.org markup
     - Visual diagrams
     - Evidence links

8. **Validation & Analytics** (`tools/validate_content_strategy.py`):
   - Validates:
     - Pillar pages have 10+ cluster articles
     - Internal linking follows best practices (3-5 per page)
     - No orphan pages (every page linked from at least 2 others)
     - Keyword cannibalization detection
   - Reports:
     - Content coverage gaps
     - Link equity distribution
     - Keyword opportunity score

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as content strategy validation
- Add `make content-strategy-validate` target to Makefile
- Link from `branding/governance/README.md`
- Update `branding/seo/canonical_map.yaml` with pillar pages

**Acceptance Criteria**:
- 5 pillar pages created (1 per domain, 2000+ words each)
- Content cluster map with 50-75 article ideas
- Internal linking strategy documented
- Keyword research tool generating clusters
- Content cluster tracker with progress visualization
- Validation tool checking linking and coverage
- CI/CD integration working

**T4 Commit Message**:
```
feat(seo): add pillar pages and content cluster strategy

Problem:
- Fragmented content across 5 domains without strategy
- Missing pillar pages for core topics
- Internal linking not optimized
- No content cluster planning

Solution:
- Created comprehensive content strategy (5 pillars, 50-75 clusters)
- Built pillar page template with SEO best practices
- Implemented content cluster generator tool
- Added internal linking optimizer (analyzes and suggests)
- Created keyword research tool with difficulty scoring
- Built content cluster tracker with progress visualization
- Generated 5 example pillar pages (2000+ words each)
- Validation tool for coverage and linking

Impact:
- Clear content roadmap for organic growth
- 5 pillar pages targeting high-value keywords
- 50-75 cluster articles planned
- Internal linking optimized for SEO
- Content calendar for next 6 months
- GAPS A2 complete (11/19 items → 12/19 = 63.2%)

Closes: GAPS-A2
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(seo): add pillar pages and content cluster strategy (GAPS A2)"

**Validation**: Run `make content-strategy-validate` before creating PR
```

---

## Post-Execution Checklist

- [ ] PR created and numbered
- [ ] PR reviewed for SEO compliance
- [ ] All tests passing
- [ ] 5 pillar pages validated (2000+ words each)
- [ ] Content cluster map verified (50-75 articles)
- [ ] Internal linking optimizer tested
- [ ] Keyword research tool functional
- [ ] `make content-strategy-validate` passes
- [ ] PR merged with squash
- [ ] Branch deleted
- [ ] Update GAPS progress to 12/19 (63.2%)

---

**Session Created**: 2025-11-08
**Ready to Execute**: Yes
