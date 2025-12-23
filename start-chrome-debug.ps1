# Chrome Debug Mode Launcher
# Запускает Chrome с отладочным портом 9222

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHROME DEBUG MODE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$userProfile = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$defaultProfile = "Default"

# Check if Chrome with debug port is already running
Write-Host "Checking for existing Chrome with debug port 9222..." -ForegroundColor Yellow
$existingChrome = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object {
    try {
        $procId = $_.Id
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $procId").CommandLine
        $cmdLine -like "*9222*" -and $cmdLine -notlike "*--type=renderer*" -and $cmdLine -notlike "*--type=gpu-process*" -and $cmdLine -notlike "*--type=utility*"
    } catch {
        $false
    }
} | Select -First 1

if ($existingChrome) {
    Write-Host "Chrome with debug port 9222 is already running (PID: $($existingChrome.Id))" -ForegroundColor Green
    
    # Verify CDP is accessible
    Write-Host "Verifying CDP endpoint..." -ForegroundColor Yellow
    $cdpVerified = $false
    for ($i = 1; $i -le 5; $i++) {
        $cdpCheck = & curl.exe -s -m 3 "http://127.0.0.1:9222/json/version" 2>&1
        if ($LASTEXITCODE -eq 0 -and $cdpCheck -match '"Browser"') {
            $cdpVerified = $true
            Write-Host "[OK] Chrome CDP is accessible!" -ForegroundColor Green
            try {
                $cdpData = $cdpCheck | ConvertFrom-Json
                Write-Host "  Browser: $($cdpData.Browser)" -ForegroundColor Gray
            } catch {}
            break
        }
        Start-Sleep -Seconds 1
    }
    
    if ($cdpVerified) {
        Write-Host ""
        Write-Host "Chrome is already running and ready!" -ForegroundColor Green
        Write-Host "CDP Endpoint: http://127.0.0.1:9222" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 0
    } else {
        Write-Host "[WARN] Chrome found but CDP not accessible. Restarting..." -ForegroundColor Yellow
        Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
}

# Check if Chrome executable exists
if (-not (Test-Path $chromePath)) {
    Write-Host "ERROR: Chrome not found at $chromePath" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Kill any remaining Chrome processes
Write-Host "Stopping existing Chrome processes..." -ForegroundColor Yellow
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Chrome with debug port
Write-Host "Starting Chrome with debug port 9222..." -ForegroundColor Yellow
$chromeArgs = @(
    "--remote-debugging-port=9222",
    "--user-data-dir=$userProfile",
    "--profile-directory=$defaultProfile",
    "--window-size=800,600",
    "--window-position=100,100",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-sync",
    "--noerrdialogs",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-default-apps",
    "--disable-component-extensions-with-background-pages"
)

try {
    # Start Chrome in Normal window style (VISIBLE on desktop)
    $chromeProcess = Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -WindowStyle Normal -PassThru -ErrorAction Stop
    Write-Host "Chrome started (PID: $($chromeProcess.Id))" -ForegroundColor Green
    Write-Host "Chrome window should be visible on desktop (800x600)" -ForegroundColor Green
    
    # Wait for Chrome to initialize
    Start-Sleep -Seconds 5
    
    # Ensure Chrome window is visible (not minimized) - try multiple times
    Write-Host "Ensuring Chrome window is visible..." -ForegroundColor Yellow
    for ($i = 1; $i -le 10; $i++) {
        Start-Sleep -Seconds 1
        try {
            $chromeWindow = Get-Process -Id $chromeProcess.Id -ErrorAction SilentlyContinue
            if ($chromeWindow -and $chromeWindow.MainWindowHandle -ne [IntPtr]::Zero) {
                $sig = '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);';
                $t = Add-Type -MemberDefinition $sig -Name Win32 -Namespace Native -PassThru;
                $t::ShowWindow($chromeWindow.MainWindowHandle, 1); # SW_SHOWNORMAL - show and activate
                Start-Sleep -Milliseconds 100
                $t::SetForegroundWindow($chromeWindow.MainWindowHandle); # Bring to foreground
                Write-Host "Chrome window is visible on desktop" -ForegroundColor Green
                break
            }
        } catch {
            # Ignore errors, retry
        }
        if ($i -eq 10) {
            Write-Host "WARNING: Could not show Chrome window after 10 attempts" -ForegroundColor Yellow
        }
    }
    
    # Verify CDP is accessible
    Write-Host "Waiting for Chrome CDP..." -ForegroundColor Yellow
    $cdpReady = $false
    for ($i = 1; $i -le 30; $i++) {
        $cdpCheck = & curl.exe -s -m 3 "http://127.0.0.1:9222/json/version" 2>&1
        if ($LASTEXITCODE -eq 0 -and $cdpCheck -match '"Browser"') {
            $cdpReady = $true
            Write-Host "[OK] Chrome CDP is ready!" -ForegroundColor Green
            try {
                $cdpData = $cdpCheck | ConvertFrom-Json
                Write-Host "  Browser: $($cdpData.Browser)" -ForegroundColor Gray
                Write-Host "  Protocol-Version: $($cdpData.'Protocol-Version')" -ForegroundColor Gray
            } catch {}
            break
        }
        if ($i % 5 -eq 0) {
            Write-Host "  Waiting... ($i/30)" -ForegroundColor Gray
        }
        Start-Sleep -Seconds 1
    }
    
    if (-not $cdpReady) {
        Write-Host "[WARN] Chrome CDP not ready after 30 seconds" -ForegroundColor Yellow
        Write-Host "Chrome may still be initializing..." -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Chrome is running in debug mode!" -ForegroundColor Green
    Write-Host "CDP Endpoint: http://127.0.0.1:9222" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "DO NOT CLOSE THIS WINDOW!" -ForegroundColor Red
    Write-Host "Chrome will run in background until you close this window." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to stop Chrome and exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # Stop Chrome when user presses key
    Write-Host ""
    Write-Host "Stopping Chrome..." -ForegroundColor Yellow
    Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Chrome stopped." -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Failed to start Chrome: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

