#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# LUKHAS Codex T4 Layout Launcher
# Creates a tmux workspace with 4 synchronized terminals
#   A: Facade (sequential)
#   B: Hidden Gem 1
#   C: Hidden Gem 2
#   D: Bugfix/Docs (optional)
# ─────────────────────────────────────────────────────────────

set -euo pipefail

SESSION="lukhas_codex"
REPO_ROOT="${LUKHAS_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# kill existing session if any
tmux has-session -t $SESSION 2>/dev/null && tmux kill-session -t $SESSION

# new session
tmux new-session -d -s $SESSION -n FACADE

# ─────────────────────────────────────────────────────────────
# Pane A: FACADE (strictly sequential)
tmux send-keys -t $SESSION:0 "cd $REPO_ROOT" C-m
tmux send-keys -t $SESSION:0 'git checkout -b feat/facade' C-m
tmux send-keys -t $SESSION:0 'make codex-bootcheck' C-m
tmux send-keys -t $SESSION:0 'echo "[FAÇADE] Follow FACADE_FAST_TRACK phases sequentially..."' C-m

# ─────────────────────────────────────────────────────────────
# Pane B: Hidden Gem 1
tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.1 "cd $REPO_ROOT" C-m
tmux send-keys -t $SESSION:0.1 'git checkout -b feat/integrate-async-orchestrator' C-m
tmux send-keys -t $SESSION:0.1 'echo "[HIDDEN GEM 1] async_orchestrator → matriz/orchestration/"' C-m

# ─────────────────────────────────────────────────────────────
# Pane C: Hidden Gem 2
tmux split-window -h -t $SESSION:0
tmux send-keys -t $SESSION:0.2 "cd $REPO_ROOT" C-m
tmux send-keys -t $SESSION:0.2 'git checkout -b feat/integrate-webauthn-adapter' C-m
tmux send-keys -t $SESSION:0.2 'echo "[HIDDEN GEM 2] webauthn_adapter → core/identity/adapters/"' C-m

# ─────────────────────────────────────────────────────────────
# Pane D: Bugfix/Docs
tmux split-window -v -t $SESSION:0.2
tmux send-keys -t $SESSION:0.3 "cd $REPO_ROOT" C-m
tmux send-keys -t $SESSION:0.3 'git checkout -b fix/matriz-node-typeerror' C-m
tmux send-keys -t $SESSION:0.3 'echo "[BUGFIX] Focus on single-file fix, run pytest + gates before commit"' C-m

# ─────────────────────────────────────────────────────────────
# Arrange panes and attach
tmux select-layout tiled
tmux attach -t $SESSION
