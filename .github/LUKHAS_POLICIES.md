# LUKHAS Context & Policies

## Repository
- **Repo**: https://github.com/LukhasAI/Lukhas
- **Main Branch**: `main`
- **Working Directory**: `/Users/agi_dev/LOCAL-REPOS/Lukhas`

## Critical Policies

### Commit Standards (T4 Minimal)
- **Format**: `<type>(<scope>): <imperative subject ≤72>`
- **Types**: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security
- **Scopes**: core|matriz|identity|memory|governance|branding|tools|docs|ci
- **Body**: Problem/Solution/Impact bullets for non-trivial changes
- **Trailers**: Include `Closes:`, `Security-Impact:`, `LLM:` when relevant
- **Examples**:
  - ✅ `feat(branding): add evidence page template system with bidirectional linking`
  - ✅ `docs(governance): add SEO technical hygiene implementation guide`
  - ❌ `🎯 BREAKTHROUGH: Evidence System Complete!!!`

### Lane-Based Import Rules
- `lukhas/` ← can import from `core/`, `matriz/`, `universal_language/`
- `candidate/` ← can import from `core/`, `matriz/` ONLY (NO lukhas imports)
- Validate with: `make lane-guard`

### Testing Standards
- **Coverage Target**: 75%+ for production promotion
- **Test Markers**: unit, integration, contract, smoke, tier1
- **Exclusions**: Always exclude `.git`, `__pycache__`, `.pytest_cache`, `node_modules`, `venv`, `.venv`, `dist`, `build`, `*.egg-info`

### Branding Vocabulary Rules
- ✅ "LUKHAS AI" (never "LUKHAS AGI")
- ✅ "quantum-inspired algorithms" (never "quantum processing")
- ✅ "bio-inspired computing" (never "biological processing")
- ✅ "consciousness simulation" (never "true consciousness" or "sentient AI")
- ✅ "deployment-ready" or "validated production" (never "production-ready" without approval)
- Run: `python3 tools/branding_vocab_lint.py` to validate

### Front-Matter Requirements
All branding markdown files must include:
```yaml
---
title: "Page Title"
domain: lukhas.ai
owner: @content-lead
audience: [developers, enterprise, researchers]
tone:
  poetic: 0.25
  user_friendly: 0.50
  academic: 0.25
canonical: https://lukhas.ai/page-path
source: branding
last_reviewed: "2025-11-06"
evidence_links:
  - 'release_artifacts/evidence-artifact.json'
claims_approval: true
claims_verified_by: ['@web-architect', '@legal']
seo:
  description: "150-160 character meta description"
  keywords: ["consciousness AI", "MATRIZ", "symbolic reasoning"]
  og_image: /assets/og-images/domain-page.png
---
```

### Evidence & Claims Policy
- All numeric/operational claims MUST have `evidence_links` in front-matter
- Claims require `claims_approval: true` after review by @web-architect and @legal
- Evidence artifacts stored in `release_artifacts/` with JSON metadata
- Generate claims registry: `python3 tools/generate_claims_registry.py`
- Validate claims: `python3 tools/validate_claims.py`

### GitHub Workflow
- Create feature branch from `main`
- Push changes and open PR
- PR title format: `<type>(<scope>): <description>`
- Request reviewers: @web-architect, @content-lead, @legal (for claims)
- All CI checks must pass before merge
