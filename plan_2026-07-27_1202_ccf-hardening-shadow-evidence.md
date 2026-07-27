# Plan: CCF hardening and shadow evidence skeleton - 2026-07-27 12:02

## Status
IN PROGRESS

## Goal
Keep building the defense-relevant technical path by hardening the CCF smoke
test into fail-hard checks, fixing any directly exposed false-surface behavior,
and creating the first shadow-cycle evidence skeleton for future measured runs.

## Files Read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `plan_2026-07-27_1143_sbir-pivot-evidence-package.md`
- [x] `handoff_codex_2026-07-27_sbir-evidence-pivot.md`
- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `CCF_Sovereign\test_mvp.py`
- [x] `CCF_Sovereign\test_inference.py`
- [x] `CCF_Sovereign\src\core\config.py`
- [x] `CCF_Sovereign\src\substrate\model.py`
- [x] `CCF_Sovereign\src\substrate\tokenizer.py`
- [x] `CCF_Sovereign\src\substrate\mamba_custom.py`
- [x] `CCF_Sovereign\src\memory\steb.py`
- [x] `CCF_Sovereign\src\memory\holographic.py`
- [x] `CCF_Sovereign\src\lifecycles\circadian_controller.py`
- [x] `CCF_Sovereign\src\plasticity\hebbian.py`
- [x] `CCF_Sovereign\src\main.py`
- [x] `CCF_Sovereign\train.py`
- [x] `CCF_Sovereign\training\execution_trace_logger.py`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `SBIR_plan.md`

## Files To Edit/Create

- [x] `CCF_Sovereign\test_mvp.py`
- [x] `CCF_Sovereign\src\lifecycles\circadian_controller.py`
- [x] `CCF_Sovereign\src\evaluation\__init__.py`
- [x] `CCF_Sovereign\src\evaluation\shadow_manifest.py`
- [x] `CCF_Sovereign\test_shadow_manifest.py`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `STATUS.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [x] this plan
- [x] final handoff

## Checklist

- [x] Capture baseline result for the existing weak `test_mvp.py`.
- [x] Replace print-only/skipped success behavior in `test_mvp.py` with
  assertion-backed fail-hard tests.
- [x] Fix the circadian `galore_torch` missing-path so the Adam fallback is real
  or the message is removed.
- [x] Add a shadow-cycle manifest module with deterministic JSON/hashing and
  train/eval leakage checks.
- [x] Add tests for the shadow manifest module.
- [x] Create a non-confidential defense evidence package folder and README.
- [x] Update SBIR/evidence/status truth surfaces and check only earned boxes.
- [x] Write root handoff for this hardening unit.
- [x] Stage explicit paths.
- [x] Run Python compile/test gates.
- [x] Run `git diff --check --cached`.
- [ ] Commit and push to `origin main`.
- [ ] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py
python test_mvp.py
python test_shadow_manifest.py
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

`test_inference.py` is not expected to run in this pass unless touched; it
depends on the ignored local checkpoint and tests checkpoint loading/generation,
not the hardening surfaces above.

## Rollback
Do not delete. If the new tests expose a deeper runtime defect, preserve the
failing output in this plan/handoff, keep the no-go status, and either fix the
defect directly or stop before committing broken source.

## Next-Agent Pickup
If interrupted, resume at the first unchecked box. Do not report CCF as
product-live or autonomous-learning verified unless the new tests and future
shadow-cycle artifacts prove it.
