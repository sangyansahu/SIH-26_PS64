@echo off
setlocal enabledelayedexpansion
title AICTE Portal - Stop Servers
cd /d "%~dp0"

echo Stopping AICTE Portal services...

:: 1. Stop Flask Backend on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING 2^>nul') do (
    echo Stopping Backend API [PID %%a]...
    taskkill /f /pid %%a >nul 2>nul
)

:: 2. Stop Vite Frontend on port 5173
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING 2^>nul') do (
    echo Stopping Frontend Server [PID %%a]...
    taskkill /f /pid %%a >nul 2>nul
)

:: 3. Stop Portable PostgreSQL
if exist "%~dp0pgsql\bin\pg_ctl.exe" (
    if exist "%~dp0pgsql\data\PG_VERSION" (
        echo Stopping PostgreSQL server...
        "%~dp0pgsql\bin\pg_ctl.exe" -D "%~dp0pgsql\data" stop -m fast >nul 2>nul
    )
)

echo All AICTE Portal servers have been stopped.
echo.
ping 127.0.0.1 -n 2 >nul
