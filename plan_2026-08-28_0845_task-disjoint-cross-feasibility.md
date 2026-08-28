# Plan - Task-Disjoint Cross-Rollout Feasibility

**Status:** COMPLETED - FEASIBLE

**Date:** 2026-08-28

## Goal

Measure whether the frozen BridgeData intake can support a strict
source-train-task-disjoint cross-candidate rollout audit before any new model
comparison is attempted. The output must be feasibility evidence only: counts,
eligibility boundaries, and a no-run/no-promotion recommendation.

## Files To Read

- `AGENTS.md`, `README.md`, `STATUS.md`, and the Charter.
- `handoff_manus_2026-08-28_cross-rollout-uncertainty.md`.
- `CCF_Sovereign\evaluate_bridgedata_cross_candidate_rollout.py`.
- `CCF_Sovereign\evaluate_bridgedata_rollout_stability.py`.
- `CCF_Sovereign\src\real_data\bridgedata_evaluation.py`.
- `CCF_Sovereign\src\real_data\bridgedata_transitions.py`.
- `CCF_Sovereign\src\real_data\bridgedata_rollouts.py`.

## Files To Edit

- A new feasibility script under `CCF_Sovereign\`.
- Focused tests for task-overlap refusal and feasibility counting.
- `.gitignore` only if a new ignored local feasibility evidence directory is needed.
- This plan, a root handoff, and truth surfaces after measured results exist.

## Ordered Steps

- [x] Verify Manus's uncertainty update against commit state, handoff text, local evidence hash, and parsed JSON rows.
- [x] Create this plan before new code, test, or evaluation work.
- [x] Inspect frozen candidate manifests and BridgeData intake loading paths.
- [x] Implement a read-only feasibility scanner that measures, for each source candidate, whether target candidate-style protected episode sets can be selected with zero source-train task overlap and zero source-selected episode overlap.
- [x] Require deterministic counts for candidate-eligible episodes, rollout-case capacity at horizons 1, 2, and 5, and minimum distinct selected episode clusters.
- [x] Write ignored local JSON evidence only after adding an ignore rule.
- [x] Run focused compile and unittest gates.
- [x] Update `README.md`, `STATUS.md`, and a handoff with the measured feasibility result and explicit non-claims.
- [ ] Commit explicit paths and push `origin main` if gates pass.

## Measured Result

The frozen intake can support a strict source-train-task-disjoint cross audit.
For source candidate `001`, excluding all source-selected episodes and all
source-train task IDs leaves 23,124 target episode clusters, 14,480 task IDs, and
715,495 h5 rollout-case capacity. For source candidate `002`, the corresponding
pool has 23,973 clusters, 14,462 task IDs, and 732,461 h5 capacity. Both reports
have zero selected-episode overlap and zero source-train task overlap. This is
feasibility evidence only; no candidate predictions were evaluated.

## Test Gate

Run `python -m compileall -q` for touched Python source/tests, then focused
unittests covering BridgeData extraction/evaluation/rollout and the new
feasibility scanner. Run `git diff --check --cached` before commit.

## Rollback Path

Do not delete, overwrite, retune, promote, or mutate candidates. If feasibility
is false, preserve the negative result and stop before model comparison.

## Next-Agent Pickup Notes

This lane is not a new candidate run. It must not train, mutate checkpoints,
promote candidates, use Chronos2, invoke a renderer, issue robot actions, or
reopen frozen renderer recipe work. The decision needed first is whether the
bounded BridgeData shard can produce enough task-disjoint episode-contained
rollout cases at h1/h2/h5.
