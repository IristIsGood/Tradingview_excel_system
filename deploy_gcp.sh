#!/bin/bash

# Google Cloud Platform Deployment Script for RSI Downloader
# This script deploys the Streamlit app to Google App Engine

set -e  # Exit on any error

echo "🚀 Deploying RSI Downloader to Google Cloud Platform"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project (replace with your project ID)
PROJECT_ID="your-project-id"
echo "📋 Project ID: $PROJECT_ID"

# Set the project
echo "🔧 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to App Engine
echo "🚀 Deploying to App Engine..."
gcloud app deploy app.yaml --quiet

# Get the service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(gcloud app browse --no-launch-browser)
echo "✅ Deployment successful!"
echo "🔗 Your app is available at: $SERVICE_URL"

echo ""
echo "📊 Deployment Summary:"
echo "- Service: rsi-downloader"
echo "- URL: $SERVICE_URL"
echo "- Runtime: Custom (Docker)"
echo "- Scaling: Automatic (1-10 instances)"
echo ""
echo "💡 To view logs: gcloud app logs tail -s rsi-downloader"
echo "💡 To stop the service: gcloud app versions stop VERSION_ID"
