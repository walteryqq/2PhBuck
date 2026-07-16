#!/bin/bash
# LAN Startup Script for Linux/macOS
cd "$(dirname "$0")"

# Check if .venv exists
if [ -d ".venv" ]; then
    echo "Found .venv. Starting Streamlit server on 0.0.0.0:8501..."
    ./.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
else
    echo "No .venv folder found. Running with system python (ensure requirements are installed)..."
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
fi
