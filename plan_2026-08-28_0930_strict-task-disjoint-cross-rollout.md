# Plan — Strict Task-Disjoint Cross-Candidate Rollout Evaluation

**Status:** COMPLETE — one bounded strict source-train-task-disjoint frozen-checkpoint evaluation passed all predeclared h1/h2/h5 point and bootstrap gates

**Date:** 2026-08-28 09:30 CDT

## Goal

Run exactly one bounded, read-only strict source-train-task-disjoint cross-candidate BridgeData rollout evaluation on frozen rejected candidates `001` and `002`. Compare only against source-train fitted baselines. Preserve a no-training, no-mutation, no-promotion record.

## Files To Read

- `AGENTS.md`, Charter, `README.md`, `STATUS.md`, latest BridgeData handoffs, and the completed task-disjoint feasibility plan/handoff.
- `CCF_Sovereign/evaluate_bridgedata_task_disjoint_feasibility.py` plus existing frozen rollout, cross-rollout, and uncertainty modules/tests.
- Both candidate lifecycle manifests/checkpoint hashes and frozen intake manifest.

## Files To Edit

- A separate strict task-disjoint frozen-rollout evaluator and focused test.
- The separate real-data evaluation package only if a reusable strict allocator is required.
- `.gitignore` only if needed to exclude the new local evidence root.
- This plan, a dated handoff, README, and STATUS only after measured results exist.

## Fixed Contract

Codex's committed feasibility scan `b047b3091a6494f7e00a48fa7155f7608d92419f` showed adequate strict target capacity: sources `001`/`002` have 23,124/23,973 eligible target episode clusters, 14,480/14,462 strictly source-train-task-disjoint target task identities, and 715,495/732,461 horizon-five cases. It is feasibility evidence only.

Before prediction, each source strict target pool must have zero overlap with any source-selected/source-train episode and zero overlap with source-train task IDs. Each rollout must be episode-contained, continuity-validated, finite, and recursively driven only by observed initial state plus recorded actions. Baselines are copy-state, train-only action mean-delta, train-only linear state/action delta, and train-only nearest-neighbor.

Use acceptance horizons 1, 2, and 5; select at most 256 deterministic cases per source/horizon using seed `20260828`; require at least 10 target episode clusters and exact finite coverage. Report point-estimate RMSE and the existing 10,000-resample seed-`20260828` episode-clustered paired bootstrap pass/indistinguishable/fail label. Horizon 10 is excluded. No label authorizes promotion.

## Ordered Steps

- [x] Capture repository, process, candidate, input, and feasibility baseline; preserve inherited dirty/untracked paths.
- [x] Inspect feasibility semantics and confirm it does not score models.
- [x] Implement/test separate strict evaluator: task/episode overlap refusal, deterministic bounded selection, train-only baselines, exact coverage, and bootstrap labels. Two read-only preflight probe failures were preserved: an unsupported custom rollout split label, then an unsupported unbounded-case request. The evaluator was corrected to the existing held-out-task case label and its fixed 256-case bound; a third preflight verified 128 observed target episodes and 256 h1/h2/h5 cases for each source.
- [x] Compile/run focused tests/audit plan; explicitly stage only owned paths; commit and push before evaluation. The complete focused BridgeData suite completed with 57 tests passed.
- [x] Run one fresh ignored local read-only evaluation; verify hashes, lifecycle, and process state. Both source candidates used 128 strict complete target episodes with zero source-selected episode and source-train task overlap, selected 256 exact finite rollout cases at every acceptance horizon, and passed all point and paired-bootstrap h1/h2/h5 labels.
- [x] Record results/non-claims in handoff, README, STATUS; audit, commit, and push.

## Test Gate

Run `python -m compileall -q` for touched Python, focused BridgeData unittest modules including feasibility/new strict evaluator tests, Markdown audit for plan/handoff, and `git diff --check --cached` before commits.

## Storage, Safety, and Rollback

New evidence must be fresh Git-ignored local output below 5 MiB. No download, training, tuning, candidate creation, checkpoint/parent/input/lifecycle mutation, promotion, renderer/Chronos/6FR work, robot action, manufacturing, deletion, reset, amend, or bulk staging. If any strict disjointness, hash, lineage, coverage, or metric check fails, preserve an ineligible receipt and stop; do not tune/rerun altered configurations.

## Next-Agent Pickup Notes

This asks whether frozen source predictors beat strongest source-train baselines on source-train-task-unseen target rollouts. Positive results are narrow predictive evidence only—not a policy, control, safety, world-model, Chronos-native, or product claim.


