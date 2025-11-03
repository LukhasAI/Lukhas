# TODO List — MATRIZ Flattening (T4 / surgical)

NOTE: all tasks must be executed from repo root. Use Python 3.9 environment to match CI.

---

TODO-01: Generate `flatten_map.csv` (top 50)
Description: Create a canonical CSV of top-50 files to flatten; seeds are provided above.
Targets:
  - release_artifacts/matriz_readiness_v1/flatten_map.csv
Agent action:
  - Step 1: Ensure discovery outputs exist (see discovery/).
    ```bash
    ls -la release_artifacts/matriz_readiness_v1/discovery || true
    ```
  - Step 2: (If not present) run the discovery commands from the main prompt to regenerate `discovery/top_python_files.txt`.
  - Step 3: Run the included helper (if you want) to create the map:
    ```bash
    python3 release_artifacts/matriz_readiness_v1/scripts/generate_flatten_map.py \
      --input release_artifacts/matriz_readiness_v1/discovery/top_python_files.txt \
      --output release_artifacts/matriz_readiness_v1/flatten_map.csv
    ```
    (Note: I included a simple generator script; it uses heuristics and the CSV shown above is already a ready draft.)
  - Step 4: Manual review: open `flatten_map.csv` and confirm `move_strategy` choices for high-risk modules.
Verification:
  - `cat release_artifacts/matriz_readiness_v1/flatten_map.csv | wc -l` should be >= 51 (header + 50 rows)
Rollback:
  - `git checkout -- release_artifacts/matriz_readiness_v1/flatten_map.csv`
Risk:
  - Low. This is a planning artifact only.
Notes:
  - After manual review, agent will proceed to implement TODO-02.

---

TODO-02: Implement shim pattern for **VIVOX** canonical file
Description: Implement shim-first for a canonical VIVOX/MATRIZ node (`candidate/core/matrix/nodes/memory_node.py`) as a worked example and PR.
Targets:
  - original: `candidate/core/matrix/nodes/memory_node.py`
  - new: `MATRIZ/matriz_memory_node.py`
  - shim: `candidate/core/matrix/nodes/memory_node.py` (replaced with shim)
Agent action:
  - Step 1: Create branch
    ```bash
    git checkout -b refactor/flatten-vivox-v1
    ```
  - Step 2: Create new flat module with a copy of implementation
    ```bash
    git show HEAD:candidate/core/matrix/nodes/memory_node.py > MATRIZ/matriz_memory_node.py
    # If the file has relative imports, pre-process them:
    # (A) use the libcst script to rewrite module-level imports if needed:
    python3 release_artifacts/matriz_readiness_v1/scripts/rewrite_imports_libcst.py \
      --mapping '{"candidate.core.matrix.nodes":"MATRIZ"}' \
      candidate/core/matrix/nodes/memory_node.py > MATRIZ/matriz_memory_node.py
    ```
  - Step 3: Create shim at original location (overwrite original file with shim):
    ```bash
    cat > candidate/core/matrix/nodes/memory_node.py <<'PY'
    # DEPRECATED shim: moved to MATRIZ/matriz_memory_node.py
    from MATRIZ.matriz_memory_node import MemoryNode  # noqa: TID001
    __all__ = ["MemoryNode"]
    PY
    ```
  - Step 4: Run formatting & lint:
    ```bash
    black MATRIZ/matriz_memory_node.py candidate/core/matrix/nodes/memory_node.py
    ruff check --select E,F,W,I --fix MATRIZ/matriz_memory_node.py candidate/core/matrix/nodes/memory_node.py || true
    ```
  - Step 5: Verification:
    ```bash
    python3 -m compileall candidate/core/matrix/nodes/memory_node.py MATRIZ/matriz_memory_node.py
    ruff check --select E,F,E741 MATRIZ/matriz_memory_node.py candidate/core/matrix/nodes/memory_node.py
    pytest tests -k "matriz or tier1" -q || true
    ```
  - Step 6: Commit & PR
    ```bash
    git add MATRIZ/matriz_memory_node.py candidate/core/matrix/nodes/memory_node.py
    git commit -m "refactor(flatten): shim memory_node → MATRIZ/matriz_memory_node.py"
    git push -u origin refactor/flatten-vivox-v1
    gh pr create --base main --head refactor/flatten-vivox-v1 \
      --title "refactor(flatten-vivox): shim memory_node → MATRIZ/matriz_memory_node.py" \
      --body-file release_artifacts/matriz_readiness_v1/pr_templates/refactor_flatten_vivox.md
    ```
