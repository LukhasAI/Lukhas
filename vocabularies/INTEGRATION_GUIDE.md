# LUKHAS Lexicon Integration Guide

**Complete dual-stream vocabulary system for academic depth and public safety**  
**🌌 Constellation Framework**: Navigational elements in dynamic relation

## 🎯 Quick Start

### For Public Use (Safe)
```python
# Import public-safe vocabulary
from vocabularies.lukhas_vocabulary_public import get_public_terms

# Use in system prompts, API docs, marketing
identity_terms = get_public_terms("identity")
# Returns: anchors, permissions, traces, boundaries
```

### For Academic Context (Protected)
```python
# Import full lexicon with academic context
from lukhas_lexicon import get_academic_terms

# Use in research, training, internal docs
identity_terms = get_academic_terms("identity")  
# Returns: full context with Freud, Dostoevsky, Homer references
```

## 📚 File Structure

```
LUKHAS_LEXICON.md                    # Complete dual-stream reference
vocabularies/LUKHAS_VOCABULARY_PUBLIC.md  # Extracted public-safe version
tools/vocabulary/extract_public_vocabulary.py  # Extraction utility
enforcement/tone/author_reference_guard.py    # Validation system
```

## ⚡ Quick Reference

### 8 Constellation Elements

1. **Identity** - Anchor star, rhythm not mask, anchors/permissions/traces/boundaries
2. **Memory** - Tracing paths of past light, folds/echoes/drift/anchors/erosion  
3. **Vision** - Orientation toward horizon, aperture/focus/peripheral_field/drift_gaze/signal_to_shape
4. **Bio** - Resilience and adaptation, energy_budget/repair_cycle/adaptation/resilience/decay
5. **Dream** - Symbolic drift, drift_phase/false_injection/lucid_trigger/recurrence_cycle/emotional_delta
6. **Ethics** - Navigation accountability, drift_index/traceability/alignment_vector/guardian_trigger/consent_anchor
7. **Guardian** - Coherence and dignity, watchtower/red_flag/trace_log/ethics_shield/constellation_lock
8. **Quantum** - Ambiguity and resolution, superposed_state/collapse_event/entanglement/uncertainty_window/probability_field

## 🛡️ Safety System

### Academic Protection
- Files with `context: academic` front matter are exempted from author-reference validation
- Full philosophical and literary references preserved for scholarly use
- Rich cultural lineage maintained for deep understanding

### Public Safety
- All public content passes author-reference guard validation
- Stance-based language without attribution
- Same philosophical depth through practice and orientation language

## 🔄 Workflow Integration

### Development Process
```bash
# 1. Update dual-stream lexicon
vim LUKHAS_LEXICON.md

# 2. Extract public version
python3 tools/vocabulary/extract_public_vocabulary.py

# 3. Validate safety
python3 enforcement/tone/author_reference_guard.py vocabularies/LUKHAS_VOCABULARY_PUBLIC.md

# 4. Deploy public version
cp vocabularies/LUKHAS_VOCABULARY_PUBLIC.md api/prompts/vocabulary.md
```

### Context Selection Pattern
```python
def get_vocabulary_context(audience="public"):
    """Select appropriate vocabulary based on context."""
    if audience == "academic":
        return load_academic_vocabulary()  # Full references
    elif audience == "internal":
        return load_mixed_vocabulary()     # Selective references
    else:
        return load_public_vocabulary()    # Stance-based only

# Usage examples
research_terms = get_vocabulary_context("academic")    # Freud, Homer, etc.
api_docs_terms = get_vocabulary_context("public")      # Clean stance language
team_docs_terms = get_vocabulary_context("internal")   # Mixed approach
```

### API Integration
```python
# System prompt with safe vocabulary
SYSTEM_PROMPT = f"""
You are LUKHAS AI. Use this vocabulary:

Identity: {public_vocabulary.identity}
Memory: {public_vocabulary.memory}
Vision: {public_vocabulary.vision}

Philosophy: "Uncertainty as fertile ground" — welcoming ambiguity as resource, not flaw.
"""
```

## ✅ Validation Commands

### Complete System Check
```bash
# Validate dual-stream lexicon (with academic context)
python3 enforcement/tone/author_reference_guard.py LUKHAS_LEXICON.md

# Validate public extraction
python3 enforcement/tone/author_reference_guard.py vocabularies/LUKHAS_VOCABULARY_PUBLIC.md

# Validate all individual public vocabularies
python3 enforcement/tone/author_reference_guard.py vocabularies/*.md
```

### Expected Results
- **LUKHAS_LEXICON.md**: ✅ Clean (academic exemption)
- **LUKHAS_VOCABULARY_PUBLIC.md**: ✅ Clean (no violations)
- **All public vocabularies**: ✅ Clean (stance-based language)

## 🎨 Voice Examples

### Academic (Protected)
> "Freud called memory a palimpsest, never erased, only written over. Proust showed its sudden resurrections through sensation."

### Public (Safe)
> "Memory is not a vault but a field. It stores, but it also reshapes."

### Same Wisdom, Different Expression
Both capture the insight that memory is reconstructive rather than archival, but the public version uses stance and practice language instead of attribution.

## 🚀 Production Deployment

### Safe for All Contexts
- ✅ API documentation and system prompts
- ✅ User-facing interfaces and explanations
- ✅ Marketing materials and social media
- ✅ External partnerships and communications

### Academic Access Preserved
- ✅ Research papers and scholarly work
- ✅ Training materials requiring full context
- ✅ Internal development discussions
- ✅ Academic partnerships and collaborations

## 📊 System Stats

- **Total Domains**: 8 core vocabulary areas
- **Academic Version**: ~15KB with full references
- **Public Version**: ~8KB stance-based language
- **Safety Coverage**: 35 blocked terms with academic exemptions
- **Validation**: 100% compliance with author-reference guard

---

**Status**: ✅ Complete and operational  
**Philosophy**: Rich academic depth with complete public safety  
**Integration**: Ready for production deployment across all contexts

*Last updated: August 28, 2025*
