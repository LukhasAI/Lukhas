---
status: wip
type: documentation
---
# MATADA Website Internationalization Plan

## Overview
Implement multi-language support for MATADA website with 7 target languages, maintaining the humble and academic tone across all translations.

## Target Languages
1. **Spanish (ES)** - 500M+ speakers globally
2. **French (FR)** - 280M+ speakers globally
3. **German (DE)** - 100M+ speakers globally
4. **Chinese Simplified (ZH)** - 1.1B+ speakers
5. **Japanese (JA)** - 125M+ speakers
6. **Italian (IT)** - 65M+ speakers
7. **Portuguese (PT)** - 260M+ speakers

## Technical Implementation Strategy

### 1. Framework: Next.js i18n + react-i18next
```bash
npm install next-i18next react-i18next i18next
```

### 2. Directory Structure
```
/locales
  /en
    - common.json
    - navigation.json
    - pages.json
    - discoveries.json
    - trinity.json
  /es
    - common.json
    - navigation.json
    - pages.json
    - discoveries.json
    - trinity.json
  /fr (same structure)
  /de (same structure)
  /zh (same structure)
  /ja (same structure)
  /it (same structure)
  /pt (same structure)
```

### 3. URL Structure
- `/` (English default)
- `/es/` (Spanish)
- `/fr/` (French)
- `/de/` (German)
- `/zh/` (Chinese)
- `/ja/` (Japanese)
- `/it/` (Italian)
- `/pt/` (Portuguese)

## Translation Content Priorities

### Phase 1: Core Pages (Week 1)
1. **Navigation** - Menu items, buttons
2. **Hero Section** - MATADA tagline, Trinity introduction
3. **About Page** - Founder story and timeline
4. **Contact/Basic Pages** - Simple content

### Phase 2: Complex Content (Week 2-3)
1. **Discoveries Page** - Technical descriptions with humility
2. **Constellation Framework** - Identity, Consciousness, Guardian
3. **Documentation** - User-friendly sections first

### Phase 3: Advanced Content (Week 4)
1. **Documentation** - Academic and poetic tones
2. **Technical Specifications** - API docs, system architecture
3. **Error Messages** - User experience consistency

## Cultural Considerations

### Spanish (ES)
- **Formal "usted" vs informal "tú"**: Use formal for professional sections
- **Regional variations**: Neutral Latin American Spanish
- **Technical terms**: Maintain English for API terms where standard

### French (FR)
- **Technical terminology**: Balance French equivalents with English tech terms
- **Formal tone**: Maintain scientific/academic register
- **Cultural context**: European French as primary

### German (DE)
- **Compound words**: Leverage German's technical precision
- **Formal address**: Use "Sie" for professional content
- **Technical accuracy**: Germans expect precise technical documentation

### Chinese Simplified (ZH)
- **Technical concepts**: Explain AI/consciousness concepts culturally
- **Honorific language**: Appropriate respect levels
- **Character limits**: Concise translations for UI elements

### Japanese (JA)
- **Keigo system**: Polite forms for all user-facing content
- **Technical terms**: Mix of katakana (AI terms) and kanji (concepts)
- **Cultural sensitivity**: Consciousness/soul concepts require careful handling

### Italian (IT)
- **Regional neutrality**: Standard Italian, not dialects
- **Technical elegance**: Italians appreciate beautiful technical prose
- **Cultural warmth**: Maintain approachable tone

### Portuguese (PT)
- **Brazilian Portuguese**: Larger user base than European
- **Technical adaptation**: Balance formal/informal registers
- **Cultural context**: Tech-forward Brazilian market

## Key Translation Challenges

### 1. Technical Terminology
- **LUKHAS AI** - Keep as brand name
- **Constellation Framework** - "Marco Trinity" (ES), "Cadre Trinité" (FR), etc.
- **Consciousness** - Cultural/philosophical variations
- **Memory Folds** - Technical metaphor translation

### 2. Humble Tone Preservation
- **"Our Discoveries"** vs "Breakthrough Innovations"
- Avoid superlatives in all languages
- Maintain Sam Altman-style humility

### 3. Academic Precision
- Mathematical formulas stay in English
- Code examples with translated comments
- Technical accuracy over fluency

## Implementation Steps

### Step 1: Setup i18n Infrastructure
```typescript
// next-i18next.config.js
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'de', 'zh', 'ja', 'it', 'pt'],
  },
  fallbackLng: 'en',
  debug: false,
  reloadOnPrerender: process.env.NODE_ENV === 'development',
}
```

