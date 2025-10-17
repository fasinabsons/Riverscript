@echo off
REM ============================================================
REM   🏅 KaratMate Labs - Setup Scheduled Tasks
REM   Creates Windows Task Scheduler tasks for automatic price fetching
REM ============================================================

echo.
echo ============================================================
echo   🏅 KaratMate Labs - Task Scheduler Setup
echo ============================================================
echo.
echo This will create 3 scheduled tasks:
echo   1. Morning Update   - 9:00 AM daily
echo   2. Afternoon Update - 5:00 PM daily  
echo   3. Evening Update   - 8:00 PM daily (UAE price update time)
echo.
echo All tasks will run FETCH_AND_EMAIL.bat
echo.
echo ============================================================
echo.
pause

REM Get the current directory
set "SCRIPT_DIR=%~dp0"
set "BATCH_FILE=%SCRIPT_DIR%FETCH_AND_EMAIL.bat"

echo.
echo Creating scheduled tasks...
echo.

REM Task 1: Morning Update (9:00 AM)
echo [1/3] Creating Morning Update task (9:00 AM)...
schtasks /create /tn "KaratMate_MorningUpdate" /tr "\"%BATCH_FILE%\"" /sc daily /st 09:00 /f
if %errorlevel% equ 0 (
    echo    ✅ Morning task created successfully
) else (
    echo    ❌ Failed to create morning task
)

REM Task 2: Afternoon Update (5:00 PM)
echo.
echo [2/3] Creating Afternoon Update task (5:00 PM)...
schtasks /create /tn "KaratMate_AfternoonUpdate" /tr "\"%BATCH_FILE%\"" /sc daily /st 17:00 /f
if %errorlevel% equ 0 (
    echo    ✅ Afternoon task created successfully
) else (
    echo    ❌ Failed to create afternoon task
)

REM Task 3: Evening Update (8:00 PM - Main UAE update time)
echo.
echo [3/3] Creating Evening Update task (8:00 PM)...
schtasks /create /tn "KaratMate_EveningUpdate" /tr "\"%BATCH_FILE%\"" /sc daily /st 20:00 /f
if %errorlevel% equ 0 (
    echo    ✅ Evening task created successfully
) else (
    echo    ❌ Failed to create evening task
)

echo.
echo ============================================================
echo   ✅ Task Scheduler Setup Complete!
echo ============================================================
echo.
echo Scheduled Tasks Created:
echo   📧 KaratMate_MorningUpdate   - Daily at 9:00 AM
echo   📧 KaratMate_AfternoonUpdate - Daily at 5:00 PM
echo   📧 KaratMate_EveningUpdate   - Daily at 8:00 PM
echo.
echo To view tasks: Open Task Scheduler (taskschd.msc)
echo To disable: Right-click task and select "Disable"
echo To delete: Right-click task and select "Delete"
echo.
echo ⚠️  IMPORTANT: Make sure the API server is running!
echo    Run START_KARATMETER.bat to start the API server.
echo.
echo ============================================================
pause

