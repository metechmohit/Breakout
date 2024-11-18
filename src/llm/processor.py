import requests
from typing import Dict, List
import streamlit as st
from time import sleep
from config import (
    GROQ_API_KEY,
    GROQ_API_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    RATE_LIMIT_DELAY,
    MAX_RETRIES
)

class LLMProcessor:
    """Handles interaction with Groq LLM API"""
    
    def __init__(self):
        self.api_key = GROQ_API_KEY
        if not self.api_key:
            st.error("GROQ_API_KEY not found in environment variables!")
        self.api_url = GROQ_API_URL
        
    def process_multiple_fields(self, entity: str, prompts: List[str], search_results: List[Dict]) -> Dict[str, str]:
        """Process multiple extraction prompts"""
        results = {}
        for prompt in prompts:
            results[prompt] = self.process(entity, prompt, search_results)
        return results
        
    def process(self, entity: str, prompt: str, search_results: List[Dict]) -> str:
        """Process search results using LLM"""
        try:
            context = "\n".join([
                f"Title: {result['title']}\nSnippet: {result['snippet']}\nURL: {result['link']}"
                for result in search_results
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an AI assistant specialized in extracting specific information from web search results. 
                    Provide concise, accurate responses focused only on the requested information. If multiple pieces of 
                    information are requested, separate them clearly."""
                },
                {
                    "role": "user",
                    "content": f"""
                    From these search results about {entity}, extract the information requested by: {prompt}
                    
                    Search Results:
                    {context}
                    
                    Provide only the extracted information without explanation.
                    If the information is not found, respond with "Information not found."
                    For multiple fields, separate them with semicolons.
                    """
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": LLM_TEMPERATURE,
                "max_tokens": LLM_MAX_TOKENS
            }
            
            for attempt in range(MAX_RETRIES):
                try:
                    response = requests.post(self.api_url, headers=headers, json=data)
                    response.raise_for_status()
                    result = response.json()
                    extracted_info = result["choices"][0]["message"]["content"].strip()
                    return extracted_info
                except requests.exceptions.RequestException as e:
                    if attempt == MAX_RETRIES - 1:
                        st.error(f"LLM API error after {MAX_RETRIES} attempts: {str(e)}")
                        return "Error in processing"
                    sleep(2 ** attempt)  # Exponential backoff
            
            sleep(RATE_LIMIT_DELAY)
            return extracted_info
            
        except Exception as e:
            st.error(f"LLM processing error for {entity}: {str(e)}")
            return "Error in processing"