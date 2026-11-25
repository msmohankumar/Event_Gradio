@echo off
cd /d "%~dp0"
echo Creating a temporary public URL for the local app on port 8501.
echo Ensure the local app is already running in another window.
cloudflared tunnel --url http://localhost:8501
pause
