"""
Input Handlers Module
Contains functions for handling different input modes.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from api.client import call_api_text, call_api_csv


def handle_text_input(on_results):
    """
    Manages the single text input interface.
    
    Args:
        on_results: Callback function to display results.
    """
    st.subheader("📝 Single Text Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_area(
            "Enter your text:",
            placeholder="E.g: The screen is great but the battery drains quickly.",
            height=150,
            help="Write the text to be analyzed. Language will be auto-detected."
        )
    
    with col2:
        st.markdown("### 💡 Tip")
        st.info(
            "Enter text containing opinions about products/services. "
            "Texts with multiple aspects provide more detailed analysis."
        )
    
    disabled = st.session_state.get('quota_exceeded', False)
    if disabled:
        st.warning("⚠️ Analysis disabled: service unavailable or quota exceeded.")

    if st.button("🚀 Analyze", type="primary", use_container_width=True, disabled=disabled):
        if not text_input.strip():
            st.error("❌ Please enter text to analyze!")
            return
        
        with st.spinner("🔍 Analyzing..."):
            results = call_api_text(text_input)
        
        if results:
            on_results(results, is_single=True)


def handle_csv_upload(on_results):
    """
    Manages the CSV file upload interface.
    
    Args:
        on_results: Callback function to display results.
    """
    st.subheader("📤 CSV File Upload")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Select CSV file:",
            type=['csv'],
            help="CSV file must contain 'id' and 'comments' columns"
        )
    
    with col2:
        st.markdown("### 📋 Format")
        st.code("""id,comments
1,First comment
2,Second comment""", language="csv")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.markdown("### 👀 Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.info(f"📊 Total {len(df)} rows found")
            
            uploaded_file.seek(0)
            disabled = st.session_state.get('quota_exceeded', False)
            if disabled:
                st.warning("⚠️ Analysis disabled: service unavailable or quota exceeded.")

            if st.button("🚀 Analyze", type="primary", use_container_width=True, disabled=disabled):
                with st.spinner("🔍 Analyzing CSV..."):
                    results = call_api_csv(uploaded_file)
                
                if results:
                    on_results(results, is_single=False)
        
        except Exception as e:
            st.error(f"❌ CSV reading error: {e}")


def handle_sample_data(on_results):
    """
    Manages the sample data demo interface.
    
    Args:
        on_results: Callback function to display results.
    """
    st.subheader("🎁 Demo with Sample Data")
    
    sample_path = Path(__file__).parent.parent / "assets" / "sample_data.csv"
    
    if not sample_path.exists():
        st.error("❌ Sample data file not found!")
        return
    
    st.markdown("""
    ### 📱 Phone Reviews Sample Dataset
    
    The sample dataset below contains user reviews about phone products.
    Each review contains different aspects (screen, battery, camera, price, etc.) and sentiments.
    """)
    
    df_sample = pd.read_csv(sample_path)
    st.dataframe(df_sample, use_container_width=True)
    
    st.info(f"📊 Contains {len(df_sample)} sample reviews")
    
    col1, col2 = st.columns(2)
    
    with col1:
        disabled = st.session_state.get('quota_exceeded', False)
        if disabled:
            st.warning("⚠️ Analysis disabled: service unavailable or quota exceeded.")

        if st.button("🚀 Analyze Sample Data", type="primary", use_container_width=True, disabled=disabled):
            with st.spinner("🔍 Analyzing sample data..."):
                with open(sample_path, 'rb') as f:
                    results = call_api_csv(f)
            
            if results:
                on_results(results, is_single=False)
    
    with col2:
        with open(sample_path, 'rb') as f:
            st.download_button(
                label="📥 Download Sample Data",
                data=f,
                file_name="sample_data.csv",
                mime="text/csv",
                use_container_width=True
            )
