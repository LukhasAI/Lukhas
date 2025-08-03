#!/bin/bash

# LUKHAS Demo Launcher
# Quick start script for investor demonstrations

echo "╔═══════════════════════════════════════════════════════╗"
echo "║           LUKHAS Demo Environment v1.0                ║"
echo "║                                                       ║"
echo "║  Preparing showcase for OpenAI/Anthropic...           ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Menu options
echo "Select demo mode:"
echo ""
echo "1) 🚀 Full Demo Suite (All APIs + Dashboard)"
echo "2) ⚡ Quick Demo (Priority APIs only)"
echo "3) 🎯 Single API Test"
echo "4) 📊 Open Pitch Deck"
echo "5) 🛑 Stop All Demos"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🚀 Starting full demo suite..."
        docker-compose up -d
        echo ""
        echo "✅ All demos started!"
        echo ""
        echo "📍 Access points:"
        echo "   Dashboard: http://localhost:8000"
        echo "   Pitch Deck: http://localhost:8000/LUKHAS_PITCH_DECK.html"
        echo ""
        echo "🔗 API Endpoints:"
        echo "   Dream Recall: http://localhost:8001/docs"
        echo "   Memory Fold: http://localhost:8003/docs"
        echo "   Emotional Coherence: http://localhost:8002/docs"
        echo "   Colony Consensus: http://localhost:8004/docs"
        echo ""
        echo "💡 Tip: Open the pitch deck for the best presentation experience!"
        ;;
        
    2)
        echo "⚡ Starting priority demos only..."
        docker-compose up -d dream-recall memory-fold emotional-coherence dashboard
        echo ""
        echo "✅ Priority demos started!"
        echo ""
        echo "📍 Access points:"
        echo "   Dashboard: http://localhost:8000"
        echo "   Dream Recall: http://localhost:8001/docs"
        echo "   Memory Fold: http://localhost:8003/docs"
        echo "   Emotional Coherence: http://localhost:8002/docs"
        ;;
        
    3)
        echo "🎯 Select API to test:"
        echo "1) Dream Recall (Multiverse exploration)"
        echo "2) Memory Fold (DNA-helix memory)"
        echo "3) Emotional Coherence (Bio-symbolic >100%)"
        echo "4) Colony Consensus (Swarm intelligence)"
        read -p "Enter choice (1-4): " api_choice
        
        case $api_choice in
            1) docker-compose up -d dream-recall ;;
            2) docker-compose up -d memory-fold ;;
            3) docker-compose up -d emotional-coherence ;;
            4) docker-compose up -d colony-consensus ;;
        esac
        
        echo "✅ API started! Check http://localhost:800$api_choice/docs"
        ;;
        
    4)
        echo "📊 Opening pitch deck..."
        open docs/presentation/LUKHAS_PITCH_DECK.html || \
        xdg-open docs/presentation/LUKHAS_PITCH_DECK.html || \
        echo "Please open: docs/presentation/LUKHAS_PITCH_DECK.html"
        ;;
        
    5)
        echo "🛑 Stopping all demos..."
        docker-compose down
        echo "✅ All demos stopped."
        ;;
        
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "Press Ctrl+C to exit"