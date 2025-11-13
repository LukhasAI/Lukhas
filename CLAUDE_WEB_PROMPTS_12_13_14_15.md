# Claude Code Web - Prompts 12, 13, 14, 15 (Phase 3: Content & Experience)

**Date**: 2025-11-08
**Phase**: 3 - Content & Experience
**Repository**: https://github.com/LukhasAI/Lukhas
**Session Type**: Claude Code Web (claude.ai/code)

---

## Overview

Phase 3 focuses on **Content & Experience** with four priority-0 GAPS items that improve product safety, developer onboarding, SEO strategy, and legal compliance. These prompts complete the remaining P0 items before moving to P1/P2 enhancements.

### Phase 3 Goals

- **B4**: Reasoning Lab Safety Controls - Privacy-preserving demo mode
- **B6**: 5-minute Reproducible Demo - Zero-config developer onboarding
- **A2**: SEO Pillars + Content Clusters - Content strategy for organic growth
- **E12**: DPA/DPIA Templates - Legal compliance documentation

### Execution Order

1. **Prompt 12** (B4: Reasoning Lab Safety) - Critical for product demo safety
2. **Prompt 13** (B6: Reproducible Demo) - Essential for developer adoption
3. **Prompt 14** (A2: SEO Content Strategy) - Long-term organic growth
4. **Prompt 15** (E12: Legal Templates) - Compliance foundation

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
```

---

# Prompt 12: Reasoning Lab Safety Controls (GAPS B4)

**Estimated Time**: 90 minutes
**Priority**: P0 (Product Safety)
**GAPS Item**: B4 - Reasoning Lab Safety Controls
**Effort**: 2 weeks of manual work → 90 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

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

# Prompt 13: 5-Minute Reproducible Demo (GAPS B6)

**Estimated Time**: 75 minutes
**Priority**: P0 (Developer Experience)
**GAPS Item**: B6 - 5-minute Reproducible Demo
**Effort**: 2 weeks of manual work → 75 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

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

# Prompt 14: SEO Pillars + Content Clusters (GAPS A2)

**Estimated Time**: 60 minutes
**Priority**: P0 (Content Strategy)
**GAPS Item**: A2 - SEO Pillars + Content Clusters
**Effort**: 3 weeks of manual work → 60 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

---

**Task**: Design SEO Pillars + Content Clusters for GAPS A2

**Goal**: Create comprehensive content strategy with pillar pages, content clusters, and internal linking optimization to drive organic search traffic across 5 LUKHAS domains.

**Background**:
- 5 production domains need coordinated content strategy
- Current content is fragmented, no clear topic clustering
- Missing pillar pages for core topics
- Internal linking not optimized for SEO
- GAPS Item: A2 from GAPS_ANALYSIS.md

**Deliverables**:

1. **Content Strategy Document** (`branding/seo/CONTENT_STRATEGY.md`):
   - 5 pillar pages identified:
     - Pillar 1: "Consciousness-Inspired AI" (lukhas.ai)
     - Pillar 2: "MATRIZ Cognitive Engine" (lukhas.dev)
     - Pillar 3: "Enterprise AI Solutions" (lukhas.com)
     - Pillar 4: "Quantum-Bio Computing" (lukhas.eu)
     - Pillar 5: "AI Safety & Ethics" (lukhas.app)
   - Content cluster map (10-15 supporting articles per pillar)
   - Internal linking strategy
   - Keyword research (primary, secondary, long-tail)
   - Target personas and search intent

2. **Pillar Page Templates** (`branding/templates/pillar_page.md`):
   - Comprehensive structure (2000-3000 words):
     - Hero section with value proposition
     - Table of contents with anchor links
     - Core concept explanation
     - Sub-topic sections (link to cluster content)
     - Visual diagrams and infographics
     - Case studies and examples
     - FAQ section
     - Related resources
     - CTA (call-to-action)
   - Front-matter with SEO metadata
   - Schema.org markup for rich snippets

3. **Content Cluster Generator** (`tools/generate_content_cluster.py`):
   - Input: pillar topic, keyword, target word count
   - Generates:
     - Outline for pillar page
     - 10-15 cluster article ideas with titles
     - Keyword map (primary/secondary per article)
     - Internal linking suggestions
     - Content calendar (publishing schedule)
   - Output: YAML file with full cluster spec

4. **Internal Linking Optimizer** (`tools/optimize_internal_links.py`):
   - Analyzes existing content for linking opportunities
   - Suggests relevant internal links based on:
     - Keyword overlap
     - Topic relevance (NLP similarity)
     - User journey mapping
   - Generates anchor text suggestions (contextual, natural)
   - Validates link health (no broken links, orphan pages)
   - Output: Markdown report with suggested additions

5. **Keyword Research Tool** (`tools/keyword_research.py`):
   - Integrates with existing `branding/seo/canonical_map.yaml`
   - Generates keyword clusters:
     - Primary keywords (high volume, competitive)
     - Secondary keywords (medium volume, moderate difficulty)
     - Long-tail keywords (low volume, low competition, high intent)
   - Keyword difficulty scoring (1-100)
   - Search volume estimates
   - Competitor analysis (top 10 ranking pages)
   - Output: JSON with keyword data

6. **Content Cluster Tracker** (`branding/seo/content_clusters.yaml`):
   - YAML file tracking:
     - Pillar page status (draft, review, published)
     - Cluster articles (planned, in-progress, published)
     - Internal links added
     - Performance metrics (traffic, rankings, conversions)
   - Progress visualization (ASCII art progress bars)

7. **Pillar Page Examples** (`branding/websites/{domain}/pillars/`):
   - Create 1 complete pillar page per domain:
     - `lukhas.ai/pillars/consciousness_ai.md` - Consciousness-Inspired AI
     - `lukhas.dev/pillars/matriz_engine.md` - MATRIZ Cognitive Engine
     - `lukhas.com/pillars/enterprise_solutions.md` - Enterprise AI Solutions
     - `lukhas.eu/pillars/quantum_bio.md` - Quantum-Bio Computing
     - `lukhas.app/pillars/ai_safety.md` - AI Safety & Ethics
   - Each with:
     - 2000+ words
     - 10+ internal links
     - Schema.org markup
     - Visual diagrams
     - Evidence links

8. **Validation & Analytics** (`tools/validate_content_strategy.py`):
   - Validates:
     - Pillar pages have 10+ cluster articles
     - Internal linking follows best practices (3-5 per page)
     - No orphan pages (every page linked from at least 2 others)
     - Keyword cannibalization detection
   - Reports:
     - Content coverage gaps
     - Link equity distribution
     - Keyword opportunity score

**Integration Requirements**:
- Add to `.github/workflows/content-lint.yml` as content strategy validation
- Add `make content-strategy-validate` target to Makefile
- Link from `branding/governance/README.md`
- Update `branding/seo/canonical_map.yaml` with pillar pages

**Acceptance Criteria**:
- 5 pillar pages created (1 per domain, 2000+ words each)
- Content cluster map with 50-75 article ideas
- Internal linking strategy documented
- Keyword research tool generating clusters
- Content cluster tracker with progress visualization
- Validation tool checking linking and coverage
- CI/CD integration working

**T4 Commit Message**:
```
feat(seo): add pillar pages and content cluster strategy

