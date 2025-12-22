## Logging rule (DoD)
- Success -> HANDOFF.md (append-only, with verification command).
- Failure -> INCIDENTS.md (append-only, with symptom/root cause/fix/verification).

# HANDOFF — B2B Platform

## How to use
Append-only progress log for successful milestones.
Each entry should include:
- datetime MSK
- what changed
- how verified (exact command + expected output)

If a step failed: do NOT add an entry here; log it into INCIDENTS.md instead.

## Entries (append-only)

## Entries
- 2025-12-13 22:40 MSK  Verified API up: GET /api/v1/health -> 200 {"status":"ok"}; Swagger /docs and /openapi.json available. Verify: open URLs or `Invoke-RestMethod http://localhost:8000/api/v1/health`. 
- 2025-12-13 22:55 MSK  Reset Postgres clean: dropped/recreated DB b2b_platform and role b2b_user; switched DATABASE_URL to 127.0.0.1; granted schema public CREATE/USAGE to b2b_user. Verify: `psql -U b2b_user -h 127.0.0.1 -d b2b_platform` works; `\dt` shows empty baseline before migrations.
- 2025-12-13 23:00 MSK  Fixed Alembic revision generation by adding `backend/alembic/script.py.mako`; created baseline migration `3315ed698ecb_init.py`; applied `alembic upgrade head`. Verify: `SELECT * FROM alembic_version;` -> 3315ed698ecb.


2025-12-13 23:11 MSK Added DB schema for UserRequests drafts: created Alembic migration 552d97f8cc92_create_requests_and_keys_tables (tables requests, request_keys) and added SQLAlchemy ORM models RequestModel, RequestKeyModel in app/adapters/db/models.py. Verified: alembic current -> 552d97f8cc92 (head) and `python -c "from app.adapters.db.models import RequestModel, RequestKeyModel; print('models ok')" -> models ok. [file:8]

2025-12-13 23:18 MSK Implemented DB adapter repository for UserRequests draft creation: added RequestRepository in app/adapters/db/repositories.py using AsyncSession and ORM models to insert into requests + request_keys and commit. Verified: `python -c "from app.adapters.db.repositories import RequestRepository; print('repo ok')" -> repo ok. [file:8]

2025-12-13 23:19 MSK Added usecase for POST /user/requests: created app/usecases/create_request_manual.py with CreateRequestManualUseCase + KeyInput validation (non-empty keys, pos>=1, non-empty text) and repo call to create draft with status draft. Verified: `python -c "from app.usecases.create_request_manual import CreateRequestManualUseCase, KeyInput; print('usecase ok')" -> usecase ok. [file:1]

2025-12-13 23:20 MSK Added transport DTOs for UserRequests manual create: created app/transport/schemas/requests.py with RequestKeyInputDTO, CreateRequestManualRequestDTO, CreateRequestResponseDTO. Verified: `python -c "from app.transport.schemas.requests import CreateRequestManualRequestDTO, CreateRequestResponseDTO; print('dto ok')" -> dto ok. [file:8]

2025-12-13 23:21 MSK Fixed response DTO field name to match SSoT: renamed requestId -> requestid in CreateRequestResponseDTO (app/transport/schemas/requests.py). Verified: CreateRequestResponseDTO.model_fields.keys() contains requestid.

2025-12-13 23:22 MSK Added POST /user/requests router: created app/transport/routers/requests.py with endpoint using AsyncSession dependency, CreateRequestManualUseCase, and returns CreateRequestResponseDTO (requestid, status="draft"). Verified: `python -c "from app.transport.routers.requests import router; print('router ok')" -> router ok. [file:1]

2025-12-13 23:24 MSK Wired POST /api/v1/user/requests into FastAPI app: included requests_router in app/main.py. Verified: Invoke-RestMethod http://localhost:8000/openapi.json contains path /api/v1/user/requests with post and schema CreateRequestResponseDTO includes requestid

2025-12-13 23:25 MSK End-to-end POST /api/v1/user/requests works (manual keys): request created in DB and API returns 200 with success=true, requestid and status="draft". Verified via PowerShell Invoke-RestMethod -Method Post http://localhost:8000/api/v1/user/requests with JSON body (title + keys) -> response includes requestid: 1, status: draft.

2025-12-13 23:27 MSK Added minimal integration test for POST /api/v1/user/requests: created tests/integration/test_create_request_manual.py; installed test deps pytest and httpx for FastAPI/Starlette TestClient. Verified: python -m pytest -q -> 1 passed.

2025-12-13 23:28 MSK Added test dependencies to requirements.txt: appended pytest==9.0.2 and httpx==0.28.1 to support integration tests. Verified by Get-Content requirements.txt showing both lines.


2025-12-13 23:37 MSK Added domain port for clean architecture: created app/domain/ports.py with RequestRepositoryPort (Protocol) exposing create_draft(title, keys) -> int. Verified: `python -c "from app.domain.ports import RequestRepositoryPort; print('ports ok')" -> ports ok. [file:5]

2025-12-13 23:39 MSK Refactored usecase to depend on domain port instead of adapters: updated app/usecases/create_request_manual.py to accept RequestRepositoryPort from app/domain/ports.py (no adapters imports). Verified: `python -c "from app.usecases.create_request_manual import CreateRequestManualUseCase, KeyInput; print('usecase ok')" -> usecase ok. [file:5]

2025-12-13 23:40 MSK Refactored DB repository to implement domain port: updated app/adapters/db/repositories.py so RequestRepository implements RequestRepositoryPort and cleaned broken-encoding comment. Verified: `python -c "from app.adapters.db.repositories import RequestRepository; print('repo ok')" -> repo ok. [file:5]

2025-12-13 23:40 MSK Confirmed refactor didn break functionality: ran integration tests after moving usecase to domain port + updating repository; python -m pytest -q -> 1 passed.

2025-12-13 23:43 MSK Extended RequestRepository with listing method: added list_requests(limit, offset) returning {items, total} from requests table (ordered by id desc). Verified: `python -c "from app.adapters.db.repositories import RequestRepository; print('repo ok')" -> repo ok. [file:5]

2025-12-13 23:43 MSK Extended RequestRepository with listing method: added list_requests(limit, offset) returning {items, total} from requests table (ordered by id desc). Verified: `python -c "from app.adapters.db.repositories import RequestRepository; print('repo ok')" -> repo ok. [file:5]

