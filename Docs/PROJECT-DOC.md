## Parsing: implementation notes (MVP)

### Depth (search pages)
- Depth controls how many search result pages are fetched per key (pages in the search engine), not a max-URL limit.
- The parser stops when it reaches the depth page limit even if more results exist.
- Default depth should be conservative for MVP (e.g., 1-3 pages) to reduce rate limits/captcha risk; tune later based on real usage.

### Domain blacklist (root-domain)
- Blacklist is stored as root domains (e.g., pulscen.ru).
- Root-domain blacklist blocks the domain itself AND all subdomains (e.g., spb.pulscen.ru, msk.pulscen.ru).
- Blacklisted results must be filtered server-side and must not appear in parsing-results at all (moderator should never see them).

### Accordion (domain groups)
- UI shows parsing results grouped by domain (accordion): domain -> list of URLs.
- Grouping is done after blacklist filtering.
- Domain in results may include subdomains; blacklist matching must normalize URL hostname to root-domain for filtering logic.

### Processing pipeline (recommended)
- parser_service: collects raw URLs per key by querying search engines up to Depth pages.
- backend: normalizes domains, applies root-domain blacklist filtering, and groups results by domain before returning them to the moderator endpoints.

## Decisions (ADR)

### D-007 — Parsing results as domain accordion
- Date: 2025-12-16 00:29 MSK
- Decision: /moderator/requests/{requestId}/parsing-results returns results grouped by domain: each group contains domain and urls[] (accordion UI).
- Why: Moderator sees unique domains without noise, but can expand to view all URLs per domain.
- Consequences: Contract updated (ParsingDomainGroupDTO, ParsingResultsByKeyDTO.groups). Backend stores and returns grouped results.

### D-008 — Parsing execution mode (MVP sync, target async)
- Date: 2025-12-16 00:29 MSK
- Decision: MVP keeps synchronous start-parsing (request waits for parser_service; timeout increased to allow manual captcha). Target: start-parsing returns quickly with status=running/queued and parsing runs in background; UI polls parsing-status/results.
- Why: Avoid client/proxy timeouts and improve UX/reliability.
- Consequences: Later introduce background task runner (in-process for MVP, then queue) without changing API semantics.

### D-009 — Parsing results dedup by domain (accordion)
- Date: 2025-12-17 23:13 MSK
- Decision: In parsing-results shown to the moderator, the list is de-duplicated by domain; the accordion contains all collected URLs for that domain.
- Blacklist rule: Blacklisted root-domains (and all subdomains) must not appear in parsing-results.
- Logs: Full raw findings are preserved in logs/hits (key->url->domain), including duplicates and occurrences for already decided/blacklisted domains.

### D-010 — Captcha requires fullscreen browser window
- Date: 2025-12-17 23:13 MSK
- Decision: If a captcha challenge appears during parsing, the browser window must be automatically maximized (fullscreen) so the moderator can see it immediately and solve it quickly.

## Moderator LK decisions (parsing + blacklist + resume)

- Priority: Moderator processes incoming client requests first; in free time, uses parsing results to gradually fill the suppliers base.
- Parsing start: Manual action in moderator LK (button like "Get URLs"). No auto-start for MVP.
- Parsing results: Moderator reviews URL groups and either creates supplier cards or adds domains to the global blacklist.

