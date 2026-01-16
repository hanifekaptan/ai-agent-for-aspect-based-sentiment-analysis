# AI Agent for Aspect Based Sentiment Analysis

AI Agent for ABSA is a full-featured AI agent that detects product or service features (aspects) in texts and scores the sentiment (positive, negative, neutral) for each feature. It has a powerful backend developed with FastAPI and a user-friendly interface created with Streamlit. It performs semantic analysis in the background using large language models (LLMs) like Google Gemini.

## 🌐 Links

- **Live Demo:** [HuggingFace Spaces](https://huggingface.co/spaces/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis)
- **Documentation**: [GitHub Pages](https://hanifekaptan.github.io/ai-agent-for-aspect-based-sentiment-analysis/)
- **GitHub Repository:** [hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis)

## ✨ Features

- **Advanced Analysis:** Processes comments from text inputs or CSV files to perform aspect-based sentiment analysis.
- **RESTful API:** A FastAPI backend offering comprehensive endpoints and automatic OpenAPI documentation.
- **Modern Interface:** A responsive Streamlit frontend that supports modes like single text, CSV file upload, and sample data analysis.
- **Scalability:** High performance through concurrent LLM calls and asynchronous operations.
- **Error Handling:** Robust error management in the API for situations like quota exceeded and connection errors.
- **Docker Support:** Easily deployable structure with a `Dockerfile` and `entrypoint.sh` script.
- **Testing:** Verification of basic API functions with smoke tests written using `pytest`.

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.12
- `pip` and `venv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis.git
    cd ai-agent-for-aspect-based-sentiment-analysis
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a file named `.env` in the project root directory and add your Google Gemini API key:
    ```env
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    MODEL_NAME="gemini-1.5-flash-latest" 
    ```

### Running the Application

1.  **Run the Backend (FastAPI):**
    ```bash
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ```
    The API will be accessible at [http://localhost:8000](http://localhost:8000), and the interactive documentation at [/docs](http://localhost:8000/docs).

2.  **Run the Frontend (Streamlit) (in a new terminal):**
    ```bash
    streamlit run frontend/app.py --server.port 8501
    ```
    The application interface will be displayed at [http://localhost:8501](http://localhost:8501).

## 📂 Project Structure

```
aspect-based-senetiment-analyzer-agent/
├── app/                          # FastAPI backend application
│   ├── api/                      # API routes and endpoints
│   │   ├── analyze.py            # Analysis endpoint
│   │   └── health.py             # Health check endpoint
│   ├── core/                     # Core configuration and helpers
│   │   └── logging.py            # Logging setup
│   ├── llm/                      # LLM client logic
│   │   └── client.py             # Gemini API calls
│   ├── prompting/                # Prompt management
│   │   └── manager.py            # Loading and rendering prompt templates
│   ├── prompts/                  # Prompt templates (YAML)
│   ├── schemas/                  # Pydantic data models
│   ├── services/                 # Business logic services
│   │   └── absa_service.py       # ABSA analysis logic
│   ├── utils/                    # Utility functions
│   └── main.py                   # FastAPI application entry point
├── frontend/                     # Streamlit frontend application
│   ├── api/
│   │   └── client.py             # Backend API client
│   ├── components/               # Reusable UI components
│   ├── streamlit_app/
│   └── app.py                    # Streamlit application entry point
├── docker/                       # Docker configurations
│   ├── entrypoint.sh             # Script to start both backend and frontend
│   └── space.Dockerfile          # Combined Dockerfile for HuggingFace
├── tests/                        # Test suite
│   └── test_smoke.py             # API smoke tests
├── Dockerfile                    # Main Dockerfile for HuggingFace Space
├── requirements.txt              # Python dependencies
└── README.md
```

## 🏗️ Architecture Overview

### Backend (FastAPI)

-   **Analysis Engine:** Makes API calls to Google's Gemini model using `langchain-google-genai`.
-   **Asynchronous Operations:** Manages concurrent LLM requests using `asyncio` and `Semaphore`, which improves performance.
-   **Data Parsing:** Uses `pandas` to process data from single text, CSV, or other formats.
-   **Service Layer:** Provides a clean separation between API routes, business logic, and LLM calls.
-   **API Documentation:** Automatically generated OpenAPI (Swagger) documentation available at `/docs`.

### Frontend (Streamlit)

-   **Component-Based:** Modular UI components for search, file upload, and result visualization.
-   **API Client:** A `requests`-based HTTP client with error handling to communicate with the backend.
-   **State Management:** Uses `st.session_state` to manage analysis results and API quota errors.
-   **User-Friendly Design:** A clean, understandable, and interactive interface.

### Data Flow

1.  The user enters text or uploads a CSV file via the Streamlit interface.
2.  The frontend sends the request to the `/analyze` endpoint.
3.  The backend receives the input, cleans it, and divides it into appropriate batches for analysis.
4.  The `absa_service` generates prompts to be sent to the LLM for each batch.
5.  The LLM analyzes the features and sentiments in the texts and returns a response in a structured format.
6.  The backend parses the LLM response and sends it to the frontend in JSON format.
7.  The frontend visualizes the results with metrics, charts, and tables.

## 🧪 Testing

The project includes basic smoke tests written with `pytest`:

```bash
# Run all tests
pytest
```

-   **Smoke Tests:** Verify the basic functionality of the API by testing the `/health` and mocked `/analyze` endpoints.

## 🐳 Deployment with Docker

This project is configured to run both the backend and frontend in a single container. This simplifies deployment, especially on platforms like HuggingFace Spaces.

1.  **Build the Docker Image:**
    ```bash
    docker build -t aspect-based-sentiment-analyzer .
    ```

2.  **Run the Container:**
    ```bash
    docker run -p 8000:8000 -p 8501:7860 -e GOOGLE_API_KEY="YOUR_GEMINI_API_KEY" aspect-based-sentiment-analyzer
    ```
    - The backend API will be accessible at `http://localhost:8000`.
    - The Streamlit interface will be accessible at `http://localhost:8501`.

### HuggingFace Spaces

The `Dockerfile` in the project root is compatible with HuggingFace Spaces. You just need to link your repository to a Space and add `GOOGLE_API_KEY` as a secret.

## 🛠️ Technology Stack

-   **Backend:**
    -   FastAPI
    -   Uvicorn
    -   langchain-google-genai
    -   Pandas, NumPy
    -   Pydantic
-   **Frontend:**
    -   Streamlit
    -   Requests
-   **Language:** Python 3.12
-   **Testing:**
    -   pytest
    -   pytest-asyncio
-   **DevOps:**
    -   Docker
    -   HuggingFace Spaces

## 📝 API Endpoints

### `GET /health`

Used to check the status of the service.

-   **Response:**
    ```json
    {
      "status": "ok",
      "timestamp": 1678886400.0
    }
    ```

### `POST /analyze`

Performs analysis on text or a CSV file.

-   **Request (Text):** `text` field in `multipart/form-data`.
-   **Request (File):** `upload_file` field in `multipart/form-data`.

-   **Successful Response:**
    ```json
    {
      "items_submitted": 5,
      "batches_sent": 1,
      "results": [
        {
          "id": "1",
          "aspects": [
            { "term": "screen", "sentiment": "positive" },
            { "term": "battery", "sentiment": "negative" }
          ]
        }
      ],
      "duration_seconds": 5.43
    }
    ```

-   **Error Response (Quota Exceeded):**
    ```json
    {
      "detail": {
        "error": "Upstream quota exceeded or rate-limit received",
        "message": "An error related to the quota was returned from the model provider. Please try again later.",
        "upstream_error": "429 Quota exceeded for model..."
      }
    }
    ```

## 📄 License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.

## 📧 Contact

Hanife Kaptan - hanifekaptan.dev@gmail.com

Project Link: [https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis](https://github.com/hanifekaptan/ai-agent-for-aspect-based-sentiment-analysis)

⭐ Don't forget to star this repository if you find it useful!
