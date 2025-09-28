#!/bin/bash

# RSI Downloader Launcher Script
# For Mac/Linux users

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ASCII Art
echo -e "${BLUE}"
echo "  ██████╗ ███████╗██╗    ██╗██╗    ██╗██╗     ██╗███████╗"
echo "  ██╔══██╗██╔════╝██║    ██║██║    ██║██║     ██║██╔════╝"
echo "  ██████╔╝███████╗██║    ██║██║    ██║██║     ██║███████╗"
echo "  ██╔══██╗╚════██║██║    ██║██║    ██║██║     ██║╚════██║"
echo "  ██║  ██║███████║╚██████╔╝╚██████╔╝███████╗██║███████║"
echo "  ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚══════╝"
echo -e "${NC}"
echo -e "${GREEN}  🚀 Multi-Exchange RSI Data Downloader${NC}"
echo -e "${GREEN}  =====================================${NC}"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found.${NC}"
    echo
    echo "Please install Python 3.8+ from: https://python.org"
    echo "After installation, run this script again."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}✅ Python found!${NC}"

# Check if we're in the right directory
if [ ! -f "src/app.py" ]; then
    echo -e "${RED}❌ Error: Application files not found.${NC}"
    echo "Please make sure you're running this from the RSI_Downloader folder."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}✅ Application files found!${NC}"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Setting up environment (first time only)...${NC}"
    echo "This may take a few minutes..."
    echo
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r config/requirements.txt
    echo
    echo -e "${GREEN}✅ Setup complete!${NC}"
else
    echo -e "${BLUE}🔄 Activating environment...${NC}"
    source venv/bin/activate
fi

echo
echo -e "${GREEN}🚀 Starting RSI Downloader...${NC}"
echo "The application will open in your web browser."
echo
echo "Press Ctrl+C to stop the application."
echo

# Run the application
python src/app.py

echo
echo -e "${YELLOW}👋 Application stopped.${NC}"
