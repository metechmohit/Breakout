import streamlit as st
import pandas as pd
import traceback
from agent.ai_agent import AIAgent

def main():
    st.set_page_config(
        page_title="AI Information Extractor",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 AI Information Extractor")
    st.markdown("""
    This tool helps you extract specific information about companies or other entities from the web using AI.
    Upload your data or connect to Google Sheets, specify what information you want to find, and let the AI do the work!
    """)
    
    # Initialize AI Agent
    agent = AIAgent()
    
    # Data Source Selection
    st.header("1️⃣ Data Source")
    data_source = st.radio(
        "Choose your data source:",
        ["Upload CSV", "Connect Google Sheets", "Use Sample Data"]
    )
    
    data = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=['csv'],
            help="Upload a CSV file containing your entity data"
        )
        if uploaded_file:
            try:
                data = pd.read_csv(uploaded_file)
                st.success("✅ File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
                
    elif data_source == "Connect Google Sheets":
        sheet_id = st.text_input("Enter Google Sheet ID")
        range_name = st.text_input("Enter Sheet Range (e.g., Sheet1!A1:D10)")
        if sheet_id and range_name:
            try:
                data = agent.sheets_handler.read_sheet(sheet_id, range_name)
                if not data.empty:
                    st.success("✅ Google Sheet connected successfully!")
            except Exception as e:
                st.error(f"Error connecting to Google Sheet: {str(e)}")
                
    else:  # Sample Data
        data = pd.DataFrame({
            'company_name': ['Apple', 'Microsoft', 'Google'],
            'industry': ['Technology', 'Technology', 'Technology']
        })
        st.success("✅ Sample data loaded!")
    
    if data is not None:
        st.header("2️⃣ Data Preview")
        st.dataframe(data.head())
        
        st.header("3️⃣ Query Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            target_column = st.selectbox(
                "Select entity column:",
                data.columns,
                help="Choose the column containing entity names"
            )
            
        with col2:
            batch_size = st.number_input(
                "Batch size",
                min_value=1,
                max_value=len(data),
                value=min(10, len(data)),
                help="Number of entities to process at once"
            )
        
        # Multiple prompts support
        st.subheader("Enter your prompts")
        st.markdown("Use {company} as a placeholder for the entity name")
        
        num_prompts = st.number_input("Number of prompts", min_value=1, max_value=5, value=1)
        prompts = []
        for i in range(num_prompts):
            prompt = st.text_area(
                f"Prompt {i+1}:",
                "What is the main product or service of {company}?" if i == 0 else "",
                key=f"prompt_{i}"
            )
            if prompt:
                prompts.append(prompt)
        
        if st.button("🚀 Start Processing", type="primary"):
            try:
                st.header("4️⃣ Processing")
                progress_bar = st.progress(0)
                
                # Process data in batches
                results_df = agent.process_batch(
                    data.head(batch_size),
                    target_column,
                    prompts,
                    progress_bar
                )
                
                st.header("5️⃣ Results")
                st.dataframe(results_df)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name="extracted_results.csv",
                        mime="text/csv"
                    )
                
                # Google Sheets export option
                if data_source == "Connect Google Sheets":
                    with col2:
                        if st.button("📤 Export to Google Sheets"):
                            agent.sheets_handler.write_results(sheet_id, "Results!A1", results_df)
                
            except Exception as e:
                st.error("❌ An error occurred during processing")
                st.error(f"Error details: {str(e)}")
                st.code(traceback.format_exc())

if __name__ == '__main__':
    main()