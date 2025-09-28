"""
Wrapper functions for all exchanges to provide a unified interface for the Streamlit app.
Each exchange has its own implementation but follows the same interface pattern.
"""

import pandas as pd
import ta
import time
import os
from typing import List, Optional, Dict, Any

# Import exchange modules
try:
    from mexc_version import get_all_spot_symbols as get_mexc_symbols, get_mexc_single_batch_klines_rest
except ImportError as e:
    print(f"Warning: Could not import MEXC module: {e}")
    get_mexc_symbols = None
    get_mexc_single_batch_klines_rest = None

try:
    from binance_ver import get_binance_all_time_klines
except ImportError as e:
    print(f"Warning: Could not import Binance module: {e}")
    get_binance_all_time_klines = None

try:
    from gateio_ver import get_all_spot_pairs_gateio, get_gateio_single_batch_klines
    print("✅ Gate.io module imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import Gate.io module: {e}")
    print("💡 Installing missing dependencies...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gate-api"])
        print("✅ Gate.io dependencies installed, retrying import...")
        from gateio_ver import get_all_spot_pairs_gateio, get_gateio_single_batch_klines
        print("✅ Gate.io module imported successfully after installation")
    except Exception as install_error:
        print(f"❌ Failed to install Gate.io dependencies: {install_error}")
        get_all_spot_pairs_gateio = None
        get_gateio_single_batch_klines = None

try:
    from bybit_ver import get_bybit_single_batch_klines
except ImportError as e:
    print(f"Warning: Could not import Bybit module: {e}")
    get_bybit_single_batch_klines = None