Problem:
- Fragmented content across 5 domains without strategy
- Missing pillar pages for core topics
- Internal linking not optimized
- No content cluster planning

Solution:
- Created comprehensive content strategy (5 pillars, 50-75 clusters)
- Built pillar page template with SEO best practices
- Implemented content cluster generator tool
- Added internal linking optimizer (analyzes and suggests)
- Created keyword research tool with difficulty scoring
- Built content cluster tracker with progress visualization
- Generated 5 example pillar pages (2000+ words each)
- Validation tool for coverage and linking

Impact:
- Clear content roadmap for organic growth
- 5 pillar pages targeting high-value keywords
- 50-75 cluster articles planned
- Internal linking optimized for SEO
- Content calendar for next 6 months
- GAPS A2 complete (11/19 items → 12/19 = 63.2%)

Closes: GAPS-A2
LLM: model=claude-sonnet-4-5, temp=1.0, ts=2025-11-08
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR** with title: "feat(seo): add pillar pages and content cluster strategy (GAPS A2)"

**Validation**: Run `make content-strategy-validate` before creating PR
```

---

# Prompt 15: DPA/DPIA Templates (GAPS E12)

**Estimated Time**: 45 minutes
**Priority**: P0 (Legal Compliance)
**GAPS Item**: E12 - DPA/DPIA Templates
**Effort**: 2 weeks of manual work → 45 min automated

## Prompt Text (Ready to Paste)

```
**LUKHAS Project Context**:
[Paste full LUKHAS policies header from above]

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

