# ===============================================================
# 📂 FILE: tools/tier.py
# 🧠 PURPOSE: CLI command to print LUCAS AGI symbolic tier levels
# ===============================================================

import argparse

import streamlit as st

TIER_DATA = {
    1: {
        "name": "Public Observer",
        "access": [
            "Read-only dream and memory logs",
            "View symbolic summaries and public dashboard",
        ],
        "restrictions": [
            "No voice access",
            "No memory editing",
            "No publishing or dream proposal",
        ],
    },
    2: {
        "name": "Contributor",
        "access": [
            "Suggest symbolic posts and dream ideas",
            "Preview voice synthesis",
            "Access contributor widgets",
        ],
        "restrictions": ["No memory changes", "No governance access"],
    },
    3: {
        "name": "Developer",
        "access": [
            "Patch memory and simulate thoughts",
            "Full CLI + symbolic interface access",
            "Vote in development-tier proposals",
        ],
        "restrictions": ["No DAO override power", "Cannot submit live dream traces"],
    },
    4: {
        "name": "Researcher",
        "access": [
            "Create and trace symbolic dreams",
            "Access research tools + audit layers",
            "Propose changes to symbolic governance",
        ],
        "restrictions": ["Cannot approve proposals", "No override of sealed memories"],
    },
    5: {
        "name": "Governor",
        "access": [
            "Full DAO access and override approval",
            "Approve dream injections and voice mutations",
            "View all symbolic trace and ethics layers",
        ],
        "restrictions": ["DAO quorum required for certain actions"],
    },
}


def print_tier(level):
    if level not in TIER_DATA:
        print("❌ Invalid tier level.")
        return
    tier = TIER_DATA[level]
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    # Use ASCII hyphen-minus instead of Unicode dash for linting
    print(f"{level}️⃣  TIER {level} - {tier['name'].upper()}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔓 ACCESS:")
    for item in tier["access"]:
        print(f"• {item}")
    print("\n🔒 RESTRICTIONS:")
    for item in tier["restrictions"]:
        print(f"• {item}")


def main():
    parser = argparse.ArgumentParser(description="🎚️ View or simulate LUCAS AGI symbolic tiers")
    parser.add_argument("--simulate", type=int, help="Simulate privileges of a given tier (1-5)")
    args = parser.parse_args()

    if args.simulate:
        print(f"\n🔮 SIMULATING TIER {args.simulate}:\n")
        print_tier(args.simulate)
    else:
        # Use hyphen instead of EN DASH for lint compliance
        print("\n🎚️ LUCAS AGI - SYMBOLIC TIER OVERVIEW")
        for i in range(1, 6):
            print_tier(i)

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🌿 Tiers reflect symbolic trust - not hierarchy.")
        print("🔗 Run 'lucasagi-ethics' for full ethics preview.\n")


if __name__ == "__main__":
    main()
