# DECISIONS.md — B2B Platform (FROZEN)

Status: DEPRECATED / FROZEN.

Do not add new decisions here.
All new decisions MUST be recorded in PROJECT-DOC.md under: "## Decisions (ADR)".

This file remains as historical context (append-only history, no rewrites except this header).

---

(Original content below, kept for history.)

# DECISIONS.md — B2B Platform (память решений)

Обновляй этот файл только когда принято важное решение (архитектура, правила, стек, контракты).
Цель: не повторять уже пройденное и не “топтаться”.

---

## D-001 — Contract-first (OpenAPI как SSoT)
**Дата:** 2025-12-13  
**Решение:** api-contracts.yaml = единственный источник правды по API.  
**Почему:** чтобы фронт/бэк/сервисы синхронизировались и был бесшовный переезд FastAPI → Node без смены API.  
**Последствия:** любые изменения API сначала в YAML, потом в коде.

---

## D-002 — Жёсткие правила качества (без мусора)
**Дата:** 2025-12-13  
**Решение:** не добавлять нерабочие решения, “костыли”, временные скрипты и свалку в main.py.  
**Почему:** проект должен расти чисто и предсказуемо.  
**Последствия:** архитектура только transport/usecases/domain/adapters (см. PROJECT-RULES.md).

---

## D-003 — Стартовый backend стек: FastAPI
**Дата:** 2025-12-13  
**Решение:** стартуем на FastAPI (Python) для MVP.  
**Почему:** быстрее выйти в работающий продукт, удобнее интеграции (парсинг/ETL/почта) на старте.  
**План миграции:** позже возможен переезд на Node (Nest/Express) без смены api-contracts.yaml.

---

## D-004 — Вложения делаем “как надо”
**Дата:** 2025-12-13  
**Решение:** вложения не передаются бинарниками в JSON.  
**Поток:** upload attachment → получаем attachment_id → send использует attachment_ids.  
**Почему:** так проще поддерживать, масштабировать и валидировать.

---

## D-005 — HANDOFF.md пока не обязателен
**Дата:** 2025-12-13  
**Решение:** HANDOFF.md не используем как обязательный процесс.  
**Почему:** не хотим жёстко привязываться к ритуалу.  
**Компенсация:** DECISIONS.md фиксирует ключевые решения, чтобы не терять контекст.

---

## D-006 — Стиль общения в пространстве
**Дата:** 2025-12-13  
**Решение:** общение “как с братишкой”, простым языком, можно эмоджи, но с техдисциплиной.  
**Почему:** так легче держать темп и не закапываться в бюрократию.

---

## D-007 — Parsing results as domain accordion
**Date:** 2025-12-16 00:29 MSK  
**Decision:** /moderator/requests/{requestId}/parsing-results returns results grouped by domain: each group contains domain and urls[] (accordion UI).  
**Why:** Moderator sees unique domains without noise, but can expand to view all URLs per domain.  
**Consequences:** Contract updated (ParsingDomainGroupDTO, ParsingResultsByKeyDTO.groups). Backend stores and returns grouped results.

## D-008 — Parsing execution mode (MVP sync, target async)
**Date:** 2025-12-16 00:29 MSK  
**Decision:** MVP keeps synchronous start-parsing (request waits for parser_service; timeout increased to allow manual captcha). Target design: start-parsing returns quickly with status=running/queued and parsing runs in background; UI polls parsing-status/results.  
**Why:** Avoid client/proxy timeouts and improve UX/reliability.  
**Consequences:** Later introduce background task runner (e.g., in-process task for MVP, then queue) without changing API semantics.

- 2025-12-16 18:04 MSK: Decision  Extend api-contracts.yaml for Moderator LK (no auth for now).

  - Add manual moderator parsing with history: clean key + depth (10..50) + source (google/yandex/both).
  - Add pending-decision domain queue with accordion URLs and key->url mapping.
  - Add domain decision state machine: supplier / reseller / blacklist / pending; allow moving between states later.
  - Add domain hit logging: key->url->domain even for decided/blacklisted domains.
  - Use hidden search prefix "buy " only at search time; never store/display it as part of the business key.

---

## D-009  Parsing results dedup by domain (accordion)
**Date:** 2025-12-17 23:13 MSK  
**Decision:** In parsing-results shown to the moderator, the list is de-duplicated by domain (one domain shown once), and the domain accordion contains all collected URLs for that domain.  
**Blacklist rule:** Blacklisted root-domains (and all subdomains) must not appear in parsing-results.  
**Logs:** Full raw findings are preserved in logs/hits (key->url->domain), including duplicates and occurrences for already decided/blacklisted domains.

---

## D-010  Captcha requires fullscreen browser window
**Date:** 2025-12-17 23:13 MSK  
**Decision:** If a captcha challenge appears during parsing, the browser window must be automatically maximized (fullscreen) so the moderator can see it immediately and solve it quickly.