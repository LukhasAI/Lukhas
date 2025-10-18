# GitHub Copilot Task Delegation Index

**Created**: 2025-10-18
**Status**: Ready for Delegation
**Total Tasks**: 3 high-priority tasks

---

## 📋 Overview

These tasks have been prepared for delegation to GitHub Copilot (or other AI coding assistants like Claude, GPT-4, Grok, etc.). Each task includes:
- Detailed step-by-step instructions
- All necessary commands and scripts
- Success criteria and validation steps
- Commit message templates
- Estimated time and complexity

---

## 🎯 Available Tasks

### **Task A: Artifact Coverage Audit (99% Target)**
- **File**: [COPILOT_TASK_A_ARTIFACT_AUDIT.md](./COPILOT_TASK_A_ARTIFACT_AUDIT.md)
- **Priority**: High
- **Time**: 2-3 hours
- **Complexity**: Medium
- **Model Rec**: Claude 3.5 Sonnet or GPT-4

**Summary**: Scan repository for orphan modules (packages without manifests) and generate missing manifests to achieve 99% artifact coverage.

**Key Steps**:
1. Find all Python packages without manifests
2. Categorize orphans by domain
3. Generate missing manifests with appropriate star/tier assignments
4. Validate all manifests pass schema checks

**Output**: ~50-100 new manifests, 99% coverage

---

### **Task B: Contract Registry Hardening**
- **File**: [COPILOT_TASK_B_CONTRACT_HARDENING.md](./COPILOT_TASK_B_CONTRACT_HARDENING.md)
- **Priority**: High
- **Time**: 1-2 hours
- **Complexity**: Medium
- **Model Rec**: Claude 3.5 Sonnet or GPT-4

**Summary**: Fix all broken contract references in manifests and ensure 100% of T1 modules have contracts.

**Key Steps**:
1. Validate all contract references
2. Fix broken paths (lukhas/ → root, candidate/ → labs/)
3. Create contract stubs for T1 modules lacking contracts
4. Validate all fixes

**Output**: 0 broken contract refs, 100% T1 coverage

---

### **Task C: CI/CD Integration for Flat Structure**
- **File**: [COPILOT_TASK_C_CI_INTEGRATION.md](./COPILOT_TASK_C_CI_INTEGRATION.md)
- **Priority**: High
- **Time**: 2-3 hours
- **Complexity**: High
- **Model Rec**: GPT-4 or Claude 3.5 Sonnet

**Summary**: Update all GitHub Actions workflows for Phase 5B flat directory structure and add manifest/contract validation.

**Key Steps**:
1. Update all workflow paths (lukhas/ → root)
2. Add manifest validation job to CI
3. Add star promotion detection
4. Add T1 enforcement (OWNERS + contracts)
5. Optimize workflow performance

**Output**: Updated CI/CD, automated governance enforcement

---

## 🚀 How to Delegate

### Option 1: GitHub Copilot Chat (VSCode/JetBrains)

1. Open the task file (e.g., `COPILOT_TASK_A_ARTIFACT_AUDIT.md`)
2. In Copilot Chat, paste:
   ```
   Please complete the task described in this file. Follow all steps,
   validate your work, and commit using the provided message template.
   ```
3. Copilot will execute the task autonomously

### Option 2: GitHub Copilot Workspace (Web)

1. Navigate to https://github.com/features/copilot/workspace
2. Select the LUKHAS repository
3. Upload the task file
4. Copilot Workspace will plan and execute the task

### Option 3: Claude Projects / ChatGPT

1. Create new project/chat session
2. Upload task file + relevant context
3. Ask: "Complete this task following all instructions"
4. Review outputs before committing

### Option 4: Grok (X.AI)

1. Start Grok coding session
2. Provide repository context + task file
3. Let Grok execute autonomously
4. Review and commit results

---

## 📊 Task Dependencies

```
Task A (Artifact Audit)     ← Independent, can run anytime
Task B (Contract Hardening) ← Independent, can run anytime
Task C (CI Integration)     ← Should wait for A+B for best results
```

**Recommendation**: Run Task A and Task B in parallel, then Task C after both complete.

---

## ✅ Validation Checklist

Before accepting delegated work, verify:

- [ ] All commands in task file were executed
- [ ] Validation steps passed (no errors)
- [ ] Commit message follows T4 standard (no hype, humble tone)
- [ ] Code changes are safe (no breaking changes)
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if applicable)

---

## 🎯 Success Metrics

**Task A Success**:
- Manifest coverage: ≥99%
- All new manifests pass validation
- Star/tier assignments are reasonable

**Task B Success**:
- Broken contract refs: 0
- T1 contract coverage: 100%
- All contracts exist at specified paths

**Task C Success**:
- All workflows updated for flat structure
- CI validates manifests on every PR
- Star promotions detected automatically
- T1 enforcement prevents non-compliant merges

---

## 📝 Notes

- **Model Selection**: Choose models with strong code execution capabilities
- **Time Estimates**: Based on autonomous execution (no human intervention)
- **Complexity Ratings**:
  - Low: Simple scripting, minimal logic
  - Medium: Multiple steps, some decision-making
  - High: Complex logic, multiple file updates, testing required
- **Parallel Execution**: Tasks A and B can be delegated to different models simultaneously

---

## 🔗 Related Documents

- [EXECUTION_PLAN.md](../../EXECUTION_PLAN.md) - Overall project execution plan
- [PHASE5B_COMPLETION_SUMMARY.md](./PHASE5B_COMPLETION_SUMMARY.md) - Directory flattening summary
- [DIRECTORY_CONSOLIDATION_PLAN.md](./DIRECTORY_CONSOLIDATION_PLAN.md) - Directory cleanup plan

---

**Last Updated**: 2025-10-18
**Prepared By**: Claude Code (Sonnet 4.5)
**Status**: Ready for delegation
