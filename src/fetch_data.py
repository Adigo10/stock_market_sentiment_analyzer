import os
import time
import requests
from datetime import datetime, timedelta
import time
import pandas as pd
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from dedup_news import dedup_news_articles
import json

# Load environment variables from .env if present
load_dotenv(dotenv_path='.env')


class FinnhubFetcher:
    """Simple wrapper to fetch financial data from Finnhub.io.

    Usage:
        api = FinnhubFetcher()  # reads FINNHUB_API_KEY from env
        news = api.fetch_company_news('AAPL', '2024-01-01', '2024-01-10')

    The class returns parsed JSON responses from Finnhub endpoints and raises
    requests.HTTPError for non-2xx responses.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("Finnhub API key not provided. Set FINNHUB_API_KEY in the environment or pass api_key to the constructor.")
        self.api_key = api_key
        self.timeout = timeout

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL}{path}"
        params = params.copy() if params else {}
        params["token"] = self.api_key
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    def fetch_company_news(self, symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """Fetch company news between two dates (YYYY-MM-DD) in a single call, deduplicate by article ID and then semantically."""
        # Validate dates
        try:
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("from_date and to_date must be in YYYY-MM-DD format")

        # Fetch all news
        fetch_start = time.time()
        news = self._get("/company-news", {"symbol": symbol, "from": from_date, "to": to_date})
        print(f"Fetched {len(news)} articles for {symbol} from Finnhub in {time.time() - fetch_start:.2f} seconds.")

        # Deduplicate by article ID
        dedup_start = time.time()
        seen_ids = set()
        deduped_news = []
        for article in news:
            aid = article.get('id')
            if aid not in seen_ids:
                seen_ids.add(aid)
                deduped_news.append(article)
        print(f"After ID deduplication: {len(deduped_news)} articles. Took {time.time() - dedup_start:.2f} seconds.")

        # Semantic deduplication
        semantic_start = time.time()
        unique_news = dedup_news_articles(deduped_news)
        print(f"After semantic deduplication: {len(unique_news)} unique articles. Took {time.time() - semantic_start:.2f} seconds.")

        # Convert 'datetime' field from UNIX to YYYY-MM-DD string
        for article in unique_news:
            dt = article.get('datetime')
            if isinstance(dt, (int, float)):
                try:
                    article['datetime'] = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d')
                except Exception:
                    pass

        return json.dumps(unique_news, ensure_ascii=False)
    
    def fetch_stocks(self) -> List[Dict[str, Any]]:
        """Fetch list of stocks from Finnhub."""
        stocks = self._get("/stock/symbol", {"exchange": "US"})
        # keep only symbol and description
        stocks = [{"symbol": s["symbol"], "description": s["description"]} for s in stocks]
        return json.dumps(stocks, ensure_ascii=False)