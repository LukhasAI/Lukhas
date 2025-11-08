#!/usr/bin/env python3
"""
Interactive API Key Setup Script
================================

Securely configure API keys in macOS Keychain for LUKHAS AI.

Usage:
    python scripts/setup_api_keys.py

    # Or directly from command line:
    python scripts/setup_api_keys.py --key JULES_API_KEY --value "your-key"

    # List stored keys:
    python scripts/setup_api_keys.py --list

    # Delete a key:
    python scripts/setup_api_keys.py --delete JULES_API_KEY
"""
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.security.keychain_manager import SUPPORTED_API_KEYS, KeychainManager


def setup_interactive():
    """Interactive setup wizard for API keys."""
    print("=" * 70)
    print("🔐 LUKHAS AI - Secure API Key Setup")
    print("=" * 70)
    print()
    print("This wizard will help you securely store API keys in macOS Keychain.")
    print("Your keys will be encrypted by the system and never stored in plaintext.")
    print()

    # Show currently configured keys
    print("📋 Currently configured keys:")
    stored_keys = KeychainManager.list_keys()
    if stored_keys:
        for key in stored_keys:
            print(f"  ✓ {key}")
    else:
        print("  (none)")
    print()

    # Ask which keys to configure
    print("Available API keys to configure:")
    for i, key in enumerate(SUPPORTED_API_KEYS, 1):
        has_key = KeychainManager.has_key(key)
        status = "✓ configured" if has_key else "○ not set"
        print(f"  {i}. {key:<25} [{status}]")
    print()

    while True:
        choice = input("Enter number to configure (or 'q' to quit): ").strip()

        if choice.lower() in ('q', 'quit', 'exit'):
            print("\n✅ Setup complete!")
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(SUPPORTED_API_KEYS):
                key_name = SUPPORTED_API_KEYS[index]
                configure_key(key_name)
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'q'.")


def configure_key(key_name: str):
    """Configure a single API key."""
    print(f"\n🔧 Configuring {key_name}")
    print("-" * 70)

    # Show where to get the key
    urls = {
        "JULES_API_KEY": "https://jules.ai (Settings > API Keys)",
        "OPENAI_API_KEY": "https://platform.openai.com/api-keys",
        "ANTHROPIC_API_KEY": "https://console.anthropic.com/",
        "GOOGLE_API_KEY": "https://makersuite.google.com/app/apikey",
        "PERPLEXITY_API_KEY": "https://www.perplexity.ai/settings/api",
    }

    if key_name in urls:
        print(f"Get your key from: {urls[key_name]}")
        print()

    # Check if key already exists
    if KeychainManager.has_key(key_name):
        overwrite = input(f"⚠️  {key_name} already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite not in ('y', 'yes'):
            print("Skipped.")
            return

    # Get key value securely (hidden input)
    key_value = getpass.getpass(f"Enter {key_name} (input hidden): ").strip()

    if not key_value:
        print("❌ No value provided. Skipped.")
        return

    # Confirm before storing
    print(f"Preview: {key_value[:8]}{'*' * (len(key_value) - 8)}")
    confirm = input("Store this key in Keychain? (Y/n): ").strip().lower()

    if confirm in ('', 'y', 'yes'):
        success = KeychainManager.set_key(key_name, key_value)
        if success:
            print(f"✅ {key_name} stored securely in macOS Keychain")
        else:
            print(f"❌ Failed to store {key_name}")
    else:
        print("Cancelled.")


def list_keys():
    """List all stored API keys."""
    print("🔐 API Keys in macOS Keychain (lukhas-ai):")
    print("-" * 70)

    keys = KeychainManager.list_keys()
    if keys:
        for key in keys:
            print(f"  ✓ {key}")
    else:
        print("  (no keys stored)")
    print()


def delete_key(key_name: str):
    """Delete an API key from Keychain."""
    if not KeychainManager.has_key(key_name):
        print(f"❌ {key_name} not found in Keychain")
        return

    confirm = input(f"⚠️  Delete {key_name} from Keychain? (y/N): ").strip().lower()
    if confirm in ('y', 'yes'):
        success = KeychainManager.delete_key(key_name)
        if success:
            print(f"✅ {key_name} deleted from Keychain")
        else:
            print(f"❌ Failed to delete {key_name}")
    else:
        print("Cancelled.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Securely configure API keys in macOS Keychain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive setup wizard
  python scripts/setup_api_keys.py

  # Set a specific key
  python scripts/setup_api_keys.py --key JULES_API_KEY --value "your-key"

  # List stored keys
  python scripts/setup_api_keys.py --list

  # Delete a key
  python scripts/setup_api_keys.py --delete JULES_API_KEY
        """
    )

    parser.add_argument(
        "--key",
        help="API key name to configure"
    )
    parser.add_argument(
        "--value",
        help="API key value to store"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all stored API keys"
    )
    parser.add_argument(
        "--delete",
        metavar="KEY_NAME",
        help="Delete an API key from Keychain"
    )

    args = parser.parse_args()

    # Handle command-line operations
    if args.list:
        list_keys()
    elif args.delete:
        delete_key(args.delete)
    elif args.key and args.value:
        success = KeychainManager.set_key(args.key, args.value)
        if success:
            print(f"✅ {args.key} stored securely")
        else:
            print(f"❌ Failed to store {args.key}")
    else:
        # Run interactive wizard
        setup_interactive()


if __name__ == "__main__":
    main()
