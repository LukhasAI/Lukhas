# Operational Runbook (Run & Validation)

Key commands
------------
# Create run lock (use create_run_issue.sh in scripts/)
./scripts/create_run_issue.sh --owner "you@example.com"

# Run lane-guard (worktree)
./scripts/run_lane_guard_worktree.sh

# Create waveC snapshot (example)
python3 scripts/wavec_snapshot.py

# Start the dev container
./scripts/setup_dev.sh

Safety
------
- Always create run issue before long experiments
- Always use WaveC snapshot before starting experiments
- Human sign-off required before merging PRs that affect run-critical modules

Ethics
------
- For any human judge study: create IRB packet (see docs/gonzo/IRB_TEMPLATE.md) and get Guardian sign-off.
