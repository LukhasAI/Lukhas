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