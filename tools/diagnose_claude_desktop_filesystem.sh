#!/bin/bash
# Claude Desktop Filesystem Diagnostic Tool
# Helps diagnose and report write_file errors

echo "=== Claude Desktop Filesystem Diagnostic ==="
echo "Generated: $(date)"
echo ""

echo "=== 1. Claude Desktop Version ==="
/Applications/Claude.app/Contents/MacOS/Claude --version 2>/dev/null || echo "Unable to detect version"
echo ""

echo "=== 2. MCP Server Configuration ==="
if [ -f ~/Library/Application\ Support/Claude/claude_desktop_config.json ]; then
    echo "✓ Config file exists"
    jq '.mcpServers | keys[]' ~/Library/Application\ Support/Claude/claude_desktop_config.json 2>/dev/null
else
    echo "✗ Config file not found"
fi
echo ""

echo "=== 3. Recent Filesystem MCP Errors ==="
if [ -f ~/Library/Logs/Claude/mcp-server-Filesystem.log ]; then
    echo "Last 5 errors (if any):"
    grep -i "error\|Error\|ERROR" ~/Library/Logs/Claude/mcp-server-Filesystem.log | tail -5 || echo "No errors found in Filesystem MCP log"
else
    echo "✗ Filesystem log not found"
fi
echo ""

echo "=== 4. Recent write_file Validation Errors ==="
grep -r "write_file.*invalid\|write_file.*undefined" ~/Library/Logs/Claude/*.log 2>/dev/null | tail -5 || echo "No write_file validation errors found in logs"
echo ""

echo "=== 5. Filesystem MCP Server Status ==="
ps aux | grep -i "filesystem.*mcp\|secure-filesystem" | grep -v grep || echo "Filesystem MCP server not currently running"
echo ""

echo "=== 6. Disk Space ==="
df -h / | tail -1
echo ""

echo "=== 7. File Permissions ==="
ls -la ~/Library/Application\ Support/Claude/ | head -5
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "Common Solutions:"
echo "1. Restart Claude Desktop: Cmd+Q then reopen"
echo "2. Clear conversation and start fresh"
echo "3. Use 'edit_file' instead of 'write_file' for existing files"
echo "4. Break large file operations into smaller chunks"
echo ""
echo "If error persists, report to: https://github.com/anthropics/anthropic-sdk-typescript/issues"
