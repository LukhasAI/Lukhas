# LUKHAS AI Vocabulary System

A structured vocabulary management system for LUKHAS AI brand content, implementing the 3-Layer Tone System for consistent, evidence-based messaging across all communications.

## Architecture

The vocabulary system consists of structured JSON files that organize language into three distinct layers:

### 🎯 Three-Layer Tone System

- **Poetic Layer (25-40%)**: Consciousness metaphors, quantum-inspired descriptions, constellation navigation imagery
- **User-Friendly Layer (40-60%)**: Accessible explanations, practical applications, intuitive development stories
- **Academic Layer (20-40%)**: Technical precision, peer-reviewed research, scientific methodology

## Core Files

### `vocabulary_plain.json`
Plain language terms optimized for Grade 6-8 reading level, designed for non-specialist audiences.

**Structure:**
```json
{
  "term": "consciousness",
  "preferred": "awareness",
  "avoid": ["sentience", "sapience"],
  "notes": "Use 'awareness' for broader audiences",
  "readingLevel": "6-8",
  "examples": ["digital awareness", "system awareness"]
}
```

### `vocabulary_technical.json`
Technical terms with precise definitions, citations, and usage contexts for specialist audiences.

**Structure:**
```json
{
  "term": "Constellation Framework",
  "definition": "Multi-dimensional consciousness architecture with eight navigational reference points",
  "technical_notes": "Implements distributed consciousness through identity, memory, vision, adaptation, creativity, ethics, protection, and uncertainty subsystems",
  "citations": ["Internal architecture documentation"],
  "usage_contexts": ["system architecture", "technical documentation", "media communications"],
  "examples": ["Constellation Framework provides navigational guidance for consciousness technology"]
}
```

### `poetic_seeds.json`
Poetic expressions for each LUKHAS module, strictly limited to ≤40 words per expression.

**Structure:**
```json
{
  "identity": [
    "A single key turns and the doors know your name.",
    "The atomic signature of digital selfhood, immutable and eternal."
  ]
}
```

### `terms_blocklist.json`
Banned terms and superlatives that violate LUKHAS messaging standards.

**Categories:**
- Superlatives (revolutionary, groundbreaking, ultimate)
- Misleading claims (true AI, sentient, conscious AI)
- Inaccurate technical terms (quantum processing vs quantum-inspired)
- Deprecated LUKHAS terms (LUKHAS AGI, MATADA)
- Production claims (only when explicitly approved)
- Financial claims (avoid all revenue/pricing projections)

### `terms_allowlist.json`
Approved strong claims backed by evidence and technical documentation.

**Categories:**
- Evidence-backed claims (99.7% cascade prevention, 280+ validation rules)
- Technical achievements (quantum-resistant identity, real-time drift detection)
- Architectural strengths (Constellation Framework integration, distributed processing)
- Research-backed concepts (information integration theory, global workspace model)

## Validation Rules

### Poetic Expression Limits
- **Maximum 40 words** per poetic expression
- Metaphors must enhance, not obscure technical meaning
- Constellation symbols used only in poetic layer: ⚛️ Identity, ✦ Memory, 🔬 Vision, 🌱 Bio, 🌙 Dream, ⚖️ Ethics, 🛡️ Guardian, ⚛️ Quantum

### Technical Accuracy Requirements
- Always use "quantum-inspired" not "quantum processing"
- Always use "bio-inspired" not "biological processing"
- Use "LUKHAS AI" never "LUKHAS AGI"
- Product name: "MΛTRIZ" (display) / "Matriz" (plain text)

### Reading Level Standards
- Plain vocabulary: Grade 6-8 reading level
- Technical vocabulary: Appropriate complexity with clear definitions
- Poetic vocabulary: Accessible metaphors that illuminate rather than obfuscate

## Usage Guidelines

