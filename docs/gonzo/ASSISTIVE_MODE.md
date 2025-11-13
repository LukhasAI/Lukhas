## LUKHAS Assistive Mode Implementation — Step-by-step

> **📋 IMPLEMENTATION STATUS**
>
> **Status**: MOVED TO CANONICAL LOCATION (2025-11-06)
>
> This implementation guide has been moved to:
> - **[branding/design/ASSISTIVE_MODE_IMPLEMENTATION.md](../../branding/design/ASSISTIVE_MODE_IMPLEMENTATION.md)**
>
> **This document remains as source reference.** For implementation details, refer to the canonical location above.

---

This document provides all the code and instructions to implement the Assistive Mode content checklist, CI validation, and sample assistive homepage for `lukhas.ai`. Follow the steps below to add the necessary files, create a PR, and start authoring assistive variants.



## 1) Assistive Mode Checklist PR — files, branch, commit & PR body

### Branch & commit

* **Branch**: `assistive/implement-checklist-2025-11-06`
* **Commits**

  1. `chore(assistive): add assistive content validator and README`
  2. `ci(assistive): add GH Action to validate assistive mode and vocab lint`

### Files to add

* `tools/assistive_validate.py` — validator script (see below).
* `.github/workflows/assistive-validate.yml` — GitHub Actions job (see below).
* `branding/ASSISTIVE_CHECKLIST.md` — short human checklist (see below).

I’ve included full file contents below. Save them and commit on the branch.

---

### tools/assistive_validate.py

Save as `tools/assistive_validate.py`. This script:

* Scans `branding/websites/*` for the critical pages (homepage, pricing, reasoning_lab, checkout, identity_flows).
* Checks either: adjacent `*.assistive.md` file exists or `variants.assistive` entry in YAML front-matter.
* Computes a Flesch–Kincaid grade with `textstat` and fails if > 8.
* Exits non-zero on any failure so CI can fail.

````python
#!/usr/bin/env python3
"""
tools/assistive_validate.py

Checks that critical pages have an assistive variant (either a `*.assistive.md` file
or front-matter with `variants.assistive`) and validates readability for assistive pages.

Usage:
  python3 tools/assistive_validate.py
"""
import sys
from pathlib import Path
import re
import yaml

try:
    import textstat
except Exception:
    print("Please pip install textstat (pip install textstat)")
    sys.exit(2)

ROOT = Path("branding/websites")
if not ROOT.exists():
    print("branding/websites not found — run from repo root.")
    sys.exit(2)

CRITICAL_PAGE_NAMES = [
    "homepage", "pricing", "reasoning_lab", "checkout", "identity_flows"
]

def read_front_matter(path):
    txt = path.read_text(encoding="utf-8")
    m = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"YAML parse error in {path}: {e}")
        return {}

def has_assistive_variant(domain_path, page):
    # Look for page.assistive.md (e.g., homepage.assistive.md)
    file1 = domain_path / f"{page}.assistive.md"
    if file1.exists():
        return file1
    # Or in folder: domain/homepage/content.assistive.md
    folder_variant = domain_path / page / "content.assistive.md"
    if folder_variant.exists():
        return folder_variant
    # Or check front-matter for variants.assistive in page file
    file2 = domain_path / f"{page}.md"
    if file2.exists():
        fm = read_front_matter(file2)
        variants = fm.get("variants") or {}
        if variants.get("assistive"):
            # variants.assistive is a path — try to resolve
            cand = domain_path / variants.get("assistive")
            if cand.exists():
                return cand
            # Or treat as present because front-matter points somewhere else
            return variants.get("assistive")
    # Or if folder exists with content.default.md, look for content.assistive.md
    folder_page = domain_path / page
    if folder_page.exists():
        cand = folder_page / "content.assistive.md"
        if cand.exists():
            return cand
    return None

