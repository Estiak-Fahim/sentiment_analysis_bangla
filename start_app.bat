@echo off
echo Starting Bangla Sentiment Analysis Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Check if model directory exists
if not exist "Fahim91Model" (
    echo Error: Model directory not found!
    echo Please ensure Fahim91Model folder exists in the current directory.
    pause
    exit /b 1
)

REM Start the application
echo.
echo Starting the sentiment analysis application...
echo The application will open in your default web browser.
echo.
python Bangla_Sentiment_App.py

pause
