@echo off
REM Startup script for Stock Market Sentiment Analyzer
REM This script starts both the backend server and frontend

echo ================================================================================
echo   AI STOCK MARKET SENTIMENT ANALYZER - STARTUP
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server...
echo.
start "Backend Server" cmd /k ".venv\Scripts\python.exe server.py"

REM Wait for server to start
echo Waiting for server to initialize (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo [2/2] Starting Frontend...
echo.
start "Frontend UI" cmd /k ".venv\Scripts\streamlit.exe run frontend.py"

echo.
echo ================================================================================
echo   SERVICES STARTED
echo ================================================================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
echo.
echo Press any key to open the frontend in your browser...
pause >nul

REM Open browser
start http://localhost:8501

echo.
echo To stop the services, close both terminal windows.
echo.
pause
