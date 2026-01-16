#!/usr/bin/env bash
set -euo pipefail

: ${PORT:=7860}

echo "🚀 Starting on HuggingFace Spaces"
echo "📊 Backend API: http://localhost:8000"
echo "🎨 Frontend UI: http://localhost:${PORT}"

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &
BACKEND_PID=$!
echo "Started backend (PID=${BACKEND_PID})"

# Ensure cleanup on exit/termination
cleanup() {
  echo "Shutting down backend (PID=${BACKEND_PID})"
  kill "${BACKEND_PID}" 2>/dev/null || true
}
trap cleanup EXIT SIGINT SIGTERM

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in $(seq 1 30); do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "❌ Backend failed to start in time"
        exit 1
    fi
    sleep 2
done

# Start Streamlit frontend in foreground (when it exits, script continues and cleanup runs)
echo "🎨 Starting Streamlit frontend on port ${PORT}..."
streamlit run frontend/app.py \
    --server.port "${PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

# When Streamlit exits, script ends and trap/cleanup runs