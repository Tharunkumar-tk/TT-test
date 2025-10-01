@echo off
echo Starting FitVision Workout Processing Backend...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting server on http://localhost:8000
python server.py
