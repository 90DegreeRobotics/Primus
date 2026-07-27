# Handoff: SBIR Technical Volume Outline

**Date:** 2026-07-27
**Agent:** Codex
**Branch:** `main`
**Scope:** Claim-matrix reconciliation and compliant Volume 2 outline for
`MDA26BZ04-NV006`

## What Changed

- Updated `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` so DSIP/MDA package
  facts are no longer mislabeled as weak, secondary, pending, or blocked.
- Created `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md`.
- Updated `docs/sbir/README.md`, `SBIR_plan.md`, and `STATUS.md` to point to
  the outline and corrected claim matrix.
- Created and maintained
  `plan_2026-07-27_1117_sbir-technical-volume-outline.md`.

## Evidence Summary

- Official BAA Appendix A confirms the Technical Volume should use this section
  order:
  1. Identification and Significance of the Problem or Opportunity.
  2. Phase I Technical Objectives.
  3. Phase I Statement of Work.
  4. Related Work.
  5. Relationship with Future Research or R&D.
  6. Commercialization Strategy.
  7. Key Personnel.
  8. Foreign Citizens.
  9. Facilities/Equipment.
  10. Subcontractors/Consultants.
  11. Prior, Current, or Pending Support.
  12. Data/software restriction assertions.
- The outline uses the official 12-section order and a 15-page page budget.
- The Statement of Work is assigned the largest page budget because the BAA
  template says it should be a substantial portion of Volume 2.
- The outline keeps business/team/company facts blocked instead of inventing
  them.

## Commands Run

- `git status --short --branch --ignored`
- `git diff --stat`
- `git ls-files --deleted`
- `Get-Content` for repo law, truth surfaces, latest handoff, SBIR plan,
  compliance register, claim matrix, Charter, Annex, and PDF skill instructions.
- Bundled Python with `pypdf` against
  `C:\Users\m\AppData\Local\Temp\primus_dsip_pdf_audit\DoW_2026_SBIR_BAA_Preface_07152026.pdf`
  to extract official Volume 2 template sections.
- `rg` stale-language scan for old DSIP blockers; result: no stale blocker
  hits.
- `rg` no-go-language scan; hits were limited to explicit no-go/warning
  sections.
- `git diff -- docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md docs/sbir/README.md SBIR_plan.md STATUS.md plan_2026-07-27_1117_sbir-technical-volume-outline.md`

## What Was Not Run

- No Python source tests; this was a docs/compliance-only pass.
- No authenticated DSIP workflow.
- No final proposal render/export.
- No company readiness verification: UEI, SAM, SBIR.gov Company Registry, SBC
  Control ID, Login.gov/DSIP access, DD Form 2345, CMMC/SPRS, ownership/control,
  employee count, TABA, corporate official, and support letters remain blocked.
- No partner verification for RF waveform, neuromorphic hardware,
  survivability, compliance, or cost review.

## Remaining Blockers

- Public Topic Q&A discrepancy remains: previous public endpoint returned `[]`
  while topic metadata reported a nonzero question count. Recheck before final
  submission.
- Sections 6 through 12 of the outline contain business/team placeholders that
  require operator/company facts.
- Current technical evidence remains prototype-level. No hardware, RF waveform,
  or product-readiness claim is allowed.

## Dirty / Untracked State At Handoff Write

Expected docs-only tracked changes before staging:

- `SBIR_plan.md`
- `STATUS.md`
- `docs/sbir/README.md`
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md`
- `plan_2026-07-27_1117_sbir-technical-volume-outline.md`
- `handoff_codex_2026-07-27_sbir-technical-volume-outline.md`

Ignored local artifacts remain intentionally unstaged.

## Next Step

Stage only the docs paths above, run `git diff --check --cached`, commit, push
`origin main`, and verify `HEAD == origin/main`. The next SBIR work unit should
move either to operator/company readiness or to a first fill of the Technical
Volume Section 3 Statement of Work using only the outline and claim matrix.
