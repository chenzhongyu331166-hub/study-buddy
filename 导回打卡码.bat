@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   把「今日任务」网页生成的打卡码写回学习台
echo   不需要重启任何东西
echo ============================================
echo.
set "PY=venv\Scripts\python.exe"
echo 可以把打卡码直接拖到这个窗口，或者复制打卡码后按回车
echo 打卡码格式：SB1 D11 2026-10-07 3 101 1
echo.
"%PY%" "%~dp0导入打卡码.py" %*
echo.
pause