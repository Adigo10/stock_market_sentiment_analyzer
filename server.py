from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
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
    max_articles: int = None  # Optional: limit returned articles (None = return all)

class FinancialNewsResponse(BaseModel):
    company_name: str
    result: List[Dict[str, Any]]  # List of ranked articles
    status: str

class APIHandler:
    def __init__(self):
        self.app = FastAPI(title="NLP Company Analysis API", version="1.0.0")
        self.fetcher = FinancialNewsFetcher()
        self.processor = FinancialDataCleaner()
        self.cache = CacheManager()  # In-memory cache
        self._setup_routes()
        self.financial_analyzer = FinancialNewsAnalyzer()
    
    def _setup_routes(self):
        self.app.post("/analyze-company", response_model=FinancialNewsResponse)(self.analyze_company)
        self.app.get("/")(self.root)
        self.app.get("/companies")(self.get_companies)
    
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
        """Analyze company: fetch news and process with NLP. Uses cache."""
        start_time = time.time()
        
        try:
            original_company_name = self._validate_company(request.company_name)
            data = await self._get_company_data(original_company_name, request.max_articles)
            
            cached_data = self.cache.get(original_company_name)
            status = "success"
            
            elapsed_time = time.time() - start_time
            print(f"✓ Request completed for '{original_company_name}' | Total Latency: {elapsed_time:.3f}s")
            
            result = self.financial_analyzer.analyze_news(data["processed_data"])

            return FinancialNewsResponse(
                company_name=original_company_name,
                result=result,
                status=status
            )
        
        except HTTPException:
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"✗ Request failed for '{request.company_name}' | Latency: {elapsed_time:.3f}s | Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
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
        if 'processed_articles' in limited_processed and max_articles is not None:
            limited_processed['processed_articles'] = limited_processed['processed_articles'][:max_articles]
        
        return limited_raw_json, limited_processed
    
    async def root(self):
        return {"message": "NLP Company Analysis API is running"}
    
    async def get_companies(self):
        """Get list of supported companies."""
        return {"companies": list(COMPANY_SYMBOLS.keys())}

# Create API handler
api_handler = APIHandler()
app = api_handler.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)