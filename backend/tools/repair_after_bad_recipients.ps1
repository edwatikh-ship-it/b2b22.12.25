param()

$ErrorActionPreference = "Stop"
$env:PYTHONPATH="."

function Step([string]$msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

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

Step "1) Remove broken alembic revision db107ba8e332 (SyntaxError)"
$bad = ".\alembic\versions\db107ba8e332_create_request_recipients_table.py"
if (Test-Path $bad) {
  Remove-Item $bad -Force
  Step "   Removed $bad"
} else {
  Step "   Not found, skip"
}

Step "2) Fix app\adapters\db\models.py: remove wrong RequestRecipientModel block (Column-style)"
$modelsPath = ".\app\adapters\db\models.py"
if (-not (Test-Path $modelsPath)) { throw "Not found: $modelsPath" }
BackupFile $modelsPath

$models = ReadText $modelsPath

# Remove everything from marker line to EOF (the block is at the end in your file)
$marker = "# ---- UserMessaging: request recipients ----"
if ($models.Contains($marker)) {
  $idx = $models.IndexOf($marker)
  $modelsFixed = $models.Substring(0, $idx).TrimEnd() + "`r`n"
  WriteText $modelsPath $modelsFixed
  Step "   Removed recipients block from models.py"
} else {
  Step "   Marker not found, skip"
}

Step "3) Fix app\adapters\db\repositories.py: remove upsert_recipients method block"
$repoPath = ".\app\adapters\db\repositories.py"
if (-not (Test-Path $repoPath)) { throw "Not found: $repoPath" }
BackupFile $repoPath

$repo = ReadText $repoPath

# We remove from 'async def upsert_recipients' to EOF (in your file it is at the end)
$pat = "async def upsert_recipients"
$pos = $repo.IndexOf($pat)
if ($pos -ge 0) {
  $repoFixed = $repo.Substring(0, $pos).TrimEnd() + "`r`n"
  WriteText $repoPath $repoFixed
  Step "   Removed upsert_recipients from repositories.py"
} else {
  Step "   upsert_recipients not found, skip"
}

Step "4) Smoke checks: alembic + python imports"
& .\.venv\Scripts\python.exe -c "from app.adapters.db.models import AttachmentModel, RequestModel; print('models import ok')" | Out-Null
& .\.venv\Scripts\python.exe -c "from app.adapters.db.repositories import AttachmentRepository, RequestRepository; print('repos import ok')" | Out-Null
& .\.venv\Scripts\alembic.exe current | Out-Null

Write-Host "REPAIR DONE" -ForegroundColor Green