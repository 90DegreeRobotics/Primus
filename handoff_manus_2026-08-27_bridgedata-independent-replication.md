# Handoff — Independent BridgeData State-Transition Replication

**Status:** Completed; independent episode-disjoint replication passed its predeclared numerical gate. Both candidates remain rejected from promotion.

## Scope

This work ran exactly one fresh bounded replication of the real-data, one-step observational task **7D state[t] plus 7D action[t] to 7D state[t+1]**. The model was a local 19,591-parameter residual MLP trained from scratch, not an external pretrained model. The frozen BridgeData V2 LeRobot intake remained local and Git-excluded; no additional data, video, raw archive, model, renderer asset, or dataset scale was downloaded.

The replication was designed to be independent at the **episode** level, not merely a different RNG seed. Before new task and episode holdout allocation, the runner read the terminally rejected prior candidate `bridge-real-20260827-001`, hash-bound its manifest and split evidence, and reserved all 453 complete episodes that candidate had selected. The new candidate, `bridge-real-20260827-002`, used a fresh deterministic allocation seed `20260828`, selected 476 complete episodes, and had measured overlap of **zero** selected episodes with the prior candidate.

This is still a bounded, one-step state-prediction experiment. It does not demonstrate policy learning, control, safety, actuation, manipulation, manufacturing, multi-step rollout, visual world modeling, native Chronos integration, creativity, or deployment readiness.

## Predeclared Gate and Result

The replication criterion was fixed before execution. A result counts only if all selected prior episodes are absent from the new train and protected partitions; all source continuity checks pass; held-out task identities are absent from fresh train and fresh held-out-episode partitions; coverage is exactly 1.0 with zero unknown/excluded predictions; and the fresh MLP has lower aggregate RMSE than the strongest explicit baseline on both protected partitions. Failure would be recorded as a non-replication with no tuning or replacement run.

The criterion passed. The candidate had exact coverage on both protected partitions and improved aggregate RMSE over the strongest explicit baseline. The stronger strict-held-out-task margin is encouraging, but it is a result on the same bounded data shard and needs additional independently declared evaluation before broader capability or funding claims.

| Partition | Cases | Strongest baseline | Baseline RMSE | Candidate RMSE | Absolute RMSE improvement | Gate |
|---|---:|---|---:|---:|---:|---|
| Train | 11,995 | Nearest train state/action | 0.0355297487 | 0.0227005622 | 0.0128291865 | Descriptive only |
| Held-out episode | 1,999 | Action-only mean delta | 0.0402912793 | 0.0264679426 | 0.0138233367 | Passed |
| Strict held-out task | 1,997 | Nearest train state/action | 0.0404739780 | 0.0273437551 | 0.0131302229 | Passed |

No pooled holdout score was emitted. For every reported partition, coverage was `1.0`, unknown prediction count was `0`, and excluded prediction count was `0`. State RMSE equals delta RMSE in this one-step evaluation because each prediction and target shares the same observed `state[t]` anchor.

## Data and Split Integrity

The frozen input manifest was `CCF_Sovereign/data/external/bridgedata2_lerobot_v3_metadata_20260827/intake_manifest.json`, SHA-256 `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`. The candidate lifecycle repeatedly verified this manifest, the bounded Parquet data/episode/task files, and both protected Council parent copies.

The extractor emitted a transition only after proving same episode identity, consecutive global index, consecutive frame index, finite seven-dimensional vectors, and expected timestamp spacing. The fresh bounded selection used whole episodes only after strict group allocation; it did not randomly split frames or perform partial episode selection.

| Integrity property | Observed value |
|---|---:|
| Prior selected episodes reserved before fresh allocation | 453 |
| Fresh selected episodes | 476 |
| Selected episode overlap | 0 |
| Fresh train episodes | 351 |
| Fresh held-out-episode episodes | 63 |
| Fresh held-out-task episodes | 62 |
| Fresh train transitions | 11,995 |
| Fresh held-out-episode transitions | 1,999 |
| Fresh held-out-task transitions | 1,997 |
| Fresh bounded split SHA-256 | `8e3a4b9fc302869f467549a806d6cdd0d3c798c6af9fa1e4676ddf421fccc059` |
| Fresh transition-set SHA-256 | `79c91b81d9c1452a9493ffed63907445934fe39aa4cefe74a039a75e14fffd4c` |

The prior candidate's split receipt was hash-bound at `91056f918b490e9b222e6c27e46477279b20f9cfe39deea7d4c4437c338f7fb5`. The prior candidate manifest was hash-bound at `1642791c641015decd884486e9bb3830a8b484523d58a8cd68a508170cda7f1e`. Neither prior artifact was changed.

## Code, Gates, and Execution

