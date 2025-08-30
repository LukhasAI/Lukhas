# path: qi/safety/provenance_uploader.py
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

# --------- ENV & defaults ---------
STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
LOCAL_DIR = os.path.join(STATE, "provenance")
os.makedirs(LOCAL_DIR, exist_ok=True)

BACKEND = os.environ.get("PROV_BACKEND", "local").lower()  # local | s3 | gcs
S3_BUCKET = os.environ.get("PROV_S3_BUCKET")
S3_PREFIX = os.environ.get("PROV_S3_PREFIX", "lukhas/provenance/")
GCS_BUCKET = os.environ.get("PROV_GCS_BUCKET")
GCS_PREFIX = os.environ.get("PROV_GCS_PREFIX", "lukhas/provenance/")

#  Integrate with signed attestation from qi.ops.provenance
_HAVE_ATTEST = False
try:
    from qi.ops.provenance import attest as _attest, merkle_chain

    _HAVE_ATTEST = True
except Exception:
    _HAVE_ATTEST = False


# --------- hashing helpers ---------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def guess_mime(path: str) -> str:
    m, _ = mimetypes.guess_type(path)
    return m or "application/octet-stream"


# --------- data classes ---------
@dataclass
class ProvenanceRecord:
    # Artifact identity
    artifact_path: str  # local absolute path (for source-of-truth copy)
    artifact_sha256: str
    size_bytes: int
    mime_type: str

    # Storage info
    storage_backend: str  # local | s3 | gcs
    storage_url: str  # file://..., s3://bucket/key, gs://bucket/key

    # Context
    created_at: float  # epoch seconds
    model_id: str | None = None
    prompt_hash: str | None = None
    parameters: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    # Links (optional)
    attestation: dict[str, Any] | None = None  # from qi.ops.provenance.attest()
    extra_attachments: list[dict[str, Any]] | None = (
        None  # e.g., list of {"path","sha256","storage_url"}
    )

    # Versioning
    schema_version: str = "1.0.0"


# --------- upload backends ----------
class Uploader:
    def put(self, *, local_path: str, key_hint: str | None = None) -> tuple[str, str]:
        """Return (storage_url, sha256)."""
        raise NotImplementedError


