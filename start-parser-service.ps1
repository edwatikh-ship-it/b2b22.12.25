# Parser Service Launcher
# Запускается из start-servers.ps1

# Get script directory - try multiple methods for reliability
if ($PSScriptRoot) {
    $scriptPath = $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $scriptPath = Get-Location
}

$parserServicePath = Join-Path $scriptPath "parser_service"

Set-Location $parserServicePath
$env:PYTHONPATH = $parserServicePath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Parser Service (Port 9003)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Parser Service..." -ForegroundColor Yellow
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

python -m uvicorn api:app --host 0.0.0.0 --port 9003

