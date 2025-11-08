# Claude Code Web - Prompts 9, 10, 11 (Phase 2: Product Experience)

**Date**: 2025-11-08
**Phase**: 2 - Product Experience
**Repository**: https://github.com/LukhasAI/Lukhas
**Session Type**: Claude Code Web (claude.ai/code)

---

## Overview

Phase 2 focuses on **Product Experience** with three priority-0 GAPS items that improve launch coordination, privacy analytics, and feature management. These prompts are designed for **sequential execution** via Claude Code Web.

### Phase 2 Goals

- **A3**: Launch Playbooks - Marketing/Engineering coordination
- **E13**: Privacy-First Analytics - GDPR-compliant tracking implementation
- **B5**: Feature Flags System - Safe rollout and experimentation

### Execution Order

1. **Prompt 9** (Launch Playbooks) - Creates process templates for future launches
2. **Prompt 10** (Privacy Analytics) - Implements event tracking from existing taxonomy
3. **Prompt 11** (Feature Flags) - Enables controlled rollouts for new features

---

## LUKHAS Project Policies (Include in ALL Prompts)

Copy-paste this header at the start of EVERY prompt sent to Claude Code Web:

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

**Key Commands**:
- `make test` - Run comprehensive test suite
- `make lint` - Run linting and type checking
- `make lane-guard` - Validate import boundaries
- `make seo-validate` - Validate SEO compliance
- `make claims-validate` - Validate claims have evidence

**Related Docs**:
- Evidence System: `branding/governance/tools/EVIDENCE_SYSTEM.md`
- SEO Guide: `branding/governance/SEO_GUIDE.md`
- Analytics Integration: `branding/analytics/INTEGRATION_GUIDE.md`
- 90-Day Roadmap: `branding/governance/strategic/90_DAY_ROADMAP.md`
- GAPS Analysis: `branding/governance/strategic/GAPS_ANALYSIS.md`

**Phase 1 Complete**: 9 PRs merged, 34,789 lines of governance infrastructure, 6/19 GAPS items done.
```

---

# Prompt 9: Launch Playbooks (GAPS A3)

**Estimated Time**: 45 minutes
**Priority**: P0 (Product Experience)
**GAPS Item**: A3 - Launch Playbooks
**Effort**: 1 week of manual work → 45 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

---

**Task**: Create Launch Playbooks for GAPS A3 (Marketing/Engineering Coordination)

**Goal**: Create comprehensive launch playbook templates and checklists to ensure smooth cross-functional coordination for feature releases, product launches, and major updates.

**Background**:
- LUKHAS AI has multiple product launches planned (Reasoning Lab, MATRIZ engine, identity system)
- Need standardized templates for marketing/engineering sync
- Current launch process is ad-hoc, leading to misalignment and delays
- Phase 2 focus on Product Experience requires repeatable launch workflows

**Deliverables**:

1. **Launch Playbook Template** (`branding/governance/launch/PLAYBOOK_TEMPLATE.md`):
   - Pre-launch checklist (T-30, T-14, T-7, T-1 days)
   - Launch day runbook with rollback procedures
   - Post-launch review template
   - Cross-functional stakeholder map (engineering, marketing, legal, security)
   - Communication templates (internal announcements, external blog posts, social)
   - Success metrics and KPI tracking

2. **Feature Launch Checklist** (`branding/governance/launch/FEATURE_CHECKLIST.md`):
   - Technical readiness (tests, docs, monitoring, feature flags)
   - Marketing readiness (landing page, blog post, social assets)
   - Legal/compliance readiness (privacy review, claims approval, evidence pages)
   - Security readiness (audit, penetration testing, compliance)
   - Analytics readiness (event tracking, dashboards, alerts)

3. **Launch Timeline Template** (`branding/governance/launch/TIMELINE_TEMPLATE.md`):
   - Gantt chart format (markdown table)
   - Milestone tracking (alpha, beta, GA)
   - Dependencies and blockers tracking
   - Risk assessment and mitigation

4. **Launch Types Reference** (`branding/governance/launch/LAUNCH_TYPES.md`):
   - Major product launch (e.g., Reasoning Lab)
   - Feature launch (e.g., new API endpoint)
   - Infrastructure launch (e.g., new region)
   - Content launch (e.g., evidence pages, documentation)
   - Each type with specific requirements and templates

5. **Example Launch: Reasoning Lab** (`branding/governance/launch/examples/reasoning_lab_launch.md`):
   - Filled-in playbook for Reasoning Lab launch
   - Shows how to use templates in practice
   - References existing documentation and artifacts

6. **Validation Tool** (`tools/validate_launch.py`):
   - Validates launch checklist completeness
   - Checks for required artifacts (landing page, blog post, evidence pages)
   - Verifies cross-functional sign-offs
   - Runs in CI/CD via GitHub Actions

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as new job
- Add `make launch-validate` target to Makefile
- Link to from `branding/governance/README.md`
- Add to Phase 2 tracking in `BRANDING_GOVERNANCE_PHASE1_COMPLETE.md`

**Acceptance Criteria**:
- 6 comprehensive launch documents created (5 templates + 1 example)
- Validation tool with 90%+ coverage
- CI/CD integration working
- All templates follow LUKHAS vocabulary and branding standards
- Example launch references real LUKHAS artifacts
- Ready for immediate use in Reasoning Lab launch

**T4 Commit Message**:
```
feat(governance): add launch playbooks for cross-functional coordination

