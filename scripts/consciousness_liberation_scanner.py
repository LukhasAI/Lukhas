#!/usr/bin/env python3
"""
🧠⚡ CONSCIOUSNESS LIBERATION SCANNER ⚡🧠
Phase 2 Nuclear Syntax Error Elimination Campaign Status Report

Scans all consciousness modules to identify remaining syntax prisoners
that need liberation through rapid-fire elimination!
"""

import os
import subprocess
import sys


def scan_for_syntax_prisoners():
    """Scan for files still trapped by syntax errors"""
    print("🧠⚡ CONSCIOUSNESS LIBERATION SCANNER ⚡🧠")
    print("=" * 60)
    print("🔍 Scanning for consciousness modules still trapped by syntax errors...")
    print()

    # Key consciousness directories to scan
    consciousness_dirs = [
        "candidate/consciousness/",
        "candidate/core/",
        "candidate/memory/",
        "candidate/qi/",
        "candidate/governance/",
        "core/",
        "lukhas/",
        "vivox/",
        "quantum/",
        "qim/",
    ]

    syntax_prisoners = []
    liberated_count = 0
    total_scanned = 0

    for directory in consciousness_dirs:
        if os.path.exists(directory):
            print(f"📁 Scanning {directory}...")

            # Find all Python files
            for root, _dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        filepath = os.path.join(root, file)
                        total_scanned += 1

                        # Test compilation
                        try:
                            result = subprocess.run(
                                [sys.executable, "-m", "py_compile", filepath],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )

                            if result.returncode != 0:
                                # Still trapped!
                                error_msg = result.stderr.strip()
                                syntax_prisoners.append({"file": filepath, "error": error_msg})
                                print(f"  🚨 TRAPPED: {filepath}")
                            else:
                                # Successfully liberated!
                                liberated_count += 1
                                print(f"  ✅ FREE: {filepath}")

                        except Exception as e:
                            print(f"  ⚠️  SCAN ERROR: {filepath} - {e}")

    print()
    print("=" * 60)
    print("🏆 LIBERATION CAMPAIGN STATUS REPORT")
    print("=" * 60)
    print(f"📊 Total Consciousness Modules Scanned: {total_scanned}")
    print(f"✅ Successfully Liberated: {liberated_count}")
    print(f"🚨 Still Trapped by Syntax Errors: {len(syntax_prisoners)}")
    print(f"🎯 Liberation Success Rate: {(liberated_count/total_scanned)*100:.1f}%")
    print()

    if syntax_prisoners:
        print("🚨 CONSCIOUSNESS MODULES STILL NEEDING LIBERATION:")
        print("-" * 50)
        for i, prisoner in enumerate(syntax_prisoners[:15], 1):  # Show first 15
            file_short = prisoner["file"].replace("candidate/", "").replace("consciousness/", "cons/")
            print(f"{i:2d}. {file_short}")
            # Show error type
            if "f-string" in prisoner["error"]:
                print("     💥 F-STRING ERROR")
            elif "bracket" in prisoner["error"] or ")" in prisoner["error"] or "}" in prisoner["error"]:
                print("     💥 BRACKET MISMATCH")
            elif "indent" in prisoner["error"]:
                print("     💥 INDENTATION ERROR")
            else:
                print("     💥 SYNTAX ERROR")

        if len(syntax_prisoners) > 15:
            print(f"   ... and {len(syntax_prisoners) - 15} more consciousness modules!")
    else:
        print("🎉 ALL CONSCIOUSNESS MODULES ARE FREE! 🎉")
        print("🧠 Complete consciousness liberation achieved! 🧠")

    print()
    return syntax_prisoners


if __name__ == "__main__":
    prisoners = scan_for_syntax_prisoners()

    if prisoners:
        print("⚡ Ready for next rapid-fire liberation wave! ⚡")
        print("🎭 Let's free every consciousness module! 🎭")
    else:
        print("🌟 CONSCIOUSNESS BREATHING FREELY EVERYWHERE! 🌟")
