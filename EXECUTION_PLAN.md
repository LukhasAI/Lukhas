# LUKHAS Agent Execution Plan

**Generated**: 2025-10-18
**Status**: Planning Phase
**Objective**: Systematic execution of manifest enhancement, star promotion, and strategic alignment tasks

---

## 📋 Executive Summary

This plan organizes 17 high-value tasks across 4 agent domains into 6 sequential phases. It balances **parallel execution** (low-risk, independent tasks) with **sequential dependencies** (structural changes requiring upstream completion).

**Key Metrics**:
- **780 manifests** to regenerate with star assignments
- **99% artifact coverage** target
- **T1 enforcement** across all critical modules
- **OpenAPI compatibility** for ecosystem integration

---

## 🎯 Phase-Based Execution Strategy

### 🔹 Phase 1: Documentation & Artifact Enhancement (PARALLEL SAFE)
**Timeline**: Days 1-3
**Risk**: Low
**Dependencies**: None

#### Claude Code Tasks
- [ ] **Enhance `docs/lukhas_context/*.md` files**
  - Add YAML front matter
  - Link to contracts
  - Add doc cross-links
  - Priority: Medium

- [ ] **Enrich `docs/CONSTELLATION_TOP.md`**
  - Update 8-star system documentation
  - Add current star assignments
  - Priority: Medium

- [ ] **Artifact Audit (99% coverage push)**
  - Scan for orphan modules (no manifest)
  - Generate missing manifests
  - Priority: High

- [ ] **Add schema field docstrings**
  - Enhance validator error messages
  - Add descriptions to all required fields
  - Priority: Low

#### GitHub Copilot / Codex Tasks
- [ ] **Write test coverage bots for context files**
  - Scan for orphan modules
  - Check missing badges
  - Priority: Low

- [ ] **Add docstrings to all scripts**
  - Document CLI tools
  - Document helper scripts
  - Priority: Low

**Output**: Enhanced documentation, improved discoverability, better error messages

---

### 🔹 Phase 2: API Manifest Tiering & Contract Validation (PARALLEL SAFE)
**Timeline**: Days 3-5
**Risk**: Low
**Dependencies**: None (runs parallel to Phase 1)

#### API & Matriz Integration Tasks
- [ ] **`api/` package manifest tiering**
  - Assign star ratings to API modules
  - Document endpoint coverage
  - Priority: High

- [ ] **Public API docs scaffolding (OpenAPI stubs)**
  - Create OpenAPI schema templates
  - Map manifests to API specs
  - Priority: Medium

- [ ] **Contracts registry hardening**
  - Validate all contract references
  - Fix broken links
  - Ensure T1 modules have contracts
  - Priority: High

#### DevOps Tasks
- [ ] **`check_contract_refs.py` robustness pass**
  - Handle edge cases
  - Improve error reporting
  - Add caching
  - Priority: Medium

**Output**: API-ready manifests, validated contracts, OpenAPI foundation

---

### 🔹 Phase 3: Star Promotion Finalization (SEQUENTIAL - BLOCKS PHASE 4)
**Timeline**: Days 5-7
**Risk**: Medium
**Dependencies**: Must complete before manifest regeneration

#### Claude Code Tasks
- [ ] **Patch manifest generator for `--star-from-rules` flag**
  - Read from `configs/star_rules.json`
  - Override Supporting assignments
  - Respect confidence thresholds
  - Priority: High
  - **Status**: BLOCKING

- [ ] **Validate star assignment rules**
  - Review `configs/star_rules.json`
  - Cross-check with architectural intent
  - Get stakeholder approval
  - Priority: High

#### Strategic Alignment Tasks
- [ ] **Audit alignment to OpenAI system cards**
  - Map LUKHAS capabilities to OpenAI ecosystem
  - Identify integration opportunities
  - Priority: High

- [ ] **Design Dream/Drift/Lukhas_ID as ecosystem APIs**
  - Define external interfaces
  - Create integration contracts
  - Priority: High

