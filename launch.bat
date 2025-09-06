@echo off
REM LucianMirror Launch Script (Windows)

echo Starting LucianMirror...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Run the Python launcher
python launch.py

pause