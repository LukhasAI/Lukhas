#!/usr/bin/env python3
"""Interactive Auth0 configuration setup for LUKHAS MCP server."""

from pathlib import Path

def setup_auth0_config():
    """Interactive setup for Auth0 configuration."""
    print("🔐 Auth0 Configuration Setup for LUKHAS MCP Server")
    print("=" * 55)
    print()
    
    # Get current values
    env_file = Path(".env")
    current_config = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    current_config[key] = value
    
    print("Please provide your Auth0 configuration values:")
    print("(You can find these in your Auth0 dashboard)")
    print()
    
    # Get Auth0 tenant domain
    tenant_domain = input("🏢 Auth0 Tenant Domain (e.g., lukhas-ai.auth0.com): ").strip()
    if not tenant_domain:
        print("❌ Tenant domain is required!")
        return False
    
    # Get API identifier
    api_identifier = input("🔗 API Identifier (e.g., https://api.lukhas.ai): ").strip()
    if not api_identifier:
        print("❌ API identifier is required!")
        return False
    
    # Get public URL
    public_url = input("🌐 Public Base URL [http://localhost:8080]: ").strip()
    if not public_url:
        public_url = "http://localhost:8080"
    
    # Build OAuth issuer URL
    oauth_issuer = f"https://{tenant_domain}/.well-known/openid-configuration"
    
    # Prepare new configuration
    new_config = {
        "LUKHAS_MCP_ROOTS": current_config.get("LUKHAS_MCP_ROOTS", "/Users/agi_dev/LOCAL-REPOS/Lukhas"),
        "WRITE_ENABLED": current_config.get("WRITE_ENABLED", "false"),
        "OAUTH_ISSUER": oauth_issuer,
        "OAUTH_AUDIENCE": api_identifier,
        "PUBLIC_BASE_URL": public_url
    }
    
    # Write new .env file
    env_content = f"""# Colon-separated absolute paths the server may read (and write if enabled)
LUKHAS_MCP_ROOTS={new_config['LUKHAS_MCP_ROOTS']}

# Optional: enable write tool (off by default)
WRITE_ENABLED={new_config['WRITE_ENABLED']}

# === Auth0 OAuth Configuration ===
# OIDC discovery endpoint
OAUTH_ISSUER={new_config['OAUTH_ISSUER']}

# API audience/identifier from Auth0
OAUTH_AUDIENCE={new_config['OAUTH_AUDIENCE']}

# Public base URL of this server
PUBLIC_BASE_URL={new_config['PUBLIC_BASE_URL']}
"""
    
    # Show preview
    print("\n📝 Configuration Preview:")
    print("-" * 40)
    print(env_content)
    print("-" * 40)
    
    confirm = input("\n✅ Save this configuration? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Configuration saved to {env_file}")
        print()
        print("🚀 Next steps:")
        print("1. Get a test JWT token from Auth0 dashboard:")
        print(f"   Auth0 Dashboard → APIs → LUKHAS MCP API → Test tab")
        print("2. Start the server: python server.py")
        print("3. Test with JWT: curl -H 'Authorization: Bearer <jwt>' http://localhost:8080/sse/")
        
        return True
    else:
        print("❌ Configuration not saved")
        return False

if __name__ == "__main__":
    try:
        setup_auth0_config()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")