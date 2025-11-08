# Session 15: DPA/DPIA Templates (GAPS E12)

**Status**: Ready to Execute
**Estimated Time**: 45 minutes
**Priority**: P0 (Legal Compliance)
**GAPS Item**: E12 - DPA/DPIA Templates

---

## Instructions

1. Copy the entire prompt text below
2. Open Claude Code Web: https://claude.ai/code
3. Paste the prompt
4. Wait for PR creation
5. Review and merge PR
6. Schedule legal review of templates

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

**Task**: Create DPA/DPIA Templates for GAPS E12

**Goal**: Build comprehensive Data Processing Agreement and Data Protection Impact Assessment templates for GDPR compliance, ready for legal review and customer use.

**Background**:
- LUKHAS processes user data (reasoning traces, memory, analytics)
- GDPR requires DPA with enterprise customers
- DPIA needed for high-risk processing activities
- Missing standardized legal templates
- GAPS Item: E12 from GAPS_ANALYSIS.md

**Deliverables**:

1. **Data Processing Agreement Template** (`legal/templates/DATA_PROCESSING_AGREEMENT.md`):
   - Standard DPA clauses (GDPR Article 28):
     - Definitions and scope
     - Data controller/processor roles
     - Processing purposes and instructions
     - Data subject rights handling
     - Security measures (technical and organizational)
     - Sub-processor management
     - Data breach notification (72 hours)
     - Data transfer mechanisms (SCCs, adequacy decisions)
     - Audit rights and compliance
     - Liability and indemnification
     - Term and termination
   - LUKHAS-specific addendum:
     - Processing activities table
     - Data categories processed
     - Technical security measures
     - Sub-processors list
   - Placeholders for customer details
   - Signature blocks

2. **Data Protection Impact Assessment Template** (`legal/templates/DATA_PROTECTION_IMPACT_ASSESSMENT.md`):
   - DPIA framework (GDPR Article 35):
     - Executive summary
     - Processing activity description
     - Necessity and proportionality assessment
     - Risk identification matrix
     - Risk mitigation measures
     - Data subject consultation
     - Sign-off and approval process
   - Risk assessment matrix:
     - Likelihood (low, medium, high)
     - Impact (low, medium, high)
     - Risk score (1-9)
     - Residual risk after mitigation
   - LUKHAS processing activities:
     - Reasoning trace storage
     - Memory persistence
     - Analytics collection
     - Feature flag targeting
   - Pre-filled with common scenarios

3. **Sub-Processors List** (`legal/SUB_PROCESSORS.md`):
   - Current sub-processors:
     - Cloud providers (AWS, Google Cloud, Azure)
     - Analytics (self-hosted, not third-party)
     - Email (SendGrid, Mailgun)
     - Monitoring (Prometheus, Grafana self-hosted)
   - For each sub-processor:
     - Name and description
     - Processing purpose
     - Data categories accessed
     - Location and data transfer mechanism
     - Security certifications (SOC 2, ISO 27001)
     - DPA status
   - Update process (30-day notice requirement)

4. **Processing Activities Record (Article 30)** (`legal/PROCESSING_ACTIVITIES_RECORD.md`):
   - Table format:
     - Processing activity name
     - Purpose
     - Legal basis (consent, contract, legitimate interest)
     - Data categories
     - Data subjects
     - Recipients
     - Data retention period
     - Security measures
   - LUKHAS processing activities:
     - User authentication and access control
     - Reasoning trace generation and storage
     - Memory fold persistence
     - Analytics and telemetry
     - Feature flag evaluation
     - Launch playbook execution

5. **Data Transfer Impact Assessment** (`legal/DATA_TRANSFER_IMPACT_ASSESSMENT.md`):
   - For international data transfers:
     - Transfer mechanism used (SCCs, BCRs, adequacy decision)
     - Third country assessment
     - Supplementary measures
     - Legal advice record
   - LUKHAS specific:
     - EU → US transfers (Privacy Shield alternative)
     - Encryption in transit and at rest
     - Access controls and audit logs

