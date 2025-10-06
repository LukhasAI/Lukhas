---
status: wip
type: documentation
---
Absolutely—here’s a tight,audits land” plan that turns results into shipped fixes without chaos.

1) Ingest → Merge → Plan (same day)

A. Drop the two audit outputs into the repo

mkdir -p reports/audit
# Save the auditors’ markdown as:
# reports/audit/strategic_findings.md
# reports/audit/neutral_findings.md

B. Merge them into a single action queue

tools/audit/merge_audits.py \
  --strategic reports/audit/strategic_findings.md \
  --neutral   reports/audit/neutral_findings.md \
  --out-dir   reports/audit/merged

# Optional: delta appendix (old vs new tag)
make audit-appendix OLD_TAG=audit-freeze-20250910T122620Z NEW_TAG=audit-freeze-20250910T143306Z

C. Create a planning PR (docs-only)
	•	Add:
	•	reports/audit/merged/action_queue.md (ranked list)
	•	reports/audit/merged/scoreboard.json
	•	reports/audit/merged/contradictions.md
	•	reports/audit/appendix_delta.md (if generated)
	•	Title: docs(audit): merged findings + ranked action queue
	•	Checklist (top 10 items from the queue) with owners from OWNERSHIP.json (or CODEOWNERS).

Definition of Ready for each item
	•	Has: file path(s) + exact code citations + risk level + “Fix Now/Later” + owner.

⸻

2) Shape the PR queue (48 hours)

A. Bucket the queue → tiny PRs
Map items in action_queue.md into these buckets (each bucket = a series of small PRs):
	1.	Lanes: remove cross-lane imports; add shims or quarantines.
	2.	MATRIZ contracts: fill/align AUDIT/NODE_CONTRACTS/*.json; add/repair golden traces.
	3.	API smoke: ensure /healthz + one trace fetch handler exist and are cited.
	4.	Security: SBOM wired in CI, secrets hooks sane, license allowlist.
	5.	Tests: stabilize Tier-1 reality tests; mark legacy xfail or quarantine.
	6.	Docs/Gov: sync LUKHAS_ARCHITECTURE_MASTER.json ↔ DEPENDENCY_MATRIX.json, refresh provenance.

B. Apply labels & owners
	•	Labels: lanes, matriz-contracts, api-smoke, security, tests, docs.
	•	Owners: auto-mention from AUDIT/OWNERSHIP.json or CODEOWNERS match.
	•	Milestone: Audit-Fix Wave 1.

C. Gate each PR with the right CI
	•	must pass: lane-guard, contracts-smoke, audit-validate, pre-commit.
	•	No “mega PRs”. Target < 300 LOC diff and one concern per PR.

D. Create the PRs fast (GitHub CLI example)

# Example: fix a cross-lane import
git checkout -b fix/lanes-core-colonies
# (apply the minimal code change)
git commit -m "fix(lanes): remove candidate import from lukhas/core/colonies/__init__.py"
gh pr create --title "fix(lanes): remove cross-lane import in colonies" \
  --body "Ref: action_queue.md item #3. Risk=Red. Evidence in reports/audit/strategic_findings.md." \
  --label lanes --assignee @owner-handle


⸻

3) Execute & Monitor (the following week)

A. Merge discipline
	•	Only merge if:
	•	✅ contracts-smoke green (Tier-1 still passes)
	•	✅ lane-guard green
	•	✅ audit-validate green (schemas & provenance)
	•	🟡 “Debt ratchet” unchanged or reduced

B. Nightly guardrails (already wired)
	•	SELF_HEALING_DISABLED=1 (read-only dashboard mode)
	•	Publish would-change reports; open a single chore(nightly): audit refresh PR.
	•	Fail nightly if schema validity < 100% or counts exceed ratchet baseline.

C. Update the scoreboard
	•	After each merge batch, re-run:

tools/audit/merge_audits.py \
  --strategic reports/audit/strategic_findings.md \
  --neutral   reports/audit/neutral_findings.md \
  --out-dir   reports/audit/merged

	•	Commit refreshed scoreboard.json so progress is visible.

D. Freeze a new tag when Red→Yellow or Yellow→Green flips

NEW_TAG="audit-freeze-$(date -u +%Y%m%dT%H%M%SZ)"
git tag -f "$NEW_TAG" && git push --tags || true


⸻

“Just give me the prompts”

Claude Code (bucketed PR factory)

/post.audit.queue
Read reports/audit/merged/action_queue.md. For the top 8 items:
1) Bucket them into {lanes, matriz-contracts, api-smoke, security, tests, docs}.
2) For each, create a new branch, apply the minimal change, and open a PR with:
   - Title: <type(scope): summary>
   - Body: cite the exact evidence block(s) and file paths; link to action_queue item.
   - Labels: bucket label; Milestone: Audit-Fix Wave 1; Assignee: owner from OWNERSHIP.
3) Ensure CI passes: lane-guard, contracts-smoke, audit-validate, pre-commit.
4) Keep each PR <300 LOC, single-concern.
Show a summary table of PRs opened.

Codex CLI (quick lanes fix template)

# replace FILE with the offending file from the audit
git checkout -b fix/lanes-$(basename FILE .py)
python - <<'PY'
p="FILE"
s=open(p).read()
s=s.replace("from candidate.", "# TODO[T4]: removed cross-lane import\n# from candidate.")
s=s.replace("import candidate", "# TODO[T4]: removed cross-lane import\n# import candidate")
open(p,"w").write(s)
PY
git commit -am "fix(lanes): remove cross-lane import in FILE"
gh pr create --title "fix(lanes): remove cross-lane import in FILE" \
  --body "Action queue item: <link>. Evidence cited in audit. Risk=Red." \
  --label lanes


⸻

“Done” criteria (per bucket)
	•	Lanes: zero lukhas → candidate imports; guard script remains green.
	•	MATRIZ contracts: all Tier-1 nodes have complete contracts + at least one golden trace each.
	•	API smoke: /healthz and one trace fetch route exist and are cited in code.
	•	Security: SBOM produced in CI; basic secrets checks run on stable lanes; license allowlist present.
	•	Tests: Tier-1 reality tests deterministic; legacy either passes or is quarantined/xfail.
	•	Docs/Gov: architecture master ↔ dependency matrix consistent; provenance updated.

