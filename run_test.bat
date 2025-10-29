@echo off
REM Quick test runner for Windows
REM This batch file starts the Flask app and runs the test

echo Starting Astrology App Planet Position Test...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Step 1: Installing required packages...
pip install requests flask

echo.
echo Step 2: Starting Flask app in background...
start "Flask App" python app.py

echo Waiting 5 seconds for Flask app to start...
timeout /t 5 >nul

echo.
echo Step 3: Running planet position test...
python test_planet_positions.py

echo.
echo Test completed. Press any key to exit...
pause