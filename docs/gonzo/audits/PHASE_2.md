
---

**To: Codex**
**Subject:** Phase 2 soft-audit follow-through + quick parallel wins

Great work on `fix/codex10/soft-audit-batch01` — the rename fixes, prod-lane gates, idempotency tests, and health artifacts all look solid. Let’s close the loop and squeeze a few high-impact wins in parallel.

## A) Immediate validation (please run now)

1. **Smoke + unit core (prod lanes only)**

```bash
pytest tests/smoke -q --maxfail=1
pytest tests/unit -q --maxfail=1
```

* **Attach**: `.pytest_cache/v/cache/lastfailed`, `tests/.pytest_last.log` (if your env writes it)

2. **Prod-lane lint + bytecode compile**

```bash
# prod-only ruff job (as per pyproject)
python3 -m ruff check lukhas MATRIZ core --output-format=full

# compileall on prod lanes
python3 -m compileall -q lukhas MATRIZ core
```

* **Goal**: 0 ruff errors in `lukhas/`, `MATRIZ/`, `core/` and compileall exits 0.

3. **Health report (prove the pipes)**

```bash
python3 scripts/generate_system_health_report.py
```

* **Attach**: `docs/audits/system_health.{md,json}` to your branch (already done — just re-run to refresh).

If any failures pop, please fix inline and push updated artifacts on the same branch.

---

## B) Canonicalize health artifacts (prevent drift)

We now have two audit generators in the tree. Let’s unify outputs so tooling doesn’t bifurcate.

* **Task:** Make `scripts/generate_system_health_report.py` write **both**:

  * `docs/audits/system_health.{md,json}` (back-compat)
  * `docs/audits/health/latest.{md,json}` (canonical going forward)
* **Acceptance:**

  * Running the script creates/updates both sets.
  * CI job `health-audit` (if present) finds `docs/audits/health/latest.md`.

---

## C) Labs rename fallout in tests (quick sweep)

You already patched the main smoke entries — let’s ensure there are no stragglers.

* **Task:** Replace any residual `candidate/` or lane assumptions under `tests/**` (not only smoke).
  Run:

  ```bash
  rg -n "candidate/|candidate\." tests | tee /tmp/candidate_hits.txt
  ```

  Patch or mark with a `labs` fixture where appropriate.
* **Acceptance:** The grep returns **0** lines.

---

## D) Soft Audit items — bite-size batch for you

Use **`~/Lukhas/docs/gonzo/audits/LUKHAS_AI_SOFT_AUDIT.md`** as the source of truth. Please ship the following in **one PR** off your worktree branch:

1. **Issue inventory (CSV + labels)**

   * Parse the Soft Audit bullets into `docs/audits/CODEX_SOFT_AUDIT_TASKS.csv` with columns:
     `id, severity, area, file_hint, summary, suggested_owner(CODEX/CLAUDE/JULES/COPILOT)`.
   * Create matching GitHub issues (if repos permissions allow) or write `scripts/seed_soft_audit_issues.py` that prints `gh issue create` commands.

2. **Lane guard docs update**

   * Add a short “labs vs lukhas” explainer to `docs/README_LANES.md`:

     * `labs/` = development, non-blocking
     * `lukhas/` + `MATRIZ/` + `core/` = production lanes, fully gated

3. **Import policy check**

   * Add `make lane-guard-prod` target that runs import-linter only on `lukhas|MATRIZ|core`.
   * Ensure it’s documented in `docs/audits/system_health.md` footer.

4. **OpenAPI quick diff hook (local)**

   * Add `make openapi-diff-local` that:

     * Generates `docs/openapi/lukhas-openai.json`
     * Diffs against `docs/openapi/baseline.json` if present
     * Prints added/removed paths summary
   * Wire a brief note into `README.md` in the openapi section.

**Acceptance for D:** One PR titled:
`chore(audit): codex soft-audit batch01 (inventory, lane-guard-prod, openapi-diff-local)`
Includes CSV + updated docs + Makefile target + passing smoke/unit.

---

## E) Delegations (create short handoffs)

* **Claude Code (observability/CI)**

  * Turn the **health report** into a PR **job summary** (GHA Markdown) so we see pass/fail badge and key numbers without downloading artifacts.
  * Ensure `openapi-diff` PR comment includes emojis (➕➖⚠️) for added/removed/breaking.

* **Copilot (docs/examples)**

  * Add `examples/python/` and `examples/js/` for:

    * `/v1/responses` (minimal + with tools)
    * `/v1/dreams`
    * `/v1/indexes/*` (CRUD + search)
  * Each includes a one-liner README and a `make run` snippet.

No blockers for your stream; these are independent.

---

## F) PR instructions

When you’re done with A–D:

```bash
git add -A
git commit -m "chore(audit): finalize phase-2 soft-audit batch01 (tests rename, prod-lane gates, health artifacts, inventory)"
git push origin fix/codex10/soft-audit-batch01

gh pr create \
  --title "chore(audit): Phase-2 soft-audit batch01 (prod gates, labs rename, health)" \
  --body "Validates labs rename across tests, locks prod-lane lint/compile gates, unifies health artifacts, and seeds Soft Audit inventory. Includes Make targets and docs updates. Smoke/unit passing."
```

Tag me and @claude-code for review.

---

If you hit anything ambiguous in the Soft Audit doc, annotate it in the CSV as `needs-clarification` and keep moving — don’t block the batch.
