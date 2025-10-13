# Migration Guide v0.9.0 — Compat Removal & Lane Rename

## Summary

Version 0.9.0 completes the Phase 2/Phase 3 canonical import migration:

- **Phase 2 (Complete)**: `candidate.*` → `labs.*` (development lane rename)
- **Phase 3 (Complete)**: `lukhas.compat.*` **removed** (compatibility layer decommissioned)
- **OpenAPI Polish**: Spec now includes `servers` and `x-service-version` metadata
- **Security Enhancements**: HSTS, X-Content-Type-Options, X-Frame-Options, CSP, log redaction
- **Observability**: X-Trace-Id header on all responses

## Breaking Changes

### 1. Development Lane Rename: `candidate/` → `labs/`

**What Changed:**
All imports from `candidate.*` must now use `labs.*`:

```python
# ❌ Old (no longer works)
from candidate.core.metrics import MetricsCollector
from candidate.memory.fold_manager import FoldManager

# ✅ New (required in v0.9.0+)
from labs.core.metrics import MetricsCollector
from labs.memory.fold_manager import FoldManager
```

**Why:** The `candidate/` directory was temporary naming during Phase 1. `labs/` better reflects the development/experimental nature of this lane.

**Migration Path:**
1. Find all imports: `rg "from candidate\.|import candidate" --type py`
2. Replace with: `sed 's/from candidate\./from labs./g'` and `sed 's/import candidate/import labs/g'`
3. Verify: `make check-legacy-imports`

### 2. Compat Layer Removed: `lukhas.compat`

**What Changed:**
The `lukhas/compat/` directory and all runtime alias machinery has been **permanently removed**.

```python
# ❌ No longer available
from lukhas.compat import install as _install_aliases
import lukhas.compat

# ✅ Use canonical imports directly
from labs.memory import MemoryManager
from lukhas.tools import analysis_tool
```

**Why:** Phase 2 completed the migration with zero compat hits for 48+ hours. The compatibility layer was training wheels that are no longer needed.

**Migration Path:**
1. Ensure all imports use canonical paths (Phase 2 complete)
2. Remove any `lukhas.compat` references from your code
3. Run smoke tests: `pytest tests/smoke/ -q`

### 3. OpenAPI Contract Changes (Non-Breaking)

**What Changed:**
- `servers` array now includes `https://api.lukhas.ai` (prod) and `http://localhost:8000` (local)
- `info.x-service-version` contains git SHA (7-char hex) for version tracking
- `X-Trace-Id` header present on all responses (32-char hex) for distributed tracing

**Why:** OpenAI alignment and observability improvements.

**Migration Path:**
No action required - additive changes only. Client SDKs regenerated from `docs/openapi/lukhas-openai.json` will automatically use production servers.

## Non-Breaking Enhancements

### Security Headers (Phase 3)

All responses now include:
- `Strict-Transport-Security`: HSTS with 1-year max-age
- `X-Content-Type-Options: nosniff`: Prevents MIME sniffing
- `X-Frame-Options: DENY`: Prevents clickjacking
- `Referrer-Policy: no-referrer`: Privacy protection
- `Content-Security-Policy`: Minimal API policy

### Log Redaction

Automatically redacts secrets from logs:
- OpenAI-style tokens (`sk-...`)
- Bearer tokens
- API key assignments

### Rate Limiter Keying Strategy

New environment variable `LUKHAS_RL_KEYING`:
- `route_principal` (default): Per-user per-endpoint limits
- `route_only`: Shared limits across all users (testing/fallback)

Tokens are now hashed (SHA-256, 16-char) before storage for security.

## Validation

Run these commands to verify successful migration:

```bash
# 1. No legacy imports
make check-legacy-imports

# 2. Smoke tests pass
pytest tests/smoke/ -q

# 3. No candidate/ references
rg "candidate/" --type py | grep -v "# legacy comment"

# 4. Compat hits = 0
python3 scripts/report_compat_hits.py --out docs/audits/compat_alias_hits.json

# 5. Generate OpenAPI spec
python3 scripts/generate_openapi.py
```

## Rollback Plan

If you need to revert:

```bash
# Restore compat layer from v0.8.x
git checkout v0.8.x -- lukhas/compat

# Or revert the entire commit
git revert <phase-3-commit-sha>

# Restore candidate/ directory name (Phase 2 rollback)
git mv labs candidate
python3 scripts/update_manifest_paths.py --root manifests --from labs/ --to candidate/
```

## Timeline

- **v0.8.x**: Compat layer active, `candidate/` and `labs/` coexist
- **v0.9.0**: Compat layer removed, `labs/` canonical (current)
- **v1.0.0+**: No further backwards compatibility guaranteed

## Support

For migration issues:
- Check [CODEX_START_HERE_3.md](../gonzo/matriz_prep/CODEX_START_HERE_3.md) for detailed Phase 3 context
- Review [CODEX_PHASE_TWO.md](../gonzo/matriz_prep/CODEX_PHASE_TWO.md) for Phase 2 import mappings
- Run diagnostics: `make doctor`

## Deprecation Notices

- `experimental.*` package: Deprecated in v0.9.0, use `labs.*` directly
- Expect removal in v1.0.0

---

**Generated**: 2025-10-13
**Applies to**: LUKHAS v0.9.0
**Supersedes**: Previous candidate/ import patterns
