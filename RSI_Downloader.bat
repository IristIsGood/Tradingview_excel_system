@echo off
title RSI Downloader
color 0A

echo.
echo  ██████╗ ███████╗██╗    ██╗██╗    ██╗██╗     ██╗███████╗
echo  ██╔══██╗██╔════╝██║    ██║██║    ██║██║     ██║██╔════╝
echo  ██████╔╝███████╗██║    ██║██║    ██║██║     ██║███████╗
echo  ██╔══██╗╚════██║██║    ██║██║    ██║██║     ██║╚════██║
echo  ██║  ██║███████║╚██████╔╝╚██████╔╝███████╗██║███████║
echo  ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚══════╝
echo.
echo  🚀 Multi-Exchange RSI Data Downloader
echo  =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not found.
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo After installation, run this script again.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!

REM Check if we're in the right directory
if not exist "src\app.py" (
    echo ❌ Error: Application files not found.
    echo Please make sure you're running this from the RSI_Downloader folder.
    echo.
    pause
    exit /b 1
)

echo ✅ Application files found!

REM Install dependencies if needed
if not exist "venv" (
    echo 📦 Setting up environment (first time only)...
    echo This may take a few minutes...
    echo.
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r config\requirements.txt
    echo.
    echo ✅ Setup complete!
) else (
    echo 🔄 Activating environment...
    call venv\Scripts\activate.bat
)

echo.
echo 🚀 Starting RSI Downloader...
echo The application will open in your web browser.
echo.
echo Press Ctrl+C to stop the application.
echo.

REM Run the application
python src\app.py

echo.
echo 👋 Application stopped.
pause