def get_exchange_symbols(exchange: str) -> List[str]:
    """Get all USDT symbols for the specified exchange."""
    print(f"🔍 [DEBUG] Starting symbol fetch for {exchange}")
    print(f"🔍 [DEBUG] Environment: {os.environ.get('STREAMLIT_SERVER_HEADLESS', 'Not set')}")
    
    if exchange == "MEXC":
        print(f"🔍 [DEBUG] MEXC: Using local module")
        if get_mexc_symbols is None:
            print(f"❌ [DEBUG] MEXC: Module not available")
            return []
        try:
            symbols = get_mexc_symbols()
            print(f"✅ [DEBUG] MEXC: Found {len(symbols)} symbols")
            return symbols
        except Exception as e:
            print(f"❌ [DEBUG] MEXC: Error - {e}")
            return []
            
    elif exchange == "Binance":
        print(f"🔍 [DEBUG] Binance: Starting HTTP request")
        import requests
        url = "https://api.binance.com/api/v3/exchangeInfo"
        print(f"🔍 [DEBUG] Binance: URL = {url}")
        
        try:
            print(f"🔍 [DEBUG] Binance: Making request...")
            resp = requests.get(url, timeout=30)
            print(f"🔍 [DEBUG] Binance: Response status = {resp.status_code}")
            print(f"🔍 [DEBUG] Binance: Response headers = {dict(resp.headers)}")
            
            if resp.status_code == 200:
                print(f"🔍 [DEBUG] Binance: Parsing JSON response...")
                data = resp.json()
                print(f"🔍 [DEBUG] Binance: Response keys = {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                symbols = [s['symbol'] for s in data.get('symbols', []) if s.get('status') == 'TRADING']
                usdt_symbols = [s for s in symbols if s.endswith('USDT')]
                print(f"✅ [DEBUG] Binance: Found {len(usdt_symbols)} USDT symbols")
                return usdt_symbols
            else:
                print(f"❌ [DEBUG] Binance: HTTP error {resp.status_code}")
                print(f"❌ [DEBUG] Binance: Response text = {resp.text[:500]}")
                return []
        except Exception as e:
            print(f"❌ [DEBUG] Binance: Exception - {e}")
            print(f"❌ [DEBUG] Binance: Exception type - {type(e)}")
            import traceback
            print(f"❌ [DEBUG] Binance: Traceback - {traceback.format_exc()}")
            return []
            
    elif exchange == "Gate":
        print(f"🔍 [DEBUG] Gate: Starting symbol fetch")
        if get_all_spot_pairs_gateio is None:
            print(f"⚠️ [DEBUG] Gate: SDK module not available, trying HTTP fallback")
            try:
                # HTTP fallback for Gate.io
                import requests
                url = "https://api.gateio.ws/api/v4/spot/currency_pairs"
                print(f"🔍 [DEBUG] Gate: HTTP fallback URL = {url}")
                
                resp = requests.get(url, timeout=30)
                print(f"🔍 [DEBUG] Gate: HTTP response status = {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    symbols = [pair['id'] for pair in data if pair.get('quote') == 'USDT' and pair.get('trade_status') == 'tradable']
                    print(f"✅ [DEBUG] Gate: HTTP fallback found {len(symbols)} symbols")
                    return symbols
                else:
                    print(f"❌ [DEBUG] Gate: HTTP fallback failed with status {resp.status_code}")
                    return []
            except Exception as e:
                print(f"❌ [DEBUG] Gate: HTTP fallback error - {e}")
                return []
        else:
            print(f"🔍 [DEBUG] Gate: Using SDK module")
            try:
                symbols = get_all_spot_pairs_gateio()
                print(f"✅ [DEBUG] Gate: SDK found {len(symbols)} symbols")
                return symbols
            except Exception as e:
                print(f"❌ [DEBUG] Gate: SDK error - {e}")
                import traceback
                print(f"❌ [DEBUG] Gate: SDK traceback - {traceback.format_exc()}")
                return []
            
    elif exchange == "Bybit":
        print(f"🔍 [DEBUG] Bybit: Starting HTTP request")
        import requests
        url = "https://api.bybit.com/v5/market/instruments-info"
        params = {"category": "spot"}
        print(f"🔍 [DEBUG] Bybit: URL = {url}")
        print(f"🔍 [DEBUG] Bybit: Params = {params}")
        
        try:
            print(f"🔍 [DEBUG] Bybit: Making request...")
            resp = requests.get(url, params=params, timeout=30)
            print(f"🔍 [DEBUG] Bybit: Response status = {resp.status_code}")
            print(f"🔍 [DEBUG] Bybit: Response headers = {dict(resp.headers)}")
            
            if resp.status_code == 200:
                print(f"🔍 [DEBUG] Bybit: Parsing JSON response...")
                data = resp.json()
                print(f"🔍 [DEBUG] Bybit: Response keys = {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                symbols = [item['symbol'] for item in data.get('result', {}).get('list', [])]
                usdt_symbols = [s for s in symbols if s.endswith('USDT')]
                print(f"✅ [DEBUG] Bybit: Found {len(usdt_symbols)} USDT symbols")
                return usdt_symbols
            else:
                print(f"❌ [DEBUG] Bybit: HTTP error {resp.status_code}")
                print(f"❌ [DEBUG] Bybit: Response text = {resp.text[:500]}")
                return []
        except Exception as e:
            print(f"❌ [DEBUG] Bybit: Exception - {e}")
            print(f"❌ [DEBUG] Bybit: Exception type - {type(e)}")
            import traceback
            print(f"❌ [DEBUG] Bybit: Traceback - {traceback.format_exc()}")
            return []
    
    print(f"❌ [DEBUG] Unknown exchange: {exchange}")
    return []

def get_single_batch_klines(exchange: str, symbol: str, interval: str, limit: int = 1000, 
                           api_key: Optional[str] = None, api_secret: Optional[str] = None,
                           **kwargs) -> Optional[pd.DataFrame]:
    """
    Get a single batch of klines for the specified exchange and symbol.
    
    Args:
        exchange: Exchange name (MEXC, Binance, Gate, Bybit)
        symbol: Trading pair symbol
        interval: Time interval
        limit: Number of candles to fetch
        api_key: API key (if required)
        api_secret: API secret (if required)
        **kwargs: Additional exchange-specific parameters
    
    Returns:
        DataFrame with OHLCV data or None if error
    """
    try:
        if exchange == "MEXC":
            if get_mexc_single_batch_klines_rest is None:
                raise ValueError("MEXC module not available")
            if not api_key or not api_secret:
                raise ValueError("MEXC requires API_KEY and API_SECRET")
            return get_mexc_single_batch_klines_rest(
                symbol=symbol,
                interval=interval,
                limit=limit,
                api_key=api_key,
                api_secret=api_secret
            )
        
        elif exchange == "Binance":
            if get_binance_all_time_klines is None:
                raise ValueError("Binance module not available")
            # Binance public endpoint, no auth needed
            return get_binance_all_time_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
        
        elif exchange == "Gate":
            if get_gateio_single_batch_klines is None:
                raise ValueError("Gate.io module not available")
            # Gate.io public endpoint, no auth needed for basic data
            return get_gateio_single_batch_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
        
        elif exchange == "Bybit":
            if get_bybit_single_batch_klines is None:
                raise ValueError("Bybit module not available")
            category = kwargs.get('category', 'spot')
            return get_bybit_single_batch_klines(
                symbol=symbol,
                interval=interval,
                category=category,
                limit=limit
            )
        
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")
    
    except Exception as e:
        print(f"Error fetching data for {symbol} from {exchange}: {e}")
        return None

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate RSI for the DataFrame."""
    if df is None or df.empty:
        return df
    
    df = df.copy()
    df['RSI'] = ta.momentum.rsi(df['Close'], window=period)
    return df

def get_exchange_credentials(exchange: str) -> Dict[str, Optional[str]]:
    """Get API credentials for the specified exchange from environment variables."""
    if exchange == "MEXC":
        return {
            'api_key': os.getenv('API_KEY'),
            'api_secret': os.getenv('API_SECRET')
        }
    elif exchange == "Binance":
        return {
            'api_key': os.getenv('BINANCE_API_KEY'),
            'api_secret': os.getenv('BINANCE_API_SECRET')
        }
    elif exchange == "Gate":
        return {
            'api_key': os.getenv('GATE_API_KEY'),
            'api_secret': os.getenv('GATE_API_SECRET')
        }
    elif exchange == "Bybit":
        return {
            'api_key': os.getenv('BYBIT_API_KEY'),
            'api_secret': os.getenv('BYBIT_API_SECRET')
        }
    return {'api_key': None, 'api_secret': None}

def requires_auth(exchange: str) -> bool:
    """Check if the exchange requires authentication for basic klines data."""
    # MEXC requires auth for klines
    # Others are public for basic data
    return exchange == "MEXC"
