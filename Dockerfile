# Simple Dockerfile for Koyeb deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install optional packages (may fail, but that's OK)
RUN pip install --no-cache-dir gate-api || echo "gate-api installation failed, continuing..."
RUN pip install --no-cache-dir ccxt || echo "ccxt installation failed, continuing..."
RUN pip install --no-cache-dir tradingview_ta || echo "tradingview_ta installation failed, continuing..."
RUN pip install --no-cache-dir pandas_ta || echo "pandas_ta installation failed, continuing..."

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the application
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
