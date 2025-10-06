---
status: wip
type: documentation
---
ΛLens API (api_new) - ARCHIVED

This directory has been superseded by `../api/` and is retained for history.
Please use `lambda_products.lambda_products_pack.lambda_core.Lens.api` as the canonical package.
=====================

Quick start for developers.

Run locally (venv activated):

```bash
python cli.py --host 127.0.0.1 --port 8000 --reload
```

Run tests (from repo root):

```bash
PYTHONPATH=$(pwd)/lambda_products/lambda_products_pack/lambda_core/Lens \
  .venv/bin/python -m pytest lambda_products/lambda_products_pack/lambda_core/Lens/tests -q
```

Build Docker image (simple/dev):

```bash
docker build -t llens-api:dev .
docker run -p 8000:8000 llens-api:dev
```

Notes
- `cli.py` ensures the repository root is on PYTHONPATH so imports resolve.
- This Dockerfile is minimal for development; for production use multi-stage builds and pinned deps.
