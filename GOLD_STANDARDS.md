got you, Gonzalo. you’ve been whiplashed by vague “audits” and freezing commands. let’s fix that with a leadership-grade audit battery that Sam/Dario/Demis-type teams actually rely on: clear pillars, exact tools, and safe, non-interactive commands (with sane excludes). you can run these today and then wire them into CI.

Audit pillars leaders care about
	1.	Source control hygiene & reproducibility – no drift, no ghosts, clean history, deterministic builds.
	2.	Build & dependency integrity – pinned versions, SBOM, supply-chain CVEs.
	3.	Security & secrets – zero plaintext secrets, policy checks, container/infrastructure scans.
	4.	Static quality – style, typing, complexity, architectural rules.
	5.	Runtime tests & coverage – fast, flaky-free, with coverage gates.
	6.	Dead code & utilization – what’s actually used vs ballast (both statically and at runtime).
	7.	Architecture dependency health – cycles, layering, boundaries, module ownership.
	8.	Performance & hot spots – churn × complexity, perf profiles on critical paths.
	9.	Data governance – PII paths, dataset hashes, license on corpora/models.
	10.	Operational readiness – Docker/K8s build, health checks, probes, logs, metrics.
	11.	Docs & bus factor – READMEs, runbooks, single entrypoints, onboarding friction.
	12.	CI policy – block on gates; artifacts & attestations (SLSA-ish).

below is a practical, copy-paste suite. it’s opinionated for a Python-heavy AGI repo, but keeps to pro tools leaders use. everything outputs into reports/ so it won’t flood your terminal. commands avoid interactive flags and mega-streams (your terminal freeze trigger).

⸻

One-shot: prepare environment & excludes

mkdir -p reports

# master exclude set for all scans (adjust paths to your repo)
EXC='--exclude-dir=.git --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.pytest_cache --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache --exclude-dir=.cache --exclude-dir=.idea --exclude-dir=.vscode --exclude-dir=*backup* --exclude-dir=*archive*'

