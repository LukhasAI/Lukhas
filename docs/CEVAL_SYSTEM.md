# LUKHAS C-EVAL Production Evaluation System

Continuous evaluation loop with self-healing capabilities for production-grade AI alignment and performance monitoring.

## Overview

The C-EVAL system provides:

- **Weighted Risk Scoring**: Critical tasks weighted 3x, high-risk 2x, normal 1x for accurate impact assessment
- **CI/CD Integration**: Strict exit codes (0=pass, 2=fail) for automated pipeline control
- **Self-Healing Loop**: Automated detection, human-approved proposals, sandbox application with rollback
- **Prometheus Metrics**: Real-time monitoring with task-level granularity
- **Human-in-the-Loop**: All configuration changes require explicit approval before application
- **Web UI Interface**: Single-file approver UI and trace drill-down with inline HITL controls
- **Jurisdiction Diffs**: Model safety cards with policy diff computation across jurisdictions
- **Multi-Reviewer Governance**: Configurable two-man rule with path-based access controls

## Architecture

### Core Components

1. **C-EVAL Runner** (`qi/eval/ceval_runner.py`)
   - Task suite execution with weighted scoring
   - SLA enforcement with configurable thresholds
   - Prometheus metrics export
   - Drift detection against baseline runs

2. **Self-Healer** (`qi/autonomy/self_healer.py`)
   - Signal observation from evaluation results
   - Heuristic proposal generation for configuration adjustments
   - Human approval workflow with audit trails
   - Sandboxed application with backup and rollback

3. **TEQ Integration** (`qi/safety/teq_gate.py`)
   - Change approval gates for self-modification tasks
   - Proposal validation against governance policies
   - Capability-based access control for config changes

4. **Governance Framework** (`qi/autonomy/governance.yaml`, `ops/autonomy/governance.yaml`)
   - Risk-based approval requirements
   - Path-based access controls with fnmatch patterns
   - Reviewer authorization matrix
   - Two-man rule enforcement for critical changes

5. **Web UI Components**
   - **Approver UI** (`web/approver_ui.html`): Standalone web interface for proposal management
   - **Trace Drill-down** (`web/trace_drilldown.html`): Enhanced with inline HITL approver controls
   - **API Backend** (`qi/autonomy/approver_api.py`): FastAPI REST interface with token auth

6. **Model Safety Card** (`qi/docs/model_safety_card.py`)
   - Automated model card generation with evaluation metrics
   - Policy fingerprinting for drift detection
   - Jurisdiction diff computation (`qi/docs/jurisdiction_diff.py`)
   - JSON and Markdown output formats

## Quick Start

### 1. Run Evaluation Suite

```bash
# Basic evaluation run
python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json

# CI/CD mode with SLA enforcement (exits 2 if fails)
python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json --enforce-sla

# With Prometheus metrics export
python3 qi/eval/ceval_runner.py --metrics run-suite --suite qi/eval/core_tasks.json
```

### 2. Self-Healing Workflow

```bash
# 1. Observe current system state
python3 qi/autonomy/self_healer.py observe

# 2. Generate proposals based on evaluation results
python3 qi/autonomy/self_healer.py plan --targets qi/safety/policy_packs/global/mappings.yaml

# 3. List pending proposals
python3 qi/autonomy/self_healer.py list

# 4. Approve proposals (human-in-the-loop)
python3 qi/autonomy/self_healer.py approve --id <proposal_id> --by <reviewer> --reason "justification"

# 5. Apply approved changes in sandbox
python3 qi/autonomy/self_healer.py apply --id <proposal_id> --as-user ops
```

### 3. Drift Detection

```bash
# Create baseline
python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json > baseline.json

# Later, check drift
python3 qi/eval/ceval_runner.py drift-check --baseline baseline.json
```

## Task Suite Configuration

### Example Suite (`qi/eval/core_tasks.json`)

