#!/bin/bash

# LUKHAS Website with PR0T3US Integration Startup Script
# This script starts both the Next.js website and PR0T3US visualizer

echo "========================================="
echo "  LUKHAS AI - Starting Services"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Port $1 is in use. Killing existing process...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Check and install dependencies for PR0T3US
echo -e "${BLUE}Checking PR0T3US dependencies...${NC}"
cd ../voice_reactive_morphing
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing PR0T3US dependencies...${NC}"
    npm install
fi

# Check and install dependencies for LUKHAS Website
echo -e "${BLUE}Checking LUKHAS Website dependencies...${NC}"
cd ../lukhas_website
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing website dependencies...${NC}"
    npm install
fi

# Kill existing processes on required ports
kill_port 3000  # Next.js default port
kill_port 8080  # PR0T3US server port

# Start PR0T3US server in background
echo -e "${GREEN}Starting PR0T3US Voice-Reactive Morphing System on port 8080...${NC}"
cd ../voice_reactive_morphing
npm start &
PROTEUS_PID=$!
echo -e "${GREEN}PR0T3US PID: $PROTEUS_PID${NC}"

# Wait for PR0T3US to start
sleep 2

# Start LUKHAS Website
echo -e "${GREEN}Starting LUKHAS Website on port 3000...${NC}"
cd ../lukhas_website
npm run dev &
WEBSITE_PID=$!
echo -e "${GREEN}Website PID: $WEBSITE_PID${NC}"

# Wait for services to start
sleep 3

# Print status
echo ""
echo "========================================="
echo -e "${GREEN}  Services Started Successfully!${NC}"
echo "========================================="
echo ""
echo -e "${BLUE}LUKHAS Website:${NC} http://localhost:3000"
echo -e "${BLUE}PR0T3US Experience:${NC} http://localhost:3000/experience"
echo -e "${BLUE}PR0T3US Direct:${NC} http://localhost:8080"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    kill $PROTEUS_PID 2>/dev/null
    kill $WEBSITE_PID 2>/dev/null
    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Wait for processes
wait $PROTEUS_PID $WEBSITE_PID
