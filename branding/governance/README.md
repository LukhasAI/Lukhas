# LUKHAS Branding Governance System

> **🛡️ Quality Assurance, Compliance & Automation for LUKHAS Branding**

**Last Updated**: 2025-11-06
**Status**: Active - Governance Framework

---

## Overview

This directory contains governance tools, policies, and automation for maintaining quality, accessibility, and legal compliance across all LUKHAS branding content.

---

## 📁 Directory Structure

```
governance/
├── README.md (this file)
├── strategic/                # Strategic planning & audit results
│   ├── T4_STRATEGIC_AUDIT.md     # Executive audit summary
│   ├── GAPS_ANALYSIS.md          # 19 missing components
│   ├── 90_DAY_ROADMAP.md         # Week-by-week execution plan
│   └── INNOVATION_PIPELINE.md    # Breakthrough ideas
├── launch/                   # Launch playbooks & coordination (GAPS A3)
│   ├── PLAYBOOK_TEMPLATE.md      # Comprehensive launch workflow
│   ├── FEATURE_CHECKLIST.md      # Readiness checklist (tech, marketing, legal)
│   ├── TIMELINE_TEMPLATE.md      # Gantt chart format for milestones
│   ├── LAUNCH_TYPES.md           # 4 launch types (product, feature, infra, content)
│   └── examples/
│       └── reasoning_lab_launch.md  # Real-world example
├── tools/                    # Validation & automation scripts
│   ├── CONTENT_LINTING.md   # Front-matter, evidence, vocab linting
│   └── GOVERNANCE_ARTIFACTS.md  # Additional governance tools
├── workflows/                # GitHub Actions CI/CD
├── policies/                 # Governance policies
└── research/                 # User research & testing plans
```

---

## 📊 Strategic Planning & Audit Results

**Status**: ✅ **COMPLETED** (2025-11-06)

### T4 Strategic Audit

**Location**: [strategic/T4_STRATEGIC_AUDIT.md](strategic/T4_STRATEGIC_AUDIT.md)

Comprehensive external audit evaluating LUKHAS branding across 8 dimensions (Content, UX, Design, Technical, Legal, Community, Operations, Measurement). Overall score: **6.0/10** - Strong foundation with operational gaps.

**Key Findings**:
- ✅ Excellent governance frameworks and assistive systems
- ⚠️ 19 missing components blocking enterprise readiness
- ⚠️ Legal compliance gaps (EU DPA/DPIA, privacy analytics)
- ⚠️ Evidence operationalization needed

### Implementation Plans

1. **[GAPS_ANALYSIS.md](strategic/GAPS_ANALYSIS.md)** - Complete analysis of 19 missing components
   - Priority distribution: 11 P0 (critical), 5 P1 (high), 3 P2 (medium)
   - Owner assignments and deliverables
   - Dependencies and sequencing

2. **[90_DAY_ROADMAP.md](strategic/90_DAY_ROADMAP.md)** - Week-by-week execution plan
   - 4 phases: Foundations → Product Experience → Trust & Legal → Scale & Growth
   - Weekly check-in agenda
   - Success metrics and risk mitigation

3. **[INNOVATION_PIPELINE.md](strategic/INNOVATION_PIPELINE.md)** - 4 breakthrough ideas
   - Audit-as-a-Service (AaaS)
   - Reasoning Graph Marketplace
   - Explainability-as-a-Standard
   - MATRIZ Research Fellowship

**Next Steps**: Execute 90-day roadmap starting with evidence pages, artifact signing, and SEO hygiene.

---

## 🚀 Launch Playbooks & Coordination

**Status**: ✅ **COMPLETED** (2025-11-08)
**GAPS Item**: A3 - Launch Playbooks

### Overview

Launch playbooks provide standardized templates and checklists for coordinating cross-functional launches (product, feature, infrastructure, content). These ensure smooth alignment between marketing and engineering teams.

**Location**: [launch/](launch/)

**Key Documents**:
1. **[PLAYBOOK_TEMPLATE.md](launch/PLAYBOOK_TEMPLATE.md)** - Comprehensive launch workflow
   - Pre-launch checklist (T-30, T-14, T-7, T-1 days)
   - Launch day runbook with rollback procedures
   - Post-launch review template
   - Cross-functional stakeholder map (engineering, marketing, legal, security)
   - Communication templates (internal announcements, external blog posts, social)
   - Success metrics and KPI tracking

