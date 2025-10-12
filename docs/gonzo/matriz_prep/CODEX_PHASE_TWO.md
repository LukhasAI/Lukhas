Fantastic update. With PRs **#375** and **#376** merged and the Phase-2 docs/tools in place, you can green-light Codex. Below is a tight **Go/No-Go gate**, the **exact run order** with guardrails, and a **copy-paste status template** Codex can post after each batch. I’ve also flagged one important nuance about the new **AST fallback** in the codemod.

---

# Go/No-Go (quick gate before Stage A)

**Go if all true:**

* `main` up to date; branch protection enforced (PRs only).
* `pytest --collect-only -q` returns **0 hard errors** on current `main`.
* `docs/gonzo/matriz_prep/PHASE_2_CODEX_BRIEF.md` + `CODEX_START_PHASE_2.md` present and current.
* **Compat alias layer** installed via `tests/conftest.py` (so collection won’t break during rewrites).
* `scripts/update_manifest_paths.py` available (JSON-safe manifest update).

**Note on codemod fallback:** PR #376 added a **built-in `ast` fallback** if LibCST isn’t present. That fallback can **reformat** code (lose comment placement, touch quoting/spacing). For T4 quality, prefer **LibCST** (format-preserving). If the runner is “restricted,” consider:

```bash
python -c "import libcst; print('LibCST OK')" || pip install libcst
```

If you must use the AST fallback, tighten review on the diff size and run `ruff format` + `ruff check`.

---

# Phase 2 execution (what Codex should do now)

## Stage A — Preview (dry run)

```bash
git checkout -b codex/phase-2-import-codemod
make codemod-dry
wc -l docs/audits/codemod_preview.csv && head -20 docs/audits/codemod_preview.csv
pytest --collect-only -q
python3 scripts/check_alias_hits.py || true
```

**Exit criteria:** Preview looks sane (no bizarre mappings), collection still ok.

## Stage B — Batches (commit after each)

**Batch 1 — Tests first**

```bash
python3 scripts/codemod_imports.py --apply --roots tests
pytest -q -x --maxfail=5
pytest --collect-only -q
python3 scripts/check_alias_hits.py || true
git add tests && git commit -m "refactor(imports): migrate tests to canonical imports"
```

**Batch 2 — Production lane (`lukhas/`)**

```bash
python3 scripts/codemod_imports.py --apply --roots lukhas
make lane-guard
make check-legacy-imports
pytest tests/smoke/ -q
python3 scripts/check_alias_hits.py || true
git add lukhas && git commit -m "refactor(imports): migrate lukhas/ to canonical imports"
```

**Batch 3 — Dev lane (`candidate/ → labs/`) + manifests**

```bash
git mv candidate labs
python3 scripts/codemod_imports.py --apply --roots labs

# JSON-safe manifest path updates (+ telemetry & links)
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/
python3 scripts/gen_rules_coverage.py
python3 docs/check_links.py --root .
rg -n "candidate/" manifests || true

make lane-guard
make check-legacy-imports
pytest tests/smoke/ -q
python3 scripts/check_alias_hits.py || true

git add -A && git commit -m "refactor(lanes): candidate→labs, imports and manifest paths updated"
```

**Batch 4 — Remaining (`core/`, `packages/`, `tools/`)**

```bash
python3 scripts/codemod_imports.py --apply --roots core packages tools
make check-legacy-imports
pytest -q -x --maxfail=10
python3 scripts/check_alias_hits.py || true
git add -A && git commit -m "refactor(imports): canonicalize core/, packages/, tools/"
```

## Stage C — Verify & PR

```bash
pytest tests/ --maxfail=20 -q
make lane-guard
make check-legacy-imports
python3 scripts/check_alias_hits.py || true
git push origin codex/phase-2-import-codemod

gh pr create -f -t "refactor(imports): Phase 2 canonical import migration" \
  -b "Phase 2 completed in 4 batches… (include alias-hits total, stats, smoke results)"
```

---

# What to watch during execution (telemetry & gates)

* **Compat alias hits**: Expect steady decline after each batch (report is `docs/audits/compat_alias_hits.json`). Plan to enforce a cap in a follow-up PR (`LUKHAS_COMPAT_MAX_HITS: "0"`).
* **Legacy import checker**: `make check-legacy-imports` should pass outside allowlist (`lukhas/compat`, `tests/conftest.py`).
* **Manifests**: `rg -n "candidate/" manifests` should return **nothing** after Batch 3.
* **Link checker**: `docs/check_links.py --root .` should be clean; CI artifact uploaded.
* **Lane guard**: No cross-lane leaks after each batch.
* **Smoke tests**: Keep them passing at each checkpoint.

