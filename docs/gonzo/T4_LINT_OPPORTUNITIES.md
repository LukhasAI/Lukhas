# T4 — Lint Opportunities & Playbook

**Resumen (español)**
Este documento resume oportunidades concretas para convertir alertas del linter en trabajo priorizado y valor técnico. Propone canales (autofix PRs, codemods, playbooks, tablero de triage) y pasos operativos para incorporar estas oportunidades al parche T4 Lint Platform ya creado.

---

## Vision (English)
T4 Lint Platform should not only track unused-imports but turn the whole lint surface into an actionable, measurable backlog of engineering work. Each lint finding becomes a tracked Intent (TODO[T4-LINT-ISSUE]) or an automated PR when safe. The platform prioritizes: safety → automation → human triage.

## Opportunities (concrete)

### 1. Autofix PR Bot (low-friction wins)
Weekly scheduled CI job that:
- Runs `isort`, `black`, `ruff --fix` where safe.
- Commits, opens a PR branch `t4-lint-autofix-<ts>`.
- Tracks PR metrics: acceptance rate, review time, lines changed.
**Value:** Rapid, low-risk cleanups for style & trivial issues (I001, F401, SIM102, RUF001...).

### 2. Codemod Library (safe but powerful)
A small library of LibCST codemods for surgical transformations:
- B008 (function-call-in-default-argument) — starter codemod included.
- F403 (import-star → explicit imports): codemod that infers used names.
- E701/E702 → split statements on separate lines.
Codemods support `--dry-run` & `--apply`, generate tests, and create PRs when applied.

### 3. Lint Triage Board + Intent Registry
- Intent Registry (SQLite) becomes source of truth; feed a GitHub Project / board with columns: `New`, `Reserved`, `Planned`, `Committed`, `Implemented`.
- Monthly "Lint Garage" working session to clear top 20 `reserved` high-impact items.

### 4. IDE Quick-Fixes & Developer UX
- Provide VSCode snippets that parse `TODO[T4-LINT-ISSUE]` structured JSON and allow maintainers to:
  - Create ticket (GH) and mark `planned`.
  - Apply suggestion locally and open PR.

### 5. Codified Playbooks & Training
- `docs/gonzo/lint_playbooks/` with recipes for common refactors:
  - B008: pattern + codemod explanation + tests.
  - F821: safe import heuristics, how to decide.
  - F403: how to replace `from x import *`.

### 6. Release Readiness & Security Gates
- Critical rules (F821, F403, B904) have thresholds for release. If any regresses above X, fail release checklist.

## Implementation Roadmap (90 days)
1. **Week 1–2**: Add Autofix scheduler (weekly) + isort & ruff --fix flow (dry-run).  
2. **Week 3–4**: Deploy Intent Registry + board; wire annotator for lint issues.  
3. **Week 5–8**: Deliver codemods: B008 (pilot), F403 (pilot). Run small pilots.  
4. **Week 9–12**: Iterate on UX (VSCode quick-fix) and enable stricter CI rules for production lanes.

## Acceptance Criteria
- Autofix PR acceptance rate > 70% after first 4 weeks.
- Top 10 lint findings show a 50% reduction after 12 weeks.
- All `planned` entries have owner + ticket before merging.

## Safety & Governance
- Autofix PRs require human review; do not merge automatically.
- Codemods run with `--dry-run` first, and all PRs must include tests.
- Annotations must not include secrets (DLP scan on comment content).

---

**End of document.**
