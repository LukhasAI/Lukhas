#!/bin/bash
# LUKHAS Startup Script

echo "🚀 Starting LUKHAS AI System..."

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Please create it with: python -m venv .venv"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Run health check
echo "🏥 Running health check..."
python health_monitor.py

# Start LUKHAS
echo "🧠 Starting LUKHAS..."
python main.py
