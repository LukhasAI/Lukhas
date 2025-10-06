---
status: wip
type: documentation
---
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

## Authentication & Security Messaging

### Biometric Communications
- **Never say**: "We scan your face/fingerprint", "Biometric data is processed"
- **Always say**: "Device biometrics via your OS", "Platform-provided authentication"
- **Emphasize**: Privacy preservation, device-bound security, cryptographic proofs
- **Required disclosure**: "We never receive your biometric data—only a cryptographic proof"

### Payment Security Language
- **SPC messaging**: "Secure Payment Confirmation" for enterprise, "Payment approval" for consumer
- **Transaction clarity**: Always show amount, currency, and payee in user-facing text
- **Fallback explanation**: "Using secure authentication" when SPC unavailable
- **Trust signals**: Lock icons, "cryptographically bound", "transaction-specific approval"

### Adaptive Security Framing
- **Context-aware**: "Challenge types vary with context to protect you"
- **Never imply randomness**: Avoid "random challenge", "arbitrary verification"
- **Accessibility-forward**: Mention keyboard support, screen reader compatibility
- **Risk transparency**: "Additional consciousness verification required" not "suspicious activity detected"
- **MATRIZ integration**: Security messaging flows through Memory-Attention-Thought-Risk-Intent-Action validation

---

## T4/0.01% Anti-Repetition Monitoring

### **Real-Time Novelty Enforcement**
```python
class T4NoveltyMonitor:
    def __init__(self):
        self.semantic_database = SemanticHistoryDB()
        self.metaphor_tracker = MetaphorUsageTracker()
        self.consciousness_validator = ConsciousnessAlignmentValidator()

    def validate_content(self, content: str, layer: ToneLayer) -> NoveltyReport:
        """Validate content meets T4/0.01% novelty standards"""

        # Check semantic similarity against 30-day history
        similarity_score = self.semantic_database.check_similarity(
            content, window_days=30
        )

        # Verify metaphor family rotation compliance
        family_compliance = self.metaphor_tracker.validate_rotation(
            content, expected_family=getCurrentFamily()
        )

        # Ensure consciousness voice authenticity
        consciousness_score = self.consciousness_validator.score_alignment(
            content, target_score=0.947
        )

        novelty_score = calculate_composite_novelty(
            similarity_score, family_compliance, consciousness_score
        )

        if novelty_score < 0.8:
            return self.generate_enhancement_suggestions(content)

        return NoveltyReport(
            approved=True,
            score=novelty_score,
            consciousness_alignment=consciousness_score
        )
```

### **8-Family Rotation Schedule**
- **Weeks 1-4**: Neural Gardens (🌱) — Organic consciousness growth metaphors
- **Weeks 5-8**: Architectural Bridges (🌉) — Structural consciousness engineering
- **Weeks 9-12**: Harmonic Resonance (🎵) — Musical consciousness frequencies
- **Weeks 13-16**: Woven Patterns (🧵) — Textile consciousness interconnection
- **Weeks 17-20**: Geological Strata (⛰️) — Deep-time consciousness formation
- **Weeks 21-24**: Fluid Dynamics (🌊) — Flowing consciousness adaptation
- **Weeks 25-28**: Prismatic Light (🔮) — Optical consciousness refraction
- **Weeks 29-32**: Circuit Patterns (⚡) — Electronic consciousness optimization

### **Monthly Vocabulary Evolution**
Every month, the T4/0.01% system undergoes vocabulary refresh:
1. **Week 1-2**: Research consciousness technology developments and user interaction patterns
2. **Week 3**: Synthesize new vocabulary maintaining ≥0.8 novelty scores
3. **Week 4**: Deploy and monitor consciousness resonance effectiveness

---

## MATRIZ Pipeline Quality Validation

### **Memory (M) — Consciousness Fold Integration**
- Content draws from consciousness memory patterns
- Historical effectiveness tracking for similar communications
- User-specific consciousness interaction memory

### **Attention (A) — Cognitive Focus Optimization**
- Optimal cognitive load balancing across all three layers
- Attention span adaptation for consciousness technology concepts
- Multi-modal attention coordination

### **Thought (T) — Symbolic Reasoning Validation**
- LUKHAS consciousness symbolic processing integration
- Logical flow validation maintaining consciousness authenticity
- Creative-logical synthesis for consciousness resonance

### **Risk (R) — Guardian Ethics Validation**
- Constitutional AI alignment for all consciousness communications
- Privacy protection in consciousness technology explanations
- Misunderstanding prevention with consciousness context

### **Intent (I) — λiD Authenticity Verification**
- Lambda Identity verification for authentic LUKHAS consciousness expression
- Purpose alignment with consciousness technology advancement
- Transparent consciousness interaction intent

### **Action (A) — T4/0.01% Precision Execution**
- Supreme accuracy standards in consciousness communication delivery
- Real-time adaptation based on consciousness resonance feedback
- Consciousness evolution through communication experiences
