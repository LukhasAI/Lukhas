
Why that ordering (short summary, T4-skeptical):
	•	The configs/ merge is low-risk and currently blocked by a small, solvable problem (broken symlinks / invalid JSON). Fixing it first removes blocking friction and reduces unknowns that could complicate the MATRIZ run.
	•	Dream consolidation is medium-risk because of potential collisions, but it’s local to consciousness research and worth resolving before changing the global MATRIZ import surface.
	•	MATRIZ is high-impact: once you rename and update 500+ imports you’ll create merges, CI churn, and coordination needs. Do that after dust settles so your PRs are less likely to conflict with other ongoing work.

Below I give you an exact, safe plan to execute Option B now, followed by the MATRIZ plan (Option A) ready to run when you say go. I include command-level steps, precise checks, and recommended commit/PR messages.

⸻

OPTION B — Fix configs/ → config/ (Recommended now)

Goal: Fix invalid JSON / symlink problems, then merge configs/ contents safely into config/.

1) Inspect and identify broken symlinks & invalid JSON

Run from repo root:

# show symlinks in configs/ and whether they are broken
echo "Symlinks (and resolved targets):"
find configs -type l -print -exec ls -l {} \; || true

# Find broken symlinks (robust cross-platform)
echo "Broken symlinks:"
find configs -type l -exec sh -c 'for f; do [ -e "$f" ] || echo "BROKEN: $f -> $(readlink "$f")"; done' _ {} +

