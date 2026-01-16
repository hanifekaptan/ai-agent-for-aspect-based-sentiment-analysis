---
title: Ai Agent For Aspect Based Sentiment Analysis
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
  - streamlit
pinned: false
short_description: Streamlit template space
---

# AI Agent for Aspect Based Sentiment Anaysis

🎯 **Aspect-Based Sentiment Analysis using natural language**

This Space runs a full-stack application with:
- 🚀 **FastAPI Backend** - Aspect-based analysis powered by Google Gemini
- 🎨 **Streamlit Frontend** - Interactive analysis and visualization dashboard

## How to Use

Simply provide text input to get detailed sentiment insights:
- "The screen is great but the battery drains quickly."
- "I love the camera, but the price is too high."
- Upload a CSV file with thousands of customer reviews for batch analysis.

The agent understands context and identifies sentiment for each specific aspect!

## Technology Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **ML Model:** Google Gemini (`gemini-1.5-flash-latest`)
- **ML Framework:** LangChain
- **Data Processing:** Pandas

## Links

- 🚀 [Live Demo on HuggingFace](https://huggingface.co/spaces/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis)
- 💻 [GitHub Repository](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis)
- 🐛 [Report Issues](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis/issues)

## Architecture

```
Streamlit Frontend (Port 7860)
         ↓
FastAPI Backend (Port 8000)
         ↓
Google Gemini API
```

Both services run in a single Docker container optimized for HuggingFace Spaces.

---

**Author:** Hanife Kaptan  
**License:** Apache 2.0
