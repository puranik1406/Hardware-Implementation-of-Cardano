@echo off
echo ========================================
echo Arduino-to-Cardano Payment Service
echo ========================================
echo.

cd /d "%~dp0blockchain"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Copying environment template...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please configure your API keys
)

echo.
echo ========================================
echo Starting Mock Payment Service...
echo ========================================
echo Service URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

python src/mock_payment_service.py

pause