# Validate JSON files (requires jq)
echo "JSON validation (will print invalid files):"
for f in configs/*.json; do
  if [ -e "$f" ]; then
    jq -e . "$f" >/dev/null 2>&1 || echo "INVALID JSON: $f"
  fi
done

2) Resolve broken symlinks

For each broken symlink listed:
	•	If the symlink target exists elsewhere in the repo, replace symlink with a copy of the real file (so config/ becomes self-contained), or update symlink to the correct path. Example:

# Example: replace broken symlink with resolved copy
orig="configs/permissions.json"
target="/path/to/real/permissions.json"  # fill in after inspection
rm "$orig"
cp -p "$target" "$orig"
git add "$orig"
git commit -m "fix(configs): replace broken symlink configs/permissions.json with real file"

If the target is missing/unknown, consult the author or check commit history:

git log -- configs/permissions.json

If symlinks are valid and point to expected locations, keep them but document the dependency (a symlink note in docs/).

3) Fix invalid JSON

Use jq to fix or at least report exact parse errors:

# show parse errors
for f in configs/*.json; do
  jq . "$f" >/dev/null 2>&1 || { echo "Parse error in $f"; jq . "$f" 2>&1 || true; }
done

	•	For small errors (trailing commas, missing quotes), edit manually or run a small python -m json.tool check and fix.
	•	After edits:

jq . configs/permissions.json > /tmp/perm_fixed.json && mv /tmp/perm_fixed.json configs/permissions.json
git add configs/permissions.json
git commit -m "fix(configs): correct JSON in configs/permissions.json"

4) Merge with preview, do not overwrite

Create a preview area, compare, and manually resolve collisions:

# preview merge
mkdir -p config/merge_preview
cp -r config/* config/merge_preview/
cp -r configs/* config/merge_preview/
# Now inspect diffs:
git --no-pager diff --no-index -- config config/merge_preview || true

Alternatively, list file name collisions:

# collisions by filename
python3 - <<'PY'
import os,sys
a=set(os.listdir('config')) if os.path.exists('config') else set()
b=set(os.listdir('configs')) if os.path.exists('configs') else set()
print("collisions:", sorted(list(a&b)))
PY

For YAML/JSON files with the same name, do a content diff and merge carefully (manual inspection recommended).

5) Move files with git mv or git add as appropriate

If file does not exist in config/:

git mv configs/legacy_imports.yml config/

If there is a collision and you resolved manually, git add config/file and commit.

Commit message for the merge:

git commit -m "chore(config): merge configs/ into config/ (resolved broken symlinks and fixed invalid JSON)"

6) Run validation script and tests

You already have scripts/consolidation/validate_config_merge.sh. Run:

bash scripts/consolidation/validate_config_merge.sh
# Then full smoke & tests
make smoke
python3 -m pytest tests/ --maxfail=1 -q

7) PR & CI
	•	Create branch chore/merge-configs-2025-10-26
	•	Push and open PR with description of symlink fixes and JSON corrections
	•	Use CI to run the repo-wide tests and the config validator
	•	Merge when CI green and reviewers approve

Estimated time: 20–40 minutes if only the two broken files are affected. Up to 1 hour if there are tricky format issues.

⸻

Dream consolidation (Phase 2 medium-risk — do as part of Option B)

Goal: Consolidate dream/, dreams/, dreamweaver_helpers_bundle/ into labs/consciousness/dream/ while avoiding filename conflicts.

Steps
	1.	Detect filename collisions & duplicates:

python3 - <<'PY'
import os,hashlib
dirs=['dream','dreams','dreamweaver_helpers_bundle','labs/consciousness/dream']
files={}
for d in dirs:
    if not os.path.exists(d): continue
    for root,_,names in os.walk(d):
        for n in names:
            path=os.path.join(root,n)
            files.setdefault(n,[]).append(path)
for bn,paths in files.items():
    if len(paths)>1:
        print("Collision:",bn)
        for p in paths: print("  ",p)
PY

	2.	For identical files (same sha256), keep one canonical copy; for distinct files with same name, rename during move (e.g., symbolic_x_helpers.py → symbolic_x_helpers_oldbundle.py), or move into helpers/ and preserve subdirs.
	3.	Use git mv to move in small batches and run tests between batches.
	4.	Add compatibility shims in top-level dream for import-time redirection if needed:

# dream/__init__.py
from importlib import import_module
from labs.consciousness import dream as _dream
# Re-export public API with deprecation warnings

	5.	Commit with message:

chore(dream): consolidate dream modules into labs/consciousness/dream; preserve compatibility shims

Estimated time: 30–90 minutes depending on collisions.

⸻

OPTION A — MATRIZ Case Standardization (High-risk, run after Option B)

You said everything is ready: AST rewriter, shim, two-step rename. Below are precise commands & checks to execute. Do these on a branch and notify the team before pushing.

Preflight (must do)

# 1. Create branch and backup
git checkout -b chore/standardize-MATRIZ-2025-10-26
git remote update
git pull

# 2. Backup repository (mirror)
cd ..
git clone --mirror /path/to/Lukhas /tmp/Lukhas-mirror-backup-$(date +%s).git
# Also backup working dir tarball
tar -czf /tmp/Lukhas_backup_before_MATRIZ_$(date +%s).tgz /Users/agi_dev/LOCAL-REPOS/Lukhas

1) Dry-run import rewrite

Run the AST rewriter in dry-run and review patch:

python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --verbose > /tmp/matriz_rewrite_dryrun.patch
less /tmp/matriz_rewrite_dryrun.patch
# Review the patch carefully

If the rewriter creates a lot of changes, consider splitting by packages to ease review.

2) Run Import Health Checker

python3 scripts/consolidation/check_import_health.py --verbose
# Expect: zero new errors or a small, manageable list to fix

3) Apply codemod (if dry-run looks good)

python3 scripts/consolidation/rewrite_matriz_imports.py
git add -A
git commit -m "chore(imports): update matriz -> MATRIZ via AST rewriter (dry-run validated)"

4) Add compatibility shim (already exists — confirm)

Ensure matriz/__init__.py exists and re-exports MATRIZ. Commit if missing:

# matriz/__init__.py
import importlib, warnings
warnings.warn("The 'matriz' package is deprecated; use 'MATRIZ' (uppercase). This shim will be removed after 2 releases.", DeprecationWarning)
MATRIZ = importlib.import_module("MATRIZ")
# Optionally: from MATRIZ import *

Commit:

git add matriz/__init__.py
git commit -m "chore(compat): add matriz->MATRIZ compatibility shim with deprecation warning"

5) Two-step rename (filesystem nuance)

Important: Do this on your feature branch, not on main. Also ensure no other developers are writing to MATRIZ simultaneously.

# step A: temp name
git mv MATRIZ MATRIZ_temp
git commit -m "temp: prepare MATRIZ for case standardization (TEMP rename)"

# step B: final uppercase name
git mv MATRIZ_temp MATRIZ
git commit -m "fix(matriz): standardize package name to uppercase MATRIZ"

If your file system treats them as the same inode, the temp step is what makes the change trackable by git.

6) Run full tests & CI locally & on PR

make smoke
python3 -m pytest tests/ -q

# If all good, push branch and open PR
git push origin chore/standardize-MATRIZ-2025-10-26

Open PR and request full CI (all tests, lint, module registry generation). Keep the compatibility shim in place for the planned deprecation period (document deprecation schedule in PR). Leave the shim until all downstream consumers update.

7) Post-merge
	•	Regenerate module registry: python3 scripts/generate_meta_registry.py (or make registry if you have it).
	•	Monitor CI, review test collection errors, and be prepared for rollbacks if major import errors appear.

Rollback plan: If things go sideways, revert the commits or reset the branch. Since these changes are many commits, prefer git revert for each commit or create a rollback branch pointing to the pre-change commit.

Estimated time: 2–4 hours (codemod review, test runs, addressing failures, organizing PR).

⸻

Quick CI snippets & safety gates (copy/paste)

Block large files

# fail if any tracked file > 100MB
python3 - <<'PY'
import os,subprocess
L=[]
for f in subprocess.check_output(['git','ls-files']).decode().splitlines():
  try: s=os.path.getsize(f)
  except: s=0
  if s>100*1024*1024: print("LARGE:",f,s) or L.append(f)
if L: raise SystemExit(1)
print("OK")
PY

Prevent matriz imports (CI check)

# fail CI if 'from matriz.' appears (unless compat shim present)
if grep -R --exclude-dir=.git "from matriz\\." .; then
  echo "Found legacy 'from matriz.' imports" && exit 1
fi

(Use the CI only temporarily — after codemod is merged, remove the rule or update it.)

⸻

Communication & governance
	•	Announce to the team: date/time window when you will run MATRIZ step or do configs merge. That avoids parallel edits that cause merge hell.
	•	Create PR descriptions that explain: rationale, compatibility shim, deprecation schedule, rollback instructions, and a contact person for urgent conflicts.

⸻

Estimated total remaining time (conservative)
	•	configs/ fixes & merge: 30–60 minutes (blocked items dependent).
	•	Dream consolidation: 30–90 minutes (collision risk variable).
	•	MATRIZ case standardization: 2–4 hours (codemod + review + CI).
Total conservative (all remaining): ~3–6 hours.

⸻
 Below I give two ready-to-paste PR packages (one for configs/ → config/, one for dream consolidation). Each package includes:
	•	exact branch + git commands,
	•	preflight checks and repair commands (symlinks + JSON),
	•	safe merge steps with preview, commit messages,
	•	CI/validation steps to run locally & in CI,
	•	an explicit PR description + checklist you can paste into GitHub,
	•	rollback steps and risk notes.

Do configs/ PR first (Option B), then dream consolidation. I keep everything concrete and reversible — think of these as surgical instructions, not a sledgehammer.

⸻

PR A — Merge configs/ → config/ (branch: chore/merge-configs-2025-10-26)

1) Create branch & backup

git checkout -b chore/merge-configs-2025-10-26
# optional safety: create a working copy backup before big moves
tar -czf /tmp/Lukhas_backup_before_merge_configs_$(date +%s).tgz .

2) Preflight: identify symlinks, broken links, and invalid JSON/YAML

Run these from repo root.

List symlinks & resolved targets

echo "Symlinks in configs/:"
find configs -type l -print -exec ls -l {} \; || true

Detect broken symlinks

echo "Broken symlinks:"
find configs -type l -exec sh -c 'for f; do [ -e "$f" ] || echo "BROKEN: $f -> $(readlink "$f")"; done' _ {} +

Find invalid JSON

# needs jq
for f in configs/*.json; do
  [ -f "$f" ] || continue
  if ! jq -e . "$f" >/dev/null 2>&1; then
    echo "INVALID JSON: $f"
    jq . "$f" 2>&1 || true
  fi
done

Find invalid YAML (if you have python -c 'import yaml'):

python3 - <<'PY'
import glob,sys,yaml
for f in glob.glob('configs/**/*.y*ml', recursive=True)+glob.glob('configs/*.y*ml'):
    try:
        yaml.safe_load(open(f))
    except Exception as e:
        print("INVALID YAML:", f, e)
PY

3) Repair broken symlinks & invalid JSON (guided, not automatic)

For each broken symlink configs/xxx you must either:
	•	Replace the symlink with a real file (if you know the target location), or
	•	Restore the missing file from history, or
	•	Update symlink to correct target.

Example: replace symlink with actual file

# Suppose configs/permissions.json is a symlink that points to /some/path/permissions.json
rm configs/permissions.json
cp -p /some/path/permissions.json configs/permissions.json
git add configs/permissions.json
git commit -m "fix(configs): replace broken symlink configs/permissions.json with real file"

If you don’t know the correct target:

git log -- configs/permissions.json
# inspect previous commit
git show <commit_hash>:configs/permissions.json > /tmp/restore_permissions.json
# then review and restore
mv /tmp/restore_permissions.json configs/permissions.json
git add configs/permissions.json
git commit -m "fix(configs): restore configs/permissions.json from history"

Fix invalid JSON:
Manual editing is safest. You can get quick hints with:

jq . configs/suspect.json > /tmp/tmp.json 2>&1 || true
# edit the file
python3 -m json.tool configs/suspect.json > /dev/null 2>&1 || echo "invalid"

After fixing:

jq . configs/suspect.json > /tmp/ok.json && mv /tmp/ok.json configs/suspect.json
git add configs/suspect.json
git commit -m "fix(configs): correct JSON format in configs/suspect.json"

T4 note: Don’t blindly copy files into config/ yet; keep a merge_preview and validate.

4) Preview the merge (safe, non-destructive)

mkdir -p config/merge_preview
cp -r config/* config/merge_preview/ 2>/dev/null || true
cp -r configs/* config/merge_preview/
# Show collisions
python3 - <<'PY'
import os
a=set(os.listdir('config')) if os.path.exists('config') else set()
b=set(os.listdir('configs')) if os.path.exists('configs') else set()
print("collisions:", sorted(list(a&b)))
PY
# Use git diff --no-index for content-level diffs:
git --no-pager diff --no-index config config/merge_preview || true

Resolve collisions by manual inspection. For same-named YAML/JSON, do a content merge (manual) or move configs/foo.yml into config/merge_preview/foo.from_configs.yml while resolving.

5) Merge files (safe rules)
	•	If configs/<file> does not exist in config/:

git mv configs/<file> config/


	•	If collision exists, manually merge into config/<file> then git add config/<file] and delete configs/<file]:

# example
# open both and merge, then:
git rm configs/foo.yml
git add config/foo.yml
git commit -m "chore(config): merge configs/foo.yml into config/foo.yml (resolved conflicts)"



Work in small batches (5–10 files per commit) and run tests between commits.

Good commit message (batch):

chore(config): merge configs/legacy_imports.yml and configs/quotas.yaml into config/

- Fixed broken symlinks: configs/permissions.json
- Corrected invalid JSON: configs/core/main.json
- Previewed merge and resolved collisions for 'star_rules.json'

6) Run validation / tests

You already have scripts/consolidation/validate_config_merge.sh. Execute it:

bash scripts/consolidation/validate_config_merge.sh

Then run smoke & unit tests:

make smoke
python3 -m pytest tests/ --maxfail=1 -q

Also run linter/isort (recommended):

# if you use ruff/isort
ruff check .
isort --check-only .

7) CI snippets (add as checks to your PR)

Add a CI job (GitHub Actions) to run a small validation YAML/JSON check and fail if invalid or broken symlink found. Example job script (bash):

# ci/check-configs.sh
set -e
# Check JSON
for f in $(git ls-files configs | grep -E "\.json$" || true); do
  jq -e . "$f" >/dev/null 2>&1 || { echo "INVALID JSON: $f"; exit 1; }
done
# Broken symlinks
for f in $(git ls-files configs | xargs -I{} sh -c 'if [ -L "{}" ]; then echo "{}"; fi' || true); do
  if [ -L "$f" ] && [ ! -e "$f" ]; then echo "BROKEN SYMLINK: $f" && exit 1; fi
done
echo "CONFIGS OK"

8) PR Description (paste this)

Title: chore(config): merge configs/ into config/ (resolve symlinks & fix JSON)

Description:

This PR safely merges contents of the legacy `configs/` directory into canonical `config/`.

Why:
- Standardize configuration storage in `config/` (single source of truth).
- Remove ambiguous duplicate directories and reduce maintenance burden.

What was done:
- Repaired broken symlinks in `configs/` (replaced with real files or restored from history).
- Fixed invalid JSON files that blocked merge (listed below).
- Merged non-conflicting files with `git mv`.
- For colliding filenames, manual content merges were performed and committed.
- Added CI check to validate configs (json/yaml and broken symlink detection).

Files fixed:
- `configs/permissions.json` — replaced broken symlink with file
- `configs/core/main.json` — JSON syntax corrected
- (Add additional file list if applicable)

Validation performed locally:
- `bash scripts/consolidation/validate_config_merge.sh` — PASS
- `make smoke` — PASS
- `python3 -m pytest tests/` — PASS

Notes:
- This PR is intentionally small/batched to reduce merge conflicts.
- No runtime code changes were made — only config file movement/fixes.

PR Checklist (to paste in the PR body):

- [ ] Run `bash scripts/consolidation/validate_config_merge.sh` (or CI check) — pass
- [ ] Smoke tests pass: `make smoke` — pass
- [ ] Unit tests pass: `pytest tests/` — pass
- [ ] Linting / formatting checked: `ruff`, `isort`
- [ ] No tracked files > 100MB added
- [ ] Confirmed no unresolved collisions remain
- [ ] Confirmed there are no relative path breakages in runtime config loaders

9) Merge & post-merge
	•	Merge once CI is green and reviewers approve.
	•	Run python3 scripts/generate_meta_registry.py if needed.
	•	Announce to the team: “configs/ consolidated into config/ — please update local scripts if they reference configs/”.

10) Rollback (if needed)

If you need to revert:

# If single merge commit or small set:
git revert <commit-hash>  # revert individual commits
# If many commits and you want to return to prior state:
git checkout -b rollback/merge-configs-2025-10-26
git reset --hard <commit-before-merge>
git push origin rollback/merge-configs-2025-10-26


⸻

PR B — Consolidate dream/, dreams/, dreamweaver_helpers_bundle/ into labs/consciousness/dream/

Branch: chore/consolidate-dreams-2025-10-26

This is medium-risk because labs/consciousness/dream/ already has 65 files. We’ll move in small batches and add a top-level shim to preserve imports.

1) Branch & preflight

git checkout -b chore/consolidate-dreams-2025-10-26
tar -czf /tmp/Lukhas_backup_before_dream_merge_$(date +%s).tgz .

2) Detect collisions & duplicates

Run this to list names and collisions:

python3 - <<'PY'
import os,hashlib
dirs=['dream','dreams','dreamweaver_helpers_bundle','labs/consciousness/dream']
files={}
for d in dirs:
    if not os.path.exists(d): continue
    for root,_,names in os.walk(d):
        for n in names:
            path=os.path.join(root,n)
            files.setdefault(n,[]).append(path)
for name,paths in sorted(files.items()):
    if len(paths)>1:
        print("Collision:", name)
        for p in paths: 
            print("  ",p)
PY

Detect identical files (sha256):

python3 - <<'PY'
import os,hashlib
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()
mapping={}
dirs=['dream','dreams','dreamweaver_helpers_bundle','labs/consciousness/dream']
for d in dirs:
    if not os.path.exists(d): continue
    for root,_,names in os.walk(d):
        for n in names:
            p=os.path.join(root,n)
            s=sha(p)
            mapping.setdefault(s,[]).append(p)
for s,paths in mapping.items():
    if len(paths)>1:
        print("Duplicate files (same sha):")
        for p in paths: print("  ",p)
PY

3) Resolve collisions

Rules:
	•	If identical (same hash): keep one canonical file under labs/consciousness/dream/ and remove duplicates.
	•	If different files with same name:
	•	Decide canonical file and rename others (<name>_from_bundle.py), or
	•	Move conflicting files into labs/consciousness/dream/helpers/<bundle_name>/ to preserve origin, then refactor later.

Work in small batches (per subdir).

4) Move files (safe small batches)

Example: move dreamweaver_helpers_bundle/helpers/* into labs/consciousness/dream/helpers/:

mkdir -p labs/consciousness/dream/helpers
git mv dreamweaver_helpers_bundle/helpers/* labs/consciousness/dream/helpers/ || true
git commit -m "chore(dream): move dreamweaver_helpers_bundle/helpers -> labs/consciousness/dream/helpers"
# run tests
make smoke || true

For high-risk file names, move with renaming:

git mv dream/some_module.py labs/consciousness/dream/some_module_from_dream_bundle.py
git commit -m "chore(dream): move dream/some_module.py -> labs/consciousness/dream/some_module_from_dream_bundle.py (avoid name collision)"

5) Add compatibility shim

Add dream/__init__.py that re-exports the new module (with deprecation warning):

# dream/__init__.py
import importlib, warnings
warnings.warn("Top-level `dream` package is deprecated. Use `labs.consciousness.dream`.", DeprecationWarning)
_mod = importlib.import_module("labs.consciousness.dream")
# optionally export common symbols:
# from labs.consciousness.dream import *

Commit:

git add dream/__init__.py
git commit -m "chore(compat): add dream -> labs.consciousness.dream shim (deprecation)"

6) Tests & lint

Run smoke & tests between each batch:

make smoke
python3 -m pytest tests/ -q
ruff check labs/consciousness/dream || true

7) PR Description (paste)

Title: chore(dream): consolidate dream/, dreams/, dreamweaver_helpers_bundle/ into labs/consciousness/dream/

Description:

This PR consolidates scattered dream-related code into the canonical `labs/consciousness/dream/` package.

Why:
- Reduce module scattering and make dream research modules discoverable.
- Prepare for future MATRIZ/Consciousness refactors.

Actions:
- Moved helpers into labs/consciousness/dream/helpers/
- Moved dream outputs into labs/consciousness/dream/results/
- Resolved filename collisions by renaming conflicting files (append `_from_*`)
- Added top-level `dream/__init__.py` compatibility shim to preserve legacy imports and warn developers.
- All moves done in small batches with tests run between commits.

Validation:
- Collision and duplicate detection ran prior to move
- `make smoke` and `pytest tests/` run after each batch — green locally
- Linting (ruff) run for moved files

Notes:
- Compatibility shim will remain for 1–2 releases. Developers should update imports to `labs.consciousness.dream.*`.

PR Checklist:

- [ ] Collision report included (list of renamed files)
- [ ] `make smoke` — pass
- [ ] `pytest tests/` — pass
- [ ] Linting checks (`ruff`) pass for moved files
- [ ] Compatibility shim in place
- [ ] No tracked large files added
- [ ] Manual review of renamed modules for API changes

8) Rollback

Use git revert for commits or git reset --hard <pre-PR-commit> in a rollback branch.

⸻

Final governance & tips (T4 lens)
	1.	Do Option B now: run the config merge first (it’s the blocker), then dream consolidation. Both should be made as small, reviewable PRs. Avoid a single massive PR that touches hundreds of files — that increases risk of conflicts.
	2.	Keep compatibility shims (for dream and for matriz later) and a clear deprecation schedule in the PR (e.g., “shim will be removed after 2 releases”).
	3.	Run codemod / AST tools for import changes (we’ll do MATRIZ later) — they are safer than bulk sed.
	4.	CI gates: add JSON/YAML validation and a large-file guard. Make these part of the PR so we catch regressions early.
	5.	Notify team before the MATRIZ run — that’s the big step; you’ll want people to avoid editing MATRIZ while you do the two-step rename.

⸻
