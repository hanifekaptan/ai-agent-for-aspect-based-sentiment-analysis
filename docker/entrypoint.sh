#!/usr/bin/env bash
set -euo pipefail

# Entrypoint to run both backend (uvicorn) and Streamlit frontend in the same container.
# Usage: container runs backend on 8000 and Streamlit on 8501.

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Started backend (PID=${BACKEND_PID})"

# Ensure backend is healthy before starting frontend (simple wait loop)
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "Backend is healthy"
    break
  fi
  echo "Waiting for backend... ($i)"
  sleep 1
done

# Start Streamlit in foreground so container stays alive
: ${PORT:=7860}
echo "Starting Streamlit on port ${PORT}"
exec streamlit run frontend/app.py --server.port ${PORT} --server.address 0.0.0.0
