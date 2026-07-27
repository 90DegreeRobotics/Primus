# Handoff: DSIP Compliance Register

**Date:** 2026-07-27
**Agent:** Codex
**Branch:** `main`
**Scope:** SBIR compliance/source audit for `MDA26BZ04-NV006`

## What Changed

- Created `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`.
- Updated `docs/sbir/README.md` so DSIP/MDA official package sources now control
  the SBIR source register.
- Updated `SBIR_plan.md` to check only the official-package facts actually
  verified in this pass.
- Updated `STATUS.md` to remove stale blockers for cutoff time, page limit,
  funding ceiling, period of performance, CMMC, and ITAR/EAR.
- Updated `plan_2026-07-27_1058_dsip-compliance-register.md` through the
  completed documentation steps.

## Official Sources Checked

- SBIR.gov topic page:
  `https://www.sbir.gov/topics/12804`
- Defense SBIR/STTR Opportunities:
  `https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/`
- DSIP topic search endpoint:
  `https://www.dodsbirsttr.mil/topics/api/public/topics/search`
- DSIP topic detail endpoint:
  `https://www.dodsbirsttr.mil/topics/api/public/topics/bc100089f0ce48e18faee7f93caeff25_86561/details`
- DSIP public Topic Q&A endpoint:
  `https://www.dodsbirsttr.mil/topics/api/public/topics/bc100089f0ce48e18faee7f93caeff25_86561/questions`
- DSIP Release 4 BAA preface PDF endpoint:
  `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&release=4&documentType=RELEASE_PREFACE`
- DSIP MDA Release 4 instructions PDF endpoint:
  `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&documentType=INSTRUCTIONS&component=MDA&release=4`

## Evidence Summary

- DSIP public topic search returned exactly one hit:
  - `MDA26BZ04-NV006`
  - `Neuromorphic Hardware`
  - `MDA`
  - `DoW SBIR 2026 BAA`
  - status `Open`
  - topic ID `bc100089f0ce48e18faee7f93caeff25_86561`
- DSIP public topic detail returned official topic JSON, including CMMC Level 1,
  `itar=true`, Phase I/II/III text, technology areas, focus areas, and
  references.
- DSIP public Q&A endpoint returned `[]`; recheck before submission because the
  topic metadata reported a nonzero topic question count.
- Downloaded official PDFs to temp only:
  - `C:\Users\m\AppData\Local\Temp\primus_dsip_pdf_audit\DoW_2026_SBIR_BAA_Preface_07152026.pdf`
  - `C:\Users\m\AppData\Local\Temp\primus_dsip_pdf_audit\MDA_SBIR_26BZ_R4_v2.pdf`
- Verified PDF signatures and extracted text with bundled Python / `pypdf`.
- PDF fingerprints:
  - `DoW_2026_SBIR_BAA_Preface_07152026.pdf`: 50 pages, 683,868 bytes,
    SHA-256 `A3E3ACB63AAD8A6DB04251E991D2F9E428340088FD0FD11DDD8AB0097BF80A75`
  - `MDA_SBIR_26BZ_R4_v2.pdf`: 26 pages, 324,066 bytes,
    SHA-256 `5752089DFD463BC9F17C99C1E581C1947F576F1AF10181BEC1492A1F26289335`

## Confirmed Package Facts

- Proposal cutoff: 2026-08-19 at 12:00 p.m. ET.
- Topic Q&A cutoff for new questions: 2026-08-12 at 12:00 p.m. ET.
- MDA Technical Volume limit: 15 pages.
- Phase I period: anticipated six months.
- Phase I cap: `$307,500` base, or `$314,000` if TABA is included.
- MDA does not use a Phase I Option.
- CMMC: Level 1.
- Export control: ITAR/EAR restricted.
- Required MDA export-control support: certified DD Form 2345 or evidence of
  application in Volume 5 under `Other`.
- Classified proposals are not accepted for MDA SBIR Phase I.

## Commands Run

- `git status --short --branch --ignored`
- `Get-Content AGENTS.md`
- `Get-Content plan_2026-07-27_1058_dsip-compliance-register.md`
- `Invoke-WebRequest` checks against DSIP app shells, topic APIs, Q&A API, and
  solicitation-document download endpoints.
- Bundled Python with `pypdf` for official PDF text extraction.
- `Get-FileHash -Algorithm SHA256` for both downloaded PDFs.
- `rg` consistency scans for stale "pending DSIP" and secondary-source language.
- `git diff --stat`
- `git diff -- SBIR_plan.md STATUS.md docs/sbir/README.md docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md plan_2026-07-27_1058_dsip-compliance-register.md`

## What Was Not Run

- No Python source tests; this was a docs/compliance-only pass.
- No DSIP authenticated account workflow.
- No actual proposal submission.
- No SAM, SBIR.gov Company Registry, Login.gov, SBC Control ID, DD Form 2345,
  CMMC/SPRS, ownership/control, or employee-count verification.
- No partner, letter-of-support, subcontractor, TABA decision, or cost-volume
  completion.

## Dirty / Untracked State At Handoff Write

Expected docs-only tracked changes before staging:

- `SBIR_plan.md`
- `STATUS.md`
- `docs/sbir/README.md`
- `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`
- `plan_2026-07-27_1058_dsip-compliance-register.md`
- `handoff_codex_2026-07-27_dsip-compliance-register.md`

Ignored local artifacts remained present and intentionally unstaged, including
virtual environments, caches, training data, local checkpoint files, generated
maps, and local conversation/archive material.

## Next Step

Stage only the docs paths above, run `git diff --check --cached`, commit, push
`origin main`, and verify `HEAD == origin/main`. After that, the next SBIR work
unit should move to operator/company readiness or a proposal-draft compliance
outline using the register as the gate.
