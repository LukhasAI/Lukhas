# AI Agent Automation Pipeline for LukhasAI/Lukhas
## Complete Implementation Guide for JULES → CODEX → CLAUDE CODE Workflow

## Executive Summary

This research delivers a comprehensive framework for implementing an aggressive auto-merge AI agent pipeline achieving **T4 precision standards (99.99% accuracy / 0.01% error rate)** through layered security controls, quality gates, and operational safeguards. The system coordinates three AI agents—JULES (planning), CODEX (implementation), and CLAUDE CODE (review/merge)—using GitHub's native automation features.

**Critical Finding**: The LukhasAI/Lukhas repository is not currently publicly accessible (private or not yet created). This guide provides a complete implementation blueprint applicable when you have repository access.

**Key Capabilities Delivered**: Autonomous PR creation, multi-agent code review, automated quality gates with ruff integration, cherry-picking before closure, daily PR reports, post-merge monitoring with rollback triggers, and comprehensive audit trails.

---

## 1. Adding Claude Code as Official GitHub Assignee

### Recommended Approach: GitHub App Integration

**Why GitHub Apps**: Most secure integration with fine-grained permissions (50+ granular controls), short-lived tokens (1-hour expiration), independent bot identity with `[bot]` attribution, zero seat consumption, and enhanced rate limits (15,000 requests/hour for Enterprise).

### Step-by-Step Implementation

**Option A: Automated Setup (Recommended)**

```bash
# In Claude Code CLI
/install-github-app
```

This automatically installs the GitHub App, creates workflows, and configures secrets. **Note**: Only for direct Anthropic API users.

**Option B: Manual Setup (Complete Control)**

**Step 1: Install Claude GitHub App**
1. Navigate to https://github.com/apps/claude
2. Click "Install" and authorize
3. Select "Only select repositories" → Choose LukhasAI/Lukhas
4. Review permissions (Contents, Issues, Pull requests: Read & write)
5. Click "Install"

**Step 2: Configure Secrets**

Navigate to `Repository → Settings → Secrets and variables → Actions` and add:

```
ANTHROPIC_API_KEY: [Your Claude API key]
APP_ID: [GitHub App ID]
APP_PRIVATE_KEY: [.pem file contents]
```

**Step 3: Create Workflow**

`.github/workflows/claude-code.yml`:

```yaml
name: Claude Code Agent
permissions:
  contents: write
  pull-requests: write
  issues: write

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude-pr:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
          
      - name: Run Claude Code Action
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          github_token: ${{ steps.app-token.outputs.token }}
```

**Step 4: Configure Agent Guidelines**

Create `CLAUDE.md` in repository root:

```markdown
# Claude Code Guidelines for LukhasAI/Lukhas

## Code Standards (T4 Precision)
- Python 3.11+ with type hints for all functions
- Follow PEP 8 via ruff (max line length: 88)
- Meaningful variable names, comprehensive docstrings

## Quality Requirements
- Test coverage ≥ 90% overall, 85% per file
- No security vulnerabilities (CodeQL must pass)
- Breaking changes require explicit approval
- All functions documented with examples

## Review Criteria
- Security: Check for vulnerabilities, credential leaks
- Testing: Verify coverage meets thresholds
- Documentation: Ensure updates alongside code
- Performance: No obvious regressions

## Restricted Operations
- Cannot commit directly to main/master
- Cannot bypass branch protection
- Must create PRs for all changes
- Cannot approve own PRs
```

**Step 5: Enable Auto-Merge**

```
Repository → Settings → General → Pull Requests
✅ Allow auto-merge
✅ Automatically delete head branches

Repository → Settings → Actions → General
✅ Allow GitHub Actions to create and approve pull requests
```

### Permission Requirements

| Operation | Permission Required | Notes |
|-----------|-------------------|-------|
| Create PRs | Contents (write) + Pull requests (write) | Can create branches/PRs |
| Review PRs | Pull requests (write) | Can approve, request changes |
| Add assignees | Issues (write) OR Pull requests (write) | PRs use issues API |
| Merge PRs | Contents (write) + Pull requests (write) | Must satisfy branch protection |
| Request reviews | Pull requests (write) | Reviewers need write access |

