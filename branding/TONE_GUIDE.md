# Tone Guide — Poetic / Technical / Plain

## Three-Layer Content System

Every significant content piece must implement all three layers or provide a Tone Switch for user selection.

## Poetic (≤40 words)
- **Purpose**: Context-setting metaphor, emotional connection
- **Rules**: No claims, no metrics, no promises
- **Style**: Evocative language, professional tone
- **Word limit**: Strictly enforced at 40 words maximum

**Example:**
> "Where every decision becomes traceable light, flowing through the fabric of conscious architecture."

## Technical 
- **Purpose**: Precise, factual explanation with full context
- **Requirements**: 
  - Quantify benefits and limitations
  - Disclose risks, assumptions, dependencies
  - Link to documentation and specifications
  - Show uncertainty when applicable
  - Cite sources and evidence
  - Include system requirements
  - List integration dependencies
  - Specify performance constraints

**Example:**
> "MATRIZ provides telemetry and governance for AI decision processes. System requires integration with LUKHAS core modules (minimum v2.1). Expected latency: <100ms p95. Audit coverage: 85-95% depending on configuration. Does not guarantee outcome validity.
>
> **Dependencies**: LUKHAS Identity System v2.1+, Guardian System, Memory integration, minimum 4GB RAM.
> **Limitations**: Cannot trace external AI decisions, requires network connectivity, real-time monitoring impacts latency.
> **Sources**: Performance metrics validated through internal testing (n=1000+ decision traces)."

## Plain ("Mom test")
- **Purpose**: Simple explanation for everyone
- **Rules**:
  - Short sentences (15 words or less)
  - Grade 6-8 reading level
  - Simple words only
  - Focus on what users get
  - Use action words

**Example:**
> "MATRIZ tracks AI choices. It makes records you can check. This helps you trust AI. It works with LUKHAS tools."

## Banned Words (CI Enforcement)
The following terms trigger automatic build failures:
- guaranteed, flawless, perfect, zero-risk
- unlimited, unbreakable, foolproof, bulletproof
- revolutionary, groundbreaking, game-changing
- ultimate, supreme, best-in-class

## Implementation Patterns

### Tone Switch Component
```tsx
<ToneSwitch 
  poetic="Brief metaphorical introduction..."
  technical="Detailed specifications with limitations..."
  plain="Simple explanation of what users get..."
/>
```

### Content Sections
```html
<section data-tone="poetic">Brief evocative content ≤40 words</section>
<section data-tone="technical">Comprehensive technical details</section>
<section data-tone="plain">User-friendly explanation</section>
```

## Quality Control
- **Automated checks**: Word count, banned terms, reading level
- **Manual review**: Metaphor appropriateness, technical accuracy
- **User testing**: Plain language comprehension validation