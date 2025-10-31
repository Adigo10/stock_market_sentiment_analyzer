import os
import time
import requests
from datetime import datetime, timedelta
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from dedup_news import dedup_news_articles
import json
from constants import COMPANY_SYMBOLS

load_dotenv()

class CompanyDataFetcher:
    """Simple wrapper to fetch financial data from Finnhub.io.

    Usage:
        api = CompanyDataFetcher()  # reads FINNHUB_API_KEY from env
        news = api.fetch_company_news('AAPL')

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
    
    def fetch_company_news(self, company_name: str) -> str:
        """
        Fetch company news by company name for the last 30 days (1 month).
        Automatically sets end date to today and start date to 30 days ago.
        
        Args:
            company_name: Name of the company
            symbol: Stock symbol (optional). If None, will use search API to find it.
        
        Returns:
            JSON string of deduplicated news articles.
        """
        # Calculate date range: end date is today, start date is 30 days ago
        to_date_obj = datetime.now()
        from_date_obj = to_date_obj - timedelta(days=30)
        
        # Format dates as strings
        from_date = from_date_obj.strftime("%Y-%m-%d")
        to_date = to_date_obj.strftime("%Y-%m-%d")
        
        print(f"Fetching news from {from_date} to {to_date} (last 30 days)")
        
        # Fetch all news
        fetch_start = time.time()
        news = self._get("/company-news", {"symbol": COMPANY_SYMBOLS.get(company_name), "from": from_date, "to": to_date})
        print(f"Fetched {len(news)} articles for {company_name} from Finnhub in {time.time() - fetch_start:.2f} seconds.")

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

        result = {'unique_news': unique_news}
        
        return json.dumps(result, ensure_ascii=False)