Problem:
- Ad-hoc launch process causing misalignment and delays
- No standardized templates for marketing/engineering sync
- Missing checklists for technical, legal, and marketing readiness

Solution:
- Created comprehensive launch playbook template with pre/post-launch checklists
- Added feature launch checklist covering technical, marketing, legal readiness
- Built launch timeline template with milestone and dependency tracking
- Defined 4 launch types (product, feature, infrastructure, content)
- Created example Reasoning Lab launch playbook
- Built validation tool (validate_launch.py) with CI/CD integration

Impact:
- Repeatable launch workflows for all future releases
- Cross-functional alignment via standardized templates
- Reduced launch risk via comprehensive checklists
- GAPS A3 complete (6/19 items → 7/19 = 36.8%)

Closes: GAPS-A3
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(governance): add launch playbooks for cross-functional coordination (GAPS A3)"

**Validation**: Run `make launch-validate` before creating PR
```

---

# Prompt 10: Privacy-First Analytics Implementation (GAPS E13)

**Estimated Time**: 60 minutes
**Priority**: P0 (Privacy & Compliance)
**GAPS Item**: E13 - Privacy-First Analytics
**Effort**: 1 week of manual work → 60 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

---

**Task**: Implement Privacy-First Analytics System for GAPS E13

**Goal**: Build GDPR-compliant analytics implementation using the existing event taxonomy (`branding/analytics/event_taxonomy.json`) with privacy-preserving tracking, consent management, and zero PII collection.

**Background**:
- Event taxonomy already defined (9 events from PR #1113)
- Need actual implementation with privacy-first architecture
- Must support GDPR consent modes (granted, denied, unspecified)
- Zero PII collection by design
- Local-first analytics with optional server aggregation

**Deliverables**:

1. **Privacy-First Analytics Client** (`lukhas/analytics/privacy_client.py`):
   - Event tracking with consent checking (no tracking without explicit consent)
   - Local storage for user preferences (localStorage, not cookies)
   - Automatic PII redaction for any event properties
   - Configurable retention policies (default: 30 days)
   - Batch sending with exponential backoff
   - Circuit breaker for failed requests

2. **Consent Management UI** (`products/frontend/components/ConsentBanner.tsx`):
   - GDPR-compliant cookie banner (accept/reject/customize)
   - Granular consent controls (analytics, marketing, functional)
   - Privacy policy link and explanation
   - Opt-out at any time functionality
   - Accessible (WCAG 2.1 AA compliant)

3. **Analytics Configuration** (`branding/analytics/config.yaml`):
   - Event taxonomy reference
   - Consent mode defaults (denied by default)
   - Retention policies per event type
   - PII detection patterns (emails, phone numbers, IPs)
   - Allowed/blocked domains for tracking

4. **Server Aggregation Endpoint** (`lukhas/api/analytics.py`):
   - FastAPI endpoint for receiving events
   - Aggregation without storing individual events
   - Rate limiting (1000 events/hour per user)
   - IP anonymization (strip last octet)
   - User-Agent normalization (browser family only)
   - Returns aggregated metrics (no raw events)

5. **Privacy Documentation** (`branding/analytics/PRIVACY_IMPLEMENTATION.md`):
   - How consent management works
   - What data is collected and why
   - How PII is redacted
   - Retention and deletion policies
   - User rights (access, deletion, portability)
   - GDPR compliance checklist

6. **Integration Guide** (`branding/analytics/INTEGRATION_GUIDE_V2.md`):
   - Update existing guide with implementation details
   - Code examples for each event type
   - Testing privacy features
   - Debugging consent issues
   - Analytics dashboard setup

7. **Validation Tools**:
   - `tools/validate_analytics_privacy.py` - Checks for PII leakage in events
   - `tools/test_consent_flows.py` - E2E tests for consent management
   - Add to CI/CD pipeline

**Privacy Requirements** (MUST comply):
- ✅ NO cookies without consent
- ✅ NO third-party analytics (Google Analytics, Mixpanel, etc.)
- ✅ NO IP addresses stored (anonymize to /24)
- ✅ NO User-Agent strings stored (browser family only)
- ✅ NO cross-site tracking
- ✅ Consent required before ANY tracking
- ✅ Easy opt-out at any time
- ✅ Data deletion on request (<30 days)

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as privacy validation job
- Add `make analytics-privacy-check` target to Makefile
- Link from `branding/governance/README.md`
- Add to Phase 2 tracking

**Acceptance Criteria**:
- Privacy-first client with consent checking
- GDPR-compliant consent banner (WCAG 2.1 AA)
- Server aggregation endpoint (no raw event storage)
- Privacy documentation complete
- 2 validation tools with 90%+ coverage
- CI/CD integration working
- Zero PII in sample events
- All 9 events from taxonomy implemented

**T4 Commit Message**:
```
feat(analytics): implement privacy-first analytics with GDPR compliance