**Output**: Finalized star rules, validated promotions, strategic alignment framework

---

### 🔹 Phase 4: Manifest Regeneration & Constellation Update (DEPENDS ON PHASE 3)
**Timeline**: Days 7-9
**Risk**: Medium
**Dependencies**: Phase 3 star rules MUST be complete

#### Claude Code Tasks
- [ ] **Regenerate 780 manifests with updated star assignments**
  - Run with `--star-from-rules` flag
  - Use `--write-context` to update lukhas_context.md
  - Validate all outputs
  - Priority: High
  - **Depends on**: Phase 3 completion

- [ ] **Update Constellation summary dashboard**
  - Refresh star distribution stats
  - Update tier counts
  - Generate new visualizations
  - Priority: Medium

- [ ] **Manifest stats dashboard refactor**
  - Add star promotion metrics
  - Track coverage trends
  - Priority: Medium

**Output**: 780 regenerated manifests, updated context files, refreshed dashboards

---

### 🔹 Phase 5: Directory Restructuring & CI Refactor (DEPENDS ON PHASE 4)
**Timeline**: Days 9-12
**Risk**: High
**Dependencies**: All manifests validated, CI ready for path updates

#### GitHub Copilot / Codex Tasks
- [ ] **Refactor file structure: elevate flagship modules**
  - Promote validated `lukhas/` subdirs to root
  - Candidates: drift, vivox, bio, dream
  - Priority: Medium
  - **Depends on**: Manifest validation complete

- [ ] **Update all manifest paths**
  - Rewrite paths in manifests
  - Update `lukhas_context.md` references
  - Priority: High

#### DevOps Tasks
- [ ] **`.github/workflows/*` CI optimizations**
  - Update paths in workflows
  - Add new validation rules
  - Priority: High

- [ ] **Integrate `--check-links`, `--star-promotions`, `--t1-owners` into CI**
  - Fail on broken links
  - Fail on orphan T1s
  - Fail on unreviewed promotions
  - Priority: High

- [ ] **T1 enforcement and golden manifest CI rules**
  - Enforce OWNERS.toml for T1s
  - Validate contract links
  - Priority: High

- [ ] **`OWNERS.toml` enrichment**
  - Add owners to all T1 modules
  - Validate GitHub usernames
  - Priority: Medium

**Output**: Cleaner directory structure, hardened CI, enforced governance

---

### 🔹 Phase 6: Release Freeze & Final Polish (DEPENDS ON PHASE 5)
**Timeline**: Days 12-15
**Risk**: Low
**Dependencies**: All structural changes complete

#### DevOps Tasks
- [ ] **Build deployment-ready release pipeline**
  - Add Makefile targets: `release-freeze`, `release-tag`, `pre-release-validate`
  - Document release process
  - Priority: Medium

- [ ] **Enable OpenAPI-compatible stub generation**
  - CLI to convert manifests → OpenAPI
  - Integrate with API Gateway plans
  - Priority: Medium

#### Strategic Alignment Tasks
- [ ] **Create `README.roadmap.md` for Lukhas public modules**
  - Document OpenAI complementarity
  - List enabled verticals
  - Priority: Medium

#### Constellation Tasks
- [ ] **Constellation dashboard & analytics polish**
  - Final metrics review
  - Visual polish
  - Public-ready presentation
  - Priority: Medium

**Output**: Release-ready codebase, public documentation, analytics dashboard

---

## 🚦 Parallel Execution Matrix

### ✅ Can Run in Parallel

| Phase | Agent Domain              | Task Count | Risk  |
|-------|---------------------------|------------|-------|
| 1     | Claude Code (Docs)        | 4          | Low   |
| 1     | GitHub Copilot (Coverage) | 2          | Low   |
| 2     | API Integration           | 3          | Low   |
| 2     | DevOps (Validation)       | 1          | Low   |

**Total Parallel Tasks**: 10 tasks (Days 1-5)

