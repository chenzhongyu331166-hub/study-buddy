@echo off
rem 学伴 StudyBuddy 启动器（使用脚本自身所在目录，换电脑/换目录都能跑）
cd /d "%~dp0"
set "PY=%~dp0venv\Scripts\pythonw.exe"
if not exist "%PY%" set "PY=pythonw"
start "" "%PY%" "%~dp0app.py"
timeout /t 2 >nul
start "" http://127.0.0.1:5000
