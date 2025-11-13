# Session 12: Reasoning Lab Safety Controls (GAPS B4)

**Status**: Ready to Execute
**Estimated Time**: 90 minutes
**Priority**: P0 (Product Safety)
**GAPS Item**: B4 - Reasoning Lab Safety Controls

---

## Instructions

1. Copy the entire prompt text below
2. Open Claude Code Web: https://claude.ai/code
3. Paste the prompt
4. Wait for PR creation
5. Review and merge PR
6. Run validation: `make reasoning-lab-safety-check`

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

**Task**: Implement Reasoning Lab Safety Controls for GAPS B4

**Goal**: Build privacy-preserving demo mode with redaction controls, sensitive data detection, and safe reasoning trace visualization for the LUKHAS Reasoning Lab (interactive AI reasoning visualization tool).

**Background**:
- Reasoning Lab is LUKHAS's flagship demo feature showing step-by-step AI reasoning
- Risk: Users may paste sensitive data (API keys, passwords, PII) into reasoning prompts
- Need: Real-time sensitive data detection and redaction
- Missing: Privacy-preserving demo mode with configurable redaction levels
- GAPS Item: B4 from GAPS_ANALYSIS.md

**Deliverables**:

1. **Sensitive Data Detector** (`lukhas/reasoning_lab/sensitive_data_detector.py`):
   - Pattern-based detection:
     - API keys (AWS, OpenAI, Anthropic, Google Cloud)
     - Passwords (common patterns, entropy-based detection)
     - Email addresses
     - Phone numbers (international formats)
     - Credit card numbers
     - Social Security Numbers
     - IP addresses (public/private)
     - UUIDs and secrets (base64, hex patterns)
   - Entropy analysis for unknown secret formats
   - Configurable detection thresholds (low, medium, high sensitivity)
   - Returns: `[(type, start_pos, end_pos, confidence)]`

2. **Redaction Engine** (`lukhas/reasoning_lab/redaction_engine.py`):
   - Multiple redaction modes:
     - `FULL`: Replace with `[REDACTED-{TYPE}]` (e.g., `[REDACTED-API-KEY]`)
     - `PARTIAL`: Show first/last 4 chars (e.g., `sk-...xyz`)
     - `HASH`: Show SHA-256 hash prefix (e.g., `hash:a1b2c3...`)
     - `BLUR`: Show placeholder length (e.g., `****-****-****`)
   - Preserves reasoning trace structure
   - Reversible for authorized users (store mapping securely)
   - Audit logging of all redactions

3. **Redaction Slider UI** (`products/frontend/components/RedactionSlider.tsx`):
   - Interactive slider: None (0) → Low (25) → Medium (50) → High (75) → Paranoid (100)
   - Real-time preview of redaction effect
   - Tooltips explaining each level
   - Persists user preference (localStorage)
   - Visual feedback when sensitive data detected

4. **Privacy-Preserving Demo Mode** (`lukhas/reasoning_lab/demo_mode.py`):
   - Auto-enable redaction for public demos
   - Sandboxed execution (no external API calls)
   - Ephemeral session storage (delete after 1 hour)
   - Watermark on reasoning traces ("Demo Mode - Not for Production")
   - Rate limiting (10 reasoning traces per IP per hour)

5. **Reasoning Trace Sanitizer** (`lukhas/reasoning_lab/trace_sanitizer.py`):
   - Sanitize reasoning traces before storage
   - Remove sensitive data from logs
   - Configurable retention policies (default: 7 days demo, 30 days authenticated)
   - Export sanitized traces for debugging (JSON format)

6. **Admin Dashboard** (`products/frontend/pages/admin/reasoning_lab_safety.tsx`):
   - View redaction statistics (detections per day, types, confidence)
   - Configure detection sensitivity thresholds
   - Review flagged reasoning traces
   - Export audit logs (CSV/JSON)

7. **Testing & Validation**:
   - `tests/reasoning_lab/test_sensitive_data_detector.py` - Pattern matching tests
   - `tests/reasoning_lab/test_redaction_engine.py` - Redaction modes tests
   - `tests/reasoning_lab/test_demo_mode.py` - Demo mode isolation tests
   - `tools/validate_reasoning_lab_safety.py` - Safety compliance checker

8. **Documentation** (`docs/reasoning_lab/SAFETY_CONTROLS.md`):
   - How redaction works
   - Detection patterns and thresholds
   - Demo mode usage
   - Privacy guarantees
   - Troubleshooting guide

**Safety Requirements** (MUST comply):
- ✅ NO storage of unredacted sensitive data
- ✅ NO external API calls in demo mode
- ✅ Redaction enabled by default (opt-out, not opt-in)
- ✅ Audit logs for all detections
- ✅ Rate limiting to prevent abuse
- ✅ Ephemeral sessions in demo mode
- ✅ Clear visual indicators of redaction level

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as safety validation job
- Add `make reasoning-lab-safety-check` target to Makefile
- Link from `branding/governance/README.md`
- Add to Phase 3 tracking

**Acceptance Criteria**:
- Sensitive data detector with 95%+ detection rate on test corpus
- 4 redaction modes working (full, partial, hash, blur)
- Redaction slider UI with real-time preview
- Demo mode fully sandboxed (no external calls)
- Admin dashboard with audit logs
- Comprehensive test coverage (90%+)
- Documentation complete with examples
- CI/CD integration working

**T4 Commit Message**:
```
feat(reasoning-lab): add privacy-preserving demo mode with redaction controls

Problem:
- Reasoning Lab risk: users may paste sensitive data (API keys, PII)
- No real-time sensitive data detection
- Missing privacy-preserving demo mode
- No configurable redaction controls

Solution:
- Built sensitive data detector (API keys, passwords, PII, credit cards, etc.)
- Implemented redaction engine with 4 modes (full, partial, hash, blur)
- Created redaction slider UI with real-time preview
- Built privacy-preserving demo mode (sandboxed, ephemeral, rate-limited)
- Added reasoning trace sanitizer with retention policies
- Created admin dashboard with audit logs and statistics
- Comprehensive testing and validation tools

Impact:
- Safe demo mode for public showcases
- Real-time sensitive data protection
- User-controlled redaction levels (0-100% paranoid mode)
- Audit trail for compliance
- 95%+ detection rate on test corpus
- GAPS B4 complete (9/19 items → 10/19 = 52.6%)

Closes: GAPS-B4
Security-Impact: Prevents sensitive data leakage in reasoning traces
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(reasoning-lab): add privacy-preserving demo mode with redaction controls (GAPS B4)"

**Validation**: Run `make reasoning-lab-safety-check` before creating PR
```

---

## Post-Execution Checklist

- [ ] PR created and numbered
- [ ] PR reviewed for safety compliance
- [ ] All tests passing (90%+ coverage)
- [ ] Demo mode tested with sample sensitive data
- [ ] Redaction slider UI validated
- [ ] Admin dashboard functional
- [ ] `make reasoning-lab-safety-check` passes
- [ ] PR merged with squash
- [ ] Branch deleted
- [ ] Update GAPS progress to 10/19 (52.6%)

---

**Session Created**: 2025-11-08
**Ready to Execute**: Yes
