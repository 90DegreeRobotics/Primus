# Plan — Independent BridgeData State-Transition Replication

**Status:** COMPLETE — independent replication passed; no promotion performed

**Date:** 2026-08-27 15:40 CDT

**Goal:** Run exactly one fresh, bounded replication of the BridgeData 7D state[t] plus 7D action[t] to 7D state[t+1] prediction gate with an episode-disjoint allocation from the prior completed candidate, immutable input evidence, explicit baselines, and no promotion.

## Files to Read

- `AGENTS.md`, the Charter, `README.md`, `STATUS.md`, and `handoff_manus_2026-08-27_bridgedata-real-transition.md`.
- `CCF_Sovereign/README.md`, `CCF_Sovereign/MVP_STATUS.md`, `CCF_Sovereign/requirements.txt`.
- `CCF_Sovereign/src/real_data/bridgedata_evaluation.py`, `CCF_Sovereign/training/real_data_candidate.py`, `CCF_Sovereign/train_bridgedata_real_transition.py`, and their focused tests.
- The prior local ignored candidate's `evidence/split.json`, `evidence/metrics.json`, and lifecycle manifest as read-only evidence.

## Files to Edit

- `CCF_Sovereign/src/real_data/bridgedata_evaluation.py` and its focused test only, to provide a fail-closed fresh-allocation path that reserves every selected episode from the previous candidate.
- `CCF_Sovereign/train_bridgedata_real_transition.py` and focused runner test only, to bind the declared prior candidate evidence and fresh split seed to the replication manifest.
- This plan and a final replication handoff. `README.md` and `STATUS.md` only after a measured result.

## Ordered Steps

- [x] Snapshot current branch, upstream, inherited untracked plans, prior candidate lifecycle, protected parent hashes, frozen input hashes, and active process state without modifying prior evidence.
- [x] Implement a deterministic replication allocation that excludes all episodes selected by the first candidate before task and episode holdout allocation, then proves complete episode/task non-overlap against the full source metadata.
- [x] Test alternate allocation determinism, prior-candidate episode exclusion, retained task leakage protections, exact coverage, and failure on invalid reserved episode identifiers.
- [x] Extend the runner so a supplied prior candidate ID and fixed fresh split seed are bound into its own manifest/config and evidence receipt; no tuning or change to the first candidate is permitted.
- [x] Run compile and focused tests, audit this plan, explicitly stage only replication code/tests/plan, commit and push `origin/main` (`c92c0f9438956b41f4f3266c30cff3b210884627`).
- [x] Preflight a fresh candidate directory, clean tracked code, exact inherited untracked-plan hashes, parent/frozen input hashes, no active training, and output scale.
- [x] Run exactly one candidate, `bridge-real-20260827-002`, with replication seed `20260828`, CPU because CUDA telemetry could not initialize.
- [x] Verify terminal lifecycle, checkpoint restore, exact coverage, no promotion, and post-run parent/input hashes. Commit and push an evidence-first result handoff.

## Predeclared Replication Criteria

The new run may count as an independent replication only if all prior selected episode indices are absent from its train and both protected partitions; every new transition still meets the extractor continuity requirements; strict held-out task identities remain absent from train and held-out-episode partitions; metric coverage is exactly 1.0 with zero unknown or excluded predictions; and the fresh MLP strictly improves aggregate RMSE over the strongest explicit baseline on both protected partitions. A failed criterion is a recorded non-replication, not an invitation to retune or rerun.

The prior candidate, `bridge-real-20260827-001`, remains a fixed rejected evidence point. Its selected episodes, raw predictions, checkpoint, split receipt, metrics, and manifest must not be overwritten, renamed, edited, retrained, or promoted.

## Test Gate

Run `python -m compileall -q` for touched Python files and `python -m unittest -v` for the extraction/evaluation, lifecycle, and runner test modules. Use the Markdown audit helper on this plan and later handoff. Require `git diff --check --cached` before every commit.

## Storage and Safety

No new raw data or video download is authorized. The existing frozen intake remains local and ignored under `CCF_Sovereign/data/external/`. The new checkpoint, raw predictions, metrics, logs, manifest, and split receipt must remain local and ignored beneath `CCF_Sovereign/checkpoints/candidates/bridge-real-20260827-002/`. No robot action, policy/control use, manufacturing operation, renderer, Chronos recipe work, 6FR work, parent mutation, or promotion is in scope.

## Rollback

Do not delete or reset any path. If a safety, split, candidate, or result gate fails, preserve the fresh candidate's local terminal failure/rejection evidence and stop. Do not reuse the candidate directory, relax the acceptance criterion, or train a replacement configuration.

## Result Boundary

The fresh candidate reserved all 453 complete episode identifiers selected by `bridge-real-20260827-001` before allocation. It then selected 476 different complete episodes; measured overlap was zero. On exact-coverage protected evaluation, its 19,591-parameter from-scratch residual MLP achieved aggregate RMSE `0.026467942605055767` versus the strongest held-out-episode baseline's `0.040291279340085966`, and `0.027343755051333143` versus the strongest strict held-out-task baseline's `0.04047397797087077`. The predeclared replication rule passed. This remains narrow real-data one-step state prediction evidence only, not evidence of robot control, safety, multi-step rollout, visual modeling, native Chronos integration, product readiness, or promotion.

## Next-Agent Pickup

Do not tune, resume, overwrite, or promote either completed candidate. The objective after this successful replication is a separately planned multi-step rollout/stability evaluation over the frozen one-step predictor outputs, using no controller/actuation and predeclared error-accumulation and coverage metrics. The parent SHA-256 is `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; the intake manifest SHA-256 is `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`.
