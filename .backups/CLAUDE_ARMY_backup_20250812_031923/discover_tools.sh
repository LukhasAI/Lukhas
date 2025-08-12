#!/bin/bash

# 🔧 CLAUDE ARMY TOOLS DISCOVERY
# Discovers available tools in ~/CLAUDE_ARMY/TOOLS/

echo "🔧 CLAUDE ARMY TOOLS DISCOVERY"
echo "==============================="
echo ""

TOOLS_DIR="$HOME/CLAUDE_ARMY/TOOLS"

if [ -d "$TOOLS_DIR" ]; then
    echo "📦 Available Tools in $TOOLS_DIR:"
    echo ""
    
    # List all .sh files
    for tool in "$TOOLS_DIR"/*.sh; do
        if [ -f "$tool" ]; then
            tool_name=$(basename "$tool")
            echo "  🔨 $tool_name"
            
            # Try to extract description from first comment
            description=$(head -5 "$tool" | grep "^#" | grep -v "^#!/" | head -1 | sed 's/^# *//')
            if [ ! -z "$description" ]; then
                echo "     → $description"
            fi
        fi
    done
    
    echo ""
    echo "📋 Tool Categories Found:"
    
    # Group by prefix if tools follow naming pattern
    for prefix in fix test deploy analyze generate validate migrate; do
        count=$(ls -1 "$TOOLS_DIR"/${prefix}*.sh 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            echo "  • ${prefix}: $count tools"
        fi
    done
    
else
    echo "❌ Tools directory not found: $TOOLS_DIR"
    echo ""
    echo "Creating symbolic link to tools..."
    # Try to find tools in common locations
    for possible_path in \
        "$HOME/CLAUDE_ARMY/TOOLS" \
        "$HOME/claude_army/tools" \
        "$HOME/tools/claude_army" \
        "$HOME/Development/CLAUDE_ARMY/TOOLS"; do
        if [ -d "$possible_path" ]; then
            echo "Found tools at: $possible_path"
            ln -s "$possible_path" ./CLAUDE_ARMY/external_tools
            echo "Created link: ./CLAUDE_ARMY/external_tools -> $possible_path"
            break
        fi
    done
fi

echo ""
echo "🎯 To use a tool:"
echo "   bash $TOOLS_DIR/<tool_name>.sh"
echo ""
echo "💡 Or copy tools to local directory:"
echo "   cp $TOOLS_DIR/<tool_name>.sh ./CLAUDE_ARMY/"