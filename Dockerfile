FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies (single image for Space)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project sources
COPY . /app

EXPOSE 8000 7860

# Entrypoint will start both backend and Streamlit
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
