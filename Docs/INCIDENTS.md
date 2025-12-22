# INCIDENTS  B2B Platform

## Rules (owned here)
- Log problems/failures here (append-only).
- Format per entry:
  - datetime MSK
  - symptom
  - root cause
  - fix/mitigation
  - verification (command + expected output)
- Keep it short (13 lines per incident). Do not paste long stacktraces.

## Entries (append-only)

- 2025-12-20 07:33:01 MSK
  Context: docs / Windows line endings
  Symptom: git add warned: CRLF will be replaced by LF (DOCS-INDEX.md).
  Root cause: inconsistent line endings (CRLF vs LF) in working copy vs repo rules.
  Fix/Mitigation: Normalize line-ending policy via .gitattributes and run git add --renormalize . when line-ending noise appears again.
  Verification commands + expected output:
    - git status -sb  -> clean
    - git diff --name-only  -> empty
  Files touched: HANDOFF.md, INCIDENTS.md
- 2025-12-20 10:41:26 MSK INCIDENT: Tried to run 'new-tab' as a PowerShell command and got: The term 'new-tab' is not recognized. Root cause: new-tab is a wt.exe argument, not a PS command. Fix/Mitigation: use 'wt.exe new-tab ...' or run multiple Start-Process calls. Verification: where.exe wt; wt.exe --help -> exit 0; PowerShell: 'new-tab' still fails (expected).
- 2025-12-20 10:41:26 MSK INCIDENT: Windows Terminal command returned 0x80070002 when launching a new tab/session. Root cause: wt launch arguments/path/working dir mismatch (often happens when mixing relative paths, quoting, or missing exe on PATH). Fix/Mitigation: verify wt.exe path via where.exe wt, then call wt.exe with explicit -d D:\b2bplatform and explicit powershell.exe -File/-Command. Verification: where.exe wt -> shows a valid path; wt.exe --version prints a version; wt.exe -d D:\b2bplatform powershell.exe -NoProfile -NoExit -> opens a window.
- 2025-12-20 10:41:26 MSK INCIDENT: Ran 'Select-String -Recurse' and got 'A parameter cannot be found that matches parameter name Recurse'. Root cause: Select-String has no -Recurse; recursion is done by Get-ChildItem. Fix/Mitigation: Get-ChildItem -Recurse -File | Select-String -Pattern '<pattern>'. Verification: Get-ChildItem -Recurse -File | Select-String -Pattern 'PARSERSERVICEURL' returns matches (when present).

- 2025-12-20 10:44:44 MSK INCIDENT: Logged a bad verification command with empty pattern: Select-String -Pattern ''. Root cause: copy/paste / quoting error while writing INCIDENTS entry. Fix/Mitigation: always use a concrete pattern (e.g. 'PARSERSERVICEURL') and validate by running the command. Verification: Get-ChildItem -Recurse -File | Select-String -SimpleMatch -Pattern 'PARSERSERVICEURL' -> returns matches when present (or no output when absent).

- 2025-12-20 11:04:15 MSK CORRECTION: In 2025-12-20 10:41:26 MSK entry about Select-String recursion, the correct verification is: Get-ChildItem -Recurse -File | Select-String -SimpleMatch -Pattern 'PARSERSERVICEURL' (no empty pattern).

- 2025-12-20 11:11:32 MSK NOTE: Legacy mojibake/garbled section (old incidents) was intentionally removed from INCIDENTS.md by explicit owner approval to keep docs readable. Backup stored under D:\\b2bplatform.tmp.
2025-12-20 113642 MSK INCIDENT Root docs contain mojibake (garbled Cyrillic sequences like '...' and '[HEX_ESCAPE]..') in HANDOFF.md and api-contracts.yaml.
Root cause: Previous edit/save operation corrupted UTF-8 text (encoding mismatch / bad tool).
Fix/Mitigation: api-contracts.yaml mojibake was removed. HANDOFF.md and other append-only logs still contain historical mojibake sequences; do NOT attempt bulk rewrite without verified decoding (TBD).
Verification: Select-String -Path .\api-contracts.yaml -SimpleMatch -Pattern '','' -Quiet -> Expected: False. Select-String -Path .\HANDOFF.md -SimpleMatch -Pattern ' ' -Quiet -> Expected: may be True (historical mojibake remains in append-only log).
Files touched: HANDOFF.md, api-contracts.yaml
2025-12-20 114022 MSK INCIDENT Process failure: docs were assumed 'OK' without running a mojibake scan.
Symptom: Later scan found garbled sequences in HANDOFF.md and api-contracts.yaml.
Root cause: Missing mandatory preflight check (Select-String scan) before confirming doc state.
Fix/Mitigation: Add mandatory doc-scan step before any 'docs OK' statement; block progress until scan is clean.
Verification: Run the doc scan (see commands below) and require zero matches before confirming.
Files touched: INCIDENTS.md
