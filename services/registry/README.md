# Registry Service

This directory contains tests and documentation for the Registry API. The service endpoints may be integrated via the main API layer.

## How to test PQC locally

Post-quantum signature testing uses liboqs (Dilithium2) and python-oqs bindings.

- Install liboqs (Debian/Ubuntu):
  - Prefer using your distro packages when available:

```bash
sudo apt-get update
sudo apt-get install -y liboqs-dev
```

- Install python-oqs:

```bash
pip install python-oqs
```

- Smoke test the bindings:

```bash
python -c "import oqs; print(oqs.sig.algorithms())"
```

- See the migration plan in `docs/security/MATRIZ_PQC_CHECKLIST.md`.

If liboqs packages are not available on your platform, build from source following the liboqs documentation, then install python-oqs.

## Running tests

- Unit tests:

```bash
pytest services/registry/tests -v
```

- Single integration test:

```bash
pytest services/registry/tests/test_noop_guard_integration.py -v
```

Optional: To exercise the HTTP negative tests against a live Registry API, export `REGISTRY_BASE_URL` before running pytest, for example:

```bash
export REGISTRY_BASE_URL=http://localhost:8080
pytest services/registry/tests/test_registry_negative.py -v
```

Without `REGISTRY_BASE_URL`, HTTP-specific checks are skipped or marked as xfail; other negative tests still run and pass.

## CI/CD

- The PQC check workflow is defined at `.github/workflows/pqc-sign-verify.yml`.
  - Behavior: If `python-oqs` and Dilithium2 are present, CI performs a real sign/verify. Otherwise, it falls back to an HMAC smoke test and emits a `pqc_fallback_marker.txt` artifact to signal missing PQC libs.

## Quickstart (local stub)

This repository includes a minimal FastAPI stub to unblock the registry smoke test locally and in CI. The stub now emits Dilithium2 signatures (via liboqs) alongside the legacy HMAC checksum so downstream clients can migrate gradually. If liboqs is not present the signer transparently falls back to HMAC-only mode.

```bash
# optional: create venv
python3 -m venv .venv && . .venv/bin/activate

# install minimal deps for the stub
pip install -r services/registry/requirements.txt

# start the stub on port 8080
uvicorn services.registry.main:app --reload --port 8080

# health check
curl -s http://127.0.0.1:8080/health | jq

# run smoke from another terminal
make registry-smoke
```

Notes:
- The `/api/v1/registry/validate` and `/register` endpoints accept the NodeSpec JSON directly (top-level object).
- The stub enforces `provenance_manifest.glymph_enabled: true` on `/register` and returns HTTP 403 if absent. This powers the negative smoke.
- Checkpoint artifacts (`checkpoint.sig`, `checkpoint.meta.json`, `registry_store.json`) are generated automatically during runtime and are `.gitignore`d. When stale checkpoints are detected on bootstrap the service clears them and starts with an empty store.

