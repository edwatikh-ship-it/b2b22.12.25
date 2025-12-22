# B2B Platform PROJECT RULES (SSoT)

Version: 2.3
Date: 2025-12-18

This document is SSoT for the development process (not for API).
Priority order (SSoT): api-contracts.yaml -> PROJECT-RULES.md -> PROJECT-DOC.md.

============================================================
HARD RULE 0: NO GUESSING / FACTS FIRST (ABSOLUTE)
============================================================
- Any debugging, commands, patches, refactors, API changes, or docs edits MUST start with facts.
- Forbidden: guessing file names, paths, base URLs, prefixes, ports, env vars, endpoints, or response shapes.
- Forbidden language: "probably", "likely", "should be", "it must be" unless proven by commands/output.
- If something is unknown: run commands to discover it OR ask the user and STOP.

============================================================
HARD RULE 1: OUTPUT CONTRACT (FULL FILE OR POWERSHELL COMMANDS)
============================================================
- In this project chat, the assistant must respond in one of two formats only:
  1) Copy/paste PowerShell commands, OR
  2) Full plain-text content of a file (complete file) ready to be pasted to replace the existing file.
- Partial snippets are allowed only if the user explicitly requests "snippet only".

============================================================
HARD RULE 2: COMMANDS-ONLY ACTIONS (COPY/PASTE POWERSHELL)
============================================================
- Every actionable instruction MUST be provided as PowerShell commands the user can copy-paste.
- Do not write "edit file X" without providing the exact safe command(s) to do it (or provide a full file replacement).
- If a next step depends on previous output: request the output first, then provide the next commands.
- Placeholders are forbidden (no <FILE>, <PORT>, http://host:port). If unknown: discover via commands first.

============================================================
HARD RULE 3: REAL-TIME DOCUMENTATION (CONTEXT MUST SURVIVE CHATS)
============================================================
Goal:
- Prevent repeated discussions and knowledge loss across sessions.
- Keep the project deployable/onboardable at any time using repo docs only.

Rules (applies to everyone: humans + agents):
- Any discussed change that affects behavior MUST be documented immediately:
  business rules, functional requirements, non-functional requirements, architecture decisions, bug fixes, and even small clarifications.
- Do not postpone documentation until later. If it is discussed and accepted, it goes into docs now.

Project registry discipline:
- Keep PROJECT-TREE.txt current and factual:
  - where each file is located
  - what it is responsible for
  - how it interacts with other components (at high level)
- Every new file MUST be documented at creation time.
- If a file is deleted or becomes obsolete/broken, document the fact and the reason.

Cross-session continuity:
- The next chat must be able to continue from a pasted prompt + repo docs, without re-explaining prior decisions.
- Use HANDOFF.md (success, verified) and INCIDENTS.md (failures) as the factual memory layer.
- Use AGENT-KNOWLEDGE.md only for reusable, confirmed patterns (no guesses, no maybe).

Documentation language and style:
- Repository documentation is English-only.
- Write facts and decisions, avoid water (no fluff).
- If something is unknown, mark it explicitly as TBD and ask for missing inputs (no guessing).
============================================================
============================================================
HARD RULE 3: REAL-TIME DOCUMENTATION (CONTEXT MUST SURVIVE CHATS)
============================================================
Goal:
- Prevent repeated discussions and knowledge loss across sessions.
- Keep the project deployable/onboardable at any time using repo docs only.

Rules (applies to everyone: humans + agents):
- Any discussed and accepted change that affects behavior MUST be documented immediately:
  business rules, functional requirements, non-functional requirements, architecture decisions, bug fixes, and small clarifications.
- Do not postpone documentation "until later". If it is discussed and accepted, it goes into docs now.

Doc-gate DoD (Definition of Done):
- Work is NOT considered done until documentation and verification are updated (applies to everyone).
- Required (when applicable):
  - API changes: update api-contracts.yaml first (SSoT), then align code/tests.
  - Product rules / behavior / architecture decisions: update PROJECT-DOC.md and/or DECISIONS.md (fact-only).
  - File structure changes: update PROJECT-TREE.txt (what each file does and where it lives).
  - Success: append HANDOFF.md with a verification command + expected output.
  - Failure: append INCIDENTS.md with symptom, root cause (if known), mitigation, verification.
  - Quality gate: run pre-commit run --all-files before logging success in HANDOFF.md.

1) SSoT (Single Source of Truth)
============================================================
- API (endpoints, DTOs, responses) = ONLY api-contracts.yaml at repo root:
  D:\b2bplatform\api-contracts.yaml
- If implementation and contract diverge: it is an error.
  Fix by aligning code to the contract OR change the contract intentionally (with explicit commit).
- SSoT files must live in repo root D:\b2bplatform\ only.
  Forbidden: duplicates inside backend\.

