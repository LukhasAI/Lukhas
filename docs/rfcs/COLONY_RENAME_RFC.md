# Colony Rename RFC
**Status**: Pending Approval | **Created**: 2025-10-15 | **Track**: C (Copilot)

---

## 🎯 Executive Summary

Propose systematic renaming of "Colony" terminology to "Agent Network" across the LUKHAS codebase to improve semantic clarity, align with industry standards, and enhance discoverability.

**Scope**: ~50-100 files estimated  
**Risk**: MEDIUM (file moves, import updates, potential API surface changes)  
**Timeline**: 2-3 weeks (staged execution in batches)  
**Stakeholders**: All developers, API consumers, documentation maintainers

---

## 📋 Rationale

### 1. **Semantic Clarity**
- **Current**: "Colony" terminology is biologically-inspired but ambiguous
- **Proposed**: "Agent Network" is explicit, industry-standard, self-documenting
- **Benefit**: Reduces cognitive load for new developers and external contributors

### 2. **Industry Alignment**
- Multi-agent systems commonly use "network" terminology
- Aligns with consciousness/orchestration patterns (agent → network → system)
- Consistent with existing LUKHAS patterns (e.g., "orchestration", "bridge")

### 3. **Discoverability**
- "Agent Network" appears in search results, documentation, and API specs
- "Colony" requires contextual knowledge to understand intent
- Improves IDE autocomplete and code navigation

### 4. **Constellation Framework Integration**
- Fits naturally with Trinity Framework (⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian)
- "Agent Network" supports multi-agent orchestration patterns
- Enables clearer separation between agent coordination and colony algorithms

---

## 🔍 Current State Analysis

### Affected Components

Based on grep analysis, the following components use "colony" terminology:

#### **Core Files** (~20 files estimated)
- `governance/colony_memory_validator.py` → `governance/agent_network_memory_validator.py`
- `api/universal_language_api.py` (colony consensus endpoints)
- `symbolic/entropy_password_system.py` (_validate_with_colony methods)
- `symbolic/exchange/universal_exchange.py` (_validate_through_colony methods)

#### **API Endpoints**
- `/v1/colony/consensus` → `/v1/agent-network/consensus`
- `ColonyConsensusRequest` → `AgentNetworkConsensusRequest`
- `ColonyValidationResponse` → `AgentNetworkValidationResponse`

#### **Classes & Methods**
- `ColonyMemoryValidator` → `AgentNetworkMemoryValidator`
- `EnhancedReasoningColony` → `EnhancedReasoningAgentNetwork`
- `register_colony()` → `register_agent_network()`
- `_validate_in_colony()` → `_validate_in_agent_network()`

#### **Configuration & Documentation**
- README.md references
- API documentation
- Configuration files
- Test fixtures

---

## 📊 Impact Assessment

### **High Impact Areas**

1. **API Surface** ⚠️
   - Endpoint paths may change (requires versioning or deprecation)
   - Request/response models change (client SDK updates needed)
   - **Mitigation**: Provide backward compatibility aliases for 1-2 release cycles

2. **Import Chains** ⚠️
   - File moves require all import statements to update
   - Potential circular dependency issues if not staged correctly
   - **Mitigation**: Use staged batches (≤20 files per PR), validate with `make lane-guard`

3. **External Integrations** ⚠️
   - Third-party code may reference old names
   - Documentation/tutorials need updates
   - **Mitigation**: Deprecation warnings, migration guide, automated import rewriters

### **Medium Impact Areas**

1. **Testing Infrastructure**
   - Test fixtures and mocks need updates
   - Integration tests may hardcode old names
   - **Mitigation**: Update tests in same PR as code changes

2. **Internal Documentation**
   - Architecture docs, ADRs, inline comments
   - **Mitigation**: Bulk find/replace with manual review

### **Low Impact Areas**

1. **Logs & Metrics**
   - Old metric names may still appear in Prometheus
   - **Mitigation**: Maintain dual metrics during transition period

---

## 🚀 Execution Plan

### **Phase 1: Preparation** (Days 1-2)

**Goal**: Generate complete inventory and validate approach

1. **Generate Dry-Run CSV**
   ```bash
   python scripts/plan_colony_renames.py
   # Output: docs/audits/colony/colony_renames_20251015.csv
   ```

