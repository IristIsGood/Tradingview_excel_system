import requests
import pandas as pd
import ta # Library for Technical Analysis indicators
import datetime
import time
import json 
import logging 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
BASE_URL_KLINES_BYBIT = "https://api.bybit.com/v5/market/kline"
BASE_URL_INSTRUMENTS_INFO_BYBIT = "https://api.bybit.com/v5/market/instruments-info"

# --- Function to map common intervals to Bybit's interval format ---
def map_interval_to_bybit(interval):
    """
    Maps common interval strings to Bybit's API format.
    """
    if interval == '1d':
        return 'D'
    elif interval == '1h':
        return '60'
    elif interval == '4h':
        return '240'
    elif interval == '15m':
        return '15'
    elif interval == '1m':
        return '1'
    logger.warning(f"Unsupported interval '{interval}' for Bybit mapping. Returning as is.")
    return interval 


# --- Function to fetch a single batch of historical data from Bybit API ---
# This function is designed to get the most recent 'limit' candles up to 'end_date'
def get_bybit_single_batch_klines(symbol, interval, category, end_str=None, limit=1000):
    """
    Fetches a single batch of historical klines (candlestick data) from Bybit
    for a given symbol, interval, and category.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
        interval (str): Time interval (e.g., '1d', '4h').
        category (str): Product category (e.g., 'spot', 'linear', 'inverse').
        end_str (str, optional): End date in 'YYYY-MM-DD' format. If None, fetches up to now.
        limit (int): Max number of candles per API request (Bybit max is 1000).

    Returns:
        pandas.DataFrame: DataFrame with OHLCV data, or None if an error occurs.
    """
    bybit_interval = map_interval_to_bybit(interval)

    end_timestamp = None
    if end_str:
        end_dt = datetime.datetime.strptime(end_str, '%Y-%m-%d')
        end_timestamp = int(end_dt.timestamp() * 1000)
    else:
        end_timestamp = int(time.time() * 1000) # Current time in milliseconds
    
    logger.debug(f"  [{symbol}] Fetching batch up to end timestamp: {end_timestamp} ({datetime.datetime.fromtimestamp(end_timestamp / 1000)})")

    params = {
        'symbol': symbol,
        'interval': bybit_interval,
        'category': category,
        'limit': limit,
        'endTime': end_timestamp
    }
    # No start_timestamp needed here, as we are simply requesting the last 'limit' candles ending at 'endTime'.
    # If a start_timestamp was provided, it might conflict with the 'limit' or make the intent less clear for a single batch.

    try:
        response = requests.get(BASE_URL_KLINES_BYBIT, params=params, timeout=15) 
        response.raise_for_status() 
        json_response = response.json()

        if json_response.get('retCode') != 0:
            error_msg = json_response.get('retMsg', 'Unknown error')
            logger.error(f"  [{symbol}] Bybit API Error (retCode: {json_response.get('retCode')}): {error_msg}")
            logger.debug(f"  [{symbol}] Full API Error Response: {json.dumps(json_response, indent=2)}")
            return None

        klines = json_response.get('result', {}).get('list', [])

        if not klines:
            logger.info(f"  [{symbol}] No data found for the specified period and limit.")
            return None

        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover' 
        ])
        df['open_time'] = pd.to_datetime(df['open_time'].astype(int), unit='ms') 
        df.set_index('open_time', inplace=True)
        
        df[['open', 'high', 'low', 'close', 'volume', 'turnover']] = df[['open', 'high', 'low', 'close', 'volume', 'turnover']].astype(float)
        
        df.sort_index(inplace=True) # Ensure chronological order (oldest to newest)

        logger.info(f"  [{symbol}] Fetched {len(df)} candles in a single batch.")
        return df[['open', 'high', 'low', 'close', 'volume']].rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        })

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"  [{symbol}] HTTP error occurred: {http_err} (Status: {http_err.response.status_code})")
        if http_err.response and http_err.response.text:
            logger.error(f"  [{symbol}] Response content: {http_err.response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"  [{symbol}] Connection error occurred: {conn_err}")
        logger.error("  This usually means no internet connection, DNS issue, or firewall blocking.")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"  [{symbol}] Timeout error occurred: {timeout_err}")
        logger.error("  The request took too long to get a response.")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"  [{symbol}] An unexpected request error occurred: {req_err}")
        return None
    except json.JSONDecodeError as json_err:
        logger.error(f"  [{symbol}] JSON decoding error: {json_err}")
        if response and response.text:
            logger.error(f"  [{symbol}] Response content (could not parse as JSON): {response.text}")
        return None
    except Exception as e:
        logger.error(f"  [{symbol}] An unexpected general error occurred during data fetching: {e}", exc_info=True)
        return None


# --- Function to fetch exchange information for Bybit ---
def get_bybit_exchange_info(category='spot'):
    """
    Fetches instrument information from Bybit's /api/v5/market/instruments-info endpoint.
    """
    url = BASE_URL_INSTRUMENTS_INFO_BYBIT
    params = {'category': category}
    
    logger.info(f"Attempting to fetch instruments info from: {url} (category: {category})")
    try:
        response = requests.get(url, params=params, timeout=15) 
        response.raise_for_status() 

        json_response = response.json()
        if json_response.get('retCode') != 0:
            error_msg = json_response.get('retMsg', 'Unknown error')
            logger.error(f"Bybit API Error for instruments info (retCode: {json_response.get('retCode')}): {error_msg}")
            logger.debug(f"Full API Error Response: {json.dumps(json_response, indent=2)}")
            return None

        logger.info("Successfully received and parsed JSON response for instruments info.")
        return json_response.get('result', {}) 

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred during instruments info fetch: {http_err} (Status: {http_err.response.status_code})")
        if http_err.response and http_err.response.text:
            logger.error(f"Response content: {http_err.response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection error occurred during instruments info fetch: {conn_err}")
        logger.error("This usually means no internet connection, DNS issue, or firewall blocking.")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout error occurred during instruments info fetch: {timeout_err}")
        logger.error("The request took too long to get a response.")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"An unexpected request error occurred during instruments info fetch: {req_err}")
        return None
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decoding error during instruments info fetch: {json_err}")
        if response and response.text:
            logger.error(f"Response content (could not parse as JSON): {response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected general error occurred during instruments info fetch: {e}", exc_info=True)
        return None