6. **Customer-Facing GDPR Documentation** (`docs/legal/GDPR_COMPLIANCE.md`):
   - How LUKHAS ensures GDPR compliance
   - Data processing transparency
   - Data subject rights (access, deletion, portability)
   - Contact information for DPO (Data Protection Officer)
   - Privacy policy summary
   - Cookie policy (analytics consent)

7. **DPA Generator Tool** (`tools/generate_dpa.py`):
   - Interactive CLI tool:
     - Input: customer name, address, contact
     - Generates: Customized DPA from template
     - Output: PDF and Markdown
   - Pre-fills LUKHAS details
   - Validates required fields
   - Option to include LUKHAS addendum

8. **DPIA Generator Tool** (`tools/generate_dpia.py`):
   - Interactive CLI tool:
     - Input: processing activity details
     - Generates: Customized DPIA from template
     - Risk assessment questionnaire
     - Output: PDF and Markdown
   - Pre-filled risk scenarios
   - Mitigation suggestions database

**Legal Requirements** (MUST comply):
- ✅ GDPR Article 28 (Controller-Processor) compliance
- ✅ GDPR Article 35 (DPIA) compliance
- ✅ GDPR Article 30 (Records of Processing) compliance
- ✅ Standard Contractual Clauses (SCCs) references
- ✅ 72-hour breach notification clause
- ✅ Data subject rights handling procedures
- ✅ Legal review required before use with customers

**Integration Requirements**:
- Add to `docs/legal/` directory
- Link from main README and `docs/README.md`
- Add to Phase 3 tracking
- Add note: "For template use only - legal review required"

**Acceptance Criteria**:
- DPA template with all GDPR Article 28 requirements
- DPIA template with risk assessment matrix
- Sub-processors list with security certifications
- Processing activities record (Article 30)
- Data transfer impact assessment
- Customer-facing GDPR documentation
- 2 generator tools (DPA, DPIA) with PDF export
- Disclaimer: "Requires legal review before use"

**T4 Commit Message**:
```
feat(legal): add DPA and DPIA templates for GDPR compliance

Problem:
- Missing Data Processing Agreement (DPA) for enterprise customers
- No Data Protection Impact Assessment (DPIA) template
- Sub-processors not documented
- Processing activities record (Article 30) incomplete

Solution:
- Created comprehensive DPA template (GDPR Article 28 compliant)
- Built DPIA template with risk assessment matrix
- Documented sub-processors with security certifications
- Created processing activities record (Article 30)
- Added data transfer impact assessment
- Built customer-facing GDPR compliance documentation
- Implemented DPA and DPIA generator tools (PDF export)

Impact:
- GDPR-compliant legal templates ready for customer use
- Reduced legal review time (pre-structured templates)
- Sub-processor transparency for customer trust
- Processing activities documented per Article 30
- Risk assessment framework for new features
- GAPS E12 complete (12/19 items → 13/19 = 68.4%)

Closes: GAPS-E12
Security-Impact: Establishes GDPR compliance framework
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(legal): add DPA and DPIA templates for GDPR compliance (GAPS E12)"

**Validation**: Legal review required before use with customers (add disclaimer)
```

---

## Post-Execution Checklist

- [ ] PR created and numbered
- [ ] PR reviewed for legal accuracy
- [ ] All templates complete
- [ ] DPA template validated (GDPR Article 28)
- [ ] DPIA template validated (Article 35)
- [ ] Sub-processors list complete
- [ ] Processing activities record complete (Article 30)
- [ ] Generator tools tested (DPA, DPIA)
- [ ] Legal review scheduled
- [ ] Disclaimer added
- [ ] PR merged with squash
- [ ] Branch deleted
- [ ] Update GAPS progress to 13/19 (68.4%)

---

**Session Created**: 2025-11-08
**Ready to Execute**: Yes

---

## Important Notes

⚠️ **LEGAL DISCLAIMER**: These templates are for initial structure only and MUST be reviewed by qualified legal counsel before use with actual customers. GDPR compliance requires professional legal advice tailored to specific circumstances.
