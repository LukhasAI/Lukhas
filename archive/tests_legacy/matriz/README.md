---
status: wip
type: documentation
---
# MATRIZ Legacy Tests Archive

This directory contains obsolete/duplicated MATRIZ test files that were quarantined during the MATRIZ Tier-1 implementation.

## Files Archived

- `test_trace_fetch.py` - Original MATRIZ trace fetch test from tests/matriz/
- `test_trace_fetch_e2e.py` - Duplicate E2E test from tests_new/e2e/matriz/

## Reason for Quarantine

These files were replaced by the new MATRIZ Tier-1 test suite located at:
- `tests_new/matriz/test_traces_tier1.py`

The new tier-1 tests provide:
- FastAPI TestClient-based testing
- Proper tier1 and matriz markers
- Deterministic golden fallback testing
- Improved paging and filtering validation

## Archive Date

Quarantined on: 2025-09-11 during MATRIZ-R1 Tier-1 implementation

## Recovery

These files can be recovered if needed, but the new tier-1 test suite should be preferred for all MATRIZ trace API testing.