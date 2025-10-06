---
status: wip
type: documentation
---
# mcp-fs-lukhas

MCP FileSystem server exposing comprehensive read-only audit tools for the Lukhas repo:

- **stat(rel)** - Get metadata about a file or directory
- **list_dir(rel)** - List entries in a directory 
- **search(query, glob?, limit?)** - Full-text search across all allowed file types
- **get_file(rel)** - Retrieve text files with automatic credential redaction
- **read_range(rel, offset, length)** - Read chunks of large files (0-64KB per call)

Root is hard-locked to `/Users/agi_dev/LOCAL-REPOS/Lukhas`.
Optimized for **comprehensive config and code auditing** by AI assistants.

## 📁 Supported File Types (Comprehensive Config Audit)

**Source Code:** `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.rs`, `.go`, `.java`, `.cpp`, `.c`, `.h`
**Configuration:** `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.config`, `.properties`
**Build Files:** `.lock`, `.gitignore`, `.gitattributes`, `.editorconfig`, `.prettierrc`
**Documentation:** `.md`, `.txt`, `.rst`, `.adoc`
**Web/Styling:** `.css`, `.scss`, `.sass`, `.less`, `.html`, `.htm`, `.xml`, `.svg`
**Safe Environment Templates:** `.env.example`, `.env.template`, `.env.sample`

## Security Features

- **Path traversal protection** - All paths are validated and restricted to the Lukhas root
- **Denylist filtering** - Blocks access to sensitive paths (secrets/, keys/, .env files)
- **Rate limiting** - Token bucket with 10 requests per 10 seconds
- **Input validation** - Zod schemas validate all inputs and reject control characters
- **Credential redaction** - Automatically redacts AWS keys, GitHub tokens, and API keys
- **Size limits** - Files capped at 2MB, configurable via `MCP_MAX_BYTES`
- **Audit logging** - All operations logged to STDERR in structured JSON

## Environment Variables

- `MCP_FS_ROOT` - Root directory (default: `/Users/agi_dev/LOCAL-REPOS/Lukhas`)
- `MCP_MAX_BYTES` - Maximum file size in bytes (default: `2097152` = 2MB)

## RUN COMMANDS

```bash
# Install dependencies
npm install

# Run smoke tests
npm run smoke

# Run security fuzz tests  
npm run fuzz

# Start the MCP server
npm run start
```

## Plugging into ChatGPT

### Option 1: ChatGPT Desktop Client

1. **Start the server locally:**
   ```bash
   export MCP_FS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
   export MCP_MAX_BYTES="2097152"
   npm run start
   ```

2. **In ChatGPT Desktop:**
   - Go to **Settings** → **Connectors** → **Add custom**
   - Choose **MCP server**
   - Name: `Lukhas Filesystem (MCP)`
   - Connection: **Local process (stdio)**
   - Command: `npm run start`
   - Working directory: `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/mcp-fs-lukhas`
   - Environment variables:
     - `MCP_FS_ROOT`: `/Users/agi_dev/LOCAL-REPOS/Lukhas`
     - `MCP_MAX_BYTES`: `2097152`
   - Permission scope: **Read-only**
   - Visibility: **Only me** (initially)

### Option 2: MCP Configuration File

Create `mcp.json` in your ChatGPT configuration directory:

```json
{
  "clients": {
    "chatgpt": {
      "servers": {
        "mcp-fs-lukhas": {
          "command": "npm",
          "args": ["run", "start"],
          "cwd": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/mcp-fs-lukhas",
          "env": {
            "MCP_FS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
            "MCP_MAX_BYTES": "2097152"
          }
        }
      }
    }
  }
}
```

### Test Commands in ChatGPT

Once connected, try these commands in a fresh ChatGPT conversation:

1. **Search for symbols:**
   ```
   Use the search tool to find files containing "symbolic OR glyph OR EQNOX" in the LUKHAS repo
   ```

2. **Get a specific file:**
   ```
   Get the README.md file from the root and summarize what EQNOX is
   ```

3. **Explore the codebase:**
   ```
   List the contents of the core/ directory and describe the architecture
   ```

