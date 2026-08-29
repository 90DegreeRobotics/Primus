# Handoff — Lane B: First Real Phase 0 Forward-Model Candidate

**Date:** 2026-08-29 CDT
**Lane:** Manus / Lane B
**Status:** **Real candidate evaluated; learned holdout result recorded; no promotion.**
**Candidate:** `geometry-phase0-20260829-001`

## Executive Result

This is a **real learned result** for the frozen `geometry_program_corpus_v2`
corpus, not a fixture result. The candidate was trained on the real structural
training partition and evaluated once against both predeclared structural
holdouts. It is a candidate-level measurement only; it is **not** a promotion,
product capability claim, renderer result, or generalization claim outside this
frozen corpus and these named holdouts.

The model beats the training-mean and step-count-only baselines for `8/11`
metrics on the held-out-length split and for `10/11` metrics on the harder
held-out-operation-combination split. Against the nearest-neighbour op-mix
baseline, it wins `9/11` and `7/11`, respectively. It does **not** uniformly
beat every baseline: volume and `is_closed` lose to all three baselines on the
length holdout; several operation-count metrics lose to op-mix nearest-neighbour
on the combination holdout. Those losses are preserved below.

## Tandem Preconditions and Start State

Before any change or candidate creation, I read `AGENTS.md` in both
`C:\Primus` and `C:\chronos2`, the required Charter and Annex, and
`handoff_claude_2026-08-29_r2-lane-a-corpus-integration.md` in both repos. The
Lane A handoff copies were SHA-256-identical. The stale v1 statement in that
handoff was not acted upon: `load_geometry_corpus_intake` was already upgraded
to v2 in `e4b9518` and successfully loaded the real 552-record corpus.

| Repository | Start commit | Start upstream | Pre-run working tree |
|---|---|---|---|
| `C:\Primus` | `e14615e9fb2aa99b19eb499bc8818c13656c24c1` | Same | Clean |
| `C:\chronos2` | `7644ca35d64a12b725dd7ddfeef95a4bde2c63d1` | Same | Clean |

## Frozen Real Corpus Receipt

| Input | Location | SHA-256 / fact |
|---|---|---|
| Corpus | `C:\Primus\CCF_Sovereign\tmp\geometry_corpus_from_chronos2\seed_20260829\corpus.jsonl` | `dedb5c1d56ac31b4e5aab56c9e48460a48db663eccc3f6ef48079b54d6bff3c0`; 552 records |
| Manifest | Same directory | `b0fd9125830fa53fa2515c9a7c6b7e845499effb87f79607b7bdb16c9cfe4bc4` |
| Split definition | Same directory | `46d05a7cf01927f3a59029b1ee59fbf75e0a45cd35143daabadc6138ab82229b` |
| Schema | `geometry_program_corpus_v2` | `61d3ed74658a4dad5afa1344634faba389ec8a03db234706032c72bb28430c47` |
| Train | Structural split | 361 records |
| Held-out length | `step_count = 6` | 56 records |
| Held-out operation combination | `create_cube + pull_face` | 135 records |

`python audit_geometry_corpus.py` reported `status: pass` against these exact
three frozen files before the candidate was created. The candidate manifest
re-verified the corpus, manifest, split, and schema receipts before evaluation.

## Predeclared Decisions

### 1. Zero-mesh records: **KEEP**

I kept all three records with `vert_count = 0`, zero area, zero volume, and zero
loose parts. These are legitimate deterministic executor outcomes in which a
valid subtractive program removes the body. Filtering them would erase a
meaningful, learnable program-to-mesh outcome and silently change the frozen
corpus. They comprise three of 552 records (approximately `0.543%`).

### 2. Target scale: **log1p for extensive metrics, then per-target z-score**

This was committed before the real result in
`ae5a231d7bf709fe48585ce55e439642931e72c8`.

`log1p` was applied to the non-negative extensive metrics: `vert_count`,
`edge_count`, `face_count`, `tri_count`, the three bbox extents,
`surface_area_mm2`, and `volume_mm3`. It maps a valid zero-mesh value to exactly
zero while compressing the severe high-value tail. `loose_part_count` and
`is_closed` remain identity-valued, and **all eleven** target columns are then
z-scored from the training partition only. Predictions are inverse-transformed
back to raw units before MAE/RMSE reporting. This prevents raw volume from
dominating the loss without filtering, reweighting by holdout data, or using
`view_score`.

## Candidate Execution and Lifecycle

The real command was executed exactly once, without `--fixture-only`:

