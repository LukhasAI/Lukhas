---
implementation_type: tone_system_v2
created: 2025-11-10
status: ready_to_implement
priority: high
source_audit: CLAUDE_TONE_COMPLIANCE_AUDIT_2025-11-10.md
estimated_effort: 80-120 hours
---

# IMPLEMENTATION GUIDE: TONE SYSTEM V2

**Based on**: Claude Tone & Compliance Audit (November 10, 2025)
**Purpose**: Replace 3-layer tone system + 8-family vocabulary rotation with simpler, more effective approach
**Priority**: HIGH - Critical for content quality and compliance

---

## 📋 OVERVIEW

This implementation guide extracts actionable steps from the Claude Tone & Compliance Audit to:

1. **Simplify tone system** from 3 layers → 2 tiers
2. **Replace decorative vocabulary** with architecture-derived explanatory language
3. **Establish enforcement** through automated validation tools
4. **Create compliance infrastructure** for EU/US regulatory readiness

---

## 🔄 IMPLEMENTATION WORKFLOW FOR CLAUDE CODE

### Step 1: Create Directory Structure

```bash
mkdir -p branding/tone
mkdir -p branding/enforcement
mkdir -p branding/examples/good_examples
mkdir -p branding/examples/anti_examples
mkdir -p docs/compliance
```

### Step 2: Extract and Create Core Documents (Priority 1)

1. **Create** `branding/tone/CONSCIOUSNESS_VOCABULARY_GUIDE.md` from audit Section 2
   - Purpose: Replace decorative metaphors with architecture-derived explanatory language
   - Content: Constellation-native vocabulary banks per star domain
   - Key principle: Explanatory vs decorative language distinction

2. **Create** `branding/tone/GENERATION_RULES.md` from audit Section 3
   - Purpose: Enforceable content creation rules
   - Content: Quality metrics, validation criteria, gated workflows
   - Key metrics: Decorative density <0.5%, Specificity >80%

3. **Create** `branding/tone/TONE_SYSTEM_V2.md` from audit Section 1 rewrite
   - Purpose: Document simplified 2-tier tone approach
   - Content: User-Friendly (70%) + Technical Precision (30%)
   - Replaces: 3-layer Poetic/User-Friendly/Academic system

### Step 3: Create Enforcement Tools (Priority 2)

1. **Create** `branding/enforcement/blocked_terms.json`
   - Decorative vocabulary to avoid (symphony, bloom, shimmer, tapestry, etc.)
   - Generic AI claims lacking architectural specificity
   - Format: `{"category": "decorative_metaphors", "terms": [...], "severity": "block"}`

2. **Create** `branding/enforcement/required_terms.json`
   - Constellation star vocabulary banks (Memory → Fold, Cascade, Causal Chain)
   - Architecture-specific terminology per domain
   - Format: `{"star": "memory", "vocabulary": [...], "usage": "explanatory"}`

3. **Create** `branding/enforcement/vocabulary_validator.py`
   - Automated markdown file validation
   - Checks: decorative density, specificity score, blocked terms, explanation ratio
   - Output: Validation report with actionable recommendations
   - Make executable: `chmod +x vocabulary_validator.py`

4. **Create** `branding/enforcement/quality_metrics.py`
   - Scoring system for content quality
   - Metrics: Flesch Reading Ease, AI detection likelihood, vocabulary rotation density
   - Integration: CI/CD validation hooks

### Step 4: Create Compliance Checklists (Priority 3)

1. **Create** `docs/compliance/EU_COMPLIANCE_CHECKLIST.md` from audit Section 3A
   - GDPR requirements (10 items)
   - EU AI Act readiness (13 items)
   - Priority ratings, effort estimates, timeline recommendations
   - Current score: 2/10 GDPR documented, 3/13 AI Act strong

2. **Create** `docs/compliance/US_COMPLIANCE_CHECKLIST.md` from audit Section 3B
   - AI Bill of Rights alignment (5 items)
   - NIST AI RMF mapping (4 items)
   - CCPA compliance (5 items)
   - Sector-specific regulations (HIPAA, COPPA, FERPA)
   - Current score: 0/5 CCPA documented (CRITICAL GAP)

### Step 5: Create Example Library (Priority 4)

1. **Extract good examples** from guide to separate files:
   - `branding/examples/good_examples/identity_explanation.md`
   - `branding/examples/good_examples/reasoning_graphs.md`
   - `branding/examples/good_examples/infrastructure_description.md`

2. **Extract anti-examples** to separate files:
   - `branding/examples/anti_examples/decorative_metaphors.md`
   - `branding/examples/anti_examples/stacked_metaphors.md`
   - `branding/examples/anti_examples/generic_ai_claims.md`

3. **Organize by topic**: Identity, Memory, Reasoning, Infrastructure, Ethics, Security

### Step 6: Create Integration README (Priority 5)

**Create** `README_TONE_SYSTEM_UPDATE.md` in repository root:
- Overview explaining changes from v1 → v2
- Usage instructions for content creators
- Quick validation examples
- Migration priority (Week 1-2: Core docs, Week 3-4: Product pages, Week 5-8: Remaining)
- Success metrics tracking

### Step 7: Validate Setup

```bash
# Test validator on existing homepage
python branding/enforcement/vocabulary_validator.py branding/websites/lukhas.cloud/homepage_matriz_ready.md

# Should output report showing:
# - Blocked terms found
# - Decorative density score
# - Specificity analysis
# - Actionable recommendations
```

### Step 8: Create Git Commit

