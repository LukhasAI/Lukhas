#!/bin/bash

# LUKHAS AGI Dashboard Launcher
# Enterprise-grade dashboard for AGI monitoring

set -e

echo "🚀 LUKHAS AGI Dashboard Launcher"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Navigate to dashboard backend
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${GREEN}✅ Activating virtual environment${NC}"
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    touch .deps_installed
fi

# Start the dashboard
echo -e "${GREEN}🎯 Starting LUKHAS AGI Dashboard${NC}"
echo ""
echo "Dashboard will be available at:"
echo "  📊 API: http://localhost:8000"
echo "  📚 Docs: http://localhost:8000/api/docs"
echo "  🔄 WebSocket: ws://localhost:8000/ws/realtime"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Run the FastAPI application
python main.py
