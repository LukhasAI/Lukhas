#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile


def fetch(path: str, out: str):
    if path.startswith("s3://"):
        subprocess.check_call(["aws", "s3", "cp", path, out])
    else:
        shutil.copy2(path, out)


def sha256_file(p: str) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path or s3:// to manifest.json")
    ap.add_argument(
        "--tarball",
        required=False,
        help="Path or s3:// to tarball (else read from manifest)",
    )
    ap.add_argument("--target", default=os.getenv("RESTORE_TARGET", "./_restore_sandbox"))
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.target, exist_ok=True)

    man_local = os.path.join(args.target, "_manifest.json")
    fetch(args.manifest, man_local)
    man = json.loads(open(man_local).read())

    tar_src = args.tarball or man["bundle"]["path"]
    tar_local = os.path.join(args.target, os.path.basename(tar_src))
    fetch(tar_src, tar_local)

    # verify bundle hash
    calc = sha256_file(tar_local)
    if calc != man["bundle"]["sha256"]:
        print(
            f"ERROR: bundle sha256 mismatch\n expected={man['bundle']['sha256']}\n   actual={calc}"
        )
        return 2

    # extract
    if args.dry_run:
        print(json.dumps({"ok": True, "verified": True, "dry_run": True}, indent=2))
        return 0

    mode = "r"
    if tar_local.endswith(".tar.zst"):
        mode = "r:zst"
    elif tar_local.endswith(".tar.gz"):
        mode = "r:gz"
    with tarfile.open(tar_local, mode) as tar:
        # safety: never extract outside of target
        def is_within(d, t):
            d = os.path.realpath(d)
            t = os.path.realpath(t)
            return os.path.commonpath([d, t]) == t

        for m in tar.getmembers():
            dest = os.path.join(args.target, m.name)
            if not is_within(dest, args.target):
                print(f"Skip unsafe path: {m.name}")
                continue
            tar.extract(m, path=args.target)

    print(json.dumps({"ok": True, "verified": True, "extracted_to": args.target}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
