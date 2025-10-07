---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# LUKHAS Scaffold Regiment

## TL;DR for Developers

The Scaffold Regiment enforces T4/0.01% quality standards across 146 modules with:
- **Canonical naming**: All modules use `snake_case`
- **Provenance tracking**: Generated files carry `@generated` headers
- **Schema validation**: Config files validated against JSON schemas
- **Secrets prevention**: Pre-commit blocks real values in environment.yaml
- **Test sharding**: 8-way parallel execution for ~8x CI speedup

## Quick Commands

```bash
# Validate all configs (run this before committing)
python3 tools/validate_configs.py

# Check module readiness score
python3 tools/module_readiness_score.py --module your_module

# Sync module from canonical template
python3 tools/scaffold_sync.py --module your_module

# Generate test shards for local parallel testing
python3 tools/test_sharding.py --shards 4 --output pytest
```

## Key Files & Tools

### Schemas
- `schemas/config.schema.json` - Module configuration schema
- `schemas/logging.schema.json` - Logging configuration schema

### Templates
- `templates/module_scaffold/` - Canonical templates for all generated files

### Tools
- `tools/guard_module_names.py` - Enforce snake_case naming
- `tools/validate_configs.py` - Validate configs + detect secrets
- `tools/add_provenance_headers.py` - Add tracking headers
- `tools/scaffold_sync.py` - Sync from canonical templates
- `tools/test_sharding.py` - Generate balanced test shards
- `tools/module_readiness_score.py` - Calculate quality metrics

## Pre-commit Hooks

These run automatically on `git commit`:

1. **Module naming guard** - Enforces snake_case
2. **Config validation** - Schema compliance check
3. **Secrets detection** - Blocks real values in configs
4. **Provenance check** - Ensures headers present
5. **Large commit prevention** - Blocks >500 files

To bypass in emergency (use sparingly):
```bash
git commit --no-verify -m "emergency: bypass hooks for hotfix"
```

## Module Readiness Scoring

Each module gets a 0-100 score based on:
- **Manifest validity** (25 points) - Complete metadata
- **MATRIZ compliance** (25 points) - Contract files present
- **Documentation** (20 points) - Real content, not templates
- **Testing** (20 points) - Unit + integration tests
- **Configuration** (10 points) - Valid YAML files

Current stats:
- Average score: 67.3%
- Ready modules: 0 (target: >90%)
- Good modules: 5 (score: 75-90%)

## FAQ

### Q: My module name has dashes, what do I do?
A: Rename it to snake_case:
```bash
git mv my-module my_module
```

### Q: How do I mark a file as human-editable?
A: Files in `docs/` are automatically marked as editable. For others, the provenance header will have `human_editable: true`.

### Q: Can I add custom fields to config.yaml?
A: Yes, but update the schema first:
1. Edit `schemas/config.schema.json`
2. Add your field to the appropriate section
3. Run validation to ensure compatibility

### Q: Why did CI fail on secrets detection?
A: Check `environment.yaml` files - they should only have placeholders:
```yaml
# Good
database_url: ${DATABASE_URL}

# Bad
database_url: postgresql://user:pass@localhost/db
```

### Q: How do I run tests in parallel locally?
A: Use test sharding:
```bash
# Generate commands for 4 shards
python3 tools/test_sharding.py --shards 4 --output pytest

# Run shard 0 (in one terminal)
pytest tests/unit tests/integration -v

# Run shard 1 (in another terminal)
pytest tests/e2e tests/smoke -v
```

## Rollback Plan

If the Scaffold Regiment causes issues:

1. **For hotfix PRs**: Add label `allow:scaffold-bypass`
2. **For naming issues**: Use the `lukhas/` compat namespace
3. **Complete rollback**: `git revert <scaffold-commit-sha>`

## The T4/0.01% Standard

✅ **What "done" looks like:**
- No secrets in repo (enforced by pre-commit)
- All configs validate against schemas
- Generated files carry provenance
- Names are canonical and consistent
- CI runs fast with sharded tests
- Readiness score trends upward

❌ **What we prevent:**
- Configuration drift across modules
- Secrets leaking into configs
- Inconsistent naming patterns
- Slow CI from serial test execution
- Review blindness from large commits

## Contributing

When adding a new module:
1. Use `snake_case` for the directory name
2. Run `python3 tools/scaffold_sync.py --module your_module`
3. Update `module.manifest.json` with real metadata
4. Ensure tests pass: `python3 tools/validate_configs.py`
5. Check readiness: `python3 tools/module_readiness_score.py --module your_module`

---

*The Scaffold Regiment: From "heroic" to "unassailable" through systematic quality control.*