import requests
from typing import Dict, List
import streamlit as st
from time import sleep
from config import (
    SERPAPI_API_KEY,
    SERPAPI_BASE_URL,
    SEARCH_RESULTS_PER_QUERY,
    SEARCH_REGION,
    RATE_LIMIT_DELAY
)

class SearchEngine:
    """Handles web searches using SerpAPI"""
    
    def __init__(self):
        self.api_key = SERPAPI_API_KEY
        if not self.api_key:
            st.error("SERPAPI_KEY not found in environment variables!")
        self.base_url = SERPAPI_BASE_URL
        
    def search(self, entity: str, prompt: str) -> List[Dict]:
        """Execute search for an entity using the provided prompt"""
        try:
            query = prompt.replace("{company}", str(entity))
            
            params = {
                "engine": "google",
                "api_key": self.api_key,
                "q": query,
                "num": SEARCH_RESULTS_PER_QUERY,
                "gl": SEARCH_REGION
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            results = response.json()
            search_results = []
            
            if "error" in results:
                st.warning(f"Search API error: {results['error']}")
                return []
                
            if "organic_results" in results:
                for result in results["organic_results"]:
                    search_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                        "position": result.get("position", 0)
                    })
            
            sleep(RATE_LIMIT_DELAY)  # Rate limiting
            return search_results
            
        except Exception as e:
            st.error(f"Search error for {entity}: {str(e)}")
            return []