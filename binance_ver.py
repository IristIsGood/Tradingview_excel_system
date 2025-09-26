import requests
import pandas as pd
import ta # Library for Technical Analysis indicators
import datetime
import time
import json # Import json for pretty printing

# --- Configuration ---
# Binance API endpoint for Klines (candlestick data)
BASE_URL_KLINES = "https://api.binance.com/api/v3/klines"
BASE_URL_EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"

# --- Function to fetch historical data from Binance API (iterative) ---
def get_binance_all_time_klines(symbol, interval, start_str=None, end_str=None, limit=1000):
    """
    Fetches all available historical klines (candlestick data) from Binance
    for a given symbol and interval, handling pagination.

    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT', 'SHIBUSDT').
        interval (str): Time interval (e.g., '1d', '4h', '1h', '15m').
        start_str (str, optional): Start date in 'YYYY-MM-DD' format. If None, fetches from earliest.
        end_str (str, optional): End date in 'YYYY-MM-DD' format. If None, fetches up to now.
        limit (int): Max number of candles per API request (Binance max is 1000).

    Returns:
        pandas.DataFrame: DataFrame with OHLCV data, or None if an error occurs.
    """
    all_klines = []
    
    start_timestamp = None
    if start_str:
        start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%d')
        start_timestamp = int(start_dt.timestamp() * 1000)
        print(f"  [{symbol}] Target start timestamp: {start_timestamp} ({start_str})")


    end_timestamp = None
    if end_str:
        end_dt = datetime.datetime.strptime(end_str, '%Y-%m-%d')
        end_timestamp = int(end_dt.timestamp() * 1000)
    else:
        end_timestamp = int(time.time() * 1000) 
    print(f"  [{symbol}] Initial end timestamp: {end_timestamp} ({datetime.datetime.fromtimestamp(end_timestamp / 1000)})")


    print(f"Starting historical data fetch for {symbol} ({interval})...")

    iteration_count = 0
    max_iterations = 5000 # Safety break: stop if too many iterations (e.g., 5000 * 1000 candles = 5M candles)


    while True:
        iteration_count += 1
        if iteration_count > max_iterations:
            print(f"  [{symbol}] Warning: Reached max iterations ({max_iterations}). Stopping fetch to prevent infinite loop.")
            break

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'endTime': end_timestamp 
        }
        if start_timestamp:
            params['startTime'] = start_timestamp 

        current_params_log = {k: (datetime.datetime.fromtimestamp(v / 1000).strftime('%Y-%m-%d %H:%M:%S') if 'Time' in k else v) for k, v in params.items()}
        print(f"  [{symbol}] API Request params (Iteration {iteration_count}): {current_params_log}")


        try:
            response = requests.get(BASE_URL_KLINES, params=params, timeout=15) # Increased timeout for robustness
            response.raise_for_status() 
            klines = response.json()

            if not klines:
                print(f"  [{symbol}] No more data found or reached beginning of history.")
                break

            all_klines = klines + all_klines

            earliest_candle_time = klines[0][0] 
            print(f"  [{symbol}] Fetched {len(klines)} candles. Total: {len(all_klines)}. Continuing from {datetime.datetime.fromtimestamp(earliest_candle_time / 1000)}...")


            if start_timestamp and earliest_candle_time <= start_timestamp:
                print(f"  [{symbol}] Reached specified start date ({start_str}). Stopping fetch.")
                break

            end_timestamp = earliest_candle_time - 1

            time.sleep(0.1) 

        except requests.exceptions.HTTPError as http_err:
            print(f"  [{symbol}] HTTP error occurred: {http_err} (Status: {http_err.response.status_code})")
            if response and response.text:
                print(f"  [{symbol}] Response content: {response.text}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            print(f"  [{symbol}] Connection error occurred: {conn_err}")
            print("  This usually means no internet connection, DNS issue, or firewall blocking.")
            return None
        except requests.exceptions.Timeout as timeout_err:
            print(f"  [{symbol}] Timeout error occurred: {timeout_err}")
            print("  The request took too long to get a response.")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"  [{symbol}] An unexpected error occurred: {req_err}")
            return None
        except json.JSONDecodeError as json_err:
            print(f"  [{symbol}] JSON decoding error: {json_err}")
            if response and response.text:
                print(f"  [{symbol}] Response content (could not parse as JSON): {response.text}")
            return None
        except Exception as e:
            print(f"  [{symbol}] An unexpected error occurred during data fetching: {e}") # Removed exc_info=True for print
            return None

    if not all_klines:
        print(f"  [{symbol}] No data retrieved.")
        return None

    df = pd.DataFrame(all_klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
    df.sort_index(inplace=True) 

    print(f"  [{symbol}] Final DataFrame created with {len(df)} entries.")
    return df[['open', 'high', 'low', 'close', 'volume']].rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
    })


