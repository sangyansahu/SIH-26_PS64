@echo off
setlocal enabledelayedexpansion
title AICTE Integrated Complaint Portal - Launcher
cd /d "%~dp0"

echo =========================================================================
echo    AICTE Integrated Complaint Monitoring ^& Coordination Portal
echo                   Smart India Hackathon 2026
echo =========================================================================
echo.

:: -------------------------------------------------------------------------
:: 1. Check Python
:: -------------------------------------------------------------------------
echo [1/6] Checking Python installation...
set "PY_CMD="
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.11 or higher from https://www.python.org/downloads/
    echo Make sure to check Add Python to PATH during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo       Found %PY_VER%

:: -------------------------------------------------------------------------
:: 2. Check Node.js and npm
:: -------------------------------------------------------------------------
echo [2/6] Checking Node.js and npm...
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in your system PATH.
    echo Please install Node.js [v18+] from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not installed or not in your system PATH.
    echo Please install Node.js [which bundles npm] from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node -v 2^>^&1') do set "NODE_VER=%%v"
for /f "tokens=*" %%v in ('npm -v 2^>^&1') do set "NPM_VER=%%v"
echo       Found Node.js %NODE_VER% and npm %NPM_VER%

:: -------------------------------------------------------------------------
:: 3. Setup Portable PostgreSQL Database
:: -------------------------------------------------------------------------
echo [3/6] Checking PostgreSQL database setup...

if not exist "%~dp0pgsql\bin\postgres.exe" (
    echo       Portable PostgreSQL not found in SIH64\pgsql.
    echo       Downloading PostgreSQL 16 portable binaries for Windows [approx 320MB]...
    echo       Please wait, this will only happen once...
    
    set "DOWNLOADER="
    where aria2c >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        aria2c -x 8 -s 8 -k 1M -o "pgsql.zip" "https://get.enterprisedb.com/postgresql/postgresql-16.4-1-windows-x64-binaries.zip"
    ) else (
        where curl >nul 2>nul
        if !ERRORLEVEL! equ 0 (
            curl -L -# -o "pgsql.zip" "https://get.enterprisedb.com/postgresql/postgresql-16.4-1-windows-x64-binaries.zip"
        ) else (
            powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://get.enterprisedb.com/postgresql/postgresql-16.4-1-windows-x64-binaries.zip', 'pgsql.zip')"
        )
    )

    if not exist "pgsql.zip" (
        echo [ERROR] Failed to download PostgreSQL binaries archive.
        echo Please verify your internet connection or download it manually.
        pause
        exit /b 1
    )

    echo       Extracting PostgreSQL binaries...
    tar -xf pgsql.zip
    del /f /q pgsql.zip >nul 2>nul
)

if not exist "%~dp0pgsql\bin\postgres.exe" (
    echo [ERROR] PostgreSQL binaries could not be located in %~dp0pgsql\bin.
    pause
    exit /b 1
)

:: Check if cluster data directory exists
if not exist "%~dp0pgsql\data\PG_VERSION" (
    echo       Initializing local database cluster in SIH64\pgsql\data...
    "%~dp0pgsql\bin\initdb.exe" -D "%~dp0pgsql\data" -U postgres -A trust -E UTF8 --locale=C >nul 2>nul
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] initdb failed to create database cluster.
        pause
        exit /b 1
    )
)

:: Ensure .env exists
if not exist "%~dp0.env" (
    echo       Creating default .env configuration...
    copy /y "%~dp0.env.example" "%~dp0.env" >nul
)
if not exist "%~dp0backend\.env" (
    copy /y "%~dp0.env" "%~dp0backend\.env" >nul
)

:: Start PostgreSQL server if not responding
"%~dp0pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5432 >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo       Starting local PostgreSQL server on port 5432...
    start "AICTE PostgreSQL Server" /MIN "%~dp0pgsql\bin\postgres.exe" -D "%~dp0pgsql\data"
    
    :: Wait up to 10 seconds for PostgreSQL to be ready
    set "PG_READY=0"
    for /l %%i in (1,1,10) do (
        if !PG_READY! equ 0 (
            ping 127.0.0.1 -n 2 >nul
            "%~dp0pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5432 >nul 2>nul
            if !ERRORLEVEL! equ 0 set "PG_READY=1"
        )
    )
    if !PG_READY! equ 0 (
        echo [WARNING] PostgreSQL did not confirm ready state yet; continuing...
    ) else (
        echo       PostgreSQL is running and ready on port 5432.
    )
) else (
    echo       PostgreSQL is already active and ready on port 5432.
)

