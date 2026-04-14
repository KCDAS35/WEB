@echo off
setlocal
title OmniVoice — Install

echo.
echo  =========================================
echo   OmniVoice Local App — First-Time Setup
echo  =========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Download it from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 ( echo  ERROR: Could not create venv. & pause & exit /b 1 )

echo  [2/4] Activating environment...
call venv\Scripts\activate.bat

echo  [3/4] Installing dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt
if errorlevel 1 ( echo  ERROR: Dependency install failed. & pause & exit /b 1 )

echo  [4/4] Done!
echo.
echo  The OmniVoice model (~4 GB) will download automatically
echo  the first time you run the app and generate audio.
echo.
echo  Run  start.bat  to launch the app.
echo.
pause
