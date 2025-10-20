# scripts/export_openapi_live.py
from pathlib import Path
import json
from lukhas.adapters.openai.api import get_app  # canonical factory

def main() -> None:
    app = get_app()
    spec = app.openapi()
    # enrich with version metadata if present in env/git (optional)
    Path("docs/openapi").mkdir(parents=True, exist_ok=True)
    out = Path("docs/openapi/lukhas-openapi.json")
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
