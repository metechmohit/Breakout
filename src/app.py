import streamlit as st
import pandas as pd
import traceback
from agent.ai_agent import AIAgent

def main():
    st.set_page_config(
        page_title="Extractor AI agent",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Extractor AI agent")
    
    # Step 1: Initialize AI Agent
    try:
        SERPAPI_KEY = st.secrets["SERPAPI_KEY"]  # Correct syntax to access secrets
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  # Correct syntax to access secrets
    except KeyError as e:
        st.error(f"Missing required secret: {str(e)}")
        return  # Stop execution if secrets are missing

    agent = AIAgent(SERPAPI_KEY, GROQ_API_KEY)  # Pass keys to the agent class

    # Step 2: Data Source Selection
    st.title("Step 1: Select Data Source")
    st.info("Choose whether to upload a CSV file or connect to a Google Sheet.")
    
    data_source = st.radio(
        "How would you like to provide your data?",
        ["Upload CSV", "Connect Google Sheets"]
    )
    
    # File Upload or Google Sheets
    data = None
    if data_source == "Upload CSV":
        st.subheader("📁 Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose your CSV file",
            type=['csv'],
            help="Upload a CSV file containing your entity data."
        )
        if uploaded_file:
            try:
                data = pd.read_csv(uploaded_file)
                st.success("✅ File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                
    elif data_source == "Connect Google Sheets":
        st.subheader("🔗 Connect to Google Sheets")
        sheet_id = st.text_input("Enter Google Sheet ID")
        range_name = st.text_input("Enter Sheet Range (e.g., Sheet1!A1:D10)")
        if sheet_id and range_name:
            try:
                data = agent.sheets_handler.read_sheet(sheet_id, range_name)
                if not data.empty:
                    st.success("✅ Google Sheet connected successfully!")
            except Exception as e:
                st.error(f"Error connecting to Google Sheet: {str(e)}")
