# Plan: Shadow Baseline Runner - 2026-07-27 13:49

## Status
COMPLETE

## Goal
Add the first no-training shadow baseline runner for CCF evidence work. The
runner must consume a validated shadow manifest, execute a parent-response
callable without training or promotion, preserve raw benchmark results, and keep
all claims scoped to component/evidence-pipeline proof.

## Files Read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `plan_2026-07-27_1202_ccf-hardening-shadow-evidence.md`
- [x] `handoff_codex_2026-07-27_ccf-hardening-shadow-evidence.md`
- [x] `CCF_Sovereign\src\evaluation\shadow_manifest.py`
- [x] `CCF_Sovereign\test_shadow_manifest.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`

## Files To Edit/Create

- [x] `CCF_Sovereign\src\evaluation\shadow_baseline.py`
- [x] `CCF_Sovereign\src\evaluation\__init__.py`
- [x] `CCF_Sovereign\test_shadow_baseline.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `STATUS.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [ ] `handoff_codex_2026-07-27_shadow-baseline-runner.md`
- [ ] this plan

## Checklist

- [x] Recheck dirty tree and repo rules.
- [x] Read Charter, Annex, and CCF truth surfaces.
- [x] Add a no-training baseline result writer bound to manifest hash.
- [x] Add tests proving pass/fail scoring, responder-error capture, artifact
  write, and no mutation/promotion semantics.
- [x] Update defense evidence and SBIR checkboxes only for earned work.
- [x] Write a fresh handoff.
- [x] Stage explicit paths.
- [x] Run Python compile/test gates.
- [x] Run `git diff --check --cached`.
- [x] Commit and push to `origin main`.
- [x] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py
python test_shadow_manifest.py
python test_shadow_baseline.py
python test_mvp.py
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

`test_inference.py` is not expected to run unless touched. This pass does not
claim checkpoint quality, learned persona quality, autonomous continual
learning, neuromorphic hardware behavior, or RF adaptation.

## Rollback
Do not delete. If the runner exposes incompatible manifest assumptions or test
failures, preserve the failure in this plan/handoff and stop before committing
broken code.

## Next-Agent Pickup
If interrupted, resume at the first unchecked item. The next real technical
step after this runner is a live no-training parent baseline using a real local
artifact and an outreach-safe benchmark set.