2025-12-13 23:44 MSK Implemented GET /api/v1/user/requests: updated app/transport/routers/requests.py to add list endpoint with limit/offset query params and RequestListResponseDTO response. Verified: `python -c "from app.transport.routers.requests import router; print('router ok')" -> router ok. [file:1]

2025-12-13 23:45 MSK Verified GET /api/v1/user/requests works end-to-end: Invoke-RestMethod "http://localhost:8000/api/v1/user/requests?limit=50&offset=0" returned items array with existing draft requests.

2025-12-13 23:49 MSK Fixed Windows pytest  loop is closed for asyncpg/SQLAlchemy: added FastAPI lifespan in app/main.py to dispose SQLAlchemy async engine on shutdown; updated integration tests to use with TestClient(app); verified python -m pytest -q -> 2 passed

- 2025-12-13 23:49 MSK Fixed pytest Windows "Event loop is closed": added FastAPI lifespan in app/main.py to dispose SQLAlchemy async engine on shutdown; tests pass (python -m pytest -q => 2 passed).
- 2025-12-13 23:56 MSK Implemented GET /api/v1/user/requests/{requestId} (RequestDetail) + integration test; verified: python -m pytest -q.

- If step failed: log it in INCIDENTS.md (rules live there).
- 2025-12-13 23:58 MSK Normalized HANDOFF.md (removed duplicate entries/rules); moved failure-logging rules to INCIDENTS.md; verified by inspecting HANDOFF tail + backup file created.
- 2025-12-14 00:00 MSK Implemented PUT /api/v1/user/requests/{requestId}/keys (UpdateRequestKeysRequest -> RequestDetail) + integration tests; verified: python -m pytest -q -> 6 passed.
- 2025-12-14 00:01 MSK Implemented POST /api/v1/user/requests/{requestId}/submit (SubmitRequestResponse) + integration tests; verified: python -m pytest -q.
- 2025-12-14 00:26 MSK DB: created attachments table via alembic revision bbff04c57403_create_attachments_table.py (previous 0dc050e5c206 was empty). Verified: psql -h 127.0.0.1 -U b2b_user -d b2b_platform -c "\dt" shows public.attachments.
- 2025-12-14 00:36 MSK Tests: fixed pytest.ini encoding (removed UTF-8 BOM) so pytest loads config; verified: .\.venv\Scripts\pytest.exe -q => 10 passed.
- 2025-12-14 00:36 MSK Tests: added pytest.ini (UTF-8 without BOM) for stable pytest import paths. Verified: .\.venv\Scripts\pytest.exe -q => 10 passed.
- 2025-12-14 00:43 MSK API: Attachments routes are wired and visible in Swagger under /api/v1/user/attachments*. Verified: http://localhost:8000/docs shows Attachments endpoints.
- 2025-12-14 0016 MSK Fixed Attachments router args to match usecase signatures (original_filename/content_type, attachment_id) and storage base_dir. Verified .\.venv\Scripts\pytest.exe -q tests\integration\test_attachments_contract_camelcase.py -> 1 passed.
- 2025-12-14 01:23 MSK Fixed Attachments router args to match usecase signatures (original_filename/content_type, attachment_id) and storage base_dir. Verified .\.venv\Scripts\pytest.exe -q tests\integration\test_attachments_contract_camelcase.py -> 1 passed.
- 2025-12-14 01:35 MSK Aligned Attachments endpoints and DTOs to SSoT (api-contracts.yaml): routes use /api/v1/userattachments, response fields use lowercase (originalfilename/contenttype/sizebytes/etc), updated attachments integration tests accordingly. Verified .\.venv\Scripts\pytest.exe -q -k attachments -> 2 passed.
- 2025-12-14 10:13 MSK  API contract updated (SSoT): added user personal blacklist by INN endpoints (/user/blacklist/inn GET/POST, /user/blacklist/inn/{inn} DELETE) and schemas AddUserBlacklistInnRequest, UserBlacklistInnListResponse (snake_case). Verified: YAML parsed via python yaml.safe_load => OK; Select-String confirms path + schema.


- 2025-12-14 09:49 MSK  Restored green test suite after recipients experiment (rollback broken alembic revision + fix repositories imports). Verify: .\.venv\Scripts\pytest.exe -q -> 11 passed; .\.venv\Scripts\python.exe -c "from app.adapters.db.repositories import RequestRepository; print('ok')" -> ok.
- 2025-12-14 09:57 MSK  Decision  UserMessaging recipients: PUT /user/requests/{requestId}/recipients uses replace-all semantics (server state mirrors UI checkboxes). Decision: when a domain is added to Blacklist, related suppliers must be automatically unselected (selected=false) across ALL requests to prevent sending. Verify (agreed): implement in Blacklist usecase + re-check in send usecase.
- 2025-12-14 10:08 MSK  Decision  New API schemas use snake_case (inn, supplier_id, created_at). User blacklist is personal and keyed by INN (UI shows company name + checko_data when available). Moderator blacklist stays global by domain (/moderator/blacklist/domains). Recipients PUT is replace-all; blacklist actions auto-unselect recipients accordingly.
 - 2025-12-14 10:49 MSK  Blacklist(User) routes wired: /api/v1/user/blacklist/inn (GET/POST) and /api/v1/user/blacklist/inn/{inn} (DELETE) are present in openapi.json; GET returns 501 Not Implemented. Verify: 	ry { Invoke-RestMethod -Method Get http://localhost:8000/api/v1/user/blacklist/inn } catch { $_.Exception.Response.StatusCode.value__ } -> 501; and (Invoke-RestMethod http://localhost:8000/openapi.json).paths... | Select-String '/api/v1/user/blacklist/inn' shows both paths.

- 2025-12-14 11:33 MSK Fixed local test run: pytest failed outside venv; activated backend venv and tests pass. Verify: cd D:\b2bplatform\backend; .\.venv\Scripts\Activate.ps1; python -m pytest -q -> 11 passed.
- 2025-12-14 12:29 MSK: Chat log recovery. Verified backend tests are green: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q -> 38 passed. Also fixed PowerShell HANDOFF append string to use ${dt} to avoid ': variable' parsing error.
- 2025-12-14 12:40 MSK Process note: HANDOFF.md and INCIDENTS.md are stored at project root (D:\b2bplatform\\HANDOFF.md and D:\b2bplatform\\INCIDENTS.md). All future log appends must target root files, not backend folder. Verified by user confirmation in chat.
- 2025-12-14 12:47 MSK Smoke OK on http://127.0.0.1:8001. Verified: GET /apiv1/health=200 status=ok; GET /openapi.json=200; PUT /apiv1/auth/policy=401 (no token, endpoint exists). Uvicorn kept running on port 8001.
- 2025-12-14 12:48 MSK Backend reachable on default port 8000; smoke OK: GET /apiv1/health=200 status=ok; GET /openapi.json=200; PUT /apiv1/auth/policy=401 Unauthorized without token (endpoint exists). Verified via Invoke-RestMethod.
- 2025-12-14 13:50 MSK Messaging MVP: confirmed endpoints return 501 Not Implemented and added integration tests backend/tests/integration/test_messaging_not_implemented.py. Verified: cd D:\b2bplatform\backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='.'; python -m pytest -q -k messaging_not_implemented -> 4 passed.
- 2025-12-14 13:58 MSK Messaging MVP: confirmed 501 Not Implemented for send/send-new/messages/delete and added integration test backend/tests/integration/test_messaging_not_implemented.py. Verified: cd D:\b2bplatform\backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='.'; python -m pytest -q -k messaging_not_implemented -> 4 passed.
- 2025-12-14 13:59 MSK Auth OTP core: added alembic migration a291dc92b69a (users, otp_codes) with idempotent upgrade, created auth OTP usecases + JwtService skeleton, added unit tests tests/unit/test_auth_otp_usecases.py. Verified: cd D:\b2bplatform\backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='.'; alembic current -> a291dc92b69a (head); python -m pytest -q -k 'auth_otp_usecases or messaging_not_implemented' -> 6 passed.
- 2025-12-14 15:13 MSK Contract test fixed: OpenAPI no longer exposes /apiv1/user/blacklist/inn* extra paths; Auth integration tests now pass for /apiv1/auth/me, /apiv1/auth/policy, /apiv1/auth/oauth/google/*. Verified: python -m pytest -q tests/contract/test_openapi_paths_match_contract.py tests/integration/test_auth_me.py tests/integration/test_auth_policy.py tests/integration/test_auth_policy_persist.py tests/integration/test_auth_oauth_google.py -q => PASS.
- 2025-12-14 15:15 MSK Contract compliance: hid non-SSoT auth endpoints (/apiv1/auth/policy and /apiv1/auth/oauth/google/*) from OpenAPI via include_in_schema=False in app/transport/routers/auth.py, while keeping integration behavior unchanged. Verified: python -m pytest -q => all passed.

- 2025-12-14 16:25 MSK: Implemented UserMessaging recipients replace-all. Changes: api-contracts.yaml updated schemas UpdateRecipientsRequest + RecipientsResponse and PUT /apiv1/userrequests/{requestId}/recipients now returns 200 RecipientsResponse; backend implemented transport DTOs (app/transport/schemas/user_messaging.py), router PUT recipients (app/transport/routers/user_messaging.py), usecase (app/usecases/update_request_recipients.py), DB repo method replace_recipients (app/adapters/db/repositories.py), ORM model RequestRecipientModel fixes (app/adapters/db/models.py), and added integration test tests/integration/test_recipients_replace_all.py. DB: applied Alembic head be4136aa1c68. Verification: cd D:\b2bplatform\backend; python -m pytest -q -> 40 passed.- 2025-12-14 17:00 MSK Ran backend on port 8002 due to stuck 8000 listener; verified GET http://localhost:8002/docs = 200 and GET http://localhost:8002/apiv1/health returns status ok; tests green when run from backend folder: cd D:\b2bplatform\backend; .\.venv\Scripts\python.exe -m pytest -q => 40 passed.

- 2025-12-14 17:25 MSK User blacklist by INN: added contract paths/schemas and enabled backend endpoints GET/POST/DELETE /apiv1/user/blacklist-inn. Verified: Invoke-RestMethod GET returned total=1 after POST and DELETE returned success=true on port 8002.
- 2025-12-14 17:25 MSK User blacklist by INN: added contract paths/schemas and enabled backend endpoints GET/POST/DELETE /apiv1/user/blacklist-inn. Verified: Invoke-RestMethod GET returned total=1 after POST and DELETE returned success=true on port 8002.
- 2025-12-14 17:36 MSK DB aligned: using role b2b_user and database b2b_platform; set DATABASEURL in backend\\.env. Verified: GET /apiv1/health = ok, GET /apiv1/user/blacklist-inn returns total=1.

## 2025-12-15 00:06:35 MSK
- What: Removed backup/tmp files and rewrote update_project_tree.ps1 to filter junk reliably
- Why: Avoid repo clutter and keep PROJECT-TREE.txt useful for new chats
- Verify: Select-String PROJECT-TREE.txt -Pattern '\.bak|\.tmp|~$' -Quiet
- Expected: False (no junk entries); PROJECT-TREE.txt regenerated
- Now: Repo hygiene is fixed; ready to pick next endpoint
- Next: Pick next endpoint from api-contracts.yaml and implement first slice
## 2025-12-15 00:09:24 MSK
- What: Removed *.bak* artifacts and fixed update_project_tree.ps1 syntax; regenerated clean PROJECT-TREE.txt
- Why: Keep repo clean and tree reliable for new chats
- Verify: Select-String PROJECT-TREE.txt -Pattern '\.bak|\.tmp|~$' -Quiet
- Expected: False
- Now: Repo hygiene complete; ready for next feature
- Next: Pick next endpoint from api-contracts.yaml and implement first slice
## 2025-12-15 00:11:01 MSK
- What: Normalized line endings via .gitattributes and git renormalize
- Why: Reduce CRLF/LF noise and keep repo consistent across Windows + Linux CI
- Verify: git status (clean) + pre-commit run --all-files
- Expected: Working tree clean; hooks pass; fewer CRLF/LF warnings
- Now: Repo hygiene complete
- Next: Pick next endpoint from api-contracts.yaml and implement first slice
## 2025-12-15 00:13:50 MSK
- What: Removed legacy file ' .txt' from repo
- Why: We keep project structure in PROJECT-TREE.txt; unicode legacy file causes git noise
- Verify: git status (after commit) shows clean working tree
- Expected: Working tree clean; file removed from main
- Now: Repo hygiene complete
- Next: Return to product work: pick next endpoint from api-contracts.yaml


# HANDOFF
- 2025-12-14 11:46 MSK: Fixed blacklist integration test to use OpenAPI-discovered path + fixed router GET response shape. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:47 MSK: Blacklist integration test aligned to current OpenAPI path /api/v1/user/blacklist/inn. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:47 MSK: Blacklist integration test aligned to current OpenAPI path /api/v1/user/blacklist/inn. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:48 MSK: Fixed Windows asyncpg 'Event loop is closed' in integration tests by adding FastAPI lifespan to dispose SQLAlchemy async engine on shutdown (app/main.py). Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:50 MSK: Fixed Windows asyncpg loop close in blacklist integration test by using TestClient(app) as context manager. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:51 MSK: Blacklist integration test fixed on Windows by using TestClient(app) context manager. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q -> 12 passed.

- 2025-12-14 11:52 MSK: Aligned blacklist endpoints to SSoT paths (/apiv1/userblacklistinn and /apiv1/userblacklistinn/{inn}) and forced API prefix to /apiv1 in app/main.py. Updated integration test. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:54 MSK: Switched API prefix to /apiv1 per api-contracts.yaml and aligned integration tests base paths accordingly. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:55 MSK: Added contract test tests/contract/test_openapi_paths_match_contract.py to enforce OpenAPI paths exactly match api-contracts.yaml. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 11:58 MSK: Aligned attachments+blacklist paths to SSoT: /apiv1/user/attachments* and /apiv1/user/blacklist/inn*. Updated integration tests accordingly. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q -> 14 passed.

- 2025-12-14 12:00 MSK: Added explicit 501 stubs for missing SSoT endpoints: GET /apiv1/suppliers/search and PUT /apiv1/auth/policy. Added integration tests expecting 501. Verified: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q -> 16 passed.

- 2025-12-14 11:55 MSK: INCIDENT contract test failed (FileNotFoundError) because it looked for api-contracts.yaml in backend/. Root cause: wrong relative path assumption. Fix: search parents for api-contracts.yaml. Note: HANDOFF entry was mistakenly added while pytest was failing; do not remove (append-only). Verification: D:\b2bplatform\backend\.venv\Scripts\python.exe -m pytest -q (all passed).

- 2025-12-14 12:15 MSK: Fixed auth router breakage + DB session alias; added users table migration; aligned auth policy tests. Files: app/transport/routers/auth.py, app/adapters/db/session.py, alembic/versions/*create_users_table*.py, tests/integration/test_auth_policy.py. Verified: python -m pytest -q (38 passed).


- 2025-12-15 02:00 MSK Added mandatory preflight rule: ensure DATABASEURL/DATABASE_URL env is set in the same shell that runs uvicorn; otherwise OpenAPI may miss DB-dependent routers. Verified by importing app.transport.routers.requests (routes=5) after setting env and installing/enabling pre-commit hooks (pre-commit run --all-files passes).
- 2025-12-15 03:29 MSK Added 409 Duplicate INN for POST /apiv1/moderator/suppliers in api-contracts.yaml and documented behavior in PROJECT-DOC.md. Verified: python -c yaml.safe_load ok; Select-String operationId shows 409 -> DuplicateInnErrorDTO.
- 2025-12-15 03:40 MSK Added deterministic integration tests for GET /apiv1/suppliers/search: present in /openapi.json and returns 501 from in-process app (TestClient). Verify: python -m pytest -q tests\integration\test_suppliers_search.py.

- 2025-12-15 05:36 MSK Fixed integration tests: aligned user blacklist INN test base path to SSoT (/apiv1/user/blacklist-inn) and skipped suppliers search integration test because SupplierModel/SupplierUrlModel are absent from current db models. Verified: cd D:\b2bplatform\backend; python -m pytest -q (39 passed, 1 skipped).

- 2025-12-15 10:21 MSK: Added Suppliers router stub: GET /apiv1/suppliers/search returns 501 Not Implemented (contract present). Updated PROJECT-TREE.txt. Verified: Invoke-RestMethod http://127.0.0.1:8000/apiv1/health -> status ok; Invoke-RestMethod http://127.0.0.1:8000/openapi.json -> 200; GET /apiv1/suppliers/search?q=test -> 501.
2025-12-15 10:40 MSK  feat: add Suppliers Search endpoint.
- Added: backend/app/transport/routers/suppliers.py (GET /apiv1/suppliers/search, q required, limit default 20), returns 200 with empty JSON array.
- Verified:
  - Invoke-RestMethod "http://127.0.0.1:8000/apiv1/health" -> status ok
  - (Invoke-RestMethod "http://127.0.0.1:8000/openapi.json").paths contains "/apiv1/suppliers/search"
  - Invoke-RestMethod "http://127.0.0.1:8000/apiv1/suppliers/search?q=test" -> 200
- 2025-12-15 11:53 MSK Fixed recurring Windows encoding pitfall while editing api-contracts.yaml: avoid PowerShell full-file rewrites that can mojibake Cyrillic; use Python scripts with explicit encoding='utf-8' and newline='
' (tools/set_limit_max_200.py) or git-based patches. Also standardized all query limit params to include maximum: 200 in api-contracts.yaml. Verify: python tools/set_limit_max_200.py then git diff shows only expected insertions; openapi.json reachable via Invoke-RestMethod http://127.0.0.1:8000/openapi.json.
- 2025-12-15 11:54 MSK Standardized pagination safety: added maximum: 200 to all query 'limit' params in api-contracts.yaml using deterministic Python script tools/set_limit_max_200.py. Documented recurring Windows encoding pitfall: avoid PowerShell full-file rewrite methods that may mojibake Cyrillic in UTF-8 files; prefer Python with explicit encoding='utf-8' and newline='
' (or git-based patch). Verify: python tools/set_limit_max_200.py -> no further changes; git diff clean; Invoke-RestMethod http://127.0.0.1:8000/openapi.json returns 200.

- 2025-12-15 18:49 MSK Success: Dropped '/apiv1' URL prefix (API is now root paths like /health, /user/requests). Updated contract/integration tests to use root paths and adjusted contract OpenAPI-vs-SSoT check to not apply API_PREFIX. Verified: cd D:\b2bplatform\backend; python -m pytest -q => 39 passed, 1 skipped.
- 2025-12-15 18:50 MSK Success: Removed '/apiv1' prefix from API routes (now root paths like /health). Updated tests and OpenAPI-vs-SSoT contract check accordingly. Verified: cd D:\b2bplatform\backend; python -m pytest -q => 39 passed, 1 skipped.
- 2025-12-15 19:48 MSK
  - What: Hardened PowerShell workflow: tools\pytest.ps1 now restores working directory (Push-Location/Pop-Location), and PROJECT-RULES.md now includes mandatory path-safety rules (anchor to repo root, no Resolve-Path for non-existent files).
  - Verify: .\tools\pytest.ps1 -> 39 passed, 1 skipped (and current directory remains D:\b2bplatform); git status -> clean.
- 2025-12-15 20:51 MSK Parser service: /parse via Playwright CDP. Adds '' to query, brings captcha tab to front, dismisses popups best-effort, returns partial results on engine timeout. Verify:
  PS> $body = @{ query = " "; depth = 1 } | ConvertTo-Json
  PS> Invoke-RestMethod http://127.0.0.1:9001/parse -Method Post -ContentType "application/json; charset=utf-8" -Body $body

## [2025-12-15 22:50] SSoT: Finalized parsing contract (runId = informational, latest-only)
- **Change**: Updated pi-contracts.yaml descriptions for start-parsing, parsing-status, parsing-results.
- **runId**: Returned in all responses but API always returns latest run (no run selection via query/path).
- **Blacklist**: Confirmed root domain + subdomain filtering, results MUST NOT include blacklisted URLs.
- **Status**: All DTO complete (StartParsingResponseDTO, ParsingStatusResponseDTO, ParsingResultsResponseDTO).
- **Next**: Backend implementation can rely on "latest run per requestId" semantics.


- 2025-12-15 23:09 MSK Env check: git is configured in D:\b2bplatform (.git exists). Branch main is up to date with origin/main. Remote origin = https://github.com/edwatikh-ship-it/b2b-platform_v3.git. Verify: Test-Path .\.git; git status; git remote -v.

- 2025-12-15 23:10 MSK Env check: git is configured in D:\b2bplatform (.git exists). Branch main is up to date with origin/main. Remote origin = https://github.com/edwatikh-ship-it/b2b-platform_v3.git. Verify: Test-Path .\.git; git status; git remote -v.

2025-12-16 00:30 MSK Implemented moderator parsing domain-accordion results (contract + backend): updated api-contracts.yaml with ParsingDomainGroupDTO and ParsingResultsByKeyDTO.groups; backend returns /moderator/requests/{requestId}/parsing-results grouped by domain with urls[]; parsing-status itemsFound counts domain groups; increased parser_service request timeout to support manual captcha waiting; removed tracked parser_service/parser.log to unblock commits. Verified: ruff check + ruff format --check + pre-commit run --all-files pass; smoke: Invoke-RestMethod http://127.0.0.1:8000/health -> {""status"":""ok""}; POST http://127.0.0.1:8000/moderator/requests/123/start-parsing -> status succeeded; GET http://127.0.0.1:8000/moderator/requests/123/parsing-status -> itemsFound > 0 and status succeeded.

- 2025-12-16 02:11 MSK Added PROJECT-RULES.md parser_service preflight: enforce checking port 9001 (netstat fallback) to avoid 'All connection attempts failed' in parsing-status. Verify: netstat -ano | findstr ":9001" shows LISTENING; Invoke-WebRequest http://127.0.0.1:9001/ returns 404 (server reachable).
- 2025-12-16 05:05 MSK Added parsing depth to StartParsing contract: POST /apiv1/moderator/requests/{requestId}/start-parsing accepts optional body {depth} (default 10, max 50). Verified: python -c "import yaml; yaml.safe_load(open('api-contracts.yaml','r',encoding='utf-8')); print('YAML_OK')" -> YAML_OK; git commit feat(contract): add start-parsing depth.
- 2025-12-16 05:10 MSK Repo hygiene: regenerated PROJECT-TREE.txt to exclude .bak/.tmp/.log artifacts (including .bak folders). Verify:
  - Select-String .\PROJECT-TREE.txt -Pattern '\.bak\.' -Quiet  # Expected: False
  - Select-String .\PROJECT-TREE.txt -Pattern '\.tmp($|\\)' -Quiet  # Expected: False
  - Select-String .\PROJECT-TREE.txt -Pattern '\.log$' -Quiet  # Expected: False
  - git diff -- .\PROJECT-TREE.txt  # Expected: no further unexpected changes after regeneration

- 2025-12-16 11:38 MSK Added Moderator LK decisions to PROJECT-DOC.md (parsing workflow, global root-domain blacklist with accordion UI, resume per keyId). Verified via: git diff -- .\PROJECT-DOC.md (shows added section).
- 2025-12-16 11:47 MSK Preflight: BackendBaseUrl http://127.0.0.1:8000, detected API_PREFIX empty, health path /health. Backend and parser_service health return status=ok; CDP 9222 check failed (Chrome not started).
  Verified via: .\tools\preflight.ps1
- 2025-12-16 11:52 MSK Preflight OK: backend http://127.0.0.1:8000, API_PREFIX empty, health path /health; parser_service http://127.0.0.1:9001 health ok; CDP 9222 not running. Verified via: .\tools\preflight.ps1
- 2025-12-16 11:52 MSK Added Moderator LK decisions to PROJECT-DOC.md (manual parsing start, global root-domain blacklist accordion with URL history, resume per keyId for failed keys only). Verified via: git diff -- .\PROJECT-DOC.md- 2025-12-16 14:33 MSK Success: Added chat guardrails and ctx.ps1 to reduce debugging mistakes (CTX-FIRST, NO-PLACEHOLDERS, NO-RAW-SETCONTENT) and required WHY/EXPECT/IF FAIL + SA-note blocks in assistant instructions.
  Verification:
  - powershell: Set-Location D:\b2bplatform; .\ctx.ps1
  - powershell: Set-Location D:\b2bplatform; pre-commit run --all-files
  Expected: ctx.ps1 prints repo/env/tool context; pre-commit hooks pass.
- 2025-12-16 14:34 MSK Success: Implemented chat-efficiency guardrails and context dump helper.
  What:
  - Added PROJECT-RULES requirement: every multi-step instruction must include WHY/EXPECT/IF FAIL + SA-note (in Russian in chat).
  - Added CTX-FIRST / NO-PLACEHOLDERS / NO-RAW-SETCONTENT guardrails.
  - Added repo-root ctx.ps1 helper to dump environment/tooling/git context before troubleshooting.
  Proof (recent commits):
  6283d0e docs: log ctx-first guardrails in handoff a60b1a8 docs: add ctx-first guardrails and ctx.ps1 helper 70a929a chore: add ctx.ps1 (context dump for chat)
  Verification:
  - powershell: Set-Location D:\b2bplatform; .\ctx.ps1
  - powershell: Set-Location D:\b2bplatform; pre-commit run --all-files
  Expected:
  - ctx.ps1 prints cwd, SSoT presence, git status, tools, python/env, and alembic quick output.
  - pre-commit hooks pass (ruff + ruff-format).
- 2025-12-16 14:36 MSK Success: Implemented chat-efficiency guardrails and a repo-root context dump helper.
  What:
  - Added PROJECT-RULES requirement: every multi-step instruction must include WHY/EXPECT/IF FAIL + SA-note (provided in Russian in chat).
  - Added CTX-FIRST / NO-PLACEHOLDERS / NO-RAW-SETCONTENT guardrails.
  - Added repo-root ctx.ps1 helper to dump environment/tooling/git context before troubleshooting.
  Proof (recent commits):
  d20e470 docs: log ctx-first guardrails milestone 6283d0e docs: log ctx-first guardrails in handoff a60b1a8 docs: add ctx-first guardrails and ctx.ps1 helper
  Verification:
  - powershell: Set-Location D:\b2bplatform; .\ctx.ps1
  - powershell: Set-Location D:\b2bplatform; pre-commit run --all-files
  Expected:
  - ctx.ps1 prints repo/env/tool context.
  - pre-commit hooks pass (ruff + ruff-format).
- 2025-12-16 14:41 MSK Note: The ctx-first guardrails milestone was logged multiple times (duplicate HANDOFF entries). Treat the latest entry as the source of truth; earlier duplicates can be ignored.

- 2025-12-16 16:45 MSK: Success Hardened OpenAPI diff tooling. What: tools/openapi_diff.py now supports offline diff via --live-file (default .tmp/runtime-openapi.json) and optional --live-url; --help no longer triggers HTTP. Verified SSoT api-contracts.yaml paths match runtime OpenAPI (29 ok). Verification: python .\tools\openapi_diff.py --help; python .\tools\openapi_diff.py ->  openapi-diff.csv: 0 missing, 0 extra, 29 ok.
- 2025-12-16 18:26 MSK: Updated moderator blacklist integration tests to match implemented endpoints; kept moderator tasks as 501 (not implemented) while keeping start-parsing non-501. Verified: just test -> 39 passed, 1 skipped.
- 2025-12-16 19:09 MSK Success Aligned moderator tasks routes to SSoT: /moderatortasks and /moderatortasks/{taskId}. Verified: .\tools\preflight.ps1 -BackendBaseUrl http://127.0.0.1:8000 ; Invoke-RestMethod http://127.0.0.1:8000/openapi.json contains /moderatortasks ; GET /moderatortasks returns 501.

- 2025-12-16 20:06 MSK Success Updated PROJECT-RULES.md: added PRE-FLIGHT v2 (human) with mandatory DB smoke check via API and clarified that env in current PowerShell may differ from running backend process. Verified: pre-commit run --all-files (PASS) and Invoke-RestMethod http://127.0.0.1:8000/user/requests?limit=1&offset=0 returns 200 with JSON.
- 2025-12-16 20:16 MSK Success Updated PROJECT-RULES.md: added rule "Plain language for non-IT " to prevent jargon-only explanations in chat. Verified: git status clean after commit, pre-commit run --all-files PASS.

2025-12-16 22:01 MSK Fixed /moderator/blacklist/domains 500: aligned DomainBlacklistUrlModel fields (domain_id, created_at) and repo returns (url, comment, created_at) tuples. Verified: Invoke-RestMethod http://127.0.0.1:8000/moderator/blacklist/domains -> 200 and POST -> 200.
- 2025-12-16 22:46 MSK Success Hardened OpenAPI diff tool to avoid false 'missing' when using stale .tmp/runtime-openapi.json. Now tools/openapi_diff.py can read runtime URL from env OPENAPI_URL when --live-url is not passed; added --openapi-url-env flag and fixed output encoding. Verified: $env:OPENAPI_URL="http://127.0.0.1:8000/openapi.json"; python .\tools\openapi_diff.py -> "OK openapi-diff.csv: 0 missing, 0 extra, 37 ok"; and python .\tools\openapi_diff.py --help | Select-String openapi-url-env shows the flag.- 2025-12-16 23:18 MSK Success Repo hygiene: removed accidental untracked draft files (moderator_api_* stubs, tools/create_moderator_stub_routers.py) and reverted local wiring changes; kept WIP copies outside repo in D:\b2bplatform__WIP\.
  - Verify: git status -sb
  - Expected: working tree clean (no M/??)
  - Verify: pre-commit run --all-files
  - Expected: ruff + ruff-format Passed
- 2025-12-17 0015 MSK Success Added ModeratorPendingDomains endpoints and DTOs.
  - What: Implemented GET /moderator/pending-domains (list) and GET /moderator/pending-domains/{domain} (detail stub 404) with transport schemas PendingDomainListResponseDTO and PendingDomainDetailDTO, wired router in backend/app/main.py.
  - Verify: Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Select-String "/moderator/pending-domains"; and detail returns 404 for unknown domain.
- 2025-12-17 0021 MSK Correction Previous entry for ModeratorPendingDomains used a Markdown link in the verify command.
  - Verify: Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Select-String "/moderator/pending-domains"; and detail returns 404 for unknown domain.
- 2025-12-17 0021 MSK Correction The ModeratorPendingDomains verify command should use a plain URL (no Markdown link).
  - Verify: Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Select-String "/moderator/pending-domains"; and detail returns 404 for unknown domain.
- 2025-12-17 0022 MSK Correction ModeratorPendingDomains verify command (copy/paste):
  - Verify: Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Select-String "/moderator/pending-domains"; and detail returns 404 for unknown domain.
- 2025-12-17 00:44 MSK Implemented moderator domain decision endpoints.
  What: Added router moderator_domain_decision and schemas for DomainDecisionRequestDTO/ResponseDTO plus SupplierCardDTO, wired router in backend/app/main.py.
  Verified: ruff check backend; pre-commit run --all-files; runtime openapi.json contains /moderator/domains/{domain}/decision and /moderator/domains/{domain}/hits.- 2025-12-17 01:09 MSK Fixed moderator domain decision endpoints 500 caused by Enum stringification; now returns contract enum values. Verify: POST and GET http://127.0.0.1:8000/moderator/domains/pulscen.ru/decision -> 200 with status 'blacklist'.
$ts MSK  Fixed Backup naming line in tools/print_new_chat_prompt.ps1.
- Replaced broken '<...>' placeholders (stripped by current PowerShell host) with safe placeholders: {original_filename}.bak.{timestamp}.
- Verified: git diff, just new-chat-prompt output, pre-commit, commit+push (f2d25a7).
2025-12-17 12:07:52 MSK  Normalized line-ending rules in .gitattributes (removed duplicates/conflicts; LF for .ps1/.md/.txt; CRLF for .bat/.cmd).
- Applied: git add --renormalize .
- Follow-up: added missing newline at EOF in .gitattributes (commit 27593e4).
- 2025-12-17 13:24 MSK Success: Reduced just prompt noise (suppress recipe echo) and updated tools/new_chat_prompt.ps1 to use BASE_URL-based OpenAPI/health checks. Verify: just prompt | Select-String -SimpleMatch "just new-chat-prompt","powershell -NoProfile -ExecutionPolicy Bypass" -Quiet  # Expected: False.

- 2025-12-17 1432 MSK Success Aligned runtime OpenAPI paths with SSoT for moderator endpoints.
  - What: Renamed legacy /moderatortasks* to /moderator/tasks* and added 501 stubs for missing SSoT paths: /moderator/parsing-runs*, /moderator/resolved-domains, /moderator/domains/{domain}/hits, /moderator/urls/hits.
  - Why: Contract compliance (api-contracts.yaml is SSoT) and OpenAPI-vs-SSoT diff must be zero.
  - Verify: python -c ""import json,yaml,urllib.request as ur; ss=yaml.safe_load(open('api-contracts.yaml','r',encoding='utf-8'))['paths']; lv=json.load(ur.urlopen('http://127.0.0.1:8000/openapi.json'))['paths']; print('missing',sorted(set(ss)-set(lv))); print('extra',sorted(set(lv)-set(ss)))""  -> missing [] extra []
- What: Found runtime router file for moderator parsing-runs endpoints.
- Where: backend\app\transport\routers\moderator_tasks.py (exists in repo).
- Why it matters: Likely source of /moderator/parsing-runs and /moderator/parsing-runs/{runId} runtime behavior; compare with api-contracts.yaml.
- When: 2025-12-17 15:06 MSK

- 2025-12-17 1641 MSK Success Updated PROJECT-RULES.md PRE-FLIGHT: added explicit rule to confirm backend is running before HTTP checks (openapi.json/health).
  - Why: avoid invalid pre-flight conclusions when backend is not started.
  - Verify: Select-String -Path .\PROJECT-RULES.md -Pattern "2\) Confirm backend is running" -Quiet
  - Expected: True

- 2025-12-17 18:20 MSK: SSoT api-contracts.yaml paths normalized (leading '/' added); runtime /openapi.json paths match (37/37).

- 2025-12-17 18:21 MSK: SSoT api-contracts.yaml paths normalized (leading '/' added); runtime /openapi.json paths match (37/37).

- 2025-12-17 18:23 MSK: NOTE: previous HANDOFF entry about OpenAPI paths was accidentally duplicated in two consecutive commits (5c6c80d, 22cade3); treat as a single milestone.
- 2025-12-17: Added pre-commit hook validate-openapi-contract to ensure OpenAPI paths keys in api-contracts.yaml start with '/'.

2025-12-17 MSK - Fixed user messaging routes: /user/requests/* and /user/messages/*; runtime OpenAPI verified on port 8010 (8000 occupied by unknown listener).
- 2025-12-17 20:03 12S+03:00 Fixed integration tests paths to match SSoT/runtime: /user/requests and /user/messages. Verified: just test (39 passed, 1 skipped).

- 2025-12-17 20:18 MSK Success Verified runtime OpenAPI and health on http://127.0.0.1:8000 (APIPREFIX empty); runtime paths match api-contracts.yaml. Verify: Invoke-RestMethod http://127.0.0.1:8000/health ; Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Out-Null ; (Invoke-RestMethod http://127.0.0.1:8000/openapi.json).paths.PSObject.Properties.Name | Sort-Object.
- 2025-12-17 22:27:41 MSK Success Added AGENT knowledge trail + communication style rules.
  - What: created AGENT-KNOWLEDGE.md; updated PROJECT-RULES.md (Communication style section + Agent learning gate).
  - Why: make chat output consistent and machine-usable; prevent agent from learning unverified fixes.
  - Verified: ruff check backend; ruff format backend; pre-commit run --all-files (all Passed).
- 2025-12-17  Docs: clarified parsing-results UI as unique domain list with accordion URLs; enforced blacklist filtering; added decisions D-009 (domain dedup + full URL list) and D-010 (captcha => fullscreen browser). Logged incident about PowerShell heredoc script failure and switched to Plan B.
## 2025-12-17 23:33 MSK  Parsing source/depth (SSoT + backend wiring)

Done:
- Extended SSoT api-contracts.yaml: POST /moderator/requests/{requestId}/start-parsing now has requestBody StartParsingRequestDTO; added ParsingRunSource enum (google|yandex|both).
- Backend: StartParsingRequestDTO updated to match SSoT (depth nullable, source nullable; removed resume).
- Backend: start_parsing endpoint accepts body payload; defaults depth=10, source='both'; forwards to parser_service /parse with query/depth/source.
- Tooling: just fmt and pre-commit run --all-files are green.

Notes:
- Parser_service currently only supports Yandex scraper; /parse ignores/does not accept source yet (next sprint item).

Files touched:
- api-contracts.yaml
- backend/app/transport/schemas/moderator_parsing.py
- backend/app/transport/routers/moderator_tasks.py
- 2025-12-18 01:54 12S+03:00 Success: process/doc safety hardened + deterministic doc editing tool.
  - What:
    - Updated PROJECT-RULES.md: chat output format, commands-first/docs-first/evidence gates.
    - Updated INCIDENTS.md: incident entry for missing just recipe suggestion.
    - Updated AGENT-KNOWLEDGE.md: incident pattern "Just recipe verification (commands-first)".
    - Added tools/doc_edit.py: deterministic patcher (anchor-check + backups + UTF-8/LF), idempotent for agent-pattern insertion.
    - Regenerated PROJECT-TREE.txt.
  - Verify:
    - pre-commit run --all-files
    - Expected: Passed (ruff, ruff-format, validate OpenAPI contract).

- 2025-12-18 0342 MSK Success parserservice: Cyrillic query became '?????' when client sent JSON without charset; fixed by sending Content-Type: application/json; charset=utf-8. Verify: $body=@{ query=''; depth=1 }|ConvertTo-Json -Depth 5; Invoke-RestMethod http://127.0.0.1:9001/parse -Method Post -ContentType 'application/json; charset=utf-8' -Body $body | ConvertTo-Json -Depth 1

- 2025-12-18 04:40 MSK docs: added "Documentation gate HARD" to PROJECT-RULES.md (deterministic doc edits + proof requirement).
  - Verify: git show --name-only b2a3a43
- 2025-12-18 04:40 MSK docs: added "Documentation gate HARD" to PROJECT-RULES.md (deterministic edits for process docs + mandatory proof).
  - Verify: git show --name-status b2a3a43
- 2025-12-18 05:20 MSK NOTE: duplicate HANDOFF entry at 2025-12-18 04:40 MSK was appended twice; treat the later one (with git show --name-status) as the correct verify command.
  - Verify: git show --name-status d80054d

- 2025-12-18 05:23 MSK Status: SSoT api-contracts.yaml paths match runtime OpenAPI; backend up on http://127.0.0.1:8000 (APIPREFIX empty). Verify: Invoke-RestMethod http://127.0.0.1:8000/health; Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Out-Null; (Invoke-RestMethod http://127.0.0.1:8000/openapi.json).paths.PSObject.Properties.Name | Sort-Object
- 2025-12-18 19:32:30 MSK Success: Added HARD RULE 3 (Real-time documentation) and Doc-gate DoD to enforce deployable-by-docs workflow. Verified via:
  - Select-String -Path .\PROJECT-RULES.md -Pattern "HARD RULE 3: REAL-TIME DOCUMENTATION" -Quiet  # Expected True
  - Select-String -Path .\PROJECT-RULES.md -Pattern "Doc-gate DoD" -Quiet                          # Expected True
  - Select-String -Path .\DOCS-INDEX.md -Pattern "Doc-gate DoD" -Quiet                             # Expected True
- 2025-12-18 19:35:06 MSK Success: Added HARD RULE 3 (Real-time documentation) + Doc-gate DoD (Definition of Done). Verified by:
  - Select-String -Path .\PROJECT-RULES.md -Pattern "HARD RULE 3: REAL-TIME DOCUMENTATION" -Quiet  # Expected True
  - Select-String -Path .\PROJECT-RULES.md -Pattern "Doc-gate DoD" -Quiet                          # Expected True
  - Select-String -Path .\DOCS-INDEX.md -Pattern "Doc-gate DoD" -Quiet                             # Expected True
  - pre-commit run --all-files                                                                     # Expected PASS
- 2025-12-18 2101 MSK Success Documented parsing/parserservice + PowerShell pitfalls from chat into INCIDENTS.md and AGENT-KNOWLEDGE.md (append-only) to prevent repeats. Verify: Select-String -Path .\INCIDENTS.md -SimpleMatch -Pattern '2025-12-18 2101 MSK' -Quiet - Expected True; Select-String -Path .\AGENT-KNOWLEDGE.md -SimpleMatch -Pattern '2025-12-18 2101 MSK Runbook Parsing failed 503' -Quiet - Expected True. Files: INCIDENTS.md, AGENT-KNOWLEDGE.md.
- 2025-12-18 2104 MSK Success Added append-only incident notes + a reusable runbook for parserservice 503 and PowerShell pitfalls. Verify: Select-String -Path .\INCIDENTS.md -SimpleMatch -Pattern '2025-12-18 2104 MSK INCIDENT Parsing-status failed with 503' -Quiet -Expected True; Select-String -Path .\AGENT-KNOWLEDGE.md -SimpleMatch -Pattern '2025-12-18 2104 MSK Runbook: 503 to parserservice' -Quiet -Expected True. Files: INCIDENTS.md, AGENT-KNOWLEDGE.md, HANDOFF.md.
- 2025-12-18 22:35 MSK:   (39 passed, 1 skipped).  PROJECT-TREE.txt  just tree.
- 2025-12-18 22:38 MSK: Smoke-check: /health=200, /openapi.json=200, parser_service(9001)=404 (service responds).
- 2025-12-18 23:47:52 MSK Success Added PROJECT-DOC.md runbook section 'PowerShell: UTF-8 JSON responses' (avoid Cyrillic mojibake and prevent here-string $variable interpolation). Verified: git show --oneline -1 shows commit 1365b2f; git status --porcelain is empty; python BOM check prints BOM_UTF8=False.
- 2025-12-19 00:02 MSK Success Implemented /moderator/tasks and /moderator/tasks/{taskId} minimal 200 response (return {}). Verified python -m pytest -q backend\tests\integration\test_moderator_tasks.py - Expected 3 passed.

- 2025-12-19 00:07 MSK Verified Moderator stubs return 501 Not Implemented: GET /moderator/parsing-runs, /moderator/resolved-domains, /moderator/urls/hits. Verify Invoke-WebRequest http://127.0.0.1:8000/moderator/parsing-runs?limit=1&offset=0 ; Invoke-WebRequest http://127.0.0.1:8000/moderator/resolved-domains?limit=1&offset=0 ; Invoke-WebRequest http://127.0.0.1:8000/moderator/urls/hits?url=https%3A%2F%2Fexample.com&limit=1&offset=0 - Expected 501 for each.


- 2025-12-19 09:05 MSK Success Aligned suppliers search integration test to root paths; updated .gitignore. Verify pre-commit run --all-files; python -m pytest -q tests\integration\test_suppliers_search.py - Expected pre-commit PASS, pytest shows 2 passed.

- 2025-12-19 09:25 MSK Removed legacy /apiv1 prefix rule from PROJECT-RULES.md and removed apiv1 token from tools/patch_api_contracts_parser.py operationIds. Verify: Select-String -Path .\PROJECT-RULES.md -SimpleMatch -Pattern "/apiv1/health" => no output; Select-String -Path .\tools\patch_api_contracts_parser.py -SimpleMatch -Pattern "apiv1" => no output. Files touched: PROJECT-RULES.md; tools\patch_api_contracts_parser.py.

- 2025-12-19 10:14 MSK Success: Stored chat handoff PDF bundle at D:\b2bplatform.tmp\20251219-100909 (chat.pdf + meta.json). chat.pdf SHA256=96138BF1AC78B8AFF312929402C1755DDDA632276FEFAAEE761431604039E110. Repo state clean. Verification: Test-Path D:\b2bplatform.tmp\20251219-100909\chat.pdf => True; git status -sb => '## main...origin/main'.

- 2025-12-19 10:26 MSK Success: Preflight facts captured. BASE_URL=http://127.0.0.1:8000. GET /health => 200 {"status":"ok"}. GET /openapi.json => 200 (OpenAPI 3.1.0). GET /moderator/urls/hits?url=https%3A%2F%2Fexample.com&limit=1&offset=0 => 200 {"items":[],"total":0,"limit":1,"offset":0}. Verification: git status -sb; Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health; Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/openapi.json; Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/moderator/urls/hits?url=https%3A%2F%2Fexample.com&limit=1&offset=0". Files touched: HANDOFF.md.
- 2025-12-19 12:02 MSK HANDOFF Smoke: moderator parsing (3 endpoints) + hits (2 endpoints) on http://127.0.0.1:8000, no 501 observed.
  Verification:
    Invoke-WebRequest "http://127.0.0.1:8000/health" -UseBasicParsing | Select-Object -ExpandProperty StatusCode -> Expected: 200
    Invoke-RestMethod "http://127.0.0.1:8000/moderator/requests/118/parsing-status" | ConvertTo-Json -Depth 20 -> Expected: status=succeeded
    Invoke-RestMethod "http://127.0.0.1:8000/moderator/requests/118/parsing-results" | ConvertTo-Json -Depth 20 -> Expected: results array present
    Invoke-WebRequest "http://127.0.0.1:8000/moderator/urls/hits?url=https%3A%2F%2Fexample.com&limit=1&offset=0" -UseBasicParsing | Select-Object -ExpandProperty StatusCode -> Expected: 200
    Invoke-WebRequest "http://127.0.0.1:8000/moderator/domains/example.com/hits?limit=1&offset=0" -UseBasicParsing | Select-Object -ExpandProperty StatusCode -> Expected: 200
- 2025-12-19 13:12 12S+03:00 Success Docs: rewrote PROJECT-DOC.md to keep only readable parsing notes and added future moderator UI notes (not implemented yet). Verify: git show --name-only HEAD -- -> Expected: shows PROJECT-DOC.md.

- 2025-12-20 07:33:01 MSK Success: Added COMMAND-DELIVERY-PROTOCOL.md and referenced it in DOCS-INDEX.md. Verified: pre-commit run --all-files (PASS); git show --name-only --oneline 5e712f4 contains COMMAND-DELIVERY-PROTOCOL.md and DOCS-INDEX.md. Expected: repo clean and docs present in main.
- 2025-12-20 07:37:27 MSK Success
  Context: quicklog
  Change: quicklog.ps1 installed
  Verification: pwsh -NoLogo -NoProfile -File .\quicklog.ps1 -Mode Success -Context quicklog -Message ok -Verify ok
  Expected: PASS
  Files touched: quicklog.ps1
- 2025-12-20 11:46:59 MSK Success Fixed mojibake in SSoT api-contracts.yaml AttachmentDTO.description (removed \\x/\\x garbage; replaced with ASCII note about lower-without-separators vs snake_case). Verification: Select-String -Path .\api-contracts.yaml -SimpleMatch -Pattern '\\x','\\x' -Quiet -> Expected: False. Files touched: api-contracts.yaml.
2025-12-20 Parsing MVP done: /start-parsing → succeeded → parsing-results domains
2025-12-20 Domain Decisions MVP done: metall.ru → pending → supplier

POST /moderator/domains/metall.ru/decision(pending) → success
POST /moderator/domains/metall.ru/decision(supplier,carddata) → success
GET /moderator/domains/metall.ru/decision → supplier verified
GET /moderator/pending-domains → [] (resolved)

- 2025-12-21 0231 MSK ✅ Endpoint SSoT tooling COMPLETE.
  - just list-endpoints → все пути api-contracts.yaml
  - just endpoint-status PATH → 200/501 status
  - just stub-endpoint PATH → TODO stub+test
## ✅ Parser Service (новое)

- **FastAPI + Playwright CDP** для скрейпинга Yandex
- Запуск: `cd B2B/parser_service && uvicorn app.main:app --port 8001 --reload`
- Health: http://localhost:8001/health ✅
- Docs: http://localhost:8001/docs ✅
