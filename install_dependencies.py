#!/usr/bin/env python3
"""
Install missing dependencies for RSI Downloader
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required dependencies"""
    print("🚀 RSI Downloader - Dependency Installer")
    print("=" * 50)
    
    # Required packages
    packages = [
        "streamlit",
        "pandas", 
        "requests",
        "ta",
        "openpyxl",
        "python-dotenv",
        "gate-api",
        "ccxt",
        "tradingview_ta",
        "pandas_ta"
    ]
    
    print("📋 Installing required packages...")
    print()
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("You can now run the RSI Downloader application.")
    else:
        print("⚠️ Some packages failed to install.")
        print("You may need to install them manually or check your internet connection.")
    
    print()
    print("🔧 To test the installation, run:")
    print("   python debug_network.py")

if __name__ == "__main__":
    main()
