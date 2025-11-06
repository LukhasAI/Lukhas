#!/usr/bin/env python3
"""
tools/build_audit_pack.py

Usage:
  python3 tools/build_audit_pack.py --claim-id matriz-p95-2025q3 \
      --artifacts release_artifacts/perf/2025-10-26-matriz-smoke.json \
      --out audit-packs/matriz-p95-2025q3.zip \
      --sign  # optional, requires gpg

Produces:
 - audit-packs/<pack>.zip containing artifacts, metadata.json, and optionally metadata.json.asc (gpg signature)
"""
import argparse, json, os, sys, shutil, hashlib
from pathlib import Path
import datetime
import subprocess

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(8192)
            if not b: break
            h.update(b)
    return h.hexdigest()

def build_pack(claim_id, artifacts, out_zip, signer=None):
    out_dir = Path("tmp_audit_pack") / claim_id
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    artifacts_meta = []
    for art in artifacts:
        path = Path(art)
        if not path.exists():
            print(f"Missing artifact: {art}", file=sys.stderr)
            sys.exit(2)
        dest = out_dir / path.name
        shutil.copy2(path, dest)
        artifacts_meta.append({
            "file": str(path.name),
            "path": str(path),
            "sha256": sha256_file(path),
            "size": path.stat().st_size
        })
    metadata = {
        "claim_id": claim_id,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "artifacts": artifacts_meta,
        "tool": "build_audit_pack.py"
    }
    md_file = out_dir / "metadata.json"
    md_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    # Optionally sign metadata.json
    if signer:
        # signer is gpg key id or True for default gpg
        sig_file = out_dir / "metadata.json.asc"
        cmd = ["gpg", "--armor", "--output", str(sig_file), "--detach-sign", str(md_file)]
        if isinstance(signer, str):
            cmd = ["gpg", "--armor", "--output", str(sig_file), "--local-user", signer, "--detach-sign", str(md_file)]
        print("Signing metadata.json with gpg...")
        subprocess.check_call(cmd)
    # Create zip
    out_zip = Path(out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    shutil.make_archive(str(out_zip.with_suffix('')), 'zip', root_dir=out_dir)
    print(f"Created audit pack: {out_zip}")
    # cleanup
    shutil.rmtree(out_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--artifacts", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sign", action="store_true", help="Sign metadata.json with gpg (needs gpg key)")
    parser.add_argument("--key", help="GPG key id to sign with (optional)")
    args = parser.parse_args()
    signer = args.key if args.key else (True if args.sign else None)
    build_pack(args.claim_id, args.artifacts, args.out, signer=signer)

if __name__=='__main__':
    main()
