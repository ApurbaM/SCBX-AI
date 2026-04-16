@echo off
setlocal EnableExtensions
set PYTHONUNBUFFERED=1
set "URLFILE=%TEMP%\scbx_dashboard_url.txt"

rem Trailing dot avoids CMD bugs when path ends with backslash (e.g. OneDrive paths).
cd /d "%~dp0."
del "%URLFILE%" >nul 2>&1

echo.
echo  SCBx local server
echo  -----------------
echo  A separate window will run the HTTP server. This window opens your browser
echo  after the server is ready (correct port even if 8844 is busy).
echo  If nothing loads, read the BLACK server window for Python errors.
echo.

where py >nul 2>&1 && (
  start "SCBx HTTP server" /D "%~dp0." cmd /k py -3 serve_local.py
  goto WAIT_OPEN
)
where python >nul 2>&1 && (
  start "SCBx HTTP server" /D "%~dp0." cmd /k python serve_local.py
  goto WAIT_OPEN
)

echo ERROR: Neither "py" nor "python" was found in PATH.
echo Install Python 3 from https://www.python.org/downloads/ and enable "Add to PATH".
pause
exit /b 1

:WAIT_OPEN
set /a tries=0

:waitagain
ping 127.0.0.1 -n 2 >nul
if exist "%URLFILE%" (
  for /f "usebackq delims=" %%u in ("%URLFILE%") do start "" "%%u"
  goto opened
)
set /a tries+=1
if %tries% GEQ 45 goto openfallback
goto waitagain

:openfallback
start "" "http://127.0.0.1:8844/SCB_CXO_Board_Dashboard.html"
echo.
echo  WARNING: Server URL file was not created in time. Tried default port 8844.
echo  Check the server window for the real link or Python errors.

:opened
echo.
echo  You may close this window. Stop the site with Ctrl+C in the server window.
pause
endlocal
