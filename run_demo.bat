@echo off
setlocal EnableExtensions
REM ============================================================
REM  Smart Tutor - one-click local demo for Windows
REM  Needs Python 3.10+ and Node.js 18+
REM ============================================================
cd /d "%~dp0"
title Smart Tutor setup

if not exist "backend\requirements.txt" (
  echo [ERROR] This file must stay inside the smart-tutor folder,
  echo         next to the "backend" and "frontend" folders.
  echo         Current folder: %cd%
  goto :fail
)

REM ---------- find a real Python 3.10+ (skips the Microsoft Store stub) ----------
set "PY="
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set "PY=python"
if not defined PY (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  echo [ERROR] Python 3.10 or newer was not found.
  echo         Install Python 3.12 from https://www.python.org/downloads/
  echo         and TICK "Add python.exe to PATH" on the first install screen.
  echo         Then close this window and run run_demo.bat again.
  goto :fail
)
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo Found %%v

REM ---------- check Node.js ----------
where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js was not found.
  echo         Install the LTS version from https://nodejs.org/ then restart your PC.
  goto :fail
)
for /f "delims=" %%v in ('node --version') do echo Found Node.js %%v

REM ---------- 1. Python packages ----------
echo.
echo [1/4] Setting up Python packages (first time takes a few minutes)...
if not exist "backend\.venv\Scripts\python.exe" (
  %PY% -m venv "backend\.venv"
  if errorlevel 1 ( echo [ERROR] Could not create the Python virtual environment. & goto :fail )
)
set "VPY=%~dp0backend\.venv\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip >nul 2>nul
"%VPY%" -m pip install -r "backend\requirements.txt"
if errorlevel 1 ( echo [ERROR] Installing Python packages failed - see the messages above. & goto :fail )
if not exist "backend\.env" copy "backend\.env.example" "backend\.env" >nul

REM ---------- 2. Web interface ----------
echo.
echo [2/4] Building the web interface...
pushd frontend
if not exist "node_modules" (
  call npm install --no-audit --no-fund
  if errorlevel 1 ( popd & echo [ERROR] npm install failed - see the messages above. & goto :fail )
)
call npm run build
if errorlevel 1 ( popd & echo [ERROR] Building the web interface failed - see the messages above. & goto :fail )
popd

REM ---------- 3. ML model + demo data ----------
echo.
echo [3/4] Training the ML model and loading demo data...
pushd backend
if not exist "ml\artifacts\risk_model.joblib" (
  "%VPY%" -m ml.train
  if errorlevel 1 ( popd & echo [ERROR] Model training failed. & goto :fail )
)
"%VPY%" -m app.seed
if errorlevel 1 ( popd & echo [ERROR] Loading demo data failed. & goto :fail )

REM ---------- 4. Start ----------
echo.
echo [4/4] Starting Smart Tutor...
echo ============================================================
echo   Open  http://localhost:8000  in your browser
echo   Keep THIS window open while using the app. Press Ctrl+C to stop.
echo ============================================================
start "" "http://localhost:8000"
"%VPY%" -m uvicorn app.main:app --port 8000
popd
echo.
echo The server stopped. If you see "address already in use", another program is using port 8000:
echo restart your PC, or close the other Smart Tutor window, and try again.
pause
exit /b 0

:fail
echo.
echo ------------------------------------------------------------
echo  Setup stopped. Take a screenshot of this window and share it.
echo ------------------------------------------------------------
pause
exit /b 1
