@echo off
title Instagram AI Bot Launcher
color 0f

echo Starting Instagram Creator AI Bot Setup...
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 goto :no_python

:: Check for virtual environment
if not exist .venv goto :create_venv

:activate_env
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 goto :venv_fail

:: Install packages
echo Verifying dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 goto :pip_fail

echo.
echo Setup complete. Launching local dashboard...
timeout /t 1 >nul
start http://localhost:8000/

python main.py
goto :eof

:no_python
echo [ERROR] Python is not installed or not in your system PATH.
echo Please install Python 3.8+ and check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:create_venv
echo Creating virtual environment (.venv)...
python -m venv .venv
if errorlevel 1 goto :venv_fail
goto :activate_env

:venv_fail
echo [ERROR] Failed to create or activate virtual environment.
pause
exit /b 1

:pip_fail
echo [ERROR] Dependency installation failed. Please check your internet connection.
echo.
pause
exit /b 1

:eof
