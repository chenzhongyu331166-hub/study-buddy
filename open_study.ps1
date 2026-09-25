# 学习台一键启动：服务没起就拉起，然后打开浏览器
$url = 'http://127.0.0.1:5000'
$root = 'D:\VibeBuddy\study-buddy'
$up = $false
try { Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 2 | Out-Null; $up = $true } catch {}

if (-not $up) {
    $running = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
        Where-Object { $_.CommandLine -like '*study-buddy*app.py*' }
    if (-not $running) {
        Start-Process -FilePath "$root\venv\Scripts\pythonw.exe" -ArgumentList "$root\app.py" -WorkingDirectory $root
    }
    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Seconds 1
        try { Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 2 | Out-Null; $up = $true; break } catch {}
    }
}
Start-Process $url