## Execution Checklist

### Before Starting
- [ ] Review Phase 2 completion document (`BRANDING_GOVERNANCE_PHASE2_COMPLETE.md`)
- [ ] Verify Phase 2 PR merged (#1144)
- [ ] Check current GAPS progress (9/19 items = 47.4%)

### Prompt 12 Execution (Reasoning Lab Safety)
- [ ] Copy LUKHAS policies + Prompt 12 text
- [ ] Paste into Claude Code Web (https://claude.ai/code)
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Test redaction on sample reasoning traces
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify `make reasoning-lab-safety-check` passes

### Prompt 13 Execution (5-Minute Demo)
- [ ] Copy LUKHAS policies + Prompt 13 text
- [ ] Paste into Claude Code Web
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Test `scripts/quickstart.sh` on clean VM (must be < 5 min)
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify all 5 examples run successfully

### Prompt 14 Execution (SEO Content Strategy)
- [ ] Copy LUKHAS policies + Prompt 14 text
- [ ] Paste into Claude Code Web
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Validate pillar pages (2000+ words each)
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Verify `make content-strategy-validate` passes

### Prompt 15 Execution (Legal Templates)
- [ ] Copy LUKHAS policies + Prompt 15 text
- [ ] Paste into Claude Code Web
- [ ] Wait for PR creation
- [ ] Review PR #XXXX
- [ ] Schedule legal review of templates
- [ ] Merge with `gh pr merge XXXX --squash --admin --delete-branch`
- [ ] Add disclaimer: "Legal review required"

### After All Prompts
- [ ] Update `BRANDING_GOVERNANCE_PHASE2_COMPLETE.md` to `BRANDING_GOVERNANCE_PHASE3_COMPLETE.md`
- [ ] Update GAPS progress to 13/19 items (68.4%)
- [ ] Create tracking issue for Phase 3 completion
- [ ] Create Prompts 16-19 for Phase 4 (if continuing)

---

## Expected Results

### Phase 3 Metrics (After Prompts 12-15)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| GAPS Items Complete | 9/19 (47.4%) | 13/19 (68.4%) | +4 ✅ |
| PRs Merged | 10 | 14 | +4 |
| Total Lines Added | ~47,000 | ~52,000 | +5,000 est. |
| Validation Tools | 10 | 14 | +4 |
| Product Readiness | Medium | High | Launch-ready |

### Time Savings

| Task | Manual | Automated | Savings |
|------|--------|-----------|---------|
| Reasoning Lab Safety | 2 weeks | 90 min | 94% |
| 5-Minute Demo | 2 weeks | 75 min | 95% |
| SEO Content Strategy | 3 weeks | 60 min | 98% |
| Legal Templates | 2 weeks | 45 min | 96% |
| **Total** | **9 weeks** | **4.5 hours** | **96.5%** |

### Quality Improvements

- ✅ Privacy-preserving demo mode
- ✅ Developer onboarding in under 5 minutes
- ✅ SEO content strategy with 5 pillars
- ✅ GDPR-compliant legal templates
- ✅ Comprehensive testing
- ✅ Complete documentation

---

## Success Criteria

### Phase 3 Complete When:
- ✅ All 4 prompts executed successfully
- ✅ All 4 PRs merged to main
- ✅ All validation tools passing in CI/CD
- ✅ GAPS progress: 13/19 items (68.4%)
- ✅ Quickstart completes in < 5 minutes on clean VM
- ✅ Legal templates reviewed and approved
- ✅ Documentation updated
- ✅ Tracking issue created
- ✅ Ready for Phase 4 planning (P1 items)

---

**Document Owner**: @web-architect
**Created**: 2025-11-08 19:15:00Z
**Session**: Branding Governance Phase 3 Planning
**Estimated Total Time**: 4.5 hours (270 minutes)

