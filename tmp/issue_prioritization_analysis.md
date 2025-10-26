# GitHub Issues Prioritization Analysis

**Analysis Date**: 2025-10-26
**Total Open Issues**: 12
**Categorized by**: Priority, Effort, Impact

---

## 📊 **Issue Overview**

### By Priority Tier

**🔴 P0 - Critical (1 issue)**
- #399: pip CVE-2025-8869 (Awaiting fix release)

**🟠 P1 - High (3 issues)**
- #490: MATRIZ-007 PQC Migration (5 engineer-days)
- #502: CI Infrastructure Fixes (2-3 hours)
- #364: Test Suite Cleanup (4 weeks)

**🟡 P2 - Medium (4 issues)**
- #491: Auth tests triage (investigation needed)
- #492: PQC runner provisioning (partially complete via WP-2)
- #493: TEMP-STUB production protection (policy already in place)
- #494: No-Op guard observation (48-72h monitoring)

**🟢 P3 - Low (4 issues)**
- #360: Security posture alert (SBOM coverage)
- #436: Manifest coverage (363 manifests needed)
- #388: Lint E402/E70x slice 1 (adapters)
- #389: Lint E402/E70x slice 2 (reliability)

---

## 🎯 **Quick Wins (Can Complete Today)**

### 1. Issue #502: CI Infrastructure Fixes ⚡
**Effort**: 1-2 hours
**Impact**: Unblocks CI checks for future PRs
**Status**: Ready to implement

**Tasks**:
- Fix registry-smoke script permissions (use inline bash)
- Fix PQC Docker OpenSSL detection (set OPENSSL_ROOT_DIR)
- Both fixes have proposed solutions in issue body

**Blocker Status**: None - ready to execute

---

### 2. Issue #493: TEMP-STUB Production Protection ✅
**Effort**: 15 minutes (documentation update)
**Impact**: Close issue (already implemented)
**Status**: **ALREADY COMPLETE**

**Evidence**:
- ✅ `temp-stub-guard.yml` workflow implemented (from TG-002)
- ✅ `matriz-007-guard.yml` workflow blocks promotion
- ✅ Branch protection configured with required checks

**Action**: Document completion and close issue

---

### 3. Issue #492: PQC Runner Provisioning ✅
**Effort**: 15 minutes (documentation update)
**Impact**: Close issue (partially complete)
**Status**: **PARTIALLY COMPLETE** (WP-2 delivered)

**Evidence**:
- ✅ PQC Docker runner implemented (.github/docker/pqc-runner.Dockerfile)
- ✅ CI matrix integration in pqc-sign-verify.yml
- ✅ Performance benchmarking (pqc-bench --json)

**Remaining**: Production deployment instructions
**Action**: Document completion status and update issue

---

### 4. Issue #494: No-Op Guard Observation ⏱️
**Effort**: Monitor for 24-48h more
**Impact**: Validate guard effectiveness
**Status**: Observation period in progress

**Action**: Check false positive rate, document findings

---

## 🔧 **Medium Complexity (1-2 Days)**

### 5. Issue #491: Auth Tests Triage 🔍
**Effort**: 4-6 hours (investigation + fixes)
**Impact**: Clean up pre-existing test failures
**Status**: Requires investigation

**Approach**:
1. Run auth tests locally to reproduce failures
2. Categorize by failure type (import, assertion, timeout)
3. Fix or document expected behavior
4. Update tests to match current API

---

## 📚 **Complex Long-Term Issues**

### 6. Issue #490: MATRIZ-007 PQC Migration 🔐
**Effort**: 5 engineer-days (1 week)
**Impact**: Production-ready quantum-resistant signatures
**Status**: Week 1-6 roadmap defined

**Dependencies**:
- liboqs-python or pqcrypto library
- Key generation/rotation procedures
- Security audit

**Approach**: Follow 6-week plan from issue #490 body

---

### 7. Issue #364: Test Suite Cleanup 🧹
**Effort**: 4 weeks (66 broken tests)
**Impact**: Improve test reliability
**Status**: Requires systematic approach

