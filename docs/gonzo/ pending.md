# Automated Repository Audit PromptsThis document contains a set of prompts and a master driver script to automate a comprehensive repository audit using AI agents. The audit covers code quality, security, dependencies, secrets, large files, OpenAI/model usage, PII/storage mapping, and documentation coverage.
---

## How to use these prompts

1. Pick an agent to run each task. Suggestions below.
2. Paste the agent prompt into that agent (or run the local shell commands directly in a terminal).
3. The agent should run commands, collect artifacts, and upload them (or attach them to the chat). If the agent cannot run shell commands, run the shell block locally and then paste outputs to the agent for analysis.
4. After all artifacts are produced, ask GPT-5 Thinking mini or Claude Sonnet 4 to synthesize a single audit report (I give a synthesis prompt too).

---

## Suggested agent roles

* **GitHub Copilot / Codegen** — generate small fixes, CI YAML, and code skeletons (setup_dev already done). Good for PRs and code patches.
* **GPT-5 Thinking mini** — high-level reasoning, synthesis of the outputs into an audit report, prioritization and next steps.
* **Claude Sonnet 4** — run heavy analysis, produce natural-language summaries and risk assessments from long outputs.
* **Local shell / Dev machine** — actually run the diagnostics (pytest, coverage, trivy, detect-secrets). Agents sometimes can't execute; run these directly as needed.

---

## Master driver script (run locally on controller machine)

Save as `scripts/run_all_reports.sh` and run from repo root. It will produce the artifact files agents expect.

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/reports
cd "$(git rev-parse --show-toplevel)"

echo "[1/11] Repo summary"
echo "TOP-LEVEL DIRS" > artifacts/reports/repo_summary.txt
ls -la | sed -n '1,200p' >> artifacts/reports/repo_summary.txt
echo "REPO SIZE" >> artifacts/reports/repo_summary.txt
du -sh . >> artifacts/reports/repo_summary.txt
echo "PY files count" >> artifacts/reports/repo_summary.txt
find . -name '*.py' | wc -l >> artifacts/reports/repo_summary.txt
find tests -name '*test*.py' -print > artifacts/reports/test_files.txt || true
git ls-files --size | awk '$1>10240 {print $0}' | sort -rn > artifacts/reports/large_tracked_files.txt || true

echo "[2/11] Tests & coverage"
pytest -q --maxfail=1 || true
coverage run -m pytest || true
coverage xml -o artifacts/reports/coverage.xml || true
coverage report -m > artifacts/reports/coverage-summary.txt || true
coverage report --skip-covered --show-missing > artifacts/reports/coverage-missing.txt || true

echo "[3/11] Lint & typing"
ruff check --format github . > artifacts/reports/ruff-report.txt 2>&1 || true
black --check . > artifacts/reports/black-report.txt 2>&1 || true
if grep -q 'mypy' pyproject.toml 2>/dev/null || [ -f mypy.ini ]; then
  mypy . > artifacts/reports/mypy-report.txt 2>&1 || true
fi

echo "[4/11] Import health & smoke"
python3 scripts/consolidation/check_import_health.py --verbose > artifacts/reports/import_health.txt 2>&1 || true
make smoke > artifacts/reports/smoke_log.txt 2>&1 || true

echo "[5/11] Dependency & security scan"
pip-audit -r requirements.txt --format json -o artifacts/reports/pip-audit.json || true
pip-licenses --format=json > artifacts/reports/pip-licenses.json || true
safety check -r requirements.txt --json > artifacts/reports/safety.json || true
if [ -f Dockerfile ]; then
  docker build -t lukhas_local_dev:latest . || true
  trivy image --scanners vuln -f json -o artifacts/reports/trivy_image_report.json lukhas_local_dev:latest || true
fi

echo "[6/11] Secrets scan"
detect-secrets scan > artifacts/reports/detect-secrets.json || true
trufflehog git file://$(pwd) --json > artifacts/reports/trufflehog.json || true

