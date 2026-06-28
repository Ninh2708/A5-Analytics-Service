@echo off
setlocal

cd /d "%~dp0"

if not exist ".env" (
    echo Creating .env from .env.example...
    copy /y ".env.example" ".env" >nul
)

set "VENV_DIR="
if exist ".venv\Scripts\activate.bat" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\activate.bat" set "VENV_DIR=venv"
if not defined VENV_DIR (
    echo Creating virtual environment in .venv...
    python -m venv .venv
    set "VENV_DIR=.venv"
)

echo Activating %VENV_DIR%...
call "%VENV_DIR%\Scripts\activate.bat"

if "%1"=="--install" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
)

if "%1"=="--with-db" (
    echo Setting up database...
    python setup_db.py
)

echo Starting Analytics Service on http://26.52.94.169:8000/
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
