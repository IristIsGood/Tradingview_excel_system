import os
import sys
import time
import platform
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from exchange_wrappers import (
    get_exchange_symbols, 
    get_single_batch_klines, 
    calculate_rsi, 
    get_exchange_credentials,
    requires_auth
)

# Create output directory if it doesn't exist
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="RSI Downloader", layout="wide")
    st.title("RSI Downloader - Multi Exchange Support")
    
    # Debug information
    with st.expander("🔍 Debug Information", expanded=False):
        st.write("**Environment Details:**")
        st.write(f"- Python Version: {sys.version}")
        st.write(f"- Streamlit Version: {st.__version__}")
        st.write(f"- Platform: {platform.platform()}")
        st.write(f"- Working Directory: {os.getcwd()}")
        st.write(f"- Environment Variables:")
        for key in ['STREAMLIT_SERVER_HEADLESS', 'STREAMLIT_SERVER_PORT', 'STREAMLIT_SERVER_ADDRESS']:
            st.write(f"  - {key}: {os.environ.get(key, 'Not set')}")
        
        st.write("**Network Test:**")
        try:
            import requests
            test_url = "https://httpbin.org/get"
            resp = requests.get(test_url, timeout=10)
            st.write(f"- HTTP Test: ✅ Success (Status: {resp.status_code})")
        except Exception as e:
            st.write(f"- HTTP Test: ❌ Failed - {e}")
        
        st.write("**Exchange API Test:**")
        for exchange in ["Binance", "Bybit"]:
            try:
                if exchange == "Binance":
                    test_url = "https://api.binance.com/api/v3/ping"
                elif exchange == "Bybit":
                    test_url = "https://api.bybit.com/v5/market/time"
                
                resp = requests.get(test_url, timeout=10)
                st.write(f"- {exchange} API: ✅ Success (Status: {resp.status_code})")
            except Exception as e:
                st.write(f"- {exchange} API: ❌ Failed - {e}")
    
    # Add sidebar for output management
    with st.sidebar:
        st.subheader("📁 Output Management")
        if st.button("🗑️ Clear Output Folder"):
            if os.path.exists(OUTPUT_DIR):
                for file in os.listdir(OUTPUT_DIR):
                    if file.endswith('.xlsx'):
                        os.remove(os.path.join(OUTPUT_DIR, file))
                st.success("Output folder cleared!")
                st.rerun()
        
        # Show current output folder status
        if os.path.exists(OUTPUT_DIR):
            output_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xlsx')]
            st.write(f"📊 Files in output: {len(output_files)}")
            if output_files:
                st.write("Recent files:")
                for file in output_files[-3:]:  # Show last 3 files
                    st.write(f"• {file}")
        else:
            st.write("📁 Output folder: Empty")
        
        st.subheader("🧪 Debug Tools")
        if st.button("🔍 Test Symbol Loading"):
            st.write("Testing symbol loading for all exchanges...")
            for exchange in ["MEXC", "Binance", "Gate", "Bybit"]:
                with st.spinner(f"Testing {exchange}..."):
                    try:
                        symbols = get_exchange_symbols(exchange)
                        st.write(f"✅ {exchange}: {len(symbols)} symbols")
                        if symbols:
                            st.write(f"  First 3: {symbols[:3]}")
                    except Exception as e:
                        st.write(f"❌ {exchange}: Error - {e}")
                        import traceback
                        st.code(traceback.format_exc())

    # Exchange selection
    exchange = st.selectbox("Exchange", ["MEXC", "Binance", "Gate", "Bybit"], index=0)
    
    # Check if exchange requires authentication
    needs_auth = requires_auth(exchange)
    if needs_auth:
        st.info(f"🔐 {exchange} requires API credentials for klines data")
    else:
        st.info(f"🌐 {exchange} uses public endpoints (no API key required)")

    # Hidden defaults
    default_limit = 1000
    default_sleep_ms = 200

    # Interval and data range
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"], index=5)

    range_mode = st.radio("Data Range", ["Recent N Candles", "Specific Year/Month"], index=0, horizontal=True)
    year = None
    month = None
    if range_mode == "Recent N Candles":
        st.caption(f"Using default limit={default_limit}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Year", list(range(2018, 2031)), index=7)
        with col2:
            month = st.selectbox("Month", list(range(1, 13)), index=0)
        st.caption("MVP will fetch data for the specified year/month range (to be implemented). Currently uses recent N candles.")

    # Exchange-specific parameters
    exchange_params = {}
    if exchange == "Bybit":
        category = st.selectbox("Category", ["spot", "linear", "inverse"], index=0)
        exchange_params['category'] = category

    # Symbol selection
    symbol_source = st.radio("Symbol Source", ["All USDT Pairs", "Manual Selection"], index=0, horizontal=True)
    symbols = []
    
    if symbol_source == "All USDT Pairs":
        if st.button("Load USDT Trading Pairs"):
            with st.spinner("Loading..."):
                st.session_state[f"{exchange.lower()}_symbols"] = get_exchange_symbols(exchange)
        symbols = st.session_state.get(f"{exchange.lower()}_symbols", [])
        st.write(f"Available USDT trading pairs: {len(symbols)}")
        st.info("ℹ️ **All USDT Pairs mode**: Will generate only a summary Excel file with lowest RSI data for all coins. No individual coin files will be created.")
    else:
        if f"{exchange.lower()}_symbols" not in st.session_state:
            with st.spinner("Loading symbols..."):
                st.session_state[f"{exchange.lower()}_symbols"] = get_exchange_symbols(exchange)
        
        # Set default symbol based on exchange format
        default_symbol = "BTC_USDT" if exchange == "Gate" else "BTCUSDT"
        symbols = st.multiselect("Select Trading Pairs", st.session_state[f"{exchange.lower()}_symbols"], default=[default_symbol])
        st.info("ℹ️ **Manual Selection mode**: Will generate individual Excel files for each selected coin plus a summary file.") 

    # Start button
    start = st.button("Start Download", type="primary")
    if not start:
        st.stop()

    # Check credentials if needed
    if needs_auth:
        credentials = get_exchange_credentials(exchange)
        api_key = credentials.get('api_key')
        api_secret = credentials.get('api_secret')
        
        if not api_key or not api_secret:
            st.error(f"{exchange} API_KEY/API_SECRET missing. Please configure in environment variables and retry.")
            st.code(f"# Add to your .env file:\n{exchange.upper()}_API_KEY=your_key_here\n{exchange.upper()}_API_SECRET=your_secret_here")
            st.stop()
    else:
        api_key = None
        api_secret = None

    # Determine target symbols
    targets = symbols if symbol_source == "Manual Selection" else symbols
    if not targets:
        st.error("No trading pairs available. Please load or select symbols first.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()
    all_coins_rsi_summary = []  # Store comprehensive results like original

    for i, sym in enumerate(targets):
        status.write(f"[{i+1}/{len(targets)}] Processing {sym} ...")
        try:
            # Call exchange wrapper function
            df = get_single_batch_klines(
                exchange=exchange,
                symbol=sym,
                interval=interval,
                limit=default_limit,
                api_key=api_key,
                api_secret=api_secret,
                **exchange_params
            )
            
            if df is None or df.empty:
                st.warning(f"No data available: {sym}")
                continue
            
            # Calculate RSI
            df = calculate_rsi(df, period=14)
            
            # Find the lowest RSI value and its details (same as original)
            lowest_rsi = df['RSI'].dropna().min()
            if not pd.isna(lowest_rsi):
                # Find the row with the lowest RSI
                lowest_rsi_row = df[df['RSI'] == lowest_rsi].iloc[0]
                date_of_lowest_rsi = lowest_rsi_row.name
                price_at_lowest_rsi = lowest_rsi_row['Close']
                
                # Get the latest data
                latest_row = df.iloc[-1]
                latest_rsi = latest_row['RSI']
                latest_price = latest_row['Close']
                latest_date = latest_row.name

                # Add all the information to the summary list (same format as original)
                all_coins_rsi_summary.append({
                    'Symbol': sym,
                    'Lowest_RSI_in_Batch': lowest_rsi,
                    'Date_of_Lowest_RSI_in_Batch': date_of_lowest_rsi.strftime('%Y-%m-%d %H:%M:%S'),
                    'Price_at_Lowest_RSI_in_Batch': price_at_lowest_rsi,
                    'Latest_RSI': latest_rsi,
                    'Latest_Price': latest_price,
                    'Latest_Date': latest_date.strftime('%Y-%m-%d %H:%M:%S') if latest_date else 'N/A',
                    'Exchange': exchange,
                    'Category': 'spot',
                    'Interval': interval,
                    'RSI_Period': 14,
                    'Batch_Start_Date': df.index.min().strftime('%Y-%m-%d %H:%M:%S'),
                    'Batch_End_Date': df.index.max().strftime('%Y-%m-%d %H:%M:%S'),
                    'Number_of_Candles_in_Batch': len(df)
                })
                st.write(f"  Lowest calculated RSI for {sym}: {lowest_rsi:.2f}")
            else:
                st.write(f"  Could not determine lowest RSI for {sym} (not enough data for calculation).")

            # Only export individual symbol data when using manual selection
            if symbol_source == "Manual Selection":
                out_name = os.path.join(OUTPUT_DIR, f"{exchange.upper()}_{sym}_historical_data_with_rsi.xlsx")
                df.to_excel(out_name)
            
        except Exception as e:
            st.error(f"Error processing {sym}: {e}")
            continue
        
        time.sleep(default_sleep_ms / 1000.0)
        progress.progress(int((i + 1) / max(1, len(targets)) * 100))

    st.success("Completed")
    
    # Show output folder contents
    if os.path.exists(OUTPUT_DIR):
        output_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.xlsx')]
        if output_files:
            st.subheader("📁 Output Files")
            st.write(f"Files saved in `{OUTPUT_DIR}/` folder:")
            
            # Create columns for file display
            cols = st.columns(3)
            for i, file in enumerate(output_files):
                with cols[i % 3]:
                    file_path = os.path.join(OUTPUT_DIR, file)
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            f"📄 {file}",
                            f,
                            file_name=file,
                            key=f"download_{i}"
                        )
    
    if all_coins_rsi_summary:
        # Create comprehensive summary DataFrame (same format as original)
        final_df = pd.DataFrame(all_coins_rsi_summary)
        # Sort the DataFrame by the lowest RSI value, in ascending order (same as original)
        final_df = final_df.sort_values(by='Lowest_RSI_in_Batch').reset_index(drop=True)
        
        # Display the summary table
        st.dataframe(final_df, use_container_width=True)
        
        # Export comprehensive summary to output folder (same naming as original)
        summary_name = os.path.join(OUTPUT_DIR, f"{exchange.upper()}.io_Lowest_RSI_Summary_Recent_{default_limit}_{interval}.xlsx")
        try:
            final_df.to_excel(summary_name, index=False)
            st.success(f"All lowest RSI values successfully exported to {summary_name}")
            
            with open(summary_name, 'rb') as f:
                filename = os.path.basename(summary_name)
                st.download_button("Download Summary Excel", f, file_name=filename)
        except Exception as e:
            st.error(f"Error exporting the final report to Excel: {e}")
    else:
        st.warning("No data successfully retrieved. Please check network connection and API configuration.")

if __name__ == "__main__":
    main()