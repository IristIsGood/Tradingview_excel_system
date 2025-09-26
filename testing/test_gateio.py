import pandas as pd
import ta
import datetime
import time
import gate_api
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Function to fetch all spot pairs from Gate.io ---
def get_all_spot_pairs_gateio():
    """
    Fetches all available spot currency pairs from Gate.io.
    Filters for USDT pairs only.
    """
    api_client = gate_api.ApiClient(gate_api.Configuration(host="https://api.gateio.ws/api/v4"))
    spot_api = gate_api.SpotApi(api_client)

    try:
        currency_pairs = spot_api.list_currency_pairs()
        usdt_pairs = [pair.id for pair in currency_pairs if pair.quote == 'USDT' and pair.trade_status == 'tradable']
        return usdt_pairs
    except gate_api.ApiException as e:
        logger.error(f"Gate.io API Exception when fetching pairs: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred when fetching pairs: {e}")
        return []

# --- Function to fetch a single batch of historical data from Gate.io ---
def get_gateio_single_batch_klines(symbol, interval, limit=1000, end_str=None):
    """
    Fetches a single batch of the most recent klines (candlestick data)
    from Gate.io for a given symbol and interval.
    """
    api_client = gate_api.ApiClient(gate_api.Configuration(host="https://api.gateio.ws/api/v4"))
    spot_api = gate_api.SpotApi(api_client)
    
    end_timestamp = int(time.time()) if not end_str else int(datetime.datetime.strptime(end_str, '%Y-%m-%d').timestamp())
    
    try:
        klines = spot_api.list_candlesticks(
            currency_pair=symbol,
            interval=interval,
            to=end_timestamp,
            limit=limit
        )

        if not klines:
            logger.info(f"[{symbol}] No data found.")
            return None

        # Gate.io API returns data in descending order of time.
        # It's a list of lists, where kline[0] is the timestamp.
        # We reverse it to be chronological and create the DataFrame.
        df = pd.DataFrame(reversed(klines), columns=[
            'timestamp', 'volume', 'close', 'high', 'low', 'open', 'quote_volume', 'is_last_item'
        ])
        
        df['open_time'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        df.set_index('open_time', inplace=True)
        df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float, 'quote_volume': float})
        
        return df[['open', 'high', 'low', 'close', 'volume']].rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        })

    except gate_api.ApiException as e:
        logger.error(f"[{symbol}] Gate.io API Exception: {e}")
        return None
    except Exception as e:
        logger.error(f"[{symbol}] An unexpected error occurred: {e}")
        return None

# --- Main execution ---
if __name__ == "__main__":
    interval_data = '1d' # Weekly candles.
    rsi_period = 14 # RSI calculation period for weekly data
    
    end_date_for_fetch = None 
    fetch_limit = 1000 # Number of recent candles to fetch (max 1000 for Gate.io)

    all_coins_rsi_summary = []

    # --- CHANGE START ---
    # We are now testing with a single, hardcoded symbol to verify the logic.
    target_symbols = ['ORNJ_USDT']
    # --- CHANGE END ---
    
    if target_symbols:
        logger.info(f"\n--- Starting process for a single symbol: {target_symbols[0]} ---")

        for i, symbol in enumerate(target_symbols):
            logger.info(f"\n[{i+1}/{len(target_symbols)}] Processing {symbol}...")
            
            # Start the timer for this coin
            start_time = time.perf_counter()

            historical_df = get_gateio_single_batch_klines(
                symbol=symbol,
                interval=interval_data,
                end_str=end_date_for_fetch,
                limit=fetch_limit
            )

            # Stop the timer
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            if historical_df is not None and not historical_df.empty:
                logger.info(f"  Successfully fetched {len(historical_df)} data points for {symbol} in {duration:.2f} seconds.")

                # 2. Calculate RSI for the fetched batch
                historical_df['RSI'] = ta.momentum.rsi(historical_df['Close'], window=rsi_period)

                # 3. Find the lowest RSI value and its details within this batch
                rsi_series_cleaned = historical_df['RSI'].dropna()

                lowest_rsi = historical_df['RSI'].dropna().min()
                if not pd.isna(lowest_rsi): # Check if lowest_rsi is not NaN (i.e., there was at least one valid RSI)
                    print(f"\nLowest calculated RSI for {target_symbols}: {lowest_rsi:.2f}")
                else:
                    print(f"\nCould not determine lowest RSI for {target_symbols} (not enough data for calculation).")


                # 4. Export historical data to Excel
                excel_filename = f'{target_symbols}_all_time_historical_data_with_rsi.xlsx'
                try:
                    historical_df.to_excel(excel_filename)
                    print(f"\nHistorical data with RSI successfully exported to {excel_filename}")
                except Exception as e:
                    print(f"\nError exporting to Excel: {e}")

    else:
        logger.error("\nFailed to retrieve exchange information. Cannot proceed with symbol processing.")

    logger.info(f"\n--- Finished full process ---")
