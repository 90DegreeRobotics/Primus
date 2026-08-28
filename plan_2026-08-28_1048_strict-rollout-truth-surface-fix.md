# Plan — Strict Rollout Truth Surface Fix

## Goal

Correct the committed truth surfaces for the strict source-train task-disjoint
cross-rollout result without touching model evidence, candidates, checkpoints,
or ignored local receipts.

## Files To Read

- `AGENTS.md`
- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `README.md`
- `STATUS.md`
- `handoff_manus_2026-08-28_strict-task-disjoint-cross-rollout.md`
- `CCF_Sovereign\evaluation\bridgedata_strict_task_cross_rollouts\strict-task-cross-rollout-20260828-001\strict_task_cross_rollout.json`

## Files To Edit

- `README.md`
- `STATUS.md`
- `handoff_manus_2026-08-28_strict-task-disjoint-cross-rollout.md`
- this plan

## Ordered Steps

1. [x] Verify the strict rollout evidence file hash and payload hash field.
2. [x] Correct the malformed payload SHA in `STATUS.md` and the handoff.
3. [x] Clarify the README feasibility paragraph so it cannot be read as current
   after the subsequent strict evaluation paragraph.
4. [x] Run the docs gate.
5. [x] Commit and push the bounded docs correction to `origin/main`.

## Test Gate

```pwsh
git diff --check --cached
git status --short --branch
```

## Rollback Path

Revert only this docs-only commit if the correction is later found wrong. Do
not alter ignored evidence receipts, candidate artifacts, or checkpoints.

## Next-Agent Pickup Notes

The strict evaluation receipt's file SHA is
`218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f`.
Its top-level `payload_sha256` field is
`445caddf9fb884dae35499a59a856a175d90ff6fee2b03862da7f303c30d172c`.
