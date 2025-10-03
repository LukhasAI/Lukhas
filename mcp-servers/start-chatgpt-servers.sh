#!/bin/bash

# 🚀 LUKHAS Enhanced MCP Servers - ChatGPT Integration Startup
# This script installs dependencies and starts all enhanced MCP servers for ChatGPT integration

set -e

LUKHAS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
export LUKHAS_ROOT

echo "🧠 LUKHAS Enhanced MCP Servers - ChatGPT Integration v2.0"
echo "=================================================="
echo "Starting enhanced MCP servers with T4/0.01% quality standards"
echo ""

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to install dependencies for a server
install_dependencies() {
    local server_dir=$1
    local server_name=$2
    
    echo "📦 Installing dependencies for $server_name..."
    cd "$LUKHAS_ROOT/mcp-servers/$server_dir"
    
    if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        npm install
    else
        echo "✅ Dependencies already installed for $server_name"
    fi
}

# Function to start a server in background
start_server() {
    local server_dir=$1
    local server_name=$2
    local port=$3
    local token=$4
    
    echo "🚀 Starting $server_name on port $port..."
    cd "$LUKHAS_ROOT/mcp-servers/$server_dir"
    
    # Export environment variables
    export MCP_HTTP_TOKEN="$token"
    export PORT="$port"
    export NODE_ENV="production"
    
    # Start server in background
    npm run start:http > "/tmp/lukhas-$server_name.log" 2>&1 &
    local pid=$!
    
    # Wait a moment for startup
    sleep 2
    
    # Check if server is running
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $server_name started successfully (PID: $pid)"
        echo "$pid" > "/tmp/lukhas-$server_name.pid"
    else
        echo "❌ Failed to start $server_name"
        return 1
    fi
}

# Check for required environment
echo "🔍 Checking environment..."

if [ ! -d "$LUKHAS_ROOT" ]; then
    echo "❌ LUKHAS_ROOT directory not found: $LUKHAS_ROOT"
    exit 1
fi

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) found"

# Generate secure token if not provided
if [ -z "$MCP_HTTP_TOKEN" ]; then
    export MCP_HTTP_TOKEN=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | base64 | tr -d '\n' | head -c 32)
    echo "🔐 Generated secure token: ${MCP_HTTP_TOKEN:0:8}..."
else
    echo "🔐 Using provided token: ${MCP_HTTP_TOKEN:0:8}..."
fi

# Check ports
echo "🔍 Checking port availability..."
PORTS=(8764 8765 8766 8767)
for port in "${PORTS[@]}"; do
    if ! check_port $port; then
        echo "❌ Port $port is not available. Please stop the service using it."
        exit 1
    fi
done
echo "✅ All ports available"

# Install dependencies for all servers
echo ""
echo "📦 Installing dependencies for all MCP servers..."
install_dependencies "lukhas-devtools-mcp" "DevTools MCP (Enhanced)"
install_dependencies "mcp-fs-lukhas" "File System MCP"
install_dependencies "lukhas-constellation-mcp" "Constellation MCP"

# Start all servers
echo ""
echo "🚀 Starting all enhanced MCP servers..."

start_server "lukhas-devtools-mcp" "devtools" 8764 "$MCP_HTTP_TOKEN"
start_server "mcp-fs-lukhas" "filesystem" 8765 "$MCP_HTTP_TOKEN"
start_server "lukhas-constellation-mcp" "constellation" 8766 "$MCP_HTTP_TOKEN"

# Health check
echo ""
echo "🏥 Performing health checks..."
sleep 3

SERVERS=(
    "devtools:8764:DevTools MCP (Enhanced v0.2.0)"
    "filesystem:8765:File System MCP"
    "constellation:8766:Constellation Framework MCP"
)

ALL_HEALTHY=true
for server_info in "${SERVERS[@]}"; do
    IFS=':' read -r name port description <<< "$server_info"
    
    if curl -s "http://localhost:$port/healthz" >/dev/null 2>&1; then
        echo "✅ $description - http://localhost:$port"
    else
        echo "❌ $description - Failed health check"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = true ]; then
    echo ""
    echo "🎉 All LUKHAS MCP servers are running successfully!"
    echo ""
    echo "📊 Server Status:"
    echo "   - DevTools MCP (Enhanced): http://localhost:8764"
    echo "   - File System MCP:         http://localhost:8765"
    echo "   - Constellation MCP:       http://localhost:8766"
    echo ""
    echo "🔗 API Endpoints for each server:"
    echo "   - Health check: GET /healthz"
    echo "   - MCP probe:    GET /mcp"
    echo "   - JSON-RPC:     POST /mcp"
    echo "   - OpenAPI:      GET /openapi.json"
    echo ""
    echo "🔐 Authentication:"
    echo "   - Token: ${MCP_HTTP_TOKEN:0:8}..."
    echo "   - Use as Bearer token or ?api_key= parameter"
    echo ""
    echo "📝 Test with curl:"
    echo "   curl -H 'Authorization: Bearer $MCP_HTTP_TOKEN' \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"jsonrpc\":\"2.0\",\"method\":\"test_infrastructure_status\",\"params\":{},\"id\":1}' \\"
    echo "        http://localhost:8764/mcp"
    echo ""
    echo "🤖 ChatGPT Integration:"
    echo "   - Configure Actions with OpenAPI specs from /openapi.json endpoints"
    echo "   - Use Bearer token authentication"
    echo "   - See CHATGPT_INTEGRATION_SETUP.md for complete setup"
    echo ""
    echo "🛑 To stop all servers: ./stop-mcp-servers.sh"
    
    # Create stop script
    cat > "$LUKHAS_ROOT/mcp-servers/stop-mcp-servers.sh" << 'EOF'
#!/bin/bash
echo "🛑 Stopping LUKHAS MCP servers..."

for pid_file in /tmp/lukhas-*.pid; do
    if [ -f "$pid_file" ]; then
        server_name=$(basename "$pid_file" .pid)
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "✅ Stopped $server_name (PID: $pid)"
        else
            echo "⚠️  $server_name was not running"
        fi
        rm -f "$pid_file"
    fi
done

echo "🧹 Cleaning up log files..."
rm -f /tmp/lukhas-*.log

echo "✅ All LUKHAS MCP servers stopped"
EOF
    chmod +x "$LUKHAS_ROOT/mcp-servers/stop-mcp-servers.sh"
    
else
    echo ""
    echo "❌ Some servers failed to start. Check logs:"
    echo "   - DevTools: /tmp/lukhas-devtools.log"
    echo "   - File System: /tmp/lukhas-filesystem.log"
    echo "   - Constellation: /tmp/lukhas-constellation.log"
    exit 1
fi