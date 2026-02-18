@echo off
TITLE ProInsight SaaS Launcher
echo starting ProInsight SaaS (FastAPI + Streamlit)...
echo.

:: Start Backend in a new window
echo [SERVER] Launching FastAPI Backend...
start cmd /k "cd backend && ..\venv\Scripts\python.exe main.py"

:: Wait a few seconds for backend to start
timeout /t 5

:: Start Frontend
echo [CLIENT] Launching Streamlit Frontend...
cd frontend && ..\venv\Scripts\python.exe -m streamlit run app.py

pause
