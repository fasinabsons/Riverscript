@echo off
REM Gold Price Tracker - Daily Runner
REM This script runs the price tracker and sends email notification

title Gold Price Tracker - Daily Run
color 0A

echo ================================
echo  Gold Price Tracker
echo  Daily Scheduled Run
echo ================================
echo.
echo Starting at: %date% %time%
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Run the tracker
python gold_tracker.py

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo  SUCCESS - Tracker completed
    echo ================================
) else (
    echo.
    echo ================================
    echo  ERROR - Tracker failed
    echo  Error Code: %ERRORLEVEL%
    echo ================================
)

echo.
echo Completed at: %date% %time%
echo.

REM Keep window open for 10 seconds to see results
timeout /t 10 /nobreak

exit /b %ERRORLEVEL%

