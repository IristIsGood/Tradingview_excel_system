# 🚀 RSI Downloader - Google Cloud Platform Deployment Guide

This guide will help you deploy the RSI Downloader Streamlit app to Google App Engine.

## 📋 Prerequisites

### 1. Google Cloud Account
- Sign up at [Google Cloud Console](https://console.cloud.google.com/)
- Enable billing (required for App Engine)

### 2. Google Cloud CLI
Install the Google Cloud CLI:

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

### 3. API Keys
You'll need API keys for the exchanges you want to use:
- **MEXC** (required): Get from [MEXC API](https://www.mexc.com/user/api)
- **Binance** (optional): Get from [Binance API](https://www.binance.com/en/my/settings/api-management)
- **Gate.io** (optional): Get from [Gate.io API](https://www.gate.io/user/api)
- **Bybit** (optional): Get from [Bybit API](https://www.bybit.com/app/user/api-management)

## 🚀 Quick Start

### Step 1: Setup Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login

# Create a new project (replace with your project name)
gcloud projects create your-rsi-project-id

# Set the project
gcloud config set project your-rsi-project-id

# Run the setup script
./setup_gcp.sh
```

### Step 2: Configure API Keys

```bash
# Edit the .env file with your API keys
nano .env
```

Add your API keys:
```env
# For MEXC (required for klines)
MEXC_API_KEY=your_actual_mexc_key
MEXC_API_SECRET=your_actual_mexc_secret

# For Binance (optional)
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret

# For Gate.io (optional)
GATE_API_KEY=your_gate_key
GATE_API_SECRET=your_gate_secret

# For Bybit (optional)
BYBIT_API_KEY=your_bybit_key
BYBIT_API_SECRET=your_bybit_secret
```

### Step 3: Deploy to App Engine

```bash
# Deploy using the script
./deploy_gcp.sh

# Or deploy manually
gcloud app deploy app.yaml
```

### Step 4: Access Your App

After deployment, your app will be available at:
```
https://your-project-id.appspot.com
```

## 🔧 Configuration Files

### Dockerfile
- Uses Python 3.11 slim image
- Installs all required dependencies
- Exposes port 8080
- Includes health checks

### app.yaml
- **Runtime**: Custom (Docker)
- **Scaling**: Automatic (1-10 instances)
- **Resources**: 1 CPU, 2GB RAM
- **Health Checks**: Built-in Streamlit health endpoint

### .gcloudignore
- Excludes unnecessary files from deployment
- Reduces deployment size and time

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
gcloud app logs tail -s rsi-downloader

# Error logs only
gcloud app logs tail -s rsi-downloader --severity=ERROR

# Logs from specific time
gcloud app logs read --service=rsi-downloader --since=1h
```

### View Metrics
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "App Engine" > "Services"
3. Click on "rsi-downloader" to view metrics

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs
gcloud app logs tail -s rsi-downloader

# Redeploy with verbose output
gcloud app deploy app.yaml --verbosity=debug
```

#### 2. Memory Issues
Increase memory in `app.yaml`:
```yaml
resources:
  memory_gb: 4  # Increase from 2 to 4
```

#### 3. API Blocking
- The app includes fallback mechanisms for IP-blocked exchanges
- MEXC should work in most regions
- Consider using VPN for other exchanges

#### 4. Health Check Failures
```bash
# Check health endpoint
curl https://your-project-id.appspot.com/_stcore/health

# View health check logs
gcloud app logs tail -s rsi-downloader --severity=ERROR
```

### Debug Commands

```bash
# Check app status
gcloud app describe

# List all versions
gcloud app versions list

# View specific version
gcloud app versions describe VERSION_ID

# Check service configuration
gcloud app services describe rsi-downloader
```

## 💰 Cost Optimization

### App Engine Pricing
- **Free Tier**: 28 instance hours per day
- **Paid**: ~$0.05-0.10 per hour per instance

### Cost Reduction Tips

#### 1. Set Minimum Instances to 0
```yaml
automatic_scaling:
  min_num_instances: 0  # Change from 1 to 0
```

#### 2. Use Smaller Instances
```yaml
resources:
  cpu: 0.5  # Reduce from 1
  memory_gb: 1  # Reduce from 2
```

#### 3. Optimize Scaling
```yaml
automatic_scaling:
  min_num_instances: 0
  max_num_instances: 3  # Reduce from 10
  cool_down_period: 120s  # Increase from 60s
```

## 🔄 Updates & Maintenance

### Update Deployment
```bash
# Make changes to your code
# Then redeploy
gcloud app deploy app.yaml

# Or use the deployment script
./deploy_gcp.sh
```

### Rollback to Previous Version
```bash
# List versions
gcloud app versions list

# Rollback to specific version
gcloud app services set-traffic rsi-downloader --splits=VERSION_ID=1
```

### Stop Service
```bash
# Stop a specific version
gcloud app versions stop VERSION_ID

# Delete the entire service
gcloud app services delete rsi-downloader
```

## 🗑️ Cleanup

### Remove App
```bash
# Delete the service
gcloud app services delete rsi-downloader

# Delete the project (careful!)
gcloud projects delete your-rsi-project-id
```

### Cost Monitoring
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "Billing" > "Reports"
3. Set up billing alerts

## 📞 Support

### Google Cloud Resources
- [App Engine Python Documentation](https://cloud.google.com/appengine/docs/python/)
- [Google Cloud Support](https://cloud.google.com/support)

### Project Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [GitHub Repository](https://github.com/MeowIrist/Tradingview_excel)

### Common Solutions
- **API Issues**: Check API keys and permissions
- **Memory Issues**: Increase memory allocation
- **Scaling Issues**: Adjust scaling parameters
- **Health Check Failures**: Check app logs and dependencies

---

## 🎯 Quick Commands Summary

```bash
# Setup
./setup_gcp.sh

# Deploy
./deploy_gcp.sh

# View logs
gcloud app logs tail -s rsi-downloader

# Check status
gcloud app describe

# Update
gcloud app deploy app.yaml

# Stop
gcloud app versions stop VERSION_ID
```

**Your app will be available at: `https://your-project-id.appspot.com`** 🚀
