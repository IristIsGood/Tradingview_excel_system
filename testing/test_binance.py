import requests
import pandas as pd
import ta # Library for Technical Analysis indicators
import datetime
import time

# --- Configuration ---
# Binance API endpoint for Klines (candlestick data)
BASE_URL = "https://api.binance.com/api/v3/klines"

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
    
    # Convert string dates to Unix milliseconds timestamps if provided
    start_timestamp = None
    if start_str:
        start_dt = datetime.datetime.strptime(start_str, '%Y-%m-%d')
        start_timestamp = int(start_dt.timestamp() * 1000)

    end_timestamp = None
    if end_str:
        end_dt = datetime.datetime.strptime(end_str, '%Y-%m-%d')
        end_timestamp = int(end_dt.timestamp() * 1000)
    else:
        end_timestamp = int(time.time() * 1000) # Start from current time if no end_date

    print(f"Starting historical data fetch for {symbol} ({interval})...")

    while True:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'endTime': end_timestamp # Fetch data up to this point
        }
        if start_timestamp:
            params['startTime'] = start_timestamp # Limit the start if specified

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses
            klines = response.json()

            if not klines:
                print("No more data found or reached beginning of history.")
                break

            # Add fetched klines to the beginning of the list (since we fetch backwards)
            all_klines = klines + all_klines

            # Get the timestamp of the earliest candle in the current batch
            # This will be the new 'endTime' for the next request
            earliest_candle_time = klines[0][0] # klines[0][0] is the open_time of the first candle

            # If we've reached or passed the user-defined start_timestamp, stop
            if start_timestamp and earliest_candle_time <= start_timestamp:
                print("Reached specified start date.")
                break

            # Update end_timestamp for the next iteration (go back one interval from earliest_candle_time)
            # Subtract a small amount to ensure we don't fetch the same candle again
            end_timestamp = earliest_candle_time - 1

            print(f"Fetched {len(klines)} candles. Total: {len(all_klines)}. Continuing from {datetime.datetime.fromtimestamp(earliest_candle_time / 1000)}...")
            time.sleep(0.1) # Be kind to the API, avoid hitting rate limits

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"An unexpected error occurred: {req_err}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during data fetching: {e}")
            return None

    if not all_klines:
        print("No data retrieved.")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(all_klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
    df.sort_index(inplace=True) # Ensure chronological order

    return df[['open', 'high', 'low', 'close', 'volume']].rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
    })


# --- Main execution ---
if __name__ == "__main__":
    # --- Define your meme coin symbol and parameters ---
    # For Binance, symbols are typically like 'DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'WIFUSDT', 'BONKUSDT'
    # Make sure the symbol exists on Binance.
    meme_coin_symbol = 'BMTBNB'
    interval_data = '1d' # Daily candles. For very long history, daily is recommended.
    rsi_period = 14 # Standard RSI calculation period

    # Set start_date to a very early date for "all-time" or when the coin was listed.
    # If None, it will fetch from the earliest available on Binance for that symbol.
    start_date = '2021-01-01' # Example: SHIB was listed around mid-2021, so this will get most of its history.
    end_date = None # Fetch up to the current moment

    # 1. Fetch historical data from Binance (all-time)
    historical_df = get_binance_all_time_klines(
        symbol=meme_coin_symbol,
        interval=interval_data,
        start_str=start_date,
        end_str=end_date
    )

    if historical_df is not None and not historical_df.empty:
        print(f"\nSuccessfully fetched {len(historical_df)} data points for {meme_coin_symbol}.")
        print("Raw historical data (first 5 rows):")
        print(historical_df.head())
        print("Raw historical data (last 5 rows):")
        print(historical_df.tail())


        # 2. Calculate RSI
        historical_df['RSI'] = ta.momentum.rsi(historical_df['Close'], window=rsi_period)

        print(f"\nHistorical Close Price and RSI for {meme_coin_symbol} (last 10 rows, RSI period {rsi_period}):")
        print(historical_df[['Close', 'RSI']].tail(10))

        # 3. Indicate the lowest RSI value
        # Drop NaN values before finding the minimum, as initial RSI values are empty
        lowest_rsi = historical_df['RSI'].dropna().min()
        if not pd.isna(lowest_rsi): # Check if lowest_rsi is not NaN (i.e., there was at least one valid RSI)
            print(f"\nLowest calculated RSI for {meme_coin_symbol}: {lowest_rsi:.2f}")
        else:
            print(f"\nCould not determine lowest RSI for {meme_coin_symbol} (not enough data for calculation).")


        # 4. Export historical data to Excel
        excel_filename = f'{meme_coin_symbol}_all_time_historical_data_with_rsi.xlsx'
        try:
            historical_df.to_excel(excel_filename)
            print(f"\nHistorical data with RSI successfully exported to {excel_filename}")
        except Exception as e:
            print(f"\nError exporting to Excel: {e}")

    else:
        print(f"\nFailed to retrieve historical data for {meme_coin_symbol}.")

