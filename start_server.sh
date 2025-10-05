#!/bin/bash
# Start FusionMCP Server

echo "🚀 Starting FusionMCP Server..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json not found! Copying from example..."
    cp examples/example_config.json config.json
    echo "📝 Please edit config.json with your API keys"
    exit 1
fi

# Start server
python -m mcp_server.server

echo "✅ Server stopped"
