# Plan — Worktree Clean Handoff

## Goal

Audit the remaining dirty worktree entries, preserve legitimate Markdown plan
artifacts in git, clear the zero-content-diff `CCF_Sovereign/README.md` status
artifact, and push `main` so the repository hands off cleanly.

## Files To Read

- `AGENTS.md`
- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `README.md`
- `STATUS.md`
- `CCF_Sovereign\README.md`
- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

## Files To Edit

- this plan
- `handoff_codex_2026-08-28_worktree-clean-handoff.md`

## Files To Stage

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`
- this plan
- `handoff_codex_2026-08-28_worktree-clean-handoff.md`

## Ordered Steps

1. [x] Inspect dirty status, diffs, deleted files, and repo parity.
2. [x] Verify `CCF_Sovereign/README.md` has no content diff and matches the
   `HEAD` blob hash.
3. [x] Read the three untracked Markdown plan artifacts and scan for obvious
   secrets/private credentials.
4. [x] Write a handoff classifying the preserved files and remaining boundary.
5. [x] Refresh the index for the zero-content-diff README marker.
6. [x] Run the docs gate on explicit staged paths.
7. [x] Commit and push to `origin/main`.
8. [x] Confirm the final worktree is clean.

## Test Gate

```pwsh
git diff --check --cached
git status --short --branch
```

## Rollback Path

Revert only the cleanup commit if these plan artifacts should later be removed
from the canonical repo. Do not delete local evidence, checkpoints, ignored
receipts, Chronos files, or unrelated worktree state.

## Next-Agent Pickup Notes

The three inherited plan files are root Markdown planning artifacts for
Chronos/renderer integration. They are being preserved as provenance, not as
completed capability evidence. The CCF README marker is a stat/index artifact:
its working-tree hash matched `HEAD` before cleanup.
