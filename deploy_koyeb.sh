#!/bin/bash

# Koyeb Deployment Script for RSI Downloader
# This script helps deploy the Streamlit app to Koyeb

set -e  # Exit on any error

echo "🚀 Deploying RSI Downloader to Koyeb"
echo "====================================="

# Check if koyeb CLI is installed
if ! command -v koyeb &> /dev/null; then
    echo "❌ Koyeb CLI is not installed."
    echo ""
    echo "Please install it:"
    echo "curl https://get.koyeb.com/cli | sh"
    echo ""
    echo "Then login:"
    echo "koyeb auth login"
    exit 1
fi

echo "✅ Koyeb CLI is installed"

# Check if user is authenticated
if ! koyeb auth whoami &> /dev/null; then
    echo "❌ Not authenticated with Koyeb."
    echo ""
    echo "Please run: koyeb auth login"
    exit 1
fi

echo "✅ Authenticated with Koyeb"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found."
    echo ""
    echo "Please create .env file with your API keys:"
    echo "cp env_template.txt .env"
    echo "nano .env"
    echo ""
    echo "Required environment variables:"
    echo "- MEXC_API_KEY"
    echo "- MEXC_API_SECRET"
    echo ""
    read -p "Continue without .env file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy to Koyeb
echo "🚀 Deploying to Koyeb..."

# Check if service already exists
if koyeb service get rsi-downloader &> /dev/null; then
    echo "📝 Service 'rsi-downloader' already exists. Updating..."
    koyeb service update rsi-downloader \
        --git github.com/MeowIrist/Tradingview_excel \
        --git-branch main \
        --env STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        --env STREAMLIT_SERVER_HEADLESS=true \
        --env STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
else
    echo "🆕 Creating new service 'rsi-downloader'..."
    koyeb service create \
        --name rsi-downloader \
        --git github.com/MeowIrist/Tradingview_excel \
        --git-branch main \
        --env STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        --env STREAMLIT_SERVER_HEADLESS=true \
        --env STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
fi

echo "✅ Deployment initiated!"

# Get service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(koyeb service get rsi-downloader --output json | jq -r '.service.domains[0].name' 2>/dev/null || echo "Check Koyeb dashboard")

echo ""
echo "🎉 Deployment successful!"
echo "🔗 Your app is available at: https://$SERVICE_URL"
echo ""
echo "📊 Next steps:"
echo "1. Set your API keys in Koyeb dashboard:"
echo "   - Go to: https://app.koyeb.com/"
echo "   - Find your service: rsi-downloader"
echo "   - Go to Environment tab"
echo "   - Add your API keys"
echo ""
echo "2. View logs:"
echo "   koyeb service logs rsi-downloader"
echo ""
echo "3. Check status:"
echo "   koyeb service get rsi-downloader"
