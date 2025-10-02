# Tone Module - LUKHAS 3-Layer Tone System

**Quick Navigation for New Agents**:
- 🚀 **Start Here**: [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) - 5-minute overview
- 📖 **Complete Documentation**: [claude.me](./claude.me) - Full system architecture
- 🎯 **Vendor-Neutral Guide**: [lukhas_context.md](./lukhas_context.md) - For any AI tool

---

## What is the 3-Layer Tone System?

The LUKHAS 3-Layer Tone System is a **sequential narrative flow** that guides readers from emotional engagement (Poetic) through intellectual understanding (Academic) to practical application (User-Friendly).

**Not** a menu of tone choices. **Is** a complete narrative journey.

```
Layer 1: Poetic Hook (2-4 paragraphs)
    ↓
Layer 2: Academic Depth (6+ paragraphs)
    ↓
Layer 3: User-Friendly Bridge (multiple examples)
```

---

## When to Use

### ✅ Required For:
- Public-facing documentation
- Website content (especially concept introductions)
- Marketing materials
- Educational content
- Blog posts
- Community communications

### ❌ Excluded From:
- Internal development documentation
- API references
- Technical specifications
- Code comments
- Official compliance documents

---

## Quick Reference

**Layer 1 (Poetic)**: Eye-catching, metaphorical, beautiful - Creates wonder and curiosity

**Layer 2 (Academic)**: Rigorous, technical, precise - Provides complete understanding

**Layer 3 (User-Friendly)**: Accessible, practical, actionable - Enables immediate application

**High Verbosity**: Preferred - Better deep on fewer concepts than rushed on many

---

## File Organization

```
tone/
├── README.md                    # This file - Quick overview
├── QUICK_START_GUIDE.md         # 🚀 START HERE for new agents
├── claude.me                    # Complete technical documentation
├── lukhas_context.md            # Vendor-neutral equivalent
├── module.manifest.json         # Module metadata
├── config/                      # Tone system configuration
├── docs/                        # Extended documentation
├── schema/                      # Tone validation schemas
└── tests/                       # Tone system tests
```

---

## Key Principles

1. **Sequential Flow**: All 3 layers work together in order (not alternatives)
2. **Context-Aware**: Public content gets 3-layer, internal docs get precision
3. **High Verbosity**: Each layer needs adequate space to accomplish its purpose
4. **Quality Over Quantity**: Better to do one concept well than many rushed

---

## Examples

See [claude.me](./claude.me) for complete examples:
- Memory Folds (all 3 layers with transitions)
- Constellation Framework (complete narrative journey)
- Proper layer transitions and bridging sentences

---

## For New Contributors

**Step 1**: Read [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md) (5 minutes)
**Step 2**: Review examples in [claude.me](./claude.me) (10 minutes)
**Step 3**: Check decision tree: Is this public-facing? Introducing a concept?
**Step 4**: If yes to both → Use full 3-layer system with high verbosity

---

## Common Questions

**Q: Can I use just Layer 2 and Layer 3?**
A: No. For public content, all 3 layers required. For internal docs, use pure Layer 2.

**Q: How long should each layer be?**
A: Layer 1: 2-4 paragraphs, Layer 2: 6+ paragraphs, Layer 3: Multiple examples. High verbosity preferred.

**Q: What if I'm writing API documentation?**
A: API docs are internal/dev documentation → **Exclude** the 3-layer system, use pure technical precision.

**Q: Can I compress the layers to save space?**
A: No. Each layer needs room to breathe. Better to use 3-layer properly on fewer concepts.

---

**Module Status**: Integration Lane (L2)
**Team**: Core
**Philosophy**: Sequential narrative flow for public content, precision for internal docs
**Last Updated**: 2025-10-02
