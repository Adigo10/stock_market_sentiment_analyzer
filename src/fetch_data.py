import json
import openai
from datetime import datetime
from typing import Dict, List, Any

class CompanyDataFetcher:
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
    
    def fetch_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Fetch latest news, forum discussions, and social media posts about a company
        
        Args:
            company_name (str): Name of the company to search for
            
        Returns:
            Dict: JSON-formatted data containing fetched information
        """
        try:
            # Create search queries for different content types
            queries = [
                f"{company_name} latest news 2024",
                f"{company_name} forum discussion reddit",
                f"{company_name} social media posts trending"
            ]
            
            results = {
                "company": company_name,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "news": [],
                    "forum_discussions": [],
                    "social_media_posts": []
                }
            }
            
            # Use GPT with browser search for each query type
            for i, query in enumerate(queries):
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that searches the web for company information. Provide structured data about the company."
                        },
                        {
                            "role": "user",
                            "content": f"Search for: {query}. Provide top 5 relevant results with titles, sources, and brief summaries."
                        }
                    ],
                    tools=[{
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for information"
                        }
                    }]
                )
                
                # Parse response and categorize
                content = response.choices[0].message.content
                
                if i == 0:  # News
                    results["data"]["news"] = self._parse_search_results(content)
                elif i == 1:  # Forum discussions
                    results["data"]["forum_discussions"] = self._parse_search_results(content)
                else:  # Social media
                    results["data"]["social_media_posts"] = self._parse_search_results(content)
            
            # Save to JSON file
            filename = f"{company_name.replace(' ', '_')}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return results
            
        except Exception as e:
            return {"error": f"Failed to fetch data: {str(e)}"}
    
    def _parse_search_results(self, content: str) -> List[Dict[str, str]]:
        """Parse search results from GPT response"""
        # Simple parsing logic - in practice, you'd want more sophisticated parsing
        results = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip() and ('http' in line or 'www' in line):
                results.append({
                    "title": line.strip()[:100],
                    "summary": line.strip(),
                    "source": "web_search"
                })
        
        return results[:5]  # Return top 5 results