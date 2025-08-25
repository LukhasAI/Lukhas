#!/bin/bash
# VS Code Crash Monitor Script
# Run: chmod +x monitor_vscode.sh && ./monitor_vscode.sh

echo "🔍 VS Code Stability Monitor"
echo "Starting monitoring at: $(date)"

while true; do
    # Check if VS Code is running
    if pgrep -f "Visual Studio Code" > /dev/null; then
        echo "✅ VS Code running - $(date)"
    else
        echo "❌ VS Code crashed or stopped - $(date)"
        echo "Attempting restart..."
        code --disable-gpu --disable-extensions &
    fi
    
    # Check crash logs
    if find ~/Library/Logs/DiagnosticReports -name "*Electron*" -newer /tmp/vscode_monitor_start -type f 2>/dev/null | grep -q .; then
        echo "🚨 New crash detected at $(date)"
        echo "Latest crash logs:"
        find ~/Library/Logs/DiagnosticReports -name "*Electron*" -newer /tmp/vscode_monitor_start -type f -exec echo {} \;
    fi
    
    sleep 30
done