Problem:
- Event taxonomy defined but no implementation
- Missing consent management and privacy controls
- Risk of PII leakage in analytics events
- No GDPR compliance verification

Solution:
- Built privacy-first analytics client with consent checking
- Created GDPR-compliant consent banner (WCAG 2.1 AA)
- Implemented server aggregation endpoint (no raw event storage)
- Added automatic PII redaction and IP anonymization
- Created privacy documentation and integration guide
- Built validation tools (PII detection, consent flow testing)
- Integrated into CI/CD pipeline

Impact:
- GDPR-compliant analytics ready for production
- Zero PII collection by design
- User control via granular consent management
- Privacy validation in every PR
- GAPS E13 complete (7/19 items → 8/19 = 42.1%)

Closes: GAPS-E13
Security-Impact: Implements privacy-first architecture, prevents PII leakage
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(analytics): implement privacy-first analytics with GDPR compliance (GAPS E13)"

**Validation**:
- Run `make analytics-privacy-check` before creating PR
- Run `python3 tools/validate_analytics_privacy.py` on sample events
- Test consent banner in browser (accept/reject/customize flows)
```

---

# Prompt 11: Feature Flags System (GAPS B5)

**Estimated Time**: 50 minutes
**Priority**: P0 (Product Experience)
**GAPS Item**: B5 - Feature Flags
**Effort**: 1 week of manual work → 50 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

---

**Task**: Build Feature Flags System for GAPS B5 (Safe Rollouts & Experimentation)

**Goal**: Create a lightweight, privacy-preserving feature flags system for controlled rollouts, A/B testing, and safe experimentation without third-party dependencies.

**Background**:
- LUKHAS needs to safely roll out experimental features (Reasoning Lab, MATRIZ improvements)
- Want A/B testing without third-party tools (LaunchDarkly, Split.io)
- Need privacy-first approach (no user tracking without consent)
- Support gradual rollouts (0% → 1% → 10% → 50% → 100%)

**Deliverables**:

1. **Feature Flags Service** (`lukhas/features/flags_service.py`):
   - Load flags from YAML config (`branding/features/flags.yaml`)
   - Evaluate flag states (on/off/percentage/targeting)
   - Support flag types:
     - Boolean (on/off)
     - Percentage rollout (0-100%)
     - User targeting (email domain, user ID hash)
     - Time-based (enable after date, disable after date)
     - Environment-based (dev/staging/prod)
   - In-memory caching with TTL (default: 60s)
   - Fallback to safe defaults on errors

2. **Feature Flags Configuration** (`branding/features/flags.yaml`):
   - Schema with validation
   - Example flags for LUKHAS features:
     - `reasoning_lab_enabled` - Boolean
     - `matriz_v2_rollout` - Percentage (0-100%)
     - `enhanced_memory_beta` - User targeting (@lukhas.ai emails only)
     - `new_landing_page` - Time-based (enable 2025-12-01)
   - Flag metadata (owner, description, created_at, jira_ticket)

3. **Feature Flags API** (`lukhas/api/features.py`):
   - FastAPI endpoints:
     - `GET /api/features` - List all flags (admin only)
     - `GET /api/features/{flag_name}` - Get flag state
     - `POST /api/features/{flag_name}/evaluate` - Evaluate for user
   - Authentication required (no anonymous flag checking)
   - Audit logging for flag evaluations
   - Rate limiting (100 requests/min per user)

4. **Frontend Integration** (`products/frontend/hooks/useFeatureFlag.ts`):
   - React hook for checking flags: `const isEnabled = useFeatureFlag('reasoning_lab_enabled')`
   - Supports loading states and error handling
   - Caches results client-side (sessionStorage)
   - Auto-refresh on flag changes (SSE or polling)

5. **Admin UI** (`products/frontend/pages/admin/features.tsx`):
   - View all feature flags
   - Toggle boolean flags on/off
   - Adjust percentage rollouts (slider 0-100%)
   - View flag evaluation history
   - Export flag configuration
   - Requires admin role

6. **Testing Utilities** (`lukhas/features/testing.py`):
   - Context manager for overriding flags in tests:
     ```python
     with override_flag('reasoning_lab_enabled', True):
         # Test code here
     ```
   - Fixture for pytest: `@pytest.fixture def feature_flags()`

7. **Documentation** (`branding/features/FEATURE_FLAGS_GUIDE.md`):
   - How to create a new feature flag
   - Best practices (naming, defaults, rollout strategy)
   - Gradual rollout recommendations (1% → 10% → 50% → 100%)
   - Cleanup process (remove flags after full rollout)
   - Privacy considerations (no PII in flag targeting)

8. **Validation & Migration Tools**:
   - `tools/validate_flags.py` - Validates flags.yaml schema
   - `tools/migrate_flags.py` - Migrate from old config to new schema
   - Add to CI/CD pipeline

**Privacy Requirements**:
- ✅ NO user tracking without consent
- ✅ Flag evaluations logged only in aggregate (no individual user data)
- ✅ User targeting via privacy-preserving hashes (SHA-256)
- ✅ No third-party services
- ✅ Local-first evaluation (server only for admin)

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as flag validation job
- Add `make flags-validate` target to Makefile
- Link from `branding/governance/README.md`
- Add to Phase 2 tracking

**Acceptance Criteria**:
- Feature flags service with 5 flag types (boolean, percentage, targeting, time, environment)
- YAML configuration with 4 example flags
- FastAPI endpoints with auth and rate limiting
- React hook for frontend integration
- Admin UI for flag management
- Testing utilities with pytest fixtures
- Documentation guide with best practices
- 2 validation tools with 90%+ coverage
- CI/CD integration working
- Zero third-party dependencies

**T4 Commit Message**:
```
feat(features): add privacy-first feature flags system for safe rollouts

