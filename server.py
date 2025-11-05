from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os
import uvicorn
import time
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_process import FinancialDataCleaner
from src.fetch_data import FinancialNewsFetcher
from src.cache_manager import CacheManager
from model_pipeline import FinancialNewsAnalyzer

from constants import COMPANY_SYMBOLS

class FinancialNewsRequest(BaseModel):
    company_name: str

class FinancialNewsResponse(BaseModel):
    company_name: str
    result: List[Dict[str, Any]]  # List of ranked articles
    status: str

class RankedArticlesResponse(BaseModel):
    company_name: str
    articles: List[Dict[str, Any]]
    count: int
    status: str

class EnrichedArticlesResponse(BaseModel):
    company_name: str
    articles: List[Dict[str, Any]]
    count: int
    status: str
    sentiment_stats: Optional[Dict[str, Any]] = None

class APIHandler:
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Sentiment Analyzer API",
            version="2.0.0",
            description="Financial news analysis with AI-powered sentiment prediction and keyphrase extraction"
        )
        
        print("\n" + "="*80)
        print("INITIALIZING STOCK MARKET SENTIMENT ANALYZER")
        print("="*80)
        
        print("📡 Initializing data fetcher...")
        self.fetcher = FinancialNewsFetcher()
        
        print("🔧 Initializing data processor...")
        self.processor = FinancialDataCleaner()
        
        print("💾 Initializing cache manager...")
        self.cache = CacheManager()  # In-memory cache
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins in development
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
        
        print("\n🤖 Initializing AI Analysis Pipeline...")
        print("-" * 80)
        try:
            self.financial_analyzer = FinancialNewsAnalyzer()
            print("-" * 80)
            print("✓ AI Analysis Pipeline initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize AI pipeline: {str(e)}")
            raise
        
        print("\n" + "="*80)
        print("✓ SERVER INITIALIZATION COMPLETE")
        print("="*80 + "\n")
    
    def _setup_routes(self):
        # Main comprehensive endpoint (backward compatible)
        self.app.post("/analyze-company", response_model=FinancialNewsResponse)(self.analyze_company)
        
        # Split endpoints for granular control
        self.app.post("/api/fetch-and-rank", response_model=RankedArticlesResponse)(self.fetch_and_rank)
        self.app.post("/api/enrich-with-ai", response_model=EnrichedArticlesResponse)(self.enrich_with_ai)
        
        # Utility endpoints
        self.app.get("/")(self.root)
        self.app.get("/companies")(self.get_companies)
        self.app.get("/health")(self.health_check)
    
    def _validate_company(self, company_name: str) -> str:
        """Validate company name and return proper casing."""
        company_name_lower = company_name.lower()
        lower_to_original = {k.lower(): k for k in COMPANY_SYMBOLS.keys()}
        
        if company_name_lower not in lower_to_original:
            raise HTTPException(status_code=400, detail=f"Company '{company_name}' is not supported.")
        
        return lower_to_original[company_name_lower]
    
    async def _fetch_and_preprocess(self, company_name: str) -> Dict[str, Any]:
        """Fetch raw news and preprocess. Returns dict with company_name, news_data, processed_data."""
        print(f"✗ No cache for '{company_name}' - fetching and processing...")
        
        raw_data_json = await self.fetcher.fetch_company_news(company_name=company_name)
        processed_data = await self._process_data_async(raw_data_json)
        self.cache.save(company_name, raw_data_json, processed_data)
        
        return {
            "company_name": company_name,
            "news_data": raw_data_json,
            "processed_data": processed_data
        }
    
    async def _get_company_data(self, company_name: str, max_articles: int = None) -> Dict[str, Any]:
        """Get data from cache or fetch & preprocess. Returns dict with company_name, news_data, processed_data."""
        cached_data = self.cache.get(company_name)
        
        if cached_data is not None:
            print(f"✓ Cache hit for '{company_name}'")
            data = {
                "company_name": company_name,
                "news_data": cached_data["raw_data"],
                "processed_data": cached_data["processed_data"]
            }
        else:
            data = await self._fetch_and_preprocess(company_name)
        
        if max_articles is not None:
            raw_data, processed_data = self._limit_articles(
                data["news_data"], data["processed_data"], max_articles
            )
            data["news_data"] = raw_data
            data["processed_data"] = processed_data
        
        return data
    
    async def analyze_company(self, request: FinancialNewsRequest):
        """
        Analyze company: fetch news, process with NLP, predict sentiment, and analyze keyphrases.
        
        Complete Pipeline:
        1. Fetch & preprocess data (cached if available)
        2. Rule-based ranking of articles
        3. Similarity expansion to select top articles
        4. Sentiment prediction using Flan-T5 model
        5. Keyphrase extraction and analysis
        
        Returns enriched articles with sentiment and keyphrases.
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate company name
            original_company_name = self._validate_company(request.company_name)
            
            # Step 2: Get data (cached or fetch & preprocess)
            data = await self._get_company_data(original_company_name, 250)
            print(f"📰 Processing {len(data['processed_data']['unique_news'])} articles for '{original_company_name}'")
            
            # Step 3: Run complete analysis pipeline
            # This includes: ranking → similarity → sentiment prediction → keyphrase analysis
            print(f"\n{'='*80}")
            print(f"RUNNING COMPLETE ANALYSIS PIPELINE FOR '{original_company_name}'")
            print(f"{'='*80}")
            
            result = self.financial_analyzer.analyze_news(data["processed_data"], original_company_name)
            
            # Log completion
            elapsed_time = time.time() - start_time
            print(f"\n{'='*80}")
            print(f"✓ REQUEST COMPLETED FOR '{original_company_name}'")
            print(f"  Total Latency: {elapsed_time:.3f}s")
            print(f"  Articles Returned: {len(result)}")
            print(f"  Cache Status: {'HIT' if self.cache.get(original_company_name) else 'MISS'}")
            print(f"{'='*80}\n")
            
            status = "success"

            return FinancialNewsResponse(
                company_name=original_company_name,
                result=result,
                status=status
            )
        
        except HTTPException:
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"\n{'='*80}")
            print(f"✗ REQUEST FAILED FOR '{request.company_name}'")
            print(f"  Error Type: {error_type}")
            print(f"  Error Message: {error_msg}")
            print(f"  Latency: {elapsed_time:.3f}s")
            print(f"{'='*80}\n")
            
            # Provide more specific error messages based on error type
            if "Model directory not found" in error_msg:
                detail = "Sentiment prediction model not found. Please ensure model files are available."
            elif "CUDA" in error_msg or "out of memory" in error_msg.lower():
                detail = "GPU memory error. Try reducing batch size or using CPU."
            elif "fetch" in error_msg.lower() or "api" in error_msg.lower():
                detail = f"Failed to fetch news data: {error_msg}"
            else:
                detail = f"Processing failed: {error_msg}"
            
            raise HTTPException(status_code=500, detail=detail)
    
    async def fetch_and_rank(self, request: FinancialNewsRequest):
        """
        Step 1 & 2: Fetch news, preprocess, and rank articles.
        Returns top 15 ranked articles without AI enrichment.
        """
        start_time = time.time()
        
        try:
            # Validate company name
            original_company_name = self._validate_company(request.company_name)
            
            # Get data (cached or fetch & preprocess)
            data = await self._get_company_data(original_company_name, 250)
            print(f"📰 Fetched {len(data['processed_data']['unique_news'])} articles for '{original_company_name}'")
            
            # Run ranking and similarity expansion
            print(f"\n{'='*80}")
            print(f"STEP 1-3: RANKING & SIMILARITY EXPANSION FOR '{original_company_name}'")
            print(f"{'='*80}")
            
            import pandas as pd
            from src.rule_based_ranker import FinancialNewsRanker
            
            # Rank articles
            ranker = FinancialNewsRanker(decay_rate=0.1, target_company=original_company_name)
            df = pd.DataFrame(data["processed_data"]["unique_news"])
            ranked_df = ranker.rank_articles(df, top_n=None)
            
            # Get top 15
            top_articles = ranked_df[:15].to_dict(orient="records")
            
            elapsed_time = time.time() - start_time
            print(f"\n✓ Ranking completed in {elapsed_time:.3f}s")
            print(f"  Top articles: {len(top_articles)}\n")
            
            return RankedArticlesResponse(
                company_name=original_company_name,
                articles=top_articles,
                count=len(top_articles),
                status="success"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"✗ Fetch and rank failed: {str(e)} | Latency: {elapsed_time:.3f}s")
            raise HTTPException(status_code=500, detail=f"Fetch and rank failed: {str(e)}")
    
    async def enrich_with_ai(self, request: FinancialNewsRequest):
        """
        Complete pipeline: Fetch, rank, and enrich with AI (sentiment + keyphrases).
        This is the main endpoint that should be used by the frontend.
        """
        start_time = time.time()
        
        try:
            # Validate company name
            original_company_name = self._validate_company(request.company_name)
            
            # Get data (cached or fetch & preprocess)
            data = await self._get_company_data(original_company_name, 250)
            print(f"📰 Processing {len(data['processed_data']['unique_news'])} articles for '{original_company_name}'")
            
            # Run complete analysis pipeline
            print(f"\n{'='*80}")
            print(f"RUNNING COMPLETE AI ANALYSIS FOR '{original_company_name}'")
            print(f"{'='*80}")
            
            result = self.financial_analyzer.analyze_news(data["processed_data"], original_company_name)
            
            # Calculate sentiment statistics
            sentiment_stats = {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'total_keyphrases': 0
            }
            
            for article in result:
                # Parse sentiment
                pred_sent = article.get('predicted_sentiment', '')
                # Split by the first occurrence of "Reason:"
                parts = pred_sent.split("Reason:", 1)

                # Extract sentiment (remove "Sentiment:" prefix and clean up)
                sentiment = parts[0].replace("Sentiment:", "").strip().rstrip('.')

                # Extract reason
                reason = parts[1].strip() if len(parts) > 1 else ""

                # Create dictionary
                sent_dict = {
                    "sentiment": sentiment,
                    "reason": reason
                }
                print(sent_dict)
                if 'Good' in sent_dict["sentiment"]:
                    sentiment_stats['positive'] += 1
                elif 'Bad' in sent_dict["sentiment"]:
                    sentiment_stats['negative'] += 1
                else:
                    sentiment_stats['neutral'] += 1
                
                # Count keyphrases
                ka = article.get('keyphrase_analysis', {})
                summary = ka.get('summary', {})
                sentiment_stats['total_keyphrases'] += summary.get('total_phrases', 0)
            
            elapsed_time = time.time() - start_time
            print(f"\n{'='*80}")
            print(f"✓ COMPLETE ANALYSIS DONE FOR '{original_company_name}'")
            print(f"  Total Latency: {elapsed_time:.3f}s")
            print(f"  Articles: {len(result)}")
            print(f"  Positive: {sentiment_stats['positive']}, Negative: {sentiment_stats['negative']}, Neutral: {sentiment_stats['neutral']}")
            print(f"{'='*80}\n")
            
            return EnrichedArticlesResponse(
                company_name=original_company_name,
                articles=result,
                count=len(result),
                status="success",
                sentiment_stats=sentiment_stats
            )
        
        except HTTPException:
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"\n{'='*80}")
            print(f"✗ AI ENRICHMENT FAILED FOR '{request.company_name}'")
            print(f"  Error Type: {error_type}")
            print(f"  Error Message: {error_msg}")
            print(f"  Latency: {elapsed_time:.3f}s")
            print(f"{'='*80}\n")
            
            raise HTTPException(status_code=500, detail=f"AI enrichment failed: {error_msg}")
    
    async def _process_data_async(self, raw_data_json: str):
        ## Implement NLP processing logic here
        processed_data = self.processor.process_json_file(
            input_file=raw_data_json, 
            output_file="processed_output.json"
        )
        return processed_data
    
    def _limit_articles(self, raw_data_json: str, processed_data: Dict[str, Any], max_articles: int):
        """Limit articles to first max_articles (0 to max_articles-1)."""
        import json
        
        raw_data = json.loads(raw_data_json)
        if 'unique_news' in raw_data and max_articles is not None:
            raw_data['unique_news'] = raw_data['unique_news'][:max_articles]
        limited_raw_json = json.dumps(raw_data, ensure_ascii=False)
        
        limited_processed = processed_data.copy()
        # Fixed: Check for 'unique_news' instead of 'processed_articles'
        if 'unique_news' in limited_processed and max_articles is not None:
            limited_processed['unique_news'] = limited_processed['unique_news'][:max_articles]
        
        return limited_raw_json, limited_processed
    
    async def root(self):
        return {
            "message": "Stock Market Sentiment Analyzer API",
            "version": "2.0.0",
            "features": [
                "Financial news data fetching",
                "Rule-based article ranking",
                "Similarity-based expansion",
                "AI sentiment prediction (Flan-T5)",
                "Keyphrase extraction & analysis"
            ],
            "endpoints": {
                "POST /api/enrich-with-ai": "⭐ RECOMMENDED: Complete AI analysis (fetch + rank + sentiment + keyphrases)",
                "POST /api/fetch-and-rank": "Fetch and rank articles only (no AI)",
                "POST /analyze-company": "Legacy: Complete analysis (backward compatible)",
                "GET /companies": "List supported companies",
                "GET /health": "Health check status"
            },
            "usage": {
                "recommended": "Use /api/enrich-with-ai for complete analysis with all features",
                "quick": "Use /api/fetch-and-rank for quick article list without AI processing"
            }
        }
    
    async def get_companies(self):
        """Get list of supported companies."""
        return {
            "companies": list(COMPANY_SYMBOLS.keys()),
            "total": len(COMPANY_SYMBOLS)
        }
    
    async def health_check(self):
        """Health check endpoint to verify all components are working."""
        health_status = {
            "status": "healthy",
            "version": "2.0.0",
            "components": {}
        }
        
        try:
            # Check data fetcher
            health_status["components"]["data_fetcher"] = "operational"
            
            # Check processor
            health_status["components"]["data_processor"] = "operational"
            
            # Check cache
            health_status["components"]["cache_manager"] = "operational"
            
            # Check AI analyzer
            if hasattr(self, 'financial_analyzer'):
                # Check sentiment predictor
                if hasattr(self.financial_analyzer, 'sentiment_predictor'):
                    device = self.financial_analyzer.sentiment_predictor.device
                    health_status["components"]["sentiment_predictor"] = f"operational ({device})"
                else:
                    health_status["components"]["sentiment_predictor"] = "not initialized"
                
                # Check keyphrase analyzer
                if hasattr(self.financial_analyzer, 'keyphrase_analyzer'):
                    health_status["components"]["keyphrase_analyzer"] = "operational"
                else:
                    health_status["components"]["keyphrase_analyzer"] = "not initialized"
            else:
                health_status["components"]["ai_pipeline"] = "not initialized"
                health_status["status"] = "degraded"
            
            # Cache statistics
            cache_stats = {
                "cached_companies": len(self.cache.cache) if hasattr(self.cache, 'cache') else 0
            }
            health_status["cache_stats"] = cache_stats
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status

# Create API handler
api_handler = APIHandler()
app = api_handler.app

if __name__ == "__main__":
    # Increased timeouts for development
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,  # 5 minutes
        timeout_graceful_shutdown=30
    )