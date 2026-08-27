# Handoff — Manus Lane B: world-data ingestion and transition metrics

**Date:** 2026-08-26
**Lane:** B — Learning path, Phases 2 and 3
**Owner:** Manus
**Director:** Claude
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus`
**Starting HEAD:** `856df203dbb3adeff10e351eaee20f3ba8063166`
**Current observed HEAD:** `ac43340f1f5ae956b3e5915d4f9b2920f56363c9`
**Status:** IMPLEMENTED AND VERIFIED — UNCOMMITTED; DIRECTOR COMMIT WINDOW REQUIRED

## Charter and lane boundary

This work follows the multi-lane build charter assigned by the operator. Manus owns only `CCF_Sovereign/src/world_data/**`, `CCF_Sovereign/src/world_metrics/**`, `CCF_Sovereign/test_world_ingestion.py`, `CCF_Sovereign/test_transition_metrics.py`, and Manus-named root plan/handoff files. No director-only truth surface, checkpoint, candidate path, or sibling repository was edited. The required Charter, `AGENTS.md`, multi-lane charter, current Stage 2 implementation, candidate/evaluation references, and `vision_deep_dive.md` were read. The latter is operator context only and is not evidence for a chronology, provenance, capability, or intellectual-property claim.

The shared `main` advanced during this lane from the listed starting commit to `ac43340f1f5ae956b3e5915d4f9b2920f56363c9`, Codex’s `test(promotion): add governance gate`. Its committed paths are confined to `src/promotion`, promotion tests, governance documentation, and Codex plan/handoff; it does not touch any Manus-owned path. The protected parent remained SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.

## What changed

### Phase 2 — manifest-bound trajectory ingestion

`CCF_Sovereign/src/world_data/ingestion.py` adds a no-training ingestion library for canonical Stage 2 `WorldProgram` JSONL. It verifies the manifest type and explicit false claims, source JSONL SHA-256, byte count, record count, program-hash-set digest, canonical JSON serialization, typed schema validation, and 4K vocabulary codec digest. It validates all four partitions from emitted records rather than trusting only the manifest: `train`, `held_out_object_class`, `held_out_operation_family`, and `held_out_composition`.

The loader rejects train-versus-held-out overlap in canonical program hashes, structural signatures, and source-evidence hashes. It also rejects whole-object, operation-family, composition, and composition-generator-family leakage. It produces deterministic 256-token segments at a 255-token stride, retaining each segment’s program, source hash, partition, family labels, evidence hashes, and precise boundaries. It batches only within a partition, and independently re-verifies the same isolation and continuous source coverage from the emitted batches.

### Phase 3 — per-split transition metrics

`CCF_Sovereign/src/world_metrics/transition_metrics.py` adds a no-training scoring library for externally supplied predicted typed programs against the manifest-bound targets. It requires exact target/prediction coverage and reports state, relation, operation, uncertainty, exact-program, evidence-completeness, compiler-evidence-completeness, and compiler-validity for each of the four partitions independently. It deliberately emits no pooled held-out score.

Compiler validity is unavailable for a split unless every supplied prediction has a matching compiler receipt labeled `observed` and bound to the predicted program SHA-256. Generated or inferred receipts are rejected. The metrics library itself does not execute a compiler or renderer, start a model, write a checkpoint, create a candidate, or authorize promotion.

## Owned pathspecs proposed for the director window

```text
CCF_Sovereign/src/world_data/__init__.py
CCF_Sovereign/src/world_data/ingestion.py
CCF_Sovereign/src/world_metrics/__init__.py
CCF_Sovereign/src/world_metrics/transition_metrics.py
CCF_Sovereign/test_world_ingestion.py
CCF_Sovereign/test_transition_metrics.py
plan_2026-08-26_2154_manus-lane-b-ingestion.md
handoff_manus_2026-08-26_lane-b-learning-path.md
```

No directory glob, checkpoint, ignored smoke artifact, gate log, foreign plan, foreign handoff, untracked Lane A file, or truth surface belongs in this pathspec. Manus has not staged, committed, pushed, pulled, stashed, reset, restored, reverted, rebased, or otherwise changed Git state.

## Commands run and exact results

The complete preserved final gate record is ignored local artifact `CCF_Sovereign/tmp/manus_lane_b_full_gate_20260826_2208.log`, SHA-256 `7f8aeb09137903b7786afd4c9f2d411038929c3e7492d71ac9ade108507e99a2`.

| Command | Result |
|---|---|
| `python -m compileall -q src\world_data src\world_metrics test_world_ingestion.py test_transition_metrics.py` | Exit `0` |
| `python test_world_ingestion.py` | 11 tests passed; exit `0` |
| `python test_transition_metrics.py` | 8 tests passed; exit `0` |
| `python test_world_trajectory_generator.py` | 7 tests passed; exit `0` |
| Parent SHA-256 before and after all gates | Identical: `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |

The real ignored Stage 2 smoke dataset was ingested without mutation. Its JSONL SHA-256 is `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28`; its manifest SHA-256 is `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`. From 21 programs, the loader produced 627 segments and 159 same-split batches at 256-token segments, 255-token stride, and batch size 4.

## Failures and corrective action

The first isolated emitted-batch leakage test hit the earlier source-evidence-overlap guard rather than the object-class guard. The fixture was corrected to use distinct synthetic test-only lineage values, then the intended object-family guard passed. This was a test-fixture ordering issue, not a runtime failure of the loader.

A GPU status probe failed with `Failed to initialize NVML: Unknown Error`. No GPU work was requested, authorized, or performed; no training, candidate, compiler, or renderer process was launched. That probe is a monitoring limitation, not evidence of GPU availability or activity.

## What remains unproven or unwired

The loader is not wired into `train.py`, because that file is outside Lane B’s assigned path ownership and no candidate run is authorized. The metric tests compare target programs to supplied fixtures; they do not evaluate a learned model. The current typed `WorldProgram` carries object state and action programs but does not contain complete per-frame post-action state snapshots, so state and operation scores are typed-program reconstruction evidence, not physical simulation or render-observed next-state evidence.

No compiler receipt exists for any real prediction. No renderer output, observed pixel hash, model-generated world prediction, candidate checkpoint, promotion decision, A–F ablation, or performance claim exists. Compiler validity remains unavailable in real use until Lane A provides actual observed receipts; it cannot be represented by generated fixture output.

## Current dirty/untracked state

The shared tree intentionally remains dirty. Director-held root files are preserved untouched: `plan_2026-08-26_2042_verify-stage2-claims.md`, `plan_2026-08-26_2058_repo-sync.md`, `plan_2026-08-26_2144_multi-lane-build-charter.md`, `plan_2026-08-26_2158_claude-lane-a-compiler-render-witness.md`, and `vision_deep_dive.md`. Lane A’s untracked owned files are also preserved untouched: `CCF_Sovereign/compile_world_programs.py`, `CCF_Sovereign/src/world_compile/**`, and `CCF_Sovereign/test_world_compiler.py`. This handoff, the Manus plan, and the six owned source/test paths are the only untracked paths created or changed by Manus.

## TRUTH-SURFACE REQUEST

**Target file:** `STATUS.md` (director-only)

**Artifact basis:** `CCF_Sovereign/tmp/manus_lane_b_full_gate_20260826_2208.log`, SHA-256 `7f8aeb09137903b7786afd4c9f2d411038929c3e7492d71ac9ade108507e99a2`; Stage 2 source manifest SHA-256 `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`.

**Proposed wording:**

> **Wired but not a learned-world result — Stage 2 ingestion and transition scoring.** The repository contains a manifest-bound loader that verifies canonical Stage 2 typed-program JSONL, source hashes, whole-family holdouts, program/signature/evidence separation, deterministic segmentation, and same-split batching. It also contains per-split typed-program scoring for train, held-out object, held-out operation, and held-out composition; no pooled held-out score is emitted. The recorded gates pass, but this is infrastructure and fixture-based scoring only. No train.py integration, model prediction, compiler execution, renderer output, candidate run, checkpoint mutation, promotion, or learned-world capability has been demonstrated.

## Director action requested

Please independently re-run the listed gates, inspect only the explicit pathspecs, verify the parent hash, ensure no foreign path is included, and grant or deny a serialized commit window. If granted, Manus will commit only the listed owned paths using the required identity and report the resulting SHA; no GPU token is requested.

## Next step if integrated

After a director-authorized integration, the next technical action is not training. First bind the loader receipt to an approved candidate-run configuration and define a training-side adapter without weakening the current corpus-manifest or parent-hash gates. In parallel, consume Lane A’s actual compiler receipts only when they are observed and hash-bound. A 50M candidate remains separately gated by operator authorization, director GPU token, Codex promotion checks, and Claude witnessing.
