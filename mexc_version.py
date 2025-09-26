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

# --- Helper function to get all tradable spot symbols ---
def get_all_spot_symbols():
    """
    Fetches a list of all tradable spot symbols from the public exchangeInfo endpoint.
    This is a public endpoint and does not require a signature.
    """
    try:
        url = "https://api.mexc.com/api/v3/exchangeInfo"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # The 'symbols' key contains a list of dictionaries with symbol information.
            # We want to extract just the 'symbol' value from each dictionary.
            symbols = [s['symbol'] for s in data['symbols']]
            return symbols
        else:
            logger.error(f"Failed to get exchange info: {resp.status_code} {resp.text}")
            return []
    except Exception as e:
        logger.error(f"An error occurred while fetching spot symbols: {e}")
        return []

# --- Function to fetch a single batch of klines using REST only ---
def get_mexc_single_batch_klines_rest(symbol, interval, limit=1000, api_key=None, api_secret=None):
    """
    Fetches a single batch of klines (candlestick data) from MEXC using a signed REST request.
    This function manually generates the signature required for the 'klines' endpoint.
    """
    try:
        # The 'klines' endpoint requires a SIGNED request.
        base_url = "https://api.mexc.com/api/v3/klines"
        params = {
            "symbol": symbol,  # Use the symbol directly as returned by exchangeInfo
            "interval": interval,
            "limit": int(limit),
            "timestamp": int(time.time() * 1000),
        }
        
        # Manually generate the signature
        query = urlencode(params)
        signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # Add the signature and API key to the request
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

        # Process the raw kline data into a DataFrame
        df_all = pd.DataFrame(klines)
        needed = df_all.iloc[:, [0, 1, 2, 3, 4, 5]].copy()
        needed.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        ts0 = int(needed.iloc[0]['open_time'])
        unit = 'ms' if ts0 > 10**12 else 's'
        needed['open_time'] = pd.to_datetime(needed['open_time'], unit=unit)
        needed.set_index('open_time', inplace=True)
        needed = needed.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
        needed = needed.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        return needed
    except Exception as e:
        logger.error(f"[{symbol}] REST error: {e}")
        return None

# --- Main execution ---
if __name__ == "__main__":
    # --- IMPORTANT: Best practice is to store API keys securely, not hardcoded. ---
    API_KEY = 'mx0vglGJXJmRcK8AL4'
    API_SECRET = '9a0da50ef84548db87211a802f4b18ac'
    
    interval_data = '1W' # Daily candles.
    rsi_period = 28 # Standard RSI calculation period
    fetch_limit = 1000 # Number of recent candles to fetch for each symbol (max 1000)
    
    all_coins_rsi_summary = [] # New list to store the comprehensive results

    # 1. Get the list of all spot symbols
    logger.info(f"\n--- Fetching all spot symbols... ---")
    target_symbols = get_all_spot_symbols()

    if not target_symbols:
        logger.error("\nNo symbols found. Cannot proceed.")
    else:
        logger.info(f"\n--- Found {len(target_symbols)} symbols. Starting data fetch... ---")

        # num_coins = 5
        # for i, symbol in enumerate(target_symbols[:num_coins]):

        for i, symbol in enumerate(target_symbols):
            logger.info(f"\n[{i+1}/{len(target_symbols)}] Processing {symbol}...")
            
            # Start the timer for this coin
            start_time = time.perf_counter()

            historical_df = get_mexc_single_batch_klines_rest(
                symbol=symbol,
                interval=interval_data,
                limit=fetch_limit,
                api_key=API_KEY,
                api_secret=API_SECRET
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
                    # Find the row with the lowest RSI
                    lowest_rsi_row = historical_df[historical_df['RSI'] == lowest_rsi].iloc[0]
                    date_of_lowest_rsi = lowest_rsi_row.name
                    price_at_lowest_rsi = lowest_rsi_row['Close']
                    
                    # Get the latest data
                    latest_row = historical_df.iloc[-1]
                    latest_rsi = latest_row['RSI']
                    latest_price = latest_row['Close']
                    latest_date = latest_row.name

                    # Add all the information to the summary list
                    all_coins_rsi_summary.append({
                        'Symbol': symbol,
                        'Lowest_RSI_in_Batch': lowest_rsi,
                        'Date_of_Lowest_RSI_in_Batch': date_of_lowest_rsi.strftime('%Y-%m-%d %H:%M:%S'),
                        'Price_at_Lowest_RSI_in_Batch': price_at_lowest_rsi,
                        'Latest_RSI': latest_rsi,
                        'Latest_Price': latest_price,
                        'Latest_Date': latest_date.strftime('%Y-%m-%d %H:%M:%S') if latest_date else 'N/A',
                        'Exchange': 'MEXC',
                        'Category': 'spot',
                        'Interval': interval_data,
                        'RSI_Period': rsi_period,
                        'Batch_Start_Date': historical_df.index.min().strftime('%Y-%m-%d %H:%M:%S'),
                        'Batch_End_Date': historical_df.index.max().strftime('%Y-%m-%d %H:%M:%S'),
                        'Number_of_Candles_in_Batch': len(historical_df)
                    })
                    print(f"  Lowest calculated RSI for {symbol}: {lowest_rsi:.2f}")
                else:
                    print(f"  Could not determine lowest RSI for {symbol} (not enough data for calculation).")
            
            # Add a small delay to avoid hitting rate limits.
            # The documentation mentions a 500 requests per 10 seconds limit.
            time.sleep(0.1)

        # --- New section to export all results to a single file ---
        if all_coins_rsi_summary:
            final_df = pd.DataFrame(all_coins_rsi_summary)
            # Sort the DataFrame by the lowest RSI value, in ascending order
            final_df = final_df.sort_values(by='Lowest_RSI_in_Batch').reset_index(drop=True)
            excel_filename = f'MEXC.io_Lowest_RSI_Summary_Recent_{fetch_limit}_{interval_data}.xlsx'
            try:
                final_df.to_excel(excel_filename, index=False)
                print(f"\nAll lowest RSI values successfully exported to {excel_filename}")
            except Exception as e:
                print(f"\nError exporting the final report to Excel: {e}")

    logger.info(f"\n--- Finished full process ---")
