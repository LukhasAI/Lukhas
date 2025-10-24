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

This repository includes a minimal FastAPI stub to unblock the registry smoke test locally and in CI. It uses HMAC as a checkpoint signature placeholder; replace with Dilithium2 when PQC is available.

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
- A lightweight `services/registry/registry_store.json` checkpoint and `services/registry/checkpoint.sig` are written per change.