class LocalUploader(Uploader):
    def __init__(self, base_dir: str = LOCAL_DIR):
        self.base = base_dir
        os.makedirs(self.base, exist_ok=True)

    def put(self, *, local_path: str, key_hint: str | None = None) -> tuple[str, str]:
        sha = sha256_file(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        rel = os.path.join(sha[:2], f"{sha}{ext or ''}")
        dst = os.path.join(self.base, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            # hardlink if same fs, else copy
            try:
                os.link(local_path, dst)
            except Exception:
                with open(local_path, "rb") as s, open(dst, "wb") as d:
                    for chunk in iter(lambda: s.read(65536), b""):
                        d.write(chunk)
        return ("file://" + dst, sha)


class S3Uploader(Uploader):
    def __init__(self, bucket: str, prefix: str = S3_PREFIX):
        try:
            import boto3  # type: ignore
        except Exception as e:
            raise RuntimeError("S3Uploader requires boto3: pip install boto3") from e
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/"

    def put(self, *, local_path: str, key_hint: str | None = None) -> tuple[str, str]:
        sha = sha256_file(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        key = f"{self.prefix}{sha[:2]}/{sha}{ext or ''}"
        extra_args = {"ContentType": guess_mime(local_path)}
        self.s3.upload_file(local_path, self.bucket, key, ExtraArgs=extra_args)
        return (f"s3://{self.bucket}/{key}", sha)


class GCSUploader(Uploader):
    def __init__(self, bucket: str, prefix: str = GCS_PREFIX):
        try:
            from google.cloud import storage  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "GCSUploader requires google-cloud-storage: pip install google-cloud-storage"
            ) from e
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket)
        self.prefix = prefix.rstrip("/") + "/"

    def put(self, *, local_path: str, key_hint: str | None = None) -> tuple[str, str]:
        sha = sha256_file(local_path)
        ext = os.path.splitext(local_path)[1].lower()
        key = f"{self.prefix}{sha[:2]}/{sha}{ext or ''}"
        blob = self.bucket.blob(key)
        blob.upload_from_filename(local_path, content_type=guess_mime(local_path))
        return (f"gs://{self.bucket.name}/{key}", sha)


def resolve_uploader() -> Uploader:
    if BACKEND == "local":
        return LocalUploader(LOCAL_DIR)
    if BACKEND == "s3":
        if not S3_BUCKET:
            raise RuntimeError("Set PROV_S3_BUCKET for S3 backend.")
        return S3Uploader(S3_BUCKET, S3_PREFIX)
    if BACKEND == "gcs":
        if not GCS_BUCKET:
            raise RuntimeError("Set PROV_GCS_BUCKET for GCS backend.")
        return GCSUploader(GCS_BUCKET, GCS_PREFIX)
    raise RuntimeError(f"Unknown PROV_BACKEND {BACKEND}")


# --------- core API ----------
def record_artifact(
    artifact_path: str,
    *,
    model_id: str | None = None,
    prompt: str | None = None,
    parameters: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    attestation_steps: list[dict[str, Any]] | None = None,
    extra_files: list[str] | None = None,
) -> ProvenanceRecord:
    """
    - Hashes local artifact
    - Uploads via chosen backend
    - Optionally signs a Merkle chain (requires qi.ops.provenance + pynacl)
    - Optionally uploads extra attachments (logs, prompts, raw outputs)
    - Writes a JSON record alongside the backend and returns the object
    """
    artifact_path = os.path.abspath(artifact_path)
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(artifact_path)

    uploader = resolve_uploader()
    storage_url, sha = uploader.put(local_path=artifact_path)

    att: dict[str, Any] | None = None
    if attestation_steps and _HAVE_ATTEST:
        chain = merkle_chain(attestation_steps)
        att_obj = _attest(chain, tag="prod")  # write signed attestation
        att = {
            "chain_path": att_obj.chain_path,
            "signature_b64": att_obj.signature_b64,
            "public_key_b64": att_obj.public_key_b64,
            "root_hash": att_obj.root_hash,
        }

    extras: list[dict[str, Any]] = []
    if extra_files:
        for p in extra_files:
            p = os.path.abspath(p)
            if not os.path.exists(p):
                continue
            url, h = uploader.put(local_path=p)
            extras.append({"path": p, "sha256": h, "storage_url": url, "mime_type": guess_mime(p)})

    rec = ProvenanceRecord(
        artifact_path=artifact_path,
        artifact_sha256=sha,
        size_bytes=os.path.getsize(artifact_path),
        mime_type=guess_mime(artifact_path),
        storage_backend=BACKEND,
        storage_url=storage_url,
        created_at=time.time(),
        model_id=model_id,
        prompt_hash=sha256_bytes(prompt.encode("utf-8")) if prompt is not None else None,
        parameters=parameters or {},
        metadata=metadata or {},
        attestation=att,
        extra_attachments=extras or None,
    )

    # persist a copy of the record locally (by hash)
    rec_path = os.path.join(LOCAL_DIR, "records", sha[:2])
    os.makedirs(rec_path, exist_ok=True)
    with open(os.path.join(rec_path, f"{sha}.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(rec), f, indent=2)

    return rec


def load_record_by_sha(sha: str) -> dict[str, Any]:
    """Load a local JSON record by artifact SHA."""
    path = os.path.join(LOCAL_DIR, "records", sha[:2], f"{sha}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Record not found: {path}")
    return json.load(open(path, encoding="utf-8"))


def verify_artifact(local_path: str, record: dict[str, Any]) -> dict[str, Any]:
    """Verify local file hash matches the recorded hash. Returns dict with 'ok' and details."""
    if not os.path.exists(local_path):
        return {"ok": False, "reason": "local_file_missing"}
    local_sha = sha256_file(local_path)
    ok = local_sha == record.get("artifact_sha256")
    return {
        "ok": ok,
        "local_sha256": local_sha,
        "record_sha256": record.get("artifact_sha256"),
        "storage_url": record.get("storage_url"),
        "backend": record.get("storage_backend"),
    }


# --------- CLI ----------
def _cli_record(args):
    meta = json.loads(args.metadata) if args.metadata else {}
    params = json.loads(args.parameters) if args.parameters else {}
    extras = args.attach or []

    att_steps = None
    if args.attest:
        # minimal, privacy-safe default steps
        att_steps = [
            {"phase": "input", "model_id": args.model_id},
            {"phase": "artifact", "path": os.path.abspath(args.artifact)},
            {"phase": "output_meta", "mime": guess_mime(args.artifact)},
        ]

    rec = record_artifact(
        args.artifact,
        model_id=args.model_id,
        prompt=args.prompt,
        parameters=params,
        metadata=meta,
        attestation_steps=att_steps,
        extra_files=extras,
    )
    print(json.dumps(asdict(rec), indent=2))


def _cli_verify(args):
    if args.sha:
        rec = load_record_by_sha(args.sha)
    else:
        rec = json.load(open(args.record, encoding="utf-8"))
    v = verify_artifact(args.local, rec)
    print(json.dumps(v, indent=2))
    if not v["ok"]:
        raise SystemExit(2)


def _cli_show(args):
    rec = load_record_by_sha(args.sha)
    print(json.dumps(rec, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Lukhas Provenance Attachments Uploader")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("record", help="Hash+upload an artifact and write a local record")
    p1.add_argument("artifact", help="Path to local file to record")
    p1.add_argument("--model-id")
    p1.add_argument("--prompt", help="Raw prompt text (we store hash only)", default=None)
    p1.add_argument("--parameters", help="JSON dict of model/route params", default=None)
    p1.add_argument("--metadata", help="JSON dict of misc metadata", default=None)
    p1.add_argument("--attach", nargs="*", help="Extra files to upload and link")
    p1.add_argument(
        "--attest",
        action="store_true",
        help="Also write a signed Merkle attestation (requires pynacl)",
    )
    p1.set_defaults(func=_cli_record)

    p2 = sub.add_parser("verify", help="Verify local file against a record")
    p2.add_argument("--local", required=True, help="Path to local file to verify")
    g = p2.add_mutually_exclusive_group(required=True)
    g.add_argument("--record", help="Path to a JSON record file")
    g.add_argument("--sha", help="Artifact SHA to load from local registry")
    p2.set_defaults(func=_cli_verify)

    p3 = sub.add_parser("show", help="Show a stored record by SHA")
    p3.add_argument("--sha", required=True)
    p3.set_defaults(func=_cli_show)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
