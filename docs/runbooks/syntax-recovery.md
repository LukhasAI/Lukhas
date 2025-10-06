---
status: wip
type: documentation
---
# Syntax Recovery Runbook - Mass Breakage Recovery Procedures

## Overview

This runbook provides step-by-step procedures for recovering from mass syntax breakage incidents in the LUKHAS AI repository. It was created after the candidate/ directory automation experiment that increased syntax errors from 7,390 → 9,968.

## 🚨 Emergency Response (>1000 new syntax errors)

### Immediate Actions (0-15 minutes)

1. **STOP all automation experiments immediately**
   ```bash
   # Kill any running automation scripts
   pkill -f "autofix\|automation\|mass_.*\.py"
   
   # Check for running background processes
   ps aux | grep -E "(ruff|black|autofix|automation)"
   ```

2. **Assess damage scope**
   ```bash
   # Run syntax guardian assessment
   python tools/ci/syntax_guardian.py
   
   # Quick error count by directory
   .venv/bin/ruff check candidate/ --select=E999,F999 --statistics
   .venv/bin/ruff check lukhas/ --select=E999,F999 --statistics
   ```

3. **Identify last known good commit**
   ```bash
   # Review recent commits for automation/mass changes
   git log --oneline -20 --grep="autofix\|automation\|mass"
   
   # Check commit sizes for unusually large changes
   git log --stat --oneline -10
   ```

### Recovery Procedure (15-45 minutes)

4. **Git history recovery (recommended for >2000 errors)**
   ```bash
   # Find the last clean commit (before automation experiment)
   git log --oneline -30 | grep -E "(clean|stable|working)"
   
   # Restore affected directory from clean commit
   git checkout <CLEAN_COMMIT> -- candidate/
   
   # Verify error reduction
   python tools/ci/syntax_guardian.py
   ```

5. **Cherry-pick essential recent changes**
   ```bash
   # Identify critical fixes made after clean commit
   git log <CLEAN_COMMIT>..HEAD --oneline
   
   # Apply essential changes manually or via selective git cherry-pick
   # Focus on: agent fixes, critical bug fixes, API changes
   ```

6. **Validate recovery**
   ```bash
   # Run comprehensive world tests
   .venv/bin/pytest tests/test_basic_functions.py -v
   .venv/bin/pytest tests/test_aka_qualia.py::TestT1T2Integration::test_complete_cycle_dangerous_input -v
   .venv/bin/pytest tests/bio/ tests/memory/test_memory_basic.py -v --tb=short
   
   # Verify 100% success rate
   echo "✅ Recovery complete if all tests pass"
   ```

## ⚠️ Critical Response (500-1000 new syntax errors)

### Automated Recovery Attempts (0-20 minutes)

1. **Run comprehensive autofix**
   ```bash
   # Ruff autofix with all safe rules
   .venv/bin/ruff check --fix candidate/ lukhas/
   
   # T4 autofix system
   bash tools/ci/nightly_autofix.sh
   ```

2. **Custom syntax fixing**
   ```bash
   # If custom fixer exists, run it
   if [ -f "tools/fix_syntax_errors.py" ]; then
       python tools/fix_syntax_errors.py
   fi
   ```

3. **Validate improvement**
   ```bash
   # Check error reduction
   python tools/ci/syntax_guardian.py
   
   # If still critical, escalate to emergency procedures
   ```

### Manual Intervention (if automated recovery insufficient)

4. **Identify systematic patterns**
   ```bash
   # Find most common error patterns
   .venv/bin/ruff check candidate/ --select=E999,F999 --output-format=json | \
     jq -r '.[].code' | sort | uniq -c | sort -nr
   ```

5. **Targeted fixing**
   ```bash
   # Fix specific error types
   .venv/bin/ruff check candidate/ --select=F999 --fix  # Syntax errors
   .venv/bin/ruff check candidate/ --select=E999 --fix  # Indentation errors
   ```

## 💡 Warning Response (100-500 new syntax errors)

### Standard Recovery (0-10 minutes)

1. **Quick autofix**
   ```bash
   .venv/bin/ruff check --fix .
   ```

2. **Review recent changes**
   ```bash
   git log --oneline -5
   git diff HEAD~1 --stat
   ```

3. **Validate and monitor**
   ```bash
   python tools/ci/syntax_guardian.py
   ```

## Recovery Validation Checklist

After any recovery procedure:

- [ ] Syntax Guardian reports "ok" status
- [ ] Error count below baseline + 100
- [ ] World tests achieve 100% success rate
- [ ] No critical functionality broken
- [ ] Recovery documented in commit message
- [ ] Baseline updated if necessary

## Prevention Measures

### Pre-Commit Protection
- Syntax Guardian pre-commit hook blocks commits with >500 new errors
- Ruff format and autofix runs before commit
- MyPy type checking prevents type-related syntax errors

### CI Protection
- GitHub Actions runs Syntax Guardian on all PRs
- Daily syntax trend monitoring
- Automatic PR comments for critical issues

### Automation Safety
- T4 autofix policies limit risky transformations
- Protected interface patterns prevent API breakage
- Manual review required for complex changes

## Baselines and Thresholds

### Current Baselines (Post-Recovery)
- `candidate/`: 4,492 syntax errors
- `lukhas/`: 814 syntax errors  
- `total`: 5,306 syntax errors

### Alert Thresholds
- **Warning**: +100 new errors
- **Critical**: +500 new errors
- **Emergency**: +1,000 new errors

## Historical Incidents

### 2025-09-08: Candidate Directory Automation Experiment
- **Cause**: Automation experiment in candidate/ directory
- **Impact**: 7,390 → 9,968 syntax errors (2,578 new errors)
- **Recovery**: Git restore to commit 60b938075 + selective cherry-picking
- **Lessons**: Need pre-commit validation, error monitoring, recovery procedures
- **Duration**: ~2 hours for full recovery with 100% test success

## Contact Information

### Escalation Path
1. **Self-service**: Use this runbook and Syntax Guardian tool
2. **Development team**: Create GitHub issue with Syntax Guardian report
3. **Emergency**: If system completely broken, consider full repository restore

### Useful Commands Reference
```bash
# Quick syntax check
python tools/ci/syntax_guardian.py

# Error counts by directory  
.venv/bin/ruff check {directory} --select=E999,F999 --statistics

# World test validation
.venv/bin/pytest tests/test_basic_functions.py tests/test_aka_qualia.py -v

# Find clean commits
git log --oneline -20 | grep -E "(clean|working|stable|✅)"

# Restore from clean commit
git checkout <COMMIT> -- {directory}/
```

---

*This runbook is maintained by the LUKHAS AI development team and updated after each major incident to improve recovery procedures.*