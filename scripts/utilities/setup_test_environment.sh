#!/bin/bash

# LUKHAS Live Integration Test Setup
echo "🚀 Setting up LUKHAS test environment..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "   Tests will run in mock mode"
    echo "   To test with real API: export OPENAI_API_KEY='your-key'"
else
    echo "✅ OpenAI API key configured"
fi

# Create necessary directories
mkdir -p .lukhas_audit
mkdir -p .lukhas_feedback

# Start API server in background
echo ""
echo "Starting API server..."
echo "Run in a separate terminal:"
echo "  uvicorn lukhas.api.app:app --reload --port 8000"
echo ""

# Wait for user to start server
echo "Press Enter when the API server is running..."
read

# Verify API is up
if curl -s http://127.0.0.1:8000/tools/registry > /dev/null; then
    echo "✅ API server is running"
else
    echo "❌ API server not reachable"
    echo "Please start it with: uvicorn lukhas.api.app:app --reload"
    exit 1
fi

echo ""
echo "✅ Environment ready!"
echo ""
echo "Run the integration tests with:"
echo "  python3 live_integration_test.py"
echo ""
echo "Monitor in browser:"
echo "  http://127.0.0.1:8000/docs - API documentation"
echo "  http://127.0.0.1:8000/tools/registry - Tool registry"
echo "  http://127.0.0.1:8000/tools/incidents - Security incidents"
echo ""