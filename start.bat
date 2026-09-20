@echo off
title AI Tutor - Start
cd /d "%~dp0"

echo ============================================
echo   AI Tutor - one-click start
echo ============================================
echo.

REM ---- 1. create .env from example if missing ----
if not exist ".env" (
    echo [INFO] .env not found. Copying from .env.example...
    copy ".env.example" ".env" >nul 2>&1
    echo [INFO] Created .env. Please open it, fill DEEPSEEK_API_KEY, then run again.
    echo.
    pause
    exit /b 1
)

REM ---- 2. create venv if missing ----
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [FAIL] Could not create venv. Make sure Python is installed and on PATH.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists.
)

echo [2/4] Installing dependencies (first time may take a few minutes)...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
".venv\Scripts\python.exe" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [INFO] Tsinghua mirror failed, trying default index...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [FAIL] Dependency install failed. Check network and retry.
        pause
        exit /b 1
    )
)

echo [3/4] Starting server...
echo.
echo Once running, open http://127.0.0.1:8000 in your browser.
echo Press Ctrl+C to stop.
echo ============================================
echo.

".venv\Scripts\python.exe" main.py

pause
