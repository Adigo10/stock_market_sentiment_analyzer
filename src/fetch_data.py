import os
import time
import requests
from datetime import datetime, timedelta
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
        # Use session for connection pooling
        self.session = requests.Session()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request to Finnhub API"""
        url = f"{self.BASE_URL}{path}"
        params = params.copy() if params else {}
        params["token"] = self.api_key
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def _fetch_news_paginated(self, symbol: str, from_date_obj: datetime, to_date_obj: datetime, chunk_days: int = 3) -> List[Dict]:
        """
        Fetch news in time chunks to avoid hitting API limits.
        
        Args:
            symbol: Stock symbol
            from_date_obj: Start date
            to_date_obj: End date
            chunk_days: Number of days per chunk (default: 3 days)
        
        Returns:
            List of all news articles
        """
        all_news = []
        current_start = from_date_obj
        failed_chunks = 0
        
        while current_start < to_date_obj:
            current_end = min(current_start + timedelta(days=chunk_days), to_date_obj)
            
            from_str = current_start.strftime("%Y-%m-%d")
            to_str = current_end.strftime("%Y-%m-%d")
            
            try:
                chunk_news = self._get("/company-news", {
                    "symbol": symbol,
                    "from": from_str,
                    "to": to_str
                })
                all_news.extend(chunk_news)
            except Exception as e:
                failed_chunks += 1
                print(f"⚠️  Failed to fetch chunk {from_str} to {to_str}: {str(e)}")
                # Continue with next chunk instead of failing completely
            
            current_start = current_end + timedelta(days=1)
        
        # If all chunks failed, raise an error
        if failed_chunks > 0 and len(all_news) == 0:
            raise Exception(f"Failed to fetch any data: all {failed_chunks} chunk(s) failed")
        
        # If some chunks failed but we have data, warn and continue
        if failed_chunks > 0:
            print(f"⚠️  Warning: {failed_chunks} chunk(s) failed. Returning partial data.")
        
        return all_news

    def fetch_company_news(self, company_name: str) -> str:
        """
        Fetch company news by company name for the last 30 days (1 month).
        Automatically sets end date to today and start date to 30 days ago.
        Uses pagination to respect Finnhub rate limits.
        
        Args:
            company_name: Name of the company
        
        Returns:
            JSON string of deduplicated news articles.
        """
        
        # Calculate date range: end date is today, start date is 30 days ago
        to_date_obj = datetime.now()
        from_date_obj = to_date_obj - timedelta(days=30)
        
        from_date = from_date_obj.strftime("%Y-%m-%d")
        to_date = to_date_obj.strftime("%Y-%m-%d")
        
        print(f"Fetching news from {from_date} to {to_date} (last 30 days)")
        
        # Get symbol
        symbol = COMPANY_SYMBOLS.get(company_name)
        if not symbol:
            raise ValueError(f"Symbol not found for company: {company_name}")
        
        # Fetch all news in 3-day chunks (30 days = ~10 API calls)
        fetch_start = time.time()
        news = self._fetch_news_paginated(symbol, from_date_obj, to_date_obj, chunk_days=3)
        print(f"Fetched {len(news)} articles for {company_name} in {time.time() - fetch_start:.2f} seconds.")

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
    
    def close(self):
        """Close the session and cleanup resources"""
        if hasattr(self, 'session'):
            self.session.close()
