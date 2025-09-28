#!/bin/bash

# Startup script for Koyeb deployment
set -e

echo "🚀 Starting RSI Downloader on Koyeb"

# Set default port if not provided
export PORT=${PORT:-8080}

# Set Streamlit environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo "📋 Using port: $PORT"
echo "🔧 Environment configured"

# Start the application
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0