---
danger_level: medium
goal: Quickly revert the last consolidation stage commit
module: unknown
name: roll-back-last-stage
type: documentation
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