Commit `c92c0f9438956b41f4f3266c30cff3b210884627` (`feat(real-data): add independent replication gate`) was pushed to `origin/main` before the candidate run. It added a fail-closed replication allocation path that rejects an empty, duplicate, non-integer, unmapped, or ineligible prior-episode reservation; allocates fresh strict task and familiar-task/held-out-episode groups only after reservation; and validates coverage against full source metadata. The runner now requires a rejected prior candidate ID and fresh split seed, and binds the prior manifest plus split receipt as frozen run inputs.

The following focused verification gate completed before the code commit:

```text
python -m compileall -q src\real_data\bridgedata_evaluation.py src\real_data\__init__.py train_bridgedata_real_transition.py test_bridgedata_transitions.py test_bridgedata_evaluation.py test_real_data_candidate.py test_train_bridgedata_real_transition.py
python -m unittest -v test_bridgedata_transitions test_bridgedata_evaluation test_real_data_candidate test_train_bridgedata_real_transition
```

The compile gate exited `0`; **25 focused tests passed**. New test coverage verifies deterministic replication allocation, exact exclusion of all selected prior episodes, retained strict-task leakage protection, invalid reservation refusal, and runner binding of a rejected prior candidate's split evidence. A read-only probe on the actual frozen intake confirmed feasibility before the run: it produced the fresh split above with zero overlap and no strict-task leakage.

The fresh candidate ran on CPU because `nvidia-smi` could not initialize NVML at preflight. It completed 1,880 updates over 40 epochs in 5.10727059998317 seconds. First and last normalized-delta batch losses were `1.17713713645935` and `0.319609314203262`, respectively. This loss reduction is only optimization evidence; the protected, split-separated RMSE results above are the generalization evidence.

## Candidate Lifecycle and Local Evidence

`bridge-real-20260827-002` completed checkpointing, scoring, and a restore smoke check, then reached terminal lifecycle status `rejected`. Rejection is intentional: the lifecycle has no promotion interface, promotion is not permitted as a training side effect, and promotion was not performed. The checkpoint restore smoke passed because restored-model predictions exactly matched the saved candidate prediction set.

All candidate evidence remains local and ignored below `C:\Primus\CCF_Sovereign\checkpoints\candidates\bridge-real-20260827-002\`.

| Artifact | SHA-256 |
|---|---|
| Checkpoint | `209bf7ef3e2ff6faf3f25b4cd12f9711edb7d9227f686ce5a8627a215d09c7bb` |
| Metrics evidence | `2a7eeeee64330a4e5b95bf20f693bf4d11433893596108453cefda3c2ad7cb4a` |
| Raw predictions | `9668858d81b1c168aadc3cb17d81d40370612f0fda4dd122592c3b2d19996074` |
| Split receipt | `57b860ac23aeb30853a38b8ef08839d630087141ac6cf3f503c70e1fa4996566` |
| Candidate lifecycle manifest | `3a2f9c00885e22e4606e661b7a98adb7f975d1aac33fe8696850e79f1ef7cca9` |
| Candidate prediction set | `e2c85d2aab694fcdba0d423aacfd26c2e00817c214ae42690fad432000b9f977` |

At final post-run verification, the live and frozen Council parent copies still had SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; the intake manifest hash remained unchanged; and no BridgeData candidate/training process was active.

## Interpretation and Non-Claims

The evidence now supports a narrowly phrased, replicated statement: on two predeclared, whole-episode-disjoint bounded selections from the frozen local BridgeData shard, a locally trained from-scratch MLP beat stated simple baselines for one-step action-conditioned seven-dimensional robot-state prediction on both familiar-task withheld episodes and fresh strict held-out-task partitions.

It does not yet justify claims that Primus understands causality, predicts long action sequences, safely chooses actions, controls a robot, reasons visually, produces native Chronos scenes, or can be promoted into the Council parent. Both experiments share the same bounded intake shard, related state/action conventions, model family, and training recipe. The next gate must directly measure multi-step error accumulation without reusing or tuning either completed candidate.

No renderer work, native Chronos recipe work, 6FR work, robot command, physical actuation, manufacturing, download, or parent mutation occurred.

## Repository State and Next Boundary

Before this documentation closure, `main` and `origin/main` both resolved to `c92c0f9438956b41f4f3266c30cff3b210884627`. The following inherited untracked plans remained preserved and unstaged throughout the run:

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

The next justified experiment is a separately planned **multi-step open-loop rollout/stability gate** using frozen existing checkpoints and observed held-out action sequences. It must be evaluation-only: no policy, no controller, no actuation, no renderer, no new model tuning, no candidate promotion, and predeclared horizon/coverage/drift metrics. That gate should quantify whether one-step gains remain useful as prediction horizons lengthen, or whether errors compound too quickly.
