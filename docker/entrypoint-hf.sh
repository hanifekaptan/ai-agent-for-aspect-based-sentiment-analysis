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

# Wait for backend to be ready (try multiple local addresses)
echo "⏳ Waiting for backend to be ready..."
HOSTS=("127.0.0.1" "localhost" "0.0.0.0")
MAX_ITER=60
SLEEP_SEC=2
ready=false
for i in $(seq 1 $MAX_ITER); do
    for h in "${HOSTS[@]}"; do
        if curl -fsS "http://${h}:8000/health" >/dev/null 2>&1; then
            echo "✅ Backend is ready (responding at http://${h}:8000/health)"
            ready=true
            break 2
        fi
    done
    if [ "$ready" = true ]; then
        break
    fi
    if [ "$i" -eq $MAX_ITER ]; then
        echo "❌ Backend failed to start in time (tried hosts: ${HOSTS[*]})"
        # print a diagnostic curl attempt to stderr for logs
        for h in "${HOSTS[@]}"; do
            echo "--- Diagnostic: curl http://${h}:8000/health ---" >&2
            curl -v "http://${h}:8000/health" 2>&1 || true
        done
        exit 1
    fi
    sleep $SLEEP_SEC
done

# Start Streamlit frontend in foreground (when it exits, script continues and cleanup runs)
echo "🎨 Starting Streamlit frontend on port ${PORT}..."
export API_BASE_URL="http://127.0.0.1:8000"
streamlit run frontend/app.py \
    --server.port "${PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

# When Streamlit exits, script ends and trap/cleanup runs