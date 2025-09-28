# 🐳 RSI Downloader - Docker Deployment

This guide shows how to run the RSI Downloader using Docker.

## 🚀 Quick Start

### Prerequisites
- Docker installed ([Download Docker](https://www.docker.com/get-started))
- Docker Compose (usually included with Docker Desktop)

### Step 1: Configure Environment

```bash
# Copy environment template
cp env_template.txt .env

# Edit with your API keys
nano .env
```

Add your API keys to `.env`:
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

### Step 2: Run with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Step 3: Access the Application

Open your browser and go to:
```
http://localhost:8501
```

## 🔧 Docker Commands

### Build Image
```bash
# Build the Docker image
docker build -t rsi-downloader .

# Build with no cache
docker build --no-cache -t rsi-downloader .
```

### Run Container
```bash
# Run the container
docker run -p 8501:8501 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/.env:/app/.env:ro \
  rsi-downloader

# Run in background
docker run -d -p 8501:8501 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/.env:/app/.env:ro \
  --name rsi-downloader \
  rsi-downloader
```

### Manage Container
```bash
# View running containers
docker ps

# View logs
docker logs rsi-downloader

# Stop container
docker stop rsi-downloader

# Remove container
docker rm rsi-downloader

# Remove image
docker rmi rsi-downloader
```

## 📁 Volume Mounts

The Docker setup includes these volume mounts:

- **`./output:/app/output`** - Output Excel files
- **`./.env:/app/.env:ro`** - Environment variables (read-only)

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8501
lsof -i :8501

# Kill the process
kill -9 PID

# Or use a different port
docker run -p 8502:8501 rsi-downloader
```

#### 2. Permission Issues
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/

# Or run with user permissions
docker run --user $(id -u):$(id -g) -p 8501:8501 rsi-downloader
```

#### 3. Environment Variables Not Loading
```bash
# Check if .env file exists
ls -la .env

# Check environment variables in container
docker exec rsi-downloader env | grep MEXC
```

#### 4. Build Failures
```bash
# Clean build
docker build --no-cache -t rsi-downloader .

# Check build logs
docker build -t rsi-downloader . 2>&1 | tee build.log
```

### Debug Commands

```bash
# Enter container shell
docker exec -it rsi-downloader /bin/bash

# View container logs
docker logs -f rsi-downloader

# Check container health
docker inspect rsi-downloader | grep -A 10 Health

# View container processes
docker exec rsi-downloader ps aux
```

## 🔄 Updates

### Update Application
```bash
# Stop current container
docker-compose down

# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d
```

### Update Dependencies
```bash
# Rebuild with updated requirements.txt
docker-compose build --no-cache

# Restart with new image
docker-compose up -d
```

## 🗑️ Cleanup

### Remove Everything
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi rsi-downloader

# Remove volumes (careful - this removes output files)
docker volume prune
```

### Keep Output Files
```bash
# Stop containers but keep volumes
docker-compose down

# Remove only the image
docker rmi rsi-downloader
```

## 📊 Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml rsi-downloader

# Scale service
docker service scale rsi-downloader_rsi-downloader=3
```

### Using Kubernetes
```bash
# Convert docker-compose to Kubernetes
kompose convert

# Deploy to Kubernetes
kubectl apply -f .
```

## 💡 Tips

1. **Development**: Use `docker-compose up` for development
2. **Production**: Use `docker-compose up -d` for background running
3. **Logs**: Always check logs with `docker-compose logs -f`
4. **Backup**: Regularly backup the `output/` directory
5. **Security**: Never commit `.env` files to git

---

**Your RSI Downloader is now running in Docker! 🐳**
