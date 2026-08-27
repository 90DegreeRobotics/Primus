# Handoff — generated world-transition positive control

**Date:** 2026-08-27 CDT
**Prepared by:** Manus
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus` / `main`
**Implementation commits:** `9daca8320c70ef88bbb18d58e82a0f993b1ec64d`, `6ec00293f69c227330faa51d97d80c3421768654`
**Successful candidate:** `world-transition-20260827-0725-linear`
**Candidate lifecycle:** `completed`; promotion not performed

## Executive status

A complete narrow generated-transition learning path now exists and has one isolated successful candidate result. It begins from a hash-verified Stage 2 JSONL/manifest pair, derives action-conditioned transition examples only from each record's declared initial subject translation and `SET_TRANSFORM` delta, trains on 256 **train-only** examples, emits exact-coverage predictions for all 448 examples, and scores train, held-out object, held-out operation, and held-out composition separately. The baseline and model artifacts are hash-bound beneath the isolated candidate directory.

This is a **generated transition positive control**, not a general learned-world result. The six input features expose the generated initial position and movement delta; the linear model learns the corresponding coordinate addition and constant relation outputs. Object class, operation family, program ID, partition, source hash, evidence URI, and final target values are not model inputs. The holdouts prove this narrow arithmetic/relation mapping generalizes across the declared data partitions, but they do not prove causal object dynamics, visual grounding, compiler/render correctness, or physical-world prediction.

## What changed

| Commit | Change |
|---|---|
| `9daca8320c70ef88bbb18d58e82a0f993b1ec64d` | Added manifest-bound generated transition derivation, split-separated numeric metrics, isolated candidate runner, additional frozen-input candidate binding, 10 focused new/updated test paths, and the execution plan. |
| `6ec00293f69c227330faa51d97d80c3421768654` | Fixed the candidate runner's final JSON receipt import after the first isolated run reached output reporting without the import. |

The runner never loads the Council corpus into the linear regressor. The existing parent checkpoint and Council corpus/manifest remain CandidateRun safety prerequisites, while the generated world dataset and manifest are added as explicit frozen inputs and are the actual experiment input.

## Source dataset and isolation

| Item | Value |
|---|---|
| Dataset directory | `CCF_Sovereign/tmp/world_transition_dataset_20260827_0710/` |
| Generator seed | `20260827` |
| Program count | 448 |
| Train / held-out object / held-out operation / held-out composition | 256 / 64 / 64 / 64 |
| JSONL SHA-256 | `f30ba907c71d2c736aeb5e13c0e8a9a79e28d5e649c697dfceee1b5c79febbeb` |
| Manifest SHA-256 | `5da51ab06158cb655aef920e744e214875e369d1aa6346f402bdec10cac5fd43` |
| Program hash-set SHA-256 | `248257dbf3263660d2da6e8e56b91a74f4b89e03ef13a3c924ff745a28edba5f` |
| Structural coverage | 448/448 unique; zero duplicates |
| Evidence labels | `generated`, `inferred` only |

The source manifest retains `model_training_started=false`, `checkpoint_modified=false`, `candidate_promoted=false`, `learned_world_dynamics_proven=false`, and `visual_correctness_proven=false`. Dataset ingestion revalidated the source and emitted 13,405 canonical 4K-codec segments across 838 same-split batches, although the positive-control regressor trains on the one-transition-example-per-program representation rather than on those serialized token segments.

## Successful candidate configuration

| Signal | Observed value |
|---|---:|
| Device | NVIDIA GeForce RTX 3060 / CUDA |
| Model | `linear_6_to_5` |
| Input contract | initial `(x, y, z)` metres and action `(dx, dy, dz)` metres |
| Target contract | final `(x, y, z)` millimetres plus support-present and near-present booleans |
| Epochs / batch size / learning rate | 120 / 16 / 0.03 |
| Train examples / all scored examples | 256 / 448 |
| Optimizer updates | 1,920 |
| Final training loss | 0.0007404651260003448 |
| Training time | 7.048898100008955 seconds |
| Position tolerance | 25 mm |
| Candidate checkpoint SHA-256 | `96493837f7ec892e803110bc11c1222f63761f39b97f23479448c7dd41654907` |

## Exact per-split result

| Split | Cases | Static-baseline all-transition accuracy | Candidate all-transition accuracy | Static position RMSE | Candidate position RMSE |
|---|---:|---:|---:|---:|---:|
| Train | 256 | 0.0 | 1.0 | 270.26547760566217 mm | 0.00004689725132517658 mm |
| Held-out object class | 64 | 0.0 | 1.0 | 270.57435053357636 mm | 0.0000482179443758269 mm |
| Held-out operation family | 64 | 0.0 | 1.0 | 259.0597582283542 mm | 0.000044591724250151294 mm |
| Held-out composition | 64 | 0.0 | 1.0 | 255.8776359577627 mm | 0.00004465426278409405 mm |

The static baseline preserves initial position, support-present, and near-absent; it scored zero on all position-within-tolerance, support relation, near relation, and complete transition metrics. The candidate scored 1.0 for all five metrics in each partition. No pooled held-out score was generated.

## Evidence artifacts

| Artifact | SHA-256 |
|---|---|
| Baseline predictions | `133b7725eed62e7af28a0786ffe54fb434e7f0df00ea68b95c6f9116a31f6144` |
| Baseline metrics file | `2ed54abee3ed40cb608c4e8a01f5c9302c116fdc8db8aa9261b046d6a09e7789` |
| Candidate predictions | `f9bed345ba164f736b04266914f6e7c8ac29f66ffe36f2fdd7e13ce43a11f056` |
| Candidate metrics file | `12fde45ad46ffa7acfff66154ca263da98e50a9cbd45e2e364adc8e65b99cd5a` |
| Candidate run summary | `7129306206affc7cbdfc28e9837d529b4796f50848a3698ed1caba66b99173fb` |
| Non-mutating promotion decision | `d6d30c84d8f5b6615a39664fb9787f68c0c5309b2a649ab70106de2f37da6762` |

The strict CPU checkpoint restore smoke loaded the candidate with `weights_only=True`, restored the state dictionary exactly, and produced finite output shape `[1, 5]`.

## Protected artifacts and promotion

The live and frozen parent stayed byte-identical at SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` before and after the successful candidate. No parent path, frozen archive, source dataset, or candidate artifact was overwritten.

