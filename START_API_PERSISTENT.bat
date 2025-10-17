@echo off
REM ============================================================
REM   🏅 KaratMate Labs - Start API Server (Persistent)
REM   Keeps the API running in background for scheduled tasks
REM ============================================================

echo.
echo ============================================================
echo   🏅 KaratMate Labs - Starting API Server
echo ============================================================
echo.
echo Starting API server in background...
echo This window will minimize automatically.
echo.
echo To stop the API: Close the "KaratMate API Server" window
echo                  or run STOP_API_PERSISTENT.bat
echo.
echo ============================================================
echo.

REM Start API in minimized window
start "KaratMate API Server" /min cmd /k "cd /d %~dp0backend && python price_fetcher_api.py"

echo.
echo ✅ API Server started in background!
echo.
echo Server Status:
echo   URL: http://localhost:5002
echo   Window: Minimized (check taskbar)
echo.
echo The API will now handle scheduled task requests.
echo.
pause

