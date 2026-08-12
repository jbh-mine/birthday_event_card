param(
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$port = 4173
$url = "http://localhost:$port/"
$pidFile = Join-Path $projectRoot ".local-birthday-server.pid"
$stdoutLog = Join-Path $projectRoot ".local-birthday.stdout.log"
$stderrLog = Join-Path $projectRoot ".local-birthday.stderr.log"

function Get-CompatibleNode {
  $candidates = @(
    (Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"),
    (Join-Path $env:ProgramFiles "nodejs\node.exe")
  )

  $pathNode = Get-Command node.exe -ErrorAction SilentlyContinue
  if ($pathNode) {
    $candidates += $pathNode.Source
  }

  foreach ($candidate in ($candidates | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath $candidate)) { continue }
    try {
      $version = (& $candidate --version).TrimStart("v")
      if ([int]($version.Split(".")[0]) -ge 22) {
        return $candidate
      }
    } catch {
      continue
    }
  }

  throw "Node.js 22 이상이 필요합니다. https://nodejs.org 에서 LTS 버전을 설치해 주세요."
}

function Test-BirthdayServerProcess([int]$processId) {
  $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
  if (-not $process) { return $false }
  if ($process.CommandLine -notlike "*scripts*vinext.mjs*dev*--port*$port*") { return $false }

  $child = Get-CimInstance Win32_Process -Filter "ParentProcessId = $processId" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*$projectRoot*node_modules*vinext*cli.js*dev*--port*$port*" } |
    Select-Object -First 1
  return $null -ne $child
}

Set-Location -LiteralPath $projectRoot

if (Test-Path -LiteralPath $pidFile) {
  $savedPid = [int](Get-Content -Raw -LiteralPath $pidFile)
  if (Test-BirthdayServerProcess $savedPid) {
    if (-not $NoBrowser) { Start-Process $url }
    Write-Host "생일 편지가 열렸습니다: $url"
    exit 0
  }
  Remove-Item -LiteralPath $pidFile -Force
}

$node = Get-CompatibleNode
$vinext = Join-Path $projectRoot "node_modules\vinext\dist\cli.js"
if (-not (Test-Path -LiteralPath $vinext)) {
  throw "실행에 필요한 파일이 없습니다. C:\bbbb 폴더에서 npm install을 먼저 실행해 주세요."
}

$server = Start-Process -FilePath $node `
  -ArgumentList @("scripts/vinext.mjs", "dev", "--port", "$port") `
  -WorkingDirectory $projectRoot `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -WindowStyle Hidden `
  -PassThru

Set-Content -LiteralPath $pidFile -Value $server.Id -NoNewline

$ready = $false
for ($attempt = 0; $attempt -lt 120; $attempt++) {
  Start-Sleep -Milliseconds 500
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
      $ready = $true
      break
    }
  } catch {
    if ($server.HasExited) { break }
  }
}

if (-not $ready) {
  throw "생일 편지를 시작하지 못했습니다. .local-birthday.stderr.log 파일을 확인해 주세요."
}

if (-not $NoBrowser) { Start-Process $url }
Write-Host "생일 편지가 열렸습니다: $url"
