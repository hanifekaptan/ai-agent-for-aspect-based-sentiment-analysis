"""
API Client Module
Handles all communication with the backend API.
"""
import streamlit as st
import requests


# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
ANALYZE_ENDPOINT = f"{API_BASE_URL}/analyze"


def call_api_text(text: str):
    """
    Calls the API with text input.
    
    Args:
        text (str): Single line of text to be analyzed.
        
    Returns:
        dict: API response or None in case of an error.
    """
    try:
        response = requests.post(
            ANALYZE_ENDPOINT,
            data={'text': text},
            timeout=60
        )
        if response.status_code == 503:
            st.session_state['quota_exceeded'] = True
            try:
                detail = response.json().get('detail', '')
            except Exception:
                detail = ''
            st.error("❌ Service unavailable or quota exceeded.\n" + (detail or "Please try again later."))
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API connection error! Is the backend running?")
        st.code("uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out!")
    except Exception as e:
        st.error(f"❌ API error: {e}")
    return None


def call_api_csv(file):
    """
    Calls the API with a CSV file.
    
    Args:
        file: File-like object containing CSV data.
        
    Returns:
        dict: API response or None in case of an error.
    """
    try:
        files = {'upload_file': ('data.csv', file, 'text/csv')}
        response = requests.post(
            ANALYZE_ENDPOINT,
            files=files,
            timeout=120
        )
        if response.status_code == 503:
            st.session_state['quota_exceeded'] = True
            try:
                detail = response.json().get('detail', '')
            except Exception:
                detail = ''
            st.error("❌ Service unavailable or quota exceeded.\n" + (detail or "Please try again later."))
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ API connection error! Is the backend running?")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out!")
    except Exception as e:
        st.error(f"❌ API error: {e}")
    return None
