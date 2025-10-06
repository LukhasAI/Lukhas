---
status: wip
type: documentation
---
# LUKHAS AI GitHub Labels

Consistent labeling system for issues and pull requests to enable effective triage and AI connector discovery.

## Area Labels (area:*)

### Core Systems
- **`area:core`** - LUKHAS core systems and GLYPH engine
- **`area:matriz`** - MATRIZ symbolic processing and envelopes
- **`area:memory`** - Memory systems, folds, and temporal processing
- **`area:consciousness`** - Consciousness, awareness, and reflection systems
- **`area:orchestration`** - Brain Hub coordination and module orchestration

### Security & Governance
- **`area:ethics`** - Guardian system, ethics validation, and safety
- **`area:identity`** - Authentication, authorization, and Lambda ID
- **`area:governance`** - Governance frameworks and policy systems
- **`area:security`** - Security, encryption, and threat detection

### Infrastructure & Operations
- **`area:api`** - API endpoints, routes, and external interfaces
- **`area:infrastructure`** - Deployment, containers, and infrastructure
- **`area:monitoring`** - Observability, metrics, and alerting
- **`area:ci-cd`** - Continuous integration and deployment
- **`area:performance`** - Performance optimization and benchmarking

### Development & Quality
- **`area:testing`** - Test frameworks, fixtures, and test automation
- **`area:documentation`** - Documentation, guides, and README files
- **`area:tooling`** - Development tools and utilities
- **`area:hygiene`** - Code quality, linting, and formatting

## Lane Labels (lane:*)

### Development Lanes
- **`lane:experimental`** - Experimental research and prototyping
- **`lane:candidate`** - Candidate features under evaluation
- **`lane:production`** - Production-ready and stable systems

## Safety Labels (safety:*)

### Risk Assessment
- **`safety:critical`** - Critical safety impact, requires immediate attention
- **`safety:high`** - High safety impact, review required
- **`safety:medium`** - Medium safety impact, standard review
- **`safety:low`** - Low safety impact, minimal review needed

### Guardian System
- **`safety:guardian`** - Related to Guardian system functionality
- **`safety:drift`** - Behavioral drift detection and correction
- **`safety:ethics`** - Ethical validation and compliance

## Oneiric Labels (oneiric:*)

### Dream & Creativity Systems
- **`oneiric:dream`** - Dream engine and reality simulation
- **`oneiric:creativity`** - Creative problem solving and generation
- **`oneiric:chaos`** - Controlled chaos and pattern emergence
- **`oneiric:research`** - Oneiric system research and experimentation

## Type Labels

### Issue Types
- **`type:bug`** - Something isn't working correctly
- **`type:feature`** - New feature or enhancement request
- **`type:improvement`** - Improvement to existing functionality
- **`type:documentation`** - Documentation related changes
- **`type:question`** - Questions about usage or implementation
- **`type:epic`** - Large feature or initiative spanning multiple issues

### Work Types
- **`type:research`** - Research and investigation work
- **`type:refactoring`** - Code refactoring and restructuring
- **`type:maintenance`** - Maintenance and housekeeping tasks
- **`type:migration`** - Migration and upgrade work
- **`type:deprecation`** - Deprecation and sunset activities

## Priority Labels

### Priority Levels
- **`priority:critical`** - Critical issues requiring immediate attention
- **`priority:high`** - High priority, address in current sprint
- **`priority:medium`** - Medium priority, address in upcoming sprints
- **`priority:low`** - Low priority, address when capacity allows
- **`priority:backlog`** - Backlog items for future consideration

## Status Labels

### Development Status
- **`status:triage`** - Needs triage and initial assessment
- **`status:planning`** - In planning phase
- **`status:in-progress`** - Currently being worked on
- **`status:review`** - Under review
- **`status:blocked`** - Blocked by external dependencies
- **`status:on-hold`** - On hold pending decisions

### Resolution Status
- **`status:wontfix`** - Will not be fixed or implemented
- **`status:duplicate`** - Duplicate of another issue
- **`status:invalid`** - Invalid issue or request

## Component Labels

### Specific Components
- **`component:brain-hub`** - Brain Hub orchestration system
- **`component:guardian`** - Guardian ethics and safety system
- **`component:glyph-engine`** - GLYPH symbolic processing engine
- **`component:lambda-id`** - Lambda ID identity system
- **`component:webauthn`** - WebAuthn authentication
- **`component:consent-ledger`** - Consent and privacy ledger

## Special Labels

### Special Handling
- **`good first issue`** - Good for newcomers to the project
- **`help wanted`** - Extra attention is needed
- **`needs feedback`** - Feedback from community is needed
- **`breaking change`** - Contains breaking changes
- **`security`** - Security-related issue (private by default)

### AI/Bot Labels
- **`ai-assisted`** - Created or modified with AI assistance
- **`connector-friendly`** - Optimized for AI connector interaction
- **`automated`** - Automated issue or PR
- **`bot:dependencies`** - Dependency update from bot

## Label Usage Guidelines

### Required Labels
Every issue/PR should have:
1. One `area:*` label
2. One `type:*` label
3. One `priority:*` label (for issues)
4. One `lane:*` label (if applicable)

### Safety-Critical Guidelines
Issues affecting these areas **must** include `safety:*` labels:
- Guardian system
- Ethics validation
- Identity/authentication
- Core GLYPH engine
- Memory system integrity

### Triage Process
1. **New Issue** → Add `status:triage`
2. **Initial Review** → Add `area:*`, `type:*`, `priority:*`
3. **Safety Assessment** → Add `safety:*` if applicable
4. **Assignment** → Add `status:in-progress`, remove `status:triage`

## Label Color Scheme

### Area Labels
- **Core Systems**: Blue (#0052CC)
- **Security/Safety**: Red (#D73A4A)
- **Infrastructure**: Purple (#5319E7)
- **Development**: Green (#0E8A16)

### Priority Labels
- **Critical**: Dark Red (#B60205)
- **High**: Orange (#D93F0B)
- **Medium**: Yellow (#FBCA04)
- **Low**: Light Green (#7ED321)

### Status Labels
- **Active States**: Blue variants
- **Blocked/Hold**: Gray (#6A737D)
- **Resolution**: Green variants

## Automation

### Auto-Labeling Rules
- PRs touching `/ethics/**` → `area:ethics`, `safety:high`
- PRs touching `/tests/**` → `area:testing`
- Issues with "bug" in title → `type:bug`
- Issues with "feature" in title → `type:feature`
- Dependabot PRs → `bot:dependencies`, `area:infrastructure`

### Label Sync
Labels are synced via `.github/labels.yml` configuration for consistency across repositories.

---

*This labeling system enables effective issue triage, PR review assignment, and AI connector discovery of relevant discussions and development activities.*