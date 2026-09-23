@echo off
cd /d "%~dp0"

echo ============================================
echo   AI Tutor - Feishu Bot
echo   keep this window open while running
echo   Ctrl+C to stop
echo ============================================

if not exist .venv\Scripts\python.exe (
    echo [first run] creating venv...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

set PYTHONIOENCODING=utf-8
echo Starting bot, please wait...
.venv\Scripts\python.exe run_feishu.py
pause