from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os
import uvicorn
from pathlib import Path

# Get the absolute path of the current file's directory
current_dir = Path(__file__).parent.absolute()

# Add src directory to path using absolute path
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))
# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_process import FinancialDataCleaner
from src.fetch_data import CompanyDataFetcher

from constants import COMPANY_SYMBOLS

class CompanyRequest(BaseModel):
    company_name: str

class CompanyResponse(BaseModel):
    company_name: str
    news_data: str  # JSON string of deduplicated news
    result: Dict[str, Any]
    status: str

class APIHandler:
    def __init__(self):
        self.app = FastAPI(title="NLP Company Analysis API", version="1.0.0")
        self.fetcher = CompanyDataFetcher()
        self.processor = FinancialDataCleaner()
        self._setup_routes()
    
    def _setup_routes(self):
        self.app.post("/analyze-company", response_model=CompanyResponse)(self.analyze_company)
        self.app.get("/")(self.root)
        self.app.get("/companies")(self.get_companies)
    
    async def analyze_company(self, request: CompanyRequest):
        """
        Analyze a company: fetch news data and process with NLP
        """
        try:
            # Fetch company news (returns JSON string)
            # Automatically fetches news from last 30 days
            # If symbol is None, fetch_company_news will use search API
            raw_data_json = self.fetcher.fetch_company_news(
                company_name=request.company_name,
            )
            
            result = await self._process_data_async(raw_data_json)
            
            
            return CompanyResponse(
                company_name=request.company_name,
                news_data=raw_data_json, # this is the raw (unprocessed) news data. can be used for debugging.
                result=result,
                status="success"
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    async def _process_data_async(self, raw_data_json: str):
        ## Implement NLP processing logic here
        result = self.processor.process_json_file(
                            input_file = raw_data_json, output_file="processed_output.json"
                            )
        return result
    
    async def root(self):
        return {"message": "NLP Company Analysis API is running"}
    
    async def get_companies(self):
        """
        Get the list of supported companies
        Returns only company names (keys from COMPANY_SYMBOLS mapping)
        """
        return {
            "companies": list(COMPANY_SYMBOLS.keys())
        }

# Create API handler instance
api_handler = APIHandler()
app = api_handler.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)