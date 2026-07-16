@echo off
:: LAN Startup Script for Windows Server / Windows PC
title 2-Phase Buck LAN Simulation Server
cd /d %~dp0

if exist .venv\Scripts\activate.bat (
    echo Found virtual environment. Activating .venv and starting Streamlit server...
    call .venv\Scripts\activate.bat
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
) else (
    echo No virtual environment folder found. Attempting to start with system python...
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
)
pause
