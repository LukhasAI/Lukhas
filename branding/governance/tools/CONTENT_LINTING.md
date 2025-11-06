# Content Linting & Governance Scripts for Branding Content

To ensure high-quality, consistent, and compliant content across your branding websites and templates, I've prepared a set of linting and validation scripts along with a GitHub Actions workflow. These tools will help enforce front-matter correctness, evidence backing for claims, vocabulary standards, and link integrity.
The package includes:

1. `tools/front_matter_lint.py` — verifies required front-matter fields, tone distribution, and some sanity checks.
2. `tools/evidence_check.py` — finds numeric/operational claims in page bodies and ensures `evidence_links` and `claims_approval` exist.
3. `tools/branding_vocab_lint.py` — already provided earlier; GH action invokes it (keeps banned terms out).
4. `.github/workflows/content-lint.yml` — the GitHub Actions workflow that runs all of the above + assistive validation + markdown link-check.
5. Short instructions for running locally and notes for reviewers.

Drop these scripts into `tools/` and the workflow into `.github/workflows/`. I also explain required dependencies and the local test commands.

---

## 1) `tools/front_matter_lint.py`

Save this file as `tools/front_matter_lint.py`:

```python
#!/usr/bin/env python3
"""
tools/front_matter_lint.py

Checks Markdown front-matter for required fields and simple validation rules:
- Required keys: title, domain, owner, audience, tone, canonical, source, last_reviewed
- Tone must include poetic, user_friendly, academic and sum to ~1.0 within tolerance.
- claims_approval must be boolean if present.
- If variants.assistive is declared, verify it's non-empty.

Exits 0 on success, non-zero on error.
"""
import re
import sys
import yaml
from pathlib import Path

ROOTS = [Path("branding/websites"), Path("branding/templates")]
REQ_KEYS = ["title", "domain", "owner", "audience", "tone", "canonical", "source", "last_reviewed"]

TONE_KEYS = ["poetic", "user_friendly", "academic"]
TONE_TOL = 0.06  # tolerance for totaling to 1.0

def get_md_files():
    files = []
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.md"):
            files.append(p)
    return sorted(files)

def read_front_matter(path):
    txt = path.read_text(encoding="utf-8")
    m = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"[YAML PARSE ERROR] {path}: {e}")
        return None

def check_tone(fm, path, errors):
    tone = fm.get("tone")
    if not isinstance(tone, dict):
        errors.append(f"{path}: tone must be an object with poetic,user_friendly,academic")
        return
    missing = [k for k in TONE_KEYS if k not in tone]
    if missing:
        errors.append(f"{path}: tone missing keys: {missing}")
        return
    try:
        vals = [float(tone[k]) for k in TONE_KEYS]
    except Exception:
        errors.append(f"{path}: tone values must be numeric")
        return
    s = sum(vals)
    if abs(s - 1.0) > TONE_TOL:
        errors.append(f"{path}: tone sum = {s:.2f} (must be ~1.0, tol {TONE_TOL})")

def check_required(path, fm, errors):
    for k in REQ_KEYS:
        if k not in fm:
            errors.append(f"{path}: missing required front-matter key: {k}")

def check_variants_assistive(path, fm, errors):
    variants = fm.get("variants") or {}
    if "assistive" in variants:
        assist_path = variants.get("assistive")
        if not assist_path:
            errors.append(f"{path}: variants.assistive is empty")
        # if a local relative path is given, ensure file exists
        if isinstance(assist_path, str) and assist_path.endswith(".md"):
            cand = (path.parent / assist_path)
            if not cand.exists():
                # also allow absolute path relative to repo root
                alt = Path(assist_path)
                if not alt.exists():
                    errors.append(f"{path}: variants.assistive points to missing file: {assist_path}")

def check_claims_approval(path, fm, errors):
    if "claims_approval" in fm:
        v = fm.get("claims_approval")
        if not isinstance(v, bool):
            errors.append(f"{path}: claims_approval must be boolean (true/false)")

def main():
    files = get_md_files()
    if not files:
        print("No markdown files found under branding/templates or branding/websites.")
        sys.exit(0)
    errors = []
    for f in files:
        fm = read_front_matter(f)
        if fm is None:
            errors.append(f"{f}: missing or invalid front-matter")
            continue
        check_required(f, fm, errors)
        check_tone(fm, f, errors)
        check_variants_assistive(f, fm, errors)
        check_claims_approval(f, fm, errors)
    if errors:
        print("Front-matter lint found issues:")
        for e in errors:
            print(" -", e)
        sys.exit(2)
    print("Front-matter lint passed for all files.")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**What it does**

* Scans `branding/templates` and `branding/websites` for Markdown files.
* Ensures front-matter present and required keys exist.
* Ensures `tone` has the required keys and sums to ~1.0.
* Verifies `variants.assistive` if present points to a file or non-empty string.
* Ensures `claims_approval` is boolean if present.

**Local run**

```bash
python3 tools/front_matter_lint.py
```

---

## 2) `tools/evidence_check.py`

Save this file as `tools/evidence_check.py`:

```python
#!/usr/bin/env python3
"""
tools/evidence_check.py

Finds numeric / operational claims in Markdown bodies and ensures:
- front-matter contains at least one evidence_links entry
- claims_approval is true when production-level claims appear (p95, %, ms, 'production-ready')

Exit non-zero on failure.
"""
import re
import sys
import yaml
from pathlib import Path

