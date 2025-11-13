# Session 13: 5-Minute Reproducible Demo (GAPS B6)

**Status**: Ready to Execute
**Estimated Time**: 75 minutes
**Priority**: P0 (Developer Experience)
**GAPS Item**: B6 - 5-minute Reproducible Demo

---

## Instructions

1. Copy the entire prompt text below
2. Open Claude Code Web: https://claude.ai/code
3. Paste the prompt
4. Wait for PR creation
5. Review and merge PR
6. Test on clean VM (must complete in < 5 minutes)

---

## Prompt Text (Copy Everything Below)

```
**LUKHAS Project Context**:

**Repository**: https://github.com/LukhasAI/Lukhas (LUKHAS AI consciousness platform)

**Critical Policies**:
- **Lane Isolation**: NEVER import from `candidate/` in `lukhas/` code (validate with `make lane-guard`)
- **Testing Standards**: Maintain 75%+ coverage for production promotion
- **Commit Format**: `<type>(<scope>): <imperative subject ≤72>` with Problem/Solution/Impact bullets
- **Vocabulary Compliance**: NO "true AI", "sentient AI", "production-ready" without approval
- **Branding**: Use "LUKHAS AI", "quantum-inspired", "bio-inspired" (never "AGI")
- **Evidence System**: Link all claims to `release_artifacts/evidence/` pages
- **SEO Standards**: Add canonical URLs, meta descriptions (150-160 chars), keywords
- **Analytics**: GDPR-first, privacy-preserving, consent-based tracking only
- **Feature Flags**: Use `lukhas/features/flags_service.py` for gradual rollouts
- **Launch Playbooks**: Follow `branding/governance/launch/` templates

**Key Commands**:
- `make test` - Run comprehensive test suite
- `make lint` - Run linting and type checking
- `make lane-guard` - Validate import boundaries
- `make seo-validate` - Validate SEO compliance
- `make claims-validate` - Validate claims have evidence
- `make flags-validate` - Validate feature flags
- `make analytics-privacy-check` - Check for PII leakage
- `make launch-validate` - Validate launch checklists

**Related Docs**:
- Evidence System: `branding/governance/tools/EVIDENCE_SYSTEM.md`
- SEO Guide: `branding/governance/SEO_GUIDE.md`
- Analytics Integration: `branding/analytics/INTEGRATION_GUIDE_V2.md`
- Privacy Implementation: `branding/analytics/PRIVACY_IMPLEMENTATION.md`
- Feature Flags Guide: `branding/features/FEATURE_FLAGS_GUIDE.md`
- Launch Playbooks: `branding/governance/launch/PLAYBOOK_TEMPLATE.md`
- 90-Day Roadmap: `branding/governance/strategic/90_DAY_ROADMAP.md`
- GAPS Analysis: `branding/governance/strategic/GAPS_ANALYSIS.md`

**Phase Progress**: 9/19 GAPS items complete (47.4%) - Phases 1 & 2 delivered 46,992 lines

---

**Task**: Create 5-Minute Reproducible Demo for GAPS B6

**Goal**: Build zero-config quickstart that gets developers from `git clone` to working LUKHAS demo in under 5 minutes, with guided onboarding, pre-configured examples, and troubleshooting assistance.

**Background**:
- Current setup requires manual configuration (env vars, dependencies, database)
- No guided onboarding for first-time developers
- Missing pre-configured examples showing key features
- GAPS Item: B6 from GAPS_ANALYSIS.md

**Deliverables**:

1. **One-Command Setup Script** (`scripts/quickstart.sh`):
   - Detects OS (macOS, Linux, Windows/WSL)
   - Checks prerequisites (Python 3.9+, Node.js, Docker)
   - Auto-installs missing dependencies (with user confirmation)
   - Creates `.env` from template with defaults
   - Runs `make bootstrap` in background
   - Opens browser to `http://localhost:8000` when ready
   - Colorized output with progress indicators
   - Estimated time remaining

2. **Interactive Onboarding Flow** (`products/frontend/components/Onboarding.tsx`):
   - Welcome screen with product overview (30 seconds)
   - Step 1: Choose your path (Developer, Researcher, Enterprise)
   - Step 2: Configure preferences (demo data, API keys optional)
   - Step 3: Quick tour (5 interactive tooltips)
   - Step 4: Run first reasoning trace
   - Progress bar showing completion
   - Skip button with option to resume later

