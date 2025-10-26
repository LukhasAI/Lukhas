#!/usr/bin/env python3
"""
Safe installer for THE_VAULT MCP server into Claude Desktop configuration.
Creates backup before modifying configuration.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


def install_vault_mcp():
    """Install THE_VAULT MCP server configuration"""

    # Paths
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    backup_path = config_path.parent / f"claude_desktop_config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    print("🧭 THE_VAULT MCP Server Installer")
    print("=" * 60)

    # Check if config exists
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        return False

    print(f"✅ Found config: {config_path}")

    # Create backup
    print(f"📦 Creating backup: {backup_path}")
    shutil.copy2(config_path, backup_path)
    print("✅ Backup created successfully")

    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Check if already installed
    if "vault-research" in config.get("mcpServers", {}):
        print("\n⚠️  vault-research MCP server already installed!")
        print("   No changes made.")
        return True

    # Add vault-research server
    vault_config = {
        "command": "/opt/homebrew/bin/python3.11",
        "args": ["/Users/agi_dev/LOCAL-REPOS/THE_VAULT/00_ORGANIZATION_PROJECT/mcp_server_vault_research.py"],
        "env": {
            "VAULT_ROOT": "/Users/agi_dev/LOCAL-REPOS/THE_VAULT",
            "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/THE_VAULT/00_ORGANIZATION_PROJECT",
            "MCP_LOG_LEVEL": "INFO"
        }
    }

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["vault-research"] = vault_config

    # Write updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("\n✅ vault-research MCP server installed successfully!")
    print("\n📊 MCP Server Details:")
    print("   Name: vault-research")
    print("   Location: /Users/agi_dev/LOCAL-REPOS/THE_VAULT/00_ORGANIZATION_PROJECT/")
    print("   Documents: 604")
    print("   Concepts: 14")
    print("   Tools: 6 (vault_stats, vault_concept_map, vault_search, etc.)")
    print("   Prompts: 2 (explore_concept, find_research)")

    print("\n🔄 Next Steps:")
    print("   1. Restart Claude Desktop to load the new MCP server")
    print("   2. Look for 'vault-research' in the MCP servers list")
    print("   3. Try tools like vault_stats or vault_concept_map")

    print("\n💾 Backup saved at:")
    print(f"   {backup_path}")

    return True


if __name__ == "__main__":
    try:
        success = install_vault_mcp()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
