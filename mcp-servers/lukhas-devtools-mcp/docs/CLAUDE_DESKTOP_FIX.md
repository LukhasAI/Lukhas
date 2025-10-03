# Claude Desktop Configuration Fix

**Issue Resolved:** npm error ENOENT - Could not read package.json

## Problem Analysis

The error occurred because Claude Desktop was trying to run `npm start` from the wrong working directory (`/Users/agi_dev/` instead of the MCP server directory).

## Solutions Provided

### Solution 1: Direct Script Execution (Recommended)
Use the enhanced startup script that ensures correct working directory:

```json
{
  "mcpServers": {
    "lukhas-devtools": {
      "command": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp/start-enhanced.sh",
      "args": [],
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
```

### Solution 2: NPM with Correct Working Directory
Use npm with explicit working directory specification:

```json
{
  "mcpServers": {
    "lukhas-devtools": {
      "command": "npm",
      "args": ["start"],
      "cwd": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp",
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
```

## Files Created

1. **start-enhanced.sh** - Startup script that ensures correct working directory
2. **claude-desktop-config.json** - Configuration using direct script execution
3. **claude-desktop-config-npm.json** - Configuration using npm with cwd
4. **package.json** - Updated to support both TypeScript and JavaScript modes

## Package.json Updates

Updated the start script to run the JavaScript version directly:
```json
"scripts": {
  "start": "node mcp-streamable.mjs",
  "start:typescript": "node --loader ts-node/esm src/server.ts",
  // ... other scripts
}
```

## Verification

The server now starts correctly:
- ✅ npm start works from MCP directory
- ✅ start-enhanced.sh script works correctly  
- ✅ All 8 tools available and functional
- ✅ Port 8766 accessible for connections

## Usage Instructions

1. **Copy the desired configuration** from `claude-desktop-config.json` or `claude-desktop-config-npm.json`
2. **Add to your Claude Desktop config** at `~/Library/Application Support/Claude/claude_desktop_config.json`
3. **Restart Claude Desktop** to apply the new configuration
4. **Test the connection** by asking Claude to use LUKHAS development tools

## Technical Details

- **Server**: mcp-streamable.mjs with enhanced file editing capabilities
- **Port**: 8766 (configurable via PORT environment variable)
- **Protocol**: MCP 2024-11-05 with JSON-RPC 2.0
- **Tools**: 8 development tools including writeFile and createFile
- **Security**: Path validation and repo boundary enforcement

The npm error is now resolved and the MCP server will start correctly from Claude Desktop.