3. **Pre-Configured Examples** (`examples/quickstart/`):
   - `01_hello_lukhas.py` - Simple consciousness query (30 lines)
   - `02_reasoning_trace.py` - Step-by-step reasoning visualization (50 lines)
   - `03_memory_persistence.py` - Context preservation demo (60 lines)
   - `04_guardian_ethics.py` - Constitutional AI demo (70 lines)
   - `05_full_workflow.py` - End-to-end example (100 lines)
   - Each with:
     - Inline comments explaining every step
     - Expected output samples
     - Troubleshooting tips
     - Links to full documentation

4. **Guided CLI** (`lukhas/cli/guided.py`):
   - `lukhas quickstart` - Interactive setup wizard
   - `lukhas demo <example-name>` - Run pre-configured examples
   - `lukhas troubleshoot` - Auto-diagnose common issues
   - `lukhas tour` - Interactive product tour
   - Rich terminal output (colors, tables, spinners)

5. **Troubleshooting Assistant** (`lukhas/cli/troubleshoot.py`):
   - Auto-detects common issues:
     - Missing dependencies
     - Port conflicts (8000, 5432, 6379)
     - Python version mismatch
     - Environment variable errors
     - Docker not running
   - Suggests fixes with copy-paste commands
   - Links to relevant docs
   - Option to open GitHub issue with diagnostics

6. **Demo Data Generator** (`tools/generate_demo_data.py`):
   - Creates sample reasoning traces (10 examples)
   - Populates memory with context folds
   - Generates example evidence pages
   - Creates sample claims
   - Configurable size (small, medium, large)
   - Safe to run multiple times (idempotent)

7. **Quickstart Documentation** (`docs/quickstart/README.md`):
   - 5-minute quickstart (actual 5 minutes, not marketing 5 minutes!)
   - Prerequisites section
   - Troubleshooting guide
   - Video walkthrough (script for future recording)
   - FAQs
   - Next steps (advanced features)

8. **Testing & Validation**:
   - `tests/quickstart/test_setup_script.sh` - Test quickstart.sh on clean VM
   - `tests/quickstart/test_examples.py` - Verify all 5 examples run
   - `tests/quickstart/test_troubleshoot.py` - Test issue detection
   - Run in CI/CD on multiple OS (macOS, Ubuntu, Windows)

**Acceptance Criteria**:
- Setup completes in under 5 minutes on clean machine
- Zero manual configuration required for demo mode
- All 5 pre-configured examples run successfully
- Onboarding flow guides user through first reasoning trace
- Troubleshooting assistant detects and suggests fixes
- Comprehensive test coverage (90%+)
- Documentation with actual 5-minute walkthrough
- CI/CD integration testing on multiple OS

**T4 Commit Message**:
```
feat(quickstart): add 5-minute reproducible demo with guided onboarding

Problem:
- Complex setup requiring manual configuration
- No guided onboarding for first-time developers
- Missing pre-configured examples
- No troubleshooting assistance

Solution:
- Created one-command setup script (scripts/quickstart.sh)
- Built interactive onboarding flow with progress tracking
- Added 5 pre-configured examples (hello → full workflow)
- Implemented guided CLI (quickstart, demo, troubleshoot, tour)
- Built troubleshooting assistant with auto-diagnosis
- Created demo data generator for sample content
- Comprehensive quickstart documentation

Impact:
- Git clone → working demo in under 5 minutes
- Zero-config default experience
- Guided onboarding reduces time-to-value by 90%
- Auto-troubleshooting reduces support burden
- Developer adoption accelerated
- GAPS B6 complete (10/19 items → 11/19 = 57.9%)

Closes: GAPS-B6
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(quickstart): add 5-minute reproducible demo with guided onboarding (GAPS B6)"

**Validation**:
- Run `scripts/quickstart.sh` on clean VM
- Time the setup (must be < 5 minutes)
- Test all 5 examples
```

---

## Post-Execution Checklist

- [ ] PR created and numbered
- [ ] PR reviewed for completeness
- [ ] All tests passing (90%+ coverage)
- [ ] Quickstart tested on clean VM
- [ ] Setup completes in < 5 minutes
- [ ] All 5 examples run successfully
- [ ] Onboarding flow validated
- [ ] Troubleshooting assistant tested
- [ ] PR merged with squash
- [ ] Branch deleted
- [ ] Update GAPS progress to 11/19 (57.9%)

---

**Session Created**: 2025-11-08
**Ready to Execute**: Yes
