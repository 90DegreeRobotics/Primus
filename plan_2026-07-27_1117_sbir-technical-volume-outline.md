# Plan: SBIR technical volume outline - 2026-07-27 11:17

## Status
IN-PROGRESS

## Goal
Create a compliance-bound proposal outline for the `MDA26BZ04-NV006` Phase I
Technical Volume and reconcile the SBIR claim/evidence matrix with the official
DSIP/MDA package facts confirmed in
`docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`.

## Files Read

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `handoff_codex_2026-07-27_dsip-compliance-register.md`
- `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`
- `SBIR_plan.md`
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- `C:\Users\m\.codex\plugins\cache\openai-primary-runtime\pdf\26.723.12215\skills\pdf\SKILL.md`
- `C:\Users\m\AppData\Local\Temp\primus_dsip_pdf_audit\DoW_2026_SBIR_BAA_Preface_07152026.pdf`

## Files To Edit/Create

- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md`
- `docs/sbir/README.md`
- `SBIR_plan.md`
- `STATUS.md`
- this plan
- final handoff

## Checklist

- [x] Reconcile opportunity/compliance rows in the claim matrix against the
  official DSIP/MDA compliance register.
- [x] Create a 15-page Technical Volume outline that maps sections to verified
  facts, evidence limits, and required Phase I deliverables.
- [x] Add explicit no-go language and claim-state tags to the outline.
- [x] Update SBIR source register/status surfaces.
- [x] Update SBIR plan checkboxes only where the outline/matrix work earns it.
- [x] Write root handoff for this outline unit.
- [x] Stage explicit docs-only paths.
- [x] Run `git diff --check --cached`.
- [ ] Commit and push to `origin main`.
- [ ] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

No Python source is expected to change in this pass.

## Rollback
Do not delete. If later DSIP or operator information changes the outline, add a
follow-up amendment that preserves this compliance-bound draft history.

## Next-Agent Pickup
If interrupted, resume at the first unchecked box. Do not draft proposal claims
outside the claim matrix or the official compliance register.
