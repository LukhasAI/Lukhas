# Claude Code — Single-file Provider/Lazy Refactor Prompt

Use this prompt in your IDE for small, safe edits that remove import-time `labs.*` dependencies in production lanes.

---

Prompt:

I want a small, safe, single-file refactor in the Lukhas repo to remove import-time production → labs edges.
Context: production lane modules must not import `labs.*` at import time. We already have `core/adapters/provider_registry.py` and `labs_integrations/*` plugin. Your job is to convert a single file to use the provider pattern or a lazy import.

Target file (replace this): `core/registry.py`
Target class / function (if specific): `RegistryManager` (or update top-level imports only).

Make these exact changes:
1) Create a branch from `origin/main` (name: `task/lazy-load-<file>-<you>`).
2) If file contains `from labs.* import ...` or `import labs`, remove the top-level import. Instead:
   - If it’s a service/client, use ProviderRegistry:

```py
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _openai_provider():
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()
```

Replace `labs.*` calls with `provider = _openai_provider(); provider.chat(...)`.

   - If usage is small, use a lazy loader:

```py
import importlib
def _get_labs():
    try:
        return importlib.import_module("labs")
    except Exception:
        return None
```

Then call `_get_labs()` inside functions and guard `None` appropriately.

Validation:
- Run: `pytest -q tests/unit/<targeted_tests>.py`
- Run: `make smoke`
- Run: `make lane-guard` (or `scripts/run_lane_guard_worktree.sh`)

Commit (T4):
`refactor(core): lazy-load labs usage in <file>`

Checklist:
- [ ] Tests OK (targeted)
- [ ] smoke OK
- [ ] lane-guard OK

