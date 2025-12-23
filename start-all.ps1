# B2B Platform - Complete Launcher (2-click)
# Запускает Chrome и все сервисы в отдельных вкладках Windows Terminal

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "B2B Platform - Starting All Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project root directory
$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}

# Check if Windows Terminal is available
$wtPath = Get-Command wt.exe -ErrorAction SilentlyContinue
$useWindowsTerminal = $null -ne $wtPath

if (-not $useWindowsTerminal) {
    Write-Host "[WARN] Windows Terminal (wt.exe) not found!" -ForegroundColor Yellow
    Write-Host "  Will use separate PowerShell windows instead" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check prerequisites
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "  Python: $pythonCheck" -ForegroundColor Green

$nodeCheck = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "  Node.js: $nodeCheck" -ForegroundColor Green
Write-Host ""

# Step 2: Start Chrome Debug Mode
Write-Host "[2/6] Starting Chrome in debug mode..." -ForegroundColor Yellow
$chromeScript = Join-Path $projectRoot "start-chrome-debug.ps1"

if (Test-Path $chromeScript) {
    if ($useWindowsTerminal) {
        Start-Process wt.exe -ArgumentList @(
            "-w", "0", "new-tab",
            "-d", $projectRoot,
            "--title", "Chrome Debug (9222)",
            "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ".\start-chrome-debug.ps1"
        ) -WindowStyle Minimized
        Write-Host "  [OK] Chrome launched in Windows Terminal tab" -ForegroundColor Green
    } else {
        Start-Process powershell.exe -ArgumentList @(
            "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $chromeScript
        ) -WindowStyle Minimized
        Write-Host "  [OK] Chrome launched in separate PowerShell window" -ForegroundColor Green
    }
    
    # Wait for Chrome to start
    Write-Host "  Waiting for Chrome to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check Chrome CDP
    $cdpCheck = & curl.exe -s -m 3 "http://127.0.0.1:9222/json/version" 2>&1
    if ($LASTEXITCODE -eq 0 -and $cdpCheck -match '"Browser"') {
        Write-Host "  [OK] Chrome CDP is ready!" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Chrome CDP not ready yet, but continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARN] Chrome script not found: $chromeScript" -ForegroundColor Yellow
    Write-Host "  Continuing without Chrome..." -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Kill existing processes on ports
Write-Host "[3/6] Cleaning up ports..." -ForegroundColor Yellow

# Kill port 9003 (Parser Service)
$port9003 = netstat -ano | findstr ":9003"
if ($port9003) {
    Write-Host "  Killing process on port 9003..." -ForegroundColor Gray
    try {
        $portLine = $port9003 | Select-Object -First 1
        $pid = ($portLine -split '\s+')[-1]
        if ($pid -match '^\d+$') {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {}
}

# Kill port 8001 (Backend)
$port8001 = netstat -ano | findstr ":8001"
if ($port8001) {
    Write-Host "  Killing process on port 8001..." -ForegroundColor Gray
    try {
        $portLine = $port8001 | Select-Object -First 1
        $pid = ($portLine -split '\s+')[-1]
        if ($pid -match '^\d+$') {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {}
}

# Kill port 3000 (Frontend)
$port3000 = netstat -ano | findstr ":3000"
if ($port3000) {
    Write-Host "  Killing process on port 3000..." -ForegroundColor Gray
    try {
        $portLine = $port3000 | Select-Object -First 1
        $pid = ($portLine -split '\s+')[-1]
        if ($pid -match '^\d+$') {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {}
}
Write-Host ""

# Step 4: Start Parser Service in separate tab
Write-Host "[4/6] Starting Parser Service in separate tab..." -ForegroundColor Yellow
$parserScript = Join-Path $projectRoot "start-parser-service.ps1"

if ($useWindowsTerminal) {
    Start-Process wt.exe -ArgumentList @(
        "-w", "0", "new-tab",
        "-d", $projectRoot,
        "--title", "Parser Service (9003)",
        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ".\start-parser-service.ps1"
    ) -WindowStyle Minimized
    Write-Host "  [OK] Parser Service launched in Windows Terminal tab" -ForegroundColor Green
} else {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $parserScript
    ) -WindowStyle Minimized
    Write-Host "  [OK] Parser Service launched in separate PowerShell window" -ForegroundColor Green
}

# Wait for parser service to start
Write-Host "  Waiting for parser service..." -ForegroundColor Yellow
$parserReady = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    $healthCheck = & curl.exe -s -m 2 "http://127.0.0.1:9003/health" 2>&1
    if ($LASTEXITCODE -eq 0 -and $healthCheck -match '"status"') {
        $parserReady = $true
        Write-Host "  [OK] Parser Service is ready!" -ForegroundColor Green
        break
    }
    if ($i % 5 -eq 0) {
        Write-Host "    Waiting... ($i/30)" -ForegroundColor Gray
    }
}
if (-not $parserReady) {
    Write-Host "  [WARN] Parser Service not ready after 30 seconds" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Start Backend in separate tab
Write-Host "[5/6] Starting Backend in separate tab..." -ForegroundColor Yellow
$backendScript = Join-Path $projectRoot "start-backend.ps1"

if ($useWindowsTerminal) {
    Start-Process wt.exe -ArgumentList @(
        "-w", "0", "new-tab",
        "-d", $projectRoot,
        "--title", "Backend API (8001)",
        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ".\start-backend.ps1"
    ) -WindowStyle Minimized
    Write-Host "  [OK] Backend launched in Windows Terminal tab" -ForegroundColor Green
} else {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript
    ) -WindowStyle Minimized
    Write-Host "  [OK] Backend launched in separate PowerShell window" -ForegroundColor Green
}

# Wait for backend to start
Write-Host "  Waiting for backend..." -ForegroundColor Yellow
$backendReady = $false
for ($i = 1; $i -le 20; $i++) {
    Start-Sleep -Seconds 1
    $backendCheck = & curl.exe -s -m 2 "http://localhost:8001/docs" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $backendReady = $true
        Write-Host "  [OK] Backend is ready!" -ForegroundColor Green
        break
    }
    if ($i % 5 -eq 0) {
        Write-Host "    Waiting... ($i/20)" -ForegroundColor Gray
    }
}
if (-not $backendReady) {
    Write-Host "  [WARN] Backend not ready after 20 seconds" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Start Frontend in separate tab
Write-Host "[6/6] Starting Frontend in separate tab..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend\moderator-dashboard-ui"

# Check .env.local
$envLocalPath = Join-Path $frontendPath ".env.local"
if (-not (Test-Path $envLocalPath)) {
    Set-Content -Path $envLocalPath -Value "NEXT_PUBLIC_API_URL=http://localhost:8001" -Encoding UTF8
}

# Install dependencies if needed
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "  Installing dependencies..." -ForegroundColor Gray
    Push-Location $frontendPath
    npm install 2>&1 | Out-Null
    Pop-Location
}

$frontendScript = Join-Path $projectRoot "start-frontend.ps1"

if ($useWindowsTerminal) {
    Start-Process wt.exe -ArgumentList @(
        "-w", "0", "new-tab",
        "-d", $projectRoot,
        "--title", "Frontend (3000)",
        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ".\start-frontend.ps1"
    ) -WindowStyle Minimized
    Write-Host "  [OK] Frontend launched in Windows Terminal tab" -ForegroundColor Green
} else {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript
    ) -WindowStyle Minimized
    Write-Host "  [OK] Frontend launched in separate PowerShell window" -ForegroundColor Green
}

# Wait for frontend to start
Write-Host "  Waiting for frontend..." -ForegroundColor Yellow
$frontendReady = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    $frontendCheck = & curl.exe -s -m 2 "http://localhost:3000" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $frontendReady = $true
        Write-Host "  [OK] Frontend is ready!" -ForegroundColor Green
        break
    }
    if ($i % 5 -eq 0) {
        Write-Host "    Waiting... ($i/30)" -ForegroundColor Gray
    }
}
if (-not $frontendReady) {
    Write-Host "  [WARN] Frontend not ready after 30 seconds" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SERVICES STATUS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Chrome Debug:     [OK] http://127.0.0.1:9222" -ForegroundColor Green
Write-Host "Parser Service:   $(if ($parserReady) { '[OK]' } else { '[FAIL]' }) http://127.0.0.1:9003" -ForegroundColor $(if ($parserReady) { "Green" } else { "Red" })
Write-Host "Backend API:      $(if ($backendReady) { '[OK]' } else { '[FAIL]' }) http://localhost:8001/docs" -ForegroundColor $(if ($backendReady) { "Green" } else { "Red" })
Write-Host "Frontend:         $(if ($frontendReady) { '[OK]' } else { '[FAIL]' }) http://localhost:3000/dashboard" -ForegroundColor $(if ($frontendReady) { "Green" } else { "Red" })
Write-Host ""
if ($useWindowsTerminal) {
    Write-Host "All services are running in separate Windows Terminal tabs!" -ForegroundColor Green
} else {
    Write-Host "All services are running in separate PowerShell windows!" -ForegroundColor Green
}
Write-Host ""

# Open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000/dashboard" -WindowStyle Minimized

Write-Host "Browser opened. All services are running!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
