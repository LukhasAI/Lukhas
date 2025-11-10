# CODEX_PROMPTS — Codex / CODEX task prompts & templates
> For Codex/CODEX (heavy-duty code edits, safe refactors, API wiring, CI changes)

## Purpose
Codex is the best agent for surgical code edits, consistent refactoring, changing scripts, and writing small, well-contained programs (e.g., `guard_patch.py` changes, OPA policies, labot improvements). Codex should NOT invent new high-level architecture unilaterally — create ADRs.

---

## High-priority edits (Codex focus)

1. **Make labot PRs draft by default**
   * File: `tools/labot.py` → function `open_pr_shell`
   * Change `gh pr create` → `gh pr create --draft`
   * Add `labels: ["labot"]` when creating PRs
   * Add `--assume-yes` flag option for dry-run

   **Prompt example**
   ```
   Modify tools/labot.py: update open_pr_shell() to create DRAFT PRs with labels ["labot"], and add a --dry-run option that prints the gh command instead of executing it. Ensure ruff/mypy pass.
   ```

2. **Guard_patch enhancements**
   * Add YAML/OPA policy integration (optional): create `.policy/rules.rego` and a `tools/check_policy.py` to evaluate.
   * Add a `--allow-large-imports` toggle for a whitelist during controlled imports.

   **Prompt example**
   ```
   Extend tools/guard_patch.py to accept a --whitelist-file path; if present, files listed there are exempt from max-files/max-lines checks. Add tests for the new behavior.
   ```

3. **Split import script & safe reimport**
   * Add `scripts/split_labot_import.sh` as earlier provided.
   * Add a `--dry-run` that shows PR titles & branch names.

4. **OPA policy + CI integration**
   * Add `.policy/rules.rego` with rules forbidding:
     * forbid `except:` with no exception types
     * forbids test deletion in PRs
   * Add `opa eval` step to `labot_audit.yml`

   **Prompt example**
   ```
   Add .policy/rules.rego with rules forbidding broad except and test deletion. Modify .github/workflows/labot_audit.yml to run 'opa eval' and fail if rules violated.
   ```

5. **DAST / EQNOX wiring tasks**
   * Add small adapter modules that standardize messaging between `dast.or.py` orchestrator and MATRIZ. Create a `lukhas/adapters/dast_adapter.py` with typed interfaces and tests.
   * Add integration tests that use dependency overrides to simulate the orchestrator.

   **Prompt example**
   ```
   Create lukhas/adapters/dast_adapter.py implementing a simple typed interface: send_task(task: dict) -> dict. Add unit tests with mocked responses. Add an ADR describing the interface.
   ```

6. **OpenAPI drift deeper check**
   * Replace the stub `tools/check_openapi_drift.py` with a deep-differ that reports path/method/response schema differences and an optional `--autofix` to update saved `openapi.json` after steward confirmation.

   **Prompt example**
   ```
   Improve tools/check_openapi_drift.py to perform deep JSON Schema diff for paths and responses, and output a machine-readable summary. Add tests for the diffing logic.
   ```

---

## Prompt templates (Codex)

Use these concise templates when sending to Codex:

### A. Safe refactor prompt
```
You are Codex, a surgical refactorer with strict safety rules.

Repo: Lukhas/Lukhas
Target: <file or module>

Task:
1. Explain the minimal refactor in 2-4 sentences.
2. Produce a patch (git diff) that:
   - keeps public API stable
   - includes unit tests for any behavior changes
   - is <= 100 LOC per patch
3. Add an ADR if the change affects design.

Run ruff and mypy on changed files and include outputs.

If you cannot perform safely, stop and explain why.
```

### B. CI patch / OPA policy prompt
```
Modify .github/workflows/labot_audit.yml to run OPA policy from .policy/rules.rego. Add .policy/rules.rego with rules forbidding broad 'except' and test deletion. Include tests that validate the OPA rules.
```

### C. Small script / utility prompt
```
Create scripts/split_labot_import.sh. Requirements:
- Input: commit SHA and group size
- Output: create draft PRs with gh (dry-run supported)
- Use safe checks (no protected paths)
- Add README: scripts/README.md describing usage
```

---

## Expected outputs (per prompt)

* A clean git patch (`git format-patch` style or `git commit`) with:
  * unit tests added/updated
  * mypy/ruff clean for changed files
  * ADR(s) if public API touched
  * PR description snippet for humans

---

## Assignment suggestions

* **Codex**: implement PR-draft change, OPA policy, labot improvements, split script, small adapters.
* **Interaction**: Codex opens Draft PRs labelled `codex:review` and assigns to Jules steward for architecture review.

---

## Audit / Sweep checklist (run now)

Run this from the repo root (Jules/maintainer):

```bash
# 1. Basic hygiene
git fetch origin main
git checkout main
git pull origin main

# 2. Guard/Policy
python3 tools/guard_patch.py --base cb5d4cc01^ --head cb5d4cc01 --protected .lukhas/protected-files.yml

# 3. Lint & types
pip install ruff mypy pip-audit pip-tools
ruff .
mypy .

# 4. Run labot plan to refresh candidates
python3 tools/labot.py --mode plan+gen

# 5. List open PRs created by labot/claude/codex
gh pr list --author labot --state open
gh pr list --author claude --state open
gh pr list --author codex --state open

# 6. Mutmut baseline (optional)
mutmut run --paths-to-mutate $(git ls-files 'serve/*.py' | tr '\n' ' ')
mutmut results > reports/mutmut_results.json

# 7. Verify artifacts
ls -al reports | sed -n '1,120p'
```

## Final note

Codex must respect the two-key rule and create Draft PRs for human review. All changes must pass guard_patch before merge.
