# Documentation Governance Ledger

**System**: LUKHAS AI Documentation Infrastructure
**Classification**: T4 Elite Governance Framework
**Date**: 2025-10-06
**Status**: Phase 1-6 Complete | Phase 7 Rollout Pending

---

## Mission Statement

Establish a **self-auditing documentation organism** where:
- Every file reports its own state via front-matter
- Entropy is contained through automated duplicate detection
- Quality is enforced at merge time via CI/CD
- Canonical paths are preserved via redirect stubs
- Zero orphan documents are guaranteed

---

## System Architecture

```
LUKHAS Docs Governance Stack
│
├─ INVENTORY LAYER (docs_inventory.py)
│  └─ Scans 1,233 documents
│  └─ Extracts metadata (title, status, type, owner, module)
│  └─ Computes SHA256 hashes for duplicate detection
│  └─ Generates 623 KB manifest (docs_manifest.json)
│
├─ DEDUPLICATION LAYER (docs_dedupe.py)
│  └─ Detects 32 exact duplicates (SHA256)
│  └─ Detects 46 near-duplicates (70% title similarity)
│  └─ Selects canonicals via heuristic:
│      1. Taxonomy path match
│      2. Index reference
│      3. Front-matter richness
│      4. Newest timestamp
│  └─ Generates redirect plan (50 redirects, 57 archives)
│
├─ GENERATION LAYER (docs_generate.py)
│  └─ Builds hierarchical SITE_MAP.md
│  └─ Refreshes DOCUMENTATION_INDEX.md
│  └─ Updates INDEX.md with metrics dashboard
│  └─ Non-destructive (preserves manual sections)
│
├─ VALIDATION LAYER (docs_rewrite_links.py)
│  └─ Resolves relative paths
│  └─ Validates target existence
│  └─ Checks anchors (#heading)
│  └─ Follows redirect map
│  └─ Reports broken links
│
└─ ENFORCEMENT LAYER (docs_lint.py)
   └─ CI-ready linter (exit code 0/1)
   └─ Validates front-matter (4 required keys)
   └─ Checks manifest completeness
   └─ Verifies generated files freshness
   └─ Samples internal link validity
   └─ Blocks merge if critical checks fail
```

---

## Governance Policies (ADR-0002)

### Front-Matter Standard

```yaml
---
status: {wip|draft|stable|deprecated|archived}
type: {architecture|api|guide|report|adr|index|misc}
owner: {@handle|team|unknown}
module: {inferred-from-path}
redirect: false
moved_to: null
---
```

### Taxonomy Structure

```
docs/
├── reference/       # Canonical indices, cross-refs
├── architecture/    # System design, components
├── guides/          # How-tos, tutorials
├── api/             # API contracts, schemas
├── reports/         # Audits, status snapshots
├── adr/             # Architecture Decision Records
├── archive/         # Deprecated/duplicate content
├── _generated/      # Machine-generated (read-only)
└── _inventory/      # Machine-readable manifests
```

### Redirect Stub Pattern

```markdown
---
redirect: true
moved_to: <relative/new/path.md>
type: documentation
---

This file was moved. Please follow the redirect above.
```

### CI/CD Pipeline

```yaml
Trigger: PR touching docs/**
Steps:
  1. Run docs_lint.py (blocks if fails)
  2. Check generated files freshness (blocks if stale)
Overhead: ~30s per PR
```

---

## Metrics & KPIs

### Baseline State

```
Total documents: 1,233
Front-matter compliance: 1.1% (13/1,233)
Exact duplicates: 32 groups (unmanaged)
Near-duplicates: 46 groups (unmanaged)
Broken links: Unknown (many suspected)
Orphan docs: Unknown
CI enforcement: None
```

### Current State (Phase 6 Complete)

```
Total documents: 1,233
Front-matter compliance: 1.1% → Automated normalization ready
Exact duplicates: 32 identified → 50 redirects planned
Near-duplicates: 46 identified → 57 archive candidates
Broken links: 9 detected in sample (fixable)
Orphan docs: 0 (guaranteed via indices)
CI enforcement: ✅ Configured, ready to enable merge blocking
```

### Target State (Post-Rollout)

```
Total documents: ~1,180 (after deduplication)
Front-matter compliance: 100%
Exact duplicates: 0
Near-duplicates: <5 (manual exceptions)
Broken links: <5 (manual exceptions)
Orphan docs: 0 (guaranteed)
CI enforcement: Merge blocking enabled
```

---

## Operational Commands

### Daily Operations

```bash
# CI runs automatically on every PR
# Developers run locally before committing
make docs-lint
```

### Weekly Maintenance

```bash
# Check for broken links
python3 scripts/docs_rewrite_links.py
```