2. **[FEATURE_CHECKLIST.md](launch/FEATURE_CHECKLIST.md)** - Readiness checklist
   - Technical readiness (tests, docs, monitoring, feature flags)
   - Marketing readiness (landing page, blog post, social assets)
   - Legal/compliance readiness (privacy review, claims approval, evidence pages)
   - Security readiness (audit, penetration testing, compliance)
   - Analytics readiness (event tracking, dashboards, alerts)

3. **[TIMELINE_TEMPLATE.md](launch/TIMELINE_TEMPLATE.md)** - Gantt chart format
   - Milestone tracking (alpha, beta, GA)
   - Dependencies and blockers tracking
   - Risk assessment and mitigation

4. **[LAUNCH_TYPES.md](launch/LAUNCH_TYPES.md)** - Launch type definitions
   - Major product launch (e.g., Reasoning Lab)
   - Feature launch (e.g., new API endpoint)
   - Infrastructure launch (e.g., new region)
   - Content launch (e.g., evidence pages, documentation)

### Example Launch

**[Reasoning Lab Launch](launch/examples/reasoning_lab_launch.md)** - Real-world example showing how to use the playbook template for a major product launch.

### Validation

```bash
# Validate all launch playbooks
make launch-validate

# Validate specific playbook
python3 tools/validate_launch.py --playbook branding/governance/launch/examples/reasoning_lab_launch.md

# Strict mode (warnings = errors)
python3 tools/validate_launch.py --strict
```

**Tool**: `tools/validate_launch.py` validates:
- Required front-matter fields (launch name, type, date, lead, sponsor)
- Stakeholder map completeness
- Checklist presence (technical, marketing, legal)
- Rollback procedure documentation
- Success metrics and KPI definitions
- Risk register
- Communication templates
- Evidence page links for claims

**CI Integration**: Launch validation runs automatically in `.github/workflows/content-lint.yml` on all PRs.

---

## 🔧 Validation Tools

### Core Linters

**Location**: [tools/CONTENT_LINTING.md](tools/CONTENT_LINTING.md)

1. **front_matter_lint.py**
   - Validates required YAML front-matter fields
   - Checks tone distribution sums to ~1.0
   - Verifies assistive variants declared
   - Ensures claims_approval is boolean

2. **evidence_check.py**
   - Scans for numeric/operational claims
   - Ensures evidence_links present
   - Requires claims_approval: true for production claims
   - Exits non-zero on missing evidence

3. **branding_vocab_lint.py**
   - Enforces vocabulary standards
   - Blocks forbidden terms
   - Checks brand consistency

4. **assistive_validate.py**
   - Validates assistive mode presence for critical pages
   - Checks Flesch-Kincaid grade ≤ 8
   - Ensures readability compliance

5. **validate_flags.py** (NEW - GAPS B5)
   - Validates feature flags configuration
   - Ensures privacy compliance (no PII in configs)
   - Checks flag schema and type-specific validation
   - Integrated into CI/CD pipeline

### Additional Tools

**Location**: [tools/GOVERNANCE_ARTIFACTS.md](tools/GOVERNANCE_ARTIFACTS.md)

5. **markdown-link-check**
   - Validates internal and external links
   - Configured via `.mlc.json`

### Claims Registry

**Tools**: `tools/generate_claims_registry.py`, `tools/validate_claims.py`

Generate and validate claims across all branding content:

```bash
# Generate claims registry
make claims-registry

# Validate claims have evidence
make claims-validate

# Strict validation (fail on warnings)
make claims-strict
```

**Registry Location**: `branding/governance/claims_registry.json`

