@echo off
cd /d "%~dp0"
set PYTHONUNBUFFERED=1

echo.
echo  SCBx local demo server
echo  ----------------------
echo  Serves this folder on 127.0.0.1 and tries ports 8844, 8845, ...
echo  Your browser should open the CXO dashboard automatically.
echo  If it does not, copy the http://127.0.0.1:PORT/... line from below.
echo  Press Ctrl+C to stop the server.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py serve_local.py
) else (
  python serve_local.py
)

echo.
echo Server stopped.
pause
