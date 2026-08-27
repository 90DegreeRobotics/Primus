# Plan — BridgeData Real State-Transition Learning Gate

**Status:** COMPLETE — no promotion performed

**Date:** 2026-08-27 19:50 CDT
**Goal:** Use the bounded, manifest-bound BridgeData V2 intake to evaluate a first real-data action-conditioned state-transition predictor without altering the parent, robot control, renderer, or native Chronos recipe path.

## Files to Read

- `AGENTS.md`, `CCF_Sovereign/README.md`, `CCF_Sovereign/MVP_STATUS.md`, and `CCF_Sovereign/requirements.txt`.
- The bounded intake `data/external/bridgedata2_lerobot_v3_metadata_20260827/intake_manifest.json` and Parquet source files.
- Existing candidate-isolation, world-data ingestion, state-transition metric, and promotion-gate code.

## Files to Edit

- New manifest-bound BridgeData extraction/evaluation modules under `CCF_Sovereign/src/`.
- Focused regression tests only.
- This plan and a final handoff; truth surfaces only after measured results are available.

## Ordered Steps

- [x] Derive transitions only when consecutive frame and episode identifiers prove `t → t+1`; never cross episode boundaries.
- [x] Split at episode/task level before training; no random frame split.
- [x] Create deterministic copy-state, action-only mean-delta, and nearest-neighbor baselines.
- [x] Add a compact isolated learned predictor with a fresh candidate path, frozen input hashes, and no promotion route.
- [x] Run extraction, leakage, baseline, and candidate tests.
- [x] Commit only verified source/tests/plan by explicit pathspec and push `origin/main` (`dff243172308400eb088cc0c95ed479d25ad473b`).
- [x] Run exactly one bounded candidate against a fresh candidate ID and write split-separated evidence (`bridge-real-20260827-001`, rejected/no promotion).

## Test Gate

Python compile gate plus fail-hard tests for manifest binding, consecutive-frame extraction, episode/task split isolation, baseline coverage, candidate isolation, and exact per-split scoring. No test that catches an exception and reports success may certify the result.

## Storage and Safety

The existing 150 MiB BridgeData intake remains local and ignored under `CCF_Sovereign/data/external/`. New candidate and raw evidence artifacts remain ignored under named local paths. No large corpus expansion, physical action, manufacturing command, renderer work, parent mutation, or promotion is in scope.

## Rollback

No tracked source will be deleted or rewritten. If the parser or candidate path fails its gates, preserve its local evidence and do not stage the failing path. Candidate runs use fresh destinations and cannot overwrite the parent.

## Result Boundary

One bounded candidate, `bridge-real-20260827-001`, was evaluated against exact-coverage real observed transitions after this plan's code commit. Its 19,591-parameter from-scratch residual MLP improved aggregate RMSE over the strongest stated baseline on both protected partitions: `0.024990440151625777` versus `0.039995863776179044` for held-out episodes and `0.10875451870665652` versus `0.11245507024109873` for held-out task identities. This is a narrow real-data one-step prediction result only. It does not validate policy learning, robot control, safety, multi-step rollout, visual prediction, native Chronos integration, or a promotion decision. The candidate was explicitly rejected from promotion despite passing the predeclared numerical comparison.

## Next-Agent Pickup

The next evidence gate should reproduce or cross-validate this result on a separately declared bounded intake/split, with the same manifest and no mutation of current artifacts. Do not tune this completed candidate in place. Re-check source hashes, candidate destination freshness, and repository cleanliness before any future run.
