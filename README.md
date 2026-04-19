# RSI Downloader: Multi-Exchange Technical Analysis Tool 📊🤖
A web-based tool that fetches historical candlestick data from multiple crypto exchanges, calculates RSI (Relative Strength Index) indicators, and exports results to Excel. Built with **Pandas**, **TA-Lib**, and **Streamlit**, this project transforms raw exchange data into actionable technical analysis reports.

## 🎯 Problem & Solution
* **Problem:** Manually checking RSI across hundreds of trading pairs on multiple exchanges is time-consuming and error-prone. Traders need a fast way to identify oversold/overbought conditions across the entire market.
* **Solution:** A **Batch RSI Scanner**. This app connects to exchange APIs, fetches historical OHLCV data for all USDT pairs, calculates RSI for each symbol, and ranks them — letting traders instantly spot the most oversold coins across Binance, Bybit, MEXC, and Gate.io.

## 🏗️ Technical Architecture & Pipeline
This project implements a multi-exchange data pipeline optimized for batch analysis:

1. **Exchange Abstraction:** Uses a unified `exchange_wrappers.py` layer to normalize API differences across Binance, Bybit, MEXC, and Gate.io into a single interface.
2. **Paginated Data Fetching:** Implements iterative backwards-fetch with `endTime` pagination to retrieve up to 1000 candles per request while respecting API rate limits.
3. **RSI Calculation:** Leverages the `ta` library's `momentum.rsi()` with a configurable window (default 14) applied to closing prices.
4. **Symbol Combiner:** A dedicated subpage that compares symbol lists between any two exchanges, identifying unique pairs not listed elsewhere — useful for finding early-stage coins.
5. **Stateful UI (Streamlit):**
   * **Session Management:** Uses `st.session_state` to cache loaded symbol lists, avoiding redundant API calls during a session.
   * **Output Management:** Saves individual and summary Excel files to a local `output/` folder with one-click download buttons.

## ✨ Key Features
* **Multi-Exchange Support:** Connects to Binance, Bybit, MEXC, and Gate.io from a single interface.
* **Batch RSI Scanning:** Processes all USDT pairs on an exchange and ranks them by lowest RSI in one click.
* **Symbol Combiner:** Upload two exchange CSV files and instantly find symbols unique to each — exported as a combined CSV.
* **Flexible Data Range:** Fetch recent N candles or specify a target year/month.
* **Excel Export:** Generates per-symbol files and a consolidated summary ranked by lowest RSI.
* **Debug Panel:** Built-in network and API connectivity tests for troubleshooting.

## 🛠️ Tech Stack
* **Framework:** Streamlit
* **Data:** Pandas, `ta` (Technical Analysis library)
* **Exchanges:** Binance REST API, Bybit REST API, MEXC REST API, Gate.io REST API
* **Export:** OpenPyXL (Excel), CSV
* **Environment:** Python 3.11+, `python-dotenv`

## 🚀 Getting Started

### 1. Installation
```bash
pip install streamlit pandas ta requests openpyxl python-dotenv
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
BYBIT_API_KEY=your_key_here
BYBIT_API_SECRET=your_secret_here
```
> Binance and Gate.io use public endpoints — API keys are optional for klines data.

### 3. Usage
**Run the Web App:**
```bash
streamlit run app.py
```
*Select an exchange, load USDT pairs, choose an interval, and click Start Download.*

## 🔑 Key Technical Decisions
* **Unified Exchange Wrapper:** All exchange-specific logic is isolated in `exchange_wrappers.py`. Adding a new exchange only requires implementing `get_symbols()` and `get_klines()` for that exchange — the main app stays untouched.
* **Backwards Pagination:** Fetches data from newest to oldest using `endTime` instead of `startTime`, ensuring the most recent candles are always included even if the full history is incomplete.
* **Summary-Only Mode:** When scanning all USDT pairs, only a single summary Excel file is generated instead of hundreds of individual files — keeping output manageable and storage lean.
* **Rate Limit Respect:** A configurable `sleep_ms` delay between requests prevents API bans during large batch scans.

## 📁 Project Structure
```
├── app.py                    # Main Streamlit app
├── exchange_wrappers.py      # Unified exchange API layer
├── symbol_combiner_page.py   # Symbol comparison subpage
├── output/                   # Generated Excel/CSV files
├── .env                      # API credentials (not committed)
├── requirements.txt
└── Procfile                  # For cloud deployment
```

## 🛡️ License
MIT

## 👤 Developer
**Irist** – Building tools that turn raw market data into trading intelligence.