**Prerequisites**: Evidence artifacts must exist (created in PR #1102)

**Claim Types Detected**:
- Percentages: 99.7%, 87%
- Latencies: <250ms, <100ms
- Counts: 340K+ users, 3M interactions
- Multipliers: 2x faster, 50% improvement
- Operational: deployment-ready, validated production

**Output**: Generates a comprehensive JSON registry with:
- Claim text and type
- Source file and line number
- Evidence validation status
- Missing evidence warnings
- Claims approval tracking
- Verification trail (verified_by, verified_date)

**CI Integration**: Use `make claims-strict` in CI to fail builds on unapproved claims.

---

## 🤖 CI/CD Workflows

### Content Lint Workflow

**File**: `.github/workflows/content-lint.yml`

**Runs on**: Pull requests + weekly schedule

**Checks**:
- ✅ Front-matter validation
- ✅ Vocabulary compliance
- ✅ Assistive mode presence
- ✅ Evidence backing for claims
- ✅ Link integrity

### Accessibility Workflow

**File**: `.github/workflows/a11y.yml`

**Runs on**: Pull requests + weekly schedule

**Checks**:
- ✅ pa11y-ci (WCAG 2 AA)
- ✅ axe-core via Puppeteer
- ✅ Contrast ratios
- ✅ Keyboard navigation

---

## 📋 Governance Policies

### 1. Claims & Evidence Policy

**File**: `policies/CLAIMS_POLICY.md`

**Requirements**:
- All numeric claims must have evidence artifacts
- Evidence stored in `release_artifacts/`
- `evidence_links` in front-matter
- `claims_approval: true` requires web-architect + legal sign-off
- Entry in claims registry

### 2. PR Template

**File**: `.github/PULL_REQUEST_TEMPLATE/content_pr.md`

**Checklist includes**:
- Front-matter validated
- Assistive variant present
- Vocabulary linter passed
- Evidence links added
- Legal sign-off (if required)
- Alt text present

### 3. Code Owners

**File**: `.github/CODEOWNERS`

**Defines ownership**:
- Domain content
- Templates
- Brand guidelines
- Release artifacts

---

## 🔬 Research & Testing

### Assistive Mode User Testing

**Location**: `research/assistive_user_test_plan.md`

**Includes**:
- Participant recruitment (6-12 neurodiverse, 3-5 control)
- Task scenarios (30-45 min sessions)
- Metrics (success rate, time, comprehension, satisfaction)
- Consent form template
- Deliverables (1-page prioritized fixes report)

### Telemetry Specification

**Location**: `research/telemetry_spec.md`

**Privacy-aware events**:
- ui.theme_changed
- assistive_variant_viewed
- reasoning_trace_viewed
- evidence_artifact_requested
- quickstart_completed
- assistive_audio_played

**Privacy requirements**:
- No PII in events
- Aggregated for anonymous users
- Anonymized IDs for logged-in users

---

## 🎯 Feature Flags System (GAPS B5)

**Status**: ✅ **COMPLETED** (2025-11-08)

**Location**: `branding/features/FEATURE_FLAGS_GUIDE.md`

Privacy-first feature flags system for controlled rollouts, A/B testing, and safe experimentation.

**Key Features**:
- 5 flag types: boolean, percentage, user targeting, time-based, environment-based
- Zero third-party dependencies (no LaunchDarkly, Split.io)
- Privacy-preserving (no user tracking without consent)
- Gradual rollouts: 0% → 1% → 10% → 50% → 100%
- Built-in A/B testing support

**Usage**:

```bash
# Validate feature flags
make flags-validate

# Migrate from old format
make flags-migrate INPUT=old.yaml OUTPUT=new.yaml
```

**Configuration**: `branding/features/flags.yaml`

**Components**:
- Backend service: `lukhas/features/flags_service.py`
- API endpoints: `lukhas/api/features.py`
- React hook: `products/frontend/hooks/useFeatureFlag.ts`
- Admin UI: `products/frontend/pages/admin/features.tsx`
- Testing utilities: `lukhas/features/testing.py`

**CI Integration**: Automated validation in `content-lint.yml` workflow

---

## 📊 Monitoring & Dashboards

### Domain Health Dashboard

**Location**: `policies/domain_health_dashboard_spec.md`

**Per-domain KPIs**:
- Traffic (uniques, sessions)
- CTA conversions
- Quickstart success rate
- Reasoning Lab engagement
- Assistive adoption rate
- Content quality metrics
- Claims health metrics
- SEO performance

---

## 🚀 Quick Start

### Running Validators Locally

```bash
# Install dependencies
python3 -m pip install pyyaml textstat
npm install -g markdown-link-check

# Run linters
python3 tools/front_matter_lint.py
python3 tools/evidence_check.py
python3 tools/branding_vocab_lint.py
python3 tools/assistive_validate.py
python3 tools/validate_flags.py

# Check links
markdown-link-check "branding/**/*.md"
```

### Setting Up CI

1. Copy workflows to `.github/workflows/`
2. Update CODEOWNERS with team handles
3. Add PR template to `.github/PULL_REQUEST_TEMPLATE/`
4. Configure markdown-link-check (`.mlc.json`)

---

## 📖 Usage Workflows

### Adding New Content

1. **Create content** using [templates](../templates/)
2. **Add front-matter** with required fields
3. **Run linters** locally (see Quick Start)
4. **Create PR** using content_pr.md template
5. **CI validates** automatically
6. **Get reviews** from CODEOWNERS
7. **Merge** when all checks pass

### Making Claims

1. **Generate evidence** artifact (perf logs, audit PDFs)
2. **Store in** `release_artifacts/` with hash
3. **Add** `evidence_links` to front-matter
4. **Set** `claims_approval: false` initially
5. **Get sign-off** from web-architect + legal
6. **Update** to `claims_approval: true`
7. **Merge** PR

### Testing Assistive Mode

1. **Review plan** in `research/assistive_user_test_plan.md`
2. **Recruit participants** (neurodiverse + control)
3. **Run sessions** (30-45 min, recorded)
4. **Collect metrics** (success, time, comprehension)
5. **Generate report** (top 5 issues, prioritized)
6. **Iterate** on fixes

---

## 🔍 Finding Information

**"What's the strategic plan for LUKHAS branding?"**
→ [strategic/T4_STRATEGIC_AUDIT.md](strategic/T4_STRATEGIC_AUDIT.md) - Full audit and strategic vision

**"What are the missing components and priorities?"**
→ [strategic/GAPS_ANALYSIS.md](strategic/GAPS_ANALYSIS.md) - 19-item analysis with owners

**"What's the 90-day execution plan?"**
→ [strategic/90_DAY_ROADMAP.md](strategic/90_DAY_ROADMAP.md) - Week-by-week roadmap

**"What breakthrough ideas should we consider?"**
→ [strategic/INNOVATION_PIPELINE.md](strategic/INNOVATION_PIPELINE.md) - 4 visionary opportunities

**"How do I validate my content before submitting?"**
→ [tools/CONTENT_LINTING.md](tools/CONTENT_LINTING.md) - Run all linters

**"What claims require evidence?"**
→ [policies/CLAIMS_POLICY.md](policies/CLAIMS_POLICY.md) - All numeric/operational claims

**"How do I set up CI workflows?"**
→ [tools/GOVERNANCE_ARTIFACTS.md](tools/GOVERNANCE_ARTIFACTS.md) - Complete CI setup

**"What metrics should we track?"**
→ [policies/domain_health_dashboard_spec.md](policies/domain_health_dashboard_spec.md) - KPI dashboard

---

## 📞 Support

- **Governance Questions**: governance@lukhas.ai
- **Tool Issues**: dev@lukhas.ai
- **Policy Clarifications**: legal@lukhas.ai
- **Accessibility**: accessibility@lukhas.ai

---

## 🎯 Governance Principles

### 1. Evidence-Based Claims
Every metric published must be backed by verifiable evidence. No exceptions.

### 2. Accessibility First
Assistive mode is not optional for critical pages. It's a core requirement.

### 3. Human Review
Automation drafts, humans approve. Especially for assistive content and legal claims.

### 4. Privacy-Aware
Track only what's necessary. Respect user privacy. Follow GDPR/CCPA.

### 5. Continuous Validation
Governance isn't a one-time gate. Weekly CI checks ensure ongoing compliance.

---

## 📜 Version History

**v1.0** (2025-11-06)
- Initial governance framework
- Core linting tools
- CI workflows
- Claims policy
- Research plans
- Dashboard specs

---

**🛡️ Remember**: Governance is what separates amateur marketing from enterprise-grade, trustworthy brand communication. These tools exist to protect both users and the business.
