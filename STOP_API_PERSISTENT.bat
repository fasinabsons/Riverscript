@echo off
REM ============================================================
REM   🏅 KaratMate Labs - Stop API Server
REM ============================================================

echo.
echo ============================================================
echo   🏅 KaratMate Labs - Stopping API Server
echo ============================================================
echo.
echo Searching for running API server...
echo.

REM Kill Python processes running price_fetcher_api.py
taskkill /FI "WINDOWTITLE eq KaratMate API Server*" /F >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ API Server stopped successfully!
) else (
    echo ℹ️  No running API server found
)

echo.
echo ============================================================
pause

