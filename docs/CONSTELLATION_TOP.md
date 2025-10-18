---
title: Constellation Top
updated: 2025-10-18
version: 1.0
owner: unassigned
---

# Constellation Top Overview

This document summarizes the eight-star Constellation system used across LUKHAS
to classify module intent and capabilities. Star assignments are generated from
manifests and can be auto-promoted from Supporting based on rules.

Stars
- ⚛️ Anchor (Identity)
- ✦ Trail (Memory)
- 🔬 Horizon (Vision)
- 🌱 Living (Bio)
- 🌙 Drift (Dream)
- ⚖️ North (Ethics)
- 🛡️ Watch (Guardian)
- 🔮 Oracle (Quantum)
- Supporting (default)

Notes
- Star assignments primarily live in `manifests/**/module.manifest.json` under `constellation_alignment.primary_star`.
- Phase 3 adds `--star-from-rules` to the manifest generator using `configs/star_rules.json` with confidence thresholds.
- Phase 4 regenerates manifests and updates dashboards; see `make top` for programmatic generation.

See also
- manifests/: Canonical module manifests
- configs/star_rules.json: Promotion rules and weights
- Makefile target `top`: scripts/gen_constellation_top.py

