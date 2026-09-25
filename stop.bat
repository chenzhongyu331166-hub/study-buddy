@echo off
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*study-buddy*app.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo StudyBuddy server stopped.
