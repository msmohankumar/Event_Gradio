@echo off
cd /d "%~dp0"
echo Starting Local Event Photo Finder...
python -m streamlit run local_event_app.py --server.address 0.0.0.0 --server.port 8501
pause
