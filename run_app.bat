@echo off
echo ============================================================
echo   HTML Portal Website - Startup Script
echo ============================================================

rem Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment .venv not found.
    echo Please run these commands first:
    echo   uv venv .venv --python 3.12
    echo   uv pip install -r requirements.txt
    pause
    exit /b 1
)

rem Activate virtual environment
call .\.venv\Scripts\activate.bat

rem Check if frontend is built
if not exist "Frontend\dist\index.html" (
    echo [INFO] Frontend not built, building...
    cd Frontend
    if not exist "node_modules" (
        echo [INFO] Installing frontend dependencies...
        call npm install
    )
    call npm run build
    cd ..
)

rem Start app.py
echo [START] Launching backend service...
.\.venv\Scripts\python.exe app.py

rem Pause to view output
rem pause

rem Deactivate virtual environment
deactivate
