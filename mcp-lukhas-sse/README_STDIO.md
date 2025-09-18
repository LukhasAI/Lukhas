# LUKHAS AI MCP Server for ChatGPT - STDIO Implementation

This is the **official STDIO-based MCP server** that ChatGPT requires, implementing the Model Context Protocol v2025-06-18 specification.

## 🎯 ChatGPT Integration Status

✅ **STDIO Transport**: Uses standard input/output as required by ChatGPT  
✅ **MCP v2025-06-18**: Implements the latest protocol specification  
✅ **JSON-RPC 2.0**: Proper message format and error handling  
✅ **Security**: Path sandboxing and input validation  
✅ **Trinity Framework**: LUKHAS AI branding and capabilities  

## 🚀 Quick Start

### Option 1: Direct Python Execution
```bash
# Run the server directly
python lukhas_mcp_server.py

# Or the manual implementation
python lukhas_mcp_stdio_manual.py
```

### Option 2: Configuration for ChatGPT Custom GPT

When configuring a Custom GPT in ChatGPT, use these settings:

**Server Configuration:**
- **Transport**: STDIO
- **Command**: `python`
- **Arguments**: `["/absolute/path/to/lukhas_mcp_server.py"]`
- **Working Directory**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse`

**Example Configuration JSON:**
```json
{
  "mcpServers": {
    "lukhas-ai": {
      "command": "python",
      "args": [
        "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse/lukhas_mcp_server.py"
      ],
      "cwd": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse"
    }
  }
}
```

## 🛠️ Available Tools

### 1. `list_directory`
Lists files and directories in a given path.

**Input:**
```json
{
  "path": "/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data"
}
```

### 2. `read_file`
Reads the contents of a text file with line limits.

**Input:**
```json
{
  "path": "/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data/welcome.txt",
  "max_lines": 100
}
```

### 3. `search_files`
Searches for files matching a pattern in a directory.

**Input:**
```json
{
  "directory": "/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data",
  "pattern": "*.txt",
  "max_results": 20
}
```

### 4. `get_lukhas_info`
Gets information about the LUKHAS AI system and Trinity Framework.

**Input:**
```json
{}
```

## 🔒 Security Features

- **Path Sandboxing**: Only allows access to configured safe directories
- **File Size Limits**: Maximum 1MB per file read
- **Input Validation**: JSON schema validation for all tool inputs
- **Safe Defaults**: Limits on search depth and result counts
- **Error Handling**: Secure error responses without information leakage

**Default Allowed Roots:**
- `/tmp`
- `/var/tmp` 
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data`

## 🧪 Testing the Server

### Manual Test with JSON-RPC

```bash
# Test initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "ChatGPT", "version": "1.0"}, "capabilities": {}}}' | python lukhas_mcp_server.py

# Test tools list
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | python lukhas_mcp_server.py

# Test list directory
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_directory", "arguments": {"path": "/tmp"}}}' | python lukhas_mcp_server.py
```

### Expected Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false}
    },
    "serverInfo": {
      "name": "lukhas-ai-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

## ⚛️🧠🛡️ LUKHAS AI Trinity Framework

This MCP server provides ChatGPT with access to LUKHAS AI Platform capabilities:

- **⚛️ Identity**: Secure session management and file system access control
- **🧠 Consciousness**: Intelligent file system exploration and content analysis
- **🛡️ Guardian**: Security validation, path sandboxing, and safe operations

## 🔧 Troubleshooting

### Common Issues

1. **"Server doesn't implement specification"**
   - Ensure you're using the STDIO version (`lukhas_mcp_server.py`)
   - Check that Python 3.9+ is installed
   - Verify the server responds to initialization requests

2. **Permission Errors**
   - Check that the `ALLOWED_ROOTS` environment variable is set correctly
   - Ensure the server has read access to specified directories

3. **JSON-RPC Errors**
   - Verify input format matches the tool schemas
   - Check server logs (written to stderr) for detailed error messages

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export PYTHONPATH=/path/to/server
export ALLOWED_ROOTS="/tmp,/var/tmp,/your/safe/directory"
python lukhas_mcp_server.py
```

## 📝 Protocol Compliance

This implementation fully complies with:
- **MCP Specification v2025-06-18**
- **JSON-RPC 2.0** message format
- **STDIO Transport** for desktop applications
- **Standard Tool Schema** validation
- **Error Handling** with proper codes and messages

---

**Ready for ChatGPT Integration!** 🎉

The server implements the exact STDIO-based MCP specification that ChatGPT expects. You can now configure it in your Custom GPT settings and start using LUKHAS AI capabilities through ChatGPT.