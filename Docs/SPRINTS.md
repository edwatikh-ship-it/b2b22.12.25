# Sprints

Rule: this is a living plan. Update checkboxes during work, and move items between sprints as reality changes.

## Sprint 1 (YYYY-MM-DD .. YYYY-MM-DD)
Goals:
- [ ] Define scope for Sprint 1 (fill dates and goals).
- [ ] Pick next API slice from api-contracts.yaml.
- [ ] Implement + tests + update HANDOFF.md.
- [ ] Update PROJECT-TREE.txt.

## Sprint 2 (YYYY-MM-DD .. YYYY-MM-DD)
Goals:
- [ ] TBD

## Sprint 3 (YYYY-MM-DD .. YYYY-MM-DD)
Goals:
- [ ] TBD
## 2025-12-17  Parsing: source/depth wiring (contract  backend)

Goal:
- Make moderator start-parsing accept {depth, source} per SSoT and wire it through backend  parser_service.

Done:
- [x] api-contracts.yaml: add requestBody StartParsingRequestDTO to POST /moderator/requests/{requestId}/start-parsing.
- [x] api-contracts.yaml: add ParsingRunSource enum (google|yandex|both).
- [x] backend: StartParsingRequestDTO updated to match SSoT (depth nullable, source nullable; removed resume).
- [x] backend: start_parsing accepts body payload; defaults depth=10, source=both; forwards to parser_service /parse.

Bugs/notes:
- [x] ruff F821: ParsingRunSource referenced before declaration  fixed via from __future__ import annotations in backend/app/transport/schemas/moderator_parsing.py.

Next:
- [ ] parser_service: accept source in /parse and implement google/yandex/both behavior (currently yandex-only).
- [ ] backend: optionally propagate per-URL/per-group source into ParsingDomainGroupDTO.source (requires parser_service to return source metadata).


## Next (handoff)  2025-12-18
- Status: SSoT api-contracts.yaml paths == runtime OpenAPI paths (1:1).
- Runtime: backend up on http://127.0.0.1:8000, APIPREFIX empty.
- Verify:
  - Invoke-RestMethod http://127.0.0.1:8000/health
  - Invoke-RestMethod http://127.0.0.1:8000/openapi.json | Out-Null
  - (Invoke-RestMethod http://127.0.0.1:8000/openapi.json).paths.PSObject.Properties.Name | Sort-Object
- Sprint tasks (pick top priority first):
  - [ ] Choose next endpoint slice from api-contracts.yaml and implement minimal behavior (+ tests).
  - [ ] Parserservice: support StartParsingRequestDTO.source (google/yandex/both); currently yandex-only.
  - [ ] Consider propagating source metadata into ParsingDomainGroupDTO.source (needs parserservice output).
