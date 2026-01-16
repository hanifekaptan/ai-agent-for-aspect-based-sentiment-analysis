FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies (single image for Space)
COPY requirements.txt ./

# Install system deps needed for health checks and SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project sources
COPY . /app

# Copy and setup entrypoint
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000 7860

# Entrypoint will start both backend and Streamlit
ENTRYPOINT ["/app/docker/entrypoint.sh"]