# --- Main execution ---
if __name__ == "__main__":
    bybit_category = 'spot' 
    interval_data = '1d' # Daily candles.
    rsi_period = 14 # Standard RSI calculation period
    
    # We are fetching the most recent 'limit' candles for each symbol
    # 'end_date' can be set to a specific past date (e.g., '2024-12-31')
    # or left as None to get data up to the current moment.
    end_date_for_fetch = None 
    fetch_limit = 1000 # Number of recent candles to fetch for each symbol (max 1000 for Bybit)

    # List to store results for all coins: [{'symbol': 'BTCUSDT', 'lowest_rsi': 25.45, ...}, ...]
    all_coins_rsi_summary = []

    logger.info(f"\n--- Starting process to find lowest RSI for recent {fetch_limit} candles across all {bybit_category.upper()} USDT pairs ---")

    # 1. Fetch exchange information to get all symbols
    exchange_info_result = get_bybit_exchange_info(category=bybit_category)

    if exchange_info_result:
        all_symbols_info = exchange_info_result.get('list', [])
        
        target_symbols = []
        for s in all_symbols_info:
            if s['status'] == 'Trading' and s['quoteCoin'] == 'USDT':
                target_symbols.append(s['symbol'])
        
        logger.info(f"Found {len(target_symbols)} active {bybit_category.upper()} USDT trading pairs on Bybit.")

        # Optional: Limit to a smaller number of symbols for faster testing/debugging
        # target_symbols = target_symbols[:50] # Process only the first 50 symbols for quick test
        # logger.info(f"Processing a subset of {len(target_symbols)} symbols for demonstration.")

        for i, symbol in enumerate(target_symbols):
            logger.info(f"\n[{i+1}/{len(target_symbols)}] Processing {symbol}...")
            
            historical_df = get_bybit_single_batch_klines( # Call the single batch function
                symbol=symbol,
                interval=interval_data,
                category=bybit_category,
                end_str=end_date_for_fetch,
                limit=fetch_limit
            )

            if historical_df is not None and not historical_df.empty:
                # 2. Calculate RSI for the fetched batch
                historical_df['RSI'] = ta.momentum.rsi(historical_df['Close'], window=rsi_period)

                # 3. Find the lowest RSI value and its details within this batch
                rsi_series_cleaned = historical_df['RSI'].dropna()

                if not rsi_series_cleaned.empty:
                    lowest_rsi = rsi_series_cleaned.min()
                    date_of_lowest_rsi = rsi_series_cleaned.idxmin()
                    price_at_lowest_rsi = historical_df.loc[date_of_lowest_rsi, 'Close']

                    logger.info(f"  Lowest RSI for {symbol} (in last {fetch_limit} candles): {lowest_rsi:.2f} on {date_of_lowest_rsi.strftime('%Y-%m-%d')} at price {price_at_lowest_rsi:.8f}")
                    
                    all_coins_rsi_summary.append({
                        'Symbol': symbol,
                        'Lowest_RSI_in_Batch': lowest_rsi, # Renamed for clarity: reflects it's from the batch
                        'Date_of_Lowest_RSI_in_Batch': date_of_lowest_rsi.strftime('%Y-%m-%d %H:%M:%S'),
                        'Price_at_Lowest_RSI_in_Batch': price_at_lowest_rsi,
                        'Exchange': 'Bybit',
                        'Category': bybit_category,
                        'Interval': interval_data,
                        'RSI_Period': rsi_period,
                        'Batch_Start_Date': historical_df.index.min().strftime('%Y-%m-%d'),
                        'Batch_End_Date': historical_df.index.max().strftime('%Y-%m-%d'),
                        'Number_of_Candles_in_Batch': len(historical_df)
                    })
                else:
                    logger.warning(f"  Could not determine lowest RSI for {symbol} (not enough valid RSI data in batch).")
            else:
                logger.info(f"  No sufficient historical data for {symbol} in the last {fetch_limit} candles to calculate RSI.")
            
            time.sleep(0.3) # Be respectful of Bybit's API rate limits

        # 4. Export all collected lowest RSI values to a single Excel file
        if all_coins_rsi_summary:
            results_df = pd.DataFrame(all_coins_rsi_summary)
            
            # Sort by lowest RSI to easily identify the "most oversold" in the fetched batches
            results_df.sort_values(by='Lowest_RSI_in_Batch', ascending=True, inplace=True)

            excel_filename = f'Bybit_Lowest_RSI_Summary_Recent_{fetch_limit}_{interval_data}_{bybit_category}.xlsx'
            try:
                results_df.to_excel(excel_filename, index=False)
                logger.info(f"\n--- All lowest RSI values (from recent {fetch_limit} candles) successfully exported to {excel_filename} ---")
                logger.info("Top 20 results (lowest RSI in batch):")
                logger.info(results_df.head(20).to_string())
            except Exception as e:
                logger.error(f"\nError exporting results to Excel: {e}", exc_info=True)
        else:
            logger.info("\nNo RSI data was collected for any symbols.")

    else:
        logger.error("\nFailed to retrieve exchange information. Cannot proceed with symbol processing.")

    logger.info(f"\n--- Finished full process ---")