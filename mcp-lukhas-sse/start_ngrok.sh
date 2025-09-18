#!/bin/bash
# ngrok startup script

echo "🚀 Starting ngrok tunnel for MCP server..."

# Check if MCP server is running
if ! curl -s http://localhost:8080/health > /dev/null; then
    echo "❌ MCP server not running on port 8080"
    echo "💡 Start it with: cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-lukhas-sse && ALLOWED_ROOTS='/Users/agi_dev/LOCAL-REPOS/Lukhas' ALLOW_NO_AUTH=true python3 chatgpt_server.py &"
    exit 1
fi

echo "✅ MCP server is running"

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 8080 --log=stdout --log-level=info &

NGROK_PID=$!
echo "🔗 ngrok PID: $NGROK_PID"

# Wait for ngrok to start
sleep 5

# Get the public URL
echo "📡 Fetching public URL..."
PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    url = data['tunnels'][0]['public_url']
    print(url)
except:
    print('Error getting URL')
" 2>/dev/null)

if [ -n "$PUBLIC_URL" ] && [ "$PUBLIC_URL" != "Error getting URL" ]; then
    echo "🎉 SUCCESS! Your MCP server is now public:"
    echo ""
    echo "   Health Check: $PUBLIC_URL/health"
    echo "   MCP Endpoint: $PUBLIC_URL/sse"
    echo ""
    echo "🤖 For ChatGPT Custom GPT, use:"
    echo "   URL: $PUBLIC_URL/sse"
    echo "   Auth: None (no-auth mode enabled)"
    echo ""
    echo "🧪 Test it:"
    echo "   curl $PUBLIC_URL/health"
    echo ""
    echo "🛑 To stop: kill $NGROK_PID"
    
    # Save URL to file
    echo "$PUBLIC_URL" > ngrok_url.txt
    echo "💾 URL saved to: ngrok_url.txt"
else
    echo "❌ Failed to get ngrok URL"
    echo "🔍 Check ngrok status at: http://localhost:4040"
fi

# Keep script running
wait $NGROK_PID