Verification:
  - compile must succeed; `ruff` must not create E/F errors; smoke tests in CI must pass for the PR.
Rollback:
  - `git reset --hard origin/main && git branch -D refactor/flatten-vivox-v1`
Risk:
  - Medium/High: potential for import path mistakes if original file used relative imports heavily. Mitigation: use libCST rewrite and run compile checks.
Notes:
  - The shim must be minimal and explicitly `# DEPRECATED` with a plan to remove after 2 release cycles.

---

TODO-03: Physical move for **BENCHMARKS** small subset using AST-based import rewrite
Description: Move 3 small benchmark modules physically into top-level flattened modules (no shim), because discovery shows they have low external import centrality.
Targets:
  - e.g. `benchmarks/matriz_pipeline.py` → `benchmarks_matriz_pipeline.py`
  - `benchmarks/scripts/benchmark_matriz_pipeline.py` → `benchmarks_benchmark_matriz_pipeline.py`
Agent action:
  - Step 1: Branch
    ```bash
    git checkout -b refactor/flatten-benchmarks-v1
    ```
  - Step 2: Move files (preserve history)
    ```bash
    git mv benchmarks/matriz_pipeline.py benchmarks_matriz_pipeline.py
    git mv benchmarks/scripts/benchmark_matriz_pipeline.py benchmarks_benchmark_matriz_pipeline.py
    ```
  - Step 3: Run AST import rewrite across repo:
    ```bash
    python3 release_artifacts/matriz_readiness_v1/scripts/rewrite_imports_libcst.py \
      --mapping '{"benchmarks.matriz_pipeline":"benchmarks_matriz_pipeline","benchmarks.scripts.benchmark_matriz_pipeline":"benchmarks_benchmark_matriz_pipeline"}' \
      --root .
    ```
    (This rewrites `from benchmarks.matriz_pipeline import ...` → `from benchmarks_matriz_pipeline import ...` safely.)
  - Step 4: Run formatters and ruff fix:
    ```bash
    black benchmarks_matriz_pipeline.py benchmarks_benchmark_matriz_pipeline.py
    ruff check --select E,F,W,I --fix .
    ```
  - Step 5: Verification:
    ```bash
    python3 -m compileall .
    pytest -q -k "benchmark or matriz" || true
    ```
  - Step 6: Commit & PR:
    ```bash
    git add -A
    git commit -m "refactor(flatten-benchmarks): flatten benchmark modules (3 files)"
    git push -u origin refactor/flatten-benchmarks-v1
    gh pr create --base main --head refactor/flatten-benchmarks-v1 --title "refactor(flatten-benchmarks): small flatten" --body-file release_artifacts/matriz_readiness_v1/pr_templates/refactor_flatten_benchmarks.md
    ```
Verification:
  - compile success, `ruff` OK, smoke tests for bench area pass.
Rollback:
  - `git reset --hard origin/main && git branch -D refactor/flatten-benchmarks-v1`
Risk:
  - Low/Medium: possible missing import rewrites or import cycles; mitigated with AST rewrite and compile checks.
Notes:
  - Keep PR small and focused (max 3 files).

---

