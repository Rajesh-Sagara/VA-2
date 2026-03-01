@echo off
title Veracity Agent Launcher
color 0A

echo ============================================
echo   Veracity Agent v2.0 - Launcher
echo ============================================
echo.

:: Set working directory to this file's location
cd /d "%~dp0"

:: Check venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Please run:  python -m venv venv
    echo Then:        venv\Scripts\pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo [1/2] Starting Backend API (FastAPI + Uvicorn)...
start "Veracity - Backend API" cmd /k "title Veracity Backend && color 0B && call venv\Scripts\activate.bat && uvicorn backend.main:app --reload"

:: Small delay so backend can start before dashboard tries to connect
timeout /t 3 /nobreak >nul

echo [2/2] Starting Dashboard (Streamlit)...
start "Veracity - Dashboard" cmd /k "title Veracity Dashboard && color 05 && call venv\Scripts\activate.bat && streamlit run dashboard/app.py"

:: Wait a moment then open the browser
timeout /t 4 /nobreak >nul
:: start "" "http://localhost:8501"

echo.
echo ============================================
echo   Both services are now running!
echo.
echo   Backend API : http://127.0.0.1:8000
echo   Dashboard   : http://localhost:8501
echo   API Docs    : http://127.0.0.1:8000/docs
echo.
echo   Close the two terminal windows to stop.
echo ============================================
echo.
pause
