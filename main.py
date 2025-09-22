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

from src.data_process import DataCleaner
from src.fetch_data import CompanyDataFetcher  

class CompanyRequest(BaseModel):
    company_name: str

class CompanyResponse(BaseModel):
    company_name: str
    result: Dict[str, Any]
    status: str

class APIHandler:
    def __init__(self):
        self.app = FastAPI(title="NLP Company Analysis API", version="1.0.0")
        self.fetcher = CompanyDataFetcher()
        self.processor = DataCleaner()
        self._setup_routes()
    
    def _setup_routes(self):
        self.app.post("/analyze-company", response_model=CompanyResponse)(self.analyze_company)
        self.app.get("/")(self.root)
    
    async def analyze_company(self, request: CompanyRequest):
        """
        Analyze a company using NLP processing
        """
        try:
            # Fetch and process company data
            raw_data = await self._fetch_data_async(request.company_name)
            result = await self._process_data_async(raw_data)
            
            return CompanyResponse(
                company_name=request.company_name,
                result=result,
                status="success"
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    async def root(self):
        return {"message": "NLP Company Analysis API is running"}

# Create API handler instance
    company_name: str

class CompanyResponse(BaseModel):
    company_name: str
    result: Dict[str, Any]
    status: str

# Create API handler instance
api_handler = APIHandler()
app = api_handler.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)