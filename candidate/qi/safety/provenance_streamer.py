# path: qi/safety/provenance_streamer.py
from __future__ import annotations

import os
import re
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from qi.ops.metrics_middleware import (
    PROV_STREAM_BYTES,
    PROV_STREAM_LAT,
    PROV_STREAM_REQ,
    PrometheusMiddleware,
    metrics_endpoint,
)
from qi.safety.provenance_receipts import write_receipt
from qi.safety.provenance_uploader import load_record_by_sha

# Reuse URL parsing from the presigner (inline minimal parser to avoid deps)
_S3_RE = re.compile(r"^s3://([^/]+)/(.+)$")
_GS_RE = re.compile(r"^gs://([^/]+)/(.+)$")
_FILE_RE = re.compile(r"^file://(.+)$")

def _parse_storage_url(url: str):
    if m := _S3_RE.match(url):
        return ("s3", m.group(1), m.group(2))
    if m := _GS_RE.match(url):
        return ("gcs", m.group(1), m.group(2))
    if m := _FILE_RE.match(url):
        p = m.group(1)
        return ("file", os.path.dirname(p) or "/", os.path.basename(p))
    raise ValueError(f"Unsupported storage_url: {url}")

app = FastAPI(title="Lukhas Provenance Streamer", version="1.0.0")
app.add_middleware(PrometheusMiddleware)
app.add_api_route("/metrics", metrics_endpoint(), methods=["GET"])

# Add rate limiting
from qi.ops.rate_limit import BucketConfig, RateLimiter


def is_prov(req):
    p = req.url.path
    return p.startswith("/provenance/") and any(seg in p for seg in ("/stream", "/download", "/link"))

buckets = {
    "prov": BucketConfig(capacity=60, refill_per_sec=1.0)  # 60 requests per minute
}
rules = [(is_prov, "prov")]
app.add_middleware(RateLimiter, buckets=buckets, rules=rules)

def _client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host if req.client else "unknown"

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/provenance/{sha}/stream")
def stream_artifact(sha: str, request: Request, filename: str | None = None, chunk_bytes: int = 1024 * 256):
    """
    Streams the artifact to the client from S3/GCS/local **without** redirect.
    Emits a signed receipt and Prometheus metrics, and sets Content-Disposition if filename provided.
    """
    try:
        rec = load_record_by_sha(sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Record not found for {sha}: {e}")

    storage_url = rec.get("storage_url")
    if not storage_url:
        raise HTTPException(status_code=400, detail="Record missing storage_url")

    backend, a, b = _parse_storage_url(storage_url)
    media_type = rec.get("mime_type") or "application/octet-stream"
    PROV_STREAM_REQ.labels(backend).inc()

    # Local file direct stream
    if backend == "file":
        path = storage_url.replace("file://", "")
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Local artifact missing")
        write_receipt(
            artifact_sha=sha, event="download_stream",
            user_id=request.headers.get("x-user-id"),
            url=storage_url, client_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            purpose=request.query_params.get("purpose"),
            extras={"backend": "file"}
        )
        return FileResponse(path, filename=filename or os.path.basename(path), media_type=media_type)

    # S3/GCS: stream by reading from the backend in chunks
    if backend == "s3":
        try:
            import boto3  # type: ignore
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 support requires boto3: {e}")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=a, Key=b)
        body = obj["Body"]  # botocore.response.StreamingBody

        def gen() -> Iterator[bytes]:
            with PROV_STREAM_LAT.labels("s3").time():
                total = 0
                while True:
                    chunk = body.read(chunk_bytes)
                    if not chunk:
                        break
                    total += len(chunk)
                    PROV_STREAM_BYTES.labels("s3").inc(len(chunk))
                    yield chunk
                # write receipt after the stream finishes
                write_receipt(
                    artifact_sha=sha, event="download_stream",
                    user_id=request.headers.get("x-user-id"),
                    url=f"s3://{a}/{b}", client_ip=_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    purpose=request.query_params.get("purpose"),
                    extras={"backend": "s3", "bytes": total}
                )
        headers = {}
        if filename:
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return StreamingResponse(gen(), media_type=media_type, headers=headers)

    if backend == "gcs":
        try:
            from google.cloud import storage  # type: ignore
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GCS support requires google-cloud-storage: {e}")
        client = storage.Client()
        bucket = client.bucket(a)
        blob = bucket.blob(b)

        def gen() -> Iterator[bytes]:
            # Use a streaming download
            # open() yields a file-like object
            with PROV_STREAM_LAT.labels("gcs").time():
                total = 0
                with blob.open("rb") as fh:
                    while True:
                        chunk = fh.read(chunk_bytes)
                        if not chunk:
                            break
                        total += len(chunk)
                        PROV_STREAM_BYTES.labels("gcs").inc(len(chunk))
                        yield chunk
                write_receipt(
                    artifact_sha=sha, event="download_stream",
                    user_id=request.headers.get("x-user-id"),
                    url=f"gs://{a}/{b}", client_ip=_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    purpose=request.query_params.get("purpose"),
                    extras={"backend": "gcs", "bytes": total}
                )
        headers = {}
        if filename:
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return StreamingResponse(gen(), media_type=media_type, headers=headers)

    raise HTTPException(status_code=400, detail=f"Unsupported backend: {backend}")
