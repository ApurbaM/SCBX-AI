@echo off
cd /d "%~dp0"
echo Starting CXO API on http://127.0.0.1:8765  (set PORT=... to change)
python server\cxo_api.py
pause
