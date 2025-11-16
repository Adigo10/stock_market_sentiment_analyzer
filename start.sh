#!/bin/bash
# Startup script for Stock Market Sentiment Analyzer
# This script starts both the backend server and frontend

echo "================================================================================"
echo "  AI STOCK MARKET SENTIMENT ANALYZER - STARTUP"
echo "================================================================================"
echo

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please create a virtual environment first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    read -p "Press any key to continue..."
    exit 1
fi

echo "[1/2] Starting Backend Server..."
echo
# Start backend in background and capture PID
.venv/bin/python server.py &
BACKEND_PID=$!

# Wait for server to start
echo "Waiting for server to initialize (10 seconds)..."
sleep 10

echo
echo "[2/2] Starting Frontend..."
echo
# Start frontend in background and capture PID
.venv/bin/streamlit run frontend.py &
FRONTEND_PID=$!

echo
echo "================================================================================"
echo "  SERVICES STARTED"
echo "================================================================================"
echo
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:8501"
echo
echo "Press any key to open the frontend in your browser..."
read -n 1 -s

# Open browser (works on macOS)
open http://localhost:8501

echo
echo "To stop the services, press Ctrl+C"
echo

# Set up trap to kill background processes when script is interrupted
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for user interrupt
wait
