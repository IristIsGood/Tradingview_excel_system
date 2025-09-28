#!/usr/bin/env python3
"""
Debug script to test network connectivity and API access
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("🔍 Testing basic internet connectivity...")
    try:
        resp = requests.get("https://httpbin.org/get", timeout=10)
        print(f"✅ Basic HTTP: Success (Status: {resp.status_code})")
        return True
    except Exception as e:
        print(f"❌ Basic HTTP: Failed - {e}")
        return False

def test_binance_api():
    """Test Binance API access"""
    print("\n🔍 Testing Binance API...")
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        print(f"URL: {url}")
        
        resp = requests.get(url, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        
        if resp.status_code == 200:
            data = resp.json()
            symbols = [s['symbol'] for s in data.get('symbols', []) if s.get('status') == 'TRADING']
            usdt_symbols = [s for s in symbols if s.endswith('USDT')]
            print(f"✅ Binance: Found {len(usdt_symbols)} USDT symbols")
            print(f"First 5: {usdt_symbols[:5]}")
            return True
        else:
            print(f"❌ Binance: HTTP error {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Binance: Exception - {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_bybit_api():
    """Test Bybit API access"""
    print("\n🔍 Testing Bybit API...")
    try:
        url = "https://api.bybit.com/v5/market/instruments-info"
        params = {"category": "spot"}
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        resp = requests.get(url, params=params, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        
        if resp.status_code == 200:
            data = resp.json()
            symbols = [item['symbol'] for item in data.get('result', {}).get('list', [])]
            usdt_symbols = [s for s in symbols if s.endswith('USDT')]
            print(f"✅ Bybit: Found {len(usdt_symbols)} USDT symbols")
            print(f"First 5: {usdt_symbols[:5]}")
            return True
        else:
            print(f"❌ Bybit: HTTP error {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Bybit: Exception - {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_environment():
    """Test environment variables and system info"""
    print("\n🔍 Environment Information:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Environment Variables:")
    for key in ['STREAMLIT_SERVER_HEADLESS', 'STREAMLIT_SERVER_PORT', 'STREAMLIT_SERVER_ADDRESS']:
        print(f"  - {key}: {os.environ.get(key, 'Not set')}")
    
    print(f"\nNetwork Configuration:")
    try:
        import socket
        print(f"Hostname: {socket.gethostname()}")
        print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
    except Exception as e:
        print(f"Network info error: {e}")

def main():
    """Main debug function"""
    print("🚀 RSI Downloader - Network Debug Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    
    # Test environment
    test_environment()
    
    # Test basic connectivity
    basic_ok = test_basic_connectivity()
    
    # Test exchange APIs
    binance_ok = test_binance_api()
    bybit_ok = test_bybit_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Debug Summary:")
    print(f"Basic Connectivity: {'✅' if basic_ok else '❌'}")
    print(f"Binance API: {'✅' if binance_ok else '❌'}")
    print(f"Bybit API: {'✅' if bybit_ok else '❌'}")
    
    if not basic_ok:
        print("\n❌ No internet connectivity. Check your network connection.")
    elif not binance_ok and not bybit_ok:
        print("\n❌ Exchange APIs are blocked. This might be due to:")
        print("  - Firewall restrictions")
        print("  - Corporate network blocking")
        print("  - Geographic restrictions")
        print("  - Rate limiting")
    elif binance_ok and bybit_ok:
        print("\n✅ All APIs working correctly!")
    else:
        print("\n⚠️ Some APIs are working, others are not.")

if __name__ == "__main__":
    main()
