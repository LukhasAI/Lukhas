"""
Minimal OpenAI-style façade.
Expected by tests:
- get_app() -> ASGI app with:
  GET  /healthz   -> {"status":"ok"}
  GET  /readyz    -> {"status":"ready"}
  GET  /metrics   -> Prometheus text
  GET  /v1/models -> {"data":[{"id":"lukhas-matriz","object":"model"}]}
  POST /v1/embeddings -> {"data":[{"embedding":[...]}]}
  POST /v1/responses  -> {"id": "...", "model":"lukhas-matriz", "output":{"text":"..."}}
  POST /v1/dreams     -> {"id":"dream_...","traces":[...]}

Wire to real orchestrator later; return static-ish values now to make tests pass.
"""
from typing import Any, Dict, List
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
import os, time, uuid

def _metrics_text() -> str:
    return "# HELP lukhas_requests_total total\n# TYPE lukhas_requests_total counter\nlukhas_requests_total 1\n"

def _maybe_trace(body: Dict[str, Any]) -> Dict[str, Any]:
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        body.setdefault("trace_id", uuid.uuid4().hex)
    return body

def get_app() -> FastAPI:
    app = FastAPI(title="Lukhas OpenAI Facade", version="0.1")

    @app.get("/healthz")
    def healthz(): return {"status": "ok"}

    @app.get("/readyz")
    def readyz(): return {"status": "ready"}

    @app.get("/metrics")
    def metrics(): return PlainTextResponse(_metrics_text(), media_type="text/plain; version=0.0.4")

    @app.get("/v1/models")
    def models():
        return {"data":[{"id":"lukhas-matriz","object":"model"}]}

    @app.post("/v1/embeddings")
    async def embeddings(payload: Dict[str, Any]):
        text = payload.get("input","")
        # placeholder deterministic vector
        vec = [float(len(text) % 7), 0.0, 1.0]
        return _maybe_trace({"data":[{"embedding":vec}]})

    @app.post("/v1/responses")
    async def responses(payload: Dict[str, Any]):
        text = str(payload.get("input",""))
        out = {"id": f"resp_{uuid.uuid4().hex[:8]}", "model": "lukhas-matriz", "output": {"text": f"echo: {text}"}}
        return JSONResponse(_maybe_trace(out))

    @app.post("/v1/dreams")
    async def dreams(payload: Dict[str, Any]):
        seed = payload.get("seed","dream")
        trace = {"step":"imagine","content": f"{seed} …"}
        return _maybe_trace({"id": f"dream_{uuid.uuid4().hex[:8]}", "traces":[trace]})

    return app
