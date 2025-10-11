
TITLE: LUKHAS — 0.01% Discipline Pack (MATRIZ/Constellation Readiness)

CONTEXT
- Repo: LukhasAI/Lukhas (default branch: main; submodules present; DO NOT remove submodules)
- Objective: Land build-time guardrails + visibility to safely finish artifacts → then move/flatten modules.
- Constraints: Minimal deps; fast CI; small PRs; no behavior changes to runtime code.
- Canon: MATRIZ pipeline + Constellation stars; star canon must be authoritative across tools.

DELIVERABLES (CREATE/UPDATE THESE FILES EXACTLY)
A) Docs + Validators
  1) docs/check_links.py — internal link + anchor checker for docs/ and manifests/ (exit 1 on internal fails)
  2) scripts/validate_contract_refs.py — validate that manifest events reference contracts/<id>.json (id format `<topic>@v<major>`)
  3) scripts/validate_context_front_matter.py — validate each `lukhas_context.md` YAML front-matter vs sibling manifest:
     - required keys: star, tier, matriz[], owner; warn on missing colony
     - canonicalize star via star canon (py pkg if installed else scripts/star_canon.json)
     - hard fail: tier mismatch for T1/T2; missing MATRIZ nodes; T1/T2 without owner
  4) docs/check_contracts_refs.md — troubleshooting guide for contract/link failures (short doc)

B) Star Canon (single source of truth)
  5) packages/star_canon_py/pyproject.toml + packages/star_canon_py/star_canon/__init__.py + star_canon.json
     - Expose `canon()` and `normalize(name)`; no heavy deps.
  6) (Optional) packages/star-canon-js/{package.json,index.js} exporting canon + normalize for future web docs.

C) Contracts Registry
  7) contracts/ (folder) with initial schemas:
     - memory.write@v1.json
     - guardian.policy.violation@v1.json
     - identity.oauth.callback@v1.json
  8) Ensure manifests’ `observability.events.{publishes,subscribes}` only use known IDs.

D) Golden Manifests + Tests
  9) tests/manifests/golden/{anchor_identity.json, flow_consciousness.json, watch_guardian.json}
  10) tests/test_golden_manifests.py — validate goldens against schemas/matriz_module_compliance.schema.json (jsonschema)

E) Guardian Belt (policy)
  11) scripts/policy_guard.py — T1_critical code must not contain eval/exec/subprocess.* unless manifest security.policies includes "allow-dangerous-exec"

F) Smoke Shards (<120s)
  12) pytest.ini — add marker `matriz_smoke`
  13) tests/smoke/test_matriz_smoke.py — import-time cheap path for T1/T2; read optional `latency_target_p95` from manifest, fail if >2x target; cap modules to keep runtime brisk

G) Owners + Freeze + PR Template
  14) OWNERS.toml — glob mapping of FQNs → owners (e.g., "lukhas.consciousness.*"="consciousness")
  15) release/FREEZE.md — Go/No-Go checkbox list (CI green, perf/obs/security, rollback, linkcheck, contracts)
  16) .github/pull_request_template.md — discipline checklist (manifests/context updated, contracts valid, linkcheck, smoke ok, T1/T2 owner + perf target)

