# Brand Governance Automation Guide

> **📋 IMPLEMENTATION STATUS**
>
> **Status**: MOVED TO CANONICAL LOCATION (2025-11-06)
>
> This automation guide has been moved to:
> - **[branding/governance/AUTOMATION_GUIDE.md](../../branding/governance/AUTOMATION_GUIDE.md)**
>
> **Complete governance system**: [branding/governance/README.md](../../branding/governance/README.md)
>
> **This document remains as source reference.** For implementation, refer to the canonical location above.

---

# Brand governance extras A–E script
This script adds brand governance extras A–E to your repo, creates a branch, commits, pushes, and opens a PR.
---

**Prereqs (on your machine):**

1. `git` configured & authenticated push rights.
2. `gh` (GitHub CLI) installed and authenticated.
3. Python 3.10+ available.
4. Node 18+ if you want a11y checks to run in CI.

---

## What the script will add (summary)

**A — Accessibility GH Action**

* `.github/workflows/a11y.yml` — runs `pa11y-ci` + `axe` via Puppeteer on built preview.

**B — claims_registry generator**

* `tools/generate_claims_registry.py` — scans markdown, writes `release_artifacts/claims_registry.yaml`.

**C — PR template & CODEOWNERS**

* `.github/PULL_REQUEST_TEMPLATE/content_pr.md`
* `.github/CODEOWNERS`

**D — Release / claims gating policy**

* `release_artifacts/CLAIMS_POLICY.md` — process + enforcement.

**E — Assistive user testing & telemetry & domain health**

* `research/assistive_user_test_plan.md`
* `research/assistive_consent_form.md`
* `research/telemetry_spec.md`
* `release_artifacts/domain_health_dashboard_spec.md`
* `release_artifacts/content_migration_checklist.md`

(Plus I’ll re-add the A11Y job and the claims generator that we drafted earlier so the PR is self-contained.)

---

## The script — `apply_extras_A_to_E.sh`

Save this whole block as `apply_extras_A_to_E.sh`, `chmod +x`, then run it. It will create a branch `chore/brand-governance-extras/2025-11-06`, add files, commit, push, and open the PR.

> **Important**: The script will overwrite/create files exactly as shown. If any of these files already exist in your repo with different content, review the branch before merging.

