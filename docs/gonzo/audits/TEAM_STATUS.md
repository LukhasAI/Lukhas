 **team status doc** and a tiny, zero-dependency **file-lock system** so agents can coordinate safely across separate worktrees without stepping on each other.

````md
# 📊 Team Status — Parallel Worktrees & Ownership

> Source of truth for who is working where. Update once per day (or when roles change).
> Locks live under `.dev/locks/*.lock` — see **Lock etiquette** below.

_Last updated:_ 2025-10-13T12:00:00Z

## ✳️ Active Worktrees

| Agent       | Worktree Path         | Branch                 | Area Ownership (no-collision)                                                                | CI Gates Owned                  | Status | Last Sync (UTC) | Notes |
|-------------|------------------------|------------------------|------------------------------------------------------------------------------------------------|----------------------------------|--------|-----------------|-------|
| **Claude**  | ../Lukhas-claude      | feat/ops/ga-guard-pack| CI/Observability + health artifacts + dashboards/alerts                                       | PR health badge, openapi-diff   | 🟢     |                 |      |
| **Codex**   | ../Lukhas-codex-B1    | fix/codex10/ruffB1     | Hot-path lint/refactor (E402/E70x/I/RUF100) in adapters/reliability/observability/MATRIZ core | ruff-phaseB-hotpaths ≤120       | 🟢     |                 | Lock: `hotpaths-b1` |
| **Copilot** | ../Lukhas-copilot-dx2 | docs/copilot/dx-polish | ✅ **Merged via #383** — README quickstart, cookbooks, Postman, CI smoke                     | dx-examples-smoke               | ✅     | 2025-10-14T00:20| DX Polish Pack complete |
_Last updated:_ 2025-10-14T15:00:00Z

## ✳️ Active Worktrees

