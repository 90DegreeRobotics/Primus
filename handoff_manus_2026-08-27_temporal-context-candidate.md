# Handoff — generated temporal-context candidate

**Date:** 2026-08-27 CDT
**Prepared by:** Manus
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus` / `main`
**Temporal witness commit:** `7fbfcaa8e0f8c083329c3fb4733f05a91b948bd6`
**Candidate runner commit:** `b3891cc141eb7597f09523c85e4b5d35b5269230`
**Candidate:** `temporal-context-20260827-0742-mlp`
**Lifecycle:** `completed`; promotion not performed

## Executive status

One isolated nonlinear candidate has completed against a fresh, hash-verified generator-v1.1 dataset. It trained only on 256 generated temporal witnesses using an eight-feature pre-state/context vector that excludes direct action delta, final target state, final relations, partition label, object class, operation family, program ID, evidence URI, and source hash. It emitted exact-coverage predictions for all 448 programs and separate metrics for train plus each 64-program whole-family holdout.

The outcome is **positive but inadequate**. It beat the static no-change baseline substantially on position and learned the binary relation outputs well, but it did not solve the generated contextual coordinate rule: complete-transition accuracy is only 3.9% on train and 1.6%–6.3% on the protected splits. Because train accuracy itself remains poor, this is evidence of **underfitting/optimization or representation inadequacy**, not evidence of a holdout-generalization failure. It does not support a learned-world claim.

## What changed

| Commit | Change |
|---|---|
| `69982abe9e8f51edaf4bff4259b03e834bc913a3` | Corrected the stale world-schema statement about the completed direct-delta positive control and created the temporal-witness plan. |
| `7fbfcaa8e0f8c083329c3fb4733f05a91b948bd6` | Added generator v1.1 context-derived declared effects, conditional relation outcome operations, manifest-bound temporal-state witnesses, compatibility tests, and updated world-schema documentation. |
| `b3891cc141eb7597f09523c85e4b5d35b5269230` | Added the isolated nonlinear temporal-context MLP runner, strict input-exclusion contract, tests, and candidate plan. |

No parent/frozen checkpoint, existing candidate, raw Council corpus, renderer output, compiler output, `chronos2`, or foreign-agent surface was edited. Generated datasets, candidates, logs, and helper scripts remain ignored and local.

## Fresh contextual source dataset

| Item | Value |
|---|---|
| Dataset directory | `CCF_Sovereign/tmp/temporal_context_dataset_20260827_0742/` |
| Generator revision | `1.1.0` |
| Seed | `20260827` |
| Programs and splits | 448: 256 train, 64 held-out object, 64 held-out operation, 64 held-out composition |
| JSONL SHA-256 | `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` |
| Manifest SHA-256 | `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41` |
| Temporal witness-set SHA-256 | `18a408d656b62a08029b76cfca25d8a4b0ee930e561ff84a64c76ad830cf5de8` |
| Support final state | 271 true / 177 false |
| Near final state | 269 true / 179 false |
| Target evidence | `generated` and `inferred` only |

The temporal witness uses the source entity’s tick-0 translation and geometry extent/bevel/variant plus material metallic/roughness context. It rederives target translation from the program’s declared `SET_TRANSFORM` operation and final relations from typed add/remove history. The candidate never reads that delta or rederived target as an input.

## Candidate configuration and integrity

| Signal | Observed value |
|---|---:|
| Device | NVIDIA GeForce RTX 3060 / CUDA |
| Model | `mlp_8_32_32_5` |
| Context inputs | 8, with direct targets/deltas/labels excluded |
| Targets | final x/y/z and support/near booleans |
| Epochs / batch size / learning rate | 300 / 16 / 0.01 |
| Train / total scored witnesses | 256 / 448 |
| Optimizer updates | 4,800 |
| Final training loss | 0.003670151811093092 |
| Training time | 20.792273499973817 seconds |
| Position tolerance | 25 mm |
| Checkpoint SHA-256 | `96a4f511757754f3a3be2b00b982ed49e675d05882fd692c0f9397e133b299a2` |

The candidate manifest binds the dataset JSONL and manifest, code commit, source parent, frozen parent, Council corpus/manifest safety prerequisites, feature exclusions, model definition, no-world-model flag, and no-automatic-promotion flag. The strict CPU restore smoke loaded the 11,048-byte checkpoint with `weights_only=True`, restored state exactly, and produced finite output shape `[1, 5]`.

## Exact protected-split results

| Split | Cases | Baseline complete accuracy | Candidate complete accuracy | Baseline RMSE | Candidate RMSE | Candidate support / near accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Train | 256 | 0.000000 | 0.0390625 | 223.1413276005441 mm | 72.1067568342624 mm | 1.000000 / 1.000000 |
| Held-out object class | 64 | 0.000000 | 0.0625000 | 221.68710353784678 mm | 77.76109059794872 mm | 1.000000 / 0.953125 |
| Held-out operation family | 64 | 0.000000 | 0.0156250 | 213.88984216959284 mm | 67.56040544020838 mm | 1.000000 / 0.968750 |
| Held-out composition | 64 | 0.000000 | 0.0312500 | 221.55041986344025 mm | 70.86518907715006 mm | 1.000000 / 0.984375 |

The declared static baseline preserves the original translation and relation default. It had complete-transition accuracy 0 in every partition, position RMSE 213.89–223.14 mm, support accuracy 0.6015625–0.609375, and near accuracy 0.296875–0.43359375. The candidate materially reduces coordinate error and learns relation outcomes, but it misses the strict 25-mm full transition target in most programs, including train cases.

No pooled held-out score was emitted.

## Evidence artifacts

| Artifact | SHA-256 |
|---|---|
| Baseline predictions | `5df2e48d3de178d89e6c436218103c17a5681dedf713c800ab8d5400b3c5551b` |
| Baseline metrics file | `c72f357220b89eb707abde1033730e7879f3f36f2e05eda42602a34b7995ebe5` |
| Candidate checkpoint | `96a4f511757754f3a3be2b00b982ed49e675d05882fd692c0f9397e133b299a2` |
| Candidate run summary | `7fd9299419315d1fedeefee24594c400b2815a9ffbae6f6bfdc1d6c65eebf1e5` |
| Non-mutating promotion decision | `03a652df6367bf8d3a9eaf4ccd37ada6e7c989ba34e32e03064169f6fb658a7a` |

The live and frozen parent remain byte-identical at SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`. No matching candidate process is active.

