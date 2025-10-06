---
status: wip
type: documentation
---
# Module Manifest Schema Changelog

## Version 3.1.0 (2025-10-02)

**Non-breaking additions:**
- Added `aliases` array for legacy import paths
- Added `deprecations` array for migration planning
- Both fields are optional with empty array defaults

**Rationale:**
Enable smooth module consolidation and renaming without breaking imports.

## Version 3.0.0 (Previous)

Initial T4/0.01%-hardened schema with comprehensive module metadata.
