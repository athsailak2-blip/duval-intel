@echo off
REM Duval County Lead Intelligence - Daily Refresh
REM Run this script via Windows Task Scheduler

echo Starting Duval County refresh...
cd /d "%~dp0.."

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.12+
    exit /b 1
)

REM Run refresh
python scripts/daily_refresh.py

if errorlevel 1 (
    echo Refresh completed with errors
    exit /b 1
) else (
    echo Refresh completed successfully
)
