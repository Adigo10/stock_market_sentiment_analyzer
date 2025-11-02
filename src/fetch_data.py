import os
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from dedup_news import dedup_news_articles
import json
from constants import COMPANY_SYMBOLS

load_dotenv()


class FinancialNewsFetcher:
    """Async wrapper to fetch financial data from Finnhub.io using parallel requests.

    Usage:
        api = FinancialNewsFetcher()  # reads FINNHUB_API_KEY from env
        news = await api.fetch_company_news('AAPL')

    The class returns parsed JSON responses from Finnhub endpoints
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(
        self, api_key: Optional[str] = None, timeout: int = 60
    ):  # Increased to 60 seconds for development
        api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError(
                "Finnhub API key not provided. Set FINNHUB_API_KEY in the environment or pass api_key to the constructor."
            )
        self.api_key = api_key
        self.timeout = timeout

    async def _get(
        self,
        session: aiohttp.ClientSession,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make async GET request to Finnhub API"""
        url = f"{self.BASE_URL}{path}"
        params = params.copy() if params else {}
        params["token"] = self.api_key

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with session.get(url, params=params, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _fetch_single_chunk(
        self, session: aiohttp.ClientSession, symbol: str, from_str: str, to_str: str
    ) -> tuple[List[Dict], Optional[str]]:
        """
        Fetch a single chunk of news data asynchronously.

        Returns:
            Tuple of (news_list, error_message)
        """
        try:
            chunk_news = await self._get(
                session,
                "/company-news",
                {"symbol": symbol, "from": from_str, "to": to_str},
            )
            return (chunk_news, None)
        except Exception as e:
            error_msg = f"Failed to fetch chunk {from_str} to {to_str}: {str(e)}"
            return ([], error_msg)

    async def _fetch_news_paginated(
        self,
        symbol: str,
        from_date_obj: datetime,
        to_date_obj: datetime,
        chunk_days: int = 3,
    ) -> List[Dict]:
        """
        Fetch news in time chunks using async parallel requests.
        Fetches in REVERSE chronological order (latest data first, then go backwards).

        Args:
            symbol: Stock symbol
            from_date_obj: Start date (oldest)
            to_date_obj: End date (most recent)
            chunk_days: Number of days per chunk (default: 3 days)

        Returns:
            List of all news articles
        """

        chunks = []
        current_end = to_date_obj

        while current_end > from_date_obj:
            current_start = max(current_end - timedelta(days=chunk_days), from_date_obj)
            from_str = current_start.strftime("%Y-%m-%d")
            to_str = current_end.strftime("%Y-%m-%d")
            chunks.append((from_str, to_str))
            current_end = current_start - timedelta(days=1)

        # Fetch all chunks in parallel with increased connection limits
        connector = aiohttp.TCPConnector(limit=30, limit_per_host=30)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                self._fetch_single_chunk(session, symbol, from_str, to_str)
                for from_str, to_str in chunks
            ]
            results = await asyncio.gather(*tasks)

        # Process results
        all_news = []
        failed_chunks = 0

        for news_list, error_msg in results:
            if error_msg:
                failed_chunks += 1
                print(f"⚠️  {error_msg}")
            else:
                all_news.extend(news_list)

        # If all chunks failed, raise an error
        if failed_chunks > 0 and len(all_news) == 0:
            raise Exception(
                f"Failed to fetch any data: all {failed_chunks} chunk(s) failed"
            )

        # If some chunks failed but we have data, warn and continue
        if failed_chunks > 0:
            print(
                f"⚠️  Warning: {failed_chunks} chunk(s) failed. Returning partial data."
            )

        return all_news

    async def fetch_company_news(self, company_name: str) -> str:
        """
        Fetch company news by company name for the last 30 days (1 month).
        Automatically sets end date to today and start date to 30 days ago.
        Uses async parallel pagination for maximum speed.

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

        print(
            f"Fetching news from {from_date} to {to_date} (last 30 days) with async parallel requests"
        )

        # Get symbol
        symbol = COMPANY_SYMBOLS.get(company_name)
        if not symbol:
            raise ValueError(f"Symbol not found for company: {company_name}")

        # Fetch all news in 3-day chunks (30 days = ~10 API calls) in parallel
        fetch_start = time.time()
        news = await self._fetch_news_paginated(
            symbol, from_date_obj, to_date_obj, chunk_days=3
        )
        print(
            f"Fetched {len(news)} articles for {company_name} in {time.time() - fetch_start:.2f} seconds."
        )

        # Deduplicate by article ID
        dedup_start = time.time()
        seen_ids = set()
        deduped_news = []
        for article in news:
            aid = article.get("id")
            if aid not in seen_ids:
                seen_ids.add(aid)
                deduped_news.append(article)
        print(
            f"After ID deduplication: {len(deduped_news)} articles. Took {time.time() - dedup_start:.2f} seconds."
        )

        # Semantic deduplication
        semantic_start = time.time()
        unique_news = dedup_news_articles(deduped_news)
        print(
            f"After semantic deduplication: {len(unique_news)} unique articles. Took {time.time() - semantic_start:.2f} seconds."
        )

        # Convert 'datetime' field from UNIX to YYYY-MM-DD string
        for article in unique_news:
            dt = article.get("datetime")
            if isinstance(dt, (int, float)):
                try:
                    article["datetime"] = datetime.utcfromtimestamp(dt).strftime(
                        "%Y-%m-%d"
                    )
                except Exception:
                    pass

        result = {"unique_news": unique_news}

        return json.dumps(result, ensure_ascii=False)
