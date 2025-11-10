#!/usr/bin/env bash
set -euo pipefail
python3 tools/labot.py --mode plan+gen
echo "✅ Generated prompts in prompts/labot and PR shells in requests/labot"
echo "Open a PR for one candidate:"
echo "  make labot-open slug=<module_path_slug>"
