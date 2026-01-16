# Aspectify

Welcome to **Aspectify** - A powerful Aspect-Based Sentiment Analysis (ABSA) system powered by Google's Gemini AI.

## Overview

Aspectify is a production-ready application that extracts aspects (features/topics) from text and analyzes the sentiment (positive/negative/neutral) associated with each aspect. It's designed for analyzing customer reviews, feedback, and opinions at a granular level.

## Key Features

- **🎯 Aspect Extraction**: Automatically identifies key topics and features mentioned in text
- **😊 Sentiment Analysis**: Determines sentiment for each extracted aspect
- **📊 Batch Processing**: Handles single texts or bulk CSV uploads efficiently
- **🌍 Multi-language Support**: Auto-detects language (Turkish, English, etc.)
- **⚡ Fast & Scalable**: Async processing with concurrent batch handling
- **🎨 Interactive Frontend**: Beautiful Streamlit UI with visualizations
- **📈 Export Options**: Download results as CSV or Excel

## Use Cases

- **Product Reviews**: Analyze what customers love or hate about specific product features
- **Service Feedback**: Understand satisfaction levels across different service aspects
- **Brand Monitoring**: Track sentiment changes for various brand attributes
- **Market Research**: Extract insights from survey responses and feedback forms

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis
.git
cd ai-agent-for-aspect-based-sentiment-analysis

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Backend API:**
```bash
uvicorn app.main:app --reload --reload-dir app
```

**Frontend UI:**
```bash
streamlit run frontend/app.py
```

## Example

**Input:**
```text
The phone's screen is amazing but the battery drains too quickly.
```

**Output:**
```json
{
  "id": "1",
  "aspects": [
    {"term": "screen", "sentiment": "positive"},
    {"term": "battery", "sentiment": "negative"}
  ]
}
```

## Architecture

The system consists of three main components:

1. **FastAPI Backend**: RESTful API for analysis requests
2. **Streamlit Frontend**: Interactive web interface with visualizations
3. **LLM Integration**: Google Gemini for aspect extraction and sentiment classification

See the [Architecture](architecture.md) page for detailed system design.

## API Reference

For detailed API endpoints and usage, see the [API Reference](api.md) page.

## Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **LLM**: Google Gemini (via LangChain)
- **Frontend**: Streamlit, Plotly
- **Data Processing**: Pandas, Jinja2
- **Testing**: Pytest

## License

This project is licensed under the Apache License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on [GitHub](https://github.com/hanifekaptan/Aspectify/issues).
