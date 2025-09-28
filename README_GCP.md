# RSI Downloader - Google Cloud Platform Deployment

This guide will help you deploy the RSI Downloader Streamlit app to Google App Engine.

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud Account**: Sign up at [Google Cloud Console](https://console.cloud.google.com/)
2. **Google Cloud CLI**: Install from [here](https://cloud.google.com/sdk/docs/install)
3. **Project Setup**: Create a new project in Google Cloud Console

### Step 1: Setup Google Cloud

```bash
# Install Google Cloud CLI (if not already installed)
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login

# Create a new project (replace with your project name)
gcloud projects create your-rsi-project-id

# Set the project
gcloud config set project your-rsi-project-id

# Enable billing (required for App Engine)
# Go to: https://console.cloud.google.com/billing
```

### Step 2: Configure Environment Variables

Create a `.env` file with your API keys:

```bash
# Copy the template
cp env_template.txt .env

# Edit .env with your actual API keys
nano .env
```

Example `.env` content:
```
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

### Step 3: Deploy to Google App Engine

```bash
# Make the deployment script executable
chmod +x deploy_gcp.sh

# Edit the script to set your project ID
nano deploy_gcp.sh
# Change: PROJECT_ID="your-project-id"

# Run the deployment
./deploy_gcp.sh
```

### Step 4: Access Your App

After deployment, you'll get a URL like:
```
https://your-project-id.appspot.com
```

## 🔧 Configuration

### App Engine Settings (app.yaml)

- **Runtime**: Custom (Docker)
- **Scaling**: Automatic (1-10 instances)
- **Resources**: 1 CPU, 2GB RAM
- **Health Checks**: Built-in Streamlit health endpoint

### Environment Variables

The app uses these environment variables:
- `STREAMLIT_SERVER_PORT=8080`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`

## 📊 Monitoring

### View Logs
```bash
# View real-time logs
gcloud app logs tail -s rsi-downloader

# View specific log levels
gcloud app logs tail -s rsi-downloader --severity=ERROR
```

### View Metrics
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to "App Engine" > "Services"
- Click on "rsi-downloader" to view metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   gcloud app logs tail -s rsi-downloader
   
   # Redeploy with verbose output
   gcloud app deploy app.yaml --verbosity=debug
   ```

2. **Memory Issues**
   - Increase memory in `app.yaml`:
     ```yaml
     resources:
       memory_gb: 4  # Increase from 2 to 4
     ```

3. **API Blocking**
   - The app includes fallback mechanisms for IP-blocked exchanges
   - MEXC should work in most regions
   - Consider using VPN for other exchanges

### Health Checks

The app includes health checks at `/_stcore/health`:
- **Readiness**: Checks if app is ready to serve traffic
- **Liveness**: Checks if app is still running

## 💰 Cost Optimization

### App Engine Pricing
- **Free Tier**: 28 instance hours per day
- **Paid**: ~$0.05-0.10 per hour per instance

### Cost Reduction Tips
1. **Set minimum instances to 0** (in app.yaml):
   ```yaml
   automatic_scaling:
     min_num_instances: 0  # Change from 1 to 0
   ```

2. **Use smaller instances**:
   ```yaml
   resources:
     cpu: 0.5  # Reduce from 1
     memory_gb: 1  # Reduce from 2
   ```

## 🔄 Updates

To update your deployment:

```bash
# Make changes to your code
# Then redeploy
gcloud app deploy app.yaml

# Or use the deployment script
./deploy_gcp.sh
```

## 🗑️ Cleanup

To stop the service:

```bash
# List versions
gcloud app versions list

# Stop a specific version
gcloud app versions stop VERSION_ID

# Delete the entire service
gcloud app services delete rsi-downloader
```

## 📞 Support

- **Google Cloud Documentation**: [App Engine Python](https://cloud.google.com/appengine/docs/python/)
- **Streamlit Documentation**: [Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- **Project Issues**: Check the GitHub repository

---

**Note**: This deployment uses Google App Engine Flexible Environment with custom Docker containers. The app will automatically scale based on traffic and includes health monitoring.
