This `api/` directory is the canonical API implementation for ΛLens. It was created by migrating the `api_new/` implementation into `api/` so imports and entrypoints reference `api`.

The `api_new/` directory remains in the repository for reference but should no longer be used.

Next steps:
- Run tests to validate the migration: `python -m pytest tests/test_api_integration.py -q`
- Remove or archive `api_new/` after CI confirms the code paths.
