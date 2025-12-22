# (вставь сюда весь контент apply_recipients_safe_v2.ps1 который я дал)param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ROOT
$env:PYTHONPATH = "."

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
function InsertBeforeMarker([string]$path, [string]$marker, [string]$insert) {
  if (-not (Test-Path $path)) { throw "Not found: $path" }
  $text = ReadText $path
  $count = ([regex]::Matches($text, [regex]::Escape($marker))).Count
  if ($count -ne 1) { throw "Marker '$marker' must appear exactly once in $path; found=$count" }

  if ($text.Contains($insert)) { Step "Already applied in $path, skip"; return }

  BackupFile $path
  $idx = $text.IndexOf($marker)
  $before = $text.Substring(0, $idx)
  $after  = $text.Substring($idx)
  $fixed = ($before.TrimEnd() + "`r`n`r`n" + $insert.Trim() + "`r`n`r`n" + $after)
  WriteText $path $fixed
  Step "Patched $path"
}

Step "1) Detect current head"
$head = (& .\.venv\Scripts\alembic.exe heads).Split("`n")[0].Split(" ")[0].Trim()

Step "2) Create alembic revision for request_recipients"
$revOut = & .\.venv\Scripts\alembic.exe revision -m "create request_recipients table"
$revLine = ($revOut | Select-String -Pattern "Generating " | Select-Object -First 1)
if (-not $revLine) { throw "Cannot detect alembic generated file path." }
$revPath = ($revLine.ToString() -replace "^Generating\s+", "") -replace "\s+\.\.\.\s+done$", ""
$revPath = $revPath.Trim()
if (-not (Test-Path $revPath)) { throw "Revision file not found: $revPath" }
$revFile = Split-Path $revPath -Leaf
$revId = $revFile.Split("_")[0]

Step "3) Write migration content: $revFile"
$revContent = @"
"""create request_recipients table

Revision ID: $revId
Revises: $head
Create Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

"""

from alembic import op
import sqlalchemy as sa

revision = "$revId"
down_revision = "$head"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "request_recipients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("request_id", "supplier_id", name="uq_request_recipients_request_supplier"),
    )
    op.create_index("ix_request_recipients_request_id", "request_recipients", ["request_id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_request_recipients_request_id", table_name="request_recipients")
    op.drop_table("request_recipients")
"@
WriteText $revPath $revContent

Step "4) Apply migration"
& .\.venv\Scripts\alembic.exe upgrade head | Out-Null

# Маркеры должны быть добавлены заранее 1 раз руками:
$modelsPath = Join-Path $ROOT "app\adapters\db\models.py"
$repoPath   = Join-Path $ROOT "app\adapters\db\repositories.py"

Step "5) Patch models.py"
$modelsInsert = @"
# ---- UserMessaging: request recipients (AUTO) ----
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

class RequestRecipientModel(Base):
    __tablename__ = "request_recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
"@
InsertBeforeMarker -path $modelsPath -marker "# __AUTO_INSERT_MODELS_END__" -insert $modelsInsert

Step "6) Patch repositories.py"
$repoInsert = @"
# ---- UserMessaging: request recipients (AUTO) ----
from app.adapters.db.models import RequestRecipientModel
"@
InsertBeforeMarker -path $repoPath -marker "# __AUTO_INSERT_REPOSITORIES_END__" -insert $repoInsert

Step "7) Smoke checks"
& .\.venv\Scripts\python.exe -m compileall -q . | Out-Null
& .\.venv\Scripts\python.exe -m pytest -q
Write-Host "DONE" -ForegroundColor Green
