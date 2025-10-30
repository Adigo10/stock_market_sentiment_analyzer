import os
import time
import requests
from datetime import datetime, timedelta
import time
# import pandas as pd
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from dedup_news import dedup_news_articles
import json

# Load environment variables - automatically searches for .env in current and parent directories
load_dotenv()

class CompanyDataFetcher:
    """Simple wrapper to fetch financial data from Finnhub.io.

    Usage:
        api = CompanyDataFetcher()  # reads FINNHUB_API_KEY from env
        news = api.fetch_company_news('AAPL', '2024-01-01', '2024-01-10')

    The class returns parsed JSON responses from Finnhub endpoints and raises
    requests.HTTPError for non-2xx responses.

    symbols for possible stocks:
    stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH"]
    usage example - pass symbol = "NVDA" in fetch_company_news method.
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
    
    def _get_all_stocks(self) -> List[Dict[str, str]]:
        """Fetch list of all US stocks from Finnhub."""
        stocks = self._get("/stock/symbol", {"exchange": "US"})
        return [{"symbol": s["symbol"], "description": s["description"]} for s in stocks]
    
    def _find_symbol_by_company_name(self, company_name: str) -> Optional[str]:
        """Find stock symbol using Finnhub's search API."""
        # Use Finnhub's search endpoint which returns ranked results
        search_results = self._get("/search", {"q": company_name})
        
        if not search_results or "result" not in search_results:
            return None
        
        results = search_results["result"]
        if not results:
            return None
        
        # Return the first (best) result's symbol
        # Finnhub ranks results by relevance, so the first match is usually correct
        first_result = results[0]
        return first_result.get("symbol")
    
    def fetch_company_news(self, company_name: str, from_date: str, to_date: str) -> str:
        """
        Fetch company news by company name between two dates (YYYY-MM-DD).
        First finds the stock symbol by matching company name, then fetches news.
        Returns JSON string of deduplicated news articles.
        """
        # Find symbol for company name
        symbol = self._find_symbol_by_company_name(company_name)
        if not symbol:
            raise ValueError(f"Could not find stock symbol for company: {company_name}")
        
        print(f"Found symbol '{symbol}' for company '{company_name}'")
        
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
        return json.dumps({'unique_news':unique_news}, ensure_ascii=False)