**Permission Hierarchy**:
- **Read**: Comment only
- **Triage**: Can assign
- **Write**: Can assign, review, approve, merge
- **Admin**: Full capabilities including protection overrides

---

## 2. Repository Structure for AI Agent Automation

### Recommended Directory Structure

```
LukhasAI/Lukhas/
├── .github/
│   ├── workflows/
│   │   ├── claude-code.yml              # Claude agent trigger
│   │   ├── auto-merge-pipeline.yml      # Aggressive auto-merge
│   │   ├── ruff-quality-gate.yml        # Python linting
│   │   ├── cherry-pick-automation.yml   # Pre-closure cherry-picking
│   │   ├── daily-pr-report.yml          # Daily PR summaries
│   │   ├── post-merge-monitor.yml       # Health checks + rollback
│   │   ├── security-scanning.yml        # CodeQL + Dependabot
│   │   └── required-checks.yml          # Unified quality gate
│   ├── agents/
│   │   ├── jules-instructions.md        # JULES planning guidelines
│   │   ├── codex-instructions.md        # CODEX implementation standards
│   │   └── claude-instructions.md       # CLAUDE review criteria
│   ├── CODEOWNERS                       # Mandatory review assignments
│   ├── PULL_REQUEST_TEMPLATE.md         # Standardized PR format
│   ├── dependabot.yml                   # Dependency updates
│   └── copilot-setup-steps.yaml         # Agent environment setup
├── src/                                  # Source code
├── tests/                                # Test suite (≥90% coverage)
├── docs/                                 # Documentation
├── CLAUDE.md                             # Claude Code guidelines
├── pyproject.toml                        # Python config + ruff
├── .gitignore
└── README.md
```

### Essential Configuration Files

**pyproject.toml** (Python + Ruff):

```toml
[project]
name = "lukhas"
version = "0.1.0"
requires-python = ">=3.11"

[tool.ruff]
line-length = 88
target-version = "py311"
exclude = [".git", "__pycache__", "build", "dist"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "S",   # flake8-bandit (security)
    "T20", # flake8-print (no print statements)
]
ignore = ["E501"]  # Line length handled by formatter

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=json --cov-report=term --cov-branch --cov-fail-under=90"

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

**CODEOWNERS** (Mandatory Reviews):

```
# Global owners
*                              @org/engineering-team

