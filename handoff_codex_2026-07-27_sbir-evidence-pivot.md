# Handoff: SBIR Evidence Pivot

**Date:** 2026-07-27
**Agent:** Codex
**Branch:** `main`
**Scope:** Source-audited strategic pivot from August 19 proposal race to
defense evidence package while company/admin readiness remains blocked.

## What Changed

- Created `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`.
- Updated `SBIR_plan.md` with Section 0A, making August 19 a conditional
  reopened gate rather than the sole success path.
- Updated `docs/sbir/README.md` with pivot and alternate-path source register
  entries.
- Updated `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` so immediate next
  work no longer points at the already-completed Technical Volume outline.
- Updated `STATUS.md` with the strategic consequence and remaining evidence
  gap.
- Created and maintained
  `plan_2026-07-27_1143_sbir-pivot-evidence-package.md`.

## Source Audit Summary

- Verified MDA OSBP and SBIR/STTR outreach surfaces, including OSBP outreach,
  MDA SBIR/STTR contacts, and capability-briefing contact path.
- Verified MDA prime/subcontracting and MDASBAC routes.
- Verified SBIR Phase III follow-on treatment for work derived from prior
  Phase I/II awards.
- Verified FAR 15.603 no-go language for unsolicited proposals that address
  previously published agency requirements.
- Verified DIU solution-brief/prototype/adoption framing, and corrected the
  pasted source label from "Defense Intelligence University" to Defense
  Innovation Unit.
- Verified DARPA MXO office-wide opportunity `DARPA-PS-26-115` deadline and
  relevant thrust areas from DARPA's MXO page.
- Verified the 2026 Space & Missile Defense Symposium date/location and
  technology-track relevance.
- Did not verify the pasted claim that the MDA SBIR/STTR Program Office will
  participate at the 2026 SMD Symposium. It is recorded as unverified.

## Commands Run

- `git status --short --branch`
- `git diff --stat`
- `git diff --name-status --diff-filter=D`
- `git ls-files --deleted`
- `Get-Content` for repo law, truth surfaces, latest plan/handoff, SBIR docs,
  Charter, Annex, and attached pasted text.
- Official-source checks via browser/search and `Invoke-WebRequest` against:
  MDA OSBP/SBIR pages, SBIR.gov policy/FAQ, SAM.gov entity registration,
  Acquisition.gov FAR 15.603, DIU, DARPA MXO, and SMD Symposium pages.
- `git diff -- docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md docs/sbir/README.md docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md SBIR_plan.md STATUS.md plan_2026-07-27_1143_sbir-pivot-evidence-package.md`
- `rg -n "SMD|SBIR/STTR Program Office|Defense Intelligence University|utm_source|94%|7 ms|Sorry, we already bought science|coffee thought" docs/sbir SBIR_plan.md STATUS.md`
- `rg -n "[^\x00-\x7F]" docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md docs/sbir/README.md docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md SBIR_plan.md STATUS.md plan_2026-07-27_1143_sbir-pivot-evidence-package.md`

## What Was Not Run

- No Python source tests; this was a docs/compliance strategy pass.
- No authenticated SAM, SBIR.gov, DSIP, Login.gov, or DD Form 2345 work.
- No legal/accounting review.
- No outreach was sent.
- No defense evidence package artifacts were generated beyond the planning
  backlog and non-confidential capability statement draft.

## Remaining Blockers

- Company/admin readiness is still blocked: legal for-profit applicant status,
  UEI, SAM, SBIR.gov Company Registry, SBC Control ID, Login.gov, DSIP, DD Form
  2345, CMMC/SPRS, cost-volume assumptions, ownership/control, and employee
  count are not verified.
- Technical evidence is still prototype-level. No measured shadow cycles,
  parent/candidate benchmark results, neuromorphic emulator, RF waveform demo,
  or hardware witness exists.
- Public Topic Q&A discrepancy remains from earlier DSIP audit.

## Dirty / Untracked State At Handoff Write

Expected docs-only tracked/untracked changes before staging:

- `SBIR_plan.md`
- `STATUS.md`
- `docs/sbir/README.md`
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- `plan_2026-07-27_1143_sbir-pivot-evidence-package.md`
- `handoff_codex_2026-07-27_sbir-evidence-pivot.md`

Ignored local artifacts remain intentionally unstaged.

## Next Step

Stage only the docs paths above, run `git diff --check --cached`, commit, push
`origin main`, and verify `HEAD == origin/main`. The next technical work should
create the non-confidential evidence package structure and define the first
shadow-cycle manifest plus parent/candidate benchmark skeleton.
