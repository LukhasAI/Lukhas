---
status: stable
type: operations
owner: engineering
module: root
redirect: false
moved_to: null
---

![Status: Stable](https://img.shields.io/badge/status-stable-green)
![Owner: engineering](https://img.shields.io/badge/owner-engineering-lightblue)

# LUKHAS — Operational Runbook (v0.03-prep)

This is the **hands-on, current** guide for branch hygiene and the **Docs/Tests colocation + legacy import ratchet**.
It supersedes older exploratory notes and chat transcripts.

## 1) Branch hygiene

```bash
git fetch --all --prune
git switch main && git pull
git checkout -b develop/v0.03-prep
git push -u origin develop/v0.03-prep
```

If an old `develop/v0.03` exists, archive + delete the remote branch:

```bash
git tag backup/develop-v0.03-before-cleanup origin/develop/v0.03
git push origin backup/develop-v0.03-before-cleanup
git push origin --delete develop/v0.03
```

## 2) Current state (✅ = done)

- ✅ Import migration infra (alias hook v2, doctor, ledger, codemod)
- ✅ Docs/Tests colocation toolchain (mapping, migration, validation, health)
- ✅ Batch-1 docs migration (160 files, history-preserving + redirects)
- ✅ Front-matter normalization (62 stubborn YAML files remain; manual)
- ✅ Import ratchet ≥5 then ≥3 (~140 tests migrated)
- ✅ CI gates: structure + smoke + legacy-import budget (passing)
- ✅ develop/v0.03-prep rebased on main

### Rebased branches status

| Branch / PR | Base branch | Status | Notes |
|-------------|-------------|--------|-------|
| `develop/v0.03-prep` | `main` | ✅ Rebased | Force-updated to commit `47f10b80a` during 2025-10-06 cleanup; history preserved after rebase. |
| **PR #385** (soft-audit batch) | `main` | 🟢 Auto-merge enabled | Hygiene batch rebased onto `main` and ready for merge once guardrails finish running. |
| **PR #386** (ruffA fixes) | Guardian YAML baseline | 🟢 Auto-merge enabled | Ruff A-tier fixes stacked on the refreshed Guardian YAML branch after rebase alignment. |

## 3) Docs/Tests colocation

### Build/review mapping:

```bash
make docs-map
less artifacts/docs_mapping_review.md   # review confidence < 0.80
```

### Migrate (history-preserving):

```bash
make docs-migrate-dry
make docs-migrate-auto
```

### Validate:

```bash
make docs-lint
make validate-structure
make module-health
```

**Safeguards**: skips special root docs (e.g. `docs/_generated`, `docs/ADR`, `docs/architecture`, `docs/research`, `docs/domain_strategy`, `docs/collaboration`); uses filesystem paths (never dotted); injects missing front-matter; ensures per-module `tests/conftest.py`.

## 4) Legacy import ratchet (weekly)

```bash
make imports-report
make codemod-apply        # threshold ≥5 → 4 → 3 (then optional ≥2 later)
make tests-smoke && make gate-legacy
git add -A
git commit -m "refactor(imports): migrate safe batch (threshold≥X); no behavior change"
git push
```

**Budget policy**: update `artifacts/legacy_import_baseline.json` as hits fall (e.g., 640→600→550).
When < 50 hits: remove `lukhas/` shims and the alias hook in `tests/conftest.py`.

## 5) Known test nits

- **TRINITY_SYMBOLS** — keep xfail (not public API).
- **MATRIZ vs matriz** — fixed via uppercase alias in `matriz/__init__.py`.
- **experimental/ vs candidate/** — fixed via alias in `experimental/__init__.py`.
- **traces latest smoke** — defer until import surface stabilizes.

## 6) YAML front-matter edge cases (62 files)

Use micro-patches (quote colon titles, normalize tags, blockify long descriptions).
See `docs/gonzo/FRONTMATTER_FIXES.md` (or run the one-liners from prior session).

## 7) Canonical terminology (enforced)

Replace "Constellation Framework (8 Stars)" and "lane-based architecture (candidate/core/lukhas)" with:

### Constellation Framework (8 Stars)

- **⚛️ Identity (Anchor)** — ΛiD authentication, namespace management
- **✦ Memory (Trail)** — Fold-based memory, temporal organization
- **🔬 Vision (Horizon)** — Pattern recognition, adaptive interfaces
- **🌱 Bio (Living)** — Adaptive bio-symbolic processing
- **🌙 Dream (Drift)** — Creative consciousness expansion
- **⚖️ Ethics (North)** — Constitutional AI, democratic oversight
- **🛡️ Guardian (Watch)** — Safety compliance, cascade prevention
- **🔮 Oracle (Quantum)** — Quantum-inspired uncertainty

### Lanes

**L1 — Exploration · L2 — Integration · L3 — Production**

(Directory names like `candidate/`, `core/`, `lukhas/` may persist; prose uses L1/L2/L3.)

## 8) PR template (reviewer-friendly)

- What changed / Why / Safety / Follow-ups (imports ratchet; remove shims <50 hits)

## 9) Rollback (surgical)

```bash
git revert <MIGRATION_SHA>
git restore -SW --source=<pre-sha> -- docs/<path>
```

If any plan shows dotted paths (e.g. `consciousness.simulation`), re-run `make docs-map` with path-inference fixes.
