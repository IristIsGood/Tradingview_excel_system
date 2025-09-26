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

        print(df)
        
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
    interval_data = '1w' # Daily candles.
    rsi_period = 28 # Standard RSI calculation period
    
    end_date_for_fetch = None 
    fetch_limit = 1000 # Number of recent candles to fetch for each symbol (max 1000 for Gate.io)

    all_coins_rsi_summary = []

    logger.info(f"\n--- Starting process to find lowest RSI for recent {fetch_limit} candles across all Gate.io USDT spot pairs ---")

    # 1. Fetch exchange information to get all symbols
    target_symbols = get_all_spot_pairs_gateio()

    if target_symbols:
        logger.info(f"Found {len(target_symbols)} active USDT trading pairs on Gate.io.")

        # Optional: Limit to a smaller number of symbols for faster testing/debugging
        # target_symbols = target_symbols[:50] # Process only the first 50 symbols for quick test
        # logger.info(f"Processing a subset of {len(target_symbols)} symbols for demonstration.")

        # num_coins = 5
        # for i, symbol in enumerate(target_symbols[:num_coins]):

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

                print(historical_df['RSI'])

                # 3. Find the lowest RSI value and its details within this batch
                rsi_series_cleaned = historical_df['RSI'].dropna()

                if not historical_df.empty:
                    # The DataFrame is already sorted chronologically (oldest to newest)
                    # So, the last row contains the latest data.
                    latest_candle = historical_df.iloc[0]
                    latest_rsi = latest_candle['RSI']
                    latest_price = latest_candle['Close']
                    latest_date = latest_candle.name # The index is the datetime

                    logger.info(f"  Latest data for {symbol}: RSI={latest_rsi:.2f}, Price={latest_price:.8f} on {latest_date.strftime('%Y-%m-%d %H:%M:%S')}")
  
                if not rsi_series_cleaned.empty:
                    lowest_rsi = rsi_series_cleaned.dropna().min()
                    date_of_lowest_rsi = rsi_series_cleaned.idxmin()
                    price_at_lowest_rsi = historical_df.loc[date_of_lowest_rsi, 'Close']

                    logger.info(f"  Lowest RSI for {symbol} (in last {fetch_limit} candles): {lowest_rsi:.2f} on {date_of_lowest_rsi.strftime('%Y-%m-%d')} at price {price_at_lowest_rsi:.8f}")
                

                    all_coins_rsi_summary.append({
                        'Symbol': symbol,
                        'Lowest_RSI_in_Batch': lowest_rsi,
                        'Date_of_Lowest_RSI_in_Batch': date_of_lowest_rsi.strftime('%Y-%m-%d %H:%M:%S'),
                        'Price_at_Lowest_RSI_in_Batch': price_at_lowest_rsi,
                        'Latest_RSI': latest_rsi, # New column
                        'Latest_Price': latest_price, # New column
                        'Latest_Date': latest_date.strftime('%Y-%m-%d %H:%M:%S') if latest_date else 'N/A', # New column
                        'Exchange': 'Gate.io',
                        'Category': 'spot',
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
            
        # 4. Export all collected lowest RSI values to a single Excel file
        if all_coins_rsi_summary:
            results_df = pd.DataFrame(all_coins_rsi_summary)
            
            # results_df.sort_values(by='Lowest_RSI_in_Batch', ascending=True, inplace=True)

            excel_filename = f'Gate.io_Lowest_RSI_Summary_Recent_{fetch_limit}_{interval_data}.xlsx'
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