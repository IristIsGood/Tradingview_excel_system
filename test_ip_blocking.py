#!/usr/bin/env python3
"""
Test script to check IP blocking issues with cryptocurrency exchanges.
This helps diagnose why APIs return 403/451 status codes.
"""

import requests
import json
import time
from datetime import datetime

def test_exchange_apis():
    """Test various exchange APIs for IP blocking issues."""
    print("🚀 IP Blocking Test for Cryptocurrency Exchanges")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test endpoints
    tests = [
        {
            "name": "Binance",
            "url": "https://api.binance.com/api/v3/ping",
            "description": "Basic connectivity test"
        },
        {
            "name": "Binance Exchange Info",
            "url": "https://api.binance.com/api/v3/exchangeInfo",
            "description": "Symbol list endpoint"
        },
        {
            "name": "Bybit",
            "url": "https://api.bybit.com/v5/market/time",
            "description": "Server time endpoint"
        },
        {
            "name": "Bybit Instruments",
            "url": "https://api.bybit.com/v5/market/instruments-info",
            "params": {"category": "spot"},
            "description": "Symbol list endpoint"
        },
        {
            "name": "Gate.io",
            "url": "https://api.gateio.ws/api/v4/spot/currency_pairs",
            "description": "Currency pairs endpoint"
        },
        {
            "name": "MEXC",
            "url": "https://api.mexc.com/api/v3/exchangeInfo",
            "description": "Exchange info endpoint"
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"🔍 Testing {test['name']}...")
        print(f"   URL: {test['url']}")
        print(f"   Description: {test['description']}")
        
        try:
            # Make request
            if 'params' in test:
                resp = requests.get(test['url'], params=test['params'], timeout=10)
            else:
                resp = requests.get(test['url'], timeout=10)
            
            print(f"   Status: {resp.status_code}")
            print(f"   Headers: {dict(resp.headers)}")
            
            # Analyze response
            if resp.status_code == 200:
                print(f"   ✅ SUCCESS: API accessible")
                status = "SUCCESS"
            elif resp.status_code == 403:
                print(f"   ❌ BLOCKED: IP address forbidden (403)")
                print(f"   💡 Solution: Use VPN or proxy server")
                status = "BLOCKED_403"
            elif resp.status_code == 451:
                print(f"   ❌ BLOCKED: Geographic restriction (451)")
                print(f"   💡 Solution: Use VPN from different region")
                status = "BLOCKED_451"
            elif resp.status_code == 429:
                print(f"   ⚠️ RATE_LIMITED: Too many requests (429)")
                print(f"   💡 Solution: Wait and retry")
                status = "RATE_LIMITED"
            else:
                print(f"   ❌ ERROR: Unexpected status {resp.status_code}")
                print(f"   Response: {resp.text[:200]}")
                status = "ERROR"
            
            results.append({
                'exchange': test['name'],
                'status_code': resp.status_code,
                'status': status,
                'url': test['url']
            })
            
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT: Request timed out")
            status = "TIMEOUT"
            results.append({
                'exchange': test['name'],
                'status_code': None,
                'status': status,
                'url': test['url']
            })
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            status = "EXCEPTION"
            results.append({
                'exchange': test['name'],
                'status_code': None,
                'status': status,
                'url': test['url']
            })
        
        print()
        time.sleep(1)  # Be nice to APIs
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    blocked_count = sum(1 for r in results if 'BLOCKED' in r['status'])
    error_count = len(results) - success_count - blocked_count
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Blocked: {blocked_count}")
    print(f"⚠️ Errors: {error_count}")
    print()
    
    # Detailed results
    for result in results:
        status_icon = {
            'SUCCESS': '✅',
            'BLOCKED_403': '❌',
            'BLOCKED_451': '❌',
            'RATE_LIMITED': '⚠️',
            'TIMEOUT': '⏰',
            'EXCEPTION': '💥',
            'ERROR': '❌'
        }.get(result['status'], '❓')
        
        print(f"{status_icon} {result['exchange']}: {result['status']}")
    
    print()
    print("💡 SOLUTIONS FOR IP BLOCKING:")
    print("- Use a VPN service (NordVPN, ExpressVPN, etc.)")
    print("- Try different server locations")
    print("- Use a proxy server")
    print("- Contact your ISP about restrictions")
    print("- Consider using MEXC which has fewer restrictions")
    
    return results

if __name__ == "__main__":
    test_exchange_apis()