4. **Find patterns:**
   ```
   4. **Find patterns:**
   ```
   Search for "Constellation Framework" and show me the top 3 most relevant files
   ```

## Threat Model Notes

**Goal:** Read-only, bounded, non-exfiltrating connector for safe AI access to LUKHAS codebase.

**Assumptions:** 
- The AI model can request arbitrary files by relative path
- We restrict access to allowlisted root directory only
- File size and type restrictions prevent abuse

**Defenses:**
- **Path traversal guard** - Resolves and validates all paths
- **Denylist enforcement** - Blocks sensitive directories and files  
- **Credential redaction** - Strips secrets from file contents
- **Rate limiting** - Prevents request flooding
- **Size/type caps** - Limits resource consumption
- **Audit logging** - Tracks all access attempts
- **No write tools** - Read-only access only

**Residual Risks:**
- Secrets stored inside allowed text files may be visible
- Consider keeping secrets outside repo or in `.git-crypt`/external vault
- AI model could request large numbers of files (mitigated by rate limiting)

## Desktop/stdio Hardening

For enhanced security when running the MCP server, consider these macOS hardening measures:

### 1. Dedicated User Account
Create a dedicated macOS user with minimal privileges:
```bash
# Create dedicated user
sudo dscl . -create /Users/lukhas_mcp
sudo dscl . -create /Users/lukhas_mcp UserShell /bin/bash
sudo dscl . -create /Users/lukhas_mcp RealName "LUKHAS MCP Server"
sudo dscl . -create /Users/lukhas_mcp UniqueID 506
sudo dscl . -create /Users/lukhas_mcp PrimaryGroupID 20

# Give read-only access to LUKHAS repo
sudo chmod -R o+r /Users/agi_dev/LOCAL-REPOS/Lukhas
sudo chown -R lukhas_mcp:staff /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/mcp-fs-lukhas
```

### 2. Process Isolation Options

**Option A: launchd Service (Recommended)**
```bash
# Create /Library/LaunchDaemons/com.lukhas.mcp-fs.plist
sudo tee /Library/LaunchDaemons/com.lukhas.mcp-fs.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lukhas.mcp-fs</string>
    <key>UserName</key>
    <string>lukhas_mcp</string>
    <key>WorkingDirectory</key>
    <string>/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/mcp-fs-lukhas</string>
    <key>Program</key>
    <string>/usr/bin/npm</string>
    <key>ProgramArguments</key>
    <array>
        <string>npm</string>
        <string>run</string>
        <string>start</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>MCP_FS_ROOT</key>
        <string>/Users/agi_dev/LOCAL-REPOS/Lukhas</string>
        <key>MCP_MAX_BYTES</key>
        <string>2097152</string>
        <key>NODE_ENV</key>
        <string>production</string>
    </dict>
    <key>KeepAlive</key>
    <false/>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# Load and start
sudo launchctl load /Library/LaunchDaemons/com.lukhas.mcp-fs.plist
```

**Option B: Docker with Colima (Extra Isolation)**
```bash
# Install colima if not present
brew install colima docker

# Start colima VM
colima start

# Run MCP server in container
docker run -it --rm \
  -v "/Users/agi_dev/LOCAL-REPOS/Lukhas:/workspace:ro" \
  -e MCP_FS_ROOT=/workspace \
  -e MCP_MAX_BYTES=2097152 \
  -w /workspace/mcp-servers/mcp-fs-lukhas \
  node:20-alpine \
  npm run start
```

### 3. Secret Management
- **Keep secrets outside the repo** - Store API keys, tokens in external vaults
- **Use git-crypt for encrypted secrets** - `git-crypt init && git-crypt add-gpg-user <key-id>`
- **Environment-based secrets** - Pass sensitive data via environment variables only
- **Audit secret redaction** - Monitor logs to ensure credential patterns are caught

### 4. Monitoring & Logging
All tool calls are logged to STDERR in structured JSON format:
```json
{
  "timestamp": "2025-01-09T15:30:00Z",
  "tool": "get_file",
  "argsHash": "{\"rel\":\"package.json\"}",
  "duration": 15,
  "resultInfo": {"size": 1024},
  "denied": false,
  "redacted": true
}
```

Monitor for:
- High request rates (potential abuse)
- Access to sensitive paths (blocked attempts)
- Redaction events (potential credential leaks)
- Unusual file access patterns

## Architecture

```
mcp-fs-lukhas/
├── src/
│   ├── server.ts      # MCP server implementation with request handlers
│   └── fsTools.ts     # Core filesystem tools with security features
├── scripts/
│   ├── smoke.ts       # Basic functionality tests
│   └── fuzz.ts        # Security and edge case tests
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
└── README.md          # This documentation
```