The saved non-mutating policy decision is ineligible. It records no passed parent/candidate comparison, verdict `NO_BEHAVIORAL_COMPARISON`, non-positive pass delta, and no specific promotion authorization. It has `performs_mutation=false` and `automatic_promotion=false`. No promotion command was run.

## Preserved failed attempt

The first candidate ID, `world-transition-20260827-0710-linear`, must remain preserved and must never be reused. It reached training, prediction artifact generation, checkpoint write, and completion state, then raised `NameError: json is not defined` while printing its final receipt. The outer handler recorded it as failed. Commit `6ec00293f69c227330faa51d97d80c3421768654` supplies the one-line import correction. The successful fresh-ID retry above is the valid result. This failure is retained as evidence, not deleted or relabelled.

## Commands run and gates

| Command or gate | Real result |
|---|---|
| Generated-transition initial verification | Compile passed; 41 focused tests passed: candidate safety 5, ingestion 11, original transition metrics 8, generator 7, generated examples 4, generated metrics 4, runner 2. |
| Receipt-fix verification | Compile passed; candidate safety 5, generated examples 4, generated metrics 4, and runner 2 passed. |
| Dataset generation | Completed 448 programs atomically at the source path above. |
| First candidate run | Failed post-checkpoint during receipt printing; preserved under the first candidate ID. |
| Fresh candidate retry | Completed with exit code 0; isolated checkpoint and all prediction/metric artifacts created. |
| Promotion evaluation | Completed with exit code 0; ineligible and non-mutating. |
| Restore smoke | Completed with exit code 0; exact checkpoint hash and finite `[1, 5]` output. |

## TRUTH-SURFACE REQUEST

**Target:** `STATUS.md` (director or operator-owned surface)

> **Generated world-transition positive control completed; no observed-world claim.** A 448-program Stage 2 dataset with 256 train and three 64-program whole-family holdouts was hash-verified and bound into a completed isolated linear candidate. It trained only on train-partition generated examples and achieved 1.0 complete-transition accuracy in train, held-out object, held-out operation, and held-out composition partitions, versus 0.0 for the declared static no-change baseline. This demonstrates only generated coordinate-addition and declared-relation transition learnability from exposed initial position and action delta. It does not demonstrate observed dynamics, visual grounding, renderer/compiler correctness, full typed WorldProgram prediction, or a promotable learned-world model. No candidate was promoted and the protected parent remained unchanged.

## What remains and next action

The decisive remaining gap is **nontrivial target construction**. Current Stage 2 programs encode generated action deltas and invariant relation outcomes; therefore the successful linear task is intentionally a pipeline positive control, not a rich world-model benchmark. The next autonomous work unit should add deterministic per-frame state snapshots or compiler-derived render/state witnesses, vary causal outcomes by action and world context, withhold target-generating rules rather than only labels, and use a capacity-matched model that does not receive the answer directly in its input features. Only then should protected split results be discussed as evidence about learned world dynamics.

Before that work begins, commit this handoff and the updated execution plan as a documentation-only closure unit; keep all candidate, generated-data, temporary helper, and log artifacts ignored and local.
