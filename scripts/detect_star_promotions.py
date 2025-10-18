#!/usr/bin/env python3
"""Detect star promotions between commits."""

import json
import sys
from pathlib import Path
from subprocess import check_output, CalledProcessError
import argparse

def get_manifest_stars(commit):
    """Get all star assignments at a commit."""
    stars = {}
    
    # Get list of manifest files at this commit
    try:
        files_output = check_output(
            ["git", "ls-tree", "-r", "--name-only", commit, "manifests/"],
            text=True
        )
        manifest_files = [f for f in files_output.strip().split('\n') 
                         if f.endswith('module.manifest.json')]
    except CalledProcessError:
        return {}
    
    for manifest_file in manifest_files:
        try:
            content = check_output(
                ["git", "show", f"{commit}:{manifest_file}"],
                text=True
            )
            data = json.loads(content)
            module_path = data.get('module', {}).get('path', '')
            star = data.get('constellation_alignment', {}).get('primary_star', 'Supporting')
            if module_path:
                stars[module_path] = star
        except:
            continue
    
    return stars

def normalize_star(star):
    """Normalize star name from various formats."""
    if not star:
        return 'Supporting'
    
    # Extract star name from emoji format
    star_map = {
        'anchor': 'Anchor',
        'trail': 'Trail',
        'horizon': 'Horizon',
        'watch': 'Watch',
        'flow': 'Flow',
        'spark': 'Spark',
        'persona': 'Persona',
        'oracle': 'Oracle',
        'living': 'Living',
        'drift': 'Drift',
        'supporting': 'Supporting'
    }
    
    star_lower = star.lower()
    for key, value in star_map.items():
        if key in star_lower:
            return value
    
    return 'Supporting'

def main():
    parser = argparse.ArgumentParser(description='Detect star promotions between commits')
    parser.add_argument('--base', required=True, help='Base commit')
    parser.add_argument('--head', required=True, help='Head commit')
    parser.add_argument('--fail-on-unapproved', action='store_true',
                       help='Exit with error if promotions found')
    args = parser.parse_args()
    
    base_stars = get_manifest_stars(args.base)
    head_stars = get_manifest_stars(args.head)
    
    promotions = []
    star_rank = {
        "Supporting": 0, "Flow": 1, "Trail": 2, "Anchor": 3,
        "Watch": 4, "Horizon": 5, "Oracle": 6, "Living": 7, "Drift": 8
    }
    
    for module, head_star in head_stars.items():
        base_star = base_stars.get(module, 'Supporting')
        
        # Normalize star names
        base_star_norm = normalize_star(base_star)
        head_star_norm = normalize_star(head_star)
        
        base_rank = star_rank.get(base_star_norm, 0)
        head_rank = star_rank.get(head_star_norm, 0)
        
        if head_rank > base_rank:
            promotions.append({
                'module': module,
                'from': base_star_norm,
                'to': head_star_norm,
                'rank_change': head_rank - base_rank
            })
    
    if promotions:
        print(f"🔍 Detected {len(promotions)} star promotions:\n")
        for p in sorted(promotions, key=lambda x: x['rank_change'], reverse=True):
            print(f"  📈 {p['module']}: {p['from']} → {p['to']} (+{p['rank_change']})")
        
        if args.fail_on_unapproved:
            print("\n❌ Star promotions require approval from module owners")
            print("   Please ensure OWNERS have approved these changes.")
            sys.exit(1)
    else:
        print("✅ No star promotions detected")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