============================================================
2) Architecture (fixed)
============================================================
Layer order is fixed and MUST NOT be violated:
transport -> usecases -> domain -> adapters

Meaning:
- transport: HTTP routes + IO validation only. NO business decisions.
- usecases: business scenarios and orchestration.
- domain: pure models/rules (no FastAPI/SQLAlchemy).
- adapters: DB/SMTP/HTTP clients and integrations.

============================================================
3) SAFETY GUARDS (MANDATORY BEFORE ANY REPO CHANGE)
============================================================
Before changing any tracked file:
1) Verify repo root and SSoT presence:
   - Set-Location D:\b2bplatform
   - Test-Path .\api-contracts.yaml
   - Test-Path .\PROJECT-RULES.md
2) Show git status BEFORE and AFTER:
   - git status -sb
3) Backup every changed file BEFORE editing:
   - Backups MUST go to: D:\b2bplatform\.tmp\backups\
   - Backup name: <file>.bak.<timestamp>
4) Rollback MUST be provided:
   - Restore from .bak OR `git restore <path>`
5) Encoding rule (mandatory):
   - Text files must be UTF-8 without BOM.
   - Forbidden for important files: Set-Content / Out-File rewrites (encoding risk).
   - Preferred: deterministic patch OR .NET WriteAllText with UTF8Encoding(false).
  - Logging tools policy (PowerShell):
    - When appending to HANDOFF.md / INCIDENTS.md, use: & .\tools\append_handoff_incidents.ps1 ...
    - Do NOT use: powershell.exe -File .\tools\append_handoff_incidents.ps1 ... (argument binding issues for string[]).
    - Any literal text containing $ (examples: $env:NAME, $true, $false) MUST be passed in single quotes to avoid interpolation.

Artifacts policy (mandatory):
- Temporary files and backups MUST NOT clutter repo root.
- Allowed locations only:
  - D:\b2bplatform\.tmp\backups\
  - D:\b2bplatform\.tmp\tmp\
- Forbidden: creating/keeping any other repo-root tmp folders.

============================================================
4) PRE-FLIGHT (MANDATORY BEFORE ROUTE/WIRING/ENDPOINT CLAIMS)
============================================================
Do NOT assume defaults. BASE_URL and API_PREFIX MUST be discovered.

FACTS to collect (in THIS shell):
1) Runtime base URL (BASE_URL):
   - Plan A: read from launch config / env.
   - Plan B: ask the user for the exact running host:port.

2) Confirm backend is running:
   - If backend is NOT running: do NOT run HTTP checks yet.
   - Provide only start commands (just dev / just dev-noreload or Plan B), then re-run this PRE-FLIGHT.
   - Ensure checks target the actually running instance (host:port from the start command output).

3) Runtime OpenAPI must be reachable:
   - Invoke-RestMethod "$BASE_URL/openapi.json" | Out-Null
   - Expect: HTTP 200 and valid JSON.

4) API_PREFIX detection rule:
   - Detect prefix from runtime OpenAPI paths. Do NOT assume apiv1.
   - If OpenAPI includes "/health": API_PREFIX is empty.
5) Health check:
   - Invoke-RestMethod "$BASE_URL/$API_PREFIX/health" (or "$BASE_URL/health" if API_PREFIX is empty)
   - Expect: JSON with status="ok" (or contract equivalent).

6) DB env in CURRENT shell (only if routers/imports require DB):
   - python -c "import os; print(os.getenv('DATABASEURL'), os.getenv('DATABASE_URL'))"
   - If import-time DB is used and env is missing: STOP and fix env before debugging.

If any PRE-FLIGHT check fails:
- Provide only Plan B commands to fix environment/services first.
- Do NOT propose code changes.

============================================================
5) Standard tooling: "6 tools" (check availability first)
============================================================
Tools: ruff, pre-commit, pyclean, uv, direnv, just

Rule:
- Always check first (no assumptions):
  - Get-Command ruff, pre-commit, pyclean, uv, direnv, just -ErrorAction SilentlyContinue
- If missing:
  - Provide Plan B commands (no installation promises).

Usage:
- Lint/format:
  - ruff check backend
  - ruff format backend
  - CI: ruff check + ruff format --check
- Hooks:
  - pre-commit run --all-files
- Routine:
  - just fmt / just test / just dev / just clean (if present)
- Cleanup:
  - pyclean . (if present)
  - Plan B: remove __pycache__ via PowerShell
- Dependencies:
  - Prefer uv
  - Plan B: python -m venv + pip install
- Env:
  - Prefer direnv
  - Plan B: set env vars explicitly in the SAME shell as the running command

