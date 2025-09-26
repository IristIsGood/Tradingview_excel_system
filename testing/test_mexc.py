import pandas as pd
import ta
import time
import hmac
import hashlib
import logging
from urllib.parse import urlencode
import requests

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
Fetch a single batch of klines (candles) from MEXC using REST only (signed request).
"""
def get_mexc_single_batch_klines_sdk(symbol, interval, limit=1000, api_key=None, api_secret=None):
    try:
        # Normalize symbol for MEXC (no underscore)
        norm_symbol = symbol.replace('_', '').upper()

        # Build signed REST request
        base_url = "https://api.mexc.com/api/v3/klines"
        params = {
            "symbol": norm_symbol,
            "interval": interval,
            "limit": int(limit),
            "timestamp": int(time.time() * 1000),
        }
        query = urlencode(params)
        signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
        headers = {"X-MEXC-APIKEY": api_key}
        url = f"{base_url}?{query}&signature={signature}"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.error(f"[{symbol}] REST klines failed: {resp.status_code} {resp.text}")
            return None
        klines = resp.json()

        if not klines:
            logger.info(f"[{symbol}] No data found (REST).")
            return None

        # Flexible parse of klines: use first six fields [open_time, open, high, low, close, volume]
        df_all = pd.DataFrame(klines)
        needed = df_all.iloc[:, [0, 1, 2, 3, 4, 5]].copy()
        needed.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        ts0 = int(needed.iloc[0]['open_time'])
        unit = 'ms' if ts0 > 10**12 else 's'
        needed['open_time'] = pd.to_datetime(needed['open_time'], unit=unit)
        needed.set_index('open_time', inplace=True)
        needed = needed.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
        return needed.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        })
    except Exception as e:
        logger.error(f"[{symbol}] REST error: {e}")
        return None

# --- Main execution ---
if __name__ == "__main__":
    # --- IMPORTANT: Best practice is to store API keys securely, not hardcoded. ---
    # For this example, we'll use the key and secret you provided.
    API_KEY = 'mx0vglGJXJmRcK8AL4'
    API_SECRET = '9a0da50ef84548db87211a802f4b18ac'
    
    interval_data = '1d' # Daily candles.
    rsi_period = 14 # Standard RSI calculation period
    fetch_limit = 1000 # Number of recent candles to fetch for each symbol (max 1000)

    # --- We are now testing with a single, hardcoded symbol as requested.
    target_symbols = ['ORNJ_USDT']
    
    if target_symbols:
        logger.info(f"\n--- Starting process for a single symbol: {target_symbols[0]} ---")

        for i, symbol in enumerate(target_symbols):
            logger.info(f"\n[{i+1}/{len(target_symbols)}] Processing {symbol}...")
            
            # Start the timer for this coin
            start_time = time.perf_counter()

            historical_df = get_mexc_single_batch_klines_sdk(
                symbol=symbol,
                interval=interval_data,
                limit=fetch_limit,
                api_key=API_KEY,  # Pass the API key
                api_secret=API_SECRET  # Pass the API secret
            )

            # Stop the timer
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            if historical_df is not None and not historical_df.empty:
                logger.info(f"  Successfully fetched {len(historical_df)} data points for {symbol} in {duration:.2f} seconds.")

                # 2. Calculate RSI for the fetched batch
                historical_df['RSI'] = ta.momentum.rsi(historical_df['Close'], window=rsi_period)

                # 3. Find the lowest RSI value and its details within this batch
                lowest_rsi = historical_df['RSI'].dropna().min()
                if not pd.isna(lowest_rsi):
                    print(f"\nLowest calculated RSI for {target_symbols[0]}: {lowest_rsi:.2f}")
                else:
                    print(f"\nCould not determine lowest RSI for {target_symbols[0]} (not enough data for calculation).")

                # 4. Export ALL 1000 historical data points to Excel
                excel_filename = f'MEXC_SDK_{target_symbols[0]}_historical_data_with_rsi.xlsx'
                try:
                    historical_df.to_excel(excel_filename)
                    print(f"\nHistorical data with RSI successfully exported to {excel_filename}")
                except Exception as e:
                    print(f"\nError exporting to Excel: {e}")

    else:
        logger.error("\nNo symbols to process. Cannot proceed.")

    logger.info(f"\n--- Finished full process ---")
