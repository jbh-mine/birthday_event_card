$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot ".local-birthday-server.pid"
$port = 4173

function Stop-ProcessTree([int]$processId) {
  $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $processId" -ErrorAction SilentlyContinue
  foreach ($child in $children) {
    Stop-ProcessTree $child.ProcessId
  }
  Stop-Process -Id $processId -ErrorAction SilentlyContinue
}

if (-not (Test-Path -LiteralPath $pidFile)) {
  Write-Host "실행 중인 생일 편지가 없습니다."
  exit 0
}

$savedPid = [int](Get-Content -Raw -LiteralPath $pidFile)
$process = Get-CimInstance Win32_Process -Filter "ProcessId = $savedPid" -ErrorAction SilentlyContinue
$child = Get-CimInstance Win32_Process -Filter "ParentProcessId = $savedPid" -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -like "*$projectRoot*node_modules*vinext*cli.js*dev*--port*$port*" } |
  Select-Object -First 1

if (
  $process -and
  $process.CommandLine -like "*scripts*vinext.mjs*dev*--port*$port*" -and
  $child
) {
  Stop-ProcessTree $savedPid
  Write-Host "생일 편지를 종료했습니다."
} else {
  Write-Host "저장된 실행 정보가 만료되어 정리했습니다."
}

Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
