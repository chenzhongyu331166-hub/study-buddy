@echo off
cd /d D:\VibeBuddy\study-buddy
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0app.py"
timeout /t 2 >nul
start "" http://127.0.0.1:5000
