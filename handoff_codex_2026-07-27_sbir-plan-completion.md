# Handoff: Codex - 2026-07-27 - SBIR plan completion

## What Changed

- Audited the builder's `SBIR_plan.md`.
- Converted it from pasted Python/chat residue into direct Markdown.
- Added source-confidence boundaries and proposal assembly content.
- Added `docs/sbir/README.md` as the SBIR source/compliance register.
- Updated `STATUS.md` to reflect the audited SBIR artifact and remaining DSIP/admin blockers.
- Updated `plan_2026-07-27_1002_complete-sbir-plan.md` with completed checkboxes.

## Builder Audit Findings

- `SBIR_plan.md` began as untracked builder output.
- It contained a Python wrapper, stale local artifact write path, broken sandbox download link, chat-response prose, and tracking-parameter URLs.
- It treated secondary-source details as useful but did not preserve enough DSIP-control discipline.
- The corrected plan now keeps hard boundaries:
  - official SBIR.gov verifies topic existence, status, dates, and summary need;
  - Defense SBIR/STTR/DSIP controls final proposal instructions;
  - `$314,000` Phase I amount remains secondary pending DSIP confirmation;
  - Primus/CCF/Chronos are not claimed as completed neuromorphic hardware.

## Commands Run

- `git status --short --branch`
  - Started and ended on `main...origin/main`; unrelated local surfaces remain untracked.
- `git diff --stat`
  - No tracked diff before edits.
- `git ls-files --deleted`
  - No deleted tracked files.
- `Select-String -Path SBIR_plan.md -Pattern ...`
  - Confirmed builder residue before cleanup and no stale artifact strings after cleanup.
- `git diff --check --cached`
  - Initially caught trailing whitespace in `SBIR_plan.md`; fixed and reran clean.
- `git commit -m "docs(sbir): complete neuromorphic hardware pursuit plan"`
  - Created `05a55365b41bcd6b109ea3c899cfe326415ae204`.
- `git push origin main`
  - Pushed through `05a5536`.
- `git rev-parse HEAD` and `git rev-parse origin/main`
  - Both returned `05a55365b41bcd6b109ea3c899cfe326415ae204` after the SBIR-plan commit.

## Web Sources Checked

- `https://www.sbir.gov/topics/12804`
- `https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/`
- `https://www.sbir.gov/faq/all`
- `https://www.bwcoconsulting.com/fod/mda26bz04-nv006`

## What Was Not Run Or Confirmed

- DSIP login/download was not performed.
- Official 26.BZ BAA/CSO and MDA component-specific instruction PDFs were not downloaded.
- Exact funding ceiling, cutoff time, period of performance, page limits, forms, CMMC/cybersecurity text, and ITAR/EAR language remain unconfirmed in DSIP.
- UEI, SAM, SBIR Company Registry, SBC Control ID, DSIP account, ownership/control, and employee count remain operator/admin confirmations.
- No `CCF_Sovereign` runtime, training, checkpoint, or integration claims were certified in this pass.

## Dirty Or Untracked Boundary

Still untracked by design:

- `CCF_Sovereign/`
- `Fascia and Mycelia Network Comparison.md`
- `Organic Wetware AI Architecture.md`
- `Sovereign Textual Mind Paradigm.md`
- `council_ideas.md`

These were not staged or imported.

## Next Step

Operator/admin path: log into DSIP, download the official package, and update
`docs/sbir/README.md` plus `SBIR_plan.md` with exact component instructions.

Technical path: run the separate Primus/CCF/Chronos source audit before any
proposal text claims actual build/test/training evidence.
