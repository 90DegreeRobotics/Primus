# Handoff: SBIR Claim/Evidence Matrix - 2026-07-27

## What Changed

- Added `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`.
- Updated `docs/sbir/README.md` so the SBIR source register points to the matrix
  and requires present-tense proposal claims to map to `VERIFIED` rows.
- Updated `SBIR_plan.md` checklist items for the completed matrix step and
  recorded CCF build/test result capture.
- Updated `STATUS.md` to list the claim/evidence matrix as a verified SBIR
  truth surface.
- Added `plan_2026-07-27_1048_sbir-claim-evidence-matrix.md`.

## Evidence Boundary

The matrix does not certify product readiness. It labels current CCF/Primus
evidence as source baseline, compile proof, weak smoke test, and local ignored
checkpoint inference. It explicitly rejects claims that the current stack
already demonstrates neuromorphic hardware, RF waveform adaptation, autonomous
continual learning, reliable sleep consolidation, sentience, or a learned
Council persona.

## Commands Run

```pwsh
git status --short --branch --ignored
git diff --stat
git ls-files --deleted
rg -n "Primus|SBIR|claim|evidence|CCF|MDA" C:\Users\m\.codex\memories\MEMORY.md
Get-Content -Raw -LiteralPath AGENTS.md
Get-Content -Raw -LiteralPath README.md
Get-Content -Raw -LiteralPath STATUS.md
Get-Content -Raw -LiteralPath SBIR_plan.md
Get-Content -Raw -LiteralPath docs\sbir\README.md
Get-Content -Raw -LiteralPath docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md
Get-Content -Raw -LiteralPath C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md
Get-Content -Raw -LiteralPath C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md
git diff --check --cached
```

`git diff --check --cached` passed before commit.

## Not Run

- No Python tests were run; this was docs-only.
- No DSIP package was downloaded.
- No administrative readiness evidence was checked.
- No training, shadow cycle, benchmark, RF, or hardware test was run.

## Remaining Blockers

- DSIP official 26.BZ BAA/CSO and MDA component instructions are still not
  archived in repo.
- UEI, SAM, SBIR.gov Company Registry, SBC Control ID, DSIP access,
  ownership/control, employee count, exact cutoff time, page limits, funding
  ceiling, period of performance, cybersecurity, and export language remain
  unverified.
- RF/waveform and neuromorphic hardware partners are not identified.
- CCF tests remain weak and must be hardened before product-readiness language.

## Next Step

Pull the official DSIP topic package and create a compliance register from the
actual BAA/CSO and MDA component instructions, or harden `test_mvp.py` into a
real failing test suite if DSIP access is not available.
