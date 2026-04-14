@echo off
setlocal
title OmniVoice Local App

echo.
echo  ================================
echo   OmniVoice Local — Starting...
echo  ================================
echo.

REM Check that install.bat was run first
if not exist venv\Scripts\activate.bat (
    echo  Virtual environment not found.
    echo  Please run install.bat first.
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo  Opening browser at http://localhost:8765
echo  Press Ctrl+C to stop the server.
echo.
python app.py
pause