---

# Parallel quick wins (run now while Codex is in Stage A)

**Claude Code (architectural / high-leverage)**

1. **OpenAI façade** (`/v1/responses`, `/v1/models`, `/v1/embeddings`), with minimal OpenAPI spec (docs/openapi).
   *Acceptance:* smoke test `tests/smoke/test_openai_facade.py` passes; spec builds in CI.

2. **OpenAI tools exporter** — generate `build/openai_tools.json` from manifests’ capabilities.
   *Acceptance:* JSONSchema validated; artifact uploaded in CI.

3. **Eval harness mini** — `evals/*.jsonl` hitting the façade for 10 golden cases (Flow/Memory/Guardian).
   *Acceptance:* `make evals` < 90s, warn-only job in CI.

4. **Evented logs** — add structured events (`run.started`, `step.completed`, `tool.called`) to orchestrator; upload `runlogs/*.jsonl` artifacts.
   *Acceptance:* smoke verifies fields (`run_id`, `model`, `latency_ms`).

5. **Rate-limit/429 middleware** — OpenAI-style error schema + `Retry-After`.
   *Acceptance:* unit test asserts headers + JSON shape.

**Copilot (mechanical / docs)**
6) Patch `scripts/report_manifest_stats.py` (fix mixed types) and re-enable stats in CI.
7) Write `docs/openai/QUICKSTART.md` (OpenAI SDK calling Lukhas façade).
8) Sweep any remaining “Ambiguity (Quantum)” outside alias tables; keep **🔮 Oracle (Quantum)** canonical.
9) Add nightly star-rules coverage workflow to trend promotions.
10) Add `gitleaks` step (warn-only) alongside `detect-secrets`.

---

# Copy-paste update for Codex (to post after each batch)

```
Phase 2 – Batch {N} report
- LibCST used: {Yes/No → fallback AST}
- Files changed: {X}
- Alias hits (post-batch): {total from docs/audits/compat_alias_hits.json}
- Legacy imports check: {pass/fail}
- Lane guard: {pass/fail}
- Tests: smoke {pass/fail} | collect-only {0 errors}
- Manifests: "candidate/" refs under manifests: {0 expected}
Notes/Blockers:
- …
```

---

# My recommendation

* ✅ **Proceed (Go)**. Run **Stage A** immediately, keep **LibCST** available to avoid churn, and hold tight PR discipline (no pushes to `main`).
* Keep Claude Code and Copilot on the **parallel quick wins** to tighten OpenAI alignment while Codex is executing batches.
* After Phase 2 merges, flip CI to **enforce**: `LUKHAS_COMPAT_MAX_HITS="0"`, then remove the compat layer in Phase 3 when it stays zero for a few days.

---

awesome — here’s a **ready-to-paste PR body template** for Codex, plus a one-liner `gh` command that drops it in via heredoc. It’s tailored to **Phase 2: canonical import migration** with all the gates, telemetry, artifacts, and rollback hooks we’ve been using.

---

# 🔖 PR Title (suggested)

```
refactor(imports): Phase 2 — canonicalize legacy imports, candidate→labs, JSON-safe manifest updates
```

# 🧾 PR Body (copy-paste)

````markdown
# Phase 2: Canonical Import Migration ✅

