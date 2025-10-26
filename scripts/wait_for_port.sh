#!/usr/bin/env bash
# usage: wait_for_port.sh host port timeout_seconds
set -euo pipefail
HOST="${1:-127.0.0.1}"
PORT="${2:-8080}"
TIMEOUT="${3:-30}"
end=$((SECONDS + TIMEOUT))
while true; do
  if nc -z "$HOST" "$PORT" >/dev/null 2>&1; then
    echo "Port $HOST:$PORT open"
    exit 0
  fi
  if [ $SECONDS -ge $end ]; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
  fi
  sleep 1
done
