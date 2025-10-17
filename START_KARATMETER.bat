@echo off
echo ============================================================
echo   🏅 KaratMate Labs - Startup Script
echo ============================================================
echo.
echo Starting KaratMate Labs API and Frontend...
echo.

REM Start the Python API server in a new window
echo [1/2] Starting KaratMate Labs API Server (port 5002)...
start "KaratMate Labs API" cmd /k "cd backend && python price_fetcher_api.py"

REM Wait 3 seconds for API to start
timeout /t 3 /nobreak >nul

REM Start the React frontend in a new window
echo [2/2] Starting React Frontend (port 5173)...
start "KaratMate Labs Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo   ✅ KaratMate Labs is starting!
echo ============================================================
echo.
echo API Server: http://localhost:5002
echo Frontend:   http://localhost:5173
echo.
echo Two windows have been opened:
echo   1. KaratMate Labs API (Python)
echo   2. KaratMate Labs Frontend (React)
echo.
echo Close those windows to stop the servers.
echo.
echo ============================================================
echo   Press any key to open the test page in browser...
echo ============================================================
pause >nul

REM Open test page in default browser
start test_karatmate.html

echo.
echo Done! You can close this window.
echo.
pause