```bash
git add branding/ docs/ README_TONE_SYSTEM_UPDATE.md
git commit -m "feat(tone): implement Consciousness Vocabulary system v2

Problem:
- 3-layer tone system (Poetic/User-Friendly/Academic) creates jarring transitions
- 8-family vocabulary rotation produces artificial-sounding prose
- Decorative metaphors undermine technical credibility
- No automated enforcement for content quality

Solution:
- Simplified 2-tier tone: User-Friendly (70%) + Technical (30%)
- Constellation-native vocabulary replacing generic decorative language
- Automated validator checking density, specificity, explanation ratio
- Comprehensive EU/US compliance checklists
- Good/anti-example library for content creators

Impact:
- Content quality enforcement through automated validation
- Regulatory compliance tracking with effort estimates
- Clear migration path for existing content (8-week timeline)
- Reduced AI-generated content 'tells' improving authenticity

Files created:
- branding/tone/CONSCIOUSNESS_VOCABULARY_GUIDE.md
- branding/tone/GENERATION_RULES.md
- branding/tone/TONE_SYSTEM_V2.md
- branding/enforcement/vocabulary_validator.py
- branding/enforcement/blocked_terms.json
- branding/enforcement/required_terms.json
- branding/enforcement/quality_metrics.py
- docs/compliance/EU_COMPLIANCE_CHECKLIST.md
- docs/compliance/US_COMPLIANCE_CHECKLIST.md
- branding/examples/good_examples/* (6 files)
- branding/examples/anti_examples/* (6 files)
- README_TONE_SYSTEM_UPDATE.md

Refs: Claude Tone & Compliance Audit (2025-11-10)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## ⚠️ IMPORTANT NOTES FOR CLAUDE CODE

1. **Preserve existing files**: Don't delete or overwrite existing domain brand guides or homepages yet. These are NEW additions to the system.

2. **Extract accurately**: When extracting sections from the audit, preserve all formatting, examples, tables, and code blocks exactly.

3. **JSON formatting**: Ensure all JSON files are valid (use `json.loads()` to verify).

4. **Python compatibility**: Validator should work with Python 3.8+.

5. **File paths**: Use absolute paths in examples, relative paths in code.

6. **Permissions**: Make validator executable: `chmod +x vocabulary_validator.py`.

7. **Testing**: After creation, test validator on at least one existing homepage to ensure it works.

8. **Documentation links**: Update any internal links to reference new file locations.

9. **Commit message**: Use conventional commit format shown above.

10. **No breaking changes**: This is additive - doesn't modify existing workflows until team adopts.

---

## 🎯 SUCCESS CRITERIA

After Claude Code completes this work, the repository should have:

- ✅ Complete vocabulary guide explaining consciousness language
- ✅ Enforceable generation rules with quality metrics
- ✅ Automated validator that can check any markdown file
- ✅ Comprehensive compliance checklists (EU + US)
- ✅ Example library showing good vs bad vocabulary use
- ✅ Integration README explaining changes and usage
- ✅ All files properly formatted and validated
- ✅ Git commit documenting the update

The team can then use these tools to:

- Validate existing content
- Guide new content creation
- Train AI assistants on proper vocabulary
- Track compliance progress
- Maintain brand consistency

---

## 📊 EFFORT ESTIMATES

| Task | Effort | Priority |
|------|---------|----------|
| Core vocabulary guide | 30 hours | P1 |
| Generation rules | 20 hours | P1 |
| Tone system v2 doc | 15 hours | P1 |
| Validator implementation | 40 hours | P2 |
| JSON term lists | 10 hours | P2 |
| Quality metrics tool | 20 hours | P2 |
| EU compliance checklist | 15 hours | P3 |
| US compliance checklist | 15 hours | P3 |
| Example library | 25 hours | P4 |
| Integration README | 10 hours | P5 |
| Testing & validation | 20 hours | All |
| **Total** | **220 hours** | **~6 weeks** |

---

## 🗓️ IMPLEMENTATION TIMELINE

### Week 1-2: Foundation
- Create directory structure
- Extract and create core documents (Priority 1)
- Initial testing of documentation

### Week 3-4: Enforcement
- Build validator and quality metrics tools (Priority 2)
- Create term lists (blocked, required)
- Test validator on existing content

### Week 5: Compliance
- Create compliance checklists (Priority 3)
- Document effort estimates and timelines
- Map current state against requirements

### Week 6: Examples & Integration
- Build example library (Priority 4)
- Create integration README (Priority 5)
- Final testing and documentation

### Week 7-8: Migration
- Apply to core homepages (lukhas.ai, .dev, .id)
- Apply to product pages
- Validate improvements with metrics

---

## 📖 HOW TO USE THIS GUIDE

### For Claude Code (AI Agent)

1. **Follow steps sequentially** (1 → 8)
2. **Extract content from audit** using section numbers referenced
3. **Create files as specified** with exact paths
4. **Validate** all JSON and Python before committing
5. **Test validator** on at least one existing file
6. **Commit with template** message provided above

### For Human Developers

1. **Review audit** (`CLAUDE_TONE_COMPLIANCE_AUDIT_2025-11-10.md`)
2. **Understand changes** in each section
3. **Test validator** on new content before publishing
4. **Track compliance** using checklists
5. **Reference examples** when writing content

---

**Created**: 2025-11-10
**Source**: Claude Tone & Compliance Audit
**Next Steps**: Execute implementation workflow (Steps 1-8)
**Questions**: Reference audit for detailed rationale behind each recommendation
