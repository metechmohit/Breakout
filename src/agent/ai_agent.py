from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
from search.search_engine import SearchEngine
from llm.processor import LLMProcessor
from data_handler.sheets_handler import GoogleSheetsHandler



class AIAgent:
    """Main AI Agent class that coordinates search and LLM processing"""
    
    def __init__(self):
        self.search_engine = SearchEngine()
        self.llm_processor = LLMProcessor()
        self.sheets_handler = GoogleSheetsHandler()
        
    def process_entity(self, entity: str, prompts: List[str]) -> Dict:
        """Process a single entity with multiple prompts"""
        search_results = []
        for prompt in prompts:
            results = self.search_engine.search(entity, prompt)
            search_results.extend(results)
        
        extracted_info = self.llm_processor.process_multiple_fields(entity, prompts, search_results)
        return {
            "entity": entity,
            **extracted_info
        }
        
    def process_batch(self, data: pd.DataFrame, target_column: str, prompts: List[str], 
                     progress_bar: Optional[st.progress] = None) -> pd.DataFrame:
        """Process a batch of entities with progress tracking"""
        results = []
        total = len(data)
        
        for idx, entity in enumerate(data[target_column]):
            if progress_bar:
                progress_bar.progress((idx + 1) / total)
                
            st.write(f"Processing: {entity}")
            result = self.process_entity(entity, prompts)
            results.append(result)
            
        return pd.DataFrame(results)