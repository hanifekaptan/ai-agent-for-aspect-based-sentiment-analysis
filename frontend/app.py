"""
Aspectify - Aspect-Based Sentiment Analysis Demo
Main application entry point.
"""
import streamlit as st
import sys
from pathlib import Path

# Add frontend to path for imports
frontend_dir = Path(__file__).parent
sys.path.insert(0, str(frontend_dir))

from components.input_handlers import handle_text_input, handle_csv_upload, handle_sample_data
from components.visualizations import display_results


# Page configuration
st.set_page_config(
    page_title="Aspectify - ABSA Demo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def apply_custom_css():
    """Applies custom CSS styling."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .positive { color: #2ecc71; font-weight: bold; }
        .negative { color: #e74c3c; font-weight: bold; }
        .neutral { color: #95a5a6; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Renders the application header."""
    st.markdown('<div class="main-header">🎯 Aspectify</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Aspect-Based Sentiment Analysis Agent</div>', unsafe_allow_html=True)


def render_sidebar():
    """Renders the sidebar with settings and information."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        input_mode = st.radio(
            "Input Type",
            ["Single Text", "CSV File", "Sample Data"],
            help="Upload text or CSV file for analysis"
        )
        
        st.divider()
        
        st.markdown("### 📊 About")
        st.markdown("""
        This application detects aspects (features/topics) in texts and 
        analyzes the sentiment (positive/negative/neutral) of each.
        
        **Supported Formats:**
        - Single line text
        - CSV file (id, comments columns)
        """)
        
        st.divider()
        
        if st.button("🔄 Clear Page"):
            st.rerun()
        
        return input_mode


def main():
    """Main application logic."""
    apply_custom_css()
    
    render_header()
    
    input_mode = render_sidebar()
    
    if input_mode == "Single Text":
        handle_text_input(on_results=display_results)
    elif input_mode == "CSV File":
        handle_csv_upload(on_results=display_results)
    else:
        handle_sample_data(on_results=display_results)


if __name__ == "__main__":
    main()
