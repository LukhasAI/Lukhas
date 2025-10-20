#!/usr/bin/env python3
"""
Module: backup_create.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

import argparse
import contextlib
import fnmatch
import hashlib
import json
import os
import pathlib
import sys
import tarfile
from datetime import datetime, timezone


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def match_any(path, patterns):
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)


def gather_files(roots, excludes):
    files = []
    for root in roots:
        rp = pathlib.Path(root)
        if not rp.exists():
            continue
        for p in rp.rglob("*"):
            if p.is_file():
                rel = str(p)
                if match_any(rel, excludes):
                    continue
                files.append(rel)
    files.sort()
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include", nargs="+", required=True)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = args.tag or ts
    os.makedirs(args.outdir, exist_ok=True)

    files = gather_files(args.include, args.exclude)
    manifest = {"version": 1, "tag": tag, "created_utc": ts, "files": []}

    # Choose compression
    comp = "gz"
    with contextlib.suppress(Exception):
        comp = "zst"

    tar_name = f"lukhas_backup_{tag}.tar.{comp}"
    tar_path = os.path.join(args.outdir, tar_name)

    mode = f"w:{comp}"
    with tarfile.open(tar_path, mode) as tar:
        for f in files:
            st = os.stat(f)
            manifest["files"].append(
                {
                    "path": f,
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                    "sha256": sha256_file(f),
                }
            )
            tar.add(f, arcname=f)

    manifest["bundle"] = {
        "path": tar_path,
        "sha256": sha256_file(tar_path),
        "size": os.stat(tar_path).st_size,
        "algo": "zstd" if comp == "zst" else "gzip",
    }
    out_manifest = os.path.join(args.outdir, f"{tar_name}.manifest.json")

    # Optional HMAC signing
    secret = os.getenv("BACKUP_HMAC_SECRET", "")
    if secret:
        hm = hashlib.sha256()
        hm.update(secret.encode("utf-8"))
        hm.update(json.dumps(manifest, sort_keys=True).encode("utf-8"))
        manifest["hmac_sha256"] = hm.hexdigest()

    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(
        json.dumps(
            {
                "ok": True,
                "tarball": tar_path,
                "manifest": out_manifest,
                "file_count": len(files),
                "comp": comp,
                "created_utc": ts,
            },
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
