# Branch Protection Configuration

## Required Status Checks for `main` branch

### Critical (Must Pass)
- ✅ `vocabulary-lint` - Vocabulary compliance
- ✅ `front-matter-lint` - Front-matter validation
- ✅ `evidence-validation` - Claims and evidence validation

### Advisory (Can Warn)
- ⚠️ `seo-validation` - SEO technical hygiene
- ⚠️ `markdown-links` - Broken link detection
- ⚠️ `visual-regression` - Visual regression testing

## Configuration Steps

1. Go to GitHub repo → Settings → Branches
2. Edit branch protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Select required checks:
   - `vocabulary-lint`
   - `front-matter-lint`
   - `evidence-validation`
5. Enable "Require branches to be up to date before merging"
6. Save changes

## Manual Override

Repository admins can bypass checks in emergencies using:
- "Override required status checks" permission
- Document override reason in PR comments
