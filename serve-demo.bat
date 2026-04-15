@echo off
cd /d "%~dp0"
echo.
echo  SCBx local demo server
echo  ----------------------
echo  Port 8844 avoids Docker and other tools that often bind 8080.
echo  After this starts, open:
echo    http://localhost:8844/index.html
echo    http://localhost:8844/SCB_CXO_Board_Dashboard.html
echo.
echo  Press Ctrl+C to stop the server.
echo.
python -m http.server 8844
if errorlevel 1 (
  py -m http.server 8844
)
