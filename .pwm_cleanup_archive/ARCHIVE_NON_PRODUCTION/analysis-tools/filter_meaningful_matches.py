# \!/usr/bin/env python3
"""Filter out trivial matches and find meaningful integration opportunities"""

import json


def filter_meaningful_matches(input_file="high_confidence_matches.json"):
    with open(input_file) as f:
        data = json.load(f)

    # Filter out matches that are just 'main' function
    meaningful_85 = []
    meaningful_75 = []

    for match in data["matches_85_plus"]:
        if "func:main" not in match["details"]:
            meaningful_85.append(match)

    for match in data["matches_75_to_84"]:
        if "func:main" not in match["details"]:
            meaningful_75.append(match)

    # Get unique counts
    unique_85 = len(set(m["isolated_file"] for m in meaningful_85))
    unique_75 = len(set(m["isolated_file"] for m in meaningful_75))

    print("=" * 70)
    print("MEANINGFUL HIGH-CONFIDENCE MATCHES (excluding 'main' function matches)")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"  - Meaningful 85%+ matches: {len(meaningful_85)}")
    print(f"  - Meaningful 75-84% matches: {len(meaningful_75)}")
    print(f"  - Unique files with 85%+ match: {unique_85}")
    print(f"  - Unique files with 75%+ match: {unique_75 + unique_85}")

    if meaningful_85:
        print("\n✨ Top Meaningful 85%+ Matches:")
        for i, match in enumerate(meaningful_85[:20], 1):
            print(f"\n  {i}. {match['isolated_file']}")
            print(f"     → {match['target_file']}")
            print(f"     Confidence: {match['confidence']:.1%}")
            print(f"     Type: {match['match_type']}")
            print(f"     {match['details']}")

    if meaningful_75:
        print("\n🎯 Top Meaningful 75-84% Matches:")
        for i, match in enumerate(meaningful_75[:10], 1):
            print(f"\n  {i}. {match['isolated_file']}")
            print(f"     → {match['target_file']}")
            print(f"     Confidence: {match['confidence']:.1%}")
            print(f"     Type: {match['match_type']}")
            print(f"     {match['details']}")

    # Save filtered results
    filtered_data = {
        "summary": {
            "meaningful_85_plus": len(meaningful_85),
            "meaningful_75_plus": len(meaningful_75) + len(meaningful_85),
            "unique_files_85": unique_85,
            "unique_files_75": unique_75 + unique_85,
        },
        "meaningful_85_plus": meaningful_85,
        "meaningful_75_to_84": meaningful_75,
    }

    with open("meaningful_matches.json", "w") as f:
        json.dump(filtered_data, f, indent=2)

    return filtered_data


if __name__ == "__main__":
    filter_meaningful_matches()