SEARCH_ROOTS = [Path("branding/websites"), Path("branding/templates")]
CLAIM_REGEX = re.compile(r'\b(p95|\bp\d+|p95 reasoning latency\b|\d+%|\d+ms\b|production-ready)\b', flags=re.I)

def md_files():
    out = []
    for root in SEARCH_ROOTS:
        if not root.exists(): continue
        for f in root.rglob("*.md"):
            out.append(f)
    return sorted(out)

def read_front_matter(path):
    txt = path.read_text(encoding="utf-8")
    m = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}, txt
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"[YAML PARSE ERROR] {path}: {e}")
        return {}, txt
    body = txt[m.end():]
    return fm, body

def has_claims(body):
    return bool(CLAIM_REGEX.search(body))

def main():
    errors = []
    for f in md_files():
        fm, body = read_front_matter(f)
        # skip empty front matter files (templates may be validated elsewhere)
        if not fm:
            continue
        if has_claims(body):
            ev = fm.get("evidence_links") or []
            approved = fm.get("claims_approval", False)
            if not ev:
                errors.append(f"{f}: contains numeric/operational claim(s) but no evidence_links in front-matter.")
            if not approved:
                errors.append(f"{f}: contains numeric/operational claim(s) but claims_approval != true.")
    if errors:
        print("Evidence check failed:")
        for e in errors:
            print(" -", e)
        sys.exit(4)
    print("Evidence check passed.")
    sys.exit(0)

if __name__ == "__main__":
    import re
    main()
```

**What it does**

* Searches Markdown bodies for numeric/operational patterns (percentages, ms, p95, production-ready).
* Ensures front-matter contains `evidence_links` and `claims_approval: true`.
* Fails PR if not satisfied.

**Local run**

```bash
python3 tools/evidence_check.py
```

---

## 3) `.github/workflows/content-lint.yml` — GH Actions

Save this to `.github/workflows/content-lint.yml`. This workflow runs on PRs and weekly and executes:

* front-matter lint
* vocab linter (you already have `tools/branding_vocab_lint.py`)
* assistive validator (we added earlier)
* evidence_check
* markdown link checker (markdown-link-check)

```yaml
name: Content Lint & Governance

on:
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: '0 7 * * 1'  # weekly Monday UTC

jobs:
  content-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Python deps
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml textstat

      - name: Front-matter lint
        run: |
          python3 tools/front_matter_lint.py

      - name: Vocabulary lint
        run: |
          if [ -f tools/branding_vocab_lint.py ]; then
            python3 tools/branding_vocab_lint.py
          else
            echo "branding_vocab_lint.py missing; skip"
          fi

      - name: Assistive validation
        run: |
          if [ -f tools/assistive_validate.py ]; then
            python3 tools/assistive_validate.py
          else
            echo "assistive_validate.py missing; skip"
          fi

      - name: Evidence checks
        run: |
          python3 tools/evidence_check.py

      - name: Setup Node for link-check
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install markdown-link-check
        run: npm install -g markdown-link-check

      - name: Run markdown-link-check
        run: |
          echo "Checking markdown links under branding and docs..."
          markdown-link-check -c .mlc.json "branding/**/*.md" || true
          markdown-link-check -c .mlc.json "docs/**/*.md" || true

      - name: Output summary
        run: echo "Content lint completed. Fix any reported issues and rerun."
```

**Notes**

* `markdown-link-check` may return non-zero on broken links; we allow it to complete to show diagnostics but can be toggled to fail CI if you prefer strictness.
* Add `.mlc.json` configuration at repo root to configure `markdown-link-check` options (I can provide a default if you want).

---

## 4) `.mlc.json` — markdown-link-check config (optional)

Create `.mlc.json` at repo root (recommended):

```json
{
  "defaultConfigs": {
    "ignorePatterns": [
      "\\/localhost(:[0-9]+)?\\/",
      "https:\\/\\/example.com",
      "https:\\/\\/.*\\.internal"
    ],
    "retryOn429": true,
    "maxConcurrency": 10,
    "timeout": 10000
  }
}
```

---

## 5) Local running & testing

Install Python deps:

```bash
python3 -m pip install pyyaml textstat
```

Install markdown-link-check (node):

```bash
npm install -g markdown-link-check
```

Run validators locally:

```bash
python3 tools/front_matter_lint.py
python3 tools/evidence_check.py
python3 tools/branding_vocab_lint.py
python3 tools/assistive_validate.py
markdown-link-check "branding/**/*.md"
```

If anything fails, the script prints helpful hints. Fix files, run again, and open PR.

---

## 6) How this integrates with the Brand Guidelines & content flow

* **PRs**: any content PR triggers `content-lint`. Fix failures, re-push. The front-matter linter and evidence check are meant to prevent publishing critical claims without evidence or proper metadata.
* **Assistive & vocab**: already wired; we added assistive CI earlier. The content-lint workflow complements that by ensuring overall front-matter correctness and link hygiene.
* **Release artifacts**: evidence is referenced via `evidence_links`. CI does not require the artifact contents, but you should keep `release_artifacts/` organized and signed for auditors.

---

## 7) Follow-ups I can prepare (optional / recommended)

* A stricter **a11y job** that builds the site and runs pa11y/axe on core pages (requires site build pipeline).
* A script to automatically **generate `claims_registry.yaml`** from front-matter `evidence_links` to produce a single governance view.
* A GitHub PR template that automatically shows required checklist items and blocks merge unless all checks pass.

---

