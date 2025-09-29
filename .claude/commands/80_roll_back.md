---
name: roll-back-last-stage
goal: Quickly revert the last consolidation stage commit
danger_level: medium
---

## Prompt
Revert the last commit created by a consolidation command (identified by conventional commit prefix).

## Shell
```bash
set -euo pipefail
git log --oneline -n 5
# Replace HASH below after confirmation:
# git revert --no-edit HASH
```

## Acceptance

* Reversion commit created; working tree clean