### Step 2: Create Translation Files
```json
// locales/en/common.json
{
  "navigation": {
    "about": "ABOUT",
    "discoveries": "DISCOVERIES",
    "docs": "DOCS",
    "careers": "CAREERS"
  },
  "hero": {
    "tagline": "MODULAR ADAPTIVE TEMPORAL ATTENTION DYNAMIC ARCHITECTURE",
    "subtitle": "Every thought becomes a traceable, governed, evolvable node",
    "trinity": {
      "identity": "IDENTITY",
      "consciousness": "CONSCIOUSNESS",
      "guardian": "GUARDIAN"
    }
  }
}
```

### Step 3: Component Updates
```typescript
// Example: Hero.tsx with i18n
import { useTranslation } from 'next-i18next'

export default function Hero() {
  const { t } = useTranslation('common')

  return (
    <motion.p className="font-regular text-base md:text-lg tracking-[0.25em] uppercase text-trinity-consciousness mb-8 opacity-90">
      {t('hero.tagline')}
    </motion.p>
  )
}
```

### Step 4: Language Switcher Component
```typescript
// components/LanguageSwitcher.tsx
const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇧🇷' }
]
```

## Quality Assurance

### 1. Native Speaker Review
- Hire professional translators for each language
- Technical review by native speaker developers
- Cultural sensitivity review

### 2. Translation Management
- Use professional translation service (DeepL Pro API for first draft)
- Maintain translation memory for consistency
- Version control for translation updates

### 3. Testing Strategy
- Automated screenshot testing for layout issues
- Manual testing by native speakers
- Performance testing with different character sets

## SEO Considerations

### 1. Hreflang Implementation
```html
<link rel="alternate" hreflang="en" href="https://matada.ai/" />
<link rel="alternate" hreflang="es" href="https://matada.ai/es/" />
<link rel="alternate" hreflang="fr" href="https://matada.ai/fr/" />
<!-- etc. -->
```

### 2. Localized Meta Tags
- Translated page titles and descriptions
- Cultural keyword research per language
- Local search optimization

### 3. Content Strategy
- Localized blog content (future)
- Regional case studies
- Local market positioning

## Budget Estimate

### Translation Costs
- **Professional Translation**: $0.15-0.25 per word
- **Estimated word count**: ~10,000 words across all pages
- **Cost per language**: $1,500-2,500
- **Total for 7 languages**: $10,500-17,500

### Development Time
- **i18n Setup**: 8-12 hours
- **Component Updates**: 16-24 hours
- **Testing & QA**: 12-16 hours
- **Total Development**: 36-52 hours

### Maintenance
- **Monthly translation updates**: 2-4 hours
- **New feature translations**: 25% overhead
- **Annual review**: 8-12 hours

## Success Metrics

### 1. Technical Metrics
- Page load time impact: <5% increase
- Translation coverage: >95% of user-facing text
- Language switcher usage: Track user engagement

### 2. Business Metrics
- International traffic growth: Target 40% increase
- Engagement by language: Time on site, pages per session
- Conversion rates by language: Form submissions, signups

### 3. Quality Metrics
- Translation accuracy: >98% (measured by native speaker review)
- Cultural appropriateness: Qualitative feedback
- Consistency score: Automated terminology checking

## Timeline

### Week 1: Foundation
- Day 1-2: i18n framework setup
- Day 3-4: Core navigation and hero translation
- Day 5-7: Basic page structure translation

### Week 2: Content Translation
- Day 8-10: About and basic pages
- Day 11-12: Discoveries page
- Day 13-14: Constellation Framework content

### Week 3: Documentation
- Day 15-17: User-friendly documentation tone
- Day 18-19: Academic documentation tone
- Day 20-21: API reference and technical content

### Week 4: Polish & Launch
- Day 22-24: Native speaker review and corrections
- Day 25-26: QA testing and bug fixes
- Day 27-28: SEO optimization and launch preparation

## Post-Launch Strategy

### Continuous Improvement
- Monthly analytics review by language
- Quarterly native speaker audits
- Annual strategy review and expansion

### Community Engagement
- Language-specific social media content
- Regional developer community outreach
- Localized documentation examples

### Future Expansion
- Arabic (AR) - 400M+ speakers
- Russian (RU) - 260M+ speakers
- Korean (KO) - 75M+ speakers
- Hindi (HI) - 600M+ speakers

## Risk Mitigation

### Technical Risks
- **Layout breaking**: Extensive testing with long German words
- **Performance impact**: Lazy loading of translation files
- **SEO dilution**: Proper hreflang and canonical setup

### Content Risks
- **Cultural sensitivity**: Professional cultural review
- **Technical accuracy**: Domain expert validation
- **Brand consistency**: Translation style guide

### Business Risks
- **Maintenance overhead**: Automated translation workflows
- **Update delays**: Simultaneous release processes
- **Quality degradation**: Regular quality audits

This comprehensive plan ensures MATADA's international expansion maintains the humble, technical excellence that defines the brand while reaching global consciousness research communities.
