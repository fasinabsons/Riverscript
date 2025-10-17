@echo off
REM ============================================================
REM   🏅 KaratMate Labs - Remove Scheduled Tasks
REM ============================================================

echo.
echo ============================================================
echo   🏅 KaratMate Labs - Remove Scheduled Tasks
echo ============================================================
echo.
echo This will REMOVE all KaratMate scheduled tasks:
echo   - KaratMate_MorningUpdate
echo   - KaratMate_AfternoonUpdate
echo   - KaratMate_EveningUpdate
echo.
echo ============================================================
echo.
pause

echo.
echo Removing scheduled tasks...
echo.

REM Remove Morning Update
echo [1/3] Removing Morning Update task...
schtasks /delete /tn "KaratMate_MorningUpdate" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Morning task removed
) else (
    echo    ℹ️  Morning task not found or already removed
)

REM Remove Afternoon Update
echo.
echo [2/3] Removing Afternoon Update task...
schtasks /delete /tn "KaratMate_AfternoonUpdate" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Afternoon task removed
) else (
    echo    ℹ️  Afternoon task not found or already removed
)

REM Remove Evening Update
echo.
echo [3/3] Removing Evening Update task...
schtasks /delete /tn "KaratMate_EveningUpdate" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Evening task removed
) else (
    echo    ℹ️  Evening task not found or already removed
)

echo.
echo ============================================================
echo   ✅ Task Removal Complete!
echo ============================================================
echo.
pause

