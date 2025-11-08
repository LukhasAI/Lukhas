#!/usr/bin/env python3
"""
Update Anthropic API Key in macOS Keychain

Interactive script to update the API key stored in keychain.

Usage:
    python3 scripts/update_keychain_key.py
    python3 scripts/update_keychain_key.py --key sk-ant-YOUR_NEW_KEY
"""

import argparse
import os
import re
import subprocess
import sys
from typing import Optional


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def validate_api_key(key: str) -> bool:
    """Validate Anthropic API key format"""
    pattern = r'^sk-ant-[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, key))


def get_current_key() -> Optional[str]:
    """Get current key from keychain"""
    try:
        result = subprocess.run(
            ['security', 'find-generic-password',
             '-s', 'LUKHASAI.ANTHROPIC_API_KEY',
             '-w'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None


def update_keychain(new_key: str) -> bool:
    """Update API key in keychain"""
    try:
        service = "LUKHASAI.ANTHROPIC_API_KEY"

        # Delete existing entry
        subprocess.run(
            ['security', 'delete-generic-password',
             '-s', service],
            capture_output=True,
            check=False  # Don't fail if doesn't exist
        )

        # Add new entry
        result = subprocess.run(
            ['security', 'add-generic-password',
             '-s', service,
             '-a', os.getenv('USER'),
             '-w', new_key],
            capture_output=True,
            text=True,
            check=True
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error updating keychain: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update Anthropic API key in macOS Keychain"
    )
    parser.add_argument(
        "--key",
        help="New API key (sk-ant-...)"
    )

    args = parser.parse_args()

    print_header("🔐 Update Anthropic API Key in Keychain")

    # Show current key
    current_key = get_current_key()
    if current_key:
        print(f"Current key: {current_key[:20]}...")
        print(f"Length: {len(current_key)} characters")
        print()
    else:
        print("No key currently in keychain\n")

    # Get new key
    if args.key:
        new_key = args.key
    else:
        print("Get a fresh API key from: https://console.anthropic.com/")
        print()
        new_key = input("Enter new API key (sk-ant-...): ").strip()

    # Validate
    if not validate_api_key(new_key):
        print("\n❌ Invalid API key format")
        print("   Must start with 'sk-ant-'")
        sys.exit(1)

    # Update
    print("\nUpdating keychain...")
    if update_keychain(new_key):
        print("✅ Keychain updated successfully!")
        print()
        print(f"New key: {new_key[:20]}...")
        print()
        print("Test it with:")
        print("  python3 scripts/test_claude_simple.py")
    else:
        print("❌ Failed to update keychain")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled by user")
        sys.exit(0)
