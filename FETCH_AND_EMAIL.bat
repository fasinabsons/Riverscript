@echo off
echo ============================================================
echo   🏅 KaratMate Labs - Fetch Prices and Send Email
echo ============================================================
echo.
echo This will:
echo   1. Fetch live gold prices from Joy Alukkas and Candere
echo   2. Calculate sovereign prices (8g and 16g)
echo   3. Calculate customs duty (Red and Green channels)
echo   4. Send complete email report with all calculations
echo.
echo ============================================================
echo.

cd backend

echo Fetching prices and sending email...
echo.

python -c "import requests; r = requests.post('http://localhost:5002/api/fetch-and-email'); print('\n'); print('='*60); print(r.json() if r.status_code == 200 else 'Error: API not running. Start it first!'); print('='*60)"

echo.
echo ============================================================
echo   Done! Check your email: faseen1532@gmail.com
echo ============================================================
echo.
pause