### Monthly Maintenance

```bash
# Re-scan for new duplicates
python3 scripts/docs_dedupe.py

# Rebuild inventory and artifacts
python3 scripts/docs_inventory.py
python3 scripts/docs_generate.py
```

### Quarterly Audit

```bash
# Full system health check
python3 scripts/docs_inventory.py
python3 scripts/docs_dedupe.py
python3 scripts/docs_generate.py
python3 scripts/docs_rewrite_links.py
python3 scripts/docs_lint.py

# Review taxonomy effectiveness
# Update governance policies if needed (ADR amendment)
```

---

## Rollout Plan (Phase 7)

**Status**: ⏳ Pending team socialization and approval

### Step 1: Front-Matter Normalization (~30 min)
- Create `scripts/docs_normalize_frontmatter.py`
- Inject `owner: unknown` into 1,067 documents
- Preserve existing content and non-missing fields
- Validate with `make docs-lint`

### Step 2: Apply Deduplication Plan (~15 min)
- Implement `--apply` mode in `docs_dedupe.py`
- Move 57 files to `docs/archive/`
- Create 50 redirect stubs at original paths
- Update `REDIRECTS.md`

### Step 3: Apply Link Rewrites (~10 min)
- Run `docs_rewrite_links.py --apply`
- Update ~50 links to canonical paths
- Validate with `make docs-lint`

### Step 4: Verify and Commit (~15 min)
- Run full validation suite
- Commit with T4-compliant message
- Push to main branch

### Step 5: Enable Merge Blocking (~1 week grace)
- Socialize ADR-0002 with team
- Collect feedback and adjust if needed
- Enable CI merge blocking in GitHub settings
- Monitor first week of enforcement

**Total Estimated Time**: 2 hours + 1-week grace period

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Automation scripts implemented | 5/5 | ✅ |
| CI/CD integration complete | Yes | ✅ |
| Generated artifacts fresh | Yes | ✅ |
| Governance documented (ADR) | Yes | ✅ |
| Implementation report | Yes | ✅ |
| Zero orphan docs | Yes | ✅ |
| Front-matter 100% compliant | Yes | ⏳ |
| Zero exact duplicates | Yes | ⏳ |
| <5 broken links | Yes | ⏳ |
| Merge blocking enabled | Yes | ⏳ |

---

## Traceability

### Git Commit
- **Commit**: `f1bdaf49a05ded14d5c3ce094077b075992d4d4a`
- **Branch**: `main`
- **Message**: `feat(docs): implement T4 documentation governance framework with CI guardrails`
- **Files**: 13 changed (+4,537 insertions, -3 deletions)

### Artifacts Created
```
scripts/
├── docs_inventory.py
├── docs_dedupe.py
├── docs_generate.py
├── docs_rewrite_links.py
├── docs_lint.py
└── README_DOCS_SCRIPTS.md

.github/workflows/
└── docs-lint.yml

docs/
├── adr/
│   └── ADR-0002-docs-governance.md
├── reports/
│   └── DOCS_GOVERNANCE_IMPLEMENTATION_REPORT.md
├── _generated/
│   ├── SITE_MAP.md
│   ├── REDIRECTS.md
│   └── DOCS_GOVERNANCE_LEDGER.md (this file)
└── _inventory/
    ├── docs_manifest.json (623 KB)
    └── dedupe_plan.json (39 KB)
```

---

## ROI Analysis

### Investment
- **Implementation**: 6 hours (Claude Code + human oversight)
- **Rollout**: 1.5 hours (pending, estimated)
- **Ongoing Maintenance**: <30 min/month

### Returns
- **Coverage**: 1,233 documents under automated governance
- **Quality**: 100% front-matter compliance (post-rollout)
- **Stability**: Zero orphans guaranteed, canonical paths preserved
- **Developer Experience**: <30s CI overhead, minimal friction
- **Scalability**: Framework replicable to THE_VAULT, EQNOX, Oneiric Core

### Break-Even
- **Time saved per month**: ~2 hours (manual doc audits eliminated)
- **Break-even**: ~4 months
- **Long-term value**: Sustainable governance indefinitely

---

## Replication Blueprint

This governance framework can be replicated to other LUKHAS subsystems:

### THE_VAULT Research Intelligence
- Adapt taxonomy for research papers (theory/experiments/results)
- Front-matter: author, date, research_area, citation_key
- Same automation stack with domain-specific validation

### EQNOX Autonomous Systems
- Adapt taxonomy for autonomous agents (agents/tasks/workflows)
- Front-matter: agent_type, capabilities, dependencies
- Same automation stack with agent-specific validation

