"""
Simple dictionary-based cache for company analysis data
"""
from typing import Dict, Any, Optional
from constants import COMPANY_SYMBOLS


class CacheManager:
    """
    Simple dictionary to store company analysis results.
    Initialized with all company names as keys with None values.
    Cache persists until server restart.
    """
    
    def __init__(self):
        # Initialize dictionary with all companies set to None
        self._cache: Dict[str, Optional[Dict[str, Any]]] = {
            company: None for company in COMPANY_SYMBOLS.keys()
        }
        print(f"Cache initialized with {len(self._cache)} companies")
    
    def get(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a company.
        
        Returns:
            Dict with raw_data and processed_data if cached, None otherwise
        """
        return self._cache.get(company_name)
    
    def save(self, company_name: str, raw_data: str, processed_data: Dict[str, Any]):
        """
        Save data to cache for a company.
        
        Args:
            company_name: Name of the company
            raw_data: Raw JSON string from fetcher
            processed_data: Processed result from NLP
        """
        self._cache[company_name] = {
            "raw_data": raw_data,
            "processed_data": processed_data
        }
        print(f"✓ Data saved to cache for '{company_name}'")
