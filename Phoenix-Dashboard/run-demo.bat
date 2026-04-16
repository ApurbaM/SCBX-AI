@echo off
setlocal
set "ROOT=%~dp0"
REM Serve repository root so /SCB_CXO_Board_Dashboard.html (single canonical file) resolves.
set "REPO=%~dp0.."
REM If this port is already in use, change PORT (e.g. 8890) and run again.
set "PORT=8889"
set "BASE=http://127.0.0.1:%PORT%"
set "DASH=%BASE%/SCB_CXO_Board_Dashboard.html"

cd /d "%REPO%"

set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE (
  echo.
  echo  Python was not found in PATH.
  echo  Install Python 3, then run this batch again.
  echo.
  pause
  exit /b 1
)

echo.
echo  Phoenix Dashboard — local HTTP server
echo  --------------------------------------
echo  Repo root: %CD%
echo  Dashboard: %DASH%
echo  Hub:       %BASE%/index.html
echo.
echo  A second window will keep the server running; close it to stop.
echo.

start "Phoenix Dashboard server :%PORT%" /D "%CD%" cmd /k "%PYEXE% -m http.server %PORT%"

timeout /t 2 /nobreak >nul
start "" "%DASH%"

echo  Opened your browser to the dashboard URL above.
echo.
pause
