# MATRIZ Rebrand Runbook

## Phase 1: Redirects & URL Management
1. **Redirects**: `/matada*` → `/matriz` (301 permanent)
2. **Canonical URLs**: Ensure `/matriz` is primary
3. **Sitemap Updates**: Replace all MATADA references
4. **Internal Links**: Update cross-references

## Phase 2: Content Migration
1. **Replace public "MATADA" → "Matriz"**
   - User-facing content only
   - Keep `matada` in schema/file IDs
   - Preserve internal documentation references
2. **Λ Usage Audit**
   - Remove from body copy, URLs, metadata
   - Maintain in logos, hero sections, wordmarks
   - Add `aria-label` for accessibility

## Phase 3: Technical Implementation
1. **JSON-LD Product Schema** for `/matriz` page
   ```json
   {
     "@type": "SoftwareApplication",
     "name": "Matriz",
     "applicationCategory": "AI Governance"
   }
   ```
2. **Meta Tags**: OG/Twitter cards with MATRIZ branding
3. **SVG Wordmarks**: Accessible fallbacks for all Λ usage

## Phase 4: Components & UX
1. **Transparency Box**: Disclaimers and limitations
   - What MATRIZ does/doesn't do
   - Dependencies and requirements
   - Data handling policies
2. **Tone Switch**: Three-layer content system
   - Poetic ≤40 words
   - Technical with sources
   - Plain language explanations

## Phase 5: Enforcement & Monitoring
1. **CI Lints**: Brand/tone/accessibility enforcement
   - `npm run lint:brand`
   - `npm run lint:tone`
   - `npm run lint:a11y`
2. **Weekly Scans**: Automated site monitoring
3. **SEO Monitoring**: Track `/matriz` indexing and performance

## Brand Council Process
- **Weekly 15min reviews** (PM/Design/Eng/Legal)
- **New Λ usage approval** required
- **Violation escalation** procedures
- **Documentation updates** as needed

## Success Criteria
- [ ] Zero public MATADA occurrences
- [ ] All Λ usage in approved contexts with aria-labels
- [ ] `/matriz` fully optimized and indexed
- [ ] Three-layer tone system implemented
- [ ] CI passes 100% brand/tone/a11y checks
- [ ] Performance metrics within targets

## Rollback Plan
If issues arise:
1. Revert redirects to preserve user access
2. Restore previous meta tags and schema
3. Document lessons learned
4. Plan incremental re-approach

## Emergency Contacts
- **Brand Council**: [internal contact info]
- **DevOps**: [deployment contact]
- **SEO**: [search optimization contact]