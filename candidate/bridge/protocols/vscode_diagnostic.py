#!/usr/bin/env python3
"""

#TAG:bridge
#TAG:protocols
#TAG:neuroplastic
#TAG:colony

VS Code Language & Status Bar Diagnostic Tool
Helps diagnose issues with language detection and status bar display
"""
import json
from pathlib import Path

import streamlit as st


def check_vscode_config():
    """Check VS Code configuration for language and status bar settings"""

    print("🔍 VS Code Configuration Diagnostic")
    print("=" * 50)

    # Check workspace settings
    workspace_settings = Path(".vscode/settings.json")
    if workspace_settings.exists():
        print("✅ Workspace settings found")
        try:
            with open(workspace_settings) as f:
                settings = json.load(f)

            # Check key settings
            key_settings = [
                "files.encoding",
                "files.associations",
                "workbench.statusBar.visible",
                "editor.formatOnSave",
                "editor.defaultFormatter",
            ]

            print("\n📋 Key Settings:")
            for setting in key_settings:
                if setting in settings:
                    print(f"  ✓ {setting}: {settings[setting]}")
                else:
                    print(f"  ❌ {setting}: Not configured")

        except Exception as e:
            print(f"❌ Error reading settings: {e}")
    else:
        print("❌ No workspace settings found")

    # Check for extensions
    print("\n🔌 Extension Requirements:")
    required_extensions = {
        "Prettier": "esbenp.prettier-vscode",
        "Python": "ms-python.python",
        "Pylance": "ms-python.vscode-pylance",
        "Error Lens": "usernamehw.errorlens",
    }

    for name, ext_id in required_extensions.items():
        print(f"  📦 {name} ({ext_id})")

    # Language associations
    print("\n🗣️ Language Associations Configured:")
    if workspace_settings.exists():
        try:
            with open(workspace_settings) as f:
                settings = json.load(f)

            if "files.associations" in settings:
                for pattern, lang in settings["files.associations"].items():
                    print(f"  {pattern} → {lang}")
            else:
                print("  ❌ No file associations configured")
        except BaseException:
            print("  ❌ Could not read associations")

    print("\n🎯 Quick Fixes:")
    print("1. Restart VS Code")
    print("2. Open Command Palette (Cmd+Shift+P)")
    print("3. Run: 'Developer: Reload Window'")
    print("4. Check View → Appearance → Status Bar")
    print("5. Right-click status bar to customize")

    print("\n✨ Test Steps:")
    print("1. Open: language_status_test.md")
    print("2. Check bottom-right for language mode")
    print("3. Click language mode to change it")
    print("4. Try formatting with Cmd+Shift+P → 'Format Document'")


if __name__ == "__main__":
    check_vscode_config()

# Λ Systems 2025 www.lukhas.ai
