param()

$ErrorActionPreference = "Stop"

function ReadText([string]$path) {
  return [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
}

function WriteText([string]$path, [string]$content) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
}

function BackupFile([string]$path) {
  if (Test-Path $path) {
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $path "$path.bak-$ts" -Force
  }
}

$repoPath = ".\app\adapters\db\repositories.py"
if (-not (Test-Path $repoPath)) { throw "Not found: $repoPath" }

BackupFile $repoPath
$t = ReadText $repoPath

# remove RequestRecipientModel token from import line(s)
$t = $t -replace ",\s*RequestRecipientModel", ""
$t = $t -replace "RequestRecipientModel,\s*", ""

WriteText $repoPath $t

# smoke import
$env:PYTHONPATH="."
& .\.venv\Scripts\python.exe -c "from app.adapters.db.repositories import RequestRepository, AttachmentRepository; print('repos import ok')" | Out-Null

Write-Host "IMPORT FIX DONE" -ForegroundColor Green