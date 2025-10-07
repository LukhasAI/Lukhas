---
status: wip
type: documentation
owner: unknown
module: planning
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Features Directory Consolidation Plan

## Overview
The `features/` directory contains 15 subdirectories that should be distributed to their proper locations.

## Consolidation Mapping

### 1. **features/api/** → `api/core/`
- Contains dream_api.py which duplicates api/core/dream.py
- Should be merged or removed

### 2. **features/config/** → `config/`
- Move all configuration files to main config directory
- 20+ config files that belong in central config

### 3. **features/core/** → `core/base/`
- Base classes (base_config, base_health, base_module)
- Core utilities (logger, ethics, symbolic)

### 4. **features/creative_engine/** → `creativity/engines/`
- Creative engine implementation
- Already have creativity/engines directory

### 5. **features/crista_optimizer/** → `bio/optimization/`
- Biological optimization components
- Related to bio systems

### 6. **features/data_manager/** → `core/data/`
- CRUD operations
- Core data management

### 7. **features/decision/** → `reasoning/decision/`
- Decision bridge
- Part of reasoning system

### 8. **features/diagnostic_engine/** → `trace/diagnostics/`
- Diagnostic payloads and engine
- Belongs with trace/monitoring

### 9. **features/docututor/** → `tools/documentation/`
- Documentation generation
- Development tool

### 10. **features/drift/** → `trace/drift/`
- Drift tracking system
- Part of monitoring

### 11. **features/entropy/** → `trace/entropy/`
- Entropy radar
- Monitoring component

### 12. **features/governance/** → `governance/`
- Governance components
- Merge with main governance

### 13. **features/integration/** → Distribute to relevant modules
- bio_awareness → `bio/awareness/`
- governance → `governance/integration/`
- meta_cognitive → `consciousness/meta_cognitive/`
- safety → `security/safety/`
- Others → `core/integration/`

### 14. **features/memory/** → `memory/advanced/`
- Advanced memory implementations
- Memory fold systems

### 15. **features/symbolic/** → `symbolic/`
- Merge with main symbolic directory
- Contains glyphs, drift, security subdirectories

## Execution Plan

1. Create necessary subdirectories
2. Move files preserving structure
3. Update imports
4. Remove empty features directory
5. Update documentation

## Expected Result
- Complete elimination of features/ directory
- Better organized codebase
- Clearer module boundaries
- No duplicate functionality
