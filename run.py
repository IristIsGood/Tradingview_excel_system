#!/usr/bin/env python3
"""
Run script for Koyeb deployment.
This script handles dynamic port assignment and starts the Streamlit app.
"""

import os
import sys
import subprocess

def main():
    """Main entry point for Koyeb deployment."""
    # Set Streamlit environment variables (let Koyeb handle port)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Start Streamlit app (Koyeb will set PORT automatically)
    cmd = [
        "streamlit", "run", "app.py",
        "--server.address", "0.0.0.0"
    ]
    
    print("🚀 Starting RSI Downloader")
    print(f"📋 Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Application stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
