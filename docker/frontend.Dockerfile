FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /workspace

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project sources (frontend lives under frontend/)
COPY . /workspace

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    API_BASE_URL=http://localhost:8000

# Default: run frontend (single-service image). For combined backend+frontend use docker/space.Dockerfile
CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]