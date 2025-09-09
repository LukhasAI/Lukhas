import os
import sys

from fastapi.testclient import TestClient

# Ensure repo root is on sys.path so we can import the api module reliably
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", "..", "..", ".."))
sys.path.insert(0, REPO_ROOT)

try:
    from products.lambda.lambda_products_pack.lambda_core.Lens.api.main import app
except Exception:
    # Fallback: import by file path if package import fails
    import importlib.util

    module_path = os.path.join(
        REPO_ROOT, "lambda_products", "lambda_products_pack", "lambda_core", "Lens", "api", "main.py"
    )
    spec = importlib.util.spec_from_file_location("lens_api_main", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    app = mod.app


client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data and data["status"] == "healthy"