# --- Function to fetch exchange information ---
def get_binance_exchange_info():
    """
    Fetches exchange information from Binance's /api/v3/exchangeInfo endpoint.
    Includes enhanced error handling and response printing for debugging.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    url = BASE_URL_EXCHANGE_INFO
    
    print(f"Attempting to fetch data from: {url}")
    try:
        response = requests.get(url, timeout=10) 
        
        print(f"HTTP Status Code: {response.status_code}")
        response.raise_for_status() 

        data = response.json()
        print("Successfully received and parsed JSON response.")
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content (if any): {response.text}") 
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        print("This usually means no internet connection, DNS issue, or firewall blocking.")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        print("The request took too long to get a response.")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return None
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {json_err}")
        print(f"Response content (could not parse as JSON): {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected general error occurred: {e}")
        return None


# --- Main execution ---
if __name__ == "__main__":
    # --- Parameters for RSI calculation ---
    interval_data = '3d' # Daily candles.
    rsi_period = 28 # Standard RSI calculation period
    start_date = '2021-01-01' # Start date for historical data fetch
    end_date = None # Fetch up to the current moment

    # List to store results: [{'symbol': 'BTCUSDT', 'lowest_rsi': 25.45, ...}, ...]
    all_coins_rsi_data = []

    print(f"\n--- Starting process to find lowest RSI for all {interval_data} candles across all Binance USDT spot pairs ---")


    # 1. Fetch exchange information to get all symbols
    exchange_info = get_binance_exchange_info()

    if exchange_info:
        print("\n--- Processing Symbols ---")
        all_symbols_info = exchange_info.get('symbols', [])
        
        # Filter for spot trading pairs that are currently trading and end with USDT
        target_symbols = []
        for s in all_symbols_info:
            if s['status'] == 'TRADING' and s['isSpotTradingAllowed'] and s['quoteAsset'] == 'USDT':
                # Example: If you want to include specific meme coins like DOGE, SHIB, PEPE, WIF, BONK
                # if s['baseAsset'] in ['DOGE', 'SHIB', 'PEPE', 'WIF', 'BONK'] or 'USDT' in s['symbol']:
                target_symbols.append(s['symbol'])
        
        print(f"Found {len(target_symbols)} active USDT spot trading pairs.")

        # Optional: Limit to a smaller number of symbols for faster testing/debugging
        # target_symbols = target_symbols[:20] 
        # print(f"Processing first {len(target_symbols)} symbols for demonstration (remove line for all symbols).")

        for i, symbol in enumerate(target_symbols):
            print(f"\n[{i+1}/{len(target_symbols)}] Processing {symbol}...")
            
            historical_df = get_binance_all_time_klines(
                symbol=symbol,
                interval=interval_data,
                start_str=start_date,
                end_str=end_date
            )

            # --- Calculate RSI for the fetched historical data ---
            if historical_df is not None and not historical_df.empty:
                historical_df['RSI'] = ta.momentum.rsi(historical_df['Close'], window=rsi_period)

                # --- Get Latest RSI and Price ---
                latest_rsi = None
                latest_price = None
                latest_date = None

                # Ensure there's enough data for RSI calculation AND the last candle has a valid RSI yet
                latest_valid_rsi_data_point = historical_df['RSI'].dropna()
                if not latest_valid_rsi_data_point.empty:
                    latest_date = latest_valid_rsi_data_point.index[-1]
                    latest_rsi = latest_valid_rsi_data_point.iloc[-1]
                    latest_price = historical_df.loc[latest_date, 'Close'] 

                    print(f"  Latest data for {symbol}: RSI={latest_rsi:.2f}, Price={latest_price:.8f} on {latest_date.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  Could not determine latest valid RSI for {symbol}.")


                # Drop NaN values from RSI before finding the minimum
                rsi_series_cleaned = historical_df['RSI'].dropna()

                if not rsi_series_cleaned.empty:
                    lowest_rsi = rsi_series_cleaned.min()
                    
                    # Find the index (datetime) of the lowest RSI
                    date_of_lowest_rsi = rsi_series_cleaned.idxmin()
                    
                    # Get the corresponding close price on that date
                    price_at_lowest_rsi = historical_df.loc[date_of_lowest_rsi, 'Close']

                    print(f"  Lowest calculated RSI for {symbol}: {lowest_rsi:.2f} on {date_of_lowest_rsi.strftime('%Y-%m-%d')} at price {price_at_lowest_rsi:.8f}")
                    
                    all_coins_rsi_data.append({
                        'Symbol': symbol,
                        'Lowest_RSI': lowest_rsi,
                        'Date_of_Lowest_RSI': date_of_lowest_rsi.strftime('%Y-%m-%d %H:%M:%S'), # Format datetime nicely
                        'Price_at_Lowest_RSI': price_at_lowest_rsi,
                        'Latest_RSI': latest_rsi, # ADDED
                        'Latest_Price': latest_price, # ADDED
                        'Latest_Date': latest_date.strftime('%Y-%m-%d %H:%M:%S') if latest_date else 'N/A', # ADDED
                        'Exchange': 'Binance', # Added for clarity in combined results
                        'Interval': interval_data,
                        'RSI_Period': rsi_period,
                        'Data_Start_Date': historical_df.index.min().strftime('%Y-%m-%d') if not historical_df.empty else 'N/A',
                        'Data_End_Date': historical_df.index.max().strftime('%Y-%m-%d') if not historical_df.empty else 'N/A',
                        'Number_of_Candles': len(historical_df)
                    })
                else:
                    print(f"  Could not determine lowest RSI for {symbol} (not enough data for calculation or all RSI values are NaN).")
            else:
                print(f"  Failed to retrieve historical data for {symbol} or data is empty.")
            
            time.sleep(0.5) # Be respectful of Binance's API rate limits between symbol fetches
            
        # 5. Export all lowest RSI values to a single Excel file
        if all_coins_rsi_data:
            results_df = pd.DataFrame(all_coins_rsi_data)
            
            results_df.sort_values(by='Lowest_RSI', ascending=True, inplace=True)

            excel_filename = f'Binance_RSI_Summary_All_Time_{interval_data}.xlsx' # Renamed for clarity
            try:
                results_df.to_excel(excel_filename, index=False)
                print(f"\n--- All RSI values (from all-time history) successfully exported to {excel_filename} ---")
                print("Top 20 results (lowest RSI in full history):")
                print(results_df.head(20).to_string())
            except Exception as e:
                print(f"\nError exporting results to Excel: {e}")
        else:
            print("\nNo RSI data was collected for any symbols.")

    else:
        print("\nFailed to retrieve exchange information. Cannot proceed with symbol processing.")

    print(f"\n--- Finished full process ---")