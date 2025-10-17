@echo off
REM Gold Price Tracker - Schedule Daily Task
REM This creates a Windows Task Scheduler entry to run daily at 8:30 PM UAE time

title Gold Price Tracker - Task Scheduler Setup
color 0B

echo ================================
echo  Gold Price Tracker
echo  Windows Task Scheduler Setup
echo ================================
echo.

REM Get the full path to run_daily.bat
set SCRIPT_PATH=%~dp0run_daily.bat

echo This will create a scheduled task to run the gold price tracker
echo daily at 8:30 PM UAE time.
echo.
echo Script location: %SCRIPT_PATH%
echo.

pause

echo.
echo Creating scheduled task...
echo.

REM Create the scheduled task
schtasks /create /tn "GoldPriceTracker_Daily" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 20:30 /f

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================
    echo  SUCCESS!
    echo ================================
    echo.
    echo Task "GoldPriceTracker_Daily" has been created successfully.
    echo.
    echo The tracker will run every day at 8:30 PM (20:30).
    echo.
    echo To view the task:
    echo   1. Open Task Scheduler (taskschd.msc)
    echo   2. Look for "GoldPriceTracker_Daily"
    echo.
    echo To delete the task:
    echo   Run: schtasks /delete /tn "GoldPriceTracker_Daily" /f
) else (
    echo.
    echo ================================
    echo  ERROR!
    echo ================================
    echo.
    echo Failed to create scheduled task.
    echo Error code: %ERRORLEVEL%
    echo.
    echo You may need to run this script as Administrator.
    echo Right-click on schedule_daily.bat and select "Run as administrator"
)

echo.
pause