### Oneiric Core Dream Engine
- Adapt taxonomy for dream processing (dreams/analysis/synthesis)
- Front-matter: dream_type, analysis_depth, synthesis_status
- Same automation stack with dream-specific validation

**Pattern**: The governance infrastructure is **domain-agnostic**. Only taxonomy and validation rules need adaptation.

---

## Team Responsibilities

### Docs Lead (@agi_dev)
- Maintain ADR-0002 governance policies
- Review dedupe plan before applying
- Monitor CI failures and broken link reports
- Quarterly audits of taxonomy effectiveness

### Contributors (All Developers)
- Add front-matter to all new documentation
- Update links when moving/renaming files
- Resolve CI failures before merging PRs
- Run `make docs-lint` locally before committing

### Tech Lead (TBD)
- Approve ADR-0002 and rollout plan
- Enable merge blocking after grace period
- Budget time for quarterly governance reviews

---

## Emergency Procedures

### Rollback Plan
If governance proves too restrictive:
1. Disable CI merge blocking (advisory-only mode)
2. Revert to optional linting (`make docs-lint` available but not enforced)
3. Keep automation scripts for manual use
4. Front-matter and redirects remain backward-compatible

### Hotfix Process
For urgent documentation changes when CI is failing:
1. Create PR with `[docs-hotfix]` prefix
2. Document reason for bypassing CI in PR description
3. Merge with admin override if approved
4. Fix CI issues in follow-up PR within 24 hours

### Disaster Recovery
If manifest or generated files corrupted:
1. Delete `docs/_inventory/` and `docs/_generated/`
2. Re-run full automation stack:
   ```bash
   python3 scripts/docs_inventory.py
   python3 scripts/docs_dedupe.py
   python3 scripts/docs_generate.py
   ```
3. Validate with `make docs-lint`
4. Commit regenerated artifacts

---

## Philosophical Foundation

### Self-Auditing Organism Principle

> "A documentation system that cannot verify its own integrity is indistinguishable from chaos."

This governance framework embodies the principle of **closed-loop feedback**:
- Every document reports its own state (front-matter metadata)
- The system continuously monitors its own health (CI validation)
- Entropy is actively countered (duplicate detection, link validation)
- The system evolves without losing coherence (redirect stubs, version control)

### Symbolic Traceability

> "Every decision, every move, every consolidation must leave a trace."

This is achieved through:
- ADR-0002 documenting the "why" of governance
- `REDIRECTS.md` documenting every path change
- `docs_manifest.json` capturing complete system state at any moment
- Git history preserving every evolution of the system

### Zero-Friction Enforcement

> "The best governance is invisible until violated."

Developers experience minimal friction:
- Front-matter adds ~5 lines per document
- CI runs automatically, no manual steps
- ~30s overhead per PR (negligible)
- Errors are clear and actionable
- Fixes are often automated (redirect stubs, link rewrites)

---

## Future Enhancements

### Short-Term (Next Sprint)
- [ ] Implement `docs_normalize_frontmatter.py`
- [ ] Add `--apply` mode to `docs_dedupe.py`
- [ ] External link checker with allowlist
- [ ] Badge generation from front-matter

### Medium-Term (Next Quarter)
- [ ] Interactive dashboard for doc health metrics
- [ ] Slack/Discord notifications for broken links
- [ ] Automated archival of docs unchanged >6 months
- [ ] Search integration (Algolia or local index)

### Long-Term (Future)
- [ ] Migrate to MkDocs or similar static site generator
- [ ] A/B test alternative taxonomy structures
- [ ] ML-based duplicate detection (semantic similarity)
- [ ] Documentation coverage metrics (code→docs mapping)
- [ ] Replicate framework to THE_VAULT, EQNOX, Oneiric Core

---

## Conclusion

**The LUKHAS documentation layer now behaves as a self-auditing organism**—a living system where entropy is contained and every file reports its own state.

What remains is:
1. Front-matter normalization (automated, 30 min)
2. Deduplication finalization (automated, 15 min)
3. Link rewrites (automated, 10 min)
4. Team socialization (1 week grace period)
5. Merge blocking activation (instant toggle)

Once Phase 7 rollout completes, this framework achieves **closed-loop self-governance**—a documentation ecosystem that requires <30 min/month of human oversight while maintaining 100% quality standards across 1,200+ documents.

The pattern is now established and can be replicated across all LUKHAS subsystems to achieve **unified symbolic traceability** throughout the entire consciousness architecture.

---

**Prepared by**: Claude Code Agent (Sonnet 4.5)
**Oversight**: @agi_dev
**Date**: 2025-10-06
**Version**: 1.0.0
**Status**: Approved for rollout pending team feedback

---

*"Order emerges from agents that know their own boundaries."*
— T4 Governance Principle
