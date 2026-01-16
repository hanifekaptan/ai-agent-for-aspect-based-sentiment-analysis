FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies from requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project sources
COPY . /app

EXPOSE 8000

# Run backend only (for single-service image)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]