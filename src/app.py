import streamlit as st
import pandas as pd
import traceback
from agent.ai_agent import AIAgent
from config import (
    SERPAPI_KEY,
    GROQ_API_KEY,
    GOOGLE_SCOPES,
    GOOGLE_SHEETS_CREDENTIALS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    SEARCH_RESULTS_PER_QUERY,
    SEARCH_REGION,
    RATE_LIMIT_DELAY,
    MAX_RETRIES,
)

def main():
    st.set_page_config(
        page_title="Extractor AI Agent",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Extractor AI Agent")
    
    # Step 1: Initialize AI Agent
    if not SERPAPI_KEY or not GROQ_API_KEY:
        st.error("Missing required API keys. Ensure `SERPAPI_KEY` and `GROQ_API_KEY` are set in the environment.")
        return

    agent = AIAgent(
        serpapi_key=SERPAPI_KEY,
        groq_api_key=GROQ_API_KEY,
        llm_model=LLM_MODEL,
        llm_temperature=LLM_TEMPERATURE,
        llm_max_tokens=LLM_MAX_TOKENS,
        rate_limit_delay=RATE_LIMIT_DELAY,
        max_retries=MAX_RETRIES
    )

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
    
    # Step 3: Dataset Preview and Configuration
    if data is not None:
        st.title("Step 2: Configure Dataset")
        st.info("Preview your dataset and select the column containing entity names.")
        with st.expander("📋 Dataset Preview", expanded=True):
            st.dataframe(data.head(), height=200)
        
        # Dataset Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            target_column = st.selectbox(
                "Select Entity Column",
                data.columns,
                help="Choose the column containing entity names."
            )
            
        with col2:
            batch_size = st.number_input(
                "Batch Size",
                min_value=1,
                max_value=len(data),
                value=min(10, len(data)),
                help="Number of entities to process at once."
            )
        
        # Step 4: Query Configuration
        st.title("Step 3: Define Query")
        st.info("Use {company} as a placeholder for the entity name in your query.")
        
        # Single prompt text area
        prompt = st.text_area(
            "Enter Your Prompt",
            "What is the main product or service of {company}?",
            help="Provide a single prompt using {company} as a placeholder for entity names."
        )
        
        # Step 5: Process Data
        st.title("Step 4: Process Data")
        st.info("Click the button below to start processing the data.")
        if st.button("🚀 Start Processing", type="primary"):
            try:
                # Progress bar
                st.subheader("Processing Data")
                progress_bar = st.progress(0)
                
                # Call the AI Agent to process the data
                results_df = agent.process_batch(
                    data.head(batch_size),
                    target_column,
                    [prompt],  # Single prompt passed as a list
                    progress_bar
                )
                
                # Display results
                st.title("Step 5: View Results")
                st.success("✅ Data processing completed!")
                st.dataframe(results_df, height=300)
                
                # Step 6: Download or Export Results
                st.title("Step 6: Download or Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name="extracted_results.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    if data_source == "Connect Google Sheets":
                        if st.button("📤 Export to Google Sheets"):
                            agent.sheets_handler.write_results(sheet_id, "Results!A1", results_df)
                            st.success("✅ Results exported to Google Sheets!")
                
            except Exception as e:
                st.error("❌ An error occurred during processing.")
                st.error(f"Error details: {str(e)}")
                st.code(traceback.format_exc())
    
if __name__ == '__main__':
    main()