2. **Validate Inventory**
   - Review CSV for completeness
   - Identify API breakage risks
   - Document backward compatibility requirements

3. **Stakeholder Review**
   - Share RFC with maintainers
   - Collect feedback on API deprecation timeline
   - Finalize execution batches

**Deliverables**:
- ✅ This RFC document
- ✅ Complete rename inventory CSV
- ✅ Stakeholder approval

---

### **Phase 2: Staged Execution** (Weeks 1-2)

**Strategy**: Execute renames in dependency order (leaf nodes first)

#### **Batch 1: Internal Utilities** (Low Risk)
**Files**: ≤15
**Scope**: Private methods, internal helpers
**Examples**:
- `_validate_with_colony()` → `_validate_with_agent_network()`
- `_gather_colony_responses()` → `_gather_agent_network_responses()`

**PR Title**: `refactor(colony): batch 1 - internal utilities rename to agent network`

**Acceptance Criteria**:
- ✅ All tests passing
- ✅ No import errors
- ✅ Smoke tests clean

---

#### **Batch 2: Core Classes** (Medium Risk)
**Files**: ≤20
**Scope**: Public classes, no API surface changes
**Examples**:
- `ColonyMemoryValidator` → `AgentNetworkMemoryValidator`
- `ColonyValidationResponse` → `AgentNetworkValidationResponse`

**PR Title**: `refactor(colony): batch 2 - core classes rename to agent network`

**Acceptance Criteria**:
- ✅ Full test suite passing
- ✅ Lane boundaries validated (`make lane-guard`)
- ✅ Integration tests clean

---

#### **Batch 3: API Surface** (High Risk ⚠️)
**Files**: ≤10
**Scope**: Public API endpoints, SDK-breaking changes
**Examples**:
- `/v1/colony/consensus` → `/v1/agent-network/consensus`
- `ColonyConsensusRequest` → `AgentNetworkConsensusRequest`

**PR Title**: `refactor(api): batch 3 - colony endpoints rename to agent-network (BREAKING)`

**Backward Compatibility Strategy**:
1. **Dual Endpoints** (Recommended):
   ```python
   # New endpoint
   @app.post("/v1/agent-network/consensus")
   async def agent_network_consensus(...): ...
   
   # Deprecated alias (maintains old endpoint for 2 releases)
   @app.post("/v1/colony/consensus", deprecated=True)
   async def colony_consensus_deprecated(...):
       warnings.warn("Use /v1/agent-network/consensus", DeprecationWarning)
       return await agent_network_consensus(...)
   ```

2. **Request/Response Aliases**:
   ```python
   # Maintain old model names as aliases
   ColonyConsensusRequest = AgentNetworkConsensusRequest  # Deprecated
   ```

3. **Migration Guide**:
   - Document all API changes
   - Provide code examples
   - Include automated migration scripts

**Acceptance Criteria**:
- ✅ Both old and new endpoints functional
- ✅ Deprecation warnings logged
- ✅ Migration guide published
- ✅ SDK updates prepared

---

#### **Batch 4: Documentation & Configuration** (Low Risk)
**Files**: ≤30
**Scope**: README, docs, config files
**Examples**:
- Update README.md references
- Update API documentation
- Update configuration examples

**PR Title**: `docs(colony): batch 4 - documentation update for agent network rename`

**Acceptance Criteria**:
- ✅ All docs consistent
- ✅ No broken links
- ✅ Examples tested

---

### **Phase 3: Cleanup & Verification** (Week 3)

**Goal**: Remove deprecated code and validate complete transition

1. **Deprecation Removal** (After 2 Release Cycles)
   - Remove `/v1/colony/*` endpoints
   - Remove `Colony*` type aliases
   - Clean up migration code

2. **Final Verification**
   ```bash
   # No "colony" references in production code
   grep -r "colony" --include="*.py" lukhas/ core/ | \
     grep -v "# Historical" | \
     wc -l  # Expected: 0
   ```

3. **Post-Migration Audit**
   - Verify all imports resolved
   - Confirm API consumers migrated
   - Update CHANGELOG.md

**Deliverables**:
- ✅ Zero colony references in production code
- ✅ Deprecation sunset complete
- ✅ Migration guide archived

---

## 🧪 Testing Strategy

