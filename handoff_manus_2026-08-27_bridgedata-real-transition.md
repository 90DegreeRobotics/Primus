# Handoff — Bounded BridgeData Real State-Transition Gate

**Status:** Completed; candidate retained as evidence and rejected from promotion.

## Scope and Result

This work executed the first bounded real-data Primus learning gate using the frozen local BridgeData V2 LeRobot intake. The task was a one-step observational regression problem: **7D `observation.state[t]` plus 7D `action[t]` predicts 7D `observation.state[t+1]`**. It deliberately excluded robot-policy learning, robot command/control, safety validation, actuation, manufacturing, visual prediction, renderer work, native Chronos integration, parent mutation, and candidate promotion.

The compact 19,591-parameter from-scratch residual MLP satisfied the predeclared numerical comparison: it had exact prediction coverage and strictly lower aggregate RMSE than the strongest stated baseline on both protected partitions. The result is narrow but real: one action-conditioned, one-step state prediction model trained on a bounded real robot-data intake generalized better than the three declared simple baselines on the held-out groups described below.

| Partition | Cases | Strongest baseline | Baseline RMSE | Candidate RMSE | Absolute improvement | Acceptance result |
|---|---:|---|---:|---:|---:|---|
| Train | 11,999 | Nearest train state/action | 0.0346366257 | 0.0223968794 | 0.0122397463 | Descriptive only |
| Held-out episode | 1,998 | Nearest train state/action | 0.0399958638 | 0.0249904402 | 0.0150054236 | Passed |
| Held-out task | 1,996 | Nearest train state/action | 0.1124550702 | 0.1087545187 | 0.0037005515 | Passed |

The predeclared acceptance rule was: **exact coverage and strictly lower aggregate RMSE than the strongest explicit baseline on both protected partitions.** It passed. The held-out-task margin is positive but modest; it requires independent replication before it should be relied upon for broader scientific, funding, or product claims.

## Data, Split, and Leakage Boundary

The frozen intake manifest is `CCF_Sovereign/data/external/bridgedata2_lerobot_v3_metadata_20260827/intake_manifest.json`, SHA-256 `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`. Its data, episode, and task inputs were independently hash-verified before creation, during training, checkpointing, evaluation, rejection, and post-run review.

The full loaded Parquet data shard contained 1,496,285 rows. The candidate used a predeclared small selection by complete episode only after strict group allocation. No frame-level random split or sampling was used. The extractor emitted a transition only when both rows proved identical episode identifiers, consecutive frame identifiers, consecutive global identifiers, finite 7D values, and a 0.2-second timestamp step within tolerance.

| Evidence property | Observed value |
|---|---:|
| Bounded train episodes | 336 |
| Bounded held-out-episode episodes | 61 |
| Bounded held-out-task episodes | 56 |
| Bounded train task identities | 269 |
| Familiar-task IDs in held-out-episode partition | 49 |
| Strict unseen task IDs in held-out-task partition | 48 |
| Unmapped/empty-task episodes excluded before allocation | 6,608 |
| Otherwise eligible episodes excluded by declared budget | 34,995 |
| Extracted transition-set SHA-256 | `a50225aae74493de5ac3700f80618409db196b614d876194e99d22ca62c02cc3` |
| Split SHA-256 | `62d31d930af6a754093c918dac4c471ae77cdeec8463e1d41810f5c7be8b55bc` |

The strict held-out-task partition has task identities disjoint from both train and held-out-episode partitions. The held-out-episode partition preserves task identities in train while withholding complete episodes. The metrics report separately for each partition; it intentionally emits no pooled holdout score.

## Implemented and Verified Code

Commit `dff243172308400eb088cc0c95ed479d25ad473b` (`feat(real-data): add BridgeData transition gate`) was pushed to `origin/main` before the candidate run. It added the separate `src/real_data` intake/extraction and evaluation package, the isolated `training/real_data_candidate.py` lifecycle, the bounded MLP runner, focused temporary-Parquet tests, and an ignore rule for external observational inputs.

The code is purposely separate from synthetic `world_data` contracts. The real-data candidate lifecycle is not the existing Council-text `CandidateRun`: that existing class binds Council corpus inputs and would be semantically inappropriate for this observational state-transition experiment. The new lifecycle still protects both Council parent copies by the established SHA-256, accepts only a new candidate directory, binds intake/data/episode/task inputs by hash, records the code commit and config, uses an atomic manifest, and exposes no promotion operation.

