# LUKHAS C-EVAL Production Evaluation System

Continuous evaluation loop with self-healing capabilities for production-grade AI alignment and performance monitoring.

## Overview

The C-EVAL system provides:

- **Weighted Risk Scoring**: Critical tasks weighted 3x, high-risk 2x, normal 1x for accurate impact assessment
- **CI/CD Integration**: Strict exit codes (0=pass, 2=fail) for automated pipeline control
- **Self-Healing Loop**: Automated detection, human-approved proposals, sandbox application with rollback
- **Prometheus Metrics**: Real-time monitoring with task-level granularity
- **Human-in-the-Loop**: All configuration changes require explicit approval before application

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

4. **Governance Framework** (`qi/autonomy/governance.yaml`)
   - Risk-based approval requirements
   - Path-based access controls
   - Reviewer authorization matrix

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

## Future Enhancements

- **Multi-Model Evaluation**: Support for A/B testing between model versions
- **Automated Baseline Updates**: Dynamic baseline adjustment based on performance trends
- **Risk-Aware Scheduling**: Evaluation frequency based on risk assessment
- **Federated Learning**: Cross-deployment evaluation coordination
- **ML-Driven Proposals**: Use ML to suggest more sophisticated configuration changes