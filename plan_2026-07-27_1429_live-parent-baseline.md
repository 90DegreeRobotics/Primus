# Plan: Live Parent Baseline - 2026-07-27 14:29

## Status
COMPLETE

## Goal
Build and run the first live no-training parent baseline against a real local
CCF parent artifact, while keeping raw checkpoint-derived outputs local/ignored
unless explicitly reviewed for outreach safety.

## Files Read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `plan_2026-07-27_1349_shadow-baseline-runner.md`
- [x] `handoff_codex_2026-07-27_shadow-baseline-runner.md`
- [x] `CCF_Sovereign\test_inference.py`
- [x] `CCF_Sovereign\src\evaluation\shadow_manifest.py`
- [x] `CCF_Sovereign\src\evaluation\shadow_baseline.py`
- [x] `CCF_Sovereign\src\substrate\model.py`
- [x] `CCF_Sovereign\src\substrate\tokenizer.py`
- [x] `CCF_Sovereign\src\core\config.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`

## Files To Edit/Create

- [x] `.gitignore`
- [x] `CCF_Sovereign\src\evaluation\live_parent_baseline.py`
- [x] `CCF_Sovereign\src\evaluation\__init__.py`
- [x] `CCF_Sovereign\src\substrate\tokenizer.py`
- [x] `CCF_Sovereign\test_live_parent_baseline.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\defense_evidence\benchmarks\shadow_001_parent_baseline_summary.md`
- [x] `docs\defense_evidence\failures\shadow_001_parent_baseline_failures.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `STATUS.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [x] `handoff_codex_2026-07-27_live-parent-baseline.md`
- [ ] this plan

Local ignored outputs expected from the live run:

- [x] `docs\defense_evidence\local_runs\shadow-001-parent-baseline\manifest.json`
- [x] `docs\defense_evidence\local_runs\shadow-001-parent-baseline\parent_baseline.json`
- [x] `docs\defense_evidence\local_runs\shadow-001-parent-baseline\run_metadata.json`

## Checklist

- [x] Recheck dirty tree and repo rules.
- [x] Read Charter, Annex, CCF truth surfaces, and current inference/evidence
  code.
- [x] Inspect the local checkpoint path, size, and hash without staging it.
- [x] Add deterministic live parent baseline builder/runner.
- [x] Add tests for manifest construction, checkpoint metadata handling, and
  no-training local output path behavior without requiring the real checkpoint.
- [x] Add ignore policy for local raw evidence outputs if not already covered.
- [x] Run the live parent baseline against the ignored local checkpoint.
- [x] Update docs with exact live result summary and keep raw outputs local.
- [x] Write a fresh handoff.
- [x] Stage explicit paths.
- [x] Run Python compile/test gates.
- [x] Run `git diff --check --cached`.
- [x] Commit and push to `origin main`.
- [x] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py CCF_Sovereign\test_live_parent_baseline.py
python test_shadow_manifest.py
python test_shadow_baseline.py
python test_live_parent_baseline.py
python test_mvp.py
python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

`test_inference.py` is not the gate for this pass because it is print-only and
stochastic. The live baseline command must record manifest-bound JSON evidence.

## Rollback
Do not delete local artifacts. If live checkpoint load or generation fails,
preserve the failure summary in this plan/handoff, leave the live baseline box
unchecked, and commit only the safe code/docs that truthfully describe the
blocker.

## Next-Agent Pickup
If interrupted, resume at the first unchecked item. Do not claim persona quality
or autonomous learning from this baseline. It is parent-only, no-training
evidence.