echo "[7/11] Large files & LFS"
find . -type f -size +50M -printf '%s %p\n' | sort -rn > artifacts/reports/large_files.txt || true
git lfs ls-files > artifacts/reports/git_lfs_files.txt || true
find . -type f \( -iname '*.safetensors' -o -iname '*.pt' -o -iname '*.ckpt' -o -iname '*.onnx' -o -iname '*.bin' \) -print > artifacts/reports/model_files.txt || true

echo "[8/11] Module manifests & import graph"
find . -name 'module.manifest.json' -print > artifacts/reports/manifests.txt || true
python3 - <<'PY' > artifacts/reports/import_graph.json
import ast, json, glob
graph={}
files=glob.glob('**/*.py', recursive=True)
for py in files:
    if '.venv' in py or 'site-packages' in py: continue
    try:
        src=open(py,'r',encoding='utf8').read()
        tree=ast.parse(src)
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module)
            elif isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
        graph[py]=sorted(list(set(i for i in imports if i)))
    except Exception as e:
        graph[py]=["__PARSE_ERROR__"]
json.dump(graph, open('artifacts/reports/import_graph.json','w'), indent=2)
print('done')
PY

echo "[9/11] OpenAI & model calls"
grep -R --exclude-dir=.git -nE "openai|anthropic|claude|azure.*openai|gpt-|sora|model=" . > artifacts/reports/openai_calls.txt || true
grep -R --exclude-dir=.git -nE "moderation|moderate|content_filter|MODERATE" . > artifacts/reports/moderation_usage.txt || true

echo "[10/11] PII & storage scan"
grep -R --exclude-dir=.git -nE "email|ssn|passport|date_of_birth|dob|personal_data|consent|PII|user_id|user_email|phone" . > artifacts/reports/pii_hits.txt || true
grep -R --exclude-dir=.git -nE "s3://|boto3|azure\\.storage|postgres|psycopg2|mongodb|pymongo|sqlalchemy" . > artifacts/reports/storage_refs.txt || true

echo "[11/11] Docs & module readme coverage"
python3 - <<'PY' > artifacts/reports/docs_coverage.json
import os,json
pkgs=[d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and os.path.exists(os.path.join(d,'__init__.py'))]
missing=[]
for p in pkgs:
    readme=os.path.join(p,'README.md')
    if not os.path.exists(readme):
        missing.append(p)
print(json.dumps({'packages':pkgs,'missing_readme':missing},indent=2))
PY

