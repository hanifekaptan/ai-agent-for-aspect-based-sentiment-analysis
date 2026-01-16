#!/usr/bin/env bash
set -euo pipefail

# Start backend (uvicorn) in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Streamlit in background
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for either process to exit
wait -n $BACKEND_PID $STREAMLIT_PID

# If one exits, forward its exit code
wait $BACKEND_PID || true
wait $STREAMLIT_PID || true
#!/usr/bin/env bash
set -euo pipefail

echo "Starting backend on 8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Streamlit on ${PORT}"
exec streamlit run frontend/app.py --server.port ${PORT} --server.address 0.0.0.0

wait ${BACKEND_PID}