**Breakdown**:
- Week 1: RecursionError fixes (8 tests) - Priority 1
- Week 2: AttributeError fixes (15 tests) - Priority 2
- Week 3: TypeError fixes (20 tests) - Priority 3
- Week 4: ImportError fixes (23 tests) - Priority 4

**Recommendation**: Create sub-issues for each week

---

### 8. Issue #436: Manifest Coverage 📦
**Effort**: 2-3 hours (automation)
**Impact**: 99% artifact coverage
**Status**: Ready for automation

**Approach**:
- Use existing scripts to find 363 orphan packages
- Generate manifests with --star-from-rules
- Validate and commit in batches

---

### 9. Issue #360: Security Posture (SBOM) 🛡️
**Effort**: 1 week (102 missing SBOMs)
**Impact**: Improve supply chain security
**Status**: Requires SBOM generation strategy

**Approach**:
- Choose SBOM format (SPDX, CycloneDX)
- Generate SBOMs for all packages
- Integrate into CI pipeline

---

### 10-12. Issues #388, #389: Lint Cleanup 🧽
**Effort**: 2-3 hours each
**Impact**: Code quality improvements
**Status**: Ready for systematic cleanup

**Approach**: Follow slice-by-slice refactoring (≤20 files each)

---

## 🚀 **Recommended Action Plan**

### **Today (High ROI, Low Effort)**

1. ✅ **Fix CI Infrastructure** (#502) - 1-2 hours
   - Unblocks future PR checks
   - Clear solution already proposed

2. ✅ **Close Completed Issues** (#493, #492) - 30 minutes
   - Document what's already done
   - Reduce backlog noise

3. 🔍 **No-Op Guard Status Update** (#494) - 15 minutes
   - Document observation results
   - Close or extend monitoring period

**Time**: 2-3 hours total
**Impact**: 4 issues resolved (33% reduction)

---

### **This Week (Medium Priority)**

4. 🔍 **Auth Tests Triage** (#491) - 4-6 hours
   - Reproduce and categorize failures
   - Fix what's fixable, document what's not

5. 📦 **Manifest Coverage Automation** (#436) - 2-3 hours
   - Generate 363 missing manifests
   - Achieve 99% coverage target

**Time**: 6-9 hours total
**Impact**: 2 more issues resolved

---

### **Next 2 Weeks (Complex Work)**

6. 🧹 **Test Suite Cleanup Phase 1** (#364) - 1 week
   - Fix Priority 1 (RecursionError) tests
   - Document approach for remaining priorities

7. 🔐 **MATRIZ-007 Week 1** (#490) - Start if PQC is priority
   - Set up development environment
   - Implement Dilithium2 integration
   - Create key management procedures

---

### **Backlog (Lower Priority)**

8. 🛡️ **Security Posture** (#360) - SBOM generation strategy
9. 🧽 **Lint Cleanup** (#388, #389) - E402/E70x refactoring
10. 🔴 **pip CVE** (#399) - Monitor for pip 25.3 release

---

## 📋 **Immediate Next Steps**

**Recommendation**: Start with **Issue #502 (CI fixes)** as it's:
- ✅ Well-defined (clear solutions provided)
- ✅ High impact (unblocks CI for all future PRs)
- ✅ Low effort (1-2 hours)
- ✅ No dependencies

**Would you like me to:**
1. **Fix CI infrastructure** (#502) - registry-smoke + PQC Docker?
2. **Close completed issues** (#493, #492) - document and clean up?
3. **Investigate auth tests** (#491) - reproduce and triage?
4. **Generate manifests** (#436) - achieve 99% coverage?
5. **Something else** - which issue would you prioritize?

---

**Summary Statistics**:
- **Quick Wins**: 4 issues (can complete today)
- **Medium Complexity**: 1 issue (1-2 days)
- **Long-Term**: 7 issues (1-4 weeks each)
- **Total Backlog**: 12 → Target 8 after today's work