The combined focused gate was run from `C:\Primus\CCF_Sovereign`:

```text
python -m compileall -q src\real_data training\real_data_candidate.py train_bridgedata_real_transition.py test_bridgedata_transitions.py test_bridgedata_evaluation.py test_real_data_candidate.py test_train_bridgedata_real_transition.py
python -m unittest -v test_bridgedata_transitions test_bridgedata_evaluation test_real_data_candidate test_train_bridgedata_real_transition
```

The compile gate exited `0`. The focused suite exited `0` with **22 tests passed**. It covers manifest/hash refusal, cross-episode exclusion, skipped-frame rejection, finite vectors, deterministic extraction, exact coverage, whole-episode and strict task leakage checks, complete-episode budget selection, train-only baselines, isolated lifecycle behavior, parent-output refusal, pre-existing hash-pinned plan handling, and compact MLP output coverage.

## Candidate Lifecycle and Local Evidence

The only candidate launched was `bridge-real-20260827-001`, on CPU because `nvidia-smi` could not initialize NVML during preflight. It ran 1,880 updates over 40 epochs in 5.39280040000449 seconds. The first-batch normalized-delta loss was `0.95059734582901`; the last-batch loss was `0.359754323959351`. This loss reduction is optimization evidence only; the split-separated RMSE table above is the relevant generalization evidence.

Candidate evidence remains intentionally local and ignored beneath `C:\Primus\CCF_Sovereign\checkpoints\candidates\bridge-real-20260827-001\`.

| Artifact | SHA-256 |
|---|---|
| Candidate checkpoint | `ed03de679a4ae7304fc7ce2179f35fce1cc8ee4b0fb5e15f1198ac6595e870` |
| Metrics evidence | `11eb6dc92edfcc2a38748696d36138add9025cac5b671fbdf65406440f58a2e7` |
| Raw predictions | `249b4012c9c4bb89d61aeaf24eff62290f8579a1b2262c016c06bfc19d1608eb` |
| Candidate prediction set | `d1e7295cf8730b69aa50e82ba545d361c18d6d228fd98aa94bed74994c2c0643` |
| Extraction receipt | `ae185ae6c1a7057b70295f539d89cfe580bc69d4c2c619aaa8182a9db7556d6e` |

The checkpoint restore smoke check passed: reconstructed model predictions exactly matched the saved-run prediction set. The candidate manifest reached terminal status `rejected`, not `promoted`. Promotion was disabled as a training side effect, promotion was not performed, and no promotion interface exists in this candidate lifecycle.

Both Council parent copies remained SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` after the run. No candidate process remained active at post-run inspection.

## Non-Claims and Current Limitations

This result does **not** demonstrate a robot policy, reliable robot behavior, safe control, counterfactual action understanding, causal intervention, manipulation success, multi-step stability, visual world modeling, renderer quality, native Chronos integration, creativity, manufacturing ability, or deployment readiness. It does not validate another dataset shard, other robots, other action horizons, or a full BridgeData package. It is not a replacement for Primus with an external model: the predictor is locally trained from scratch and the public dataset is observational grounding only.

The 6,608 excluded episodes reveal an intake limitation: their metadata had blank or unmapped task catalog entries, so they were retained in source evidence but deliberately excluded from task-aware allocation. The 34,995 budget exclusions show that this is a small approved experiment, not an exhaustive pass over the acquired shard. The modest strict-task improvement is particularly sensitive to replication requirements.

## Repository State and Preserved Work

At post-run inspection, `main` and `origin/main` were both `dff243172308400eb088cc0c95ed479d25ad473b`. The candidate artifacts and frozen BridgeData inputs are ignored. The following inherited untracked root plans remained preserved and unstaged; their hashes were pinned by the candidate lifecycle during the run:

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

No Chronos2 renderer files were changed, no renderer image was produced, and no 6FR work was performed.

## Next Evidence Boundary

Do not tune or resume `bridge-real-20260827-001`. Retain it as a completed fixed evidence point. The next justified action is one independently declared replication or cross-validation gate, using a fresh candidate ID and distinct whole-group selection from a separately approved bounded input extent. It must preserve the same hash checks, exact coverage, explicit baseline comparison, and separate no-promotion decision. A result should be treated as stronger only if it reproduces the held-out-task improvement without relaxing leakage rules or scaling data silently.
