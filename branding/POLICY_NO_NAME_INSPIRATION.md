# 🛡️ No-Name Inspiration Policy

---
context: public
title: No-Name Inspiration Policy
---

## Purpose
Preserve our poetic-yet-grounded voice (retro-modern, tactile, human) without invoking specific authors or schools in public-facing copy. The voice should welcome uncertainty as fertile ground, balance art and science, and remain anchored in factual care.

## Defaults
- **Public contexts** (site copy, product UI, marketing, social): do **not** reference specific thinkers, movements, or texts as authority.
- **Academic contexts** (papers, thesis, appendix, citations, /docs/references/): references allowed, with clear sourcing and restraint.

## Allowed abstractions (safe)
- "comfort with uncertainty"
- "poetic yet grounded voice"
- "holding open questions"
- "negative capability stance" *(as a lowercase stance; not as a proper noun reference)*

## Blocked in public
- Direct name-drops of classic or modern thinkers (see tone/tools/author_blocklist.yaml).
- Claims of "final truth," "sacred authority," or anything that forecloses inquiry.

## Exceptions
Set `context: academic` in the front matter **or** place content under:
- `/docs/references/`
- `/thesis/appendix/`

## Rationale
This policy keeps the tone inclusive, de-mystified, and accessible while keeping a high bar for rigor and safety (⚛️🧠🛡️). It fits our brand validators and CI posture.

---

## 🔧 Implementation

### 1. Validation Tools
- **Author Reference Guard**: `enforcement/tone/author_reference_guard.py`
- **Sanitizer**: `tone/tools/author_reference_sanitizer.py` 
- **Blocklist**: `tone/tools/author_blocklist.yaml`

### 2. CI/CD Integration
```bash
# Add to existing pre-commit hook
python enforcement/tone/author_reference_guard.py || exit 1
```

### 3. Content Review Process
- **Pre-publish scan**: All public content checked automatically
- **PR review**: Violations flagged before merge
- **Emergency sanitization**: Auto-replacements available

---

## 📝 Tone Guidelines

### Core Principles
- **Poetic yet grounded**: Clear, minimal, human
- **Metaphor clarifies**: Never obscures meaning  
- **Uncertainty as fertile ground**: Embrace questions
- **Breathable sentences**: Natural rhythm and flow

### Balance Target
- **40% plain clarity** (grandparent-friendly)
- **40% evocative imagery** (retro-modern, tactile, everyday)
- **20% precise technical** (architecture, safeguards, verifiability)

### Voice Characteristics
- **Never claim final truth**: Hold questions with care
- **Avoid name-dropping**: Focus on stance and practice
- **Anchored and expansive**: Leave reader stable yet opened

---

## 🎭 Example Transformations

### Before (Author-Referenced)
> "Following Keats' concept of Negative Capability, LUKHAS embraces uncertainty like the Zen tradition of sitting with mystery."

### After (Stance-Focused) 
> "LUKHAS isn't a machine for final answers. It's a place where clarity and mystery can sit together until better language arrives."

### Before (Name-Heavy)
> "Drawing from Freudian depth psychology and Einsteinian wonder, the system maintains cosmic curiosity."

### After (Practice-Focused)
> "The system balances logic with imagination, maintaining patient curiosity about what remains unknown."

---

## 🚨 Emergency Procedures

### If Author References Slip Through
1. **Immediate sanitization**: Use automated replacement tool
2. **Content audit**: Scan related materials for similar issues
3. **Team notification**: Alert content creators about policy
4. **Process improvement**: Update validation rules if needed

### Sanitization Mapping
```
Keatsian → poetic yet grounded
Shakespearean → classical dramatic  
Freudian → depth-psychology
Einsteinian → cosmic curiosity
Zen → attentive presence
Taoist → flow-oriented wisdom
```

---

## 📊 Compliance Monitoring

### Success Metrics
- **Zero violations** in public-facing content
- **Fast replacement** when issues detected
- **Tone consistency** across all materials
- **Team adoption** of stance-based language

### Regular Audits
- **Weekly scans** of new content
- **Monthly review** of existing materials  
- **Quarterly policy** updates as needed
- **Annual assessment** of effectiveness

---

**Remember**: We preserve the beauty and depth of the philosophical stance while making it safely our own. The wisdom remains; the attributions fade into practice.

*"We write from a place that welcomes uncertainty as fertile ground."*
