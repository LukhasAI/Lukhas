# mcp-fs-lukhas

MCP FileSystem server exposing read-only, safe tools for the Lukhas repo:

- **stat(rel)** - Get metadata about a file or directory
- **list_dir(rel)** - List entries in a directory 
- **search(query, glob?, limit?)** - Full-text search across allowed text files
- **get_file(rel)** - Retrieve a small text file

Root is hard-locked to `/Users/agi_dev/LOCAL-REPOS/Lukhas`.
Binary files and large files are blocked. Path traversal is prevented.

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
   Search for "Trinity Framework" and show me the top 3 most relevant files
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
