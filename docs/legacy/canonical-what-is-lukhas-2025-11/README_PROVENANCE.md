# Canonical "What is LUKHAS?" Content Archive

**Archive Date**: 2025-11-10
**Original Location**: `lukhas_website/WEBSITE_WHAT_IS_LUKHAS.md`
**Last Updated**: November 5, 2025 (per file metadata)
**Status**: WIP (work in progress)
**Archive Reason**: Preservation of canonical website content for reference during multi-model documentation review

---

## Purpose of This Archive

This directory preserves the **canonical "What is LUKHAS?" website content** as it existed during the November 2025 documentation audit and multi-model review process.

### Why Archived

1. **Historical Reference**: Captures the approved messaging, tone, and positioning from November 2025
2. **Multi-Model Review**: Provides reviewers (GPT, Claude, Gemini) with source material for tone/compliance audits
3. **Content Reuse**: Serves as source material for:
   - Developer quickstart guides
   - Homepage content for lukhas.dev, lukhas.ai, lukhas.com
   - Elevator summaries and executive positioning
   - API documentation examples

### Content Structure

The archived `WEBSITE_WHAT_IS_LUKHAS.md` contains:

- **3-Layer Tone System** implementation:
  - 🎭 Poetic Layer (~30%): Inspirational, metaphorical
  - 🌈 User-Friendly Layer (~50%): Accessible, clear
  - 🎓 Academic/Technical Layer (~20%): Precise specifications

- **Complete website sections**:
  1. Hero Section (all 3 layers)
  2. The LUKHAS Revolution (5 solved problems)
  3. How LUKHAS Works (architecture)
  4. Core Features (specifications table)
  5. Use Cases (individuals, families, business, healthcare)
  6. Technology Deep Dive (technical stack)
  7. Getting Started (pricing, developer quickstart)

### Key Content Highlights

**The 5 Solved Problems**:
1. Password Paradox (multi-modal passwords)
2. Understanding Gap (GLYPH symbolic language)
3. Privacy Invasion (zero-knowledge proofs)
4. Relationship Reset (persistent memory)
5. Consciousness Question (emergent consciousness)

**Technical Specifications**:
- GLYPH Engine: 10,000 symbols/second
- Colony Consensus: <500ms decision time
- Memory System: 99.7% cascade prevention
- Quantum Security: Kyber-1024, Dilithium-5
- API Throughput: 50,000 req/sec

**Developer Snippet** (from Section 6):
```python
from lukhas import LUKHAS
lukhas = LUKHAS(api_key="your-key")
companion = lukhas.create_companion()
response = companion.chat("Hello, LUKHAS!")
```

---

## Relationship to Current Documentation Work

### Integration Opportunities

This canonical content can inform:

1. **lukhas.ai homepage** (flagship domain)
   - Use Hero Section with 3-layer blend
   - Feature "5 Solved Problems" prominently
   - Adapt tone to 35% Poetic / 45% User-Friendly / 20% Academic

2. **lukhas.dev homepage** (developer platform)
   - Extract Developer Quick Start from Section 6
   - Use Technical Stack from Section 5
   - Focus on API specifications and code examples
   - Adapt tone to 60% Academic / 25% User-Friendly / 15% Poetic

3. **lukhas.com homepage** (corporate hub)
   - Use Business Use Cases from Section 4
   - Feature Enterprise pricing tier
   - Emphasize security and compliance
   - Adapt tone to 50% User-Friendly / 40% Academic / 10% Poetic

4. **Elevator Summaries** (150-250 words)
   - Distill Layer 2 (User-Friendly) content from Hero Section
   - Focus on "What problem?" and "Who benefits?"
   - Avoid jargon while preserving key concepts

### Divergence from Current Strategy

**Notable differences** from Phase 1 MVP documentation approach:

1. **Pricing mentioned**: This content includes specific pricing ($0 / $29 / $99 / Enterprise)
   - Current strategy: No pricing in documentation phase
   - Resolution: Strip pricing for docs, preserve for future website

2. **Product claims**: "World's first Universal Language and Consciousness System"
   - Current strategy: T4 Precision (avoid superlatives)
   - Resolution: Reframe as evidence-based claims for MVP docs

3. **Feature completeness**: Describes features as complete/shipping
   - Current strategy: MATRIZ 87% complete, transparent about WIP
   - Resolution: Align messaging with actual implementation status

4. **Use cases depth**: Extensive use case library
   - Current strategy: Focus on developer use cases first (Phase 1)
   - Resolution: Preserve for Phase 2, prioritize dev docs now

---

## Usage Guidelines

### For Content Creators

When creating new LUKHAS content, reference this archive for:

✅ **Approved tone balance**: See how 3 layers blend in practice
✅ **Key messaging**: "5 Solved Problems" framework
✅ **Technical specs**: Verified performance numbers
✅ **Code examples**: Python SDK usage patterns
✅ **Architecture diagrams**: ASCII art structure visualization

❌ **Don't copy verbatim**: Adapt to domain-specific audience and current implementation status
❌ **Don't reuse pricing**: Pricing strategy may have changed since Nov 2025
❌ **Don't assume feature completeness**: Verify current implementation before claiming capabilities

### For Reviewers (GPT, Claude, Gemini)

This content demonstrates:

- **Tone system in practice**: Evaluate whether 3-layer blend creates clarity or confusion
- **T4 compliance**: Assess claims against Truth/Transparency/Testability/Temperance
- **Technical accuracy**: Verify specs match MATRIZ capabilities
- **Jargon accessibility**: Test whether terms like "Fold Memory" and "Colony Consensus" are sufficiently explained

---

## Files in This Archive

```
docs/legacy/canonical-what-is-lukhas-2025-11/
├── README_PROVENANCE.md        # This file - provenance and usage
├── WEBSITE_WHAT_IS_LUKHAS.md   # Canonical website content (Nov 5, 2025)
└── [Future: DEVELOPER_QUICKSTART_API.md - Enhanced quickstart created Nov 10]
```

---

## Next Steps

1. **Developer QuickStart Addition**: User-created enhanced quickstart with curl/Python/Node.js examples can be added to this archive
2. **Multi-Model Review**: Share this archive location with GPT/Claude/Gemini for tone/compliance audits
3. **Content Extraction**: Mine this content for Phase 1 MVP homepages (lukhas.dev, lukhas.ai, lukhas.cloud, lukhas.id)
4. **Tone Analysis**: Use as baseline for evaluating whether 3-layer tone system works in practice

---

**Archived by**: Claude Code
**Session**: Multi-model documentation review preparation
**Related Work**:
- `docs/gpt_packages/LUKHAS_ECOSYSTEM_REVIEW_PACKAGE.md`
- `docs/gpt_packages/GPT_STRATEGIC_AUDIT_PROMPT.md`
- `docs/gpt_packages/CLAUDE_TONE_COMPLIANCE_AUDIT_PROMPT.md`
- `docs/gpt_packages/GEMINI_TECHNICAL_SEO_AUDIT_PROMPT.md`
- `branding/config/domain_registry.yaml` (Phase 1 MVP strategy)

**Preservation Commitment**: This archive will be maintained as historical reference even as new content is created, ensuring we can always trace the evolution of LUKHAS messaging and positioning.
