param(
  [string]$TestsDir = "D:\b2bplatform\backend\tests\integration"
)
$ErrorActionPreference = "Stop"

function ReadText([string]$path) { [System.IO.File]::ReadAllText($path, (New-Object System.Text.UTF8Encoding($false))) }
function WriteText([string]$path, [string]$content) { [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false))) }

$targets = @(
  "test_get_user_request_detail.py",
  "test_update_request_keys.py",
  "test_submit_request.py"
)

foreach ($name in $targets) {
  $p = Join-Path $TestsDir $name
  if (!(Test-Path $p)) { throw "Not found: $p" }

  $c = ReadText $p
  $orig = $c

  $c = $c -replace "/apiv1/userrequests/", "/apiv1/user/requests/"

  if ($c -ne $orig) {
    Copy-Item $p "$p.bak.$(Get-Date -Format yyyyMMdd-HHmmss)" -Force
    WriteText $p $c
    Write-Host "Reverted: $p" -ForegroundColor Green
  } else {
    Write-Host "No changes: $p" -ForegroundColor DarkGray
  }
}

Write-Host "DONE" -ForegroundColor Green
