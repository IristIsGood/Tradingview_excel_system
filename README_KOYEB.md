# 🚀 RSI Downloader - Koyeb Deployment

This guide shows how to deploy the RSI Downloader to Koyeb using Docker.

## 🚀 Quick Deployment

### Prerequisites
- Koyeb account ([Sign up here](https://koyeb.com/))
- GitHub repository with your code

### Step 1: Prepare Your Repository

Make sure your repository has:
- `Dockerfile` (already created)
- `Procfile` (already created)
- `start.sh` (already created)
- `requirements.txt` (already created)
- `.env` file with your API keys (create this)

### Step 2: Create .env File

Create a `.env` file in your repository root:

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

### Step 3: Deploy to Koyeb

#### Option A: Using Koyeb Dashboard

1. Go to [Koyeb Dashboard](https://app.koyeb.com/)
2. Click "Create Service"
3. Choose "GitHub" as source
4. Select your repository: `MeowIrist/Tradingview_excel`
5. Set branch to `main`
6. Choose "Docker" as runtime
7. Configure environment variables:
   - `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`
8. Add your API keys as environment variables
9. Click "Deploy"

#### Option B: Using Koyeb CLI

```bash
# Install Koyeb CLI
curl https://get.koyeb.com/cli | sh

# Login to Koyeb
koyeb auth login

# Deploy from GitHub
koyeb service create \
  --name rsi-downloader \
  --git github.com/MeowIrist/Tradingview_excel \
  --git-branch main \
  --dockerfile Dockerfile \
  --env STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
  --env STREAMLIT_SERVER_HEADLESS=true \
  --env STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Step 4: Access Your App

After deployment, your app will be available at:
```
https://your-service-name.koyeb.app
```

## 🔧 Configuration

### Dockerfile Features
- **Base Image**: Python 3.11 slim
- **Dependencies**: All required packages installed
- **Port**: Dynamic port assignment via `$PORT` environment variable
- **Health Check**: Built-in Streamlit health endpoint
- **Output Directory**: Created for Excel file storage

### Procfile
The `Procfile` tells Koyeb how to run your application:
```
web: ./start.sh
```

### Environment Variables
Set these in Koyeb dashboard or CLI:

**Required:**
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

**API Keys (add your actual keys):**
- `MEXC_API_KEY=your_mexc_key`
- `MEXC_API_SECRET=your_mexc_secret`
- `BINANCE_API_KEY=your_binance_key`
- `BINANCE_API_SECRET=your_binance_secret`
- `GATE_API_KEY=your_gate_key`
- `GATE_API_SECRET=your_gate_secret`
- `BYBIT_API_KEY=your_bybit_key`
- `BYBIT_API_SECRET=your_bybit_secret`

## 📊 Monitoring

### View Logs
```bash
# Using Koyeb CLI
koyeb service logs rsi-downloader

# Follow logs in real-time
koyeb service logs rsi-downloader --follow
```

### Check Status
```bash
# List services
koyeb service list

# Get service details
koyeb service get rsi-downloader
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "no command to run your application"
**Solution:** Make sure you have a `Procfile` in your repository root.

#### 2. Port Issues
**Solution:** The Dockerfile and startup script handle dynamic port assignment automatically.

#### 3. Environment Variables Not Loading
**Solution:** Set environment variables in Koyeb dashboard:
1. Go to your service
2. Click "Environment"
3. Add your API keys

#### 4. Build Failures
**Solution:** Check your `requirements.txt` includes all dependencies:
```
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
ta>=0.11.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
gate-api>=6.0.0
ccxt>=4.0.0
tradingview_ta>=3.3.0
pandas_ta>=0.3.14b0
numpy>=1.24.0
```

### Debug Commands

```bash
# Check service status
koyeb service get rsi-downloader

# View recent logs
koyeb service logs rsi-downloader --tail 100

# Check service health
koyeb service health rsi-downloader
```

## 🔄 Updates

### Update Your App
```bash
# Push changes to GitHub
git add .
git commit -m "Update app"
git push origin main

# Koyeb will automatically redeploy
```

### Manual Redeploy
```bash
# Force redeploy
koyeb service redeploy rsi-downloader
```

## 💰 Cost Optimization

### Koyeb Pricing
- **Free Tier**: 1 service, 512MB RAM, 0.1 CPU
- **Paid**: $0.10/hour per service

### Cost Reduction Tips
1. **Use Free Tier**: Perfect for development
2. **Optimize Resources**: Use minimal CPU/memory
3. **Auto-scaling**: Set appropriate min/max replicas

## 🗑️ Cleanup

### Remove Service
```bash
# Delete service
koyeb service delete rsi-downloader

# Or delete via dashboard
```

---

**Your RSI Downloader is now running on Koyeb! 🚀**

**App URL:** `https://your-service-name.koyeb.app`