# Plan — Stage 2 grounded world trajectories

**Date:** 2026-08-26 20:24 CDT
**Owner:** Manus AI
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus`
**Branch:** `main`
**Starting commit:** `896ebd71d9f8aff8ff0d1a19706fa031d3e5185f`
**Factual change commit:** `8cf4e695297b8f76cd6d6de4784581463d6fcf86`
**Handoff commit:** `40b84dab0e54bd01a789134b4b5244c872ccf502`
**Status:** COMPLETED — PUSHED AND SYNCHRONIZED

## Goal

Build the first bounded, deterministic Stage 2 generator for validated, evidence-labeled, multi-frame `WorldProgram` trajectories. Produce whole-family holdouts, structural-program coverage evidence, canonical JSONL plus a hash-bound manifest, and fail-hard regression gates. Do not launch model training, touch checkpoints, alter promotion state, or claim learned world dynamics or visual correctness.

## Files read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `handoff_manus_2026-08-26_priority-correction-and-claude-ab.md`
- [x] `CCF_Sovereign/README.md`
- [x] `CCF_Sovereign/MVP_STATUS.md`
- [x] `CCF_Sovereign/requirements.txt`
- [x] `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- [x] `CCF_Sovereign/src/world_schema/model.py`
- [x] `CCF_Sovereign/src/world_schema/tokens.py`
- [x] `CCF_Sovereign/src/world_schema/__init__.py`
- [x] `CCF_Sovereign/test_world_schema.py`
- [x] `docs/research/PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`
- [x] `C:\chronos2\plan_2026-08-26_0531_primus-world-core.md` (read-only coordination surface)
- [x] `C:\chronos2\HANDOFF_claude_2026-08-26_primus-world-core-and-doc-truth.md` (read-only coordination surface)

## Files to create or edit

- [x] `CCF_Sovereign/src/world_schema/trajectory_generator.py`
- [x] `CCF_Sovereign/src/world_schema/__init__.py`
- [x] `CCF_Sovereign/generate_world_trajectories.py`
- [x] `CCF_Sovereign/test_world_trajectory_generator.py`
- [x] `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- [x] `CCF_Sovereign/README.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `docs/defense_evidence/benchmarks/ccf_world_core_day_one_2026-08-26.md`
- [x] This plan
- [x] Final root handoff

## Ordered steps

- [x] Define a deterministic generator configuration and manifest schema.
- [x] Emit validated multi-frame trajectories using only compiler-owned operations and explicit capability status.
- [x] Preserve generated and inferred evidence distinctions, source hashes, camera state, and uncertainty. No observed or measured evidence is claimed.
- [x] Enforce whole object-class, whole operation-family, and composition holdouts without random-example leakage.
- [x] Record structural-program coverage using the existing normalization and signature implementation.
- [x] Refuse an existing output destination and publish output through a temporary sibling directory.
- [x] Add a small command-line entry point with explicit output, seed, and count controls.
- [x] Add fail-hard tests for determinism, validation, codec and S³V round trips, holdout integrity, manifest hashes, structural diversity, and destination refusal.
- [x] Run the focused gates and a tiny ignored local smoke generation.
- [x] Inspect generated hashes, split counts, coverage, and working-tree scope.
- [x] Update truth surfaces with only verified behavior and explicit non-claims.
- [x] Audit source, tests, evidence-bearing Markdown, smoke hashes, and protected-parent integrity.
- [x] Explicitly stage and commit the verified Stage 2 unit as the factual change commit recorded above.
- [x] Seal the factual commit hash into a final handoff, commit the handoff, push `origin main`, and verify synchronization.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_schema generate_world_trajectories.py test_world_schema.py test_world_trajectory_generator.py
python test_world_schema.py
python test_world_trajectory_generator.py
```

A tiny CLI smoke generation wrote only to `CCF_Sovereign/tmp/stage2_smoke_20260826_2024/`, which is ignored. It produced 21 programs with 21 unique structural signatures, zero duplicates, and split counts of 12 train plus three per holdout. The JSONL SHA-256 is `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28`; the manifest SHA-256 is `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`.

The final verification matrix completed with exit code 0: compileall, eight schema tests, seven generator tests, four candidate-safety tests, and six MVP tests. No training or promotion command was run. No candidate was promoted.

## Rollback path

Do not reset, clean, or delete shared work. Before commit, rollback is limited to restoring only the explicit Stage 2 paths after inspecting their diffs and confirming no concurrent edits. After push, use a new revert commit if rollback is necessary. Generated smoke data remains local and ignored; do not delete it without explicit per-item operator approval.

## Next-agent pickup notes

Start by checking `git status --short --branch`, `git diff --stat`, the protected parent hash, and this checklist. Chronos2 is a separate dirty shared tree and must remain read-only. If any unexpected Primus path becomes dirty, stop and attribute ownership before continuing. No training or candidate promotion is authorized by this plan.