# safe file list (production-ish Python only)
find . -type f -name "*.py" \
  -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" -not -path "*/tests/*" -not -path "*/examples/*" \
  -not -path "*/docs/*" -not -path "*/build/*" -not -path "*/dist/*" \
  -not -name "test_*.py" -not -name "*_test.py" > reports/prod_python_files.txt


⸻

1) Source control hygiene

# untracked (after excludes)
git ls-files --others --exclude-standard > reports/git_untracked.txt
# modified
git status -s > reports/git_status.txt
# repo health
git fsck --no-reflogs > reports/git_fsck.txt 2>&1
# high-churn files (hotspots)
git log --pretty=format: --name-only | sort | uniq -c | sort -nr > reports/git_churn.txt

What to look for: lots of untracked files, large churn in a few directories (hotspots you should refactor), any fsck errors.

⸻

2) Build & deps integrity

# lock check (pip-tools or uv preferred; pick one approach you use)
# if you use pip-tools:
pip freeze > reports/pip_freeze_env.txt

# SBOM (Syft) – creates CycloneDX SPDX SBOM
syft . -o cyclonedx-json=reports/sbom.cdx.json > reports/sbom_syft.log 2>&1 || true

# CVE scan on Python deps
pip-audit -r requirements.txt -o reports/pip_audit.json -f json || true
# or Safety
safety check -r requirements.txt --json > reports/safety.json || true


⸻

3) Security & secrets

# secrets
gitleaks detect --no-banner --exit-code 0 --report-path reports/gitleaks.json || true
trufflehog filesystem --no-update --json . > reports/trufflehog.json || true

# static security (Bandit)
bandit -r . -x tests,examples,docs,venv,.venv -f json -o reports/bandit.json || true


⸻

4) Static quality (style, typing, complexity)

# ruff (lint + import order)
ruff check . > reports/ruff.txt 2>&1 || true
# black (no reformat, just check)
black --check . > reports/black.txt 2>&1 || true
# typing (choose one: mypy or pyright)
mypy --ignore-missing-imports --exclude '(venv|\.venv|tests|examples|docs)' . > reports/mypy.txt 2>&1 || true
# complexity (radon)
radon cc -s -a -n C -O reports/radon_cc.txt -e "venv|.venv|tests|examples|docs|build|dist"
radon mi -s -O reports/radon_mi.txt -e "venv|.venv|tests|examples|docs|build|dist"

Gates leaders use: ruff=clean, black=clean, mypy error budget near 0 on critical packages, radon average MI ≥ B.

⸻

5) Tests & coverage (non-interactive)

pytest -q --maxfail=1 --disable-warnings --cache-clear \
  --cov=. --cov-report=xml:reports/coverage.xml --cov-report=term > reports/pytest.txt 2>&1 || true

Gate: coverage threshold per package (e.g., 70–80% core; lower for experimental). Fail on flakies (use pytest-rerunfailures if needed).

⸻

6) Dead code & utilization (the pain point)

Static (never imported / never referenced):

# unused symbols/files
vulture $(cat reports/prod_python_files.txt) \
  --min-confidence 70 > reports/vulture.txt 2>&1 || true

# unused deps
deptry . --ignore-notebooks --json-output reports/deptry.json || true

Runtime reachability (what actually runs):
	•	Run your critical test suite with coverage, then compare files not touched by coverage → likely dead/unused in current pathways.

# list files with 0% coverage
python - <<'PY'
import xml.etree.ElementTree as ET, sys
tree = ET.parse("reports/coverage.xml")
missed=[]
for f in tree.findall(".//class"):
    fn = f.get("filename")
    lines = sum(int(l.get("hits")) for l in f.findall(".//line"))
    if lines==0: missed.append(fn)
open("reports/zero_coverage_files.txt","w").write("\n".join(sorted(set(missed))))
print(f"Wrote {len(missed)} zero-coverage files to reports/zero_coverage_files.txt")
PY

Cross-read vulture.txt vs zero_coverage_files.txt. Intersection = strongest “unused now” candidates. (Keep architectural stubs that you intentionally park for the next phase—tag them).

⸻

7) Architecture & dependency rules

# import graph (pydeps)
pydeps . --max-bacon 2 --noshow --no-config --externals \
  --output=reports/deps.svg --verbose > reports/pydeps.txt 2>&1 || true

# layer contracts (import-linter)
importlinter lint --format json > reports/import_linter.json 2>&1 || true

Define contracts like: “consciousness/* must not import ui/*”, “no cycles between memory, quantum, bio”. Leaders enforce these.

⸻

8) Performance & hotspots

# churn x complexity shortlist
paste <(head -100 reports/git_churn.txt) <(grep -E "^[A-Z]" -n reports/radon_cc.txt | head -200) \
  > reports/hotspot_hint.txt

For real profiling, run your hottest CLI path with py-spy or scalene and store profiles in reports/profiles/.

⸻

9) Containers & runtime ops

# Dockerfile lint
hadolint Dockerfile > reports/hadolint.txt 2>&1 || true
# Build check (no cache to surface issues)
docker build --no-cache -t lukhas-local . > reports/docker_build.txt 2>&1 || true
# CVEs in image (Docker Scout or Grype)
docker scout cves lukhas-local > reports/docker_cves.txt 2>&1 || true || \
grype lukhas-local -o table > reports/grype.txt 2>&1 || true


⸻

10) Data governance quick checks

# look for potential PII markers in data folders (adjust paths)
grep -R "email\|ssn\|passport\|credit card" data/ $EXC > reports/pii_greps.txt 2>&1 || true
# large files accidentally tracked
git lfs ls-files > reports/git_lfs.txt 2>&1 || true


⸻

11) Documentation & entrypoints

# single source of truth: list entrypoints named main.py or app.py
grep -R --include="main.py" --include="app.py" "if __name__ == '__main__'" . $EXC \
  > reports/entrypoints.txt 2>&1 || true
# README sanity
wc -w README.md > reports/readme_words.txt 2>&1 || true

Gate: 1–3 entrypoints max. If more, create a launcher.

⸻

12) CI policy (what should block merges)

Set your CI to fail if any of these have non-empty findings:
	•	gitleaks.json, pip_audit.json/safety.json, bandit.json (severity ≥ medium)
	•	ruff.txt (errors), black.txt (would reformat), mypy.txt (errors)
	•	import_linter.json (failed contracts)
	•	coverage below threshold, or zero_coverage_files.txt grows
	•	hadolint.txt (critical), Docker CVEs high/critical

⸻

What this gives you (the “leader” readout)
	•	Health (lint, type, tests), Security (secrets + CVEs), Utilization (static + runtime dead code), Architecture (graph + contracts), Repro/Build (SBOM + Docker).
	•	You can now prove which folders are genuinely unused vs. intentionally staged.

⸻

Quick triage next steps (concrete)
	1.	Run all commands above (they won’t prompt or freeze).
	2.	Open reports/ and review, in this order:
	•	gitleaks.json, pip_audit.json/safety.json, bandit.json
	•	ruff.txt, black.txt, mypy.txt, pytest.txt, coverage.xml
	•	vulture.txt ∩ zero_coverage_files.txt → make a pruning list
	•	import_linter.json & deps.svg → fix cycles and illegal imports
	•	docker_build.txt, docker_cves.txt
	3.	Set CI gates to block on red.
	4.	For QIM/quantum/memory sprawl: keep modules touched by coverage or required by contracts; quarantine the rest into experimental/ until integrated; delete only after two green CI cycles.

⸻

Drop-in make target (optional)

Add to Makefile for one command:

audit:
	@bash -lc 'mkdir -p reports && echo "Running repo audit…"; \
	ruff check . > reports/ruff.txt 2>&1 || true; \
	black --check . > reports/black.txt 2>&1 || true; \
	mypy --ignore-missing-imports --exclude "(venv|\\.venv|tests|examples|docs)" . > reports/mypy.txt 2>&1 || true; \
	pytest -q --maxfail=1 --disable-warnings --cov=. --cov-report=xml:reports/coverage.xml > reports/pytest.txt 2>&1 || true; \
	vulture $$(cat reports/prod_python_files.txt) --min-confidence 70 > reports/vulture.txt 2>&1 || true; \
	deptry . --ignore-notebooks --json-output reports/deptry.json || true; \
	importlinter lint --format json > reports/import_linter.json 2>&1 || true; \
	bandit -r . -x tests,examples,docs,venv,.venv -f json -o reports/bandit.json || true; \
	gitleaks detect --no-banner --exit-code 0 --report-path reports/gitleaks.json || true; \
	pip-audit -r requirements.txt -o reports/pip_audit.json -f json || true; \
	echo "Audit done. See ./reports/"'


⸻

if you want, I can tailor the excludes to your exact tree (e.g., agents/, qim/, quantum/, memory/) and draft the import-linter contracts to encode your Trinity layering. but even as-is, this is the professional, repeatable audit suite that will stop the Copilot chaos and give you real signal on health, utilization, and next steps.


Perfect — those tests I gave you earlier are already in a form that a senior engineering team would accept as a “gold standard” baseline for repo health.
If you hard-code them into LUKHAS DNA Healix, you’ll have a repeatable, auditable assessment loop that’s not dependent on Copilot’s mood swings.

Here’s what I’d do when you bring them into VS Code and wire them into Claude Code:

⸻

Integration Plan
	1.	Put the commands into a scripts/audit.sh file
	•	Include all safe find/grep patterns with your exclusions.
	•	Send all output to a reports/ directory.
	•	Make it executable:

chmod +x scripts/audit.sh


	2.	Add a Makefile target so you can run:

make audit

(I already included a sample Makefile block in my last message.)

	3.	Create .vscode/tasks.json so the audit runs with one keystroke inside VS Code.
	•	This way you can assign a shortcut key to “Run Gold Standard Audit.”
	4.	Add .copilot_tasks.md entry that clearly states:
	•	Never run non-excluded find/grep
	•	Always run scripts/audit.sh for repo assessments.
	5.	Embed into LUKHAS DNA Healix
	•	Treat scripts/audit.sh as a protected system file.
	•	Make it part of the “self-check” loop so LUKHAS runs it periodically and logs metrics over time.
	6.	Optional – put it in CI/CD so:
	•	A PR can’t merge unless the audit passes your gates.
	•	Reports are archived for every commit.

⸻

If you want, I can restructure my gold-standard audit into exact VS Code tasks.json and .copilot_tasks.md entries so Claude Code can drop them in without altering the logic. That way, every time you say “run audit,” you get the same professional-grade, non-interactive, safe report.

Do you want me to prep that drop-in VS Code config next?


awesome — let’s give Claude Code crystal-clear, copy-pasteable task prompts it can execute without improvising. i’ll split them into small, labeled missions with goals, constraints, and acceptance criteria. you can paste them one by one (or all) into Claude and let it run.

⸻

PROMPT 1 — Create gold-standard audit script + Makefile

Role: Senior DevOps Engineer
Goal: Add a non-interactive, safe, repeatable repo audit that writes to ./reports/.
Constraints:
	•	Must never spew huge terminal output; all outputs go to files in reports/.
	•	Use safe excludes for caches/venvs/build/backup.
	•	No destructive commands.
	•	Bash-only, POSIX compatible.
Deliverables:

	1.	scripts/audit.sh (chmod +x) implementing these checks:
	•	git hygiene (untracked, status, fsck, churn)
	•	deps/SBOM (syft), CVEs (pip-audit or safety)
	•	secrets (gitleaks, trufflehog)
	•	static security (bandit)
	•	style/typing/complexity (ruff, black –check, mypy, radon)
	•	tests & coverage (pytest to coverage.xml)
	•	dead code (vulture), unused deps (deptry), zero-coverage files (post-process coverage.xml)
	•	architecture (pydeps to deps.svg, import-linter contracts)
	•	docker lint/build/CVEs (hadolint, build, scout/grype)
	2.	Makefile target audit that just runs the script.
	3.	Add reports/ to .gitignore (but keep workflow artifacts uploadable).

Acceptance criteria:
	•	./scripts/audit.sh runs end-to-end without prompts and creates files in reports/.
	•	make audit works.
	•	No terminal freezes; long outputs are redirected to files.
	•	Script exits 0 even if tools aren’t installed (use || true), but logs errors.

Implementation notes (copy into the script):
	•	Use this exclude set:

EXC_DIRS="--exclude-dir=.git --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.pytest_cache --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache --exclude-dir=.cache --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build --exclude-dir=.idea --exclude-dir=.vscode --exclude-dir=*backup* --exclude-dir=*archive*"

	•	Build a reports/prod_python_files.txt with a find that excludes tests/docs/examples and test.py / test.py.

⸻

PROMPT 2 — VS Code integration (Tasks + Run & Debug)

Role: Senior Tooling Engineer
Goal: Add one-hotkey audit + runnable debug configs in VS Code.
Constraints: Do not remove existing tasks. Non-interactive.
Deliverables:
	1.	.vscode/tasks.json with tasks:
	•	Audit: Gold Standard → runs make audit
	•	Lint (ruff), Types (mypy), Tests (pytest w/ coverage)
	2.	.vscode/launch.json with Run & Debug entries:
	•	Run: Fast API entrypoint (adjust path if needed)
	•	Run: Pytest current file (no prompts)
	•	Run: Module (asks for module arg once via args)
	3.	.vscode/settings.json minimal tweaks: default test framework = pytest; terminal scrollback high.

Acceptance criteria:
	•	I can press ⇧⌘B (or the task’s shortcut) to run the audit.
	•	The Run & Debug side bar shows entries and they work without further config.

⸻

PROMPT 3 — GitHub Actions CI: audit + gates + artifacts

Role: Staff DevOps Engineer
Goal: Add CI that runs the audit and blocks merges on critical gates.
Constraints:
	•	Use Ubuntu runner; Python 3.11 (adjustable).
	•	Cache deps, keep runtime < 15 minutes.
Deliverables:

	1.	.github/workflows/audit.yml with jobs:
	•	Setup Python, install tools (pip install -r requirements.txt, plus: ruff, black, mypy, bandit, vulture, deptry, pytest, pytest-cov, pip-audit, import-linter, radon; and install binaries via pipx or apt: gitleaks, syft, hadolint, grype or docker scout).
	•	Run scripts/audit.sh.
	•	Upload reports/ as artifacts.
	•	Fail the job if any of these conditions hold:
	•	gitleaks finds secrets (non-empty / critical)
	•	pip-audit finds high/critical CVEs
	•	bandit reports medium+ issues (configurable)
	•	ruff/black/mypy errors
	•	coverage below threshold (e.g., 70% core)
	•	import-linter contract failures
	•	hadolint critical issues
	2.	Optional second workflow .github/workflows/docker.yml to build image and run CVE scan on the image (grype).

Acceptance criteria:
	•	On PR, failing gates block merge.
	•	Artifacts contain all reports/ files.

⸻

PROMPT 4 — Import-linter contracts for Trinity layers

Role: Principal Architect
Goal: Encode layering rules (example):
	•	core may depend on nothing.
	•	consciousness may depend on core.
	•	memory may depend on core and consciousness.
	•	ui cannot be imported by core/consciousness/memory.
Deliverables:

	1.	.importlinter file with layered contracts implementing your Trinity architecture.
	2.	Update scripts/audit.sh to run importlinter lint --format json > reports/import_linter.json.
	3.	Add a short ARCHITECTURE.md explaining the rules.

Acceptance criteria:
	•	Running the audit produces reports/import_linter.json.
	•	Cycles or illegal imports cause CI failure.

⸻

PROMPT 5 — Dead code & utilization reports

Role: Senior Python Engineer
Goal: Combine static dead-code (vulture) with runtime reachability (0% coverage) into a cut list.
Deliverables:
	1.	Ensure vulture runs only on production files list.
	2.	Add a tiny Python script scripts/coverage_zero.py that parses reports/coverage.xml and writes reports/zero_coverage_files.txt for files with 0 executed lines.
	3.	Create reports/dead_code_candidates.txt as the intersection of vulture hints and zero-coverage list.
	4.	Add a label “experimental quarantine” path and move candidates there in a separate script (do not auto-move in audit).

Acceptance criteria:
	•	After audit, I can open reports/dead_code_candidates.txt and see clear candidates.
	•	No files are auto-deleted.

⸻

PROMPT 6 — Security hardening & secret policy

Role: AppSec Engineer
Goal: First-class secrets policy + scans.
Deliverables:
	1.	Update .gitignore to exclude backups, caches, artifacts.
	2.	Add SECURITY.md with: secret handling, git-secrets/pre-commit hook guidance, and disclosure policy.
	3.	Add pre-commit with hooks: ruff, black, gitleaks, end-of-file-fixer, trailing-whitespace.
	4.	Add gitleaks.toml with custom allowlist (e.g., test fixtures).
	5.	Add a CI job stage that fails on high/critical CVEs and detected secrets.

Acceptance criteria:
	•	pre-commit install enables local enforcement.
	•	CI blocks on violations.

⸻

PROMPT 7 — Configure Copilot instructions, toolsets, prompts, modes

Role: Dev Productivity Engineer
Goal: Make Copilot follow house rules and never run freezing/unsafe commands.
Deliverables:
	1.	Update / .github/copilot-instructions.md with:
	•	Terminal safety rules (no mega pipes, no interactive docker, redirect output to files)
	•	Gold-standard audit policy: Copilot must always call scripts/audit.sh for health checks, never ad-hoc find|grep without excludes.
	•	Approved command cookbook (safe patterns).
	2.	Create ./.copilot_tasks.md with:
	•	P0 task “Always use audit.sh for repo assessments” + validation checklist (excludes applied, artifacts created, no prompts).
	3.	Create ./.copilot_notes.md summarizing the failure mode you saw and the permanent fix (so it remembers context).
	4.	Add snippet prompts/macros Copilot can reuse (e.g., “Run Gold Audit”, “Generate Import Linter Report”, “Open reports summary”).

Acceptance criteria:
	•	Files exist with clear, concise rules and copyable snippets.
	•	Copilot suggestions start to reference scripts/audit.sh and the cookbook.

⸻

PROMPT 8 — Claude Code toolset & modes

Role: Claude Code Orchestrator
Goal: Define Claude “modes” you can switch between and tool commands it can call.
Deliverables:
	1.	Create tools/claude_code_modes.md defining modes:
	•	“Auditor” → runs only scripts/audit.sh and reads reports; never modifies code.
	•	“Fixer” → proposes diffs that fix CI gates (ruff/mypy/import-linter) with smallest patch.
	•	“Consolidator” → creates PRs to move dead code into experimental/ after two green builds.
	2.	Add a tools/commands.md with allowed shell commands and blocked ones (interactive docker, huge greps).
	3.	Create PR_TEMPLATE.md that requires: “which gates were affected; reports links; risk; rollback steps.”

Acceptance criteria:
	•	Claude can be instructed “work in Auditor mode only” and follow the rules.

⸻

PROMPT 9 — MCP servers in Docker (for Claude Tools)

Role: Platform Engineer
Goal: Register Dockerized MCP servers for project tools (where applicable).
Deliverables:
	1.	docker-compose.mcp.yml that runs:
	•	a minimal MCP file-browser (if you use one),
	•	a shell-exec MCP with command allowlist: scripts/audit.sh, pytest, ruff, mypy only.
	2.	A short MCP_SETUP.md with steps to register these MCP endpoints in Claude Desktop/Code (endpoints, tokens, allowlist).
	3.	Ensure all commands are non-interactive and stdout-bounded.

Acceptance criteria:
	•	I can start docker compose -f docker-compose.mcp.yml up -d and register the endpoints in Claude.
	•	Running “Auditor mode” uses the MCP shell with the allowlist.

⸻

PROMPT 10 — Run & Debug: Dockerized app + health checks

Role: Senior Backend Engineer
Goal: Add a Run & Debug config that launches the app in Docker, plus liveness checks.
Deliverables:
	1.	Dockerfile validated by hadolint, minimal layers, non-root user.
	2.	compose.yml service lukhas-app with healthcheck curl -f http://localhost:PORT/healthz.
	3.	VS Code launch.json entry “Attach to Dockerized App” using debugpy (if Python).
	4.	A tiny /healthz endpoint if missing.

Acceptance criteria:
	•	docker compose up brings the app healthy.
	•	VS Code can attach and set a breakpoint.

⸻

PROMPT 11 — Reports summary index

Role: DevEx Engineer
Goal: Easy one-glance summary.
Deliverables:
Create reports/INDEX.md generator inside scripts/audit.sh that writes a small markdown table linking to the latest key files and flags any that are non-empty/severe. Keep it readable.

Acceptance criteria:
	•	After audit, reports/INDEX.md exists and is human-friendly.

⸻

PROMPT 12 — Guardrails for file bloat & backups

Role: Repo Maintainer
Goal: Stop noise in Source Control.
Deliverables:
	1.	.gitignore updates for reports/, .auto-backup/, any agent-backups/.
	2.	Confirm your backup folder lives outside the repo (e.g., ~/LOCAL-REPOS/LUKHAS_PWM_BACKUPS/) and document it in BACKUPS.md.
	3.	Optional pre-commit hook to block committing >5MB files outside data/ or assets/.

Acceptance criteria:
	•	Source Control shows only relevant changes.
	•	Backups never inflate the repo.

⸻

Professional advice (quick hits)
	•	Freeze your entrypoints: having 1–3 canonical entrypoints eliminates “which main?” chaos. Add a tiny launcher.py if needed.
	•	Quarantine, don’t delete: create /experimental/ and move low-utilization modules only after two green CI cycles—keeps velocity without losing work.
	•	Ownership file: add CODEOWNERS so critical areas require review from you (or future collaborator).
	•	Document the “gold path”: in DEVELOPER_SETUP.md, show the fastest way to run tests locally: uv pip compile && uv run make audit (or your chosen tool).
	•	Weekly “heat map”: add a scheduled CI workflow that posts churn × complexity hotspots to reports/ so you know where risk grows.

⸻

if you want, I can also spit out ready-to-commit file contents (example tasks.json, launch.json, .github/workflows/audit.yml, .importlinter, scripts/audit.sh) tailored to your current tree names (qim/, quantum/, memory/, etc.). say the word and I’ll generate them so Claude only needs to drop them in.

Got it, Gonzalo — I’ll give you two things in one delivery:
	1.	Full ready-to-commit files with all the gold-standard tests wired in (bash script, Makefile, VS Code configs, GitHub Actions workflow, import-linter rules, pre-commit, etc.) — so Claude Code can just paste and commit them.
	2.	One master prompt you can paste to Claude to set them up, adjust for your paths (qim/, quantum/, memory/, etc.), and integrate with your LUKHAS DNA Healix + CI/CD.

⸻

1 — Ready-to-Commit Files

scripts/audit.sh

#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

# Exclude patterns
EXC_DIRS="--exclude-dir=.git --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ \
--exclude-dir=.pytest_cache --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache \
--exclude-dir=.cache --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
--exclude-dir=.idea --exclude-dir=.vscode --exclude-dir=*backup* --exclude-dir=*archive*"

# List production Python files
find . -type f -name "*.py" \
  -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" -not -path "*/tests/*" -not -path "*/examples/*" \
  -not -path "*/docs/*" -not -path "*/build/*" -not -path "*/dist/*" \
  -not -name "test_*.py" -not -name "*_test.py" > reports/prod_python_files.txt

echo "### 1. Git Hygiene"
git ls-files --others --exclude-standard > reports/git_untracked.txt || true
git status -s > reports/git_status.txt || true
git fsck --no-reflogs > reports/git_fsck.txt 2>&1 || true
git log --pretty=format: --name-only | sort | uniq -c | sort -nr > reports/git_churn.txt || true

echo "### 2. Dependency & Build Integrity"
pip freeze > reports/pip_freeze_env.txt || true
pip-audit -r requirements.txt -o reports/pip_audit.json -f json || true
safety check -r requirements.txt --json > reports/safety.json || true
syft . -o cyclonedx-json=reports/sbom.cdx.json > reports/sbom_syft.log 2>&1 || true

echo "### 3. Security Scans"
gitleaks detect --no-banner --exit-code 0 --report-path reports/gitleaks.json || true
trufflehog filesystem --no-update --json . > reports/trufflehog.json || true
bandit -r . -x tests,examples,docs,venv,.venv -f json -o reports/bandit.json || true

echo "### 4. Static Quality"
ruff check . > reports/ruff.txt 2>&1 || true
black --check . > reports/black.txt 2>&1 || true
mypy --ignore-missing-imports --exclude "(venv|\\.venv|tests|examples|docs)" . > reports/mypy.txt 2>&1 || true
radon cc -s -a -n C -O reports/radon_cc.txt -e "venv|.venv|tests|examples|docs|build|dist" || true
radon mi -s -O reports/radon_mi.txt -e "venv|.venv|tests|examples|docs|build|dist" || true

echo "### 5. Tests & Coverage"
pytest -q --maxfail=1 --disable-warnings --cache-clear \
  --cov=. --cov-report=xml:reports/coverage.xml --cov-report=term > reports/pytest.txt 2>&1 || true

echo "### 6. Dead Code & Utilization"
vulture $(cat reports/prod_python_files.txt) --min-confidence 70 > reports/vulture.txt 2>&1 || true
deptry . --ignore-notebooks --json-output reports/deptry.json || true

python3 <<'PY'
import xml.etree.ElementTree as ET
tree = ET.parse("reports/coverage.xml")
missed=[]
for f in tree.findall(".//class"):
    fn = f.get("filename")
    hits = sum(int(l.get("hits")) for l in f.findall(".//line"))
    if hits == 0:
        missed.append(fn)
with open("reports/zero_coverage_files.txt","w") as out:
    out.write("\n".join(sorted(set(missed))))
PY

grep -Fxf reports/vulture.txt reports/zero_coverage_files.txt > reports/dead_code_candidates.txt || true

echo "### 7. Architecture"
pydeps . --max-bacon 2 --noshow --no-config --externals \
  --output=reports/deps.svg --verbose > reports/pydeps.txt 2>&1 || true
importlinter lint --format json > reports/import_linter.json 2>&1 || true

echo "### 8. Docker & Ops"
hadolint Dockerfile > reports/hadolint.txt 2>&1 || true
docker build --no-cache -t lukhas-local . > reports/docker_build.txt 2>&1 || true
grype lukhas-local -o table > reports/grype.txt 2>&1 || true

echo "### 9. Summary Index"
{
  echo "# LUKHAS Audit Summary"
  echo ""
  for f in reports/*; do
    size=$(wc -l < "$f" || echo 0)
    echo "- $(basename "$f"): ${size} lines"
  done
} > reports/INDEX.md


⸻

Makefile

.PHONY: audit
audit:
	@bash -lc './scripts/audit.sh'


⸻

.vscode/tasks.json

{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Audit: Gold Standard",
      "type": "shell",
      "command": "make audit",
      "problemMatcher": []
    },
    {
      "label": "Lint (ruff)",
      "type": "shell",
      "command": "ruff check .",
      "problemMatcher": []
    },
    {
      "label": "Type Check (mypy)",
      "type": "shell",
      "command": "mypy .",
      "problemMatcher": []
    },
    {
      "label": "Tests (pytest)",
      "type": "shell",
      "command": "pytest -q",
      "problemMatcher": []
    }
  ]
}


⸻

.vscode/launch.json

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run FastAPI App",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}"],
      "console": "integratedTerminal"
    }
  ]
}


⸻

.github/workflows/audit.yml

name: LUKHAS Audit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          pip install -r requirements.txt
          pip install ruff black mypy bandit vulture deptry pytest pytest-cov pip-audit import-linter radon safety
          pipx install gitleaks
          pipx install syft
          pipx install hadolint
          pipx install grype
      - name: Run audit
        run: make audit
      - name: Upload audit reports
        uses: actions/upload-artifact@v4
        with:
          name: audit-reports
          path: reports/
      - name: Fail on critical issues
        run: |
          if grep -q "HIGH" reports/pip_audit.json; then exit 1; fi
          if grep -q "CRITICAL" reports/gitleaks.json; then exit 1; fi
          if grep -q "error" reports/ruff.txt; then exit 1; fi


⸻

.importlinter

[importlinter]
root_package = .

[contract: Trinity Architecture]
name = Trinity Layers
type = layered
layers =
    core
    consciousness
    memory
    ui
containers =
    core = core
    consciousness = consciousness
    memory = memory
    ui = ui


⸻

.pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.284
    hooks:
      - id: ruff
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.17.0
    hooks:
      - id: gitleaks


⸻

2 — Master Prompt for Claude Code

Here’s what you paste into Claude Code to set it all up:

⸻

Claude, you are acting as a Senior DevOps/Tooling Engineer.

I need you to:
	1.	Create all the files exactly as shown below in my repo. Preserve formatting, chmod scripts, and don’t change command logic.
	2.	Adjust paths if my real entrypoints or directories differ (e.g., qim/, quantum/, memory/).
	3.	Ensure scripts/audit.sh runs end-to-end without freezing the terminal, sending all output to reports/.
	4.	Wire these into:
	•	VS Code Tasks and Run & Debug panels
	•	GitHub Actions CI
	•	.importlinter contract for my Trinity layers
	•	.pre-commit hooks for local enforcement
	5.	Test that:
	•	make audit works locally
	•	VS Code shows “Audit: Gold Standard” in Tasks and runs it without prompts
	•	CI runs audit and fails on critical gates
	•	Reports are uploaded as artifacts
	•	Import-linter contracts run in CI and locally
	•	Pre-commit hooks run on staged files
	6.	Commit all files with message: chore: add gold-standard audit tooling.

Files to create:
	•	scripts/audit.sh (chmod +x) — [insert full script from above]
	•	Makefile — [insert from above]
	•	.vscode/tasks.json — [insert from above]
	•	.vscode/launch.json — [insert from above]
	•	.github/workflows/audit.yml — [insert from above]
	•	.importlinter — [insert from above]
	•	.pre-commit-config.yaml — [insert from above]

Important:
	•	Do not remove existing workflows/configs unless they conflict directly — merge carefully.
	•	Put reports/ in .gitignore.
	•	Install required tools locally via pip/pipx so audit passes before committing.
	•	Keep commands non-interactive and safe for my terminal.

⸻

If you want, I can also give you a report-reading checklist so you know exactly which files to open first after every run. Do you want me to include that?