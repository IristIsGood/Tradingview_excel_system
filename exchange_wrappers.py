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
except ImportError as e:
    print(f"Warning: Could not import Gate.io module: {e}")
    get_all_spot_pairs_gateio = None
    get_gateio_single_batch_klines = None

try:
    from bybit_ver import get_bybit_single_batch_klines
except ImportError as e:
    print(f"Warning: Could not import Bybit module: {e}")
    get_bybit_single_batch_klines = None

def get_exchange_symbols(exchange: str) -> List[str]:
    """Get all USDT symbols for the specified exchange."""
    if exchange == "MEXC":
        if get_mexc_symbols is None:
            return []
        return get_mexc_symbols()
    elif exchange == "Binance":
        # Binance doesn't need API key for public data
        import requests
        url = "https://api.binance.com/api/v3/exchangeInfo"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            symbols = [s['symbol'] for s in data.get('symbols', []) if s.get('status') == 'TRADING']
            return [s for s in symbols if s.endswith('USDT')]
        return []
    elif exchange == "Gate":
        if get_all_spot_pairs_gateio is None:
            return []
        return get_all_spot_pairs_gateio()
    elif exchange == "Bybit":
        # Bybit public endpoint for instruments
        import requests
        url = "https://api.bybit.com/v5/market/instruments-info"
        params = {"category": "spot"}
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            symbols = [item['symbol'] for item in data.get('result', {}).get('list', [])]
            return [s for s in symbols if s.endswith('USDT')]
        return []
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
