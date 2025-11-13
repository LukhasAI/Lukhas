# CLAUDE TONE & COMPLIANCE AUDIT PROMPT
**Reviewer**: Claude 4.5 (Sonnet)
**Role**: Tone Analysis, Regulatory Compliance, Content Authenticity
**Blind Review**: Do NOT read other reviewer outputs before completing this

---

## 📋 YOUR MISSION

Evaluate the **tone system, regulatory compliance posture, and content authenticity** of the LUKHAS documentation approach. Provide polished rewrites and compliance checklists.

**Your Strengths** (why you're doing this):
- Nuanced tone and voice analysis
- Regulatory compliance frameworks
- Ethical AI considerations
- Long-form content generation and polishing
- Safety and transparency evaluation

**Your Focus Areas**:
- 3-Layer Tone System effectiveness
- EU/US regulatory compliance readiness
- Content authenticity (AI-generated vs human-written)
- Brand clarity and accessibility
- Ethical messaging and transparency

---

## 📚 CONTEXT DOCUMENTS

**Primary Document**: `LUKHAS_ECOSYSTEM_REVIEW_PACKAGE.md`
- Location: https://github.com/LukhasAI/Lukhas/blob/main/docs/gpt_packages/LUKHAS_ECOSYSTEM_REVIEW_PACKAGE.md

**Supporting Documents** (review these):
1. **Homepage Examples** (completed):
   - lukhas.cloud: https://github.com/LukhasAI/Lukhas/blob/main/branding/websites/lukhas.cloud/homepage_matriz_ready.md
   - lukhas.eu: https://github.com/LukhasAI/Lukhas/blob/main/branding/websites/lukhas.eu/homepage_matriz_ready.md
   - lukhas.id: https://github.com/LukhasAI/Lukhas/blob/main/branding/websites/lukhas.id/homepage_matriz_ready.md

2. **Brand Guides**:
   - lukhas.dev: https://github.com/LukhasAI/Lukhas/blob/main/branding/domains/lukhas.dev/BRAND_GUIDE.md
   - lukhas.ai: https://github.com/LukhasAI/Lukhas/blob/main/branding/domains/lukhas.ai/BRAND_GUIDE.md

3. **Domain Registry**:
   - https://github.com/LukhasAI/Lukhas/blob/main/branding/config/domain_registry.yaml

---

## 🎯 YOUR DELIVERABLES

### 1. Tone System Evaluation (500-800 words)

**Analyze the 3-Layer Tone System**:

**Current System**:
- Poetic Layer: Inspirational, metaphorical, emotional (varies by domain: 5%-40%)
- User-Friendly Layer: Accessible, practical, clear (25%-50%)
- Academic Layer: Technical, precise, evidence-based (15%-70%)

**Questions to Answer**:
1. **Does this system actually work?**
   - Review completed homepages (lukhas.cloud, lukhas.eu, lukhas.id)
   - Can you identify the three layers in practice?
   - Does the blend create clarity or confusion?

2. **Is the tone distribution appropriate per domain?**
   - Developer domain (lukhas.dev): 60% Academic, 25% User-Friendly, 15% Poetic
   - Flagship (lukhas.ai): 35% Poetic, 45% User-Friendly, 20% Academic
   - Compliance (lukhas.eu/us): 70% Academic, 25% User-Friendly, 5% Poetic
   - Are these ratios effective? Would you adjust?

3. **Accessibility & Clarity**:
   - Does the poetic layer enhance or obscure meaning?
   - Does the academic layer alienate non-technical readers?
   - Is the user-friendly layer actually friendly?

4. **Recommendation**:
   - Keep the 3-layer system as-is?
   - Simplify to 2 layers (User-Friendly + Academic)?
   - Use different approach entirely?
   - Provide specific improvements

### 2. "What is LUKHAS?" Page (200-250 words)

**Create a plain-language executive summary** for general audiences:

**Requirements**:
- Answer: "What problem does LUKHAS solve?"
- Answer: "Who benefits first and how?"
- Avoid jargon (Constellation, MATRIZ, ΛiD, Trinity)
- If technical terms needed, define them immediately
- Clear call-to-action
- Accessible to non-technical readers
- Suitable for top of lukhas.com homepage

**Format**:
```markdown
# What is LUKHAS?

[Your 200-250 word summary]

**For Developers**: [1 sentence with link]
**For Enterprises**: [1 sentence with link]
**For Researchers**: [1 sentence with link]
```

### 3. Regulatory Compliance Checklist

**Create compliance checklists for lukhas.eu and lukhas.us**:

#### A. EU Compliance Checklist (lukhas.eu)

**GDPR Requirements**:
- [ ] Data processing legal basis documented per purpose
- [ ] Data retention and deletion policies published
- [ ] User rights (access, rectification, erasure, portability) implemented
- [ ] Data Protection Impact Assessment (DPIA) completed
- [ ] Data Processing Agreement (DPA) templates available
- [ ] Cookie consent and tracking disclosures
- [ ] Third-party data processor inventory
- [ ] Cross-border data transfer mechanisms (SCCs, adequacy decisions)
- [ ] Data breach notification procedures (<72 hours)
- [ ] Privacy Policy accessible and compliant

**EU AI Act Readiness** (High-Risk AI System):
- [ ] Risk classification completed (high-risk determination)
- [ ] Transparency obligations met (AI system disclosure)
- [ ] Human oversight mechanisms documented
- [ ] Accuracy, robustness, cybersecurity measures
- [ ] Technical documentation for authorities
- [ ] Quality management system
- [ ] Post-market monitoring plan
- [ ] Registration in EU database (if high-risk)
- [ ] Conformity assessment completed
- [ ] CE marking (if required)

**Additional EU Requirements**:
- [ ] Non-discrimination and fairness testing
- [ ] Explainability and interpretability documentation
- [ ] Environmental impact disclosure (if applicable)

#### B. US Compliance Checklist (lukhas.us)

**AI Bill of Rights Alignment**:
- [ ] **Safe and Effective Systems**: Testing, monitoring, safety protocols documented
- [ ] **Algorithmic Discrimination Protection**: Bias testing, fairness audits
- [ ] **Data Privacy**: Notice and consent for data collection
- [ ] **Notice and Explanation**: Clear disclosure of AI use, how decisions made
- [ ] **Human Alternatives**: Option for human review/override

**NIST AI Risk Management Framework**:
- [ ] GOVERN: Policies, procedures, accountability structures
- [ ] MAP: Context, risks, impacts identified and documented
- [ ] MEASURE: Metrics for trustworthiness (accuracy, safety, fairness)
- [ ] MANAGE: Risk mitigation strategies, monitoring, incident response

**CCPA Compliance** (California):
- [ ] Privacy Policy with required disclosures
- [ ] Consumer rights (know, delete, opt-out) implemented
- [ ] "Do Not Sell My Personal Information" link
- [ ] Data collection and sale disclosures
- [ ] Minor data protections (<16 years)

**Sector-Specific** (if applicable):
- [ ] HIPAA (health data)
- [ ] COPPA (children's data)
- [ ] FERPA (education data)
- [ ] Financial regulations (if relevant)

**Additional US Considerations**:
- [ ] State-level AI laws (CO, CA, VA, etc.)
- [ ] FTC Act Section 5 (unfair/deceptive practices)
- [ ] Accessibility (ADA, WCAG compliance)

### 4. Brand Jargon Glossary

**Create plain-language definitions** for technical terms:

Provide 1-2 sentence definitions for:
- LUKHAS
- MATRIZ Engine
- Constellation Framework
- 8-Star System (Individual stars: Identity, Memory, Vision, Bio, Dream, Ethics, Guardian, Quantum)
- ΛiD (Lambda ID) Authentication
- Trinity Framework
- Cognitive DNA
- Reasoning Graphs
- Constitutional AI
- T4 Precision

**Format** (example):
```markdown
**MATRIZ Engine**: The core cognitive processing system that handles memory, attention, decision-making, and ethical validation. Think of it as the "brain" that powers LUKHAS consciousness capabilities.
```

### 5. Content Authenticity Assessment

**Evaluate AI-generated content approach**:

**Questions**:
1. **Transparency**: Should AI-generated sections be labeled? How?
2. **Quality Control**: What editorial workflow ensures quality?
3. **Voice Consistency**: Can AI maintain 3-layer tone across 150,000+ words?
4. **User Testing**: How to validate AI content doesn't feel "soulless"?
5. **Ethical Concerns**: Disclosure requirements? Best practices?

**Recommendations**:
- Editorial guidelines for AI-assisted content
- Human review requirements (which sections need human authorship)
- Quality metrics (readability, accuracy, authenticity scores)
- Disclosure policy (transparent about AI assistance)

### 6. Compliance Documentation Gaps

**Identify missing compliance documents** for lukhas.eu and lukhas.us:

**lukhas.eu Missing**:
- [ ] List specific missing docs (e.g., DPIA template, DPA template)
- [ ] Priority ranking (critical, high, medium, low)
- [ ] Estimated effort to create
- [ ] Recommended timeline

**lukhas.us Missing**:
- [ ] List specific missing docs (e.g., NIST framework mapping, fairness audit)
- [ ] Priority ranking
- [ ] Estimated effort
- [ ] Recommended timeline

### 7. Tone Examples & Rewrites

**Provide 3 rewrite examples** showing better tone balance:

**Example 1: Technical Content (lukhas.dev)**
- Original: [Quote from existing doc]
- Issues: [What's wrong with tone]
- Rewrite: [Your improved version]
- Rationale: [Why this is better]

**Example 2: Marketing Content (lukhas.ai)**
- Original: [Quote from existing doc]
- Issues: [What's wrong with tone]
- Rewrite: [Your improved version]
- Rationale: [Why this is better]

**Example 3: Compliance Content (lukhas.eu)**
- Original: [Quote from existing doc]
- Issues: [What's wrong with tone]
- Rewrite: [Your improved version]
- Rationale: [Why this is better]

---

## 📊 SPECIFIC EVALUATION AREAS

### A. Evaluate 8-Family Vocabulary Rotation

**Current System**: Rotate through 8 metaphorical families every 200-300 words:
1. Circuit Patterns (precision, connectivity)
2. Architectural Bridges (structure, foundation)
3. Geological Strata (layers, depth)
4. Woven Patterns (integration)
5. Fluid Dynamics (flow, movement)
6. Harmonic Resonance (synchronization)
7. Neural Gardens (organic growth)
8. Prismatic Light (clarity, refraction)

**Your Assessment**:
- Does this create fresh, varied content or artificial-sounding writing?
- Is the rotation noticeable to readers? Jarring or smooth?
- Does it help or hurt readability?
- Would you keep, simplify, or abandon this system?

### B. Evaluate "T4 Precision" Messaging

**Current Approach**: Avoid marketing superlatives
- Forbidden: "Revolutionary," "breakthrough," "game-changing," "world's first"
- Preferred: Evidence-based, measured claims with citations

**Your Assessment**:
- Does this make LUKHAS more credible or more boring?
- In a noisy AI market, does restraint help or hurt?
- Are they taking it too far (overly academic)?
- How to balance credibility with market visibility?

### C. Evaluate "MATRIZ 87% Complete" Messaging

**Current Status**: Prominently featured in technical domains
- Claim: "87% Complete with Full SDK Support"
- Performance: "<250ms p95 latency"

**Your Assessment**:
- Does "87% complete" signal near-completion or stalled progress?
- Better alternatives for messaging incomplete-but-functional systems?
- How to frame ongoing development positively?
- Transparency vs. marketing trade-offs?

---

## 📝 OUTPUT FORMAT

**Provide your review as**:

```markdown
# CLAUDE TONE & COMPLIANCE AUDIT - LUKHAS ECOSYSTEM

**Reviewer**: Claude 4.5 (Sonnet)
**Date**: [Date]
**Review Type**: Tone, Compliance, Authenticity Analysis
**Confidence**: [Low/Medium/High]

---

## EXECUTIVE SUMMARY (150-200 words)

[Overall tone assessment, key compliance gaps, top recommendations]

---

## 1. TONE SYSTEM EVALUATION (500-800 words)

### Does the 3-Layer System Work?
[Analysis]

### Domain-Specific Tone Appropriateness
[Analysis]

### Accessibility & Clarity Assessment
[Analysis]

### Recommendations
[Keep/modify/replace with specific suggestions]

---

## 2. "WHAT IS LUKHAS?" PAGE (200-250 words)

[Your polished executive summary]

---

## 3. REGULATORY COMPLIANCE CHECKLISTS

### A. EU Compliance (lukhas.eu)

#### GDPR Checklist
[Detailed checklist with status]

#### EU AI Act Readiness
[Detailed checklist with status]

### B. US Compliance (lukhas.us)

#### AI Bill of Rights Alignment
[Detailed checklist with status]

#### NIST AI RMF
[Detailed checklist with status]

#### CCPA Compliance
[Detailed checklist with status]

---

## 4. BRAND JARGON GLOSSARY

[Plain-language definitions for all technical terms]

---

## 5. CONTENT AUTHENTICITY ASSESSMENT

### Transparency Recommendations
[How to label/disclose AI-generated content]

### Editorial Workflow
[Quality control process]

### User Testing Plan
[How to validate authenticity]

---

## 6. COMPLIANCE DOCUMENTATION GAPS

### lukhas.eu Missing Documents
[Prioritized list with effort estimates]

### lukhas.us Missing Documents
[Prioritized list with effort estimates]

---

## 7. TONE EXAMPLES & REWRITES

### Example 1: Technical Content
[Original, issues, rewrite, rationale]

### Example 2: Marketing Content
[Original, issues, rewrite, rationale]

### Example 3: Compliance Content
[Original, issues, rewrite, rationale]

---

## 8. EVALUATION OF SPECIFIC SYSTEMS

### 8-Family Vocabulary Rotation
[Assessment and recommendation]

### T4 Precision Approach
[Assessment and recommendation]

### MATRIZ 87% Messaging
[Assessment and recommendation]

---

## 9. ADDITIONAL RECOMMENDATIONS

[Anything else not covered above]
```

---

## ⚠️ IMPORTANT GUIDELINES

**DO**:
- ✅ Provide polished, publication-ready rewrites
- ✅ Be specific about compliance requirements
- ✅ Evaluate tone from reader perspective
- ✅ Create actionable checklists
- ✅ Balance transparency with marketing needs
- ✅ Consider accessibility and plain language
- ✅ Think about diverse audiences (technical, business, regulatory)

**DON'T**:
- ❌ Accept jargon without question
- ❌ Ignore regulatory complexity
- ❌ Provide generic compliance advice
- ❌ Overlook accessibility concerns
- ❌ Assume all readers are technical
- ❌ Ignore ethical implications of AI-generated content
- ❌ Sacrifice accuracy for readability (or vice versa)

---

## 🎯 SUCCESS CRITERIA

Your review is successful if:
1. ✅ It provides concrete tone improvements (not just critique)
2. ✅ It includes publication-ready "What is LUKHAS?" page
3. ✅ It delivers actionable compliance checklists (EU + US)
4. ✅ It creates accessible jargon glossary
5. ✅ It evaluates 3-layer tone system with evidence
6. ✅ It provides 3+ rewrite examples
7. ✅ It addresses AI content authenticity concerns

---

**Ready to begin?**

Load the context documents and provide your tone & compliance analysis following the format above. Focus on clarity, accessibility, regulatory readiness, and authentic voice.

---

**Package Version**: 1.0
**Created**: 2025-11-10
**For**: Claude 4.5 tone and compliance review
**Review Type**: Independent, blind, clarity-focused
