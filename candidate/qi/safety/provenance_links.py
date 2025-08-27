# path: qi/safety/provenance_links.py
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
from typing import Any

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))

# ---------- tiny utils ----------
_S3_RE = re.compile(r"^s3://([^/]+)/(.+)$")
_GS_RE = re.compile(r"^gs://([^/]+)/(.+)$")
_FILE_RE = re.compile(r"^file://(.+)$")

def _parse_storage_url(url: str) -> tuple[str, str, str]:
    """
    Returns (scheme, bucket_or_root, key_or_path).
    Supports s3://, gs://, file://
    """
    if m := _S3_RE.match(url):
        return ("s3", m.group(1), m.group(2))
    if m := _GS_RE.match(url):
        return ("gs", m.group(1), m.group(2))
    if m := _FILE_RE.match(url):
        p = m.group(1)
        return ("file", os.path.dirname(p) or "/", os.path.basename(p))
    raise ValueError(f"Unsupported storage_url: {url}")

def _load_record_by_sha(sha: str) -> dict[str, Any]:
    rec_path = os.path.join(STATE, "provenance", "records", sha[:2], f"{sha}.json")
    if not os.path.exists(rec_path):
        raise FileNotFoundError(f"Record not found: {rec_path}")
    return json.load(open(rec_path, encoding="utf-8"))

# ---------- S3 presign ----------
def _s3_presign(bucket: str, key: str, expires: int, *, filename: str | None, content_type: str | None) -> str:
    try:
        import boto3  # type: ignore
    except Exception as e:
        raise RuntimeError("S3 presign requires boto3. pip install boto3") from e
    s3 = boto3.client("s3")
    params = {"Bucket": bucket, "Key": key}
    if filename:
        params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
    if content_type:
        params["ResponseContentType"] = content_type
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
        ExpiresIn=int(expires),
    )

# ---------- GCS presign (V4) ----------
def _gcs_presign(bucket: str, key: str, expires: int, *, filename: str | None, content_type: str | None) -> str:
    try:
        from google.cloud import storage  # type: ignore
    except Exception as e:
        raise RuntimeError("GCS presign requires google-cloud-storage. pip install google-cloud-storage") from e
    client = storage.Client()
    b = client.bucket(bucket)
    blob = b.blob(key)
    response_disposition = f'attachment; filename="{filename}"' if filename else None
    return blob.generate_signed_url(
        version="v4",
        expiration=int(expires),
        method="GET",
        response_disposition=response_disposition,
        response_type=content_type or None,
    )

# ---------- Local "presign" ----------
def _file_link(path_root: str, name: str) -> str:
    # For local artifacts, we just return file:// (your UI/backend should proxy/serve if needed).
    full = os.path.join(path_root, name)
    return "file://" + os.path.abspath(full)

# ---------- Public API ----------
def presign_url(
    storage_url: str,
    *,
    expires: int = 900,
    filename: str | None = None,
    content_type: str | None = None,
) -> dict[str, Any]:
    """
    Return a dict: {"url": ..., "expires_in": seconds, "backend": "s3|gcs|file", "note": "..."}.
    """
    scheme, bucket_or_root, key_or_path = _parse_storage_url(storage_url)
    if scheme == "s3":
        url = _s3_presign(bucket_or_root, key_or_path, expires, filename=filename, content_type=content_type)
        return {"backend": "s3", "url": url, "expires_in": int(expires)}
    if scheme == "gs":
        url = _gcs_presign(bucket_or_root, key_or_path, expires, filename=filename, content_type=content_type)
        return {"backend": "gcs", "url": url, "expires_in": int(expires)}
    if scheme == "file":
        url = _file_link(bucket_or_root, key_or_path)
        return {
            "backend": "file",
            "url": url,
            "expires_in": None,
            "note": "Local file link; consider proxying via your app for remote users."
        }
    raise ValueError(f"Unsupported scheme for {storage_url}")

def presign_for_record(
    record_or_sha: dict[str, Any] | str,
    *,
    expires: int = 900,
    filename: str | None = None,
) -> dict[str, Any]:
    """
    Accepts:
      - sha (str): loads record from ~/.lukhas/state/provenance/records/..
      - record dict (from provenance_uploader)
    Returns dict with url + metadata. Content-Type derived from record when available.
    """
    if isinstance(record_or_sha, str):
        rec = _load_record_by_sha(record_or_sha)
    else:
        rec = record_or_sha

    storage_url = rec.get("storage_url")
    if not storage_url:
        raise ValueError("Record has no storage_url.")

    # default filename = SHA.ext if record has mime/extension guessable
    if not filename:
        sha = rec.get("artifact_sha256", "artifact")
        # try to deduce extension from storage_url path
        parsed = urllib.parse.urlparse(storage_url)
        ext = os.path.splitext(parsed.path)[1] if parsed.path else ""
        filename = f"{sha}{ext}"

    return presign_url(storage_url, expires=expires, filename=filename, content_type=rec.get("mime_type"))

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="Provenance presigned URL fetcher (S3/GCS/file)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("sign-url", help="Presign a raw storage_url")
    p1.add_argument("--url", required=True, help="s3://... | gs://... | file://...")
    p1.add_argument("--expires", type=int, default=900)
    p1.add_argument("--filename")
    p1.add_argument("--content-type")
    p1.set_defaults(func=lambda a: print(json.dumps(
        presign_url(a.url, expires=a.expires, filename=a.filename, content_type=a.content_type), indent=2)))

    p2 = sub.add_parser("sign", help="Presign for a provenance record")
    g = p2.add_mutually_exclusive_group(required=True)
    g.add_argument("--sha", help="Artifact SHA256 to load record from local registry")
    g.add_argument("--record", help="Path to a record JSON file")
    p2.add_argument("--expires", type=int, default=900)
    p2.add_argument("--filename")
    def _run_sign(a):
        rec = _load_record_by_sha(a.sha) if a.sha else json.load(open(a.record, encoding="utf-8"))
        print(json.dumps(presign_for_record(rec, expires=a.expires, filename=a.filename), indent=2))
    p2.set_defaults(func=_run_sign)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
