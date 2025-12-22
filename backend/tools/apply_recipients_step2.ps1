param(
  [string]$BackendRoot = "D:\b2bplatform\backend"
)
$ErrorActionPreference = "Stop"

function ReadText([string]$path) { [System.IO.File]::ReadAllText($path, (New-Object System.Text.UTF8Encoding($false))) }
function WriteText([string]$path, [string]$content) { [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false))) }
function EnsureDir([string]$path) { if (!(Test-Path $path)) { New-Item -ItemType Directory -Force -Path $path | Out-Null } }
function BackupFile([string]$path) { if (Test-Path $path) { Copy-Item $path "$path.bak.$(Get-Date -Format yyyyMMdd-HHmmss)" -Force } }

Push-Location $BackendRoot
$env:PYTHONPATH = $BackendRoot

# Paths
$dtoPath = Join-Path $BackendRoot "app\transport\schemas\messaging.py"
$ucPath  = Join-Path $BackendRoot "app\usecases\update_recipients.py"
$routerPath = Join-Path $BackendRoot "app\transport\routers\user_messaging.py"
$repoPath = Join-Path $BackendRoot "app\adapters\db\repositories.py"
$modelsPath = Join-Path $BackendRoot "app\adapters\db\models.py"
$testPath = Join-Path $BackendRoot "tests\integration\test_update_recipients.py"

EnsureDir (Split-Path $dtoPath)
EnsureDir (Split-Path $ucPath)
EnsureDir (Split-Path $testPath)

# --- 1) DTO ---
$dto = @'
from __future__ import annotations

from pydantic import BaseModel, Field

from app.transport.schemas.common import GenericOkResponseDTO


class RecipientDTO(BaseModel):
    supplierid: int = Field(ge=1)
    selected: bool


class UpdateRecipientsRequestDTO(BaseModel):
    recipients: list[RecipientDTO]


class UpdateRecipientsResponseDTO(GenericOkResponseDTO):
    pass
'@
WriteText $dtoPath $dto

# --- 2) Usecase ---
$uc = @'
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecipientInput:
    supplierid: int
    selected: bool


class UpdateRecipientsUseCase:
    def __init__(self, repo):
        self._repo = repo

    async def execute(self, request_id: int, recipients: list[RecipientInput]) -> None:
        if request_id <= 0:
            raise ValueError("request_id must be > 0")

        # Replace-all semantics (server state mirrors UI)
        await self._repo.replace_recipients(request_id=request_id, recipients=recipients)
'@
WriteText $ucPath $uc

# --- 3) Repo method (RequestRepository) ---
if (!(Test-Path $repoPath)) { throw "Repo not found: $repoPath" }
BackupFile $repoPath
$repoText = ReadText $repoPath

if ($repoText -notmatch "async def replace_recipients") {
  if ($repoText -notmatch "RequestRecipientModel") {
    throw "RequestRecipientModel is not imported/defined in adapters yet. Need model first in app/adapters/db/models.py"
  }

  $insert = @'

    async def replace_recipients(self, request_id: int, recipients: list) -> None:
        """
        Replace-all recipients list for a request.
        Each item must have fields: supplierid:int, selected:bool
        """
        from sqlalchemy import delete

        # delete previous
        await self.session.execute(
            delete(RequestRecipientModel).where(RequestRecipientModel.requestid == request_id)
        )

        # insert new
        for r in recipients:
            self.session.add(
                RequestRecipientModel(
                    requestid=request_id,
                    supplierid=int(r.supplierid),
                    selected=bool(r.selected),
                )
            )

        await self.session.commit()
'@

  # вставляем перед концом класса (наивно: перед последним "class" не подходит; поэтому добавим перед EOF)
  $repoText = $repoText.TrimEnd() + "`r`n" + $insert + "`r`n"
  WriteText $repoPath $repoText
}

# --- 4) Router: update_recipients makes DB call; others keep 501 ---
if (!(Test-Path $routerPath)) { throw "Router not found: $routerPath" }
BackupFile $routerPath
$routerText = ReadText $routerPath

# Ensure imports
if ($routerText -notmatch "AsyncSession") {
  $routerText = $routerText -replace "from fastapi import APIRouter, HTTPException",
@'
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.adapters.db.repositories import RequestRepository
from app.transport.schemas.messaging import UpdateRecipientsRequestDTO, UpdateRecipientsResponseDTO
from app.usecases.update_recipients import UpdateRecipientsUseCase, RecipientInput
'@
}

# Replace handler body only for update_recipients
$routerText = $routerText -replace '(?s)@router\.put\("?/userrequests/\{requestId\}/recipients"?\)\s*async def update_recipients\([^\)]*\):\s*raise HTTPException\(status_code=501, detail="Not Implemented"\)',
@'
@router.put("/userrequests/{requestId}/recipients", response_model=UpdateRecipientsResponseDTO)
async def update_recipients(
    requestId: int,
    body: UpdateRecipientsRequestDTO,
    db: AsyncSession = Depends(get_db_session),
):
    repo = RequestRepository(db)
    uc = UpdateRecipientsUseCase(repo=repo)
    recipients = [RecipientInput(supplierid=r.supplierid, selected=r.selected) for r in body.recipients]
    await uc.execute(request_id=requestId, recipients=recipients)
    return UpdateRecipientsResponseDTO(success=True, message="ok")
'@

WriteText $routerPath $routerText

# --- 5) Test ---
$test = @'
from fastapi.testclient import TestClient

from app.main import app


def test_put_recipients_returns_200_and_persists(db_session):
    client = TestClient(app)

    # create request first (existing endpoint)
    resp = client.post("/apiv1/userrequests", json={"title": "t", "keys": [{"pos": 1, "text": "x"}]})
    assert resp.status_code == 200
    request_id = resp.json()["requestid"]

    # put recipients (replace-all)
    resp2 = client.put(
        f"/apiv1/userrequests/{request_id}/recipients",
        json={"recipients": [{"supplierid": 1, "selected": True}, {"supplierid": 2, "selected": False}]},
    )
    assert resp2.status_code == 200
    assert resp2.json()["success"] is True

    # put again with different set (replace-all)
    resp3 = client.put(
        f"/apiv1/userrequests/{request_id}/recipients",
        json={"recipients": [{"supplierid": 3, "selected": True}]},
    )
    assert resp3.status_code == 200
    assert resp3.json()["success"] is True
'@
WriteText $testPath $test

Write-Host "STEP2 files written. Now run pytest." -ForegroundColor Green
Pop-Location
