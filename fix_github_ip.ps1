# github连通性自愈：github.com:443被掐时，扫描可用IP并写入hosts
# 用法：右键用PowerShell运行，或 pwsh -File fix_github_ip.ps1
$hosts = "C:\Windows\System32\drivers\etc\hosts"
$candidates = @(
    "140.82.114.3", "140.82.113.3", "140.82.116.3", "140.82.121.4",
    "140.82.114.4", "20.27.177.113", "4.237.22.38", "20.205.243.166"
)

$working = $null
foreach ($ip in $candidates) {
    $code = curl.exe -s -o NUL -w "%{http_code}" --resolve "github.com:443:$ip" `
        --connect-timeout 5 --max-time 8 https://github.com/ 2>$null
    if ($code -eq "200") { $working = $ip; break }
}
if (-not $working) {
    Write-Output "没有可用IP(可能整体断网)，稍后再试"
    exit 1
}

$lines = Get-Content $hosts | Where-Object { $_ -notmatch "^\s*\d+\.\d+\.\d+\.\d+\s+github\.com\s*$" -and $_ -notmatch "github-ip-fallback" }
$lines += "# github-ip-fallback (auto $(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
$lines += "$working     github.com"
Set-Content -Path $hosts -Value $lines -Encoding ASCII
ipconfig /flushdns | Out-Null
Write-Output "hosts 已指向 $working"
