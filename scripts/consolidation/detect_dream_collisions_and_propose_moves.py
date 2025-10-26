#!/usr/bin/env python3
"""
Detect collisions/duplicates across dream/, dreams/, dreamweaver_helpers_bundle/
and prepare a safe, reviewable 'proposed_moves.sh' to move files into
labs/consciousness/dream/{synthesis,helpers,results,helpers/<bundle>}
Run with --dry-run to only print/report.
"""
import os,sys,hashlib,argparse,shutil

SRC_DIRS = ['dream','dreams','dreamweaver_helpers_bundle']
DEST_BASE = 'labs/consciousness/dream'
DEST_HELPERS = os.path.join(DEST_BASE,'helpers')
DEST_RESULTS = os.path.join(DEST_BASE,'results')
DEST_SYNTH = os.path.join(DEST_BASE,'synthesis')

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def walk_files(dirs):
    files = {}
    for d in dirs:
        if not os.path.exists(d): continue
        for root,_,names in os.walk(d):
            for n in names:
                p=os.path.join(root,n)
                files.setdefault(n,[]).append(p)
    return files

def detect_duplicates(files):
    hash_map = {}
    for name,paths in files.items():
        for p in paths:
            try:
                s=sha256(p)
            except Exception as e:
                s = None
            hash_map.setdefault(s,[]).append(p)
    dups = {h:ps for h,ps in hash_map.items() if len(ps)>1 and h is not None}
    return dups

def propose_moves(files):
    moves = []
    for name,paths in files.items():
        for p in paths:
            # decide destination
            # heuristics: if path contains 'helpers' -> DEST_HELPERS
            lp = p.lower()
            if 'helper' in lp or 'helpers' in lp:
                dest_dir = DEST_HELPERS
            elif 'result' in lp or 'outputs' in lp or 'images' in lp:
                dest_dir = DEST_RESULTS
            else:
                dest_dir = DEST_SYNTH
            # ensure destination exists
            dest_subdir = os.path.join(dest_dir)
            # create a relative dest path that preserves subdir structure (under dest)
            rel = os.path.relpath(p)
            # create a safe name: if a file with same name exists in dest_subdir, append suffix
            base_name = os.path.basename(p)
            dest_path = os.path.join(dest_subdir, base_name)
            i = 1
            while os.path.exists(dest_path):
                # if identical file (sha), we will remove duplicate
                if os.path.exists(dest_path):
                    try:
                        if sha256(dest_path) == sha256(p):
                            # identical file: plan to REMOVE duplicate (or skip move)
                            dest_path = None
                            break
                    except Exception:
                        pass
                # make a renamed destination
                name_only, ext = os.path.splitext(base_name)
                dest_path = os.path.join(dest_subdir, f"{name_only}_from_{os.path.basename(os.path.dirname(p))}{('_'+str(i)) if i>1 else ''}{ext}")
                i+=1
            if dest_path:
                moves.append((p, dest_path))
            else:
                moves.append((p, None))  # duplicate identical -> will be removed
    return moves

def write_proposed(moves, out='proposed_moves.sh'):
    lines = ["#!/bin/bash", "set -euo pipefail", "echo '=== PROPOSED MOVES — REVIEW BEFORE EXECUTION ==='"]
    for src,dst in moves:
        if dst is None:
            lines.append("# DUPLICATE (identical sha) - REMOVE: {}".format(src))
        else:
            lines.append("echo 'PROPOSE: git mv -v \"{}\" \"{}\"'".format(src,dst))
    lines.append("echo '--- End of proposed moves. Edit as needed. To execute, remove the echo and run this script.'")
    with open(out,'w') as f:
        f.write("\n".join(lines))
    os.chmod(out,0o755)
    print(f"Wrote {out} with {len(moves)} entries. Inspect before executing.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=False)
    args = parser.parse_args()
    files = walk_files(SRC_DIRS)
    dups = detect_duplicates(files)
    print("Files with same filename count (potential collisions):")
    for k,v in sorted(files.items(), key=lambda kv: -len(kv[1])):
        if len(v)>1:
            print(f"{k}:")
            for p in v: print("  ",p)
    print("\nDetected identical file duplicates (same sha):")
    for h,ps in dups.items():
        print("sha:",h)
        for p in ps: print("  ",p)
    moves = propose_moves(files)
    write_proposed(moves)
    if not args.dry_run:
        print("NOTE: This script will not perform moves. Edit proposed_moves.sh to execute moves.")
    else:
        print("Dry-run complete. Check ./proposed_moves.sh for review.")

if __name__=='__main__':
    main()
