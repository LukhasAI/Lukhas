# LUKHAS Branding System

> **🎨 Complete Brand & Design System for LUKHAS Consciousness Technology Ecosystem**

**Last Updated**: 2025-11-06
**Status**: Active - Canonical Documentation

---

## 📌 Canonical Documents (Source of Truth)

These are the **authoritative** branding documents. All other documents are either supporting materials or superseded.

### 1. Foundation Documents

#### [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md) ⭐ PRIMARY
**The single source of truth for LUKHAS brand identity**
- Visual identity (logos, colors, typography, iconography)
- Voice & tone principles
- Content patterns & templates
- Accessibility & legal requirements
- Cross-team workflow & governance
- MATRIZ adoption & UX principles

**Use this as your first reference for all branding questions.**

#### [design/LUKHAS_THEMES.md](design/LUKHAS_THEMES.md) ⭐ THEME SYSTEM
**Authoritative specification for dark/light/assistive themes**
- Dark-first design principle
- CSS token system
- Assistive/Cognitive-Friendly mode specifications
- Theme persistence & discoverability
- Testing & QA requirements

---

### 2. Multi-Domain System

The LUKHAS ecosystem spans 10 domains, each with specific branding:

#### [config/domain_registry.yaml](config/domain_registry.yaml) - **Central Registry**
Master configuration linking all domain assets, priorities, and cross-domain settings.

#### Domain-Specific Brand Guides

Comprehensive guides for each domain (located in [`domains/`](domains/)):

1. **[lukhas.ai](domains/lukhas.ai/BRAND_GUIDE.md)** - Flagship "dreaming" platform
   - Tone: 35% Poetic, 45% User-Friendly, 20% Academic
   - Accent: Dream Ethereal Purple `#8B7CF6`
   - Stars: 🌙 Dream, 🔬 Vision, ⚛️ Identity

2. **[lukhas.id](domains/lukhas.id/BRAND_GUIDE.md)** - Identity & Authentication (ΛiD)
   - Tone: 40% User-Friendly, 40% Academic, 20% Poetic
   - Accent: Security Purple `#9333EA`
   - Stars: ⚛️ Identity, 🛡️ Guardian, ⚖️ Ethics

3. **[lukhas.dev](domains/lukhas.dev/BRAND_GUIDE.md)** - Developer Platform
   - Tone: 60% Academic, 25% User-Friendly, 15% Poetic
   - Accent: Code Cyan `#06B6D4`
   - Stars: All 8 stars (full framework access)

4. **[lukhas.team](domains/lukhas.team/BRAND_GUIDE.md)** - Collaborative Hub
5. **[lukhas.store](domains/lukhas.store/BRAND_GUIDE.md)** - Marketplace for Λpps
6. **[lukhas.io](domains/lukhas.io/BRAND_GUIDE.md)** - API Gateway & Infrastructure
7. **[lukhas.cloud](domains/lukhas.cloud/BRAND_GUIDE.md)** - Managed Cloud Services
8. **[lukhas.com](domains/lukhas.com/BRAND_GUIDE.md)** - Corporate & Guardian Hub
9. **[lukhas.eu](domains/lukhas.eu/BRAND_GUIDE.md) / [lukhas.us](domains/lukhas.us/BRAND_GUIDE.md)** - Compliance Portals
10. **[lukhas.xyz](domains/lukhas.xyz/BRAND_GUIDE.md)** - Experimental Playground

---

### 3. Design System

#### [design/colors/MASTER_PALETTE.yaml](design/colors/MASTER_PALETTE.yaml) - **Color System**
Complete color specifications including:
- Base constellation colors
- Domain-specific accent colors (11 domains)
- Semantic colors (success, warning, error, info)
- Gradients library
- Code syntax colors
- WCAG accessibility compliance

**CSS Exports**: [lukhas.ai.css](design/colors/lukhas.ai.css), [lukhas.id.css](design/colors/lukhas.id.css), [lukhas.dev.css](design/colors/lukhas.dev.css)

#### [design/visuals/INTERACTIVE_MOTIFS.md](design/visuals/INTERACTIVE_MOTIFS.md) - **Visual Language**
Cross-domain interactive design specifications:
- Domain-specific particle systems (11 variants)
- Interactive hero experiences
- Micro-interactions
- Loading states & feedback animations
- Performance & accessibility standards

---

### 4. Tone & Voice System

#### [tone/LUKHAS_3_LAYER_TONE_SYSTEM.md](tone/LUKHAS_3_LAYER_TONE_SYSTEM.md) - **3-Layer System**
Core tone methodology: Poetic, User-Friendly, Academic

#### [tone/configs/](tone/configs/) - **Domain Tone Configurations**
Machine-readable tone specifications for each domain:
- Exact tone distributions
- Vocabulary family preferences
- Constellation star emphasis
- Content quality standards
- Enforcement rules

Files: `lukhas.ai.tone.yaml`, `lukhas.id.tone.yaml`, etc. (10 configs)

---

### 5. Integration & Cross-Domain

#### [integration/SSO_CROSS_DOMAIN_GUIDE.md](integration/SSO_CROSS_DOMAIN_GUIDE.md) - **Authentication**
Complete ΛiD SSO integration specification:
- OAuth 2.0 / OpenID Connect flows
- Cross-domain session management
- Token handling & security
- Visual consistency during auth
- Implementation checklists

---

