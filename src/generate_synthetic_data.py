"""Fetch real AI company news via DeepSeek API and generate sentiment CSV.

Output format is a CSV with two columns:
1. source: The actual news text fetched from the web
2. sentiment: Formatted as <senti>Good/Bad/Neutral<reason>description

Usage (example):
    python src/generate_synthetic_data.py --n 10 --out data/ai_stock_sentiment.csv

The script reads the deepseeker_api_key from the .env file.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple

import requests
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

AI_COMPANIES = [
    "OpenAI",
    "NVIDIA",
    "Google",
    "Microsoft",
    "Meta",
    "Amazon",
    "Intel",
    "AMD",
    "Palantir",
    "C3.ai",
    "Anthropic",
    "Tesla",
]


def get_api_key() -> str:
    """Load the DeepSeek API key from environment."""
    api_key = os.getenv("deepseeker_api_key")
    if not api_key:
        raise ValueError(
            "deepseeker_api_key not found in .env file. "
            "Please add it: deepseeker_api_key=your_key_here"
        )
    return api_key


def fetch_news_and_sentiment(
    api_key: str, companies: List[str], count: int
) -> List[Tuple[str, str, str]]:
    """Call DeepSeek API with web search to fetch news articles and classify sentiment.

    Returns a list of tuples: (source_name, article_summary, sentiment_formatted)
    where sentiment_formatted is: <senti>Good/Bad/Neutral<reason>...
    """
    # Build a prompt that asks the model to search for recent news and return structured output
    company_list = ", ".join(companies)

    system_prompt = (
        "You are an AI assistant that searches the web for recent news articles about companies "
        "and analyzes the sentiment impact on their stock prices. "
        "For each news article, return EXACTLY one line in this format:\n"
        "<source_name>Publication Name<article>Comprehensive summary of the article content (3-5 sentences)<senti>Good/Bad/Neutral<reason>Brief analysis\n\n"
        "Rules:\n"
        "- Each line MUST start with <source_name> containing the publication name (e.g., Reuters, Bloomberg, TechCrunch)\n"
        "- Then <article> containing a comprehensive 3-5 sentence summary of the FULL article content, not just the headline\n"
        "- Then <senti> with one of: Good, Bad, or Neutral (capitalize first letter)\n"
        "- Then <reason> with a brief analysis of stock impact (1-2 sentences)\n"
        "- Do NOT include any other text, explanations, or numbering\n"
        "- Format: <source_name>name<article>summary<senti>sentiment<reason>analysis"
    )

    user_prompt = (
        f"Search the web for the latest {count} news articles from 2025 ONLY about these AI-related companies: {company_list}. "
        f"Focus on articles from 2025 that could impact stock prices (earnings, partnerships, products, layoffs, regulations, etc.). "
        f"For each article:\n"
        f"1. Identify the publication name in <source_name>\n"
        f"2. Read the full article and write a comprehensive 3-5 sentence summary in <article>\n"
        f"3. Determine if it's Good (positive), Bad (negative), or Neutral for the stock price in <senti>\n"
        f"4. Provide brief stock impact analysis in <reason>\n\n"
        f"Return exactly {count} lines, each formatted as: <source_name>publication<article>detailed summary<senti>sentiment<reason>analysis"
    )

    payload = {
        "model": "deepseek-v3-1-250821",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    print("Calling DeepSeek API to fetch news...")
    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"API call failed with status {response.status_code}: {response.text}"
        )

    result = response.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Parse the response to extract source name, article summary, and sentiment
    rows = parse_news_and_sentiment(content)

    if not rows:
        print("Warning: No valid news items found in API response.")
        print(f"Raw response:\n{content}\n")

    return rows


def parse_news_and_sentiment(text: str) -> List[Tuple[str, str, str]]:
    """Extract source name, article summary, and sentiment from API response.

    Returns list of tuples: (source_name, article_summary, sentiment_formatted)
    """
    # Pattern to match: <source_name>name<article>summary<senti>sentiment<reason>reason
    pattern = r"<source_name>(.+?)<article>(.+?)<senti>(Good|Bad|Neutral)<reason>(.+?)(?=<source_name>|$)"

    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    rows = []
    for source_name, article, sentiment, reason in matches:
        # Clean up source name
        source_name = source_name.strip().replace("\n", " ").replace("\r", "")
        source_name = re.sub(r"\s+", " ", source_name)

        # Clean up article summary
        article = article.strip().replace("\n", " ").replace("\r", "")
        article = re.sub(r"\s+", " ", article)

        # Normalize sentiment capitalization
        sentiment = sentiment.capitalize()

        # Clean up reason
        reason = reason.strip().replace("\n", " ").replace("\r", "")
        reason = re.sub(r"\s+", " ", reason)

        # Format sentiment column as: <senti>sentiment<reason>reason
        sentiment_formatted = f"<senti>{sentiment}<reason>{reason}"

        rows.append((source_name, article, sentiment_formatted))

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch AI company news via DeepSeek API and generate sentiment lines"
    )
    parser.add_argument(
        "--n",
        type=int,
        default=10,
        help="Number of news items to fetch per API call (default: 10)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="data/ai_stock_sentiment.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--companies",
        type=str,
        nargs="+",
        default=None,
        help="Optional list of companies to focus on (overrides default list)",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=None,
        help="Total number of rows to generate (will make multiple API calls if needed)",
    )
    args = parser.parse_args()

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Use custom companies if provided
    companies = args.companies if args.companies else AI_COMPANIES

    # Ensure output directory exists
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Check if file exists to determine if we need to write header
    file_exists = os.path.exists(args.out)

    # Write header if file doesn't exist
    if not file_exists:
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["source_name", "source", "sentiment"])
        print(f"✓ Created new file: {args.out}\n")
    else:
        print(f"✓ Appending to existing file: {args.out}\n")

    # Determine total rows to generate
    total_rows = args.total if args.total else args.n
    items_per_call = args.n

    # Fetch news and sentiment (make multiple calls if needed)
    total_saved = 0
    remaining = total_rows
    call_count = 0

    while remaining > 0:
        call_count += 1
        batch_size = min(remaining, items_per_call)

        print(
            f"[Call {call_count}] Fetching {batch_size} items (Total progress: {total_saved}/{total_rows})..."
        )

        try:
            rows = fetch_news_and_sentiment(api_key, companies, batch_size)
            if rows:
                # Save to CSV immediately after each successful API call
                with open(args.out, "a", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    for source_name, article_summary, sentiment in rows:
                        writer.writerow([source_name, article_summary, sentiment])

                total_saved += len(rows)
                remaining -= len(rows)
                print(f"  ✓ Successfully fetched and saved {len(rows)} items")
            else:
                print(f"  ⚠ No items returned in this batch")
                remaining -= batch_size  # Still decrement to avoid infinite loop
        except Exception as e:
            print(f"  ✗ Error fetching news: {e}")
            # Continue with next batch instead of failing completely
            remaining -= batch_size

    if total_saved == 0:
        print("\nNo news items generated. Exiting.")
        return

    print(f"\n{'='*60}")
    print(f"✓ Generation complete!")
    print(f"  Total items saved: {total_saved}")
    print(f"  Output file: {args.out}")
    print(
        f"  Columns: source_name (publication) | source (article summary) | sentiment (<senti>...<reason>...)"
    )
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
