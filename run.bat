@echo off
title Instagram AI Bot Launcher
color 0f

echo Starting Instagram Creator AI Bot Setup...
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.8+ and check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Create virtual environment if missing
if not exist .venv (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install packages
echo Verifying dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed. Please check your internet connection.
    pause
    exit /b 1
)

:: Run Server and launch dashboard
echo.
echo Setup complete. Launching local dashboard...
timeout /t 1 >nul
start http://localhost:8000/

python main.py
pause
