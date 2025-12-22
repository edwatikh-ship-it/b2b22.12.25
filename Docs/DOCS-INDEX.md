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
