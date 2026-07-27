# Plan: Shadow Compare Gate - 2026-07-27 18:24

## Status
IN PROGRESS

## Goal
Add the parent/candidate comparison referee before any candidate generation.
The gate must compare two baseline result artifacts from the same frozen
manifest, reject mismatches, detect protected-task regressions, summarize
latency/error/pass deltas, and produce a promotion-safe verdict without relying
on raw private responses.

## Files Read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- [x] `plan_2026-07-27_1429_live-parent-baseline.md`
- [x] `handoff_codex_2026-07-27_live-parent-baseline.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `CCF_Sovereign\src\evaluation\shadow_baseline.py`
- [x] `CCF_Sovereign\test_shadow_baseline.py`
- [x] `CCF_Sovereign\src\evaluation\__init__.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\defense_evidence\benchmarks\shadow_001_parent_baseline_summary.md`
- [x] `docs\defense_evidence\failures\shadow_001_parent_baseline_failures.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`

## Files To Edit/Create

- [x] `CCF_Sovereign\src\evaluation\shadow_compare.py`
- [x] `CCF_Sovereign\src\evaluation\__init__.py`
- [x] `CCF_Sovereign\test_shadow_compare.py`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\defense_evidence\benchmarks\shadow_compare_gate_summary.md`
- [x] `docs\sbir\DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `STATUS.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [x] `handoff_codex_2026-07-27_shadow-compare-gate.md`
- [x] this plan

## Checklist

- [x] Recheck dirty tree and repo rules.
- [x] Read Charter, Annex, CCF truth surfaces, and current baseline evidence.
- [x] Add comparison dataclasses and JSON loader.
- [x] Reject manifest hash, cycle ID, or case-set mismatch.
- [x] Detect protected regressions, new errors, pass/fail delta, and latency
  delta.
- [x] Add tests using fixture JSON only.
- [x] Update evidence/SBIR/docs checkboxes without claiming candidate work.
- [x] Write fresh handoff.
- [x] Stage explicit paths.
- [x] Run Python compile/test gates.
- [x] Run `git diff --check --cached`.
- [ ] Commit and push to `origin main`.
- [ ] Verify `HEAD == origin/main`.

## Test Gate

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py CCF_Sovereign\test_live_parent_baseline.py CCF_Sovereign\test_shadow_compare.py
python test_shadow_manifest.py
python test_shadow_baseline.py
python test_live_parent_baseline.py
python test_shadow_compare.py
python test_mvp.py
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

No live checkpoint run, training run, candidate generation, or raw-response
publication is expected in this pass.

## Rollback
Do not delete local artifacts. If the comparison gate exposes incompatible
result schema assumptions, preserve the failure in this plan/handoff and stop
before committing broken source.

## Next-Agent Pickup
If interrupted, resume at the first unchecked item. The next real work after
this is candidate generation and a candidate baseline result that must pass this
gate against the frozen parent baseline.
