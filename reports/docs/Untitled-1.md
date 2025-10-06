---
module: reports
title: Untitled 1
---

 Neutral Baseline Deep Search (separate Pro chat)

ChatGPT Pro (paste as first message)

Baseline Deep Search (Neutral).
ANCHOR TAG: {{same tag}}
Do NOT analyze HEAD. Prior baseline tag (if useful): audit-freeze-20250910T143306Z.

RULES
- Every conclusion must include a code citation:
  File: <path>:<start>-<end>

<≤20 lines excerpt>

- Deterministic: TZ=UTC, PYTHONHASHSEED=0.

SCOPE
- Include: lukhas/, MATRIZ/, ops/, AUDIT/
- Ignore: .git/, .venv/, node_modules/, archive/, quarantine/**
- File types: .py, .json, .yaml, .yml, OpenAPI

TASKS
1) Syntax & imports: Ruff E9/F63/F7/F82 (2–3 citations), cross-lane imports with citations
2) Dependency structure: top-10 connected modules; show any cycles (citations)
3) Test posture: pytest markers (smoke/matriz/golden), counts + samples; coverage if artifacts exist
4) API: verify /healthz and one MATRIZ trace handler; cite one OpenAPI-implemented route
5) Security & SBOM: confirm CycloneDX; surface secret patterns or gitleaks config

OUTPUT
- Clinical Summary (≤200 words)
- Evidence Ledger (citations)
- Scoreboard (R/Y/G): {Syntax, Imports, Lanes, Tests, API, Security}
- First 48h Fix Plan (6–8 bullets)
- Appendix: skipped dirs & why

ARTIFACTS
    •    Save to reports/audit/{{TAG}}/ :
    •    neutral.md
    •    neutral_findings.csv
    •    neutral_scoreboard.json
    •    neutral_contradictions.json
    •    neutral_evidence.jsonl
    •    neutral_logs/gptpro_run.log
    •    At end, print only: SAVED reports/audit/{{TAG}}/neutral.md

⸻

Step 4 — Post-processing (auto-merge artifacts)

python3 tools/audit/mk_delta_appendix.py --since-tag "$tag" --out reports/audit/delta_$tag.md || true

# If you already have the merge script:
python3 tools/audit/merge_audits.py \
  --strategic reports/audit/strategic_$tag.md \
  --neutral   reports/audit/neutral_$tag.md \
  --out-dir   reports/audit/merged \
  --issues    --labels "matriz-traces,lane-integrity,security-sbom,hygiene"

# Provenance stamp and symlinks
ln -sf reports/audit/$tag/strategic.md reports/audit/latest_strategic.md
ln -sf reports/audit/$tag/neutral.md   reports/audit/latest_neutral.md
printf '{"tag":"%s","tz":"UTC","PYTHONHASHSEED":"0","created_utc":"%s"}\n' "$tag" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > reports/audit/$tag/_stamp.json

# SBOM status
python3 - <<'PY'
import hashlib, json, sys, os
p="reports/sbom/cyclonedx.json"
try:
    h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    print(json.dumps({"sbom":"present","sha256":h}))
except FileNotFoundError:
    print(json.dumps({"sbom":"missing"}))
PY | tee reports/audit/$tag/sbom_status.json

⸻

Step 5 — Go/No-Go gates for MATRIZ implementation

Go when all are true:
	•	lint-imports = 0 broken contracts
	•	/traces/latest green via golden fallback
	•	Tier-1 MATRIZ smoke green (or xfail explicitly documented)
	•	Doctor strict shows no ❌ and only acceptable ⚠️ (documented)
	•	No new lane violations introduced since the tag

If any are red, add a 24-hour “Fix Now” mini-batch before starting lane promotions.

⸻

Optional — Codex CLI companion prompt

Use this in your Codex CLI to prep & run the audits locally (idempotent):

system: You are a senior infra engineer enforcing T4 standards: determinism, minimal blast radius, reproducible artifacts.

user:
Task: Prepare repo for dual deep searches at tag {{TAG}} and emit artifacts.

Actions:
1) Ensure pyproject editable install, pytest.ini with pythonpath=., tests not packages.
2) Run:
   - make doctor-json
   - PYTHONPATH=. .venv/bin/lint-imports || true
   - PYTHONPATH=. python3 -m pytest -q -m tier1 tests_new/matriz || true
3) Generate SBOM if missing: make sbom
4) Emit bundle:
   - reports/audit/doctor_summary.json
   - reports/sbom/cyclonedx.json
   - reports/matriz/traces/*.json (ensure ≥1 golden)
5) Print next commands for Claude/Pro (the two prompts above) with TAG substituted.

Constraints:
- Do not modify code. Only create config/artifacts.
- If any step fails, continue and log a short reason.


⸻

Optional — Add Makefile helper

mk/audit.mk (add target)

```makefile
.PHONY: audit-collect
audit-collect:
	@[ -n "$$tag" ] || (echo "Set tag=<TAG>"; exit 2)
	@ls reports/audit/$$tag/strategic.md reports/audit/$$tag/neutral.md >/dev/null
	@python3 tools/audit/mk_delta_appendix.py --since-tag audit-freeze-20250910T143306Z --out reports/audit/$$tag/appendix_delta.md || true
	@ln -sf reports/audit/$$tag/strategic.md reports/audit/latest_strategic.md
	@ln -sf reports/audit/$$tag/neutral.md   reports/audit/latest_neutral.md
	@echo "✅ audit-collect OK for $$tag"
```

⸻

Why this is the right move
	•	Anchors reality with a fresh tag (no HEAD drift).
	•	Dual lenses: strategic (integration tissue) + neutral (clinical hygiene).
	•	Outputs are machine-readable and tie back to code with citations.
	•	Clear Go/No-Go gates to start lane promotions and full MATRIZ wiring without surprises.

When you’ve got the two audit results, drop the exec summaries and Top-5 fixes; I’ll turn them into the lane-by-lane implementation plan and PR batch queue.