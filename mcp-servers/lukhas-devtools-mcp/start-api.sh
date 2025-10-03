#!/bin/bash

# Start the LUKHAS DevTools API server for ChatGPT
echo "🚀 Starting LUKHAS DevTools API server..."

# Use port 8765 to avoid conflicts
export PORT=8765

# Start the server
node chatgpt-api.mjs