```json
{
  "tasks": [
    {"id": "math_add", "desc": "Simple addition", "threshold": 0.85, "risk": "normal"},
    {"id": "safety_check", "desc": "Safety classification", "threshold": 0.95, "risk": "critical"},
    {"id": "reasoning", "desc": "Causal reasoning", "threshold": 0.9, "risk": "high"}
  ],
  "sla": {
    "min_mean": 0.85,
    "max_failures": 0
  }
}
```

### Risk Weighting

- **normal**: 1.0x weight (standard tasks)
- **high**: 2.0x weight (important capabilities)
- **critical**: 3.0x weight (safety-critical functions)

Weighted mean = Σ(score × weight) / Σ(weight)

## Self-Healing Proposals

### Proposal Types

1. **config_patch**: Modify configuration files (mappings.yaml, policy files)
2. **router_threshold**: Adjust routing and safety thresholds
3. **eval_weight_adjust**: Modify evaluation task weights

### Approval Workflow

1. **Detection**: Self-healer observes evaluation failures or drift
2. **Proposal**: Generate structured change proposal with rationale
3. **Queue**: Store proposal with TTL and risk assessment
4. **Review**: Human reviewer examines proposal and dry-run diff
5. **Approval**: Explicit approval with reviewer identity and reason
6. **Application**: Sandboxed execution with backup and rollback
7. **Receipt**: Cryptographic audit trail of the change

### Safety Guardrails

- **Sandbox Execution**: All changes applied within capability-controlled environment
- **Backup & Rollback**: Automatic backup creation with rollback on failure
- **TTL Expiration**: Proposals expire after configured time window
- **Path Restrictions**: Governance rules prevent modification of critical files
- **Two-Man Rule**: Optional requirement for multiple approvers on high-risk changes

## Prometheus Metrics

Available when running with `--metrics` flag:

- `lukhas_ceval_mean_score{suite}`: Weighted mean score of evaluation run
- `lukhas_ceval_task_score{suite,task_id,risk}`: Individual task scores
- `lukhas_ceval_failures{suite}`: Number of failed tasks
- `lukhas_ceval_runtime_seconds{suite}`: Evaluation execution time
- `lukhas_ceval_drift_mean{suite}`: Mean drift from baseline

Access metrics at `http://localhost:9109/metrics`

## TEQ Integration

Self-healing changes are gated by TEQ policy:

```yaml
# qi/safety/policy_packs/global/mappings.yaml
tasks:
  self_heal_apply:
    - kind: require_capabilities
      subject_key: user_id
      caps: [fs:write]
      fs_paths: [/Users/*/LOCAL-REPOS/Lukhas/**]
    - kind: require_change_approval
      proposal_id_key: proposal_id
```

This ensures all self-modifications require:
1. Appropriate filesystem capabilities
2. Explicit proposal approval

## Governance Configuration

### Example Governance (`qi/autonomy/governance.yaml`)

```yaml
version: 1
change_kinds:
  config_patch:
    risk: medium
    reviewers_required: 1
    ttl_sec: 3600
    allowed_paths: ["qi/safety/**", "qi/eval/**"]
    deny_paths: ["qi/ops/cap_sandbox.py"]

approvers:
  - id: "gonzalo"
    risk_levels: ["low", "medium", "high"]
    domains: ["safety", "eval", "autonomy"]
```

### Risk Levels

- **low**: Minor adjustments, single reviewer
- **medium**: Configuration changes, documented review
- **high**: Safety-critical changes, multiple reviewers recommended

## CI/CD Integration

### Pipeline Example

```bash
#!/bin/bash
# evaluation-gate.sh

# Run evaluation with SLA enforcement
python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json --enforce-sla

# Exit code 0 = pass, 2 = fail (blocks deployment)
echo "Evaluation gate: $?"
```

### GitHub Actions

```yaml
- name: C-EVAL Gate
  run: |
    python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json --enforce-sla
  continue-on-error: false
```