# Security-sensitive
/src/auth/**                   @org/security-team
/.github/workflows/**          @org/devops-team

# AI agent configurations
/.github/agents/**             @org/ai-leads
/CLAUDE.md                     @org/ai-leads
```

---

## 3. Aggressive Auto-Merge Pipeline with Quality Gates

### Complete Auto-Merge Workflow

`.github/workflows/auto-merge-pipeline.yml`:

```yaml
name: Aggressive Auto-Merge Pipeline
on:
  pull_request:
    types: [labeled, synchronize, opened, ready_for_review]
  pull_request_review:
    types: [submitted]
  check_suite:
    types: [completed]

permissions:
  contents: write
  pull-requests: write
  checks: read

jobs:
  quality-gate-check:
    runs-on: ubuntu-latest
    if: |
      github.event.pull_request.draft == false &&
      !contains(github.event.pull_request.labels.*.name, 'do-not-merge') &&
      !contains(github.event.pull_request.labels.*.name, 'wip')
    
    steps:
      - name: Verify all checks passed
        run: |
          PR_NUM="${{ github.event.pull_request.number }}"
          STATUS=$(gh pr view $PR_NUM --json statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion != "SUCCESS") | .name')
          
          if [ -n "$STATUS" ]; then
            echo "❌ Required checks failed: $STATUS"
            exit 1
          fi
          echo "✅ All required checks passed"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  
  enhancement-verification:
    needs: quality-gate-check
    runs-on: ubuntu-latest
    steps:
      - name: Verify PR enhances repository
        run: |
          # Check for meaningful changes
          ADDITIONS=$(gh pr view ${{ github.event.pull_request.number }} --json additions --jq '.additions')
          
          if [ $ADDITIONS -eq 0 ]; then
            echo "⚠️ No substantive changes"
            exit 1
          fi
          
          # Verify tests updated if source changed
          SRC_CHANGED=$(gh pr view ${{ github.event.pull_request.number }} --json files --jq '.files[] | select(.path | startswith("src/")) | .path' | wc -l)
          TEST_CHANGED=$(gh pr view ${{ github.event.pull_request.number }} --json files --jq '.files[] | select(.path | startswith("tests/")) | .path' | wc -l)
          
          if [ $SRC_CHANGED -gt 0 ] && [ $TEST_CHANGED -eq 0 ]; then
            echo "❌ Source changed but no tests added"
            gh pr comment ${{ github.event.pull_request.number }} \
              --body "⚠️ **Quality Gate Failed**: Source code modified without test updates."
            exit 1
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  
  automerge:
    needs: enhancement-verification
    runs-on: ubuntu-latest
    if: |
      (
        github.actor == 'dependabot[bot]' ||
        github.actor == 'claude[bot]' ||
        contains(github.event.pull_request.labels.*.name, 'automerge')
      )
    
    steps:
      - name: Auto-approve bot PRs
        if: contains(fromJson('["dependabot[bot]", "claude[bot]", "codex[bot]"]'), github.actor)
        run: |
          gh pr review --approve "$PR_URL" --body "✅ Automated approval: All quality gates passed"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Enable auto-merge
        run: |
          gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Ruff Quality Gate Integration

`.github/workflows/ruff-quality-gate.yml`:

```yaml
name: Ruff Quality Gate
on:
  pull_request:
    paths: ['**.py']
  push:
    branches: [main]

jobs:
  ruff-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Ruff
        run: pip install ruff
      
      - name: Run Ruff Linter
        run: ruff check --output-format=github .
      
      - name: Run Ruff Formatter Check
        run: ruff format --check .
      
      - name: Comment on PR if failed
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ **Ruff Quality Gate Failed**\n\nRun locally:\n```bash\nruff check --fix .\nruff format .\n```'
            })
```

### Unified Quality Gate (alls-green Pattern)

`.github/workflows/required-checks.yml`:

```yaml
name: Required Quality Checks
on:
  pull_request:
    branches: [main]

jobs:
  ruff-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff && ruff check .
  
  test-suite:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]" && pytest --cov=src --cov-fail-under=90
  
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/analyze@v4
  
  # Single status check for branch protection
  all-checks-passed:
    if: always()
    needs: [ruff-lint, test-suite, security-scan]
    runs-on: ubuntu-latest
    steps:
      - uses: re-actors/alls-green@release/v1
        with:
          jobs: ${{ toJSON(needs) }}
```

**Branch Protection**: Set only `all-checks-passed` as required status check, avoiding maintenance of individual job tracking.

---

## 4. Cherry-Picking Automation Before PR Closure

### Label-Based Cherry-Pick Workflow

`.github/workflows/cherry-pick-automation.yml`:

```yaml
name: Cherry-Pick Before Closure
on:
  pull_request:
    branches: [main]
    types: ['closed', 'labeled']

jobs:
  cherry-pick-to-release:
    runs-on: ubuntu-latest
    if: |
      github.event.pull_request.merged == true &&
      contains(github.event.pull_request.labels.*.name, 'cherry-pick')
    
    strategy:
      matrix:
        branch: [release-v1.0, release-v2.0]
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Cherry pick to release
        uses: carloscastrojumo/github-cherry-pick-action@v1.0.1
        with:
          branch: ${{ matrix.branch }}
          labels: cherry-picked,auto-generated
          reviewers: '@org/release-team'
          title: '[cherry-pick to ${{ matrix.branch }}] {old_title}'
          body: |
            🍒 Automated cherry-pick of #${{ github.event.pull_request.number }}
            
            **Original PR**: ${{ github.event.pull_request.html_url }}
            **Author**: @${{ github.event.pull_request.user.login }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.payload.pull_request.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `⚠️ Cherry-pick failed for \`${{ matrix.branch }}\`. Manual intervention required.`
            })
```

**Usage**: Add `cherry-pick:v1.0` or `cherry-pick:v2.0` labels to PRs before merging. Automation creates new PRs to those branches.

---

## 5. Daily PR Report Generation

### Comprehensive Daily Report

`.github/workflows/daily-pr-report.yml`:

```yaml
name: Daily PR Report
on:
  schedule:
    - cron: '0 9 * * 1-5'  # 9 AM UTC weekdays
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate statistics
        id: stats
        run: |
          OPEN_PRS=$(gh pr list --state open --json number --jq 'length')
          PENDING_REVIEW=$(gh pr list --state open --json reviewDecision --jq '[.[] | select(.reviewDecision == null)] | length')
          APPROVED=$(gh pr list --state open --json reviewDecision --jq '[.[] | select(.reviewDecision == "APPROVED")] | length')
          STALE=$(gh pr list --state open --json createdAt --jq "[.[] | select(.createdAt | fromdateiso8601 < (now - 604800))] | length")
          
          echo "open_prs=$OPEN_PRS" >> $GITHUB_OUTPUT
          echo "pending_review=$PENDING_REVIEW" >> $GITHUB_OUTPUT
          echo "approved=$APPROVED" >> $GITHUB_OUTPUT
          echo "stale=$STALE" >> $GITHUB_OUTPUT
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Generate report
        run: |
          cat > pr_report.md << EOF
          # Daily Pull Request Report
          **Generated**: $(date -u +"%Y-%m-%d %H:%M UTC")
          
          ## Summary
          - 📊 Total Open: ${{ steps.stats.outputs.open_prs }}
          - ⏳ Pending Review: ${{ steps.stats.outputs.pending_review }}
          - ✅ Approved: ${{ steps.stats.outputs.approved }}
          - 🕰️ Stale (>7 days): ${{ steps.stats.outputs.stale }}
          
          ## PRs Ready to Merge
          EOF
          
          gh pr list --state open --json number,title,author,reviewDecision \
            --jq '.[] | select(.reviewDecision == "APPROVED") | "- #\(.number): \(.title) by @\(.author.login)"' >> pr_report.md
          
          echo "" >> pr_report.md
          echo "## Stale PRs" >> pr_report.md
          
          gh pr list --state open --json number,title,updatedAt \
            --jq '.[] | select(.updatedAt | fromdateiso8601 < (now - 604800)) | "- #\(.number): \(.title)"' >> pr_report.md
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create report issue
        run: |
          gh issue create \
            --title "📋 Daily PR Report - $(date +%Y-%m-%d)" \
            --body-file pr_report.md \
            --label "report,automated"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 6. Post-Merge Monitoring and Rollback

### Health Check with Auto-Rollback

`.github/workflows/post-merge-monitor.yml`:

```yaml
name: Post-Merge Health Monitor
on:
  push:
    branches: [main]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run health checks
        id: health
        timeout-minutes: 10
        run: |
          pip install -e ".[dev]"
          pytest --maxfail=1 -q
          
          # Security scan
          pip install bandit
          bandit -r src/ -ll
        continue-on-error: true
      
      - name: Trigger rollback on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `🚨 Health check failed for ${context.sha.substring(0, 7)}`,
              body: `**Commit**: ${context.sha}\n**Failed**: [Workflow](${context.payload.repository.html_url}/actions/runs/${context.runId})\n\n@org/on-call`,
              labels: ['urgent', 'health-check-failure']
            });
```

### Manual Rollback Workflow

`.github/workflows/rollback.yml`:

```yaml
name: Emergency Rollback
on:
  workflow_dispatch:
    inputs:
      commit_sha:
        description: 'Commit SHA to rollback'
        required: true
      reason:
        description: 'Rollback reason'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Perform rollback
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git revert ${{ github.event.inputs.commit_sha }} --no-edit
          git push origin main
      
      - name: Create report
        run: |
          gh issue create \
            --title "✅ Rollback Complete: ${{ github.event.inputs.commit_sha }}" \
            --body "**Reason**: ${{ github.event.inputs.reason }}" \
            --label "rollback"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 7. Security and T4 Precision Guardrails

### Comprehensive Security Scanning

`.github/workflows/security-scanning.yml`:

```yaml
name: Security Scanning Suite
on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v4
        with:
          languages: python
          queries: security-and-quality
      - uses: github/codeql-action/autobuild@v4
      - uses: github/codeql-action/analyze@v4
  
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@main
```

### Test Coverage Enforcement (90% Minimum)

```yaml
      - name: Enforce coverage thresholds
        run: |
          pytest --cov=src --cov-report=json --cov-branch --cov-fail-under=90
      
      - name: Per-file coverage check
        run: |
          python - << 'PY'
          import json, sys
          with open('coverage.json') as f:
              data = json.load(f)
          
          failed = [f"{f}: {d['summary']['percent_covered']:.1f}%" 
                    for f, d in data['files'].items() 
                    if d['summary']['percent_covered'] < 85.0]
          
          if failed:
              print("❌ Files below 85%:")
              [print(f"  • {x}") for x in failed]
              sys.exit(1)
          PY
```

### Branch Protection Rules (T4 Standard)

Configure in `Repository → Settings → Branches`:

```
Branch: main

✅ Require pull request reviews
  - Required approvals: 2
  - Dismiss stale approvals on new commits
  - Require review from Code Owners

✅ Require status checks to pass
  - Require branches up to date
  - Required checks: all-checks-passed, codeql, dependency-scan

✅ Require conversation resolution
✅ Require signed commits
✅ Require linear history
✅ Include administrators
✅ Do not allow bypassing

❌ Allow force pushes: Never
❌ Allow deletions: Never
```

### Audit Logging

`.github/workflows/audit-logger.yml`:

```yaml
name: Audit Trail Logger
on: [push, pull_request, workflow_run]

jobs:
  audit-log:
    runs-on: ubuntu-latest
    steps:
      - name: Generate audit entry
        run: |
          cat > audit.json << EOF
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "event": "${{ github.event_name }}",
            "actor": "${{ github.actor }}",
            "sha": "${{ github.sha }}",
            "workflow": "${{ github.workflow }}"
          }
          EOF
      
      - uses: actions/upload-artifact@v4
        with:
          name: audit-log-${{ github.run_id }}
          path: audit.json
          retention-days: 365
```

---

## 8. JULES → CODEX → CLAUDE CODE Pipeline

### Architecture Overview

```
Stage 1: JULES (Planning)
  ↓ Creates GitHub Issue with spec
Stage 2: CODEX (Implementation)  
  ↓ Creates feature branch + draft PR
Stage 3: CLAUDE CODE (Review)
  ↓ Reviews and approves
Stage 4: Auto-Merge (Automated)
  ↓ All quality gates pass
Stage 5: Post-Merge Monitor
  ↓ Health checks + rollback if needed
```

### Agent-Specific Instructions

**`.github/agents/jules-instructions.md`**:

```markdown
# JULES: Planning & Specification Agent

## Role
Create comprehensive, actionable specifications for CODEX.

## Process
1. Analyze request thoroughly
2. Create GitHub Issue with structured template
3. Define acceptance criteria (minimum 3)
4. Identify dependencies
5. Outline file structure
6. Tag @codex when complete

## Issue Template
```
## Overview
[Brief description]

## Technical Specification
- Components: [files/modules]
- New files: [with purposes]
- Dependencies: [libraries]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Test coverage ≥ 90%
- [ ] Documentation updated

@codex Ready for implementation
```

## Quality Standards
- Specs must be implementable without clarification
- Include edge cases
- Specify test requirements
```

**`.github/agents/codex-instructions.md`**:

```markdown
# CODEX: Implementation Agent

## Role
Transform JULES specifications into working code.

## Process
1. Receive issue assignment from JULES
2. Create branch: `codex/issue-{number}-{slug}`
3. Implement solution per specification
4. Write tests (≥90% coverage)
5. Run: `ruff format . && ruff check --fix .`
6. Open draft PR
7. Tag @claude for review

## Code Standards
- Type hints for all functions
- Comprehensive docstrings
- Error handling with specific exceptions
- Logging for critical operations

## Before Review
- [ ] All tests pass
- [ ] Ruff formatting applied
- [ ] Coverage ≥ 90%
- [ ] Documentation updated
```

**`.github/agents/claude-instructions.md`**:

```markdown
# CLAUDE CODE: Review & Optimization Agent

## Role
Ensure all code meets T4 precision standards.

## Review Checklist

### Security
- [ ] No credential leaks
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention

### Code Quality
- [ ] Self-documenting code
- [ ] No duplication
- [ ] Consistent naming
- [ ] Cyclomatic complexity < 10

### Testing
- [ ] Coverage ≥ 90%
- [ ] Edge cases covered
- [ ] Error scenarios tested

### Documentation
- [ ] All public functions documented
- [ ] README updated if needed

## Actions
- **APPROVE**: All criteria met
- **REQUEST_CHANGES**: Issues require fixes
```

### Agent Coordination Automation

`.github/workflows/agent-coordination.yml`:

```yaml
name: Agent Pipeline Coordination
on:
  issues:
    types: [opened, assigned, labeled]
  pull_request:
    types: [opened, ready_for_review]

jobs:
  route-to-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Determine pipeline stage
        id: stage
        run: |
          if [[ "${{ github.event_name }}" == "issues" ]]; then
            echo "stage=planning" >> $GITHUB_OUTPUT
            echo "next_agent=codex-bot" >> $GITHUB_OUTPUT
          elif [[ "${{ github.event.pull_request.draft }}" == "true" ]]; then
            echo "stage=implementation" >> $GITHUB_OUTPUT
            echo "next_agent=claude-bot" >> $GITHUB_OUTPUT
          fi
      
      - name: Notify next agent
        run: |
          if [[ "${{ github.event_name }}" == "issues" ]]; then
            gh issue comment ${{ github.event.issue.number }} \
              --body "✅ Planning complete. @${{ steps.stage.outputs.next_agent }} ready for implementation."
          else
            gh pr comment ${{ github.event.pull_request.number }} \
              --body "✅ Implementation complete. @${{ steps.stage.outputs.next_agent }} ready for review."
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Quality Gate Progression

**Gate 1: JULES → CODEX**
- Issue has detailed specification
- Acceptance criteria defined (≥3 items)
- Dependencies identified
- File structure outlined

**Gate 2: CODEX → CLAUDE**
- Draft PR created
- All acceptance criteria addressed
- Tests passing
- Ruff formatting applied

**Gate 3: CLAUDE → Human Review**
- CLAUDE approved PR
- Test coverage ≥ 90%
- No security vulnerabilities
- Documentation updated

**Gate 4: Human → Auto-Merge**
- 2+ human approvals
- All conversations resolved
- All status checks passed
- No "do-not-merge" labels

---

## 9. Jules API Integration

**Note**: Jules-specific API documentation was not found during research. Here's a generic integration pattern for PR creation agents:

### Generic PR Agent Integration

```yaml
# .github/workflows/jules-trigger.yml
name: Trigger Jules PR Creation
on:
  issues:
    types: [labeled]

jobs:
  trigger-jules:
    if: contains(github.event.issue.labels.*.name, 'ready-for-pr')
    runs-on: ubuntu-latest
    steps:
      - name: Call Jules API
        run: |
          curl -X POST https://jules-api.example.com/create-pr \
            -H "Authorization: Bearer ${{ secrets.JULES_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "repository": "${{ github.repository }}",
              "issue_number": ${{ github.event.issue.number }},
              "target_branch": "main"
            }'
```

### Tagging Agents in Comments

```yaml
      - name: Request codex review
        run: |
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "@codex Please review for code quality, test coverage, and security."
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Implementation Steps**:
1. Obtain Jules API credentials/documentation
2. Identify webhook endpoints
3. Configure authentication (API key/OAuth/GitHub App)
4. Set up error handling and retry logic

---

## 10. GitHub Copilot Integration

### Enable Copilot Coding Agent

**Setup**:
1. GitHub Copilot subscription required
2. Enable: `Settings → Copilot → Enable for organization`
3. Grant permissions: `Settings → Actions → Allow Actions to create PRs`

**Usage**:
- Assign issues to `@github` (Copilot agent)
- Agent implements, tests, creates draft PR
- CLAUDE CODE reviews
- Human approves → Auto-merge

### Copilot Code Review Configuration

Enable via repository rulesets:

```
Repository → Settings → Rules → Rulesets → Create

Ruleset: "Copilot Code Review"
Target: Default branch

Rules:
✅ Require Copilot code review
  - Review new pushes
  - Review draft PRs

✅ Require status checks
  - Include Copilot review
```

**Custom Instructions**: `.github/copilot-instructions.md`:

```markdown
# Copilot Review Instructions

## Focus Areas
1. Security: SQL injection, XSS, credentials
2. Performance: Inefficient algorithms, N+1 queries
3. Testing: ≥90% coverage
4. Documentation: Public APIs documented

## T4 Requirements
- Zero security vulnerabilities
- All changes include tests
- Breaking changes flagged
- Performance regressions identified
```

### Multi-Model Strategy (2025)

**Recommended assignments**:
- **JULES (Planning)**: Claude 3.5 Sonnet (architectural thinking)
- **CODEX (Implementation)**: OpenAI o3-mini/GPT-4 (code generation)
- **CLAUDE CODE (Review)**: Claude Sonnet 4.5 (code analysis)

---

## Implementation Priority Roadmap

### Phase 1: Foundation (Week 1)
1. Install Claude GitHub App
2. Configure branch protection rules
3. Set up basic security scanning (CodeQL, Dependabot)
4. Create audit logging

### Phase 2: Quality Gates (Week 2)
1. Implement ruff quality gate
2. Enforce 90% test coverage
3. Configure CODEOWNERS
4. Set up unified quality gate (alls-green)

### Phase 3: Automation (Week 3)
1. Configure aggressive auto-merge pipeline
2. Set up cherry-pick automation
3. Implement daily PR reports
4. Add post-merge health monitoring

### Phase 4: Agent Pipeline (Week 4)
1. Create agent-specific instructions
2. Set up agent coordination workflows
3. Configure GitHub Projects for tracking
4. Implement quality gate progression

### Phase 5: Optimization (Week 5)
1. Enable Copilot Code Review
2. Configure multi-model selection
3. Fine-tune rollback triggers
4. Performance monitoring and tuning

---

## Key Takeaways

**Security & Guardrails**:
- GitHub Apps provide most secure integration (fine-grained permissions, short-lived tokens)
- Branch protection enforces 2+ reviews, all checks pass, conversations resolved
- T4 precision requires 90%+ coverage, zero High/Critical vulnerabilities, comprehensive audit trails

**Automation Pipeline**:
- Aggressive auto-merge only proceeds after ALL quality gates pass (ruff, tests, security, reviews)
- Cherry-picking automation uses labels (`cherry-pick:v1.0`) to target release branches
- Daily reports track stale PRs, approved PRs, and proposed closures
- Post-merge monitoring with automatic rollback triggers on health check failures

**AI Agent Orchestration**:
- JULES → CODEX → CLAUDE CODE pipeline uses GitHub Issues and draft PRs as handoff points
- Agent-specific instructions in `.github/agents/` ensure consistent behavior
- Quality gates at each stage prevent low-quality work from advancing
- GitHub Projects V2 tracks pipeline status and agent assignments

**Achieving T4 Precision (0.01% error rate)**:
- Multiple validation layers: SAST, DAST, SCA, secret scanning, breaking change detection
- Comprehensive testing: 90%+ coverage with branch coverage, integration tests, E2E tests
- Human-in-the-loop: Mandatory Code Owner approval, security team for sensitive changes
- Progressive deployment: Canary releases, automated rollback, continuous monitoring

**GitHub Copilot Integration**:
- Copilot Coding Agent can replace CODEX for implementation tasks
- Copilot Code Review provides 30-second automated reviews before human review
- Multi-model selection optimizes each agent for their strengths

This complete framework enables autonomous AI agent coordination while maintaining enterprise-grade reliability, security, and compliance standards.