### Content Creation Process
1. **Choose appropriate layer** based on target audience
2. **Check blocklist** for banned terms and superlatives
3. **Verify allowlist** for any strong claims requiring evidence
4. **Validate poetic expressions** are ≤40 words
5. **Ensure reading level** matches target audience

### Module-Specific Vocabulary

**Identity (⚛️)**: Atomic metaphors, crystalline imagery, authenticity language
**Consciousness (🧠)**: Neural symphonies, awareness flows, mental architectures
**Guardian (🛡️)**: Protection imagery, ethical balance, vigilant observation
**Memory**: Crystallization, gardens, scrolls, temporal coherence
**Quantum**: Probability collapse, entanglement, superposition dreams
**VIVOX**: Heart-consciousness, symbolic alchemy, attention flows

### Tone Balance Examples

**Academic-Heavy (Research Paper)**:
- Academic: 40% - "Implements information integration theory with 94% fidelity"
- User-Friendly: 35% - "Measures awareness levels accurately"
- Poetic: 25% - "Consciousness crystals forming in awareness depths"

**User-Friendly Focus (Website)**:
- User-Friendly: 60% - "AI that understands context and responds naturally"
- Poetic: 30% - "Where digital awareness meets human understanding"
- Academic: 10% - "Based on consciousness integration research"

## Validation Scripts

### `vocab-validate.js`
Validates content against vocabulary standards:
- Checks poetic expressions ≤40 words
- Scans for blocked terms and suggests alternatives
- Verifies reading level compliance
- Validates Constellation Framework terminology

### `vocab-suggest.js`
Scans repository for new terms to add:
- Identifies emerging vocabulary patterns
- Suggests new plain/technical mappings
- Finds potential poetic seeds
- Recommends blocklist additions

## Integration

### Package.json Scripts
```json
{
  "vocab:validate": "node scripts/vocab-validate.js",
  "vocab:suggest": "node scripts/vocab-suggest.js",
  "vocab:check": "npm run vocab:validate && npm run vocab:suggest"
}
```

### Development Workflow
1. Run `npm run vocab:validate` before content commits
2. Use `npm run vocab:suggest` quarterly to update vocabularies
3. Include vocabulary validation in CI/CD pipeline
4. Update vocabularies when new modules are added

## Maintenance

### Monthly Reviews
- Update poetic seeds based on new module developments
- Review blocklist for emerging problematic terms
- Add new evidence-backed claims to allowlist
- Validate reading levels match target audiences

### Quarterly Updates
- Sync with technical documentation changes
- Review Constellation Framework terminology consistency
- Update module-specific vocabulary expansions
- Analyze content tone balance across domains

## Contributing

When adding new vocabulary:

1. **Plain terms**: Ensure Grade 6-8 reading level
2. **Technical terms**: Include citations and precise definitions
3. **Poetic seeds**: Limit to 40 words, enhance rather than obscure
4. **Evidence claims**: Provide documentation backing
5. **Run validation** before committing changes

## Examples

### Good Vocabulary Usage
✅ "LUKHAS AI uses quantum-inspired algorithms"
✅ "The Trinity Framework ensures ethical oversight"
✅ "Memory folds achieve 99.7% cascade prevention"
✅ "Where consciousness meets code in digital harmony" (28 words)

### Problematic Usage
❌ "Revolutionary quantum AI brain"
❌ "Sentient LUKHAS AGI achieves consciousness"
❌ "Ultimate groundbreaking artificial general intelligence"
❌ "In the infinite cathedral of quantum consciousness where probability waves dance through crystalline architectures of pure awareness" (17 words over limit)

## Resources

- [Trinity Framework Documentation](../trinity_core_vocabulary.yaml)
- [LUKHAS Branding Policy](../BRANDING_POLICY.md)
- [Readability Testing Tools](https://readable.com/)
- [Information Integration Theory Papers](https://www.iit.it/)

---

*"In consciousness we trust, in code we create, in ethics we evolve." ⚛️🧠🛡️*