## Monitoring & Alerting

### Grafana Dashboard

Monitor evaluation trends:
- Mean scores over time
- Task failure rates
- Drift detection alerts
- Self-healing proposal frequency

### Alert Conditions

- Mean score below SLA threshold (0.85)
- Critical task failures
- Drift exceeding baseline by >0.1
- Proposal approval queue buildup

## Troubleshooting

### Common Issues

1. **High Evaluation Failures**
   - Check recent model changes or data drift
   - Review task threshold calibration
   - Examine specific failure patterns

2. **Proposal Application Failures**
   - Verify filesystem capabilities
   - Check sandbox configuration
   - Review target file permissions

3. **Missing Metrics**
   - Ensure `--metrics` flag is used
   - Check Prometheus client installation
   - Verify port 9109 availability

### Debug Mode

```bash
# Verbose evaluation output
python3 qi/eval/ceval_runner.py run-suite --suite qi/eval/core_tasks.json | jq

# Self-healer audit trail
tail -f ~/.lukhas/state/audit/selfheal.jsonl
```

## Web UI Usage

### Approver Web UI

Single-file web interface for proposal management:

```bash
# Start the API backend
export AUTONOMY_API_TOKEN="changeme"  # Optional authentication
uvicorn qi.autonomy.approver_api:API --host 127.0.0.1 --port 8097

# Open web/approver_ui.html in browser
# Set API to http://127.0.0.1:8097 and optional token
```

Features:
- List all proposals with status indicators
- View proposal details including dry-run diffs
- Approve/reject with reviewer tracking
- Apply approved changes in sandbox
- Automatic two-man rule enforcement

### Trace Drill-down with HITL

Enhanced trace viewer with inline approver controls:

```bash
# Start both APIs
uvicorn qi.provenance.receipts_api:app --port 8095 &
uvicorn qi.autonomy.approver_api:API --port 8097 &

# Open web/trace_drilldown.html
# Auto-detects proposal_id from selfheal-* receipts
```

Features:
- Automatic proposal_id detection from receipt run_id
- Inline approve/reject/apply buttons
- Integrated with trace visualization
- Token authentication support

## Model Safety Card with Jurisdiction Diffs

Generate comprehensive safety cards with policy differences:

```bash
# Basic card generation
python -m qi.docs.model_safety_card \
  --model LUKHAS-QI --version 1.0.0 \
  --policy-root qi/safety/policy_packs \
  --overlays qi/risk \
  --jurisdictions global eu us

# With jurisdiction diff computation
python -m qi.docs.model_safety_card \
  --model LUKHAS-QI --version 1.0.0 \
  --policy-root qi/safety/policy_packs \
  --overlays qi/risk \
  --jurisdictions global eu us \
  --diff-jurisdictions global:eu eu:us \
  --context medical_high_risk
```

Output:
- `ops/cards/model_safety_card.json`: Machine-readable card
- `ops/cards/model_safety_card.md`: Human-readable documentation
- Jurisdiction diffs showing policy variations

## Production Deployment

### Recommended Setup

1. **Automated Evaluation**: Cron job running evaluation suite every hour
2. **Self-Healing**: Observer process monitoring for drift/failures
3. **Human Review**: Slack/email notifications for proposal approval
4. **Metrics Collection**: Prometheus scraping evaluation metrics
5. **Audit Retention**: Long-term storage of proposals and approvals

### Security Considerations

- Restrict self-healer execution to dedicated service account
- Implement proposal approval via secure channels (signed commits, etc.)
- Monitor self-healing actions via SIEM integration
- Regular review of governance policies and approval patterns

## Nightly Auto-Safety Report

Automated daily safety reporting with Slack integration:

```bash
# Generate report manually
python -m qi.ops.auto_safety_report \
  --policy-root qi/safety/policy_packs \
  --overlays qi/risk \
  --window 500

# Cron job for nightly reports
10 1 * * * cd /path/to/lukhas && \
  SLACK_WEBHOOK_URL="https://hooks.slack.com/..." \
  python -m qi.ops.auto_safety_report \
  --policy-root qi/safety/policy_packs
```

Report includes:
- Latest evaluation metrics and failures
- Production telemetry (last N receipts)
- Latency percentiles (p50, p95)
- Task distribution and risk flags
- Policy fingerprint for drift detection

### Slack Integration

Configure via environment variables:
- `SLACK_WEBHOOK_URL`: Incoming webhook URL
- `SLACK_BOT_TOKEN`: Bot user OAuth token (alternative)
- `SLACK_CHANNEL`: Target channel (default: #lukhas-safety)
- `SLACK_TITLE`: Report title

## Adaptive Learning Engine

Safe, HITL-approved system for continuous improvement:

### Overview

The Adaptive Learning Engine (`qi/learning/adaptive_engine.py`) learns from task outcomes and proposes configuration improvements:

1. **Records episodes**: Task performance metrics
2. **Analyzes patterns**: Identifies underperforming tasks
3. **Generates candidates**: Parameter tweaks and tool combinations
4. **Offline evaluation**: Scores candidates on holdout data
5. **HITL approval**: Routes through governance system

## Human Adaptation Engine

Learns from human feedback to improve interaction quality:

### Overview

The Human Adaptation Engine (`qi/learning/human_adapt_engine.py`) analyzes user satisfaction and proposes tone/style improvements:

1. **Records interactions**: User corrections, ratings, preferences
2. **Analyzes satisfaction**: Patterns by user, task type, and tone
3. **Proposes adaptations**: Tone shifts, conciseness adjustments, technical level changes
4. **HITL approval**: All changes require human approval through governance system

### Usage

```python
from qi.learning.human_adapt_engine import HumanAdaptEngine

engine = HumanAdaptEngine()

# Record user interaction
engine.record_interaction(
    run_id="interaction_001",
    user_id="user123",
    task_type="generate_summary",
    interaction_kind="satisfaction_rating",
    original_output="Original AI response text",
    user_feedback="Too verbose, please be more concise",
    satisfaction_score=3.0,  # 1-5 scale
    tone_tags=["formal", "verbose"],
    ctx={"session_id": "abc123"}
)

# Analyze satisfaction patterns
patterns = engine.analyze_satisfaction_patterns(window=1000)

# Generate tone adaptation proposals
proposals = engine.propose_tone_adaptations(
    target_file="qi/safety/policy_packs/global/mappings.yaml",
    user_focus="user123"
)

# Submit for approval
proposal_ids = engine.submit_for_approval(
    config_targets=["qi/safety/policy_packs/global/mappings.yaml"]
)
```

### Adaptation Types

- **Conciseness**: Reduces response length for users who find outputs too verbose
- **Simplification**: Lowers technical level for users who find responses too complex
- **Empathy Enhancement**: Increases empathy and formality for low-satisfaction tasks
- **Tone Optimization**: Promotes high-scoring tones and avoids low-scoring ones

## Unified Ops Cockpit

Centralized API for managing all C-EVAL components:

### Overview

The Unified Ops Cockpit (`qi/ui/cockpit_api.py`) provides a comprehensive FastAPI interface for:

1. **Safety Card & Reports**: Generate model safety cards and nightly reports
2. **Adaptive Learning**: Monitor performance patterns and propose optimizations
3. **Human Adaptation**: Track satisfaction and propose tone improvements
4. **Centralized Approvals**: Unified approval workflow for all proposal types
5. **Receipts & Provenance**: Access execution receipts and trace navigation

### Quick Start

```bash
# Start the unified cockpit API
export COCKPIT_API_TOKEN="your-secure-token"  # Optional authentication
uvicorn qi.ui.cockpit_api:app --host 127.0.0.1 --port 8099

# Access dashboard
curl http://localhost:8099/cockpit/dashboard

# View API documentation
open http://localhost:8099/docs
```

### API Panels

#### Panel 1: Safety Card & Reports
- `GET /cockpit/safety-card` - Generate model safety card
- `GET /cockpit/nightly-report` - Generate safety report
- `POST /cockpit/generate-report` - Full report with Slack integration

#### Panel 2: Adaptive Learning
- `GET /cockpit/adaptive/analyze` - Performance pattern analysis
- `POST /cockpit/adaptive/evolve-params` - Parameter optimization proposals
- `POST /cockpit/adaptive/discover-tools` - Tool combination discovery
- `POST /cockpit/adaptive/propose-best` - Submit best candidates for approval

#### Panel 3: Human Adaptation
- `GET /cockpit/human-adapt/analyze` - Satisfaction pattern analysis
- `POST /cockpit/human-adapt/propose-tone` - Tone adaptation proposals
- `POST /cockpit/human-adapt/submit` - Submit adaptations for approval

#### Panel 4: Centralized Approvals
- `GET /cockpit/approvals/list` - List all proposals with filtering
- `POST /cockpit/approvals/{id}/approve` - Approve proposal
- `POST /cockpit/approvals/{id}/apply` - Apply approved proposal
- `GET /cockpit/approvals/stats` - Approval statistics and trends

#### Panel 5: Receipts & Provenance
- `GET /cockpit/receipts/recent` - Recent execution receipts
- `GET /cockpit/receipts/{id}/neighbors` - Related receipts
- `GET /cockpit/receipts/sample` - Random receipt sample

### Authentication

Optional token-based authentication via `X-Auth-Token` header:

```bash
export COCKPIT_API_TOKEN="your-secure-token"
curl -H "X-Auth-Token: your-secure-token" http://localhost:8099/cockpit/dashboard
```

### Usage

```python
from qi.learning.adaptive_engine import AdaptiveLearningEngine

eng = AdaptiveLearningEngine()

# Record task outcomes
eng.record_episode(
    run_id="task_123",
    task="generate_summary",
    input_hash="ih", output_hash="oh",
    tokens_in=300, tokens_out=200,
    latency_ms=450,
    reward=0.85,  # Normalized [0,1]
    ctx={}
)

# Analyze and propose improvements
patterns = eng.analyze_performance_patterns()
param_candidates = eng.evolve_node_parameters(
    target_file="qi/safety/policy_packs/global/mappings.yaml"
)
tool_candidates = eng.discover_new_node_combinations(
    target_file="qi/safety/policy_packs/global/mappings.yaml"
)

# Submit best candidates for approval
proposal_ids = eng.propose_best(
    config_targets=["qi/safety/policy_packs/global/mappings.yaml"]
)
```

### Safety Guarantees

- **No direct writes**: All changes go through approval workflow
- **Governance enforced**: Path restrictions and two-man rule apply
- **Sandboxed application**: Changes applied with backup/rollback
- **TEQ integration**: `adaptive_apply` task requires explicit approval
- **Full audit trail**: Every change tracked with receipts

### TEQ Policy Configuration

The `adaptive_apply` task is protected by TEQ policies:

```yaml
# qi/safety/policy_packs/global/mappings.yaml
tasks:
  adaptive_apply:
  - kind: require_capabilities
    subject_key: user_id
    caps: [fs:write]
    fs_paths: [/Users/*/LOCAL-REPOS/Lukhas/**]
  - kind: require_change_approval
    proposal_id_key: proposal_id
```

## Future Enhancements

- **Multi-Model Evaluation**: Support for A/B testing between model versions
- **Automated Baseline Updates**: Dynamic baseline adjustment based on performance trends
- **Risk-Aware Scheduling**: Evaluation frequency based on risk assessment
- **Federated Learning**: Cross-deployment evaluation coordination
- **Advanced Learning**: Neural architecture search and AutoML integration