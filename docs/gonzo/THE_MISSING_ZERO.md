#!/usr/bin/env bash
# setup_dev.sh
# T4-ready developer environment setup helper.
# Usage:
#   ./scripts/setup_dev.sh            # default: docker mode (recommended)
#   ./scripts/setup_dev.sh --venv     # create local venv and install requirements
#   AZURE_IMAGE=registry.azurecr.io/lukhas:2025-10-01 ./scripts/setup_dev.sh
# Note: requires docker (default mode), or python3 + pip for venv mode.
set -euo pipefail

MODE="docker"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv) MODE="venv"; shift ;;
    --help) echo "Usage: $0 [--venv]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
cd "$REPO_ROOT"

# Helpful environment variables (optional overrides)
AZURE_IMAGE=${AZURE_IMAGE:-}
DEV_CONTAINER_NAME="lukhas_dev_$$"
HOST_UID=${HOST_UID:-$(id -u)}
HOST_GID=${HOST_GID:-$(id -g)}

if [ "$MODE" = "docker" ]; then
  echo "[setup] Running in DOCKER mode"
  if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker not found on PATH. Install Docker Desktop or Docker Engine." >&2
    exit 2
  fi

  # If AZURE_IMAGE specified, pull that image; otherwise look for local Dockerfile
  if [ -n "$AZURE_IMAGE" ]; then
    echo "[setup] Pulling Azure image: $AZURE_IMAGE"
    docker pull "$AZURE_IMAGE"
    IMAGE="$AZURE_IMAGE"
  else
    # Build a local image if Dockerfile exists
    if [ -f Dockerfile ]; then
      IMAGE="lukhas_local_dev:latest"
      echo "[setup] Building local Docker image: $IMAGE"
      docker build -t "$IMAGE" .
    else
      echo "ERROR: No Azure image provided and no Dockerfile found in repo root." >&2
      exit 3
    fi
  fi

  # Run container with repo mounted and a persistent dev volume for caches
  echo "[setup] Starting development container (name=$DEV_CONTAINER_NAME)"
  docker run -it --rm \
    --name "$DEV_CONTAINER_NAME" \
    -v "$REPO_ROOT":/workspace:cached \
    -v "lukhas_cache_${HOST_UID}":/root/.cache \
    -e HOST_UID="$HOST_UID" -e HOST_GID="$HOST_GID" \
    -w /workspace \
    "$IMAGE" /bin/bash -lc "\
      python3 -m pip install --upgrade pip || true; \
      if [ -f requirements.txt ]; then pip3 install -r requirements.txt || true; fi; \
      echo 'Dev container ready. You can run: ./scripts/preflight_check.py'\"

  echo "[setup] Container exited (or was closed). If you need an interactive container, re-run with the same AZURE_IMAGE or Dockerfile."
  exit 0
fi

# VENV mode
if [ "$MODE" = "venv" ]; then
  echo "[setup] Running in VENV mode"
  if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found" >&2; exit 4
  fi
  PYTHON=$(which python3)
  VENV_DIR=".venv"
  $PYTHON -m venv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip setuptools wheel
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  else
    echo "No requirements.txt found; skipping pip install"
  fi
  # Optional: install pre-commit hooks
  if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install || true
  else
    pip install pre-commit && pre-commit install || true
  fi
  echo "[setup] VENV ready at $VENV_DIR. Activate with: source $VENV_DIR/bin/activate"
  exit 0
fi

# fallback
echo "Unknown mode or error"; exit 1

#!/usr/bin/env bash
# create_run_issue.sh
# Create a GitHub issue to act as a run lock and store run metadata.
# Requires: GitHub CLI (gh) configured and authenticated.
# Usage:
#   ./scripts/create_run_issue.sh --run-id RUN_ID --owner OWNER --title "Optional Title"
set -euo pipefail

RUN_ID=""
OWNER=""
TITLE=""
BODY=""
REPO=${REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\.git)?$#\1#')}
LABEL=${LABEL:-"run:active"}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id) RUN_ID="$2"; shift 2;;
    --owner) OWNER="$2"; shift 2;;
    --title) TITLE="$2"; shift 2;;
    --body) BODY="$2"; shift 2;;
    --help) echo "Usage: $0 --run-id RUN_ID --owner OWNER [--title TITLE]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ -z "$RUN_ID" ]; then
  RUN_ID=$(uuidgen)
  echo "[info] Generated RUN_ID: $RUN_ID"
fi
if [ -z "$OWNER" ]; then
  OWNER=$(git config user.email || echo "$USER")
  echo "[info] OWNER defaulting to: $OWNER"
fi
if [ -z "$TITLE" ]; then
  TITLE="RUN: $RUN_ID"
fi

# Check for existing active runs with label
EXISTING=$(gh issue list --repo "$REPO" --label "$LABEL" --state open --json number,title --jq '.[] | .number' || true)
if [ -n "$EXISTING" ]; then
  echo "[warn] Found existing open run issues with label $LABEL:" && echo "$EXISTING"
  echo "Aborting new run creation. If this is stale, close the existing issue first."
  exit 2
fi

# Build body metadata
GIT_SHA=$(git rev-parse --short HEAD || echo "unknown")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BODY_FINAL=""$BODY"\n\n---\nRun ID: $RUN_ID\nOwner: $OWNER\nCreated: $NOW\nGit SHA: $GIT_SHA\nRepo: $REPO\n"

# Create the issue
echo "[info] Creating issue: $TITLE"
gh issue create --repo "$REPO" --title "$TITLE" --body "$BODY_FINAL" --label "$LABEL"

echo "[info] Issue created and labeled $LABEL. Use the issue to coordinate run state and lock."

You added two executable shell scripts under the `scripts/` directory:

1. `setup_dev.sh`: This script sets up the developer environment either by running a Docker container with the project mounted (default mode) or by creating and activating a local Python virtual environment (`--venv` mode). It uses environment variables like `AZURE_IMAGE` to specify a Docker image, and handles user/group IDs for proper volume mounting. Prerequisites include Docker (for default mode) or Python 3 with pip (for venv mode).

2. `create_run_issue.sh`: This script creates a GitHub issue to serve as a run lock and store metadata about a run. It requires the GitHub CLI (`gh`) to be installed and authenticated. You can specify run ID, owner, and title via arguments; it prevents creating a new run if an active run issue with the label `run:active` already exists. The `REPO` environment variable can override the GitHub repository target.

To use these scripts, ensure:
- For `setup_dev.sh`: Docker is installed and running, or Python 3 and pip are available for virtual env mode. Optionally set `AZURE_IMAGE` to specify a Docker image.
- For `create_run_issue.sh`: GitHub CLI (`gh`) is installed, authenticated, and optionally set `REPO` and `LABEL` environment variables to target a specific repository and label.