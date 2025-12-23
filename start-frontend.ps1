# Frontend Launcher
# Запускается из 4-start-frontend.bat

# Get script directory
if ($PSScriptRoot) {
    $scriptPath = $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $scriptPath = Get-Location
}

$frontendPath = Join-Path $scriptPath "frontend\moderator-dashboard-ui"

Set-Location $frontendPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend (Port 5173)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

npm run dev

