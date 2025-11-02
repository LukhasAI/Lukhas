#!/usr/bin/env python3
import os
from pathlib import Path


def load(path):
    p = Path(path)
    if not p.exists(): return []
    with p.open() as f: return [ln.strip() for ln in f if ln.strip()]

def stat(batch):
    done = load(batch + ".done")
    todo = [ln for ln in load(batch) if ln not in set(done)]
    return done, todo

def rows(batch):
    done, todo = stat(batch)
    bname = os.path.basename(batch)
    return {
        "batch": bname,
        "total": len(done) + len(todo),
        "done": len(done),
        "remaining": len(todo),
        "next": (todo[0] if todo else "")
    }

def fmt(r):
    n = r["next"].split("\t")[0] if r["next"] else ""
    return f"{r['batch']:<24} | total:{r['total']:>3}  done:{r['done']:>3}  rem:{r['remaining']:>3}  next:{n}"

if __name__ == "__main__":
    batches = sys.argv[1:] or [
        "/tmp/batch_matriz.tsv",
        "/tmp/batch_core.tsv",
        "/tmp/batch_serve.tsv"
    ]
    for b in batches:
        if not Path(b).exists():
            print(f"{os.path.basename(b):<24} | (missing)")
            continue
        print(fmt(rows(b)))
