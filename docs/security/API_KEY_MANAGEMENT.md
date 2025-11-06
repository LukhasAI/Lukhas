# Secure API Key Management

## Overview

LUKHAS uses **macOS Keychain** for secure API key storage. This is the most secure way to store credentials on macOS, as keys are:
- Encrypted by the operating system
- Protected by FileVault
- Never stored in plaintext
- Accessible only to your user account

## Quick Setup

### Option 1: Interactive Setup (Recommended)

Run the setup wizard:

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python scripts/setup_api_keys.py
```

The wizard will:
1. Show currently configured keys
2. Guide you through setting up each API key
3. Store keys securely in Keychain
4. Never display keys in plaintext

### Option 2: Command Line

Set a specific key:

```bash
python scripts/setup_api_keys.py --key JULES_API_KEY --value "your-key-here"
```

List all stored keys:

```bash
python scripts/setup_api_keys.py --list
```

Delete a key:

```bash
python scripts/setup_api_keys.py --delete JULES_API_KEY
```

### Option 3: Manual Keychain Setup

Using macOS `security` command directly:

```bash
# Store a key
security add-generic-password \
  -s lukhas-ai \
  -a JULES_API_KEY \
  -w "your-actual-api-key" \
  -U

# Retrieve a key
security find-generic-password \
  -s lukhas-ai \
  -a JULES_API_KEY \
  -w

# Delete a key
security delete-generic-password \
  -s lukhas-ai \
  -a JULES_API_KEY
```

## Supported API Keys

The following API keys are supported:

- **JULES_API_KEY** - Google Jules coding agent
  - Get from: https://jules.ai (Settings > API Keys)

- **OPENAI_API_KEY** - OpenAI API access
  - Get from: https://platform.openai.com/api-keys

- **ANTHROPIC_API_KEY** - Anthropic Claude API
  - Get from: https://console.anthropic.com/

- **GOOGLE_API_KEY** - Google AI (Gemini)
  - Get from: https://makersuite.google.com/app/apikey

- **PERPLEXITY_API_KEY** - Perplexity AI
  - Get from: https://www.perplexity.ai/settings/api

- **LUKHAS_API_TOKEN** - LUKHAS internal API token
- **LUKHAS_ID_SECRET** - Identity system secret key

## How It Works

### Automatic Key Lookup

When you use LUKHAS APIs, keys are automatically retrieved in this order:

1. **macOS Keychain** (most secure) ✅
2. **Environment variable** (fallback)
3. **Explicit parameter** (override)

Example - Jules API automatically uses Keychain:

```python
from bridge.llm_wrappers.jules_wrapper import JulesClient

# No API key needed - automatically retrieved from Keychain!
async with JulesClient() as jules:
    session = await jules.create_session(
        prompt="Write tests for orchestration",
        repository_url="https://github.com/LukhasAI/Lukhas"
    )
```

### Manual Key Retrieval

You can also retrieve keys programmatically:

```python
from core.security.keychain_manager import KeychainManager

# Get any API key
api_key = KeychainManager.get_key("JULES_API_KEY")

# Or use convenience functions
from core.security.keychain_manager import get_jules_api_key

jules_key = get_jules_api_key()
```

## Security Best Practices

### ✅ DO:

- Store all API keys in macOS Keychain
- Rotate keys regularly (Jules allows max 3 keys)
- Use the setup script for easy management
- Delete keys when no longer needed
- Use FileVault encryption on your Mac

### ❌ DON'T:

- Commit API keys to git (`.env` files with keys)
- Share API keys in chat or email
- Store keys in plaintext files
- Use production keys for testing
- Reuse keys across projects

## Troubleshooting

### "security: command not found"

You're not on macOS. Use environment variables instead:

```bash
export JULES_API_KEY=your-key-here
```

### "API key not found"

Check if key is stored:

```bash
python scripts/setup_api_keys.py --list
```

If not listed, add it:

```bash
python scripts/setup_api_keys.py
```

### "Permission denied" or "User interaction is not allowed"

Your keychain is locked. Unlock it:

1. Open **Keychain Access** app
2. Click **login** keychain
3. Unlock with your Mac password

### Key works in terminal but not in Python

Make sure you've imported the keychain manager:

```python
from core.security.keychain_manager import get_jules_api_key
```

## Migration from .env Files

If you have keys in `.env` files, migrate them:

1. **Run setup script**:
   ```bash
   python scripts/setup_api_keys.py
   ```

2. **Copy keys from .env** to Keychain via the wizard

3. **Remove keys from .env**:
   ```bash
   # Edit .env and remove API key values
   # Keep placeholders:
   JULES_API_KEY=  # Now in Keychain
   ```

4. **Verify**:
   ```bash
   python scripts/setup_api_keys.py --list
   ```

## Architecture

### KeychainManager Class

Located in `core/security/keychain_manager.py`:

```python
class KeychainManager:
    SERVICE_NAME = "lukhas-ai"

    @classmethod
    def set_key(key_name: str, key_value: str) -> bool

    @classmethod
    def get_key(key_name: str, fallback_to_env: bool = True) -> Optional[str]

    @classmethod
    def delete_key(key_name: str) -> bool

    @classmethod
    def list_keys() -> list[str]

    @classmethod
    def has_key(key_name: str) -> bool
```

### Keychain Service Name

All LUKHAS keys are stored under service name: **`lukhas-ai`**

This allows easy identification in Keychain Access app.

## Verification

Verify your setup:

```python
from core.security.keychain_manager import KeychainManager

# Check if Jules key is configured
if KeychainManager.has_key("JULES_API_KEY"):
    print("✅ Jules API key is configured")
else:
    print("❌ Jules API key not found")

# List all configured keys
keys = KeychainManager.list_keys()
print(f"Configured keys: {keys}")
```

## Support

- **Keychain Access App**: `/Applications/Utilities/Keychain Access.app`
- **macOS Security Command**: `man security`
- **LUKHAS Issues**: https://github.com/LukhasAI/Lukhas/issues

## License

Part of LUKHAS AI platform. Secure credential management is critical for production deployments.