echo "All reports collected under artifacts/reports/"
```

Make it executable:

```bash
chmod +x scripts/run_all_reports.sh
```

---

## 11 agent prompts — exact (copy/paste)

Below each prompt I include the **expected output files** so you can track artifacts.

---

### Prompt 1 — Repo health

```
You are an automated repo auditor. Run a repo health summary and produce a small JSON file with:
- top-level directories
- repo size (human)
- Python files count
- list of test files
- list of large tracked files (>10MB)
Save results to artifacts/reports/repo_summary.txt and artifacts/reports/test_files.txt and artifacts/reports/large_tracked_files.txt.
Return a one-paragraph summary: repo size, py file count, top 5 large files.
```

**Outputs:** `artifacts/reports/repo_summary.txt`, `artifacts/reports/test_files.txt`, `artifacts/reports/large_tracked_files.txt`

---

### Prompt 2 — Tests & coverage

```
Run pytest fast mode and a coverage run. Produce coverage.xml and summary:
- pytest quick summary
- coverage report, and coverage-missing.txt listing top missing modules.
Save: artifacts/reports/coverage.xml, artifacts/reports/coverage-summary.txt, artifacts/reports/coverage-missing.txt
If tests fail, capture the failing stack traces into artifacts/reports/pytest_failures.txt.
```

**Outputs:** `coverage.xml`, `coverage-summary.txt`, `coverage-missing.txt`, optionally `pytest_failures.txt`

---

### Prompt 3 — Lint / style / types

```
Run ruff, black (check), and mypy where configured. Save outputs to artifacts/reports/ruff-report.txt, black-report.txt, mypy-report.txt.
Also propose a short list of the top 10 (or fewer) lint/type issues and suggested fixes.
```

**Outputs:** `ruff-report.txt`, `black-report.txt`, `mypy-report.txt` (if applicable)

---

### Prompt 4 — Import health & smoke

```
Run the import-health script: scripts/consolidation/check_import_health.py --verbose, and make smoke: make smoke. Save logs to artifacts/reports/import_health.txt and artifacts/reports/smoke_log.txt.
Summarize any import errors, missing modules, or failing services.
```

**Outputs:** `import_health.txt`, `smoke_log.txt`

---

### Prompt 5 — Dependencies & security

```
Run pip-audit, pip-licenses, and safety. If Dockerfile exists, build the local image and run trivy image scan. Save JSON outputs: pip-audit.json, pip-licenses.json, safety.json, trivy_image_report.json
Summarize critical CVEs (CVSS >= 7) and license risks (GPL-type or unknown).
```

**Outputs:** `pip-audit.json`, `pip-licenses.json`, `safety.json`, `trivy_image_report.json`

---

### Prompt 6 — Secrets & history

```
Run detect-secrets or truffleHog across the repository (history + working tree) and produce artifacts/reports/detect-secrets.json (or trufflehog.json). Redact any sensitive matches in the output but list filenames and confidence levels. If matches exist, classify by type (aws-key, ssh-key, private-token).
```

**Outputs:** `detect-secrets.json`, `trufflehog.json`

---

### Prompt 7 — Large files & LFS

```
List files >50MB and model file types (.safetensors/.pt/.ckpt/.onnx/.bin). Check git lfs tracked files. Save results to artifacts/reports/large_files.txt, artifacts/reports/model_files.txt, artifacts/reports/git_lfs_files.txt
If large files are tracked in git (not LFS) annotate them as urgent for history cleanup.
```

**Outputs:** `large_files.txt`, `model_files.txt`, `git_lfs_files.txt`

---

### Prompt 8 — Module manifests & import graph

```
Find all module.manifest.json files and produce a JSON import graph mapping file -> module imports. Save to artifacts/reports/manifests.txt and artifacts/reports/import_graph.json. Flag files with parse errors.
```

**Outputs:** `manifests.txt`, `import_graph.json`

---

### Prompt 9 — Model / OpenAI usage

```
Search repo for OpenAI/Anthropic/Claude/azure model calls and moderation usage. Save to artifacts/reports/openai_calls.txt and moderation_usage.txt. For each call, record filepath, line number, client (openai/anthropic/claude/azure) and whether moderation is used nearby.
```

**Outputs:** `openai_calls.txt`, `moderation_usage.txt`

---

### Prompt 10 — PII & storage mapping

```
Heuristically scan for PII patterns and storage references. Save pii_hits.txt and storage_refs.txt (S3/Azure/Postgres/Mongo references). Produce a short map: potential PII ingestion points and the storage locations used.
```

**Outputs:** `pii_hits.txt`, `storage_refs.txt`

---

### Prompt 11 — Docs & module README coverage

```
Produce a JSON report of top-level Python packages and whether each package has a README or module manifest. Save to artifacts/reports/docs_coverage.json. Also list missing READMEs and modules without manifest.
```

**Outputs:** `docs_coverage.json`

---

## 12) Synthesis prompt — ask GPT-5 Thinking mini / Claude Sonnet 4

When all artifacts exist, ask a high-reasoning agent to synthesize:

```
You are an expert systems auditor. I have produced a set of repository artifacts under artifacts/reports/ (list of files below). Please synthesize a single audit report (max 3 pages) with:
- High-level summary (top 5 urgent issues)
- Security risks (top 3)
- Test/coverage gaps and recommended quick PRs (top 5)
- OpenAI/model usage and compliance red flags
- Data/PII mapping and compliance issues
- Suggested prioritized remediation: 7-day quick sweep and 30-day roadmap
Return: short executive summary, prioritized actions (with owners), and suggested PR titles/messages for each quick fix.
Files: [list artifact filenames here]
```

**Expected output:** `artifacts/reports/audit_summary.txt` (or paste into PR)

---

## Final notes & tips

* **Run everything from controller laptop** (the one that will run experiments). Copy the artifacts to the other laptop as needed.
* **Parallel agent strategy:** run heavy scans (trivy, detect-secrets) in parallel to quick checks (ruff, pytest) — saves time.
* **If agents can’t run shell commands**, run the shell commands locally and paste outputs into the agents for analysis.
* **Store artifacts** in durable location (S3/Azure) and attach a link in the audit report.

---
# Comprehensive Repository Audit Guide. 
This guide provides a set of prompts and a master shell script to automate a comprehensive repository audit using AI agents. The audit covers code quality, security, dependencies, secrets, large files, OpenAI/model usage, PII/storage mapping, and documentation coverage.

`run_all_reports.sh` driver, and provide how to synthesize the outputs into a final T4 audit summary.

Keep this page open while you run things. Workflow:

1. Run the automated shell driver on your **controller laptop** (this produces the raw artifacts).
2. While it runs, use your **IDE agents** to generate fixes, CI YAMLs, and PR text.
3. Feed the artifacts to a high-reasoning model (GPT-5 Thinking mini or Claude Sonnet 4) for synthesis.
4. Use GitHub Copilot for quick PR creation and code patches.

---

## Which agent to use for what (short)

* **Local shell / controller** — run `scripts/run_all_reports.sh` (actual heavy scans, coverage, trivy, detect-secrets).
* **GitHub Copilot** — generate CI YAMLs, small code fixes, commit messages, PR bodies. Best for incremental PRs.
* **Codex OpenAI** — generate code templates, unit test skeletons, bootstrap_test & contradiction_score functions.
* **Claude Code** — analyze long outputs (pip-audit, detect-secrets), produce a safe risk summary and mitigation suggestions.
* **Gemini** — produce a human-friendly executive summary (optional).
* **GPT-5 Thinking mini** (if available) — *final* audit synthesis and prioritized roadmap (T4-style recommendations).

---

## A. Run the reports on the controller laptop

**Pre-reqs** (run once):

```bash
# Install recommended CLI tools (you may already have these)
pip install coverage ruff pip-audit pip-licenses safety detect-secrets truffleHog
# System tools for scanning
# trivy - install via brew or apt; for mac: brew install aquasecurity/trivy/trivy
# gh (GitHub CLI): https://cli.github.com/
chmod +x scripts/run_all_reports.sh
```

**Run the driver (this produces everything):**

```bash
# from repo root
./scripts/run_all_reports.sh
# outputs will be under artifacts/reports/
```

This may take 10–40 minutes depending on tests and trivy. Leave it running; while it runs, proceed with the agent tasks below.

---

## B. Exact agent prompts (copy/paste)

Below are **ready-to-paste prompts** per extension. Paste each into the chat window of that extension and run. If the extension cannot run shell commands, paste the resulting files into the chat afterward for analysis.

### 1) **GitHub Copilot** — create CI jobs & pre-commit config

**Paste to Copilot chat:**

```
I need small CI and pre-commit artifacts for this Python repo.

