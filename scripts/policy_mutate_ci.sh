#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT"
export LUKHAS_STATE="${LUKHAS_STATE:-$HOME/.lukhas/state}"
mkdir -p "$LUKHAS_STATE"

JSON_OUT="$LUKHAS_STATE/safety_ci.json"
export SAFETY_CI_JSON="$JSON_OUT"

# 1) run all safety checks into JSON (non-zero exit triggers CI fail)
python3 -m qi.safety.ci_runner \
  --policy-root "$ROOT/qi/safety/policy_packs" \
  --jurisdiction "global" \
  --mutations 40 \
  --max-mutation-passes 0 \
  --out-json "$JSON_OUT" || true

# 2) always render a markdown report (even if previous step failed)
python3 -m qi.safety.ci_report || true

# If you're running locally, show where files landed:
echo "Safety CI artifacts:"
echo " - JSON: $JSON_OUT"
echo " - MD:   ${JSON_OUT%.json}.md"

# rethrow failure if ci_runner failed
python3 - <<'PY'
import json, os, sys
p = os.environ["SAFETY_CI_JSON"]
rep = json.load(open(p))
# determine failure: any step non-zero OR mutation_violation present
failed = any(s.get("rc",0)!=0 for s in rep.get("steps",[])) or ("mutation_violation" in rep)
sys.exit(1 if failed else 0)
PY