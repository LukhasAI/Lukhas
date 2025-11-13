# Agent Brief — Lukhas AI (T4 / 0.01%)

Purpose
-------
This directory contains agent-ready artifacts for safe, auditable, high-value repo work:
- surgical single-file refactors (Claude Code / Copilot)
- codemods and batch PR orchestration (Codex / ChatGPT-Codex)
- CI changes for SLSA attestations and runbooks
- safety & ethics templates

Principles (T4 / 0.01%)
-----------------------
1. **Small, auditable changes**: one file per commit/PR where possible.
2. **Human-in-loop**: no automated merges. Every PR must be reviewed before merge.
3. **Reversible**: back up files before applying changes. Use `.bak` or branch per PR.
4. **No secrets in repo**: use env vars or secret stores (cosign keys, in-toto keys).
5. **Ethics first**: Do not run human-judged experiments without IRB/ethics signoff.

Agent roles
-----------
- **Claude Code (IDE)**: surgical single-file edits (providerization, lazy-load, types, tests).
- **Codex / ChatGPT-Codex (Cloud)**: codemods, batch PR generation, ephemeral worktree validation, SLSA automation, nightly harness.

How to use
----------
1. For single-file work: use `docs/agents/claude_prompts.md`.
2. For batch codemods: use `scripts/codemods/replace_labs_with_provider.py` (dry-run -> patches).
3. For orchestrated PRs: use `scripts/automation/run_codmod_and_prs.sh` (supervised).
4. For SLSA attestation: use `.github/workflows/slsa-attest.yml` and `scripts/automation/run_slsa_for_modules.sh`.

Always attach artifacts produced (ruff/mypy logs, lane-guard run) to the PR and do not merge until a human signoff is present.
