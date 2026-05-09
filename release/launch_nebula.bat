@echo off
setlocal

:: Get the directory of the script
set "BASE_DIR=%~dp0"

echo Starting NebulaTorrent Backend...
start /b "" "%BASE_DIR%backend\main.exe"

echo Starting Frontend Web Server...
:: We can use a simple python server to host the built frontend dist
start /b "" python -m http.server 5173 --directory "%BASE_DIR%frontend"

echo.
echo NebulaTorrent is starting!
echo Access the application at: http://localhost:5173
echo.
echo Press any key to stop both services...
pause > nul

:: Stop services
taskkill /F /IM main.exe
echo Services stopped.
