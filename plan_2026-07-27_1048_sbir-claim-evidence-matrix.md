# Plan: SBIR claim/evidence matrix - 2026-07-27 10:48

## Status
COMPLETE

## Goal
Create the SBIR claim/evidence matrix required by `SBIR_plan.md`, using current
repo truth to classify every proposal-facing technical claim as verified,
experimental hypothesis, future work, or blocked. The matrix must prevent
current CCF/Primus prototype evidence from being inflated into neuromorphic
hardware, RF waveform, product-readiness, sentience, or learned-persona claims.

## Files Read

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `SBIR_plan.md`
- `docs/sbir/README.md`
- `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`
- `handoff_codex_2026-07-27_ccf-source-import-audit.md`
- `plan_2026-07-27_1011_source-import-audit.md`
- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`

## Files To Edit/Create

- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `docs/sbir/README.md`
- `SBIR_plan.md`
- this plan
- final handoff

## Checklist

- [x] Draft matrix schema and classification vocabulary.
- [x] Populate proposal claims from `SBIR_plan.md`.
- [x] Attach current repo evidence and missing evidence to each claim.
- [x] Mark unsupported/no-go claims plainly.
- [x] Add proposal language rules and acceptance gates.
- [x] Update `docs/sbir/README.md` source register.
- [x] Update `SBIR_plan.md` checkboxes for the completed matrix step.
- [x] Write root handoff for this matrix unit.
- [x] Stage explicit docs-only paths.
- [x] Run `git diff --check --cached`.
- [x] Commit and push to `origin main`.
- [x] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

No Python source is expected to change in this pass.

## Rollback
Do not delete. If matrix language is wrong, correct it in a follow-up commit
that preserves the audit history.

## Next-Agent Pickup
If interrupted, resume at the first unchecked box. Do not broaden this into DSIP
download/admin work unless the operator explicitly provides access or asks for
that lane.
