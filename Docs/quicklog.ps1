param(
  [Parameter(Mandatory=$true)][ValidateSet("Success","Incident")] [string] $Mode,
  [Parameter(Mandatory=$true)] [string] $Context,
  [Parameter(Mandatory=$true)] [string] $Message,
  [Parameter(Mandatory=$true)] [string] $Verify,
  [string[]] $FilesTouched = @(),
  [switch] $RunPreCommit,
  [switch] $AutoCommitPush,
  [string] $CommitMessage = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = "D:\b2bplatform"
Set-Location $repoRoot

$dt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$enc = New-Object System.Text.UTF8Encoding($false)

$filesLine = ""
if ($FilesTouched.Count -gt 0) {
  $filesLine = "Files touched: " + ($FilesTouched -join ", ")
}

$head = (git rev-parse --short HEAD)
$gitLine = (git status -sb | Select-Object -First 1)

Write-Output "=== quicklog snapshot ==="
Write-Output ("time=" + $dt + " MSK")
Write-Output ("head=" + $head)
Write-Output ("git=" + $gitLine)

if ($RunPreCommit) {
  Write-Output "=== pre-commit ==="
  pre-commit run --all-files
}

if ($Mode -eq "Success") {
  $entry = @"

- $dt MSK Success
  Context: $Context
  Change: $Message
  Verification: $Verify
  Expected: PASS
  $filesLine
"@
  [System.IO.File]::AppendAllText((Join-Path $repoRoot "HANDOFF.md"), $entry, $enc)
  Write-Output "Appended: HANDOFF.md"
}

if ($Mode -eq "Incident") {
  $entry = @"

- $dt MSK
  Context: $Context
  Symptom: $Message
  Root cause: TBD
  Fix/Mitigation: TBD
  Verification commands + expected output: $Verify
  $filesLine
"@
  [System.IO.File]::AppendAllText((Join-Path $repoRoot "INCIDENTS.md"), $entry, $enc)
  Write-Output "Appended: INCIDENTS.md"
}

if ($AutoCommitPush) {
  if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    throw "CommitMessage is required when -AutoCommitPush is used."
  }
  git add "HANDOFF.md" "INCIDENTS.md" 2>$null | Out-Null
  git add "quicklog.ps1" 2>$null | Out-Null
  git commit -m $CommitMessage
  git push origin main
  Write-Output ("committed=" + (git rev-parse --short HEAD))
  git status -sb
}