TODO-04: E741 pass for moved modules in **TESTS**
Description: After flattening, run E741 renames in tests for single-letter variables introduced or exposed by moves.
Targets:
  - tests/** (subtree), run E741 fixes PR per test-subsystem.
Agent action:
  - Step 1: Branch (per-test-subsystem)
    ```bash
    git checkout -b refactor/e741-tests-v1
    ```
  - Step 2: Find E741 instances:
    ```bash
    rg -n --type py '\b[lOI]\b(?!\w)' tests/ -g '!**/fixtures/**' > release_artifacts/matriz_readiness_v1/discovery/tests_e741_candidates.txt
    ```
  - Step 3: Make manual/contextual renames (examples)
    - `l` → `line_idx` if used as index; `l` → `logger` if used as logger
    - `O` → `output_val` / `op_result`
    - `I` → `input_` / `in_val`
  - Step 4: Run `ruff` and tests:
    ```bash
    ruff check --select E741,F401,F841 tests/ --fix || true
    pytest tests -q -k "matriz or smoke" || true
    ```
  - Step 5: Commit & PR:
    ```bash
    git add -A
    git commit -m "refactor(e741-tests): rename single-letter identifiers in tests"
    git push -u origin refactor/e741-tests-v1
    gh pr create --base main --head refactor/e741-tests-v1 --title "refactor(e741-tests): disambiguate single-letter names" --body-file release_artifacts/matriz_readiness_v1/pr_templates/refactor_e741_tests.md
    ```
Verification:
  - `ruff check --select E741 tests/` returns zero (or documented `# noqa` exceptions).
Rollback:
  - `git reset --hard origin/main && git branch -D refactor/e741-tests-v1`
Risk:
  - Medium: renaming fixtures requires updating conftest or adding shims for fixture names; add compatibility alias if necessary.

---

TODO-05: CI & packaging updates (pyproject + pre-commit)
Description: Update `pyproject.toml` and `.pre-commit-config.yaml` to reflect new top-level modules and to ensure future changes are gated.
Targets:
  - pyproject.toml (adjust `tool.ruff.src` and `target-version`), `.pre-commit-config.yaml` under repo root.
Agent action:
  - Step 1: Branch
    ```bash
    git checkout -b chore/flatten-ci-updates
    ```
  - Step 2: Update `pyproject.toml`:
    - Add new flattened directories to `tool.ruff.src`, e.g. add `"MATRIZ"` and top-level flattened module directory if not present.
    - Ensure `target-version` matches CI (py39).
  - Step 3: Add `.pre-commit-config.yaml` if missing with Black + Ruff hooks (I provided a recommended snippet in artifacts).
  - Step 4: Commit & PR:
    ```bash
    git add pyproject.toml .pre-commit-config.yaml
    git commit -m "chore(ci): add pre-commit and update ruff src for flattening"
    git push -u origin chore/flatten-ci-updates
    gh pr create --base main --head chore/flatten-ci-updates --title "chore(ci): prepare CI for flattening"
    ```
Verification:
  - On branch PR, CI must run ruff/black checks and pass.
Rollback:
  - `git reset --hard origin/main && git branch -D chore/flatten-ci-updates`
Risk:
  - Low. Standard CI housekeeping.
Notes:
  - Ensure `pyproject.toml` `tool.ruff.lint.isort.known-first-party` includes new top-level names.

---

TODO-06: Full verification & artifact packaging
Description: Run full compile/ruff/smoke tests and collect artifacts for release and audit.
Targets:
  - release_artifacts/matriz_readiness_v1/verification/*
Agent action:
  - Step 1:
    ```bash
    chmod +x release_artifacts/matriz_readiness_v1/scripts/verify_and_collect.sh
    ./release_artifacts/matriz_readiness_v1/scripts/verify_and_collect.sh
    ```
  - Step 2: Package artifacts
    ```bash
    tar -czf release_artifacts/matriz_readiness_v1/artifact_bundle.tar.gz -C release_artifacts matriz_readiness_v1
    ```
Verification:
  - `verification/compile_log.txt` shows no SyntaxError
  - `verification/ruff_ef_log.txt` shows `0` E/F errors for moved/shimmed files
Rollback:
  - See individual PR rollback commands (pre-PR)
Risk:
  - Low. This is verification only.

---

TODO-07: Release preview & signed tag `v0.9.2-flatten-preview`
Description: After PRs merge, produce a signed preview tag and a draft release with artifacts.
Targets:
  - Tag: `v0.9.2-flatten-preview`; Draft release upload via `gh`.
Agent action:
  - Step 1: Create signed tag (dry run / then real):
    ```bash
    git checkout main
    git pull
    git tag -s v0.9.2-flatten-preview -F release_artifacts/matriz_readiness_v1/tag_message.txt
    git push origin v0.9.2-flatten-preview
    ```
  - Step 2: Create a draft release and upload artifacts:
    ```bash
    gh release create v0.9.2-flatten-preview --repo LukhasAI/Lukhas --notes-file release_artifacts/matriz_readiness_v1/release_notes.md --draft
    gh release upload v0.9.2-flatten-preview release_artifacts/matriz_readiness_v1/artifact_bundle.tar.gz
    ```
Verification:
  - Release created as draft, artifacts attached, tag is GPG-signed and verifiable.
Rollback:
  - `git push origin --delete v0.9.2-flatten-preview` and delete draft release on GitHub
Risk:
  - Low.
