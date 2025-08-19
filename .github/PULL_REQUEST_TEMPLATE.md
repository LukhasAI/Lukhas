## Summary
- [ ] Describes purpose, risk, rollback plan

## Scope & Interfaces
- [ ] Touches Core Surface API (context bus / adapters / identity / consent)
  - If yes: increments bus_schema_version and updates tests
- [ ] Lists old -> new imports added to docs/MIGRATION_GUIDE.md
- [ ] Adds/updates compatibility shims (if moving modules) with removal date

## Safety & Policy
- [ ] All privileged steps evaluated by policy hot-path
- [ ] Emits Λ-trace + UNL explanation for actions
- [ ] No vendor API calls outside adapters
- [ ] PII linter clean

## Brand Policy (for UI/content changes)
- [ ] **No public "MATADA"** references in user-facing content
- [ ] **"Matriz"** used in body text, SEO, alt text, metadata  
- [ ] **"MΛTRIZ"** only in logos, hero sections, wordmarks
- [ ] **All Λ usage** includes `aria-label="Matriz"`
- [ ] **No banned words**: guaranteed, perfect, revolutionary, flawless, unlimited
- [ ] **Poetic sections ≤40 words** (if applicable)
- [ ] **Brand policy lints pass**: `npm run lint:policy` in lukhas_website/

## Tests & Perf
- [ ] Unit tests added/updated
- [ ] Canary pack for this domain passes
- [ ] Perf: auth p95 < 100ms (if affected), context p95 < 250ms

## Feature Flags
- [ ] UL_ENABLED / VIVOX_LITE / QIM_SANDBOX unchanged or toggled intentionally

## Ownership
- [ ] CODEOWNERS approval for affected lanes