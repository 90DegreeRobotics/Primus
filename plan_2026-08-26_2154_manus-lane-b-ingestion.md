# Plan — Manus Lane B world-trajectory ingestion

**Created:** 2026-08-26 21:54 CDT
**Owner:** Manus
**Charter lane:** B — Learning path, Phase 2 dataset ingestion
**Repository:** `C:\Primus`
**Starting HEAD:** `856df203dbb3adeff10e351eaee20f3ba8063166`
**Starting parent SHA-256:** `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`
**Current observed HEAD:** `ac43340f1f5ae956b3e5915d4f9b2920f56363c9`
**Status:** PHASES 2 AND 3 VERIFIED — READY FOR DIRECTOR COMMIT-WINDOW DECISION

## Goal

Implement the learner-side ingestion path for deterministic Stage 2 world-trajectory JSONL. The loader will bind the source manifest, verify file hashes, preserve whole-family holdouts downstream of the manifest, segment approximately 7.4K-token programs, create deterministic batches, and reject malformed records, manifest drift, partition leakage, and any train/evaluation overlap. It will not start training, create candidates, access checkpoints, alter promotion state, or write director-only truth surfaces.

## Governing and context files read

- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `AGENTS.md`
- [x] `vision_deep_dive.md` as operator-provided constellation context only
- [x] Multi-lane build charter, especially §§1.5, 2, 3, 4, 5, 6, 7, and 9
- [x] `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- [x] `CCF_Sovereign/src/world_schema/model.py`
- [x] `CCF_Sovereign/src/world_schema/tokens.py`
- [x] `CCF_Sovereign/src/world_schema/trajectory_generator.py`
- [x] `CCF_Sovereign/test_world_trajectory_generator.py`
- [x] `CCF_Sovereign/train.py` and current conversation-data loader, as integration boundary
- [x] Existing candidate and evaluation manifest contracts, as read-only reference

`vision_deep_dive.md` is orientation only. This plan makes no chronology, provenance, intellectual-property, or capability claim based on it.

## Owned paths

- [x] `CCF_Sovereign/src/world_data/__init__.py`
- [x] `CCF_Sovereign/src/world_data/ingestion.py`
- [x] `CCF_Sovereign/test_world_ingestion.py`
- [x] `CCF_Sovereign/src/world_metrics/__init__.py`
- [x] `CCF_Sovereign/src/world_metrics/transition_metrics.py`
- [x] `CCF_Sovereign/test_transition_metrics.py`
- [x] `plan_2026-08-26_2154_manus-lane-b-ingestion.md`
- [x] `handoff_manus_2026-08-26_lane-b-learning-path.md`

No other path will be edited. Director-only truth surfaces will receive a `TRUTH-SURFACE REQUEST` block in the handoff rather than edits.

## Ordered work

- [x] Read current trainer, candidate, and evaluation contracts.
- [x] Define immutable ingestion configuration and manifest-bound dataset receipt.
- [x] Load only canonical JSONL records whose SHA-256 matches the supplied manifest.
- [x] Parse and validate each `WorldProgram`; re-encode through the existing 4K codec.
- [x] Preserve and independently re-verify every partition from emitted examples and batches.
- [x] Enforce no program-hash, structural-signature, or source-evidence overlap between train and each held-out split.
- [x] Segment program token streams deterministically without crossing program or split boundaries.
- [x] Batch segments deterministically, retaining program ID, source hash, partition, and segment boundaries.
- [x] Write fail-hard tests for normal ingestion, hash drift, malformed JSON, split leakage, signature leakage, source-evidence overlap, deterministic segmentation, batching, and empty-split rejection.
- [x] Run the focused gate and produce a tiny ignored smoke receipt; do not start training.
- [x] Implement Phase 3 per-split transition metrics after Phase 2 validated the emitted batches.
- [x] Run and preserve the complete Phase 2/3/Stage 2 regression record with parent hashes before and after.
- [x] Write a complete handoff with exact paths, commands, output, evidence, non-claims, and a truth-surface request.
- [ ] Request a commit window from the Claude director with explicit owned pathspecs and full gate output. Do not stage, commit, push, pull, stash, reset, restore, or rebase.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_data test_world_ingestion.py
python test_world_ingestion.py
python test_world_trajectory_generator.py
```

The smoke input was the existing ignored Stage 2 dataset at `CCF_Sovereign/tmp/stage2_smoke_20260826_2024/`, whose JSONL SHA-256 is `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28` and manifest SHA-256 is `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`. With a 256-token segment length, 255-token stride, and batch size 4, ingestion emitted 627 segments and 159 same-split batches from 21 programs. The preserved final gate record is `CCF_Sovereign/tmp/manus_lane_b_full_gate_20260826_2208.log`, SHA-256 `7f8aeb09137903b7786afd4c9f2d411038929c3e7492d71ac9ade108507e99a2`: compileall exited 0; 11 ingestion tests, 8 transition-metrics tests, and 7 Stage 2 regression tests passed; the parent SHA-256 was identical before and after. No training, checkpoint, candidate, compiler, or renderer command was run.

## Phase 3 metric boundary

The new metrics score supplied predicted typed programs against manifest-bound targets separately for `train`, `held_out_object_class`, `held_out_operation_family`, and `held_out_composition`. They report state, relation, operation, uncertainty, exact-program, evidence completeness, compiler-evidence completeness, and compiler-validity independently. No pooled held-out result is emitted. Compiler validity remains unavailable unless every prediction in a split has a matching `observed` compiler receipt; a generated or inferred receipt is rejected. The current schema is a typed program and does not contain full post-action state snapshots, so this is typed-program/action reconstruction evidence, not observed physical next-state or rendering evidence.

## Rollback path

Until a director-authorized commit, only Manus-owned paths may be changed. If a rollback is required, stop and request the director’s working-tree adjudication; do not use Git restore, reset, clean, stash, or deletion. Smoke artifacts are written only to an ignored, new explicit temporary directory and remain preserved unless Michael authorizes deletion item by item.

## Director commit-window request

The requested explicit pathspecs and complete gate record are in `handoff_manus_2026-08-26_lane-b-learning-path.md`. The director must independently re-run the gate, review only the listed eight owned paths, verify the protected parent hash, and grant or deny the commit window. Manus must not stage, commit, push, pull, stash, reset, restore, revert, or rebase before that decision.

## Next-agent pickup notes

The working tree has the four expected director-held untracked files named in the multi-lane charter: `plan_2026-08-26_2042_verify-stage2-claims.md`, `plan_2026-08-26_2058_repo-sync.md`, `plan_2026-08-26_2144_multi-lane-build-charter.md`, and `vision_deep_dive.md`. Do not touch, stage, or adjudicate them. The GPU probe failed with `Failed to initialize NVML: Unknown Error`; that is a monitoring limitation, not evidence of GPU use. No GPU work is authorized for this lane or plan.
