# Lukhas Commercial API

Expose core Lukhas capabilities using FastAPI.

## Usage

```bash
uvicorn serve.main:app --reload
```

## Endpoints

### `POST /generate-dream/`
Generates a symbolic dream.

Example:
```bash
curl -X POST "http://localhost:8000/generate-dream/" \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["alpha", "beta"]}'
```

### `POST /glyph-feedback/`
Returns adjustment suggestions from drift/collapse metrics.

```bash
curl -X POST "http://localhost:8000/glyph-feedback/" \
     -H "Content-Type: application/json" \
     -d '{"driftScore": 0.1, "collapseHash": "abc"}'
```

### `POST /tier-auth/`
Resolves a symbolic token to access rights.

```bash
curl -X POST "http://localhost:8000/tier-auth/" \
     -H "Content-Type: application/json" \
     -d '{"token": "symbolic-tier-1"}'
```

### `POST /plugin-load/`
Registers plugin symbols.

```bash
curl -X POST "http://localhost:8000/plugin-load/" \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["modA"]}'
```

### `GET /memory-dump/`
Exports symbolic folds and emotional state.

```bash
curl "http://localhost:8000/memory-dump/"
```