| Agent       | Worktree Path                      | Branch                           | Area Ownership (no-collision)                                                                 | CI Gates Owned                               | Status | Last Sync (UTC) | Notes |
|-------------|------------------------------------|----------------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------|--------|-----------------|-------|
| **Claude**  | `/Users/agi_dev/LOCAL-REPOS/Lukhas` | `main`                          | Observability/CI (workflows, rules, dashboards, health scripts, `docs/**`)                      | PR health badge, Prometheus rules, health artifacts | ✅    | 2025-10-14      | GA Guard Pack merged (#382, #383); monitoring deploy pending Guardian YAML fix |
| **Codex**   | `/Users/agi_dev/LOCAL-REPOS/Lukhas-main` | `main`                          | Hot-path lint/refactor (`lukhas/adapters/**`, `lukhas/core/reliability/**`, `lukhas/observability/**`, `MATRIZ/core/**`) | `ruff-phaseB-hotpaths ≤120`  | ✅    | 2025-10-14      | Phase-B.1 merged (#381); prepping Slice 1 (E402/E70x, Issue #388) |
| **Copilot** | `../Lukhas-copilot-dx2`            | `docs/copilot/quickstart-polish` | DX/docs/examples (`README.md`, `examples/sdk/**`, `docs/**`, Postman/Newman workflows)         | newman golden flows                           | ✅    | 2025-10-13      | Phase 2 DX complete, merged to main (#383) |

### 📁 Retired Worktrees

| Branch | Status | Notes |
|--------|--------|-------|
| `feat-jules-ruff-complete` | Archived (`archive/feat-jules-ruff-complete-20251014`) | Remote branch removed; pre-codemod drift and heavy conflicts superseded by GA guard work |

### 🧭 Ownership rules
- **Claude** can change **metrics/health/CI**; avoid runtime refactors in Codex’ hot paths.
- **Codex** limits changes to **lint/import/one-liners** in declared hot paths; no behavior changes.
- **Copilot** keeps to **docs/examples/workflows** (no Python runtime).

---

## 🔒 Lock etiquette (lightweight, repo-local)
- A lock is a small JSON file in `.dev/locks/NAME.lock` that lists **owner, branch, ttl**.
- Use it to claim a logical area (e.g. `guardian-metrics`, `openapi-spec-pipeline`, `hotpaths-b1`).
- Locks are **ignored by git** (local coordination only).

### Create a lock (60 minutes TTL)
```bash
make lock-guardian-metrics owner="Claude Code" branch="$(git rev-parse --abbrev-ref HEAD)" ttl=3600
````

### Inspect all locks

```bash
make locks-status
```

### Release a lock

```bash
make unlock-guardian-metrics owner="Claude Code"
```

> If a lock is expired, `lock.py` will auto-reclaim it for you.

---

## ✅ Daily 90-second sync

1. `git fetch --all --prune` in your worktree
2. Re-run your lint or smoke sanity command
3. Update this table (status + last sync + short note)
4. Ensure your lock still reflects your active scope

```
PR checklist (paste in your PR):
- [ ] I stayed within my declared ownership
- [ ] ruff-phaseB-hotpaths stayed ≤ budget
- [ ] Facade smoke stayed green (uses auth fixture)
- [ ] No lock conflicts (checked `make locks-status`)
```

````

---

## 2) Minimal lock system

> Add these files exactly as shown. They’re tiny Python scripts (no external deps).

### a) `.dev/locks/.gitkeep` (empty placeholder)

```txt

````

### b) `.gitignore` addition (append these lines)

```gitignore
# Local collaboration locks
.dev/locks/*.lock
```

### c) `scripts/locks/lock.py`

```python
#!/usr/bin/env python3
import argparse, json, os, sys, time
from datetime import datetime, timezone, timedelta

LOCK_DIR = ".dev/locks"

def now_utc():
    return datetime.now(timezone.utc)

def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()

def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser(description="Create or refresh a lightweight repo-local lock.")
    ap.add_argument("--key", required=True, help="Logical area name, e.g. guardian-metrics")
    ap.add_argument("--owner", required=True, help="Human-readable owner name")
    ap.add_argument("--branch", default="", help="Git branch owning the work")
    ap.add_argument("--ttl", type=int, default=3600, help="TTL seconds (default 3600)")
    args = ap.parse_args()

    os.makedirs(LOCK_DIR, exist_ok=True)
    path = os.path.join(LOCK_DIR, f"{args.key}.lock")

    now = now_utc()
    data = load(path)
    if data:
        exp = datetime.fromisoformat(data.get("expires_at"))
        if exp > now:
            print(f"[LOCK] '{args.key}' already held by {data.get('owner')} until {data.get('expires_at')}", file=sys.stderr)
            sys.exit(2)

    expires = now + timedelta(seconds=args.ttl)
    payload = {
        "key": args.key,
        "owner": args.owner,
        "branch": args.branch,
        "pid": os.getpid(),
        "created_at": iso(now),
        "ttl_seconds": args.ttl,
        "expires_at": iso(expires),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[LOCK] acquired '{args.key}' for {args.owner} until {payload['expires_at']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### d) `scripts/locks/unlock.py`

```python
#!/usr/bin/env python3
import argparse, json, os, sys

LOCK_DIR = ".dev/locks"

def main():
    ap = argparse.ArgumentParser(description="Release a repo-local lock.")
    ap.add_argument("--key", required=True)
    ap.add_argument("--owner", default="", help="Owner name (required unless --force)")
    ap.add_argument("--force", action="store_true", help="Force unlock even if owner mismatches")
    args = ap.parse_args()

    path = os.path.join(LOCK_DIR, f"{args.key}.lock")
    if not os.path.exists(path):
        print(f"[LOCK] '{args.key}' not found; nothing to unlock")
        return 0

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if not args.force and args.owner and data.get("owner") and args.owner != data.get("owner"):
        print(f"[LOCK] '{args.key}' held by {data.get('owner')}, not {args.owner}. Use --force if needed.", file=sys.stderr)
        return 3

    os.remove(path)
    print(f"[LOCK] released '{args.key}'")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### e) `scripts/locks/status.py`

```python
#!/usr/bin/env python3
import json, os, sys
from datetime import datetime, timezone

LOCK_DIR = ".dev/locks"

def parse_iso(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def main():
    if not os.path.isdir(LOCK_DIR):
        print("(no locks dir)")
        return 0

    rows = []
    for name in sorted(os.listdir(LOCK_DIR)):
        if not name.endswith(".lock"): continue
        path = os.path.join(LOCK_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            d = {}

        key = d.get("key") or name[:-5]
        owner = d.get("owner") or "unknown"
        branch = d.get("branch") or ""
        exp = parse_iso(d.get("expires_at") or "")
        now = datetime.now(timezone.utc)
        remaining = int((exp - now).total_seconds()) if exp else -1
        state = "EXPIRED" if remaining < 0 else "HELD"
        rows.append((key, owner, branch, state, remaining))

    if not rows:
        print("(no active locks)")
        return 0

    print(f"{'KEY':24} {'OWNER':20} {'BRANCH':28} {'STATE':8} {'TTL(s)':7}")
    for r in rows:
        ttl = str(r[4]) if r[4] >= 0 else "-"
        print(f"{r[0]:24} {r[1]:20} {r[2]:28} {r[3]:8} {ttl:7}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### f) Makefile shortcuts (append to `Makefile`)

```make
# --- Lightweight collaboration locks ---
locks-status:
	@python3 scripts/locks/status.py

lock-%:
	@python3 scripts/locks/lock.py --key "$*" --owner "$(owner)" --branch "$(branch)" --ttl "$(ttl)"

unlock-%:
	@python3 scripts/locks/unlock.py --key "$*" --owner "$(owner)" $(if $(force),--force,)
```

**Usage examples**

```bash
# Acquire a 1h lock for the GA guard pack
make lock-ga-guard-pack owner="Claude Code" branch="$(git rev-parse --abbrev-ref HEAD)" ttl=3600

# List locks
make locks-status

# Release (normal)
make unlock-ga-guard-pack owner="Claude Code"

# Force release if owner not present (use sparingly)
make unlock-ga-guard-pack force=1
```

---
