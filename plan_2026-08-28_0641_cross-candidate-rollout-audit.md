# Plan — Cross-Candidate BridgeData Rollout Robustness Audit

**Status:** ACTIVE - LINEAR BASELINE AMENDMENT IN PROGRESS

**Date:** 2026-08-28 06:41 CDT

## Goal

Evaluate, without training or mutation, whether each frozen rejected BridgeData transition predictor retains its short-horizon open-loop advantage when scored on the other candidate's independently selected protected episode sets. The result must be reported as robustness evidence only, with explicit task-overlap limitations.

## Files To Read

- `AGENTS.md`, `README.md`, `STATUS.md`, and the Charter of Cognitive Sovereignty.
- `handoff_manus_2026-08-28_bridgedata-rollout-stability.md`.
- `plan_2026-08-27_1640_bridgedata-rollout-stability.md`.
- `CCF_Sovereign\evaluate_bridgedata_rollout_stability.py`.
- `CCF_Sovereign\src\real_data\bridgedata_rollouts.py`.
- Existing BridgeData transition, evaluation, candidate, and rollout tests.

## Files To Edit

- New read-only cross-candidate evaluator under `CCF_Sovereign\`.
- Focused tests for cross-candidate eligibility, no episode overlap, task-overlap reporting, and no-promotion evidence.
- `.gitignore` only if a new local evidence directory is needed.
- This plan, final handoff, and truth surfaces after measured results exist.

## Ordered Steps

- [x] Verify Manus's rollout-stability update against git, handoff text, local evidence hash, JSON metrics, focused tests, and process state.
- [x] Create this plan before source edits.
- [x] Add the missing train-only ordinary least-squares state/action delta baseline to one-step and rollout evaluation paths before treating the cross audit as conclusive.
- [x] Implement a cross-candidate evaluator that loads only the two predeclared terminal rejected candidates, reuses the frozen-candidate verifier, and never writes checkpoints, candidates, source data, parent files, or promotion state.
- [x] For each ordered pair `001 -> 002` and `002 -> 001`, score the source candidate's frozen model on the target candidate's held-out-episode and held-out-task rollout cases. Baselines must be fitted only from the source candidate's train partition.
- [x] Reject evaluation if any source-train episode overlaps the target protected episodes. Report task-index overlap per protected target split instead of calling cross-target held-out-task semantics strict when source training contains those tasks.
- [x] Apply the predeclared robustness rule: exact finite coverage and strictly lower terminal RMSE than the strongest source-train baseline at horizons 1, 2, and 5 for both target protected partitions. Horizon 10 remains descriptive only. Failure is evidence, not grounds for retuning.
- [x] Write ignored local JSON evidence under `CCF_Sovereign\evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-001\` after adding the ignore rule.
- [x] Rerun rollout and cross-candidate evidence with the linear baseline under fresh ignored directories.
- [x] Run compile and focused unittest gates, then update `README.md`, `STATUS.md`, and a root handoff with only measured results and explicit non-claims.
- [ ] Commit explicit paths and push `origin main` if gates pass.

## Measured Result

The linear baseline became the strongest comparator in every own-split protected
rollout acceptance row. Both candidates still passed h1/h2/h5 on their own
protected rollout partitions, but margins narrowed. Candidate `001` strict-task
h5 is now `0.2579618763146602` versus linear baseline `0.2638808140470817`.
Candidate `002` strict-task h5 is `0.07452113239630093` versus linear baseline
`0.08877005240438241`.

Cross-candidate robustness is mixed, not symmetric. Candidate `001` on candidate
`002` passed both target protected partitions at h1/h2/h5. Candidate `002` on
candidate `001` passed target held-out episodes but failed target held-out-task
h5 by `0.0006815841557626` RMSE. All cross-target splits had zero selected/train
episode overlap and exact finite 256-case coverage, but all had source-train
task overlap, so this is not strict unseen-task evidence relative to the source
model.

## Test Gate

Run `python -m compileall -q` for touched Python source and tests, then run focused unittest modules covering BridgeData extraction/evaluation/candidate/rollout/cross-rollout behavior. Run `git diff --check --cached` before commits.

## Rollback Path

Do not delete, reset, overwrite, or amend anything. If eligibility or evaluation fails, preserve the failure in a new ignored local evidence directory or handoff, leave candidates untouched, and report the limitation.

## Next-Agent Pickup Notes

The only valid source candidates are `bridge-real-20260827-001` and `bridge-real-20260827-002`. Both are terminally rejected, no-promotion candidates. The prior rollout evidence is local and ignored at `CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260827-001\rollout_stability.json` with SHA-256 `9cbd9458cac0926d572fb0130c06ca863996c9403d9f03ad6b7bdba8afce0920`. Do not resume renderer, Chronos integration, robot control, actuation, or training from this plan.
