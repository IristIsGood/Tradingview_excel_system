import requests
import datetime
import json # Import json for pretty printing

def get_binance_exchange_info():
    """
    Fetches exchange information from Binance's /api/v3/exchangeInfo endpoint.
    Includes enhanced error handling and response printing for debugging.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    url = "https://api.binance.com/api/v3/exchangeInfo"
    
    print(f"Attempting to fetch data from: {url}")
    try:
        response = requests.get(url, timeout=10) # Added a timeout for robustness
        
        # Print status code for immediate feedback
        print(f"HTTP Status Code: {response.status_code}")

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status() 

        # Try to parse JSON
        data = response.json()
        print("Successfully received and parsed JSON response.")
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content (if any): {response.text}") # Print raw response for debugging
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

if __name__ == "__main__":
    exchange_info = get_binance_exchange_info()

    if exchange_info:
        print("\n--- Successfully Fetched Exchange Info ---")
        print(f"Exchange Name: {exchange_info.get('timezone', 'N/A')}") # Timezone is a common top-level key
        print(f"Number of symbols (trading pairs): {len(exchange_info.get('symbols', []))}")

        # Extract and print all symbols
        all_symbols = [s['symbol'] for s in exchange_info.get('symbols', [])]
        print("\n--- List of All Trading Symbols ---")
        # Print symbols in a more readable, column-like format if there are many
        # For simplicity, let's print them separated by commas for now.
        # If the list is very long, you might want to format it into columns.
        print(", ".join(all_symbols))
        print(f"\nTotal symbols listed: {len(all_symbols)}")
        print("-----------------------------------")


        # Print the entire exchange_info dictionary for full details (optional, can be very long)
        # print("\n--- Full Exchange Info Details (Pretty Printed) ---")
        # print(json.dumps(exchange_info, indent=2))
        # print("-------------------------------------------------")

        # Find the latest listed symbol (as done previously)
        recent_listings = []
        for symbol_info in exchange_info.get('symbols', []):
            if 'onboardDate' in symbol_info and symbol_info['onboardDate'] is not None:
                onboard_timestamp_ms = symbol_info['onboardDate']
                listing_date = datetime.datetime.fromtimestamp(onboard_timestamp_ms / 1000)
                recent_listings.append({
                    'symbol': symbol_info['symbol'],
                    'status': symbol_info['status'],
                    'onboardDate_timestamp_ms': onboard_timestamp_ms,
                    'listing_date_readable': listing_date.strftime('%Y-%m-%d %H:%M:%S UTC')
                })
        
        recent_listings.sort(key=lambda x: x['onboardDate_timestamp_ms'], reverse=True)

        if recent_listings:
            latest_listing = recent_listings[0]
            print(f"\n--- Latest Binance Listing Found ---")
            print(f"Symbol: {latest_listing['symbol']}")
            print(f"Status: {latest_listing['status']}")
            print(f"Listed On: {latest_listing['listing_date_readable']}")
            print(f"----------------------------------")
        else:
            print("\nNo symbols with 'onboardDate' found or no recent listings in the data.")

    else:
        print("\nFailed to retrieve exchange information. Please check the error messages above for details.")
