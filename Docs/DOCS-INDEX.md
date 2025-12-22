# DOCS INDEX (SSoT-aware)

Note (process):
- Real-time documentation is mandatory: discussed + accepted = documented immediately.
- "Done" requires Doc-gate DoD: update the right root docs + add verification (HANDOFF/INCIDENTS) so the project is deployable from repo state.

This file explains what each top-level documentation file means and where it lives.

## SSoT priority
1) api-contracts.yaml  API contract SSoT (endpoints/DTOs/responses).
2) PROJECT-RULES.md  development process SSoT (safety guards, pre-flight, tooling).
3) PROJECT-DOC.md  product/architecture notes (NOT API SSoT).

## Files
- api-contracts.yaml  API contract SSoT (OpenAPI YAML).
- PROJECT-RULES.md  process rules, safety guards, pre-flight, tooling.
- PROJECT-DOC.md  product notes, MVP behavior notes, scenarios, and Decisions (ADR).
- DECISIONS.md  DEPRECATED / FROZEN (historical only). Use PROJECT-DOC.md#Decisions for new decisions.
- HANDOFF.md  success log (append-only) with verification commands.
- INCIDENTS.md  failure log (append-only) with root cause and mitigation.
- PROJECT-TREE.txt  current repo tree snapshot; update after meaningful changes.
- SPRINTS.md  sprint plan (dates, goals, checkboxes); keep it current.

## Where these files live
All files above must live in the repo root D:\b2bplatform (SSoT rule: no duplicates in backend\).

## Sandbox snapshot 2025-12-22

- Local sandbox root: D:\b2b
- GitHub repo: https://github.com/edwatikh-ship-it/b2b22.12.25
- Docs for this snapshot live in D:\b2b\Docs (same structure as root repo docs).

- SPRINTS.md
  - Sprint plan and status.
  - Living checklist of goals per sprint; update dates, goals, and checkboxes as work progresses.
- tmp\backend (local only, not in repo)
  - Storage for temporary .bak and tmp-* files from backend to keep source tree clean.
  - May be safely cleaned up; never treat it as SSoT.