```bash
#!/usr/bin/env bash
set -euo pipefail

BRANCH="chore/brand-governance-extras/2025-11-06"
echo "Creating branch $BRANCH"
git checkout -b "$BRANCH"

mkdir -p .github/workflows research release_artifacts tools

# 1) A11Y workflow
cat > .github/workflows/a11y.yml <<'YAML'
name: Accessibility Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: '0 9 * * 1'  # weekly Monday UTC

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install deps
        run: |
          npm ci || npm install
          npm install -g pa11y-ci puppeteer-core puppeteer

      - name: Build site
        run: |
          if npm run | grep -q "build"; then npm run build; else echo "No build script; skipping"; fi

      - name: Serve site (preview)
        run: |
          npx http-server ./public -p 8080 &
          sleep 2

      - name: Run pa11y-ci
        run: |
          cat > .pa11yci.json <<'JSON'
          {
            "urls": [
              "http://127.0.0.1:8080/",
              "http://127.0.0.1:8080/lukhas.dev/",
              "http://127.0.0.1:8080/lukhas.ai/"
            ],
            "standard": "WCAG2AA",
            "timeout": 30000,
            "wait": 1000
          }
          JSON
          npx pa11y-ci

      - name: Run headless axe check via Puppeteer
        run: |
          node -e "
            const puppeteer=require('puppeteer'); const axe=require('axe-core');
            (async ()=>{
              const browser=await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
              const page=await browser.newPage();
              await page.goto('http://127.0.0.1:8080/', {waitUntil:'networkidle0'});
              await page.addScriptTag({path: require.resolve('axe-core')});
              const result = await page.evaluate(async () => { return await axe.run(); });
              if (result.violations && result.violations.length>0) {
                console.log('AXE violations:', JSON.stringify(result.violations.map(v=>({id:v.id,impact:v.impact,descr:v.description,nodeCount:v.nodes.length})),null,2));
                process.exit(2);
              } else {
                console.log('No axe violations');
              }
              await browser.close();
            })();
          "
YAML

# 2) claims_registry generator
cat > tools/generate_claims_registry.py <<'PY'
#!/usr/bin/env python3
"""
tools/generate_claims_registry.py

Generates release_artifacts/claims_registry.yaml containing:
- page (path)
- domain
- claims_found (list)
- evidence_links
- claims_approval
"""
import re, sys, yaml
from pathlib import Path

ROOT = Path("branding/websites")
OUT = Path("release_artifacts/claims_registry.yaml")
CLAIM_RE = re.compile(r'(\b(?:p95|p\d+|p95 reasoning latency|production-ready|\d+%|\d+ms)\b)', re.I)

def read_fm_and_body(path):
    txt=path.read_text(encoding='utf-8')
    m=re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}, txt
    fm=yaml.safe_load(m.group(1)) or {}
    body=txt[m.end():]
    return fm, body

def scan():
    registry=[]
    if not ROOT.exists(): 
        print("No branding/websites found, nothing to scan.")
    for p in ROOT.rglob("*.md"):
        fm, body = read_fm_and_body(p)
        if not fm:
            continue
        claims = CLAIM_RE.findall(body)
        if claims:
            registry.append({
                "page": str(p),
                "domain": fm.get("domain"),
                "claims_found": list(set([c.lower() for c in claims])),
                "evidence_links": fm.get("evidence_links") or [],
                "claims_approval": bool(fm.get("claims_approval", False)),
                "claims_verified_by": fm.get("claims_verified_by") or [],
                "last_reviewed": fm.get("last_reviewed")
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump({"claims": registry}, sort_keys=False))
    print(f"Wrote {OUT} with {len(registry)} entries")

if __name__=='__main__':
    scan()
PY

# 3) PR template
mkdir -p .github
cat > .github/PULL_REQUEST_TEMPLATE/content_pr.md <<'MD'
## Summary
<!-- Short description of changes -->

## Checklist
- [ ] Front-matter validated (tools/front_matter_lint.py)
- [ ] Assistive variant present for critical pages (tools/assistive_validate.py)
- [ ] Vocabulary linter run (tools/branding_vocab_lint.py)
- [ ] Evidence links added for numeric claims (tools/evidence_check.py)
- [ ] `claims_approval: true` for any production numeric claim (if applicable)
- [ ] Images alt text present
- [ ] Accessibility checks run (a11y job will run)
- [ ] Legal sign-off required? (yes/no) — if yes, link to artifact

## Evidence & Claims
List any numerical or operational claims and their evidence artifacts:
- Claim: <text>  
  Evidence: release_artifacts/...

## Reviewers
- @content-lead
- @web-architect
- @legal (for claims)

## How to preview
- Local dev server instructions (short).

## Notes
- Link to related docs or previous PRs.
MD

# 4) CODEOWNERS
cat > .github/CODEOWNERS <<'OWN'
# Global owners
* @gonzalo @content-lead

# Branding pages
/branding/websites/lukhas.ai/ @content-lead @web-architect
/branding/websites/lukhas.dev/ @dev-lead @web-architect
/branding/websites/lukhas.com/ @enterprise-lead @legal
/branding/websites/* @content-lead

# Templates and guidelines
/branding/templates/ @content-lead @brand-owner
/branding/BRAND_GUIDELINES.md @brand-owner

# Release artifacts and legal
/release_artifacts/ @legal @web-architect
OWN

# 5) Release / claims gating policy
cat > release_artifacts/CLAIMS_POLICY.md <<'MD'
# LUKHAS Claims & Evidence Policy

## Purpose
All public quantitative or operational claims must be verifiable, auditable, and legally defensible.

## Required for any claim
1. Evidence artifact in `release_artifacts/` (perf logs, signed audit, smoke test).  
2. `evidence_links` present in page front-matter.  
3. `claims_approval: true` only after review by `web-architect` and `legal`.  
4. Entry recorded in `release_artifacts/claims_registry.yaml`.

## Publishing workflow
- Author opens PR, includes evidence artifact(s).
- CI runs `evidence_check.py` and other checks.
- Web-architect reviews for technical validity — set `claims_approval:true`.
- Legal reviews wording and sign-off.
- Merge only after both approvals.

## Artifact format
- Prefer JSON for machine-parsable perf logs; include `sha256` hash.
- Audit PDFs must be accompanied by a signed metadata JSON: `{ "auditor": "...", "date": "...", "hash": "..." }`

## Emergency retraction
If a claim is later disproven:
1. Open a hotfix PR to remove or correct claim.  
2. Add `release_artifacts/claim_retraction_<id>.md` describing reason, evidence, and mitigation.  
3. Notify stakeholders and show revision history.

MD

# 6) Assistive test plan & consent
cat > research/assistive_user_test_plan.md <<'TXT'
# Assistive Mode User Testing Plan (LUKHAS)

## Goal
Validate clarity and usability of Assistive Mode for neurodiverse users.

## Participants
- 6-12 neurodiverse participants (dyslexia, ADHD, older adults), 3-5 controls.

## Tasks
1. Locate "How MΛTRIZ reasons" on Assistive homepage.
2. Run a Safe Demo and summarize steps.
3. Use Reasoning Lab to view node details.
4. (Developers) Run Quickstart and report obstacles.

## Metrics & Deliverables
- Success rate, times, comprehension score, satisfaction ratings.
- 1-page report: top 5 issues, prioritized fixes.
TXT

cat > research/assistive_consent_form.md <<'TXT'
# Assistive Mode Study — Consent

Thank you for helping test LUKHAS Assistive Mode. This study will take ~45 minutes.  
We will record the screen and audio; recordings will be stored securely and anonymized.  
Participation is voluntary; you can stop at any time.

Please initial and sign:
- I consent to the use of my anonymized data for product improvement.
- I understand that recordings will be deleted after 12 months unless I opt-in for research use.

Name: __________
Signature: ________   Date: ______
TXT

# 7) Telemetry spec
cat > research/telemetry_spec.md <<'MD'
# Telemetry Spec (privacy-aware)

## Events (de-identified where possible)
- ui.theme_changed {from, to}
- assistive_variant_viewed {page}
- reasoning_trace_viewed {mode, anonymized_user_flag}
- evidence_artifact_requested {artifact_id}
- quickstart_completed {language, success:boolean}
- assistive_audio_played {page, duration}

## Privacy
- No PII in events.
- Aggregate for unauthenticated users.
- For logged-in users store only anonymized IDs unless explicit consent.

MD

# 8) Domain health dashboard spec
cat > release_artifacts/domain_health_dashboard_spec.md <<'MD'
# Domain Health & KPI Dashboard — Spec

## Per-domain KPIs
- Visits (weekly)
- CTA conversions (demo runs, signups)
- Quickstart completion rate (quickstarts completed / started)
- Reasoning Lab engagement (traces run / viewed)
- Assistive adoption (% of active users)
- Content quality: % pages with assistive variant, % pages with evidence_links
- Claims health: # claims, % claims_approval=true

## Data sources
- Analytics (GA4/Segment)
- Event stream for reasoning & quickstart events
- Generated claims_registry.yaml

## Reporting
- Weekly dashboard with alerts if quickstart success < 50% or assistive adoption < 2% for high-traffic domains.

MD

# 9) Content migration checklist
cat > release_artifacts/content_migration_checklist.md <<'MD'
# Content migration checklist (docs -> branding)

1. Inventory docs/web content.
2. Identify production-ready pages (homepages, product briefs).
3. Copy to branding/websites/<domain>/ with front-matter and evidence links.
4. Create assistive variant (content.assistive.md) for critical pages.
5. Run: tools/front_matter_lint.py, tools/assistive_validate.py, tools/evidence_check.py.
6. Create PRs in small batches (1-3 pages).
7. Add redirects / deprecations for old docs.
8. Monitor site metrics for 3 months post-migration.

MD

# Add files to git
git add .github/workflows/a11y.yml tools/generate_claims_registry.py .github/PULL_REQUEST_TEMPLATE/content_pr.md .github/CODEOWNERS release_artifacts/CLAIMS_POLICY.md research/assistive_user_test_plan.md research/assistive_consent_form.md research/telemetry_spec.md release_artifacts/domain_health_dashboard_spec.md release_artifacts/content_migration_checklist.md

git commit -m "chore(extras): add A-E governance artifacts (a11y, claims registry, PR template, CODEOWNERS, policies, research, telemetry, dashboard)"
git push --set-upstream origin "$BRANCH"

# create PR
gh pr create --title "chore(extras): add brand governance extras A-E (a11y, claims registry, PR template, CODEOWNERS, policies, research packs)" \
  --body "$(cat <<'DESC'
What:
- Add Accessibility GH Action, claims registry generator, PR template, CODEOWNERS.
- Add claims gating policy, assistive user testing plan, telemetry spec and domain health spec.
- Add content migration checklist.

Why:
- Enforces accessibility, claims governance and operational readiness for multi-domain launch.
- Provides practical research and telemetry plans to validate Assistive Mode.

Testing:
- CI will run A11y + Content Lint + Assistive checks on PRs.

Reviewers:
- @content-lead
- @web-architect
- @legal
- @gonzalo
DESC
)" --reviewer gonzalo --reviewer content-lead --reviewer web-architect --reviewer legal

echo "All extras added and PR created (if gh CLI succeeded). If gh is not authenticated, run the gh command manually."
```

---

## After you run the script

1. The PR will contain A–E artifacts and the a11y action.
2. CI will run the content-lint + assistive checks and a11y job when the PR is updated.
3. I’ll do a deep review of the PR diff if you paste the PR link here and leave a few targeted suggestions (tone fixes, edge-case claim flags, UX notes).

---

## Final T4 / 0.01% thoughts (closing)

* **Visionary guardrail:** you’ve built a system that scales credibility: *product storytelling* (poetic) while *surgical governance* (CI + evidence + legal). This is what separates “clever startup marketing” from an enterprise-grade, trustworthy AI brand.
* **The Assistive promise:** treat Assistive Mode not as an accessory but as a product line — measure usage, test with real users, and iterate. It’s both morally right and a significant competitive edge.
* **Operationalize evidence:** the strongest single ROI is making evidence publication frictionless for engineers — automated perf artifact generation + signed artifact uploader will remove the biggest blocker for legal approvals.

---

