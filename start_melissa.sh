#!/bin/bash

# Melissa Voice Assistant - Startup Script
# This script starts the LiveKit server and Melissa agent
# Use LiveKit Agents Playground to interact: https://agents-playground.livekit.io

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LIVEKIT_CONTAINER_NAME="melissa-livekit"

echo "🎙️ Starting Melissa Voice Assistant..."
echo ""

# Check if .env exists
echo "📋 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found! Copy env.example to .env and fill in your API keys:"
    echo "   cp env.example .env"
    exit 1
fi
echo "   ✓ .env found"

# Check if Docker is available
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found! Please install Docker first."
    exit 1
fi
echo "   ✓ Docker available"

# Activate venv
echo "🐍 Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "   ✓ venv activated"
else
    echo "⚠️  No venv found! Create it first:"
    echo "   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if LiveKit server is already running
echo "🔍 Checking LiveKit server..."
if curl -s --connect-timeout 2 --max-time 3 http://localhost:7880 > /dev/null 2>&1; then
    echo "   ✓ LiveKit server already running"
else
    echo "🚀 Starting LiveKit server (Docker)..."
    
    # Remove old container if exists
    docker rm -f $LIVEKIT_CONTAINER_NAME 2>/dev/null || true
    
    # Start LiveKit in Docker
    docker run -d \
        --name $LIVEKIT_CONTAINER_NAME \
        -p 7880:7880 \
        -p 7881:7881 \
        -p 7882:7882/udp \
        -e LIVEKIT_KEYS="devkey: secret" \
        livekit/livekit-server \
        --dev
    
    # Wait for LiveKit to be ready
    echo "   Waiting for LiveKit to start..."
    for i in {1..30}; do
        if curl -s --connect-timeout 2 --max-time 3 http://localhost:7880 > /dev/null 2>&1; then
            echo "   ✓ LiveKit server started"
            break
        fi
        echo -n "."
        sleep 1
        if [ $i -eq 30 ]; then
            echo ""
            echo "❌ LiveKit failed to start. Check Docker logs:"
            echo "   docker logs $LIVEKIT_CONTAINER_NAME"
            exit 1
        fi
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎧 Melissa Agent is starting!"
echo ""
echo "  To talk to Melissa, use LiveKit Agents Playground:"
echo "  https://agents-playground.livekit.io"
echo ""
echo "  LiveKit URL: ws://localhost:7880"
echo "  API Key: devkey"
echo "  API Secret: secret"
echo ""
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo "👋 Shutting down Melissa..."
    echo "🐳 Stopping LiveKit container..."
    docker stop $LIVEKIT_CONTAINER_NAME 2>/dev/null || true
    docker rm $LIVEKIT_CONTAINER_NAME 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start agent (foreground)
echo "🤖 Starting Melissa Agent..."
python melissa_agent.py dev

# Cleanup on exit
docker stop $LIVEKIT_CONTAINER_NAME 2>/dev/null || true
docker rm $LIVEKIT_CONTAINER_NAME 2>/dev/null || true
