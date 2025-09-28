#!/bin/bash

# Google Cloud Platform Setup Script for RSI Downloader
# This script sets up the GCP project and prepares for deployment

set -e  # Exit on any error

echo "🚀 Setting up Google Cloud Platform for RSI Downloader"
echo "====================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed."
    echo ""
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "For macOS:"
    echo "  brew install google-cloud-sdk"
    echo ""
    echo "For Linux:"
    echo "  curl https://sdk.cloud.google.com | bash"
    echo ""
    exit 1
fi

echo "✅ Google Cloud CLI is installed"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud."
    echo ""
    echo "Please run: gcloud auth login"
    echo "This will open a browser window for authentication."
    exit 1
fi

echo "✅ Authenticated with Google Cloud"

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No project is currently set."
    echo ""
    echo "Please set a project:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "Or create a new project:"
    echo "  gcloud projects create your-rsi-project-id"
    echo "  gcloud config set project your-rsi-project-id"
    exit 1
fi

echo "✅ Current project: $CURRENT_PROJECT"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable compute.googleapis.com

echo "✅ APIs enabled"

# Initialize App Engine (if not already done)
echo "🔧 Initializing App Engine..."
if ! gcloud app describe &> /dev/null; then
    echo "Creating App Engine application..."
    gcloud app create --region=us-central
    echo "✅ App Engine application created"
else
    echo "✅ App Engine application already exists"
fi

# Check billing
echo "🔧 Checking billing..."
if ! gcloud billing projects describe $CURRENT_PROJECT &> /dev/null; then
    echo "⚠️  Billing is not enabled for this project."
    echo ""
    echo "Please enable billing:"
    echo "1. Go to: https://console.cloud.google.com/billing"
    echo "2. Select your project: $CURRENT_PROJECT"
    echo "3. Enable billing"
    echo ""
    echo "Or run: gcloud billing accounts list"
    echo "Then: gcloud billing projects link $CURRENT_PROJECT --billing-account=BILLING_ACCOUNT_ID"
    exit 1
fi

echo "✅ Billing is enabled"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "env_template.txt" ]; then
        cp env_template.txt .env
        echo "✅ .env file created from template"
        echo "⚠️  Please edit .env file with your actual API keys"
    else
        echo "❌ env_template.txt not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Deploy to App Engine:"
echo "   ./deploy_gcp.sh"
echo ""
echo "3. Or deploy manually:"
echo "   gcloud app deploy app.yaml"
echo ""
echo "Your app will be available at:"
echo "https://$CURRENT_PROJECT.appspot.com"
