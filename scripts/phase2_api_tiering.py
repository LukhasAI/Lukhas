#!/usr/bin/env python3
"""
Module: phase2_api_tiering.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Phase 2: API Manifest Tiering & Contract Validation

Systematically assigns star ratings to API modules based on:
- Public-facing vs internal APIs
- Integration with external systems (OpenAI compatibility, etc.)
- Guardian/authentication requirements
- Business-critical vs supporting functionality

Usage:
  python scripts/phase2_api_tiering.py --manifests manifests --dry-run
  python scripts/phase2_api_tiering.py --manifests manifests --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]

# API Tiering Rules (Phase 2 - EXECUTION_PLAN.md)
API_TIER_RULES = {
    "🛡️ Watch (Guardian)": {
        "keywords": ["auth", "oidc", "oauth", "security", "guardian", "policy", "rbac"],
        "patterns": ["authentication", "authorization", "identity"],
        "priority": 1,
    },
    "⚛️ Anchor (Identity)": {
        "keywords": ["identity", "profile", "account", "session", "user"],
        "patterns": ["lambda_id", "λid", "tier", "persona"],
        "priority": 2,
    },
    "🌊 Flow (Consciousness)": {
        "keywords": ["consciousness", "awareness", "attention", "metacognition"],
        "patterns": ["api/consciousness", "api/platform"],
        "priority": 3,
    },
    "✦ Trail (Memory)": {
        "keywords": ["memory", "retrieval", "cache", "embedding", "vector"],
        "patterns": ["memory_api", "recall"],
        "priority": 4,
    },
    "Supporting": {
        "keywords": [],
        "patterns": [],
        "priority": 10,  # Default
    },
}


def analyze_api_module(manifest_path: pathlib.Path) -> Tuple[str, float, str]:
    """
    Analyze API module and suggest star rating.
    
    Returns: (suggested_star, confidence, reason)
    """
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return ("Supporting", 0.0, f"Failed to read: {e}")
    
    mod = data.get("module", {}) or {}
    name = mod.get("name", "")
    path = mod.get("path", "")
    current_star = (data.get("constellation_alignment", {}) or {}).get("primary_star", "Supporting")
    
    capabilities = data.get("capabilities", []) or []
    security = data.get("security", {}) or {}
    
    # Don't override if already assigned to a specific star
    if current_star != "Supporting":
        return (current_star, 1.0, "Already assigned (preserving)")
    
    # Analyze content
    full_text = f"{name} {path}".lower()
    for cap in capabilities:
        full_text += f" {cap.get('name', '')} {cap.get('description', '')}".lower()
    
    scores: Dict[str, float] = {}
    reasons: List[str] = []
    
    for star, rules in API_TIER_RULES.items():
        score = 0.0
        
        # Keyword matching
        for keyword in rules["keywords"]:
            if keyword in full_text:
                score += 0.4
                reasons.append(f"{star}: keyword '{keyword}'")
        
        # Pattern matching (stronger signal)
        for pattern in rules["patterns"]:
            if pattern in full_text:
                score += 0.6
                reasons.append(f"{star}: pattern '{pattern}'")
        
        # Security context boost for Guardian
        if star == "🛡️ Watch (Guardian)" and security.get("requires_auth"):
            score += 0.5
            reasons.append(f"{star}: requires_auth=true")
        
        if score > 0:
            scores[star] = score
    
    if not scores:
        return ("Supporting", 0.0, "No specific API patterns detected")
    
    # Get highest scoring star
    best_star = max(scores.items(), key=lambda x: x[1])[0]
    confidence = min(scores[best_star], 1.0)
    reason = "; ".join([r for r in reasons if best_star in r][:3])
    
    return (best_star, confidence, reason)


def main():
    parser = argparse.ArgumentParser(description="Phase 2: API Manifest Tiering")
    parser.add_argument("--manifests", default="manifests", help="Manifests root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply star rating changes")
    parser.add_argument("--min-confidence", type=float, default=0.60, help="Minimum confidence for auto-assignment")
    args = parser.parse_args()
    
    root = pathlib.Path(args.manifests)
    
    # Find all API-related manifests
    api_manifests = []
    for pattern in ["*/api/*", "*/bridge/*", "*/adapters/openai/*", "*/public_api/*"]:
        api_manifests.extend(root.glob(f"**/{pattern}/module.manifest.json"))
    
    # Remove duplicates and archived
    api_manifests = list(set([m for m in api_manifests if "/.archive/" not in str(m)]))
    api_manifests.sort()
    
    print(f"Found {len(api_manifests)} API-related manifests\n")
    
    changes = []
    for manifest in api_manifests:
        suggested_star, confidence, reason = analyze_api_module(manifest)
        
        # Read current state
        data = json.loads(manifest.read_text(encoding="utf-8"))
        current_star = (data.get("constellation_alignment", {}) or {}).get("primary_star", "Supporting")
        
        if suggested_star != current_star and confidence >= args.min_confidence:
            changes.append({
                "path": str(manifest),
                "current": current_star,
                "suggested": suggested_star,
                "confidence": confidence,
                "reason": reason,
            })
            
            status = "[DRY]" if args.dry_run else "[OK]"
            print(f"{status} {manifest.parent.name}")
            print(f"      Current: {current_star}")
            print(f"      Suggest: {suggested_star} (conf: {confidence:.2f})")
            print(f"      Reason: {reason}")
            print()
            
            if args.apply and not args.dry_run:
                # Apply the change
                if "constellation_alignment" not in data:
                    data["constellation_alignment"] = {}
                data["constellation_alignment"]["primary_star"] = suggested_star
                
                # Update metadata
                if "metadata" not in data:
                    data["metadata"] = {}
                data["metadata"]["last_updated"] = "2025-10-18T00:00:00Z"
                
                manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    
    print(f"\n{'=' * 60}")
    print(f"Summary: {len(changes)} modules with suggested changes")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLIED' if args.apply else 'ANALYSIS ONLY'}")
    print(f"Confidence threshold: {args.min_confidence}")
    
    if changes:
        print(f"\nStar Distribution:")
        star_counts: Dict[str, int] = {}
        for change in changes:
            star = change["suggested"]
            star_counts[star] = star_counts.get(star, 0) + 1
        
        for star, count in sorted(star_counts.items(), key=lambda x: -x[1]):
            print(f"  {star}: {count}")


if __name__ == "__main__":
    main()
