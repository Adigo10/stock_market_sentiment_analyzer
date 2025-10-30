## remove before merging
## This is a test script to verify that the FinnhubFetcher is working correctly.
## It is not part of the main application.

from fetch_data import FinnhubFetcher
import pandas as pd

if __name__ == "__main__":
    try:
        api = FinnhubFetcher()
        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH"]
        symbol = "NVDA"
        news = api.fetch_company_news(symbol, "2025-01-01", "2025-05-28")
        print("News articles fetched")

    except Exception as e:
        print(f"Error: {e}")
