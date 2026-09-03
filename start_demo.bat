@echo off
echo Starting LoomIQ AI-Powered Textile Manufacturing Intelligence Demo...
cd /d "%~dp0"
call venv\Scripts\activate
start "LoomIQ Backend" cmd /c "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
echo Backend started on http://localhost:8000
echo.
echo Launching frontend...
start "" "http://localhost:8000/"
echo LoomIQ is now running.
pause
