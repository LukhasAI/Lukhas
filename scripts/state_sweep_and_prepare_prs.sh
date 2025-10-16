#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
AUD="docs/audits/live/${STAMP}"
mkdir -p "$AUD"

echo "==> Sweep stamp: $STAMP"
echo "==> Output dir: $AUD"

# 1) Ruff snapshot (concise + stats)
python3 -m ruff check lukhas core matriz --no-cache --output-format=concise 2>&1 | tee "${AUD}/ruff.out" || true
python3 -m ruff check lukhas core matriz --statistics --no-cache 2>&1 | tee "${AUD}/ruff_stats.txt" || true
wc -l "${AUD}/ruff.out" 2>/dev/null | awk '{print $1}' > "${AUD}/RUFF_TOTAL.txt" || echo "0" > "${AUD}/RUFF_TOTAL.txt"

# 2) Candidate→labs sanity (exclude manifests/fixtures)
rg -nI --hidden --glob '!*manifests/*' --glob '!tests/**/fixtures/**' 'candidate/' 2>&1 | tee "${AUD}/candidate_refs.txt" || true

# 3) OpenAPI artifact + validate (if generator is present)
if [ -f scripts/generate_openapi.py ]; then
  mkdir -p docs/openapi
  python3 scripts/generate_openapi.py 2>&1 || true
  if python3 - <<'PY' 2>&1
import sys, json
try:
    from openapi_spec_validator import validate_spec
    spec=json.load(open('docs/openapi/lukhas-openapi.json'))
    validate_spec(spec)
    print("OpenAPI: validation OK")
except Exception as e:
    print(f"OpenAPI: validation FAILED - {e}")
    sys.exit(1)
PY
  then
    echo "OpenAPI validated" | tee "${AUD}/openapi_status.txt"
  else
    echo "OpenAPI validation FAILED" | tee "${AUD}/openapi_status.txt"
  fi
else
  echo "OpenAPI generator not found" | tee "${AUD}/openapi_status.txt"
fi

# 4) Compat alias hits
if [ -f scripts/report_compat_hits.py ]; then
  python3 scripts/report_compat_hits.py --out "${AUD}/compat_alias_hits.json" 2>&1 || true
fi

# 5) Summary
cat > "${AUD}/STATE_SWEEP_SUMMARY.md" <<MD
# T4 State Sweep — ${STAMP}

**Ruff total**: \`$(cat "${AUD}/RUFF_TOTAL.txt")\`
See: \`${AUD}/ruff_stats.txt\`

**Candidate→labs refs (non-manifest/fixtures)**: $(wc -l < "${AUD}/candidate_refs.txt" 2>/dev/null || echo 0)
See: \`${AUD}/candidate_refs.txt\`

**OpenAPI**: $(cat "${AUD}/openapi_status.txt" 2>/dev/null || echo "not generated")

**Compat alias hits**: $(test -f "${AUD}/compat_alias_hits.json" && jq '. | length' "${AUD}/compat_alias_hits.json" 2>/dev/null || echo "n/a")

MD

# 6) PR bodies scaffolding (docs-only PRs B & C)
mkdir -p docs/gonzo/pr_bodies
cat > docs/gonzo/pr_bodies/PR_B_F821_PLAN.md <<MD
# docs(ruff): F821 guided import suggestions (no code change)

**Problem**: Undefined names (F821) degrade reliability and block strict gates.
**Solution**: Document a *guided* owner-by-owner plan (≤20-file slices), no runtime changes.
**Scope**: Plan-only document generated during the ${STAMP} sweep.

Artifacts:
- \`${AUD}/ruff_stats.txt\`
- \`${AUD}/STATE_SWEEP_SUMMARY.md\`

**Safety**: Docs only. No code changes.
MD

cat > docs/gonzo/pr_bodies/PR_C_STAR_PROMOTIONS.md <<MD
# docs(matriz): proposed star promotions (supporting → production)

**Summary**: Proposes promotions based on the ${STAMP} State Sweep.
**Scope**: CSV + MD report for discussion. No behavior changes.

Artifacts:
- \`${AUD}/STATE_SWEEP_SUMMARY.md\`

**Safety**: Docs only.
MD

echo "==> Sweep complete. See ${AUD}/STATE_SWEEP_SUMMARY.md"