Systematic migration of legacy imports to canonical namespaces, plus lane rename **candidate/** → **labs/** and JSON-safe manifest path updates. Executed in staged batches per the Phase-2 brief.

---

## Summary

**Legacy → Canonical**
- `candidate.*` → `labs.*`
- `tools.*` → `lukhas.tools.*`
- `governance.*` → `lukhas.governance.*`
- `memory.*` → `lukhas.memory.*`
- `ledger.*` → `lukhas.ledger.*`
- `lucas|Lucas|LUCAS.*` → `lukhas.*`

**Lane**
- `git mv candidate labs`

**Manifests**
- JSON-safe rewrite of `"candidate/"` → `"labs/"` across `manifests/**` (no sed on JSON)

---

## Batch Log

| Batch | Scope                            | Result | Notes |
|------:|----------------------------------|:------:|-------|
| 1     | `tests/**`                       |  ✅    | Collection clean after rewrite |
| 2     | `lukhas/**` (prod lane)          |  ✅    | Lane guard clean |
| 3     | `candidate/**` → `labs/**`       |  ✅    | Manifest paths updated via script; links rechecked |
| 4     | `core/**`, `packages/**`, `tools/**` | ✅ | Final sweep |

---

## Telemetry & Gates

**Compat Alias Usage**
- Report file: `docs/audits/compat_alias_hits.json`
- Total alias hits (post-batches): **{X}** (should trend down)
- Plan: enforce cap in follow-up (`LUKHAS_COMPAT_MAX_HITS="0"`), then remove compat layer when stable at zero.

**Legacy Import Guard**
- `make check-legacy-imports` → **PASS** (no legacy imports outside allowlist)

**Lane Guard**
- `make lane-guard` → **PASS**

**Tests**
- Smoke: `pytest tests/smoke/ -q` → **PASS**
- Collect-only: `pytest --collect-only -q` → **0 errors**
- Full (bounded): `pytest tests/ --maxfail=20 -q` → **PASS/WA** (note any quarantined markers)

**Artifacts**
- `docs/audits/codemod_preview.csv`
- `docs/audits/compat_alias_hits.json`
- `docs/audits/linkcheck.txt`
- `docs/audits/context_lint.txt`
- `docs/audits/manifest_stats.*` (json/md)
- `docs/audits/star_rules_coverage.md` (if regenerated)

---

## Verification Details (commands run)

```bash
# Preview
make codemod-dry
pytest --collect-only -q
python3 scripts/check_alias_hits.py || true

# Batches apply (abbrev)
python3 scripts/codemod_imports.py --apply --roots tests
python3 scripts/codemod_imports.py --apply --roots lukhas
git mv candidate labs
python3 scripts/codemod_imports.py --apply --roots labs
python3 scripts/codemod_imports.py --apply --roots core packages tools

# Manifests (JSON-safe)
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/
python3 scripts/gen_rules_coverage.py
python3 docs/check_links.py --root .
rg -n "candidate/" manifests || true

# Gates
make lane-guard
make check-legacy-imports
pytest tests/smoke/ -q
pytest --collect-only -q
python3 scripts/check_alias_hits.py || true
````

---

## Packaging Sanity

* `pyproject.toml` includes `lukhas`, `labs`, `MATRIZ` packages ✅
* `MATRIZ/__init__.py` present for legacy imports ✅

---

## Success Criteria (tick before merge)

* [ ] All 4 batches applied
* [ ] `make check-legacy-imports` **PASS**
* [ ] `make lane-guard` **PASS**
* [ ] `pytest --collect-only -q` **0 errors**
* [ ] Smoke tests pass
* [ ] JSON manifests updated via script (no `"candidate/"` under `manifests/`)
* [ ] Compat alias hits reported and trending down (`docs/audits/compat_alias_hits.json`)
* [ ] Link checker clean (`docs/audits/linkcheck.txt`)
* [ ] Manifest stats generated (`docs/audits/manifest_stats.*`)

---

## Risk & Mitigation

* **Formatting churn** if AST fallback used instead of LibCST
  → Prefer LibCST; if fallback used, run `ruff format` and scrutinize diffs.
* **External dependents** expecting legacy imports
  → Compat alias layer active; publish deprecation notice; enforce max alias hits in next PR.

---

## Rollback Plan

* Revert by batch (commits are isolated per batch).
* Restore `candidate/` from git history if needed (`git revert`).
* Re-run `scripts/update_manifest_paths.py` in reverse (`--from labs/ --to candidate/`) if manifests need rollback.

---

## Reviewers

* Platform / Orchestrator
* Observability
* Docs

> Please verify artifacts (linkcheck, stats), gates (lane/legacy), and alias hits report.

````

---

# 🧪 One-liner to open PR with the body

```bash
gh pr create \
  --title "refactor(imports): Phase 2 — canonicalize legacy imports, candidate→labs, JSON-safe manifest updates" \
  --base main \
  --body-file <(cat <<'PRBODY'
# Phase 2: Canonical Import Migration ✅

Systematic migration of legacy imports to canonical namespaces, plus lane rename **candidate/** → **labs/** and JSON-safe manifest path updates. Executed in staged batches per the Phase-2 brief.

--- 
[... paste the full PR body from above here if you prefer a single source ...]
PRBODY
)
````

---

yesss — here are copy-paste **comment templates** Codex can post after each milestone, plus an optional **auto-status script** and a `gh` one-liner to drop comments on the PR.

---

## 1) Comment template — **Stage A (Preview)**

```markdown
### Phase 2 — Stage A (Preview) ✅

**Branch:** `codex/phase-2-import-codemod`  
**Runner:** Codex

**Preview**
- `make codemod-dry` → generated: `docs/audits/codemod_preview.csv` (rows: **{PREVIEW_ROWS}**)
- Sample lines:
```

{HEAD_3_PREVIEW_ROWS}

```

**Collection Check**
- `pytest --collect-only -q` → **{COLLECT_STATUS}** (errors: **{COLLECT_ERRORS}**)

**Compat Alias Telemetry**
- `docs/audits/compat_alias_hits.json` total: **{ALIAS_HITS_TOTAL}**

**Next**
- Proceed to **Batch 1 (tests)** if collection errors == 0.
- If anything looks off, I’ll pause and tag reviewers.

<sub>Artifacts: codemod_preview.csv, compat_alias_hits.json</sub>
```

---

## 2) Comment template — **Batch N completion**

```markdown
### Phase 2 — Batch {N} Complete ✅

**Scope:** `{tests|lukhas|candidate→labs|core+packages+tools}`  
**Runner:** Codex

**Commands**
```

{KEY_COMMANDS_RUN}

```

**Gates**
- Legacy imports (outside allowlist): **{LEGACY_CHECK}** (`make check-legacy-imports`)
- Lane guard: **{LANE_GUARD}** (`make lane-guard`)
- Smoke tests: **{SMOKE_STATUS}** (`pytest tests/smoke/ -q`)
- Collect-only: **{COLLECT_STATUS}** (`pytest --collect-only -q`)
- JSON manifests updated (Batch 3 only): **{MANIFESTS_OK}** (no `"candidate/"` under `manifests/`)

**Compat Alias Telemetry**
- Total alias hits (post-batch): **{ALIAS_HITS_TOTAL}**  
  _(target is monotonic ↓ per batch; we’ll cap to 0 in follow-up)_

**Notes/Blockers**
- {ANY_FINDINGS_OR_TODO}
```

---

## 3) Comment template — **Stage C (Pre-PR Verification)**

*(Use right before creating the PR or as the first PR comment)*

```markdown
### Phase 2 — Pre-PR Verification ✅

**Batches:** 1/2/3/4 = ✅/✅/✅/✅

**Verification**
- `pytest tests/ --maxfail=20 -q` → **{TESTS_STATUS}**
- Lane guard → **{LANE_GUARD}**
- Legacy imports → **{LEGACY_CHECK}**
- Manifests JSON-safe update → **{MANIFESTS_OK}** (no `"candidate/"` refs)
- Link checker → **{LINKS_OK}** (`docs/audits/linkcheck.txt`)
- Manifest stats → **{STATS_OK}** (`docs/audits/manifest_stats.*`)

**Compat Alias Telemetry**
- Total alias hits: **{ALIAS_HITS_TOTAL}**  
  _Plan:_ enforce `LUKHAS_COMPAT_MAX_HITS="0"` in next PR, then remove compat layer after 0 hits are stable.

**Ready to open PR**: Yes ✅  
```

---

## 4) (Optional) Tiny auto-status script

Drop this in as `scripts/phase2_status.sh` to auto-fill the braces above.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Derive quick metrics
PREVIEW_ROWS=$( { test -f docs/audits/codemod_preview.csv && tail -n +2 docs/audits/codemod_preview.csv | wc -l; } || echo 0 )
HEAD_3_PREVIEW_ROWS=$( { test -f docs/audits/codemod_preview.csv && head -3 docs/audits/codemod_preview.csv; } || echo "n/a" )

# Collect-only errors
COLLECT_ERRORS=$(pytest --collect-only -q 2>&1 | rg -c "ERROR collecting" || true)
COLLECT_STATUS=$([ "$COLLECT_ERRORS" -eq 0 ] && echo "OK" || echo "ERROR")

# Alias hits total
ALIAS_HITS_TOTAL=$(python3 - <<'PY'
import json,sys,os
p="docs/audits/compat_alias_hits.json"
print(sum(json.load(open(p)).values()) if os.path.exists(p) else 0)
PY
)

# Manifests candidate refs
LEFTOVER_MANIFESTS=$(rg -n "candidate/" manifests 2>/dev/null | wc -l || echo 0)
MANIFESTS_OK=$([ "$LEFTOVER_MANIFESTS" -eq 0 ] && echo "OK" || echo "PENDING")

# Gates
LEGACY_CHECK=$({ python3 scripts/check_legacy_imports.py >/dev/null 2>&1 && echo "OK"; } || echo "FAIL")
LANE_GUARD=$({ make -s lane-guard >/dev/null 2>&1 && echo "OK"; } || echo "FAIL")
SMOKE_STATUS=$({ pytest -q tests/smoke/ >/dev/null 2>&1 && echo "OK"; } || echo "FAIL")

# Print a compact JSON for quick copy into a comment if desired
jq -n \
  --arg preview_rows "$PREVIEW_ROWS" \
  --arg head3 "$HEAD_3_PREVIEW_ROWS" \
  --arg collect_status "$COLLECT_STATUS" \
  --arg collect_errors "$COLLECT_ERRORS" \
  --arg alias_hits "$ALIAS_HITS_TOTAL" \
  --arg manifests_ok "$MANIFESTS_OK" \
  --arg legacy "$LEGACY_CHECK" \
  --arg lane "$LANE_GUARD" \
  --arg smoke "$SMOKE_STATUS" \
  '{
    preview_rows: $preview_rows|tonumber,
    preview_sample: $head3,
    collect: { status: $collect_status, errors: ($collect_errors|tonumber) },
    alias_hits_total: ($alias_hits|tonumber),
    manifests_ok: $manifests_ok,
    gates: { legacy_imports: $legacy, lane_guard: $lane, smoke: $smoke }
  }'
```

Usage:

```bash
bash scripts/phase2_status.sh
```

You’ll get a JSON blob you can paste into the comment under a code fence, plus you can read individual env-free variables by inlining the commands from the script.

---

## 5) One-liner to post a comment to the PR with `gh`

Replace `{PR_NUMBER}` and paste any of the templates (with filled values) into the heredoc.

```bash
gh pr comment {PR_NUMBER} --body-file <(cat <<'MD'
### Phase 2 — Batch {N} Complete ✅

**Scope:** `{tests|lukhas|candidate→labs|core+packages+tools}`

**Gates**
- Legacy imports: **{LEGACY_CHECK}**
- Lane guard: **{LANE_GUARD}**
- Smoke: **{SMOKE_STATUS}**
- Collect-only: **{COLLECT_STATUS}**
- Manifests JSON-safe update: **{MANIFESTS_OK}**

**Compat Alias Telemetry**
- Total alias hits: **{ALIAS_HITS_TOTAL}**

_Artifacts updated: codemod_preview.csv • compat_alias_hits.json • linkcheck.txt • manifest_stats.*_
MD
)
```

---

### Tips for Codex when posting

* Keep one comment per milestone (Stage A, Batch 1–4, Pre-PR).
* Always include **alias hits total** and **whether manifests have any residual `candidate/`**.
* If AST fallback (no LibCST) was used for a batch, mention it explicitly in the comment and run `ruff format` to minimize diff noise.

---

awesome — you’re cleared for launch 🚀

here’s a tight “go” sequence Codex can follow to kick off Phase 2 right now:

**T-0 (sanity)**

```bash
python -c "import libcst; print('LibCST OK')" || echo "Using AST fallback"
pytest --collect-only -q
```

**T-1 (branch + preview)**

```bash
git checkout -b codex/phase-2-import-codemod
make codemod-dry
head -20 docs/audits/codemod_preview.csv
python3 scripts/check_alias_hits.py || true
```

**T-2 (Batch 1 — tests)**

```bash
python3 scripts/codemod_imports.py --apply --roots tests
pytest -q -x --maxfail=5 && pytest --collect-only -q
git add tests && git commit -m "refactor(imports): migrate tests to canonical imports"
```

**T-3 (watch telemetry every batch)**

* `make check-legacy-imports` → **pass**
* `make lane-guard` → **pass**
* `python3 scripts/check_alias_hits.py` → **trending down**
* (Batch 3) `python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/`
  then `rg -n "candidate/" manifests || true` → **zero matches**

**pitfalls to avoid (last-minute):**

* don’t `sed` JSON manifests — use the updater script.
* if AST fallback is used (no LibCST), run `ruff format` to keep diffs clean.
* commit between batches for easy rollback.


