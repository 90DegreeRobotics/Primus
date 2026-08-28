# Plan — BridgeData Frozen-Checkpoint Rollout Stability Gate

**Status:** ACTIVE

**Date:** 2026-08-27 16:40 CDT

**Goal:** Evaluate, without training or mutation, whether the two terminally rejected, frozen BridgeData one-step transition predictors retain action-conditioned accuracy over open-loop observed action sequences at predeclared horizons on their own leakage-safe protected partitions.

## Files to Read

- `AGENTS.md`, the Charter, `README.md`, `STATUS.md`, and `handoff_manus_2026-08-27_bridgedata-independent-replication.md`.
- `CCF_Sovereign/README.md`, `CCF_Sovereign/MVP_STATUS.md`, and `CCF_Sovereign/requirements.txt`.
- `CCF_Sovereign/src/real_data/bridgedata_transitions.py`, `CCF_Sovereign/src/real_data/bridgedata_evaluation.py`, `CCF_Sovereign/train_bridgedata_real_transition.py`, and focused tests.
- Both local ignored candidate manifests, split receipts, checkpoints, metrics, and raw prediction receipts as read-only frozen inputs.

## Files to Edit

- A separate `CCF_Sovereign/src/real_data/bridgedata_rollouts.py` evaluation module and focused temporary-fixture test.
- A separate `CCF_Sovereign/evaluate_bridgedata_rollout_stability.py` read-only evaluator and focused test, if needed to prove frozen artifact binding.
- This plan and a final root handoff. Update `README.md` and `STATUS.md` only after a measured result.

## Ordered Steps

- [x] Record a repository/process/hash baseline for both candidate checkpoints, lifecycle manifests, split receipts, the frozen intake, and protected Council parent; do not edit candidates.
- [x] Define the evaluation contract before implementation: starts from an observed state; uses only recorded observed actions; recursively feeds predicted state into the next model step; evaluates horizons 1, 2, 5, and 10 with episode-contained consecutive sequences only. At every candidate/partition/horizon, deterministically retain at most 256 valid rollout starts using a stable declared case-order seed; report the exact selected-case count and identity digest rather than treating it as an exhaustive shard result.
- [x] Define non-learned open-loop baselines: copy-state persistence, repeated train-only action-only mean delta, and a nearest-train state/action rollout that remains train-only at each predicted state/action query. Do not use observed intermediate states after rollout start.
- [x] Report split-separated horizon RMSE/MAE, exact sequence/prediction coverage, finite-output rate, and error-growth ratio to horizon 1. Emit no pooled protected score.
- [x] Implement and test fail-hard fixture cases: sequence never crosses an episode boundary; skipped frame/timestamp breaks a sequence; target/horizon coverage is exact; intermediate observed states cannot leak into recursive prediction; checkpoint/manifest/split hash drift refuses evaluation. The full focused suite completed with 34 tests passed.
- [ ] Run compile and focused tests, audit this plan, explicitly stage only evaluator/test/plan paths, commit and push `origin/main` before any evaluation.
- [ ] Run exactly one evaluation-only invocation for both frozen candidates, writing ignored local evidence below a new `CCF_Sovereign/evaluation/bridgedata_rollouts/` directory. No checkpoint, candidate manifest, source data, or parent mutation is allowed.
- [ ] Verify post-evaluation hashes and no process; interpret results by candidate, partition, and horizon. Update truth surfaces and commit a handoff whether the gate passes or fails.

## Predeclared Evaluation and Interpretation Criteria

The evaluator must reject any input whose candidate lifecycle is not terminal `rejected`, whose frozen candidate files/hash bindings drift, whose split receipt cannot map exactly to source transitions, or whose sequence crosses an episode boundary, skips a frame/global index, has invalid timestamp cadence, contains non-finite state/action values, or lacks exact horizon coverage.

The **minimum evidence threshold** is a complete finite curve for every candidate, protected partition, baseline, and declared horizon. At each candidate/partition/horizon, the evaluator will score the first 256 or fewer episode-contained sequences under stable SHA-256 ordering with case-selection seed `20260827`; this is a declared bounded sample, not an exhaustive shard claim. A candidate's temporal result is reported as a narrow positive signal only if it has exact coverage and strictly lower RMSE than the strongest declared baseline at both protected partitions for each of horizons 1, 2, and 5. Horizon 10 is descriptive and may expose failure. A result that fails any condition is a preserved stability limitation, not grounds for retraining, retuning, new candidate creation, or relaxing the protocol.

The output remains an open-loop observational prediction measurement. It is not an action recommendation, robot policy, control command, safety claim, manipulation demonstration, causal test, renderer input, native Chronos integration, or promotion gate.

## Test Gate

Run `python -m compileall -q` for every touched Python module/test and `python -m unittest -v` for the new rollout tests plus existing BridgeData extraction/evaluation/runner tests. Run the repository Markdown audit on this plan and final handoff. Require `git diff --check --cached` before each commit.

## Storage and Safety

No data download, video download, training, candidate creation, checkpoint write, renderer operation, Chronos recipe work, 6FR implementation, robot command, actuation, manufacturing, parent change, or promotion is authorized. All evaluation evidence and logs remain local and ignored under `CCF_Sovereign/evaluation/bridgedata_rollouts/`; expected scale is less than 20 MiB per evaluated candidate because the task stores numeric JSON only.

## Rollback

Do not delete, overwrite, reset, or amend anything. If preflight, integrity, or evaluation fails, preserve an immutable failure receipt in a new ignored directory and stop. Do not alter the candidate artifacts or rerun under a modified protocol.

## Next-Agent Pickup

The two evaluated checkpoints are `bridge-real-20260827-001` and `bridge-real-20260827-002`, both terminally rejected and hash-bound. The first candidate uses 1,998 held-out-episode and 1,996 strict-task one-step transitions; the second uses 1,999 and 1,997. The second candidate's selected 476 complete episodes overlap zero of the first candidate's selected 453. The protected parent SHA-256 is `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; the intake manifest SHA-256 is `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`.
