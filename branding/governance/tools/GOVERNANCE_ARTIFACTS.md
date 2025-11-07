## Summary of Content Governance Artifacts

To help your team manage content quality, accessibility, claims verification, and assistive features, I've prepared a set of governance artifacts. These include CI workflows, scripts, templates, policies, and plans to ensure your branding websites maintain high standards.

The artifacts are:


1. Accessibility (a11y) GitHub Action (pa11y + axe)
2. `claims_registry` generator (script)
3. PR template for content + checklist (auto-inserts)
4. CODEOWNERS suggestion (example)
5. Release / claims gating policy (process + sample workflow)
6. Assistive Mode user-testing plan (recruit + tasks + metrics)
7. Telemetry/analytics event list + privacy note (what to track)
8. Domain health & KPI dashboard spec (metrics + formulas)
9. Content migration checklist (to move docs → branding safely)

I’ll include small scripts / YAML for items 1–4 and clear instructions for 5–9. If you’d like me to commit these directly like the previous scripts, I’ll prepare a push script afterward — but for now I’m giving the artifacts so you can review and apply.

---

## 1) Accessibility (a11y) GH Action — `.github/workflows/a11y.yml`

This runs on PRs and weekly. It builds the site, serves it locally, then runs `pa11y-ci` and an `axe` check (via `axe-core` + `puppeteer`). It assumes `npm run build` builds to `./public` and `npm run serve` serves it in preview mode; adapt if your build pipeline differs.

```yaml
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
```

**How to adjust**

* If your static output is not `./public`, change the `http-server` path.
* You can limit the `pa11y-ci` URL list to changed pages in PR (advanced: parse PR diff and pass URL lists).

**Why this matters**

* Particle-heavy pages often hide accessibility gaps (contrast/keyboard). This job enforces a baseline.

---

## 2) `claims_registry` generator — `tools/generate_claims_registry.py`

Scans Markdown for evidence_links and claim patterns, creates `release_artifacts/claims_registry.yaml`. This is useful for auditors and for the evidence CI.

```python
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
```

**Usage**

```bash
python3 tools/generate_claims_registry.py
git add release_artifacts/claims_registry.yaml && git commit -m "chore: update claims registry"
```

**T4 note:** Run this in release PRs too. It gives legal a single source of truth.

---

## 3) PR template — `.github/PULL_REQUEST_TEMPLATE/content_pr.md`

This is the standard PR template for content authors, ensuring all gates are visible.

```markdown
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
```

**Why this matters**

* Keeps authors honest and reviewers efficient.

---

## 4) `CODEOWNERS` example — `.github/CODEOWNERS`

A starting point for enforced owners by directory.

```
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
```

**Action**

* Update to reflect your team handles.

---

## 5) Release / claims gating policy + sample workflow

### Policy (one paragraph)

**Any** public numeric or operational claim (latency numbers, compliance %) must have:

1. Evidence artifact in `release_artifacts/` (perf logs, signed PDF audit).
2. `evidence_links` listed in page front-matter.
3. `claims_approval: true` only after `web-architect` + `legal` sign-off in PR review.
4. Entry in `release_artifacts/claims_registry.yaml`.

**Sample enforcement workflow**

* Author opens PR with new claim → `content-lint` CI fails if no evidence.
* Author adds evidence artifact (signed) and sets `claims_approval:false`.
* `web-architect` reviews and, if happy, sets `claims_approval:true` and `claims_verified_by`.
* `legal` approves and adds `.release_signoff` file in `release_artifacts/` referencing artifact hash.
* Merge only when both approvals present.

**Automated helper (optional)**

* A GitHub Action `claims-approval` that fails merges unless `claims_approval` and a matching `release_artifacts/.approval-<artifact>.json` exist.

---

## 6) Assistive Mode user-testing plan (brief, actionable)

**Goal:** Validate Assistive Mode for clarity, comprehension, and navigation for neurodiverse users.

**Participants**

* 6–12 participants with cognitive or attention differences (mix of mild dyslexia, ADHD, and older users).
* 3–5 control participants (typical users).

**Tasks (30–45 min per session)**

1. On the Assistive homepage, find “How MΛTRIZ reasons.” (Measure time & success)
2. Run a Safe Demo and explain the steps in your own words.
3. Use Reasoning Lab: navigate to a node and read the node details.
4. For developers: complete Quickstart (5-min) or report where they got stuck.

**Metrics**

* Success rate (% of participants completing task)
* Time on task
* Comprehension score (a 3-question quiz about what each step meant)
* Satisfaction (Likert scale 1–7)
* Accessibility issues observed (notes)

**Protocol**

* Scripted intro, consent, scenario & tasks, debrief.
* Use screen recording + think aloud.
* Pay participants fairly; offer honorarium.

**Deliverable**

* 1-page report with key issues and prioritized fixes. Repeat after 2–3 sprints.

---

## 7) Telemetry events + GDPR note

**Suggested telemetry (de-identified where possible)**

* `ui.theme_changed` {from, to, user_id?} — track assistive adoption (if logged-in)
* `assistive_variant_viewed` {page, user_anonymous}
* `reasoning_trace_viewed` {trace_id, mode(public/dev/enterprise)}
* `evidence_artifact_downloaded` {artifact_id, page}
* `assistive_audio_played` {page, duration}
* `content_readability_flag` {page, FK_grade}

**Privacy**

* Respect GDPR: keep events aggregated for anonymous users; for logged-in users, keep only non-sensitive flags unless consented.
* Don’t store any PII in events. For enterprise audit traces, ensure logs are protected and access controlled.

---

## 8) Domain Health & KPI dashboard spec

**Metrics to compute (per domain & total)**

* **Traffic**: uniques, sessions
* **Conversion**: CTA conversions (demo runs, quickstart completions, trial signups)
* **Quickstart success rate**: completions / starts
* **Reasoning Lab engagement**: traces run / traces viewed / trace exports
* **Assistive adoption**: assistive_mode_enabled % of active users
* **Content quality**: % of pages with assistive variant, % with evidence_links
* **Claims health**: claims_registry count, claims_approval true %
* **SEO**: organic CTR & ranking for top keywords

**Implementation**

* Track events (Segment/GA4), ingest into Looker/Metabase. Create a weekly summary email to stakeholders.

---

## 9) Content migration checklist (docs → branding)

A short, safe process to move production pages to `branding/websites`.

1. **Inventory**: export list of pages in `docs/web/content/domains/*`.
2. **Pick**: move only production-ready pages (homepages, product briefs, short architecture summaries).
3. **Transform**: add front-matter, tone tokens, evidence_links, and an assistive variant.
4. **Link**: add `Read deeper in docs` pointing to `docs/web/...` for technical appendices.
5. **CI**: run `front_matter_lint`, `evidence_check`, `assistive_validate`.
6. **PR**: small PRs per domain (1–3 pages) for easier review.
7. **Retire**: mark old docs pages as deprecated with redirect pages pointing to branding canonical pages.
8. **Monitor**: after merge, run broken-link check and run content-lint weekly for 3 months.

---

## Final T4 Notes — what to watch for

* **Legal + Marketing friction**: marketing wants bold claims, legal wants proof. Build small friction into publishing — that’s healthy. The CI gating above is your friend.
* **Assistive authenticity**: assistive variants must be human-reviewed. Automation only drafts; human approval reduces risk and respects neurodiverse users.
* **Telemetry & consent**: don’t overinstrument. Track only necessary metadata; log traces are sensitive.
* **Measurement discipline**: set baselines then iterate — rolling out Assistive Mode without a plan to measure adoption and effect is a missed opportunity.

---
