# Plan — independently verify the Stage 2 trajectory claims

**Created:** 2026-08-26 20:42
**Author:** Claude (Opus 5), desktop session
**Status:** COMPLETE — all steps closed 2026-08-26 20:45

## Goal

Verify, against the disk and by execution, the reported Stage 2 state:
HEAD `856df203`, parent hash unchanged, no ladder active, no candidate
promoted. Trust no truth surface or gate table without re-running it.
This is a verification pass only. No source, doc, checkpoint, or git
state is modified beyond this plan file.

## Files to read

- `handoff_manus_2026-08-26_stage2-grounded-trajectories.md`
- `plan_2026-08-26_2024_stage2-grounded-trajectories.md`
- `CCF_Sovereign/src/world_schema/trajectory_generator.py`
- `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- `STATUS.md`, `README.md`, `CCF_Sovereign/README.md`

## Files to edit

- This plan file only.

## Ordered steps

1. Confirm HEAD, `origin/main` via `git ls-remote`, worktree status. DONE
2. Hash live parent and frozen archive against
   `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`. DONE
3. Enumerate `.pt` files by mtime; confirm none created in the Stage 2
   window. DONE
4. Confirm GPU idle and no training process. DONE
5. Hash untracked `vision_deep_dive.md`; confirm chronos2 untouched. DONE
6. Re-run every gate in the handoff matrix. DONE - 25/25 pass, matrix confirmed.
7. Read the generator diff for defects the tests would not catch. DONE -
   regenerated from seed, bit-identical hashes; holdout contract independently
   confirmed non-leaking from the data, not from the tests.
8. Reconcile the "4K token encoding" claim. DONE - NOT a contradiction.
   "4K" is WORLD_VOCAB_SIZE = 4096 (vocabulary size), not a sequence bound.
   Sequence lengths of 7,391-7,494 are consistent with it.
9. Report findings. DONE - no stale surface found; no correction needed.

## Outcome

Every reported claim verified true. No defect found. This plan file is the
only tree change; it is uncommitted and awaits operator instruction.

## Test gate

From `C:\Primus\CCF_Sovereign`:

- `python -m compileall -q src\world_schema generate_world_trajectories.py test_world_schema.py test_world_trajectory_generator.py`
- `python test_world_schema.py`
- `python test_world_trajectory_generator.py`
- `python test_candidate_training.py`
- `python test_mvp.py`

## Rollback path

This plan file is the only artifact created. Delete it on operator
instruction; nothing else to revert. No commit is made without approval.

## Next-agent pickup notes

If interrupted, the first unfinished step is named above. The tree must
be left with `vision_deep_dive.md` untouched — it belongs to a
concurrent builder.