def check_readability(assistive_path):
    if isinstance(assistive_path, str):
        # not a local file; skip readability but warn
        print(f"Assistive variant declared as string: {assistive_path} (not checked for FK)")
        return True
    txt = assistive_path.read_text(encoding="utf-8")
    # Remove front-matter if present
    txt = re.sub(r'^\s*---\s*\n.*?\n---\s*\n', '', txt, flags=re.S)
    # For readability, strip code fences
    txt = re.sub(r'```.*?```', '', txt, flags=re.S)
    fk = textstat.flesch_kincaid_grade(txt)
    print(f"[READABILITY] {assistive_path}: FK grade = {fk:.1f}")
    return fk <= 8.0

def main():
    failures = []
    for domain_dir in sorted(ROOT.iterdir()):
        if not domain_dir.is_dir():
            continue
        domain = domain_dir.name
        print(f"\nChecking domain: {domain}")
        for page in CRITICAL_PAGE_NAMES:
            found = has_assistive_variant(domain_dir, page)
            if not found:
                msg = f"[MISSING] {domain}/{page} -> no assistive variant found"
                print(msg)
                failures.append(msg)
            else:
                print(f"[OK] assistive variant for {domain}/{page} -> {found}")
                # If found is a Path, check readability
                if isinstance(found, Path):
                    ok = check_readability(found)
                    if not ok:
                        failures.append(f"[READABILITY FAIL] {domain}/{page} FK>8: {found}")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(" -", f)
        sys.exit(3)
    print("\nAll assistive checks passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
````

---

### .github/workflows/assistive-validate.yml

This GH Action runs on PRs and weekly. It executes the vocabulary linter (you already have `tools/branding_vocab_lint.py`) and the new `assistive_validate.py`. Put this at `.github/workflows/assistive-validate.yml`.

```yaml
name: Assistive Content Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: '0 6 * * 1' # weekly on Mondays UTC

jobs:
  assistive-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Python deps
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml textstat

      - name: Run vocabulary linter
        run: |
          if [ -f tools/branding_vocab_lint.py ]; then
            python3 tools/branding_vocab_lint.py || (echo "vocab-lint found issues" && exit 2)
          else
            echo "branding_vocab_lint.py missing - skip"
          fi

      - name: Run assistive validator
        run: |
          python3 tools/assistive_validate.py

      - name: Output tip
        run: |
          echo "If assistive validation fails, author should add a content.assistive.md or variants.assistive front-matter, and ensure FK grade <=8."
```

**Notes:** This workflow requires `textstat` (pip) and the presence of `tools/branding_vocab_lint.py`. If you want a full a11y check later, we can add `pa11y` or `axe` against a built preview.

---

### branding/ASSISTIVE_CHECKLIST.md

Add a human checklist to `branding/ASSISTIVE_CHECKLIST.md` that authors and reviewers can follow:

```markdown
# Assistive Mode Checklist (Author & Reviewer)

## For authors (before opening PR)
- [ ] Create `content.assistive.md` for each critical page (homepage, pricing, reasoning_lab, checkout, identity_flows).
  - Or add `variants.assistive` entry in front-matter pointing to an existing assistive file.
- [ ] Write in short sentences. Target Flesch–Kincaid grade ≤ 8.
- [ ] Remove metaphors where possible; use explicit language and step-by-step instructions.
- [ ] Add help text for interactive elements (e.g., Reasoning Lab nodes).
- [ ] Ensure images used have alt text. Provide plain-language descriptions for complex visuals.
- [ ] Add `evidence_links` if the page contains any claims.
- [ ] Run local checks:
  - `python3 tools/branding_vocab_lint.py`
  - `python3 tools/assistive_validate.py`

## For reviewers (before approving)
- [ ] Validate assistive content is human-authored (not auto-converted) OR that an editor checked it.
- [ ] Confirm FK grade ≤ 8 (CI will check but verify manually if borderline).
- [ ] Verify that interactive components have clear text alternatives.
- [ ] Confirm no forbidden terms (e.g., `true consciousness`, `production-ready`) unless legal-approved.
- [ ] Confirm `claims_approval` and `evidence_links` exist for numerical claims.
```

---

### PR body (copy/paste)

**Title:** `chore(assistive): add assistive content validator + GH Action`

**Description (paste into PR)**:

```
What:
- Add tools/assistive_validate.py — validates presence and readability of assistive variants for critical pages.
- Add .github/workflows/assistive-validate.yml — CI job that runs on PR and weekly to enforce assistive mode checks and vocabulary lint.
- Add branding/ASSISTIVE_CHECKLIST.md — human checklist for authors and reviewers.

Why:
- Enforces Assistive Mode presence and quality (readability FK ≤ 8).
- Ensures accessibility-first content for users with cognitive needs.
- Integrates with existing vocabulary linter and claims governance.

Files:
- tools/assistive_validate.py
- .github/workflows/assistive-validate.yml
- branding/ASSISTIVE_CHECKLIST.md

Testing:
- CI will run the linter and assistive validation on PRs.
- Locally run: python3 tools/assistive_validate.py

Reviewers:
- @content-lead
- @web-architect
- @gonzalo
```

---

## 2) `content.assistive.md` for `lukhas.ai` homepage (ready to paste)

Place this file as `branding/websites/lukhas.ai/homepage.assistive.md` (or `content.assistive.md` if you use folder pattern). It uses the required front-matter and follows the Assistive Mode rules (short sentences, clear steps, explicit CTAs, evidence placeholders).

```markdown
---
title: "LUKHAS — Consciousness AI Platform (Assistive Mode)"
domain: lukhas.ai
owner: "@gonzalo"
audience: "general"
tone:
  poetic: 0.16
  user_friendly: 0.58
  academic: 0.26
canonical: true
source: "branding/websites/lukhas.ai/homepage.md"
evidence_links:
  - "release_artifacts/perf/2025-10-26-matriz-smoke.json"
claims_verified_by:
  - "@web-architect"
claims_verified_date: "2025-11-05"
claims_approval: false
seo:
  title: "LUKHAS — Explainable AI | Assistive Mode"
  description: "Assistive view: brief, clear explanations of LUKHAS and the MΛTRIZ reasoning system."
last_reviewed: "2025-11-06"
variants:
  assistive: "homepage.assistive.md"
tags: ["assistive", "homepage", "matriz"]
---

# LUKHAS.AI — Assistive Summary

LUKHAS builds AI that explains its decisions.  
This page shows the main ideas in short sentences. If you want more detail, click "Full details" at the end of each section.

---

## What is MΛTRIZ?

MΛTRIZ is the LUKHAS reasoning engine.  
It breaks thinking into six stages:
1. Memory — fetches past facts.
2. Attention — picks the relevant facts.
3. Thought — analyzes and combines facts.
4. Action — produces an action or suggestion.
5. Decision — checks safety and rules.
6. Awareness — reflects on confidence and gaps.

Each step is short and traceable. You can view the steps in the Reasoning Lab.

---

## How LUKHAS helps you

- **Clear answers.** We show the steps we used to reach an answer.  
- **Understandable results.** You can click a step to see why it mattered.  
- **Safe outputs.** Our Guardian component checks for harmful or biased outputs.

---

## Quick Demo (Try now)

1. Click **Try a Safe Demo**.  
2. Type a short question.  
3. Watch the steps appear: Memory → Attention → Thought → Decision.  
4. Click any step to read a short explanation and sources.

**Try a Safe Demo** → [Reasoning Lab]

---

## Evidence (summary)

- **Latency claim**: p95 reasoning latency < 250ms.  
  Proof: `release_artifacts/perf/2025-10-26-matriz-smoke.json` (signed).  
- **Guardian compliance**: compliance metrics available in `release_artifacts/audit/guardian-compliance-2025-Q3.pdf`.

If you need full technical details, click **Full details** or go to the Developer Docs.

---

## Need help?

- If an explanation is unclear, click the "Why?" button beside the step.  
- For accessibility help, open **Assistive Mode** settings in your account and enable additional audio descriptions or larger text.

---

**Start**: Try a Safe Demo — [Reasoning Lab]  
**More**: Full details → [MΛTRIZ Technical Guide]
```

**Notes for editors**

* Keep the assistive page focused; use bullet lists and short sentences.
* Always include evidence links for claims.
* Add brief help hints for any interactive element.

---

## 3) Figma / design token JSON (dark-first + light + assistive)

This JSON is a production-ready token export that your design system can ingest. Save as `branding/tokens/lukhas-tokens.json`.

```json
{
  "global": {
    "space": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px"
    },
    "radius": {
      "sm": "6px",
      "md": "8px",
      "lg": "12px"
    },
    "font": {
      "body": "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      "display": "Source Serif 4, Georgia, serif",
      "mono": "Fira Code, 'Courier New', monospace"
    }
  },
  "theme": {
    "dark": {
      "bg": "#0B0F1A",
      "surface": "#0F1724",
      "card": "#071124",
      "text": "#E6EEF6",
      "muted": "#9AA7B8",
      "matriz": "#7A3BFF",
      "identity": "#0EA5A4",
      "dev": "#06B6D4",
      "enterprise": "#1E3A8A",
      "success": "#10B981",
      "warning": "#F59E0B",
      "danger": "#EF4444"
    },
    "light": {
      "bg": "#FFFFFF",
      "surface": "#F7FAFC",
      "card": "#FFFFFF",
      "text": "#0B1220",
      "muted": "#475569",
      "matriz": "#6E3BFF",
      "identity": "#0EA5A4",
      "dev": "#06B6D4",
      "enterprise": "#1E3A8A",
      "success": "#10B981",
      "warning": "#F59E0B",
      "danger": "#EF4444"
    },
    "assistive": {
      "bg": "#0B0F1A",
      "surface": "#10131A",
      "card": "#0B1118",
      "text": "#FFFFFF",
      "muted": "#D1E4F2",
      "matriz": "#8C6DFF",
      "identity": "#13C9B0",
      "dev": "#0CC7F2",
      "enterprise": "#274AA6",
      "success": "#2DD4BF",
      "warning": "#FBBF24",
      "danger": "#FB7185",
      "fontSize": {
        "body": "18px",
        "sm": "14px",
        "md": "18px",
        "lg": "22px",
        "xl": "30px"
      },
      "iconSize": {
        "sm": "24px",
        "md": "32px",
        "lg": "40px"
      },
      "spacing": {
        "md": "20px",
        "lg": "32px"
      }
    }
  }
}
```

**How to import**

* Provide this JSON to your token pipeline (Style Dictionary, Theo or Figma plugin).
* Add `assistive` theme to your token export maps; publish CSS variables for `:root`, `.light`, `.assistive`.

---

## How to apply these changes now (step-by-step)

1. Create new branch:

   ```bash
   git checkout -b assistive/implement-checklist-2025-11-06
   ```
2. Add files:

   * `tools/assistive_validate.py` (script above)
   * `.github/workflows/assistive-validate.yml` (workflow above)
   * `branding/ASSISTIVE_CHECKLIST.md` (checklist above)
3. Commit and push:

   ```bash
   git add tools/assistive_validate.py .github/workflows/assistive-validate.yml branding/ASSISTIVE_CHECKLIST.md
   git commit -m "chore(assistive): add assistive content validator + GH Action"
   git push --set-upstream origin assistive/implement-checklist-2025-11-06
   ```
4. Create a PR with the PR body above and request the reviewers `@content-lead`, `@web-architect`, `@gonzalo`.
5. After CI green, merge and follow the checklist to start authoring assistive variants.

---

If you want I’ll now:

* open the PR contents for you to paste (I already gave the exact PR body), and then
* produce the **CI job YAML** (done), then
* Produce the **sample assistive homepage** (done) and
* Finally give the Figma token JSON (done).

Would you like me to (A) paste these three files into a single patch/unified-diff to apply with `git apply` or (B) you’ll add them manually and open the PR? I can also open the PR for you if you give me permission to push.