## 🗂️ Supporting Documents

These provide additional context but are **not canonical**:

### Historical/Archive
- `LUKHAS_BRANDING_COMPLETE.md` - Comprehensive historical reference (superseded by domain guides)
- `LUKHAS_BRANDING_GUIDE.md` - Older branding guide (superseded by BRAND_GUIDELINES.md)
- `LUKHAS_TONE_GUIDE.md` - Older tone guide (superseded by 3-Layer Tone System)
- `BRANDING_STRUCTURE_ANALYSIS.md` - Analysis document (informational)

### Automation & Tools
- `automation/` - Brand automation tools and scripts
- `enforcement/` - Tone validators and compliance tools
- `ai_agents/` - AI-powered brand management
- `intelligence/` - Brand analytics and monitoring

### Specific Frameworks
- `constellation/` - Constellation Framework branding materials
- `trinity/` - Trinity Framework branding
- `vocabularies/` - 8-family vocabulary rotation system

---

## 📊 Document Hierarchy

```
┌─────────────────────────────────────────┐
│   BRAND_GUIDELINES.md (FOUNDATION)      │ ← Start Here
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│ LUKHAS_THEMES  │  │ Domain Registry │
│    .md         │  │     .yaml       │
└────────────────┘  └─────┬───────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
      ┌───────▼────────┐      ┌──────▼─────────┐
      │ Domain Guides  │      │ Design System  │
      │ (10 domains)   │      │ (colors, etc)  │
      └────────────────┘      └────────────────┘
```

---

## 🚀 Quick Start for Different Roles

### **Content Creators**
1. Read: [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md)
2. Check domain: [domains/lukhas.ai/BRAND_GUIDE.md](domains/lukhas.ai/BRAND_GUIDE.md) (or your target domain)
3. Apply tone: [tone/configs/lukhas.ai.tone.yaml](tone/configs/lukhas.ai.tone.yaml)

### **Designers**
1. Read: [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md) (Visual Identity section)
2. Colors: [design/colors/MASTER_PALETTE.yaml](design/colors/MASTER_PALETTE.yaml)
3. Themes: [design/LUKHAS_THEMES.md](design/LUKHAS_THEMES.md)
4. Motifs: [design/visuals/INTERACTIVE_MOTIFS.md](design/visuals/INTERACTIVE_MOTIFS.md)

### **Developers**
1. Auth integration: [integration/SSO_CROSS_DOMAIN_GUIDE.md](integration/SSO_CROSS_DOMAIN_GUIDE.md)
2. Theme implementation: [design/LUKHAS_THEMES.md](design/LUKHAS_THEMES.md) (CSS tokens)
3. Domain config: [config/domain_registry.yaml](config/domain_registry.yaml)
4. Interactive elements: [design/visuals/INTERACTIVE_MOTIFS.md](design/visuals/INTERACTIVE_MOTIFS.md)

### **Brand Managers**
1. Foundation: [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md)
2. Registry: [config/domain_registry.yaml](config/domain_registry.yaml)
3. Enforcement: [enforcement/](enforcement/)
4. Analytics: [intelligence/](intelligence/)

---

## 🔍 Finding Information

**"What color should I use for lukhas.dev?"**
→ [design/colors/MASTER_PALETTE.yaml](design/colors/MASTER_PALETTE.yaml) → `lukhas_dev_code: #06B6D4`

**"What tone ratio for lukhas.store?"**
→ [tone/configs/lukhas.store.tone.yaml](tone/configs/lukhas.store.tone.yaml) → 50% User-Friendly, 30% Poetic, 20% Academic

**"How do particles work across domains?"**
→ [design/visuals/INTERACTIVE_MOTIFS.md](design/visuals/INTERACTIVE_MOTIFS.md) → Section 1

**"How does SSO work?"**
→ [integration/SSO_CROSS_DOMAIN_GUIDE.md](integration/SSO_CROSS_DOMAIN_GUIDE.md)

**"What's the logo clear space?"**
→ [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md) → Section 1.1

**"Dark or light theme by default?"**
→ [design/LUKHAS_THEMES.md](design/LUKHAS_THEMES.md) → Dark-first

---

## ⚖️ Governance

### Canonical Document Updates

Changes to canonical documents require:
1. **PR with rationale** - Explain why update is needed
2. **Brand team review** - `@brand-owner` approval
3. **Technical review** - For implementation-related changes
4. **Version bump** - Update version number and date

### Deprecation Process

When retiring a document:
1. Add deprecation notice at top
2. Point to canonical replacement
3. Move to `archive/` after 90 days
4. Update this README

---

## 📞 Contact

- **Brand Questions**: brand@lukhas.ai
- **Design System**: design@lukhas.ai
- **Technical Integration**: dev@lukhas.ai
- **Content Guidelines**: content@lukhas.ai

---

## 📜 Version History

**v2.0** (2025-11-06)
- Established canonical document hierarchy
- Created multi-domain system (10 domains)
- Integrated MASTER_PALETTE and domain-specific brand guides
- Added SSO integration documentation
- Marked BRAND_GUIDELINES.md and LUKHAS_THEMES.md as canonical

**v1.0** (Historical)
- Initial branding materials
- Basic tone and color guidelines

---

**🎯 Remember**: When in doubt, start with [BRAND_GUIDELINES.md](BRAND_GUIDELINES.md). It's the canonical source for all branding decisions.