H) Stats + Dashboards
  17) scripts/report_manifest_stats.py → docs/audits/manifest_stats.{json,md}
  18) (Ensure) scripts/gen_constellation_top.py + scripts/top_config.json + scripts/star_canon.json (if py pkg absent) generate docs/CONSTELLATION_TOP.md + docs/stars/*.md

I) CI & Pre-commit
  19) .github/workflows/* — add:
      - concurrency block (cancel-in-progress)
      - steps: link checker; contract refs validator; context front-matter validator; guardian belt; (optional) stats artifact upload
  20) Upload artifacts: docs/audits/linkcheck.txt, docs/audits/context_lint.txt, docs/audits/manifest_report.json (if validator writes it), docs/audits/manifest_stats.*
  21) .pre-commit-config.yaml — ensure hooks:
      - ruff (fix + format), detect-secrets with .secrets.baseline, commitizen (commit-msg), local hooks:
        * scripts/validate_manifests.py (existing) with schema path
        * scripts/validate_context_front_matter.py
        * forbid debug prints (ripgrep)
  22) Makefile targets:
      - top:    python scripts/gen_constellation_top.py
      - stats:  python scripts/report_manifest_stats.py --manifests manifests --out docs/audits
      - context-validate: python scripts/validate_context_front_matter.py

IMPLEMENTATION NOTES
- Use Python 3.11 on CI. Keep new scripts stdlib-only where possible (jsonschema is acceptable for tests).
- Prefer star canon PY package if importable; otherwise fallback to scripts/star_canon.json.
- For OWNERS stamping: update the manifest generator (if present) to apply OWNER glob rules; CI must fail if any T1/T2 ends with owner "unassigned".
- Do not refactor runtime modules in this PR set; guardrails only.
- Preserve submodules; don’t move directories yet.

ACCEPTANCE CRITERIA (CI MUST PASS)
1) Link checker: `python docs/check_links.py --root .` exits 0; artifact `linkcheck.txt` uploaded.
2) Contract refs validator: exits 0 when manifests reference only known contracts; unknown → CI fails.
3) Context validator: exits 0; for a deliberately broken branch, fails on T1/T2 tier mismatch / missing owner / missing MATRIZ nodes.
4) Guardian belt: exits 0; detecting eval/exec/subprocess.* in any T1 without explicit policy must fail.
5) Golden manifests validate against the active schema via pytest.
6) Smoke shard: `pytest -q -m matriz_smoke` runs <120s on CI; logs which modules were checked; respects `latency_target_p95` if present.
7) Owners: T1/T2 must have non-"unassigned" owner (CI guard).
8) Concurrency enabled; superseded runs canceled.
9) Artifacts uploaded for linkcheck, context lint, manifest report (if present), and stats.
10) Make targets `top`, `stats`, `context-validate` work locally and on CI runners.

COMMANDS (LOCAL DEV)
- Bootstrap:
  pip install -r requirements.txt || true
  pip install jsonschema pre-commit detect-secrets
  detect-secrets scan > .secrets.baseline
  pre-commit install && pre-commit install --hook-type commit-msg
- Validate everything:
  make context-validate
  python docs/check_links.py --root .
  python scripts/validate_contract_refs.py
  pytest -q -m matriz_smoke
  make top
  make stats

FILE SKELETON (CREATE IF MISSING)
- docs/check_links.py           (internal links + anchors; write docs/audits/linkcheck.txt)
- scripts/validate_contract_refs.py
- scripts/validate_context_front_matter.py
- docs/check_contracts_refs.md
- contracts/{memory.write@v1.json, guardian.policy.violation@v1.json, identity.oauth.callback@v1.json}
- tests/manifests/golden/{anchor_identity.json, flow_consciousness.json, watch_guardian.json}
- tests/test_golden_manifests.py
- scripts/policy_guard.py
- pytest.ini                    (add matriz_smoke marker)
- tests/smoke/test_matriz_smoke.py
- packages/star_canon_py/pyproject.toml
- packages/star_canon_py/star_canon/{__init__.py, star_canon.json}
- packages/star-canon-js/{package.json, index.js}   (optional)
- OWNERS.toml
- release/FREEZE.md
- .github/pull_request_template.md
- .github/workflows/*           (add concurrency + new steps + artifacts)
- scripts/report_manifest_stats.py
- Makefile                      (targets: top, stats, context-validate)
- .pre-commit-config.yaml       (ensure hooks: ruff, ruff-format, detect-secrets, commitizen, local validators)

QUALITY DIALS (T4 STYLE)
- Keep scripts dependency-light and fast.
- Emit clear, actionable errors with short file:line pointers.
- Prefer warnings for non-blocking drift; hard-fail only on correctness & safety (owners, T1/T2 tier/owner, contracts, guardian belt).
- Add small docstrings to every new script; no magic numbers.

HANDOFF
- Open PR(s) with the label `discipline-pack`.
- In PR body, paste latest outputs from:
  - docs/audits/linkcheck.txt
  - docs/audits/context_lint.txt
  - docs/audits/manifest_stats.md
- Request reviewers: platform (schema/CI), consciousness (Flow), guardian (Watch).
```
