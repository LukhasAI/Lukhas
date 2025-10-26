#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import sys

STAR_RULES = [
    (re.compile(r'(governance|guardian|ethic)'), (["Ethics","Guardian"], 0.95)),
    (re.compile(r'identity'), (["Identity"], 0.90)),
    (re.compile(r'memory'), (["Memory"], 0.90)),
    (re.compile(r'(conscious|swarm|collective|cognitive)'), (["Consciousness"], 0.88)),
    (re.compile(r'vision'), (["Vision"], 0.85)),
    (re.compile(r'\bbio\b'), (["Bio"], 0.85)),
    (re.compile(r'dream'), (["Dream"], 0.85)),
    (re.compile(r'quantum'), (["Quantum"], 0.85)),
]

LANE_TIER = { 'core': 'integration', 'lukhas': 'production', 'matriz': 'integration' }

REQUIRED_FIELDS = [
    "name","path","constellation_stars","confidence","description",
    "status","tier","lane","version","created","updated","metadata"
]

def discover_packages(lanes):
    pkgs = set()
    for lane in lanes:
        root = lane  # enforce lowercase, real code lives under 'matriz/' not 'MATRIZ/'
        if not os.path.isdir(root):
            print(f"WARNING: lane '{lane}' root directory '{root}' not found; skipping", file=sys.stderr)
            continue
        found = 0
        for dirpath, dirnames, filenames in os.walk(root):
            if '__init__.py' in filenames:
                pkgs.add(dirpath)
                found += 1
        if found == 0:
            print(f"WARNING: lane '{lane}' contains no Python packages under '{root}'", file=sys.stderr)
    return sorted(pkgs)

def discover_manifests(lanes):
    paths = set()
    for lane in lanes:
        base = os.path.join('manifests', lane)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            if 'module.manifest.json' in filenames:
                rel = os.path.relpath(dirpath, 'manifests')
                paths.add(rel)
    return sorted(paths)

def decide_star(pkg: str):
    low = pkg.lower()
    for rx,(stars,conf) in STAR_RULES:
        if rx.search(low):
            return stars, conf
    if low.startswith('matriz/') or low == 'matriz':
        return ["Consciousness"], 0.85
    return ["Infrastructure"], 0.70

def build_manifest(pkg: str):
    lane = pkg.split('/')[0]
    name = pkg.replace('/', '.')
    stars, conf = decide_star(pkg)
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    return {
        "name": name,
        "path": pkg,
        "constellation_stars": stars,
        "confidence": conf,
        "description": f"Auto-generated manifest for {name}",
        "dependencies": [],
        "status": 'production' if lane=='lukhas' else 'integration',
        "tier": LANE_TIER.get(lane, 'integration'),
        "lane": lane,
        "version": "1.0.0",
        "created": now,
        "updated": now,
        "metadata": {"complexity":"medium","test_coverage":"unknown","documentation":"partial"}
    }

def write_manifest(m):
    out_dir = os.path.join('manifests', *m['path'].split('/'))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'module.manifest.json')
    with open(out_path, 'w') as f:
        json.dump(m, f, indent=2)
    return out_path

def main():
    ap = argparse.ArgumentParser(description='Generate manifests for orphan packages')
    ap.add_argument('--lanes', default='core,matriz', help='Comma-separated lanes to cover (core,matriz,lukhas)')
    ap.add_argument('--limit', type=int, default=0, help='Max manifests to generate (0 = no limit)')
    ap.add_argument('--dry-run', action='store_true', help='Show what would be generated, do not write files')
    args = ap.parse_args()

    lanes = [x.strip() for x in args.lanes.split(',') if x.strip()]
    pkgs = discover_packages(lanes)
    if not pkgs:
        print("WARNING: no packages discovered for requested lanes; check lane roots and case sensitivity", file=sys.stderr)
    manis = discover_manifests(lanes)
    have = set(manis)

    created = []
    count = 0
    for pkg in pkgs:
        rel = pkg
        if rel in have:
            continue
        m = build_manifest(rel)
        if args.dry_run:
            print(json.dumps(m, indent=2))
        else:
            p = write_manifest(m)
            created.append(p)
            count += 1
            if args.limit and count >= args.limit:
                break
    print(f"Created {count} manifests")
    if created:
        print("\n".join(created))

if __name__ == '__main__':
    sys.exit(main())
