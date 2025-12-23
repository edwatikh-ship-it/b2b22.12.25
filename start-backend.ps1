# Backend Launcher
# Запускается из 3-start-backend.bat

# Get script directory
if ($PSScriptRoot) {
    $scriptPath = $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $scriptPath = Get-Location
}

# Set backend directory
$backendPath = Join-Path $scriptPath "backend"
Set-Location $backendPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend API (Port 8000)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Backend..." -ForegroundColor Yellow
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Start backend from backend directory
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