Please generate:
1) A GitHub Actions CI workflow `/.github/workflows/ci.yml` that:
   - runs on push and pull_request,
   - sets up Python 3.10,
   - installs dependencies from requirements.txt,
   - runs ruff, black --check, pytest (fast mode),
   - runs coverage and uploads coverage.xml,
   - runs pip-audit and reports results (non-blocking by default).

2) A GitHub Actions job `security.yml` for trivy (if Dockerfile present) and detect-secrets that runs nightly.

3) A `.pre-commit-config.yaml` that runs ruff and black and the detect-secrets local hook.

Keep the YAML compact, with comments. Output the three files (content only).
```

**Why Copilot:** Great for generating concise CI snippets and `pre-commit` configs; you can quickly iterate and add repo specifics.

---

### 2) **Codex OpenAI** — code templates for tests & utilities

**Paste to Codex OpenAI chat:**

```
Generate Python code templates for these helper functions to include in `scripts/`:

1) `bootstrap_test.py` — performs a bootstrap test comparing two lists of numeric distances and returns p-value & 95% CI; includes a CLI interface `--in file.json --out report.json`.

2) `contradiction_score.py` — function `contradiction_score(cycle, meta)` that computes a semantic+causal mismatch. Provide a simple version using embeddings cosine distance and a placeholder causal mismatch metric (explain where to plug the causal signal).