:: Ensure aicte_complaints database exists
"%~dp0pgsql\bin\psql.exe" -U postgres -h 127.0.0.1 -lqt 2>nul | findstr /I "aicte_complaints" >nul
if %ERRORLEVEL% neq 0 (
    echo       Creating database 'aicte_complaints'...
    "%~dp0pgsql\bin\createdb.exe" -U postgres -h 127.0.0.1 aicte_complaints >nul 2>nul
    "%~dp0pgsql\bin\createdb.exe" -U postgres -h 127.0.0.1 aicte_complaints_test >nul 2>nul
    set "AUTO_SEED=1"
)

:: -------------------------------------------------------------------------
:: 4. Setup Backend Virtual Environment & Dependencies
:: -------------------------------------------------------------------------
echo [4/6] Checking Python backend virtual environment...
if not exist "%~dp0backend\.venv\Scripts\python.exe" (
    echo       Creating virtual environment in backend\.venv...
    %PY_CMD% -m venv "%~dp0backend\.venv"
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PY=%~dp0backend\.venv\Scripts\python.exe"

:: Check if core packages are installed
"%VENV_PY%" -c "import flask, psycopg2, rapidfuzz, sqlalchemy" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo       Installing backend requirements from backend\requirements.txt...
    "%VENV_PY%" -m pip install --upgrade pip >nul 2>nul
    "%VENV_PY%" -m pip install -r "%~dp0backend\requirements.txt"
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to install backend requirements.
        pause
        exit /b 1
    )
    echo       Backend requirements installed successfully.
) else (
    echo       Backend Python packages verified.
)

:: Seed database if fresh or requested
if "%AUTO_SEED%"=="1" (
    echo       Seeding initial database with SIH 2026 data...
    cd /d "%~dp0backend"
    "%VENV_PY%" seed.py
    cd /d "%~dp0"
)

:: -------------------------------------------------------------------------
:: 5. Setup Frontend Dependencies
:: -------------------------------------------------------------------------
echo [5/6] Checking Frontend npm dependencies...
if not exist "%~dp0frontend\node_modules" (
    echo       Installing frontend dependencies with npm install...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] npm install encountered errors.
        pause
        exit /b 1
    )
    echo       Frontend dependencies installed successfully.
) else (
    echo       Frontend dependencies verified.
)

:: -------------------------------------------------------------------------
:: 6. Launch Backend & Frontend Servers
:: -------------------------------------------------------------------------
echo [6/6] Launching Servers...

:: Kill any existing processes on 5000 and 5173 to avoid port collisions
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>nul

echo       Starting Flask REST API on http://localhost:5000 ...
start "AICTE Backend API (Port 5000)" cmd /k "cd /d "%~dp0backend" && .\.venv\Scripts\python.exe run.py"

echo       Starting Vite Frontend on http://localhost:5173 ...
start "AICTE Frontend Web (Port 5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo =========================================================================
echo    SUCCESS! AICTE Complaint Portal is starting up.
echo =========================================================================
echo    Frontend URL : http://localhost:5173
echo    Backend API  : http://localhost:5000/api/health
echo    Database     : PostgreSQL 16 on 127.0.0.1:5432
echo.
echo    Default Roles ^& Credentials:
echo    -----------------------------------------------------------------
echo    1. SYSTEM ADMIN : admin    / admin    (admin@aicte.gov.in)
echo    2. INDUSTRY     : industry / industry (industry@aicte.gov.in)
echo    3. COMPLAINANT  : user     / user     (user@aicte.gov.in)
echo =========================================================================
echo.

:: Wait 3 seconds and launch the browser
ping 127.0.0.1 -n 4 >nul
start http://localhost:5173

:MENU
echo Actions:
echo   [B] Open browser to http://localhost:5173
echo   [S] Run database seed script [backend\seed.py]
echo   [Q] Stop all servers and exit
echo.
set /p "CHOICE=Select an option [B/S/Q]: "

if /i "%CHOICE%"=="B" (
    start http://localhost:5173
    goto MENU
)
if /i "%CHOICE%"=="S" (
    echo Re-seeding database...
    cd /d "%~dp0backend"
    "%VENV_PY%" seed.py
    cd /d "%~dp0"
    goto MENU
)
if /i "%CHOICE%"=="Q" (
    echo Stopping servers...
    call "%~dp0stop.bat"
    echo Bye!
    exit /b 0
)

goto MENU
