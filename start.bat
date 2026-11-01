@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo   Filomino Puzzle - launcher
echo ============================================
echo.

REM ---------- Prerequisites ----------
where python >nul 2>&1 || (
    echo [ERROR] Python was not found on PATH. Install it from https://www.python.org and try again.
    pause
    exit /b 1
)
where npm >nul 2>&1 || (
    echo [ERROR] Node.js/npm was not found on PATH. Install Node.js from https://nodejs.org and try again.
    pause
    exit /b 1
)

REM ---------- Backend dependencies ----------
call python -c "import flask, flask_cors" >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies ^(flask, flask-cors^)...
    call python -m pip install --quiet flask flask-cors || goto :fail
)

REM ---------- Frontend dependencies ----------
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies ^(first run only, may take a while^)...
    pushd frontend
    call npm install --no-audit --no-fund || (popd & goto :fail)
    popd
)

REM ---------- Backend: reuse if already running, otherwise start hidden ----------
set "API_PID="
call python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/api/health',timeout=2)" >nul 2>&1
if not errorlevel 1 goto :reuse_api

echo Starting backend API on http://127.0.0.1:5000 ...
del "%TEMP%\filomino-api.pid" >nul 2>&1
powershell -NoProfile -Command "$p = Start-Process python -ArgumentList 'app.py' -WorkingDirectory '%~dp0backend' -WindowStyle Hidden -RedirectStandardOutput '%TEMP%\filomino-api.log' -RedirectStandardError '%TEMP%\filomino-api-error.log' -PassThru; Set-Content -Path '%TEMP%\filomino-api.pid' -Value $p.Id"
set "API_PID="
if exist "%TEMP%\filomino-api.pid" set /p API_PID=<"%TEMP%\filomino-api.pid"
if not defined API_PID goto :backend_failed

set /a tries=0
:wait_api
call python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/api/health',timeout=2)" >nul 2>&1 && goto :api_up
set /a tries+=1
if %tries% geq 30 goto :backend_failed
timeout /t 1 /nobreak >nul
goto :wait_api

:api_up
echo Backend ready.
goto :launch_frontend

:reuse_api
echo Reusing backend already running on port 5000.
echo Backend ready.

REM ---------- Frontend (blocks until the game window is closed) ----------
:launch_frontend
pushd frontend
call npm start
popd

if defined API_PID taskkill /PID %API_PID% /T /F >nul 2>&1
echo.
echo Game closed - backend stopped. Goodbye!
exit /b 0

:backend_failed
if defined API_PID taskkill /PID %API_PID% /T /F >nul 2>&1
echo.
echo [ERROR] Backend did not become healthy within 30 seconds.
echo Check "%TEMP%\filomino-api-error.log" for details (a stale process on port 5000 is a common cause).
pause
exit /b 1

:fail
echo.
echo [ERROR] Startup failed - see messages above.
pause
exit /b 1
