#!/bin/bash

echo "Starting Instagram Creator AI Bot Setup..."
echo

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed or not in your PATH."
    echo "Termux (Android) users: Please run 'pkg update && pkg install python' first."
    exit 1
fi

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[WARNING] Failed to create virtual environment. Installing packages globally in user space instead..."
        python -m pip install --user -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "[ERROR] Package installation failed."
            exit 1
        fi
        
        echo
        echo "Setup complete. Launching FastAPI server..."
        python main.py
        exit 0
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment."
    exit 1
fi

# Install packages
echo "Verifying dependencies..."
python -m pip install --upgrade pip &> /dev/null
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Dependency installation failed."
    exit 1
fi

echo
echo "Setup complete. Launching FastAPI server..."
echo "Please open http://localhost:8000 in your browser."
python main.py