============================================================
6) Windows / PowerShell pitfalls (MANDATORY)
============================================================
- Forbidden: bash heredoc in PowerShell (python - << PY).
- PowerShell: $ref inside strings must be escaped.
- Prefer Windows-safe commands. Avoid fragile quoting.
- Regex: avoid [regex]::Replace overload pitfalls; prefer Regex object then .Replace.
- ConvertTo-Json has a hard max depth (100). Do not use it to dump OpenAPI.
- Always write text as UTF-8 without BOM.

============================================================
7) Documentation language (strict)
============================================================
- Repository documentation language is English only.
- Russian is allowed only for live chat communication.
- Append-only logs: one entry = one language, no forced translation.

============================================================
8) Specification (Use Cases / BR / FR / NFR) (MANDATORY)
============================================================
Goal:
- By the end of the project we must have a complete specification that can be used to:
  implement features, test behavior, onboard new people, and continue work in new chats without context loss.

Specification scope (minimum):
1) Use Cases
- For each use case:
  - ID, name
  - Primary actor(s)
  - Preconditions
  - Trigger
  - Main success scenario (step-by-step)
  - Alternate/error flows
  - Postconditions
  - Related API endpoints (paths from api-contracts.yaml)
  - Acceptance criteria (testable)

2) Business Requirements (BR)
- Business goal/problem, scope, and success criteria (if known).

3) Functional Requirements (FR)
- Concrete system behavior, validations, error cases, inputs/outputs.

4) Non-Functional Requirements (NFR)
- Performance, reliability, security/privacy, observability, maintainability.

Lifecycle rule:
- The specification is a living artifact: we add, update, and remove obsolete items as reality changes.
- Contradictory requirements must not remain in the docs. They must be resolved or marked as "TBD (business confirmation)".

Storage decision (chosen by assistant, documented here):
- Specification is stored as a single root file for maximum speed and low navigation overhead:
  D:\b2bplatform\SPEC.md

============================================================
9) Decisions are mandatory (document every important decision)
============================================================
- Any important decision must be documented.
- A decision is "important" if it affects:
  - API shape, endpoint semantics, error codes
  - persistence schema
  - business rules (blacklist, parsing, matching, auth)
  - architecture or service boundaries (backend vs parser_service)
  - security/authorization behavior
- Decisions must be written in PROJECT-DOC.md (product/business) OR PROJECT-RULES.md (process) depending on the nature of the decision.
- If in doubt: document in PROJECT-DOC.md.

Decision entry format (fact-only):
- Date/time (MSK)
- Decision
- Why (short)
- Consequences (what changes)
- How to verify (commands/tests)

============================================================
10) Progress logging (MANDATORY)
============================================================
Success:
- Append-only: HANDOFF.md
- Update: PROJECT-TREE.txt
- Commit + push origin/main

Failure:
- Append-only: INCIDENTS.md
- Commit + push origin/main

HANDOFF/INCIDENTS entry format:
- Datetime (MSK)
- What happened / what was done
- Root cause
- Fix/Mitigation
- Verification command + expected output
- Files touched (paths)

Chat safety / question gate:
- If a critical fact is missing (BASE_URL, API_PREFIX, env vars, target file content):
  ask up to 3 bold questions OR provide commands to discover the facts, then STOP.

============================================================
11) Chat handoff protocol (PDF) (MANDATORY)
============================================================
Purpose:
- Reduce repeated mistakes when starting a new chat.
- Convert previous chat into verifiable knowledge: incidents + successful decisions + runnable runbooks.

A) End-of-chat rule (current chat)
- At the end of each chat, the user provides a PDF that contains the full conversation log.
- This PDF is the handoff artifact for the next chat.

B) Start-of-chat rule (new chat)
- Every new chat MUST start with two things:
  1) Request the previous chat PDF handoff.
  2) Run CTX-FIRST commands (repo facts) before proposing changes.
- The agent must NOT proceed to design/patching without the PDF (unless the user explicitly says the PDF is unavailable).

C) Analysis + documentation duties (in the new chat)
The agent MUST analyze the PDF and document:
1) All incidents/errors/pitfalls discovered in the chat (append-only to INCIDENTS.md)
2) All successful outcomes and verified changes (append-only to HANDOFF.md)
3) Any new reusable playbooks (update AGENT-KNOWLEDGE.md)
4) Any new decisions (update PROJECT-DOC.md or PROJECT-RULES.md depending on decision type)

D) How to prepare a handoff bundle (commands)
Note: PDF export method depends on the chat platform/browser and is not guaranteed by this repo.
We store the PDF plus a small metadata file next to it.

PowerShell (bundle folder):
- Set-Location D:\b2bplatform
- $ts = Get-Date -Format "yyyyMMdd-HHmmss"
- $bundle = Join-Path ".\.tmp\handoff" $ts
- New-Item -ItemType Directory -Force $bundle | Out-Null
- Write-Host "Put your chat PDF into: $bundle"
- Write-Host "Name it: chat.pdf"