### Global domain blacklist (root-domain)
- Blacklist key is a hostname/root-domain only (e.g. cvetmetall.ru), without scheme (https://) and without trailing slash (/).
- Blacklist is global (shared across all requests and moderators).
- Blacklisted domains (including subdomains) MUST NOT appear in parsing-results responses (server-side filtering).

### Resume behavior (per key)
- If parsing partially fails, already collected results are preserved.
- Resume is per keyId: next start-parsing should parse only failed keys and continue from the page where the key failed (successful keys are not re-parsed).
- Comment on blacklist add is optional.

## Future UI notes (not implemented yet)

### Moderator UI: parsing desk
- Goal: Moderator needs a working desk to run parsing, review domains/URLs, make decisions (4 statuses), and gradually build the supplier base.
- Parsing start: Manual action in moderator UI (button like "Get URLs"). No auto-start for MVP.

### Results UI (accordion)
- Results shown to the moderator are grouped by domain (accordion): domain -> list of URLs.
- Domains that match the global root-domain blacklist MUST NOT appear in parsing results at all (server-side filtering).
- For each domain/URL, UI should show which keys produced it (key -> url -> domain mapping).

### Domain decisions (4 statuses)
- Green: Create Supplier card (required: INN, company name, email; URL auto-filled from parsed domain/URL).
- Purple: Create Reseller/Trading Organization card (same required fields; marked/flagged as reseller for users).
- Black: Add domain to global blacklist (root-domain; blocks subdomains); optional comment.
- Yellow: Pending decision queue; domain stays visible until decided.

### History and logging
- Each manual parsing run should be stored in history (list + details).
- Even if a domain is already decided/blacklisted, log every occurrence: key -> url -> domain (so moderator can see which keys keep producing that domain).

### Resume behavior (per key)
- If parsing partially fails, already collected results are preserved.
- Resume is per keyId: next start-parsing should parse only failed keys and continue from the page where the key failed (successful keys are not re-parsed).

### TBD (explicitly not done)
- UI screens themselves (layouts, fields, filters, sorting) are not implemented yet.
- Blacklist UI as accordion with per-domain captured URLs and optional comment is not implemented yet.
- Full moderator parsing run history UI is not implemented yet.
## Docs hygiene note (legacy mojibake)
Added: 2025-12-20 11:52:48 MSK.
Fact: HANDOFF.md and INCIDENTS.md contain historical mojibake/garbled sequences from earlier edits; full decoding is TBD.
Rule: Do not bulk-rewrite append-only logs to 'clean' encoding without verified decoding; prefer adding corrections/notes and keep SSoT files (api-contracts.yaml) clean.
Verification: Select-String -Path .\api-contracts.yaml -SimpleMatch -Pattern 'Ð\x','Ñ\x' -Quiet -> Expected: False.

## Clean backend sandbox (D:\b2b, GitHub b2b22.12.25)

- Code and env:
  - Local path: D:\b2b (backend/, .venv/, Docs/, justfile).
  - DATABASE_URL points to PostgreSQL: postgresql+asyncpg://b2buser:****@127.0.0.1:5432/b2bplatform (same as original project).
- Git:
  - Clean standalone repository: https://github.com/edwatikh-ship-it/b2b22.12.25
  - Purpose: sandbox for contract-driven backend work, separate from legacy D:\b2bplatform history.
- Runtime:
  - Start: cd D:\b2b\backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 127.0.0.1 --port 8001
  - Health: GET /health -> {"status": "ok"}
  - User requests: GET /user/requests?limit=1&offset=0 -> 200 with items from PostgreSQL.

## Parser Service (Search Parser API) — внешняя интеграция

Source: D:\ProjectVC\search-parser (отдельный репозиторий).

### Режимы работы

1. CLI-режим (ручной запуск модератором / отладка)

- Служебный скрипт `start_chrome_debug.ps1`:
  - Убивает все процессы Chrome.
  - Запускает Chrome с CDP: `--remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug`.
  - Окно PowerShell с этим скриптом нельзя закрывать — оно держит CDP-сессию.
- Новый сеанс модератора:
  - Открыть отдельное окно PowerShell.
  - Выполнить:
    - `cd D:\ProjectVC\search-parser`
    - `.\.venv\Scripts\Activate.ps1`
    - `python cli.py <keyword> <depth> <mode>`
- Параметры:
  - `keyword`: бизнес-ключ (без префикса "buy ", он добавляется только на стороне поиска).
  - `depth`: количество страниц (глубина поиска).
  - `mode`: `yandex|google|both`.
  - `--output`: путь к файлу (по умолчанию `results.txt`).
- Результат:
  - Парсер создаёт `SearchParser`, выполняет запрос и сохраняет все уникальные ссылки в файл.
  - В консоли выводится количество найденных ссылок и имя файла.

2. HTTP API (интеграция с backend B2B)

- FastAPI-приложение в `api.py`:
  - `POST /parse`:
    - Request: `ParseRequest { keyword, depth (1-10), mode (yandex|google|both), output_file? }`.
    - Поведение:
      - Генерирует `task_id = <keyword>_<timestamp>`.
      - Ставит фоновую задачу `parse_task(task_id, request)`.
      - Пишет `results_storage[task_id] = {"status": "running"}`.
      - Возвращает `ParseResponse { task_id, message, started_at }`.
  - `parse_task(task_id, request)`:
    - Создаёт `SearchParser` и вызывает `parser.parse(keyword, depth, mode)`.
    - Сохраняет ссылки в файл `output_file` (по умолчанию `results_<task_id>.txt`).
    - Обновляет `results_storage[task_id]`:
      - Успешно: `{"status": "completed", "links_count", "links", "keyword", "depth, "mode", "output_file"}`.
      - Ошибка: `{"status": "failed", "error"}`.
  - `GET /results/{task_id}`:
    - Возвращает состояние задачи и результаты.
  - `GET /health`:
    - Возвращает статус живости сервиса.

### Связь с ЛК модератора

- При нажатии “Начать парсинг” по ключу (задачи или ручной ввод) backend вызывает Parser Service `POST /parse` с:
  - `keyword` — чистый бизнес-ключ.
  - `depth` — глубина из UI (10–50, маппится в 1–10 для парсера).
  - `mode` — `google|yandex|both`.
- Backend периодически опрашивает `/results/{task_id}`.
- После `status="completed"` backend:
  - Берёт `links` (URL).
  - Извлекает домены.
  - Группирует по доменам (accordion UI).
  - Фильтрует blacklist-домены.
  - Сохраняет результаты и историю в БД (parsing_runs, domain_hits).
- Ошибки парсера:
  - Не пишутся в INCIDENTS.md.
  - Сохраняются в БД и показываются модератору в отдельном окне ошибок.
