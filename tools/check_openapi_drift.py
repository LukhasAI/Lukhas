"""
Stub: compare saved openapi.json vs. live FastAPI app schema.
Exits nonzero if drift detected (basic shape check).
"""
import json, sys
from fastapi.testclient import TestClient

try:
    from serve.main import app  # adjust import if needed
except Exception as e:
    print(f"Could not import app: {e}")
    sys.exit(0)

def main():
    live = TestClient(app).get("/openapi.json").json()
    try:
        with open("openapi.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
    except FileNotFoundError:
        print("No saved openapi.json; skipping drift check.")
        return

    # Very naive shape compare:
    live_keys = set(live.keys())
    saved_keys = set(saved.keys())
    if live_keys != saved_keys:
        print(f"OpenAPI top-level keys differ:\n live={live_keys}\n saved={saved_keys}")
        sys.exit(1)

    # Check paths presence only (not full deep diff to keep it cheap)
    lpaths = set(live.get("paths", {}).keys())
    spaths = set(saved.get("paths", {}).keys())
    missing = spaths - lpaths
    added = lpaths - spaths
    if missing or added:
        print(f"OpenAPI paths drift. missing={missing} added={added}")
        sys.exit(1)

if __name__ == "__main__":
    main()
