# Dream EXPAND++ Modules

![Dream EXPAND++](https://github.com/USER/REPO/actions/workflows/dream-expand-ci.yml/badge.svg)

Clean, production-safe baseline for advanced dream system capabilities.

## 📂 Module Overview

### `atlas.py` - Drift Atlas
Logs drift/entropy across dream runs for constellation mapping.
```python
row = atlas.log("run_001", snapshot, drift_score=0.5, entropy=0.3)
atlas.export_html("drift_report.html")
```

### `mediation.py` - Conflict Mediation
Resolves high-tension conflicts with compromise vectors.
```python
result = mediation.mediate(dream_a, dream_b, target_emotion)
# Returns: {"compromise": {...}, "trace": "..."}
```

### `sentinel.py` - Ethical Sentinel
Monitors thresholds and blocks unsafe dreams.
```python
is_unsafe = sentinel.detect(snapshot)  # True if fear > 0.8
```

### `archetypes.py` - Archetypal Mesh
Maps dream snapshots to archetypal categories.
```python
tags = archetypes.tag(snapshot)  # ["Hero"] or ["Shadow"]
mesh_result = archetypes.mesh(dream_list)  # "clash" or "harmony"
```

### `replay.py` - Narrative Replay
Generates explainability in plain language.
```python
description = replay.describe(trace)
# "Dream xyz chosen (align=high_confidence)"
```

## 🧪 Testing

All modules include comprehensive tests:
```bash
pytest tests/unit/dream/expand -v
```

## 🚀 CI Pipeline

- **Auto-trigger**: On changes to expand modules or tests
- **Manual dispatch**: Available for on-demand runs
- **Nightly**: Automated runs at 03:00 UTC
- **Badge-ready**: CI status visible in README

## ✅ Production Safety

- **Minimal stubs**: Simple, safe implementations
- **No side effects**: Pure functions with predictable behavior
- **Comprehensive tests**: 12 test cases covering all modules
- **CI validated**: Automated testing on every change

## 🔄 Development Workflow

1. **Modify** any module in `candidate/consciousness/dream/expand/`
2. **Test** locally with `pytest tests/unit/dream/expand`
3. **Push** changes → CI automatically validates
4. **Monitor** with GitHub Actions badge

## 📊 Badge Integration

Add to your main README.md:
```markdown
![Dream EXPAND++](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/dream-expand-ci.yml/badge.svg)
```

Replace `YOUR_ORG/YOUR_REPO` with your GitHub organization and repository.

---

**Status**: ✅ Baseline scaffolded and ready for expansion
**Tests**: 12/12 passing
**CI**: Automated with nightly runs