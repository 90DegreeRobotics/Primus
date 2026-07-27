@echo off
echo ========================================
echo   CCF SOVEREIGN MIND - MVP LAUNCHER
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo [Setup] Creating virtual environment...
    python -m venv venv
    echo [Setup] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo [Setup] Checking dependencies...
pip install -q -r requirements.txt

REM Run the system
echo.
echo [Launch] Starting CCF Sovereign Mind...
echo.
python src\main.py

pause