Metadata (minimal, to avoid losing context):
- $meta = @{
    timestamp_msk = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    timezone = "MSK"
    note = "Chat handoff PDF for next chat. Place chat.pdf here."
  } | ConvertTo-Json -Depth 5
- [System.IO.File]::WriteAllText((Join-Path $bundle "meta.json"), $meta, (New-Object System.Text.UTF8Encoding($false)))

After placing the PDF:
- Get-ChildItem $bundle
- Get-FileHash (Join-Path $bundle "chat.pdf") -Algorithm SHA256

============================================================
12) PowerShell path safety (MANDATORY)
============================================================
- Always anchor scripts to repo root:
  - Set-Location D:\b2bplatform OR use $PSScriptRoot + Join-Path
- Do not use Resolve-Path for non-existing targets.
- Any script that changes directory MUST restore it (Push-Location/Pop-Location).

============================================================
13) Mandatory preflight script (START HERE)
============================================================
- Before any work (dev/debug) and before any commit: run:
  - Set-Location D:\b2bplatform
  - .\tools\preflight.ps1 -BackendBaseUrl "<actual base url>"
- If preflight fails: fix environment/services first. Do NOT commit/push.

============================================================
14) One-click dev run (justfile)
============================================================
- Canonical local run uses repo-root justfile.
- If just is missing: use Plan B manual uvicorn commands from justfile docs.

============================================================
15) Assistant message format (chat)
============================================================
Any multi-step instruction MUST include:
- WHY
- EXPECT
- IF FAIL

Additionally, every message must include two short explanations:
- Customer mode (plain Russian, no IT terms, focus on value/outcome).
- Junior analyst mode (simplified explanation + small metaphor).

============================================================
16) CTX-FIRST + NO-PLACEHOLDERS (STRICT)
============================================================
- CTX-FIRST: run .\ctx.ps1 from repo root and paste output before fixes.
- NO-PLACEHOLDERS: commands must not contain placeholders. If unknown: discover first.

============================================================
17) Anti-Guessing Protocol (FACT-LOCK) (HARD)
============================================================
The assistant MUST NOT propose any patch/refactor/API change unless ALL items are present:

1) Repo root & SSoT presence:
   - Set-Location D:\b2bplatform
   - Test-Path .\api-contracts.yaml
   - Test-Path .\PROJECT-RULES.md

2) Git state:
   - git status -sb

3) Runtime base:
   - Invoke-RestMethod "$BASE_URL/openapi.json" | Out-Null (expect 200)
   - API_PREFIX is derived from OpenAPI paths (no assumptions)

4) DB env in CURRENT shell:
   - python -c "import os; print(os.getenv('DATABASEURL'), os.getenv('DATABASE_URL'))"

5) Target code snapshot for EVERY file to be patched:
   - Get-Content <path> -Raw
   - OR Select-String <path> -Pattern "<anchor>" -Context <n>,<n>

If any item is missing:
- Provide only commands to collect facts.
- Then STOP.

STOP-ON-MISMATCH (PATCH SAFETY):
- Any patch MUST validate that expected anchor blocks exist.
- If anchor block is not found: STOP and request a fresh snapshot.
- Fallback/guess patches are forbidden.

ATOMIC CROSS-LAYER CHANGES:
- If a change modifies a data shape between layers: patch ALL impacted ends in the same instruction block.

VERIFY OR ROLLBACK (MANDATORY):
- Each patch instruction MUST include backups + git status + rollback + verification commands.

============================================================
18) Draft files policy (NO REPO TRASH)
============================================================
- New files created during experiments are TEMP by default.
- Preferred WIP location: D:\b2bplatform__WIP\
- If a draft must be in repo temporarily:
  - it MUST be in a clearly named folder and ignored by git.
- Before commit/push:
  - git status --porcelain must be clean (no accidental ?? files).

============================================================
19) Freedom + confirmation (structure evolution)
============================================================
- The assistant may propose new docs/folder structure to improve maintainability.
- Any deletion or merging of existing docs/log files requires explicit user confirmation.

============================================================
20) Documentation style guide (single style, fact-only)
============================================================
All operational documentation must follow one standard style:

A) RUNBOOK entries (how to run / debug)
- Goal
- Preconditions
- Commands (PowerShell)
- Expected output
- If fail (Plan B)
- Artifacts touched (files/paths)

B) LOG entries (HANDOFF / INCIDENTS)
- Timestamp (MSK)
- Context (feature/endpoint/service)
- Symptom or Change
- Root cause (if known)
- Fix/Mitigation
- Verification commands + expected output
- Files touched

- Rule: Любой клиент parserservice, который шлёт кириллицу в query, обязан использовать UTF-8 и заголовок Content-Type: application/json; charset=utf-8. При появлении '?????' или 'Р В Р...' сначала проверить charset клиента, а не править parserservice или api-contracts.yaml.
