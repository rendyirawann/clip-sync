@echo off
echo ============================================
echo   Clip-Sync: Refresh YouTube Cookies (Edge)
echo ============================================
echo.

:: Run as admin automatically
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo Extracting cookies from Microsoft Edge...
".venv\Scripts\python.exe" "extract_cookies.py"
echo.
echo Done! Cookies saved to cookies_auto.txt
echo You can now use YouTube links in Clip-Sync.
echo.
pause