3) `wavec_snapshot.py` — functions to serialize memory state, gzip it, compute sha256, sign with HMAC (ENV: WAVEC_HMAC_KEY), and upload to S3/Azure (use `AZURE_STORAGE_CONNECTION_STRING` or `AWS_ACCESS_KEY_ID`/AWS secret fallback). Include CLI to `--snapshot file.json --run-id RUNID`.

Return code only with docstrings, and small unit test skeletons for each in `tests/`.
```

**Why Codex:** Great at generating correct, runnable code and small unit test skeletons.

---

### 3) **Claude Code** — analyze large outputs & produce risk summary

**Paste to Claude Code chat and attach the large artifacts** (or paste contents of `pip-audit.json`, `trufflehog.json`, `trivy_image_report.json`, `detect-secrets.json`):

```
You are a security auditor. I have these raw scan outputs:
- artifacts/reports/pip-audit.json
- artifacts/reports/trivy_image_report.json
- artifacts/reports/detect-secrets.json
- artifacts/reports/trufflehog.json

Please:
1) Summarize the top 5 security vulnerabilities (CVSS >= 7) with file/module references and how to fix them quickly.
2) Summarize secrets findings (high confidence) with remediation (rotate keys, revoke, secrets manager).
3) Output a prioritized remediation list: urgent (fix in 24h), high (7d), medium (30d), with suggested PR titles and short commit message templates.

Return structured JSON and a 1-paragraph executive summary.
```

**Why Claude:** Handles large JSON and provides nuanced risk mitigation.

---

### 4) **Gemini or GPT-5 Thinking mini** — audit synthesis

**Paste to GPT-5 Thinking mini or Gemini (best for final)** and attach the other text artifacts (`coverage-summary.txt`, `coverage-missing.txt`, `ruff-report.txt`, `openai_calls.txt`, `pii_hits.txt`, `import_graph.json`):

```
You are a T4-grade system auditor. I have the following repository audit artifacts in artifacts/reports/:
[list the files: coverage-summary.txt, coverage-missing.txt, ruff-report.txt, import_health.txt, openai_calls.txt, pii_hits.txt, import_graph.json and the security outputs summarized by Claude.]

Produce a consolidated audit report (max 3 pages) with:
- Executive summary (top 5 urgent issues).
- Security risks (top 3), compliance risks (top 3).
- Test/coverage gaps and a short prioritized list of quick PRs (5) to raise baseline.
- OpenAI/model usage red flags (top 3), and quick fixes for alignment/moderation.
- PII storage & retention urgent items.
- A 7-day “quick sweep” plan and a 30-day roadmap. For each item include owner roles and approximate time (hours/days).

Return structured JSON with `urgent`, `high`, `medium`, and a plain text report for posting to stakeholders.
```

**Why GPT-5 Thinking mini / Gemini:** They synthesize many inputs into a crisp, prioritized plan in T4 style.

---

## C. How to combine agent outputs & produce PRs

1. **Run the driver** and wait for artifacts.
2. **Feed the artifacts** to Claude Code for security summarization.
3. **Use Copilot** to generate CI/pre-commit patches and small fixes (use the Copilot prompt above). Save as branch `infra/initial-audit-fixes-2025-10-26`.
4. **Use Codex** to create the test & snapshot utilities. Commit in a feature branch `tools/bootstrap-wavec-2025-10-26`.
5. **Feed everything to GPT-5 Thinking mini** for final audit and the prioritized 7-day sweep.
6. **Open small PRs** for the quick fixes (ruff, pre-commit, pip-audit job, secrets scan, doc placeholders). Use Copilot to craft PR body and commit messages.

---

## D. Practical notes & operations

* **Run the heavy scans on the machine with highest RAM/CPU** (controller). Trivy and full pytest coverage can be heavy.
* **When giving artifacts to the cloud models**, redact secrets (don’t paste raw secret values). Use truncated masks for keys. For example `AKIA***REDACTED`.
* **Upload artifacts** to a private artifact store (S3/Azure) and give agents file contents or summaries; for large JSON, zip them and attach.
* **If an agent cannot run shell commands**, run scripts locally and paste the outputs into the agent for analysis.

---
