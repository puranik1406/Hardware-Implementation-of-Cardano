param(
  [switch]$Rebuild
)

$ErrorActionPreference = 'Stop'

Write-Host "[1/4] Ensuring Docker is running..." -ForegroundColor Cyan
# Simple check
try { docker version | Out-Null } catch { throw "Docker Desktop not running" }

Write-Host "[2/4] Starting services..." -ForegroundColor Cyan
Push-Location "$PSScriptRoot\.."
if ($Rebuild) { docker compose up -d --build } else { docker compose up -d }
Pop-Location

Write-Host "[3/4] Waiting for healthchecks..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Smoke tests
Write-Host "[4/4] Hitting health endpoints" -ForegroundColor Cyan
$svc = @(
  @{ Name='Masumi Payment'; Url='http://localhost:3001/health' },
  @{ Name='Cardano Integration'; Url='http://localhost:4002/health' },
  @{ Name='AI Agents'; Url='http://localhost:6001/health' }
)
foreach ($s in $svc) {
  try {
    $r = Invoke-RestMethod -Uri $s.Url -TimeoutSec 10
    Write-Host (" - {0}: OK" -f $s.Name) -ForegroundColor Green
  } catch {
    Write-Host (" - {0}: FAIL" -f $s.Name) -ForegroundColor Yellow
  }
}

Write-Host "Done. Dashboard: http://localhost:8090" -ForegroundColor Cyan