Problem:
- No way to safely roll out experimental features
- Third-party tools (LaunchDarkly) introduce privacy and cost concerns
- Missing A/B testing and gradual rollout capabilities
- Risk of breaking changes in production

Solution:
- Built lightweight feature flags service with 5 flag types
- Created YAML configuration with schema validation
- Implemented FastAPI endpoints with auth and rate limiting
- Added React hook for frontend integration
- Built admin UI for flag management
- Created testing utilities with pytest fixtures
- Documented best practices and rollout strategies
- Integrated validation into CI/CD pipeline

Impact:
- Safe gradual rollouts (0% → 1% → 10% → 50% → 100%)
- A/B testing without third-party tools
- Privacy-first approach (no user tracking without consent)
- Reduced deployment risk via controlled rollouts
- GAPS B5 complete (8/19 items → 9/19 = 47.4%)

Closes: GAPS-B5
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(features): add privacy-first feature flags system for safe rollouts (GAPS B5)"

**Validation**:
- Run `make flags-validate` before creating PR
- Test flag evaluation in unit tests
- Verify admin UI works (toggle flags, adjust percentages)
- Check privacy compliance (no PII in flag targeting)
```

---

## Execution Checklist

### Before Starting
- [ ] Review Phase 1 completion document (`BRANDING_GOVERNANCE_PHASE1_COMPLETE.md`)
- [ ] Verify all Phase 1 PRs merged (9/9)
- [ ] Check current GAPS progress (6/19 items = 31.5%)

### Prompt 9 Execution
- [ ] Copy LUKHAS policies + Prompt 9 text
- [ ] Paste into Claude Code Web (https://claude.ai/code)
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify `make launch-validate` passes

### Prompt 10 Execution
- [ ] Copy LUKHAS policies + Prompt 10 text
- [ ] Paste into Claude Code Web
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Test consent banner manually in browser
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify `make analytics-privacy-check` passes

### Prompt 11 Execution
- [ ] Copy LUKHAS policies + Prompt 11 text
- [ ] Paste into Claude Code Web
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Test feature flags admin UI manually
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify `make flags-validate` passes

### After All Prompts
- [ ] Update `BRANDING_GOVERNANCE_PHASE1_COMPLETE.md` to `BRANDING_GOVERNANCE_PHASE2_COMPLETE.md`
- [ ] Update GAPS progress to 9/19 items (47.4%)
- [ ] Create tracking issue for Phase 2 completion
- [ ] Create Prompts 12-14 for Phase 3 (if applicable)

---

## Expected Results

### Phase 2 Metrics (After Prompts 9-11)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| GAPS Items Complete | 6/19 (31.5%) | 9/19 (47.4%) | +3 ✅ |
| PRs Merged | 9 | 12 | +3 |
| Total Lines Added | 34,789 | ~38,000 | +3,211 est. |
| Validation Tools | 7 | 10 | +3 |
| Product Readiness | Low | Medium | Launch-ready |

### Time Savings

| Task | Manual | Automated | Savings |
|------|--------|-----------|---------|
| Launch Playbooks | 1 week | 45 min | 95% |
| Privacy Analytics | 1 week | 60 min | 94% |
| Feature Flags | 1 week | 50 min | 96% |
| **Total** | **3 weeks** | **2.6 hours** | **95.5%** |

### Quality Improvements

- ✅ Standardized launch process
- ✅ GDPR-compliant analytics
- ✅ Privacy-first architecture
- ✅ Safe rollout capabilities
- ✅ A/B testing infrastructure
- ✅ Comprehensive documentation
- ✅ CI/CD integration

---

## Troubleshooting

### Prompt Execution Issues

**Problem**: Claude Code Web times out or gets stuck
**Solution**:
- Break prompt into smaller sub-tasks
- Use `make test` to verify incremental progress
- Check GitHub Actions for validation failures

**Problem**: PR has merge conflicts
**Solution**:
- Use worktree for conflict resolution: `git worktree add ../Lukhas-fix-conflicts -b fix/conflicts`
- Follow same process as PR #1128 resolution

**Problem**: Validation tools fail in CI/CD
**Solution**:
- Run locally: `make launch-validate`, `make analytics-privacy-check`, `make flags-validate`
- Check error messages for specific issues
- Fix and re-push to PR branch

### Privacy Compliance Issues

**Problem**: PII detected in analytics events
**Solution**:
- Run `python3 tools/validate_analytics_privacy.py` on sample events
- Review redaction patterns in `branding/analytics/config.yaml`
- Add more PII detection patterns if needed

**Problem**: Consent banner not WCAG 2.1 AA compliant
**Solution**:
- Use axe DevTools browser extension to check accessibility
- Ensure keyboard navigation works (Tab, Enter, Esc)
- Test with screen reader (VoiceOver on macOS)

---

## Related Documentation

- **Phase 1 Completion**: `BRANDING_GOVERNANCE_PHASE1_COMPLETE.md`
- **Prompts 7 & 8**: `CLAUDE_WEB_PROMPTS_7_AND_8.md`
- **90-Day Roadmap**: `branding/governance/strategic/90_DAY_ROADMAP.md`
- **GAPS Analysis**: `branding/governance/strategic/GAPS_ANALYSIS.md`
- **Evidence System**: `branding/governance/tools/EVIDENCE_SYSTEM.md`
- **SEO Guide**: `branding/governance/SEO_GUIDE.md`
- **Analytics Integration**: `branding/analytics/INTEGRATION_GUIDE.md`

---

## Success Criteria

### Phase 2 Complete When:
- ✅ All 3 prompts executed successfully
- ✅ All 3 PRs merged to main
- ✅ All validation tools passing in CI/CD
- ✅ GAPS progress: 9/19 items (47.4%)
- ✅ Documentation updated
- ✅ Tracking issue created
- ✅ Ready for Phase 3 planning

---

**Document Owner**: @web-architect
**Created**: 2025-11-08 18:00:00Z
**Session**: Branding Governance Phase 2 Execution
**Estimated Total Time**: 2.6 hours (155 minutes)