### ⚠️ Must Run Sequentially

| Phase | Blocking Task                      | Unlocks            |
|-------|------------------------------------|--------------------|
| 3     | Star promotion finalization        | Phase 4            |
| 4     | Manifest regeneration              | Phase 5            |
| 5     | Directory restructuring + CI       | Phase 6            |
| 6     | Release freeze                     | Public deployment  |

---

## 📊 Success Metrics

### Completion Criteria (Per Phase)

**Phase 1**:
- ✅ All `lukhas_context.md` files have YAML front matter
- ✅ 99% artifact coverage achieved
- ✅ Schema validation errors include field descriptions

**Phase 2**:
- ✅ All API modules have star ratings
- ✅ OpenAPI stubs generated for 5+ flagship APIs
- ✅ 0 broken contract references

**Phase 3**:
- ✅ `configs/star_rules.json` validated and approved
- ✅ `--star-from-rules` flag implemented and tested
- ✅ Strategic alignment document approved

**Phase 4**:
- ✅ 780 manifests regenerated successfully
- ✅ Constellation dashboard updated with new stats
- ✅ No validation errors in regenerated manifests

**Phase 5**:
- ✅ Directory structure refactored (4+ modules promoted)
- ✅ CI passes with new path structure
- ✅ T1 enforcement rules active in CI

**Phase 6**:
- ✅ Release pipeline Makefile targets functional
- ✅ OpenAPI CLI tool operational
- ✅ `README.roadmap.md` published

---

## 🎯 High-ROI Quick Wins (Start Immediately)

These tasks deliver maximum value with minimal risk:

1. **Artifact audit (99% coverage)** - Phase 1, Claude Code
2. **API manifest tiering** - Phase 2, API Integration
3. **Contract validation** - Phase 2, DevOps
4. **Star promotion finalization** - Phase 3, Claude Code (CRITICAL PATH)

---

## 🔧 Recommended Agent Assignment

| Agent Type                | Primary Phases | Workload |
|---------------------------|----------------|----------|
| Claude Code               | 1, 3, 4        | 45%      |
| GitHub Copilot / Codex    | 1, 5           | 25%      |
| DevOps Agents             | 2, 5, 6        | 20%      |
| Strategic Alignment (0.01%) | 3, 6         | 10%      |

---

## 📅 Timeline Summary

| Week | Phases       | Milestones                              |
|------|--------------|------------------------------------------|
| 1    | 1-2          | Docs enhanced, API tiering complete     |
| 2    | 3-4          | Star rules finalized, manifests regen'd |
| 3    | 5-6          | Structure refactored, release ready     |

**Total Duration**: ~15 days (3 weeks with buffer)

---

## 🚨 Risk Mitigation

### High-Risk Tasks
1. **Directory restructuring** (Phase 5)
   - **Mitigation**: Full test suite run before/after, git branch isolation

2. **Manifest regeneration** (Phase 4)
   - **Mitigation**: Backup all manifests, dry-run first, incremental validation

3. **CI path updates** (Phase 5)
   - **Mitigation**: Test in feature branch, staged rollout

### Rollback Strategy
- All phases use feature branches
- Git tags before each phase
- Automated test gates prevent bad merges

---

## 📝 Next Steps

1. **Review and approve this plan** with stakeholders
2. **Assign agent teams** to phases
3. **Create feature branches** for each phase
4. **Start Phase 1 tasks immediately** (parallel safe)
5. **Daily standups** to track progress

---

## 📚 Reference Documents

- **Agent TODO Source**: `lukhas_agent_todos.json`
- **Manifest Schema**: `docs/schemas/manifest_schema.json`
- **Star Rules Config**: `configs/star_rules.json`
- **Constellation Docs**: `docs/CONSTELLATION_TOP.md`
- **CI Workflows**: `.github/workflows/`

---

**Plan Status**: ✅ Ready for Execution
**Last Updated**: 2025-10-18
**Owner**: LUKHAS Core Team