```powershell
python train_geometry_phase0.py `
  --corpus   tmp/geometry_corpus_from_chronos2/seed_20260829/corpus.jsonl `
  --manifest tmp/geometry_corpus_from_chronos2/seed_20260829/manifest.json `
  --splits   tmp/geometry_corpus_from_chronos2/seed_20260829/splits.json `
  --output-root checkpoints/candidates `
  --candidate-id geometry-phase0-20260829-001
```

| Execution field | Actual value |
|---|---|
| Start UTC | `2026-08-29T17:11:11.8359644Z` |
| End UTC | `2026-08-29T17:11:21.0049644Z` |
| Elapsed | `9.169` seconds |
| Code commit recorded by candidate | `ae5a231d7bf709fe48585ce55e439642931e72c8` |
| Model configuration | seed `17`; 32 epochs; learning rate `0.01`; hidden width `32` |
| Loss | initial `1.1421766281`; final `0.3823361397` |
| Manifest state | `evaluated` |
| Fixture-only | `false` |
| Promotion state | `rejected_by_default`; `permitted: false` |
| Parent model | None; no parent was read, changed, or compared |

The candidate was created only at
`C:\Primus\CCF_Sovereign\checkpoints\candidates\geometry_phase0_candidates\geometry-phase0-20260829-001`.
It contains atomically written manifest and checkpoint evidence. The checkpoint
SHA-256 is
`1f99e802dd70c65e21fe5073723860d83606bd545970f1a6c9a16ab07422bc7b`.

## Complete Holdout Results

All numbers are raw-unit MAE/RMSE after inverse-transforming model predictions.
The three baselines were declared before results: **training mean**,
**step-count-only**, and **nearest neighbour over op-mix**. `yes / no` states
whether the model’s RMSE is strictly lower than the baseline RMSE in the column
order mean / step-count / op-mix NN.

| Holdout | Metric | N | Model MAE | Model RMSE | Mean RMSE | Step-count RMSE | Op-mix NN RMSE | Beats mean / step / NN |
|---|---|---:|---:|---:|---:|---:|---:|---|
| held_out_length | vert_count | 56 | 1462.75 | 7021.63 | 7114.40 | 7114.40 | 7140.10 | yes / yes / yes |
| held_out_length | edge_count | 56 | 2917.69 | 14070.40 | 14217.70 | 14217.70 | 14273.50 | yes / yes / yes |
| held_out_length | face_count | 56 | 1477.99 | 6933.98 | 7103.61 | 7103.61 | 7133.36 | yes / yes / yes |
| held_out_length | tri_count | 56 | 3118.57 | 13937.30 | 14252.50 | 14252.50 | 14304.40 | yes / yes / yes |
| held_out_length | loose_part_count | 56 | 0.305415 | 0.540254 | 0.577172 | 0.577172 | 0.654654 | yes / yes / yes |
| held_out_length | bbox_extent_x_mm | 56 | 143.499 | 192.005 | 203.506 | 203.506 | 217.112 | yes / yes / yes |
| held_out_length | bbox_extent_y_mm | 56 | 90.1974 | 154.653 | 168.636 | 168.636 | 203.228 | yes / yes / yes |
| held_out_length | bbox_extent_z_mm | 56 | 130.849 | 216.308 | 196.343 | 196.343 | 276.846 | no / no / yes |
| held_out_length | surface_area_mm2 | 56 | 512443 | 1.50012e+06 | 1.53350e+06 | 1.53350e+06 | 1.64811e+06 | yes / yes / yes |
| held_out_length | volume_mm3 | 56 | 1.04891e+07 | 2.42663e+07 | 1.65457e+07 | 1.65457e+07 | 1.93073e+07 | no / no / no |
| held_out_length | is_closed | 56 | 0.447132 | 0.632443 | 0.523181 | 0.523181 | 0.534522 | no / no / no |
| held_out_op_combo | vert_count | 135 | 287.244 | 1202.47 | 1239.38 | 1331.11 | 1042.45 | yes / yes / no |
| held_out_op_combo | edge_count | 135 | 570.090 | 2414.54 | 2478.77 | 2661.96 | 2084.58 | yes / yes / no |
| held_out_op_combo | face_count | 135 | 278.796 | 1173.68 | 1239.69 | 1331.17 | 1042.57 | yes / yes / no |
| held_out_op_combo | tri_count | 135 | 574.154 | 2361.63 | 2484.69 | 2670.52 | 2090.84 | yes / yes / no |
| held_out_op_combo | loose_part_count | 135 | 0.117195 | 0.223465 | 0.208735 | 0.209807 | 0.285450 | no / no / yes |
| held_out_op_combo | bbox_extent_x_mm | 135 | 98.6810 | 202.701 | 229.199 | 225.247 | 258.965 | yes / yes / yes |
| held_out_op_combo | bbox_extent_y_mm | 135 | 112.825 | 230.371 | 242.741 | 238.578 | 272.506 | yes / yes / yes |
| held_out_op_combo | bbox_extent_z_mm | 135 | 101.918 | 245.565 | 265.255 | 261.138 | 309.107 | yes / yes / yes |
| held_out_op_combo | surface_area_mm2 | 135 | 507860 | 2.36832e+06 | 2.38322e+06 | 2.38919e+06 | 2.44149e+06 | yes / yes / yes |
| held_out_op_combo | volume_mm3 | 135 | 7.83118e+06 | 1.62582e+07 | 1.99297e+07 | 1.94742e+07 | 2.33731e+07 | yes / yes / yes |
| held_out_op_combo | is_closed | 135 | 0.207063 | 0.254859 | 0.470174 | 0.470164 | 0.354860 | yes / yes / yes |

The held-out-combination result is mixed rather than perfect. The candidate
beats mean and step-count-only for the four complexity-count metrics, all three
bbox extents, surface area, volume, and closure; it loses to op-mix NN on the
four complexity-count metrics and loses to mean and step-count-only on loose
parts. This is an informative first composition result, not evidence that the
model has mastered every structural effect.

## Leakage and Safety Gates

| Gate | Actual result |
|---|---|
| Real corpus audit | `status: pass` before candidate creation. |
| Candidate receipt verification | All frozen input hashes, current trainer SHA-256, checkpoint SHA-256, manifest state, and no-promotion state matched. |
| Target-transform regression | Passed. Zero inputs remain zero under `log1p`; inverse transform restores raw values. |
| `view_score` non-use regression | Passed. Changing every score by `1000` leaves features, targets, model metrics, and baseline metrics unchanged. |
| Mesh-target leakage regression | Passed. Altering `mesh_metrics` changes target tensors but leaves model features byte-identical. |
| `python test_train_geometry_phase0.py` | Passed: 5 tests in 2.497s. |
| `python test_geometry_corpus.py` | Passed: 8 tests in 2.698s. |
| `python test_no_recipe_guard.py` | Passed: 5 tests in 0.089s. |
| `python -m py_compile test_train_geometry_phase0.py train_geometry_phase0.py` | Passed with no output. |

The final target-leakage regression test was committed after the candidate run
in `95ef333118271bdd1c64cf23b0b96f4f3d5c85fe`; it changes only the test and
not the candidate’s recorded trainer source. The actual candidate trainer hash
continues to match its manifest receipt.

## Evidence Artifacts

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| Candidate manifest | `35e20589c0ed29797f1ad4b6461b051f3656f2bba3a905f7651488a97ac3b6c1` | 40192 |
| Candidate checkpoint | `1f99e802dd70c65e21fe5073723860d83606bd545970f1a6c9a16ab07422bc7b` | 7960 |
| Split-separated machine summary | `3d17739e9468e6da15016618b17d42dff13710c80010096aebd661439cf992b5` | 13093 |
| Split-separated Markdown table | `231dbd1d2dbe894cb40756eac1faefe04f8d722d9cf17d775019e9473a678569` | 3037 |

## Files Touched

| Repository | Paths |
|---|---|
| `C:\Primus` | `CCF_Sovereign/train_geometry_phase0.py` — declared zero-preserving target transforms and candidate receipt fields; `CCF_Sovereign/test_train_geometry_phase0.py` — transform, `view_score`, and target-leakage guards. |
| `C:\chronos2` | No source, corpus, renderer, executor, UI, installer, or product-surface changes in this lane. This identical handoff is the only lane document copied there. |

## Commits and Final Synchronization

| Repository | Source commits in this unit | Handoff commit | Final state |
|---|---|---|---|
| `C:\Primus` | `ae5a231d7bf709fe48585ce55e439642931e72c8`; `95ef333118271bdd1c64cf23b0b96f4f3d5c85fe` | Recorded after this handoff is committed | Must end clean with `HEAD == origin/main`. |
| `C:\chronos2` | None | Recorded after this handoff is committed | Must end clean with `HEAD == origin/main`. |

## Not Run

I did not run Blender, use port `9876`, alter the real corpus, touch
`src/real_data`, touch BridgeData intake, extend the synthetic trajectory
generator, run fixture data as a reported result, retrain or tune after seeing
this result, promote the candidate, modify a parent, change product or UI
surfaces, build/install anything, or run the full Primus/Chronos2 suites. No
candidate artifact is committed to Git.

Any follow-up must use a **new candidate ID**, preserve the existing candidate
unchanged, declare any change before looking at its result, compare it against
this candidate and the same baselines on the same frozen holdouts, and retain
rejection-by-default unless separately authorized.
