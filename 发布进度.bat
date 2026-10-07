@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 读取学习台记录，计算你真实学到第几天，推到 GitHub Pages
echo （公司电脑看的就是这个。不用重启，学习台开着关着都行）
echo.
set "PY=venv\Scripts\python.exe"
"%PY%" "%~dp0发布进度.py"
echo.
pause