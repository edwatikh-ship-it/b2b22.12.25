param(
  [Parameter(Mandatory=$true)]
  [string]$ContractPath
)

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

$path = $ContractPath
if (-not (Test-Path $path)) { throw "Not found: $path" }
BackupFile $path
$t = ReadText $path

# ---- PATHS INSERT ----
if ($t -notmatch "(?m)^\s*/user/blacklist/inn:\s*$") {
  $needle = "/user/messages/{messageId}:"
  $ins = @"
  /user/blacklist/inn:
    post:
      tags: [Blacklist]
      summary: Add company INN to user's personal blacklist (user-level)
      description: >
        Personal blacklist. Prevent sending to this company for this user.
        UI may display supplier_name and checko_data when available.
        When added, system must auto-unselect related recipients (selected=false) for this user's requests.
      requestBody:
        required: true
        content:
          application/json:
            schema: { `$ref: "#/components/schemas/AddUserBlacklistInnRequest" }
      responses:
        "200":
          description: Added
          content:
            application/json:
              schema: { `$ref: "#/components/schemas/GenericOkResponse" }
    get:
      tags: [Blacklist]
      summary: List user's personal blacklist (by INN)
      parameters:
        - in: query
          name: limit
          schema: { type: integer, default: 200, minimum: 1, maximum: 500 }
      responses:
        "200":
          description: Blacklist
          content:
            application/json:
              schema: { `$ref: "#/components/schemas/UserBlacklistInnListResponse" }

  /user/blacklist/inn/{inn}:
    delete:
      tags: [Blacklist]
      summary: Remove INN from user's personal blacklist
      parameters:
        - in: path
          name: inn
          required: true
          schema: { type: string, minLength: 10, maxLength: 12 }
      responses:
        "200":
          description: Removed
          content:
            application/json:
              schema: { `$ref: "#/components/schemas/GenericOkResponse" }

"@
  if ($t.Contains($needle)) {
    $idx = $t.IndexOf($needle) + $needle.Length
    $t = $t.Insert($idx, "`r`n`r`n" + $ins)
  } else {
    $t = $t + "`r`n`r`n" + $ins
  }
}

# ---- SCHEMAS INSERT (correct indentation under components/schemas) ----
if ($t -notmatch "(?m)^\s{2}AddUserBlacklistInnRequest:\s*$") {
  # Find "schemas:" line under components:
  $m = [regex]::Match($t, "(?m)^\s{2}schemas:\s*$")
  if (-not $m.Success) { throw "Cannot find '  schemas:' in api-contracts.yaml" }

  $insertAt = $m.Index + $m.Length

  $schemas = @"

  AddUserBlacklistInnRequest:
    type: object
    properties:
      inn:
        type: string
        minLength: 10
        maxLength: 12
      reason:
        type: string
        nullable: true
    required: [inn]

  UserBlacklistInnListResponse:
    type: object
    properties:
      items:
        type: array
        items:
          type: object
          properties:
            id: { type: integer }
            inn: { type: string }
            supplier_id: { type: integer, nullable: true }
            supplier_name: { type: string, nullable: true }
            checko_data:
              type: object
              nullable: true
              additionalProperties: true
            reason: { type: string, nullable: true }
            created_at: { type: string, format: date-time }
          required: [id, inn, created_at]
    required: [items]
"@

  $t = $t.Insert($insertAt, $schemas)
}

WriteText $path $t
Write-Host "PATCH DONE (v3)" -ForegroundColor Green