### **Per-Batch Testing**

1. **Unit Tests**
   ```bash
   pytest tests/unit/ -k "network or colony" -v
   ```

2. **Integration Tests**
   ```bash
   pytest tests/integration/ -v
   ```

3. **Smoke Tests**
   ```bash
   pytest tests/smoke/ -q
   ```

4. **Import Validation**
   ```bash
   make lane-guard      # Validate import boundaries
   make imports-guard   # Check circular dependencies
   ```

5. **API Contract Tests**
   ```bash
   # Verify both old and new endpoints during transition
   curl http://localhost:8000/v1/colony/consensus  # Should work with deprecation warning
   curl http://localhost:8000/v1/agent-network/consensus  # New endpoint
   ```

---

## 🔄 Rollback Plan

### **If Batch Fails**

1. **Git Revert**
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

2. **Reinstall Dependencies** (if needed)
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Verify System Health**
   ```bash
   make doctor
   pytest tests/smoke/ -q
   ```

### **If API Breakage Detected**

1. **Immediate Rollback**
   - Revert API changes
   - Restore old endpoints

2. **Extend Deprecation Period**
   - Keep dual endpoints longer
   - Notify API consumers

3. **Document Issues**
   - Create GitHub issues for affected integrations
   - Update migration guide with known issues

---

## 📅 Timeline & Milestones

| Phase | Duration | Milestone |
|-------|----------|-----------|
| **Phase 1: Preparation** | 2 days | RFC approved, CSV generated |
| **Batch 1: Internal Utilities** | 2 days | PR merged, tests passing |
| **Batch 2: Core Classes** | 3 days | PR merged, lane guards clean |
| **Batch 3: API Surface** | 5 days | PR merged, deprecation active |
| **Batch 4: Documentation** | 2 days | PR merged, docs updated |
| **Phase 3: Cleanup** | 3 days (post-2 releases) | Deprecation sunset |
| **Total** | ~2-3 weeks | Complete migration |

---

## ✅ Approval Checklist

### **Pre-Execution**

- [ ] RFC reviewed by maintainers
- [ ] Dry-run CSV generated and validated
- [ ] API deprecation timeline approved
- [ ] Stakeholder buy-in confirmed
- [ ] Test coverage verified (≥75%)

### **Per-Batch Approval**

- [ ] PR created with clear scope
- [ ] All tests passing (unit, integration, smoke)
- [ ] Import boundaries validated (`make lane-guard`)
- [ ] Documentation updated
- [ ] Reviewer approval obtained

### **Post-Execution**

- [ ] Zero colony references in production code
- [ ] API consumers migrated successfully
- [ ] CHANGELOG.md updated
- [ ] Deprecation sunset confirmed

---

## 📚 References

### **Tools & Scripts**

- **Rename Planner**: `scripts/plan_colony_renames.py`
- **Dry-Run Output**: `docs/audits/colony/colony_renames_<timestamp>.csv`
- **Import Validator**: `make lane-guard`, `make imports-guard`

### **Related Documents**

- **Parallel Execution Plan**: `docs/plans/PARALLEL_AGENT_EXECUTION_PLAN.md`
- **Constellation Framework**: `branding/constellation/`
- **API Documentation**: `docs/api/`
- **Testing Guide**: `docs/testing/`

### **External References**

- Multi-Agent System Naming Conventions
- RESTful API Deprecation Best Practices
- Semantic Versioning Guidelines (semver.org)

---

## 🔗 Next Steps (Post-Approval)

1. **Generate Dry-Run CSV**
   ```bash
   python scripts/plan_colony_renames.py
   ```

2. **Create Batch 1 Branch**
   ```bash
   git checkout -b refactor/colony-batch1-internal
   ```

3. **Execute First Batch**
   - Follow execution plan
   - Create PR with T4 commit format
   - Wait for approval

4. **Iterate Through Batches**
   - Complete all 4 batches
   - Monitor for regressions
   - Collect stakeholder feedback

---

## 📞 Contact & Questions

**RFC Owner**: Copilot (Track C)  
**Status**: Pending Stakeholder Approval  
**Discussion**: Create GitHub issue for questions/feedback

---

**Last Updated**: 2025-10-15  
**Version**: 1.0  
**Status**: DRAFT - Awaiting Approval
