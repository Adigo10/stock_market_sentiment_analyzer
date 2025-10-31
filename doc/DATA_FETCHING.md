# Data Fetching & Caching Documentation

Complete guide to the data fetching and caching system for the Stock Market Sentiment Analyzer API.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Supported Companies](#supported-companies)
4. [Caching System](#caching-system)
5. [Rate Limiting & Pagination](#rate-limiting--pagination)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Performance](#performance)
9. [Error Handling](#error-handling)

---

## Overview

The Stock Market Sentiment Analyzer fetches real-time company news from the Finnhub API, caches results in memory, and serves them through a FastAPI REST API.

### Key Features

- Fast Caching: Sub-millisecond cache hits (0.000s)
- Connection Pooling: Reuses TCP connections for better performance
- Graceful Degradation: Returns partial data if some chunks fail
- Case-Insensitive: Company names work in any case
- Smart Pagination: 3-day chunks to respect API limits

---

## System Architecture

### Data Flow

```
Client Request
     ↓
FastAPI Endpoint
     ↓
Cache Check → Cache Hit (0.000s) → Return Data
     ↓
Cache Miss
     ↓
Finnhub API (10 paginated calls)
     ↓
Deduplication (ID + Semantic)
     ↓
NLP Processing
     ↓
Save to Cache → Return Data
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| API Handler | main.py | FastAPI endpoints, request routing |
| Data Fetcher | src/fetch_data.py | Finnhub API integration, pagination |
| Cache Manager | src/cache_manager.py | In-memory caching |
| Constants | src/constants.py | Company-to-ticker mapping |

---

## Supported Companies

The system currently supports 11 companies:

| Company | Ticker |
|---------|--------|
| Apple | AAPL |
| NVIDIA | NVDA |
| Google | GOOGL |
| Microsoft | MSFT |
| Meta | META |
| Amazon | AMZN |
| Intel | INTC |
| AMD | AMD |
| Palantir | PLTR |
| C3.ai | AI |
| Tesla | TSLA |

### Case-Insensitive Lookup

All of these work identically:
- "apple" → Apple (AAPL)
- "APPLE" → Apple (AAPL)
- "Apple" → Apple (AAPL)

### Adding New Companies

Edit src/constants.py and add the company to COMPANY_SYMBOLS dictionary, then restart the server.

---

## Caching System

### Design

Simple in-memory dictionary with these characteristics:
- No external dependencies (Redis, Memcached)
- O(1) lookup time
- Clears only on server restart

### Cache Behavior

**First Request (Cache Miss)**
- Fetches data from Finnhub API
- Processes through NLP pipeline
- Saves to cache
- Returns result with status: "success"
- Typical latency: 7-9 seconds

**Second Request (Cache Hit)**
- Returns cached data immediately
- status: "success (cached)"
- Typical latency: 0.000 seconds

### When Cache Clears

Cache clears only on:
- Server restart
- Server crash
- Application shutdown

Note: Cache does NOT expire automatically. Data persists until server restart.

---

## Rate Limiting & Pagination

### Finnhub API Limits

- Calls per second: 30
- Calls per minute: 60

### Pagination Strategy

Time-based chunking:
- 30 days ÷ 3 days per chunk = 10 API calls per request

Why 3-day chunks?
- Well below rate limits (10 calls << 60/min)
- Fast enough (6-7 seconds total)
- Good balance between speed and API usage

### Fail-Fast with Partial Data

If a chunk fails, the system:
1. Logs the failure
2. Continues with remaining chunks
3. Returns partial data with warning

If all chunks fail:
- Raises exception: "Failed to fetch any data: all X chunk(s) failed"

### Connection Pooling

Uses requests.Session() to reuse TCP connections:
- 10-20% faster than creating new connections
- Reduces network overhead
- Better performance for 10 paginated calls

---

## API Endpoints

### 1. Analyze Company

POST /analyze-company

Fetch and analyze company news (with caching).

Request body:
```json
{
  "company_name": "apple"
}
```

Response (Success):
```json
{
  "company_name": "Apple",
  "news_data": "{\"unique_news\": [...]}",
  "result": {...},
  "status": "success"
}
```

Response (Cached):
```json
{
  "company_name": "Apple",
  "news_data": "{\"unique_news\": [...]}",
  "result": {...},
  "status": "success (cached)"
}
```

### 2. Get Supported Companies

GET /companies

List all available companies.

Response:
```json
{
  "companies": [
    "Apple",
    "NVIDIA",
    "Google",
    "Microsoft",
    "Meta",
    "Amazon",
    "Intel",
    "AMD",
    "Palantir",
    "C3.ai",
    "Tesla"
  ]
}
```

## Configuration

### Environment Variables

Create a .env file:

```
FINNHUB_API_KEY=your_api_key_here
```

### Getting Finnhub API Key

1. Visit https://finnhub.io/
2. Sign up for free account
3. Copy API key from dashboard
4. Add to .env file

---

## Performance

### Real-World Examples

**Apple (887 articles)**
- Fetched: 887 articles (4.07s)
- After ID dedup: 887 articles (0.00s)
- After semantic dedup: 735 articles (4.05s)
- Total latency: 8.394s
- Cache hit: 0.000s

**C3.ai (45 articles)**
- Fetched: 45 articles (3.41s)
- After ID dedup: 45 articles (0.00s)
- After semantic dedup: 35 articles (3.36s)
- Total latency: 7.275s
- Cache hit: 0.000s

### Deduplication Impact

| Company | Raw | ID Dedup | Semantic Dedup | Removed |
|---------|-----|----------|----------------|---------|
| Apple | 887 | 887 (0%) | 735 (-17.1%) | 152 |
| C3.ai | 45 | 45 (0%) | 35 (-22.2%) | 10 |
| Palantir | 441 | 441 (0%) | 309 (-29.9%) | 132 |

---

## Error Handling

### Graceful Degradation

The system continues on errors and returns partial data:

- Scenario 1: All chunks succeed → Return all data
- Scenario 2: Some chunks fail → Return partial data with warning
- Scenario 3: All chunks fail → Return error

### Common Errors

**Company Not Found**
```json
{
  "detail": "Company 'XYZ' is not supported."
}
```
Solution: Check /companies endpoint for supported companies.

**No Data Fetched**
```
Error: Failed to fetch any data: all 10 chunk(s) failed
```
Causes: Network down, API key invalid, Finnhub service down
Solution: Check network, API key, and Finnhub status.

**Timeout**
```
Failed to fetch chunk: Request timeout
```
Solution: Increase timeout in fetch_data.py or check network.

---

## Starting the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env file with FINNHUB_API_KEY

# Start server
python main.py
```

Server runs on: http://localhost:8000

---

## Quick Reference

### Key Files
- main.py - FastAPI app, routes, caching logic
- src/fetch_data.py - Finnhub API calls, pagination
- src/cache_manager.py - In-memory cache
- src/constants.py - Company-to-ticker mapping

### Key Concepts
- Cache: In-memory, clears on restart
- Pagination: 10 chunks of 3 days each
- Fail-Fast: Returns partial data on failures
- Connection Pooling: Reuses TCP connections

### Performance
- Cache hit: 0.000s (instant)
- Cache miss: 7-9s (fetch + process)
- API calls: ~10 per company

---

## References

- Finnhub API: https://finnhub.io/docs/api
- FastAPI: https://fastapi.tiangolo.com/
- Requests: https://requests.readthedocs.io/

---

Last Updated: October 31, 2025
Version: 1.0.0
