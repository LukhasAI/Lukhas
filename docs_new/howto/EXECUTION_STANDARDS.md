---
title: Execution Standards
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "testing", "security", "howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "guardian"]
  audience: ["dev"]
---

# LUKHAS AI EXECUTION STANDARDS

## 🎯 Quality Target
**We execute at the level that would make Sam Altman (scale/orchestration), Dario Amodei (constitutional safety), and Demis Hassabis (scientific rigor) proud.**

This is our 3rd attempt. No more mistakes are acceptable.

## 📋 Master Checklist (ALWAYS FOLLOW)

### Phase 1: Critical Security & Foundation
Reference: `reality_check_phase_1_and_beyond.md` lines 1-110, `phase_beyond.md` lines 4-21

1. **CRITICAL SECURITY - Remove exposed API keys**
   - [ ] Remove .env from git tracking
   - [ ] Add .env to .gitignore
   - [ ] Purge API keys from git history
   - [ ] Create .env.example with safe defaults
   - [ ] **ROTATE ALL EXPOSED KEYS AT PROVIDERS**

2. **AST-based Acceptance Gate**
   Reference: `reality_check_phase_1_and_beyond.md` lines 11-110
   - [ ] Replace tools/acceptance_gate.py with AST version
   - [ ] Verify it catches ALL existing violations
   - [ ] Verify it detects facade files (<40 lines, imports only)

3. **Fix Illegal Imports with Registry Pattern**
   Reference: `reality_check_phase_1_and_beyond.md` lines 119-157, `phase_beyond.md` lines 55-101
   - [ ] Fix lukhas/core/core_wrapper.py
   - [ ] Fix lukhas/governance/guardian/guardian_impl.py
   - [ ] NO static imports from candidate/ in accepted/

4. **Safety Defaults**
   Reference: `reality_check_phase_1_and_beyond.md` lines 162-185
   - [ ] Create conftest.py with DRY_RUN_MODE=true
   - [ ] Create .env.example with all features OFF
   - [ ] Verify defaults load in all tests

5. **E2E Test**
   Reference: `reality_check_phase_1_and_beyond.md` lines 189-208
   - [ ] Create tests/test_e2e_dryrun.py
   - [ ] Verify it passes with dry-run mode
   - [ ] No real API calls, no side effects

### Phase 2: CI/CD & Documentation
Reference: `reality_check_phase_1_and_beyond.md` lines 212-224, `phase_beyond.md` lines 23-35

6. **CI Integration**
   - [ ] Add acceptance gate to CI BEFORE tests
   - [ ] Add import-linter contracts
   - [ ] Verify CI fails on violations

7. **Honest Documentation**
   Reference: `phase_beyond.md` lines 122-151
   - [ ] Write LUKHAS_SYSTEM_STATUS.md with REAL metrics
   - [ ] Update MODULE_MANIFEST.json files
   - [ ] Document actual vs claimed state

### Phase 3: Real Promotions
Reference: `reality_check_phase_1_and_beyond.md` lines 227-243

8. **Promotion Criteria (6-point checklist)**
   - [ ] Lane: accepted (not candidate/quarantine/archive)
   - [ ] No banned imports (verified by AST gate)
   - [ ] MATRIZ instrumentation at public APIs
   - [ ] Tests passing in CI
   - [ ] P95 latency meets SLA on reference machine
   - [ ] Dry-run default + consent gates

## 🚫 Common Failures to Avoid

1. **Acceptance Gate Inadequacy**
   - Old gate only checked NEW files via git diff
   - Must scan ALL files in lukhas/ directory
   - Must use AST parsing, not grep/regex

2. **Facade Files**
   - Files that just import and re-export from candidate
   - Less than 40 lines, mostly imports
   - Must be replaced with registry pattern

3. **Security Breaches**
   - API keys in tracked files
   - Keys in git history
   - Not rotating compromised keys

4. **False Claims**
   - Saying "promoted" when only interfaces exist
   - Claiming 100% tests pass when they fail
   - Performance metrics without measurements

## 🛠️ Resources to Use

- **Local LLMs**: For quick validation and testing
- **Claude Agents**: For specialized tasks (use Task tool)
- **API Services**: Only in dry-run mode initially
- **AST Parser**: For accurate import detection
- **Registry Pattern**: For clean separation of concerns

## 📊 Success Metrics

- **Acceptance Gate**: Zero violations in lukhas/
- **Tests**: At least one E2E test passing
- **Security**: No secrets in git, all keys rotated
- **Documentation**: Honest status reflecting reality
- **CI/CD**: Gate runs on every commit

## 🔍 Verification Commands

```bash
# Run acceptance gate
python3 tools/acceptance_gate.py

# Check for secrets
grep -r "sk-" . --exclude-dir=.git

# Run E2E test
pytest tests/test_e2e_dryrun.py -v

# Check imports
python3 -c "import ast; print('AST available')"
```

## 📝 Document References

Always check back to these source documents:
- `reality_check_phase_1_and_beyond.md` - Complete Phase 1-3 plan
- `phase_beyond.md` - Security fixes and execution order

These contain the exact code snippets and commands needed.

## ⚠️ CRITICAL REMINDERS

1. This is the 3rd attempt - no more mistakes
2. Execute at the level of industry leaders
3. Always verify before claiming completion
4. Use AST, not grep/regex for parsing
5. Registry pattern, not static imports
6. Dry-run mode by default
7. Rotate ALL exposed keys immediately

---

**Remember**: We're building a system that would pass review by:
- Sam Altman: Scale, orchestration, production-readiness
- Dario Amodei: Constitutional AI, safety, ethics
- Demis Hassabis: Scientific rigor, verifiable claims
