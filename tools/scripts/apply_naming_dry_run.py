#!/usr/bin/env python3
"""
LUKHAS Naming Convention Dry Run
Shows what changes would be made without applying them
"""

import os
import sys

from scripts.apply_lukhas_naming_conventions import LukhasNamingApplicator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    applicator = LukhasNamingApplicator()

    print("🚀 LUKHAS Naming Convention Analysis (DRY RUN)\n")
    applicator.apply_refinements(dry_run=True)

    print("\n✅ Analysis complete. No changes were made.")
    print("\nTo apply changes, run:")
    print("   python3 tools/scripts/apply_lukhas_naming_conventions.py")
    print("   Then type 'yes' when prompted")


if __name__ == "__main__":
    main()