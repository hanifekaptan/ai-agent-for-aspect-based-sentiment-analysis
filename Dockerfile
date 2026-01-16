# Dockerfile for Hugging Face Spaces - Aspect-Based Sentiment Analysis
# Build date: 2026-01-16
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
RUN chmod +x /app/docker/entrypoint-hf.sh

EXPOSE 8000 7860

# Use the HuggingFace-specific entrypoint which includes health checks and HF-friendly flags
ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint-hf.sh"]