## Promotion decision

The policy decision is explicitly **ineligible** and has `performs_mutation=false` and `automatic_promotion=false`. It records a missing parent/candidate behavioral comparison, verdict not equal to `CANDIDATE_IMPROVES`, non-positive pass delta, and absence of specific promotion authorization. No promotion command was run.

## Commands and test gates

| Gate | Result |
|---|---|
| Temporal witness evidence contract | Compile passed; 54 focused compatibility tests passed across schema, generator, ingestion, existing/new metrics, candidate safety, original candidate runner, and temporal witness. |
| Temporal-context runner | Compile passed; the complete 57-test matrix passed, adding 3 temporal-context runner tests. |
| Dataset generation | Completed atomically with the source hashes and split distribution above. |
| Candidate run | Completed exit code 0 with an isolated candidate directory and artifacts. |
| Checkpoint restore smoke | Completed exit code 0 with exact hash and finite output. |
| Promotion policy evaluation | Completed exit code 0 and returned ineligible without mutation. |

## TRUTH-SURFACE REQUEST

**Target:** `STATUS.md` (director/operator-owned)

> **Generated temporal-context candidate completed; no learned-world or promotion claim.** A 448-program generator-v1.1 dataset was hash-verified and converted into manifest-bound tick-0/context/tick-2 witnesses. A small nonlinear MLP trained only on 256 generated train witnesses without direct action-delta, target-state, or partition-label inputs. It improved position RMSE versus the static baseline in train and all three whole-family holdouts and learned the two generated relation outputs, but complete transition accuracy remained only 3.9% on train and 1.6%–6.3% on held-out splits. This is an underfit generated-context benchmark result, not evidence of observed dynamics, physical correctness, rendering, general world learning, or a promotable candidate. Parent and frozen checkpoint hashes are unchanged; promotion was not performed.

## Next factual action

Do not train a larger model or claim scaling yet. The immediate next unit should perform a **fixed-data, fixed-split optimizer/representation diagnostic**: normalize the context features and target coordinates with train-only statistics, make target scaling explicit, log train loss by component, and compare one bounded capacity/optimization alternative against this exact MLP under identical 256/64/64/64 source and metric contracts. It must be a planned ablation with equal resource budget, fresh candidate IDs, no pooled holdout score, and no promotion.

If normalization lets the model fit the train data but not the protected splits, that cleanly reveals a real generalization limitation. If it cannot fit train even after the numerical representation is stabilized, improve the generator target design or model class before treating scores as dynamics evidence. Do not conflate either outcome with observed-world learning.

Before the next unit starts, commit this handoff and the updated temporal-context plan as a documentation-only closure, then verify `main` remains clean and synchronized.
