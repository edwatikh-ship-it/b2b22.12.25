param(
  [string]$BackendRoot = "D:\b2bplatform\backend",
  [string]$RouterFile = "D:\b2bplatform\backend\app\transport\routers\user_messaging.py",
  [int]$Port = 8000
)
$ErrorActionPreference = "Stop"

function ReadText([string]$path) { [System.IO.File]::ReadAllText($path, (New-Object System.Text.UTF8Encoding($false))) }
function WriteText([string]$path, [string]$content) { [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false))) }

# 1) Patch router paths
if (!(Test-Path $RouterFile)) { throw "File not found: $RouterFile" }
$src = ReadText $RouterFile
$src = $src -replace '"/user/requests/\{requestId\}/recipients"', '"/userrequests/{requestId}/recipients"'
$src = $src -replace '"/user/requests/\{requestId\}/send-new"', '"/userrequests/{requestId}/send-new"'
$src = $src -replace '"/user/requests/\{requestId\}/send"', '"/userrequests/{requestId}/send"'
$src = $src -replace '"/user/requests/\{requestId\}/messages"', '"/userrequests/{requestId}/messages"'
$src = $src -replace '"/user/messages/\{messageId\}"', '"/usermessages/{messageId}"'
WriteText $RouterFile $src
Write-Host "OK patched: $RouterFile" -ForegroundColor Green

# 2) Free port 8000 (kill whoever listens)
try {
  $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
  foreach ($c in $conn) {
    Write-Host "Killing PID $($c.OwningProcess) on port $Port" -ForegroundColor Yellow
    Stop-Process -Id $c.OwningProcess -Force
  }
} catch {
  Write-Host "No listener on port $Port (ok)" -ForegroundColor DarkGray
}

# 3) Start uvicorn in background
Push-Location $BackendRoot
$env:PYTHONPATH = $BackendRoot

$uvicornCmd = "python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload --log-level warning"
Write-Host "Starting: $uvicornCmd" -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-Command",$uvicornCmd) | Out-Null

# 4) Wait for OpenAPI
$ok = $false
for ($i=0; $i -lt 25; $i++) {
  try {
    $null = Invoke-RestMethod "http://localhost:$Port/openapi.json" -TimeoutSec 2
    $ok = $true
    break
  } catch {
    Start-Sleep -Milliseconds 400
  }
}
if (!$ok) { throw "Server did not come up on http://localhost:$Port" }
Write-Host "OK server is up." -ForegroundColor Green

# 5) Ensure route is in OpenAPI
$openapi = Invoke-RestMethod "http://localhost:$Port/openapi.json"
$txt = $openapi | ConvertTo-Json -Depth 60
if ($txt -notmatch "userrequests/\{requestId\}/recipients") {
  throw "Route not in OpenAPI: /apiv1/userrequests/{requestId}/recipients"
}
Write-Host "OK route present in OpenAPI." -ForegroundColor Green

# 6) Call PUT (expect 501 Not Implemented for now)
try {
  Invoke-RestMethod -Method Put "http://localhost:$Port/apiv1/userrequests/1/recipients" -ContentType "application/json" -Body "{}"
  throw "Unexpected success response (should be 501 for stub)."
} catch {
  $msg = $_.Exception.Message
  Write-Host "PUT result: $msg" -ForegroundColor Cyan
}

Pop-Location
Write-Host "DONE" -ForegroundColor Green
